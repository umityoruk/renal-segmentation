import numpy as np
from skimage.measure import regionprops
from scipy.ndimage import uniform_filter


def extractFeatures(im4d):
    nx, ny, nz, nt = im4d.shape

    # Flatten signal from the time-points of interest.
    sig = im4d.reshape(-1, nt)

    # Percent Signal Change
    psc_raw = get_psc(sig)

    # Normalize the dataset to account for injection and baseline differences
    sig = normalize_range(sig)

    # Percent Signal Change
    psc = get_psc(sig)

    # Mean signal for normalization
    mean_sig = np.mean(sig, axis=0, keepdims=True)

    # t_ref = get_first_crossing_time(mean_sig, 0.10)
    t_10 = get_first_crossing_time(sig, 0.10)
    t_50 = get_first_crossing_time(sig, 0.50)
    t_90 = get_first_crossing_time(sig, 0.90)

    # Add voxel coordinates
    ind = np.arange(nx*ny*nz)
    pos_z = ind%nz
    pos_y = (ind//nz)%ny
    pos_x = (ind//(ny*nz))%nx
    pos = np.vstack([pos_x, pos_y, pos_z]).T

    # features = np.hstack([pos, sig/mean_sig, t_10, t_50, t_90])
    # sig_norm = sig/(np.sqrt(np.sum(sig**2, axis=1, keepdims=True))+0.00001)
    # mean_sig_norm = np.mean(sig_norm, axis=0, keepdims=True)
    features = np.hstack([pos, psc_raw, psc, sig, t_10, t_50, t_90])
    return features


from scipy.ndimage.filters import median_filter, maximum_filter
def extractMedSegFeatures(im4d):
    nx, ny, nz, nt = im4d.shape

    res = np.array([1.7, 1.4, 2.4])  # image resolution in mm
    ctx_thickness = 11 # mm
    str_radius = np.round((ctx_thickness/2)/res).astype(np.int)

    im3d = np.mean(np.diff(im4d.astype(np.float), axis=3), axis=3)
    im3d_filt = maximum_filter(im3d, size=2*str_radius)

    # Flatten signal from the time-points of interest.
    sig = im4d.reshape(-1, nt)
    mean_sig = np.mean(sig, axis=0, keepdims=True)

    t_95 = get_first_crossing_time(mean_sig, 0.95)[0, 0]
    t_start = np.ceil(t_95)

    im4d_diff = np.diff(im4d[:,:,:,t_start:].astype(float), axis=3)
    mean_slope3d = np.mean(im4d_diff, axis=3)
    
    feat_slope = mean_slope3d.reshape(-1, 1)
    feat_slope -= np.mean(feat_slope)
    feat_slope /= np.std(feat_slope)

    feat_median = im3d_filt.reshape(-1, 1)
    feat_median -= np.mean(feat_median)
    feat_median /= np.std(feat_median)

    # # Add voxel coordinates
    # ind = np.arange(nx*ny*nz)
    # pos_z = ind%nz
    # pos_y = (ind//nz)%ny
    # pos_x = (ind//(ny*nz))%nx
    # pos = np.vstack([pos_x, pos_y, pos_z]).T

    features = np.hstack([feat_slope, feat_median])
    return features


def normalize_range(sig):
	mean_sig = np.mean(sig, axis=0)
	sig_norm = sig/np.amin(mean_sig)
	mean_sig /= np.amin(mean_sig)
	sig_norm -= 1
	mean_sig -= 1
	sig_norm /= np.amax(mean_sig)
	sig_norm += 1
	sig_norm[sig_norm<0] = 0
	return sig_norm


def get_psc(sig):
	sig_base = np.amin(sig, axis=1, keepdims=True)
	psc = (sig-sig_base)/(sig_base+0.00001)
	psc[sig_base[:,0]==0, :] = 0
	return psc


# MOVED TO "util.py"
# def get_first_crossing_time(sig, thresh_frac):
# 	M, N = sig.shape
# 	sig_min = np.amin(sig, axis=1, keepdims=True)
# 	sig_max = np.amax(sig, axis=1, keepdims=True)
# 	sig_thresh = sig_min + thresh_frac*(sig_max-sig_min)
# 	first_over = np.argmax(np.diff((sig > sig_thresh).astype('int'), axis=1), axis=1) + 1
# 	first_below = first_over - 1
# 	val_over = sig[np.arange(M), first_over]
# 	val_below = sig[np.arange(M), first_below]
# 	val_range = val_over - val_below
# 	frac_below = (val_over - sig_thresh.ravel())/(val_range + 0.00001)
# 	frac_below[val_range == 0] = 0
# 	first_crossing = first_over - frac_below
# 	return first_crossing.reshape(-1, 1)


# def extractFeaturesWithHog(im4d, hog4d, cell_size):
#     nx, ny, nz, nt = im4d.shape

#     # Expand HOG to the same shape as im4d
#     cell_size = 8  # 8x8 pixels per cell
    
#     border_size = (block_size//2)*cell_size
#     hog_expand = np.zeros([nx, ny, nz, hog4d.shape[-1]])
#     for zz in range(hog4d.shape[2]):
#     	for i in range(hog4d.shape[0]):
#     		for j in range(hog4d.shape[1]):
#     			hog_expand[border_size+i*cell_size:border_size+(i+1)*cell_size, 
#     			border_size+j*cell_size:border_size+(j+1)*cell_size, zz, :] = hog4d[i, j, zz, :]

#     hog_expand = np.concatenate([im4d, hog_expand], axis=3)

#   	# Flatten signal from the time-points of interest.
#     sig = hog_expand.reshape(-1, hog_expand.shape[3])
#     features = sig
#     return features


def hog_feature(im):
  """Compute Histogram of Gradient (HOG) feature for an image
  
       Modified from skimage.feature.hog
       http://pydoc.net/Python/scikits-image/0.4.2/skimage.feature.hog
     
     Reference:
       Histograms of Oriented Gradients for Human Detection
       Navneet Dalal and Bill Triggs, CVPR 2005
     
    Parameters:
      im : an input grayscale or rgb image
      
    Returns:
      feat: Histogram of Gradient (HOG) feature
    
  """
  
  # convert rgb to grayscale if needed
  if im.ndim == 3:
    image = rgb2gray(im)
  else:
    image = np.at_least_2d(im)

  sx, sy = image.shape # image size
  orientations = 9 # number of gradient bins
  cx, cy = (8, 8) # pixels per cell

  gx = np.zeros(image.shape)
  gy = np.zeros(image.shape)
  gx[:, :-1] = np.diff(image, n=1, axis=1) # compute gradient on x-direction
  gy[:-1, :] = np.diff(image, n=1, axis=0) # compute gradient on y-direction
  grad_mag = np.sqrt(gx ** 2 + gy ** 2) # gradient magnitude
  grad_ori = np.arctan2(gy, (gx + 1e-15)) * (180 / np.pi) + 90 # gradient orientation

  n_cellsx = int(np.floor(sx / cx))  # number of cells in x
  n_cellsy = int(np.floor(sy / cy))  # number of cells in y
  # compute orientations integral images
  orientation_histogram = np.zeros((n_cellsx, n_cellsy, orientations))
  for i in range(orientations):
    # create new integral image for this orientation
    # isolate orientations in this range
    temp_ori = np.where(grad_ori < 180 / orientations * (i + 1),
                        grad_ori, 0)
    temp_ori = np.where(grad_ori >= 180 / orientations * i,
                        temp_ori, 0)
    # select magnitudes for those orientations
    cond2 = temp_ori > 0
    temp_mag = np.where(cond2, grad_mag, 0)
    orientation_histogram[:,:,i] = uniform_filter(temp_mag, size=(cx, cy))[cx/2:sx-cx/2+1:cx, cy/2:sy-cy/2+1:cy]
  
  return orientation_histogram


def appendHogFeatures(subject_features, subject_hog4d, cell_size):
	# The first 3 features are position
	block_size = 4 # 4x4 cells per patch (i.e. 32x32 image patch)
	pos = subject_features[:,:3]
	hog_x, hog_y = get_hog_xy_position(pos[:,0], pos[:,1], cell_size, block_size)
	hog_z = pos[:,2]

	# Clip out-of-bounds positions
	hx, hy, hz, ho = subject_hog4d.shape
	hog_x[hog_x<0] = 0
	hog_y[hog_y<0] = 0
	hog_x[hog_x>hx-block_size] = hx-block_size
	hog_y[hog_y>hy-block_size] = hy-block_size


	hog_block_ind = np.zeros([hog_x.shape[0], 3*block_size*block_size], dtype='int32')
	cell_cnt = 0
	for i in range(block_size):
		for j in range(block_size):
			hog_block_ind[:, 3*cell_cnt+0] = hog_x + i
			hog_block_ind[:, 3*cell_cnt+1] = hog_y + j
			hog_block_ind[:, 3*cell_cnt+2] = hog_z
			cell_cnt += 1

	hog_block_ind = hog_block_ind.reshape(-1,3)

	hog_feat = subject_hog4d[hog_block_ind[:,0],hog_block_ind[:,1],hog_block_ind[:,2],:]
	hog_feat = hog_feat.reshape(-1, ho*block_size*block_size)

	# Apply L2 block normalization
	hog_feat /= np.sqrt(np.sum(hog_feat*hog_feat, axis=1, keepdims=True) + 0.00001)

	return np.hstack([subject_features, hog_feat])


def get_hog_xy_position(row, col, cell_size, block_size):
    x = row//(cell_size//2)
    x -= (block_size-1)
    x = x//2
    
    y = col//(cell_size//2)
    y -= (block_size-1)
    y = y//2
    return (x, y)



def appendHog5dFeatures(subject_features, subject_hog5d, cell_size):
	# The first 3 features are position
	block_size = 4 # 4x4 cells per patch (i.e. 32x32 image patch)
	pos = subject_features[:,:3]
	hog_x, hog_y, hog_o = get_hog_xyo_position(pos[:,0], pos[:,1], cell_size, block_size)
	hog_z = pos[:,2]

	# Clip out-of-bounds positions
	hx, hy, hz, hoff, ho = subject_hog5d.shape
	hog_x[hog_x<0] = 0
	hog_y[hog_y<0] = 0
	hog_x[hog_x>hx-block_size] = hx-block_size
	hog_y[hog_y>hy-block_size] = hy-block_size


	hog_block_ind = np.zeros([hog_x.shape[0], 4*block_size*block_size], dtype='int32')
	cell_cnt = 0
	for i in range(block_size):
		for j in range(block_size):
			hog_block_ind[:, 4*cell_cnt+0] = hog_x + i
			hog_block_ind[:, 4*cell_cnt+1] = hog_y + j
			hog_block_ind[:, 4*cell_cnt+2] = hog_z
			hog_block_ind[:, 4*cell_cnt+3] = hog_o
			cell_cnt += 1

	hog_block_ind = hog_block_ind.reshape(-1,4)

	hog_feat = subject_hog5d[hog_block_ind[:,0],hog_block_ind[:,1],hog_block_ind[:,2],hog_block_ind[:,3],:]
	hog_feat = hog_feat.reshape(-1, ho*block_size*block_size)

	# Apply L2 block normalization
	hog_feat /= np.sqrt(np.sum(hog_feat*hog_feat, axis=1, keepdims=True) + 0.00001)

	return np.hstack([subject_features, hog_feat])


def get_hog_xyo_position(row, col, cell_size, block_size):
 	x = row//(cell_size//2)
 	x -= block_size
 	x = x//2

 	y = col//(cell_size//2)
 	y -= block_size
 	y = y//2

 	border = block_size/2*cell_size
 	off_x = (row-border)%cell_size
 	off_y = (col-border)%cell_size
 	offset = off_x*cell_size+off_y
 	return (x.astype('int'), y.astype('int'), offset.astype('int'))