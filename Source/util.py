import os
import numpy as np
from scipy.ndimage.measurements import label
from queue import Queue
from skimage.morphology import disk, opening, closing, dilation, erosion
from skimage.feature import canny
from scipy.ndimage.filters import gaussian_filter
from sklearn.externals.joblib import Parallel, delayed
from skimage.filters import threshold_otsu, rank
from sklearn.svm import SVC
import pickle

def getPathsToVisit(topLevelName):
    topLevelPath = os.path.abspath(topLevelName)
    listing = os.listdir(topLevelPath)

    folderCnt = 0
    pathsToVisit = []
    for ff in listing:
        ffPath = os.path.join(topLevelPath, ff)
        if os.path.isdir(ffPath) and ff.isnumeric():
            pathsToVisit.append(ffPath)

    return sorted(pathsToVisit)


def get_first_crossing_time(sig, thresh_frac, mode=1):
  # mode = 0 Returns the first crossing time of the threshold.
  # mode = 1 Returns the first rising edge that crosses the threshold.
  # mode = -1 Returns the first falling edge that crosses the threshold.
  # All modes return 0 for flat signals.
  # Rising and falling edge modes return 0 if no valid crossing is found.

  sig_min = np.amin(sig.astype(np.float), axis=-1, keepdims=True)
  sig_max = np.amax(sig.astype(np.float), axis=-1, keepdims=True)
  sig_thresh = sig_min + thresh_frac*(sig_max-sig_min)
  sig_crossing = np.diff((sig.astype(np.float) > sig_thresh).astype('int'), axis=-1)
  if mode == 0:
    first_over = np.argmax(np.abs(sig_crossing), axis=-1) + 1
  elif mode == 1:
    first_over = np.argmax(sig_crossing, axis=-1) + 1
  elif mode == -1:
    first_over = np.argmax(-1*sig_crossing, axis=-1) + 1
  else:
    raise ValueError('Invalid mode argument!')
  first_below = first_over - 1

  mesh_list = []
  for dim in range(sig.ndim-1):
    mesh_list.append(np.arange(sig.shape[dim]))
  if len(mesh_list) > 0:
    mesh_list = np.meshgrid(*mesh_list, indexing='ij')

  cross_type = sig_crossing[ mesh_list + [first_below] ]
  val_over = sig[ mesh_list + [first_over] ].astype(np.float)
  val_below = sig[ mesh_list + [first_below] ].astype(np.float)

  val_range = val_over - val_below
  frac_below = (val_over - np.squeeze(sig_thresh))/(val_range + 0.00001)
  first_crossing = first_over - frac_below
  first_crossing[cross_type == 0] = 0
  return first_crossing


def randomSubset(features, labels, subsetSize):
    numCategories = np.amax(labels) + 1
    numSamples = []

    for category in range(numCategories):
        posRate = np.sum(labels==category)/labels.shape[0]
        numSamples.append(np.ceil(posRate*subsetSize).astype('int'))

    totalSamples = sum(numSamples)
    overflow = totalSamples - subsetSize

    step = 1
    if overflow < 0:
        step = -step

    # Redistribute the overflow difference to the largest group.
    for i in range(abs(overflow)):
        index, val = max(list(enumerate(numSamples)), key=lambda x: x[1])
        numSamples[index] -= step

    selList = []
    for category in range(numCategories):
        indexList = np.where(labels==category)[0]
        sampleSize = numSamples[category]
        if indexList.size == 0:
            continue
        sel = np.random.choice(indexList, size=sampleSize, replace=False)
        selList.append(sel)
    sel = np.hstack(selList)

    # Sample the features and labels
    # featuresSubset = features[sel]
    # labelsSubset = labels[sel]
    # return (featuresSubset, labelsSubset)
    return sel


def randomSubsetBalanced(features, labels, subsetSize):
    numCategories = np.amax(labels) + 1
    numSamples = []

    for category in range(numCategories):
        numSamples.append(subsetSize//numCategories)

    # Add the remaining samples to the first category
    numSamples[0] += subsetSize%numCategories

    selList = []
    for category in range(numCategories):
        indexList = np.where(labels==category)[0]
        sampleSize = numSamples[category]
        if indexList.size == 0:
            continue
        sel = np.random.choice(indexList, size=sampleSize, replace=True)
        selList.append(sel)
    sel = np.hstack(selList)

    # Sample the features and labels
    # featuresSubset = features[sel]
    # labelsSubset = labels[sel]
    # return (featuresSubset, labelsSubset)
    return sel


def write_ppm(filename, img):
    if img.ndim < 2 or img.ndim > 3:
        raise ValueError('Image can only have 2 or 3 dimensions!')
    if img.ndim == 2:
        im = np.dstack((img, img, img)) 
    height, width, num_channels = im.shape
    if num_channels != 3:
        raise ValueError('Image needs to have 3 channels!')
    head = 'P6' + '\n' + str(width) + ' ' + str(height) + '\n' + '255' + '\n'
    data = im.ravel().astype('uint8').tobytes()
    with open(filename, 'wb') as f:
        f.write(bytes(head, 'UTF-8'))
        f.write(data)


# def read_ppm(filename):
#     with open(filename, 'rb') as f:
#         line = f.readline().decode()   # Read format
#         while(line[0]=="#"):  # Skip comments
#             line = f.readline().decode()
#         if "P6" not in line:
#             print('Error: This function can only read P6 format!')
#             return None
#         line = f.readline().decode()   # Read Size
#         while(line[0]=="#"):  # Skip comments
#             line = f.readline().decode()
#         nx, ny = [int(x) for x in line.split()]
#         line = f.readline().decode()   # Read Range
#         while(line[0]=="#"):  # Skip comments
#             line = f.readline().decode()
#         vmax = [int(x) for x in line.split()][0]
#         if vmax > 255 or vmax < 0:
#             print('Error: This function can only read uint8 images!')
#             return None
#         data_size = nx*ny*3
#         data = np.fromstring(f.read(data_size), dtype=np.uint8).reshape(nx, ny, 3)
#     return data

def read_ppm(filename):
    with open(filename, 'rb') as f:
        
        # Read PPM parameters
        valid_params = []
        for line in f:
            param_str = line.decode('utf-8').strip()
            if not param_str or param_str[0] == '#':
                continue
            valid_params += param_str.split()
            if len(valid_params) == 4:
                ppm_mode = valid_params[0]
                width, height, maxval = [int(x) for x in valid_params[1:]]
                break

        # Check if parameters are valid
        if ppm_mode == 'P3':
            raw_mode = False
        elif ppm_mode == 'P6':
            raw_mode = True
        else:
            raise ValueError('Invalid PPM mode!')
        if width <= 0 or height <=0:
            raise ValueError('Invalid width and height in PPM header!')
        if maxval > 255:
            raise ValueError('Cannot handle values larger than 255!')

        # Read in the data
        if raw_mode:
            data_bytes = f.read(width*height*3)
            img = np.fromstring(data_bytes, dtype=np.uint8).reshape(height, width, 3)
        else:
            data_str = f.read().decode('utf-8')
            data_int = [int(x) for x in data_str.split()]
            img = np.array(data_int, dtype=np.uint8).reshape(height, width, 3)
            
        return img    


def connected_comp3d(labels3d):
    max_label = np.amax(labels3d)
    total_components = 0
    comp2label_list = []
    comp2label_list.append(np.array([0], dtype='int'))
    connected3d_all = np.zeros(labels3d.shape, dtype='int')
    for ll in range(1,max_label+1):
        label_map = (labels3d==ll)
        connected3d, n_components = connect3d(label_map)
        connected3d_all[connected3d > 0] = connected3d[connected3d > 0] + total_components
        comp2label_list.append(np.ones(n_components, dtype='int')*ll)
        total_components += n_components
        
    comp2label = np.hstack(comp2label_list)
    return connected3d_all, comp2label


def tile_x(im3d, vertical=True):
    if im3d.ndim < 3 or im3d.ndim > 4:
        raise ValueError('Invalid number of dimensions!')
    if im3d.ndim == 4:
        # Multichannel image
        im3d_t = np.transpose(im3d, (1, 2, 0, 3))
    else:
        # Single channel image
        im3d_t = np.transpose(im3d, (1, 2, 0))
    im2d = tile_z(im3d_t, vertical)
    return im2d

def untile_x(im2d, shape, vertical=True):
    if im2d.ndim < 2 or im2d.ndim > 3:
        raise ValueError('Invalid number of dimensions!')
    shape_t = [shape[1], shape[2], shape[0]]
    im3d_t = untile_z(im2d, shape_t, vertical)
    if im2d.ndim == 3:
        # Multichannel image
        im3d = np.transpose(im3d_t, (2, 0, 1, 3))
    else:
        # Single channel image
        im3d = np.transpose(im3d_t, (2, 0, 1))
    return im3d

def tile_y(im3d, vertical=True):
    if im3d.ndim < 3 or im3d.ndim > 4:
        raise ValueError('Invalid number of dimensions!')
    if im3d.ndim == 4:
        # Multichannel image
        im3d_t = np.transpose(im3d, (0, 2, 1, 3))
    else:
        # Single channel image
        im3d_t = np.transpose(im3d, (0, 2, 1))
    im2d = tile_z(im3d_t, vertical)
    return im2d

def untile_y(im2d, shape, vertical=True):
    if im2d.ndim < 2 or im2d.ndim > 3:
        raise ValueError('Invalid number of dimensions!')
    shape_t = [shape[0], shape[2], shape[1]]
    im3d_t = untile_z(im2d, shape_t, vertical)
    if im2d.ndim == 3:
        # Multichannel image
        im3d = np.transpose(im3d_t, (0, 2, 1, 3))
    else:
        # Single channel image
        im3d = np.transpose(im3d_t, (0, 2, 1))
    return im3d

def tile_z(im3d, vertical=True):
    if im3d.ndim < 3 or im3d.ndim > 4:
        raise ValueError('Invalid number of dimensions!')
    nx, ny, nz = im3d.shape[:3]
    if im3d.ndim == 4:
        # Multichannel image
        if vertical:
            im2d = np.transpose(im3d, (2, 0, 1, 3)).reshape(nx*nz, ny, -1)
        else:
            im2d = np.transpose(im3d, (0, 2, 1, 3)).reshape(nx, ny*nz, -1)
    else:
        # Single channel image
        if vertical:
            im2d = np.transpose(im3d, (2, 0, 1)).reshape(nx*nz, ny)
        else:
            im2d = np.transpose(im3d, (0, 2, 1)).reshape(nx, ny*nz)
    return im2d

def untile_z(im2d, shape, vertical=True):
    if im2d.ndim < 2 or im2d.ndim > 3:
        raise ValueError('Invalid number of dimensions!')
    nx, ny, nz = shape[:3]
    if im2d.ndim == 3:
        # Multichannel image
        if vertical:
            im3d = np.transpose(im2d.reshape(nz, nx, ny, -1), (1, 2, 0, 3))
        else:
            im3d = np.transpose(im2d.reshape(nx, nz, ny, -1), (0, 2, 1, 3))
    else:
        # Single channel image
        if vertical:
            im3d = np.transpose(im2d.reshape(nz, nx, ny), (1, 2, 0))
        else:
            im3d = np.transpose(im2d.reshape(nx, nz, ny), (0, 2, 1))
    return im3d

def connect3d(bm3d):
    nx, ny, nz = bm3d.shape
    # bm2d = np.transpose(bm3d, (0, 2, 1)).reshape(nx, ny*nz)
    # connected2d, n_components = label(bm2d)
    # connected3d = np.transpose(connected2d.reshape(nx, nz, ny), (0, 2, 1))

    bm2d = tile_z(bm3d)
    connected2d, n_components_z = label(bm2d)
    connected3d_z = untile_z(connected2d, bm3d.shape)

    bm2d = tile_x(bm3d)
    connected2d, n_components_x = label(bm2d)
    connected3d_x = untile_x(connected2d, bm3d.shape)

    parent_z = np.arange(n_components_z+1)
    for id_x in range(1,n_components_x+1):
        joined_z = connected3d_z[connected3d_x==id_x]
        group_id_z = np.amin(joined_z)
        for id_z in joined_z:
            parent_z[id_z] = parent_z[group_id_z]
    
    unique_id = {}
    unique_cnt = 0
    for ii in range(1, n_components_z+1):
        if parent_z[ii] not in unique_id:
            unique_cnt += 1
            unique_id[parent_z[ii]] = unique_cnt
        parent_z[ii] = unique_id[parent_z[ii]]
    # Do the final mapping and return the result
    connected3d = parent_z[connected3d_z]
    n_components = unique_cnt

    # Now we need to find overlaps between slices
    # Create an adj_list and then run bfs
    g = {}
    for zz in range(nz-1):
        current_slice = connected3d[:,:,zz].ravel()
        next_slice = connected3d[:,:,zz+1].ravel()
        overlap = (current_slice*next_slice)>0
        src_arr = current_slice[overlap]
        dst_arr = next_slice[overlap]
        for ss in range(src_arr.shape[0]):
            src = src_arr[ss]
            dst = dst_arr[ss]
            if src == dst:
                continue
            if src not in g:
                g[src] = set()
            if dst not in g:
                g[dst] = set()
            g[src].add(dst)
            g[dst].add(src)
    # print('Graph_size =', n_components)

    # BFS
    processed = set()
    parent = np.arange(n_components+1)
    for cc in range(1, n_components+1):
        if cc in processed or cc not in g:
            continue
        discovered = Queue()
        discovered.put(cc)
        seen = set()
        seen.add(cc)
        while not discovered.empty():
            v = discovered.get()
            adj_set = g[v]
            for u in adj_set:
                if u in seen or u in processed:
                    continue
                discovered.put(u)
                seen.add(cc)
                parent[u] = cc
            processed.add(v)
    unique_id = {}
    unique_cnt = 0
    for ii in range(1, n_components+1):
        if parent[ii] not in unique_id:
            unique_cnt += 1
            unique_id[parent[ii]] = unique_cnt
        parent[ii] = unique_id[parent[ii]]
    # Do the final mapping and return the result
    connected3d = parent[connected3d]
    return connected3d, unique_cnt


def connect3d_parallel(bm3d):
    n_jobs = 12
    nz = bm3d.shape[2]
    chunk_size = nz//n_jobs
    chunk_start = np.arange(0, nz-chunk_size+1, chunk_size)
    chunk_end = chunk_start+chunk_size
    chunk_end[-1] = nz
    chunks = Parallel(n_jobs=12)(delayed(connect3d)(bm3d[:,:,chunk_start[zz]:chunk_end[zz]]) for zz in range(n_jobs))
    chunks = [chunk[0] for chunk in chunks]  # Ignore n_components for each chunk
    cluster_cnt = 0
    for chunk in chunks:
        chunk += cluster_cnt
        chunk[chunk==cluster_cnt] = 0
        cluster_cnt = np.amax(chunk)
    chunks = np.dstack(chunks)
    return connect3d(chunks)

# def canny3d_z(im3d):
#     nx, ny, nz = im3d.shape
#     edge3d_list = []
#     for zz in range(nz):
#         im = im3d[:,:,zz]
#         im = gaussian_filter(im, sigma=2)
#         im = opening(im, disk(4))
#         edges = canny(im, sigma=1)
#         # edges = canny(im, sigma=1, low_threshold=0.05*255, high_threshold=0.15*255)
#         edges = dilation(edges, disk(2))
#         edges = erosion(edges, disk(1))
#         # edges = closing(edges, disk(3))
#         edge3d_list.append(edges)
#     edge3d_z = np.dstack(edge3d_list)
#     return edge3d_z

def canny3d_x(im3d):
    im3d_t = np.transpose(im3d, (1, 2, 0))
    edge3d_x_t = canny3d_z(im3d_t)
    edge3d_x = np.transpose(edge3d_x_t, (2, 0, 1))
    return edge3d_x

def canny3d_y(im3d):
    im3d_t = np.transpose(im3d, (0, 2, 1))
    edge3d_y_t = canny3d_z(im3d_t)
    edge3d_y = np.transpose(edge3d_y_t, (0, 2, 1))
    return edge3d_y


def otsu_slice(im2d):
    im2d = gaussian_filter(im2d, sigma=2)
    local_otsu = rank.otsu(im2d, disk(5))
    edges = im2d < local_otsu
    # edges = closing(edges, disk(5))
    return edges

def otsu3d_z(im3d):
    nx, ny, nz = im3d.shape
    slices_z = Parallel(n_jobs=12)(delayed(otsu_slice)(im3d[:,:,zz]) \
        for zz in range(nz))
    return np.dstack(slices_z)


# def otsu3d_z(im3d):
#     nx, ny, nz = im3d.shape
#     edge3d_list = []
#     for zz in range(nz):
#         im = im3d[:,:,zz]
#         im = gaussian_filter(im, sigma=2)
#         im = opening(im, disk(4))
#         local_otsu = rank.otsu(im, disk(15))
#         threshold_global_otsu = threshold_otsu(im)
#         edges = im >= local_otsu
#         edges = closing(edges, disk(5))
#         edge3d_list.append(edges)
#     edge3d_z = np.dstack(edge3d_list)
#     return edge3d_z

def otsu3d_x(im3d):
    im3d_t = np.transpose(im3d, (1, 2, 0))
    edge3d_x_t = otsu3d_z(im3d_t)
    edge3d_x = np.transpose(edge3d_x_t, (2, 0, 1))
    return edge3d_x

def otsu3d_y(im3d):
    im3d_t = np.transpose(im3d, (0, 2, 1))
    edge3d_y_t = otsu3d_z(im3d_t)
    edge3d_y = np.transpose(edge3d_y_t, (0, 2, 1))
    return edge3d_y

def fast_predict(classifier, X_test):
    # Run in parallel
    # Load classifier
    classifier_bytes = pickle.dumps(classifier)
    n_jobs = 12
    n_samples = X_test.shape[0]
    chunk_size = n_samples//n_jobs
    chunk_start = np.arange(0, n_samples-chunk_size+1, chunk_size)
    chunk_end = chunk_start+chunk_size
    chunk_end[-1] = n_samples
    classifier_list = [pickle.loads(classifier_bytes) for i in range(n_jobs)]
    chunks = Parallel(n_jobs=12)(delayed(classifier_list[i].predict)(X_test[chunk_start[i]:chunk_end[i], :])\
                                 for i in range(n_jobs))
    predicted = np.hstack(chunks)
    return predicted

import warnings
def SI2C(SI, TR, FA, T10, r1, baseline=None, t_baseline=None):
    # This function takes a signal and returns the concentration C(t).
    # If SI is 2D (n by t), each row should correspond to a voxel.
    # The function assumes min(signal) -> 0 mM.
    # SI = Signal Intensity
    # TR = Repetition time (sec)
    # FA = Flip angle (rad)
    # T10 = T1 of the tissue (pre-contrast)
    # r1 = Relaxivity of the contrast agent (s^-1)*(mM^-1)
    # baseline = Baseline value to use for the voxels. 
    #   - This should be either a scalar or a vector of length n.
    #   - For scalar value, all voxels use the same baseline value.
    #   - For vector, each voxel gets its own baseline.
    # t_baseline = Number of time points to average for baseline.
    #   - Each voxel gets its own baseline value.
    #   - This is only valid if the baseline parameter not defined.
    # Return Value: C in mM

    C_limit = 20  # Cap for estimation (mM)

    if SI.ndim == 1:
        SI = SI.reshape(1, -1)

    if baseline is None:
        # Define baseline
        if t_baseline is None:
            # Estimate the baseline cut-off time from data
            # t0 = int(get_first_crossing_time(np.mean(SI, axis=0, keepdims=True), 0.05))
            t0 = int(np.ceil(get_first_crossing_time(np.mean(SI, axis=0, keepdims=True), 0.10)))
            # print('t_baseline =', t0)
        else:
            # use the given baseline time
            t0 = t_baseline

        baseline = np.mean(SI[:, :t0], axis=1, keepdims=True)
    else:
        if np.isscalar(baseline):
            # use the given baseline value for all voxels
            SI[SI<baseline] = baseline
            baseline = baseline * np.ones((SI.shape[0], 1), dtype=SI.dtype)
        else:
            baseline = baseline.reshape(-1, 1)
            SI[SI<baseline] = np.broadcast_to(baseline, SI.shape)[SI<baseline]



    R10 = 1/T10
    S0 = baseline*(1-np.exp(-R10*TR)*np.cos(FA))/((1-np.exp(-R10*TR))*np.sin(FA))

    R1_limit = R10 + r1*C_limit
    SI_limit = S0*((1-np.exp(-R1_limit*TR))*np.sin(FA))/(1-np.exp(-R1_limit*TR)*np.cos(FA))

    SI_mask = SI - SI_limit
    SI_mask[SI_mask < 0] = 0
    SI -= SI_mask

    R1 = 1/TR * (np.log(-SI*np.cos(FA)+S0*np.sin(FA)) - np.log(-SI+S0*np.sin(FA)))
    C = (R1-R10)/r1

    C[C<0] = 0

    return C


def imresize3d(im3d, scale):
    nx, ny, nz = im3d.shape
    nx_sc, ny_sc, nz_sc = [round(scale*x) for x in im3d.shape]
    im_fft = np.fft.fftn(im3d)
    im_fft = np.fft.fftshift(im_fft)
    im_fft_scaled = np.zeros((nx_sc, ny_sc, nz_sc), dtype=im_fft.dtype)
    off_kx = (nx_sc-nx)//2
    off_ky = (ny_sc-ny)//2
    off_kz = (nz_sc-nz)//2
    im_fft_scaled[off_kx:off_kx+nx, off_ky:off_ky+ny, off_kz:off_kz+nz] = im_fft
    im_fft_scaled = np.fft.ifftshift(im_fft_scaled)
    im_scaled = np.fft.ifftn(im_fft_scaled)
    return np.abs(im_scaled)

from skimage.transform import resize
def imresize3d_along_z(im3d, scale):
    nx, ny, nz = im3d.shape
    im_list = []
    for zz in range(nz):
        im2d = im3d[:,:,zz]
        im2d = resize(im2d, (2*nx, 2*ny))
        im_list.append(im2d)
    im_temp3d = np.dstack(im_list)
    im_list = []
    for xx in range(im_temp3d.shape[0]):
        im2d = im_temp3d[xx,:,:]
        im2d = resize(im2d, (2*ny, 2*nz))
        im_list.append(im2d[np.newaxis, :, :])
    im3d_sc = np.vstack(im_list)
    return im3d_sc


def imresize3d_along_x(im3d, scale):
    nx, ny, nz = im3d.shape
    im_list = []
    for xx in range(nx):
        im2d = im3d[xx,:,:]
        im2d = resize(im2d, (2*ny, 2*nz))
        im_list.append(im2d[np.newaxis, :, :])
    im_temp3d = np.vstack(im_list)
    im_list = []
    for zz in range(im_temp3d.shape[2]):
        im2d = im_temp3d[:,:,zz]
        im2d = resize(im2d, (2*nx, 2*ny))
        im_list.append(im2d)
    im3d_sc = np.dstack(im_list)
    return im3d_sc


def imresize3d_along_y(im3d, scale):
    nx, ny, nz = im3d.shape
    im_list = []
    for yy in range(ny):
        im2d = im3d[:,yy,:]
        im2d = resize(im2d, (2*nx, 2*nz))
        im_list.append(im2d[:, np.newaxis, :])
    im_temp3d = np.hstack(im_list)
    im_list = []
    for zz in range(im_temp3d.shape[2]):
        im2d = im_temp3d[:,:,zz]
        im2d = resize(im2d, (2*nx, 2*ny))
        im_list.append(im2d)
    im3d_sc = np.dstack(im_list)
    return im3d_sc


from scipy.ndimage.morphology import binary_fill_holes
def fill2d(im):
    # Binary fill gaps
    cluster_size = np.bincount(im.ravel())
    cluster_size[0] = 0  # Remove bg
    cluster_ids = np.where(cluster_size > 0)[0]
    cluster_size = cluster_size[cluster_ids]
    cluster_sort = np.argsort(cluster_size)[::-1]
    im_filled = np.zeros_like(im)
    for cluster_id in cluster_ids[cluster_sort]:
        bm = im == cluster_id
        bm = binary_fill_holes(bm)  # Fill holes
        im_filled[bm>0] = cluster_id
    return im_filled


def erode2d(im):
    # Binary erode
    cluster_size = np.bincount(im.ravel())
    cluster_size[0] = 0  # Remove bg
    cluster_ids = np.where(cluster_size > 0)[0]
    cluster_size = cluster_size[cluster_ids]
    cluster_sort = np.argsort(cluster_size)[::-1]
    im_filled = np.zeros_like(im)

    for cluster_id in cluster_ids[cluster_sort]:
        bm = im == cluster_id
        im_filled[bm>0] = 0  # First, fill the original space with 0
        bm = erosion(bm, disk(8))  # Erode back more to disconnect thin structures (i.e. vessels)
        im_filled[bm>0] = cluster_id
    return im_filled


def dilate2d(im, selem):
    # Binary dilate
    cluster_size = np.bincount(im.ravel())
    cluster_size[0] = 0  # Remove bg
    cluster_ids = np.where(cluster_size > 0)[0]
    cluster_size = cluster_size[cluster_ids]
    cluster_sort = np.argsort(cluster_size)[::-1]
    im_filled = np.zeros_like(im)

    for cluster_id in cluster_ids[cluster_sort]:
        bm = im == cluster_id
        bm = dilation(bm, selem)
        im_filled[bm>0] = cluster_id
    return im_filled

from scipy.ndimage import distance_transform_edt
from skimage.feature import peak_local_max
from skimage.morphology import watershed
def apply_watershed(label3d):
    num_components = np.amax(label3d)
    new_labels = np.zeros_like(label3d)
    cluster_cnt = 0
    for cc in range(1,num_components+1):
        proj_z = np.sum(label3d == cc, axis=2)
        bm = proj_z>0
        distance = distance_transform_edt(bm)
        distance = gaussian_filter(distance, sigma=2)
        local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((40, 40)), labels=bm)
        markers = label(local_maxi)[0]
        ws_labels = watershed(-distance, markers, mask=proj_z>0)
        num_labels = np.amax(ws_labels)
        bm = (label3d == cc).astype('int')
        bm *= ws_labels[:,:,np.newaxis]
        bm += cluster_cnt
        new_labels[bm > cluster_cnt] = bm[bm > cluster_cnt]
        cluster_cnt += num_labels
    return new_labels

from scipy.ndimage.measurements import label
def otsu_segment(im3d):
    global_otsu_speedup = True
    im3d_sc_x = imresize3d_along_x(im3d, 2)
    im3d_sc_y = imresize3d_along_y(im3d, 2)
    im3d_sc_z = imresize3d_along_z(im3d, 2)

    edges3d_x = otsu3d_x(im3d_sc_x)
    edges3d_y = otsu3d_y(im3d_sc_y)
    edges3d_z = otsu3d_z(im3d_sc_z)

    edges3d = (edges3d_x + edges3d_y + edges3d_z) > 0


    if global_otsu_speedup:
        # Reduce number of regions using global otsu (optional speedup)
        im3d_comp = im3d_sc_x.copy()
        im3d_comp[edges3d>0] = 0
        threshold_global_otsu = threshold_otsu(im3d_comp[im3d_comp>0])

        # Find connected components in x direction
        from Source.util import tile_x, untile_x
        from scipy.ndimage.measurements import label
        bm3d = im3d_comp > 0
        bm2d = tile_x(bm3d)
        connected2d, n_components_x = label(bm2d)
        connected3d_x = untile_x(connected2d, bm3d.shape)

        # Calculate cluster averages
        cluster_size = np.bincount(connected3d_x.ravel())
        cluster_size[cluster_size==0] = 1
        cluster_sum = np.bincount(connected3d_x.ravel(), weights=im3d_sc_x.ravel())
        cluster_mean = cluster_sum/cluster_size
        cluster_mean[cluster_mean < threshold_global_otsu] = 0
        cluster_mean_x = cluster_mean[connected3d_x]

        # Merge the zeros into edges.
        edges3d[cluster_mean_x == 0] = 1

    # Find connected components in x direction
    im3d_comp = im3d_sc_x.copy()
    im3d_comp[edges3d>0] = 0
    bm3d = im3d_comp > 0
    bm2d = tile_x(bm3d)
    connected2d, n_components_x = label(bm2d)
    connected3d_x = untile_x(connected2d, bm3d.shape)

    # Fill holes in x
    slices_x = Parallel(n_jobs=12)(delayed(fill2d)(connected3d_x[xx,:,:])\
                                   for xx in range(connected3d_x.shape[0]))
    connected3d_x = np.dstack(slices_x)
    connected3d_x = np.transpose(connected3d_x, (2, 0, 1))

    # Find connected components in y
    bm3d = connected3d_x > 0
    bm2d = tile_y(bm3d)
    connected2d, n_components_y = label(bm2d)
    connected3d_y = untile_y(connected2d, bm3d.shape)

    # Fill holes in y
    slices_y = Parallel(n_jobs=12)(delayed(fill2d)(connected3d_y[:,yy,:])\
                                   for yy in range(connected3d_y.shape[1]))
    connected3d_y = np.dstack(slices_y)
    connected3d_y = np.transpose(connected3d_y, (0, 2, 1))

    # Find connected components in z
    bm3d = connected3d_y > 0
    bm2d = tile_z(bm3d)
    connected2d, n_components_z = label(bm2d)
    connected3d_z = untile_z(connected2d, bm3d.shape)

    # Fill holes in z
    slices_z = Parallel(n_jobs=12)(delayed(fill2d)(connected3d_z[:,:,zz])\
                                   for zz in range(connected3d_z.shape[2]))
    connected3d_z = np.dstack(slices_z)

    # Find connected components in x direction
    bm3d = connected3d_z > 0
    bm2d = tile_x(bm3d)
    connected2d, n_components_x = label(bm2d)
    connected3d_x = untile_x(connected2d, bm3d.shape)

    # Erode in x
    slices_x = Parallel(n_jobs=12)(delayed(erode2d)(connected3d_x[xx,:,:])\
                                   for xx in range(connected3d_x.shape[0]))
    connected3d_x = np.dstack(slices_x)
    connected3d_x = np.transpose(connected3d_x, (2, 0, 1))

    connected3d = connected3d_x

    # Now find 3d connections in the eroded 3d volume
    connected3d_eroded, n_components = connect3d(connected3d)

    # Remove small elements
    cluster_size = np.bincount(connected3d_eroded.ravel())
    cluster_size[0] = 0  # Remove bg
    cluster_size[cluster_size < 1000] = 0
    num_remaining = np.sum(cluster_size > 0)
    cluster_size[cluster_size > 0] = np.arange(1, num_remaining+1)
    connected3d_eroded = cluster_size[connected3d_eroded]

    # Dilate in x
    disk_size = 8
    selem = disk(disk_size)
    slices_x = Parallel(n_jobs=12)(delayed(dilate2d)(connected3d_eroded[xx,:,:], selem)\
                                   for xx in range(connected3d_eroded.shape[0]))
    connected3d_x = np.dstack(slices_x)
    connected3d_opened= np.transpose(connected3d_x, (2, 0, 1))

    connected3d_ws = apply_watershed(connected3d_opened)
    connected3d_final = connected3d_ws[::2,::2,::2]
    return connected3d_final


def get_bbox(im3d):
    # Calculate the bounding box
    # Returns a tuple with starting and end points
    # Access the bbox array with a[bbox[0][0]:bbox[1][0], bbox[0][1]:bbox[1][1], bbox[0][2]:bbox[1][2]]
    xyz_pos = np.where(im3d)
    xyz_min = [np.amin(x) for x in xyz_pos]
    xyz_max = [np.amax(x) for x in xyz_pos]
    bbox = (np.array(xyz_min), np.array(xyz_max)+1)
    # xyz_len = [x-y+1 for x,y in zip(xyz_max, xyz_min)]
    # bbox = (np.array(xyz_min), np.array(xyz_len))
    return bbox


from scipy.spatial import ConvexHull
def convex_hull_image_3d(im3d):
    # Solve the plane equation ax+by+cz+d = 0 for all points in the volume
    # hull.equations gives us [a, b, c, d] for all planes and the points are given as [x ,y, z, 1].
    # Select points such that they are in the bounding box but not a part of the object.
    # The sign of the dot product [a, b, c, d]*[x, y, z, 1].T tells us which side of the plane the point lies.
    # Assuming plane norms are pointing outwards, then the points with negative projection are inside the hull.
    if (np.sum(im3d) == 0):
        return np.zeros_like(im3d)
    bb_l, bb_h = get_bbox(im3d)
    im3d_bbox = im3d[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2]]
    points = np.vstack(np.where(im3d_bbox > 0)).T
    hull = ConvexHull(points)
    test3d_bbox = im3d_bbox == 0 
    abcd = hull.equations
    xyz1 = np.vstack((np.where(test3d_bbox), np.ones(np.sum(test3d_bbox), dtype=np.int)))
    proj = np.dot(abcd, xyz1)
    proj = proj <= 0
    inside = np.all(proj, axis=0)
    im3d_bbox[test3d_bbox] = inside
    out3d = np.zeros_like(im3d)
    out3d[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2]] = im3d_bbox 
    return out3d


from scipy.ndimage.morphology import binary_fill_holes
def fill_holes3d(im3d):
    iter_max = 1
    nx, ny, nz = im3d.shape
    out3d = im3d.copy()
    for iter_num in range(iter_max):
        sum_prev = np.sum(out3d)
        for xx in range(nx):
            bm = out3d[xx,:,:]
            if not np.any(bm):
                continue
            out3d[xx,:,:] = binary_fill_holes(bm)
        for yy in range(ny):
            bm = out3d[:,yy,:]
            if not np.any(bm):
                continue
            out3d[:,yy,:] = binary_fill_holes(bm)
        for zz in range(nz):
            bm = out3d[:,:,zz]
            if not np.any(bm):
                continue
            out3d[:,:,zz] = binary_fill_holes(bm)
        sum_current = np.sum(out3d)
        progress = sum_current-sum_prev
        if progress == 0:
            break
    return out3d


def umtWrite(filename, data):
    if data.dtype != np.uint8:
        print('Data has to be of type uint8')
        return
    headerStr = repr(data.ndim) + '\n' + \
                ' '.join([repr(x) for x in data.shape]) + ' \n'
    header = bytes(headerStr.encode())
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(bytes(data.ravel()))
        
def umtRead(filename):
    with open(filename, 'rb') as f:
        line = f.readline() # ndim
        line = f.readline() # shape
        data_shape = [int(x) for x in line.split()]
        data_size = np.prod(data_shape)
        data = np.fromstring(f.read(data_size), dtype=np.uint8).reshape(data_shape)
        return data


# Install pydicom package during setup
import dicom
import h5py
import sys
from glob import glob
def dicom2hdf5(dicom_path, output_path=None):
    dicom_list = glob(os.path.join(dicom_path, '*.dcm'))
    dicom_list += glob(os.path.join(dicom_path, '*.mag'))
    print(len(dicom_list) ,'files found')
    sys.stdout.flush()

    # Get metadata
    ds = dicom.read_file(dicom_list[0])
    rows = int(ds.Rows)
    cols = int(ds.Columns)
    fa = float(ds.FlipAngle)
    tr = float(ds.RepetitionTime)
    te = float(ds.EchoTime)
    x_spacing = float(ds.PixelSpacing[0])
    y_spacing = float(ds.PixelSpacing[1])
    if "SpacingBetweenSlices" in ds:
        z_spacing = float(ds.SpacingBetweenSlices)
    else:
        z_spacing = 0
    spacing = [x_spacing, y_spacing, z_spacing]
    slice_location = None
    num_slices = 0
    temporal_resolution = 0
    slice_location_set = set()
    trigger_time_set = set()
    img_list = []
    for i in range(len(dicom_list)):
        if i%(len(dicom_list)//10) == 0:
            print('\t' + str(i) + '/' + str(len(dicom_list)))
            sys.stdout.flush()
        ds = dicom.read_file(dicom_list[i])
        slice_location = ds.SliceLocation
        trigger_time = int(ds.TriggerTime) # ms
        slice_location_set.add(slice_location)
        trigger_time_set.add(trigger_time) # ms
        img_list.append((ds.pixel_array, slice_location, trigger_time, dicom_list[i]))
    print('\tDone')
    sys.stdout.flush()

    num_slices = len(slice_location_set)
    num_timepoints = len(trigger_time_set)
    trigger_times = sorted(trigger_time_set)
    if len(trigger_times) >= 2:
        temporal_resolution = trigger_times[1]-trigger_times[0]
    print('Triggers(ms):', trigger_times)
    data_shape = (rows, cols, num_slices, num_timepoints)
    if num_slices*num_timepoints != len(dicom_list):
        raise ValueError('Data size is inconsistent!')
    print('Data Shape =', data_shape)
    print('Spacing (mm) =', spacing)
    print('Temporal Res (ms) =', temporal_resolution)
    print('FA (deg) =', fa)
    print('TR (ms) =', tr)
    print('TE (ms) =', te)

    print('Sorting dicom data ...')
    sys.stdout.flush()
    img_list.sort(key=lambda x: (x[2],x[1]))

    sorted_dicom_list = [x[3] for x in img_list]
    img_list = [x[0] for x in img_list]

    data4d = np.zeros(data_shape, dtype=ds.pixel_array.dtype)
    for tt in range(num_timepoints):
        for zz in range(num_slices):
            data4d[:,:,zz,tt] = img_list[tt*num_slices + zz]
    print('Done')

    if output_path is not None:
        print('Saving output ...')
        sys.stdout.flush()
        with h5py.File(output_path, 'w') as f:
            dset = f.create_dataset('recon', data=data4d, compression='gzip')
            dset2 = f.create_dataset('shape', data=data_shape)
            dset3 = f.create_dataset('spacing', data=spacing)
            dset4 = f.create_dataset('temp_res', data=temporal_resolution)
            dset5 = f.create_dataset('fa', data=fa)
            dset6 = f.create_dataset('tr', data=tr)
            dset7 = f.create_dataset('te', data=te)
        print('Done')
        sys.stdout.flush()
    else:
        # Do not write out the contents of file.
        dataset = {}
        dataset['recon'] = data4d
        dataset['shape'] = data_shape
        dataset['spacing'] = spacing
        dataset['temp_res'] = temporal_resolution
        dataset['fa'] = fa
        dataset['tr'] = tr
        dataset['te'] = te
        dataset['dicom_list'] = sorted_dicom_list
        return dataset

def roi_export(filename, roi):
    if roi.dtype != np.uint8:
        print('ROI has to be of type uint8')
        return
    headerStr = repr(roi.ndim) + '\n' + \
                ' '.join([repr(x) for x in roi.shape]) + ' \n'
    header = bytes(headerStr.encode())
    with open(filename, 'wb') as f:
        f.write(header)
        for zz in range(roi.shape[-1]):
            f.write(bytes(roi[...,zz].ravel()))
