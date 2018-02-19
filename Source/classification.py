import numpy as np
import os
import pickle
import warnings

from scipy import interpolate 
from scipy.ndimage.morphology import distance_transform_edt
from sklearn.ensemble import RandomForestClassifier

from Source.util import convex_hull_image_3d, get_bbox, get_first_crossing_time


def get_model(models_path, num_feats):
  # Fetches the model mathcing the number of features specified.
  # model_filename = os.path.join(os.getcwd(), '../Model', 'subsegment_model_f' + str(num_feats) + '.pkl')
  model_filename = os.path.join(models_path, 'subsegment_model_f' + str(num_feats) + '.pkl')
  with open(model_filename, 'rb') as f:
    with warnings.catch_warnings():
      warnings.simplefilter("ignore", category=UserWarning)
      model = pickle.load(f)
  return model

def make_predictions(im4d, spacing, time_stamps, kidney_labels3d, models_path):
  # im4d:           np.array containing the dynamic images [x,y,z,t].
  # spacing:        np.array containing the spatial resolution [x,y,z]
  # time_stamps:    np.array containing the time stamps corresponding to the last axis of im4d in seconds.
  # kidney_mask3d:  np.array containing the bulk kidney masks obtained from GrabCut (1 = left, 2 = right).

  # Get the shape of the dataset.
  nx, ny, nz, nt = im4d.shape

  if time_stamps.shape[0] != nt:
    raise ValueError("time_stamps should have the same length as the last dimension of im4d!")

  # Allocate output
  prediction3d = np.zeros((nx, ny, nz), dtype=np.int)

  # Process each kidney
  features_list = []
  for label_id in np.unique(kidney_labels3d):
    if label_id == 0: # Background
      continue

    # Calculate the bounding box of the kidney
    kidney_mask = kidney_labels3d == label_id
    bbox = get_bbox(kidney_mask)

    # Extract data from the bounding box
    bb_l, bb_h = bbox
    im4d_bbox = im4d[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2], :].copy()
    kidney_mask_bbox = kidney_mask[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2]].copy()

    nx_bb, ny_bb, nz_bb = kidney_mask_bbox.shape

    features = extract_features(im4d_bbox, spacing, time_stamps, kidney_mask_bbox)
    
    num_feats = features.shape[1]
    model = get_model(models_path, num_feats)
    classifier = model['classifier']
    X_mean = model['mean']
    X_std = model['std']

    X_test = features.copy()
    X_test -= X_mean
    X_test /= X_std

    pred_test = classifier.predict(X_test)
    pred_test = pred_test*kidney_mask_bbox.ravel()

    pred_labels3d = pred_test.reshape(nx_bb, ny_bb, nz_bb)

    prediction3d_bbox = prediction3d[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2]]
    prediction3d_bbox[pred_labels3d > 0] = pred_labels3d[pred_labels3d > 0]
    
  return prediction3d


def relabel_predictions(prediction3d, gc_labels3d):
  # Relabel kidney regions
  # 0 - background
  # 1 - aorta
  # 2 - left cortex
  # 3 - right cortex
  # 4 - left medulla
  # 5 - right medulla
  # 6 - left collecting system
  # 7 - right collecting system
  nx, ny, nz = prediction3d.shape
  y_centers = []
  for i in range(1, np.amax(gc_labels3d)+1):
    y_center = np.mean(np.where(gc_labels3d==i)[1])
    y_centers.append((i, y_center))
  y_centers = sorted(y_centers, key=lambda x: x[1])
  label_offsets = []
  if len(y_centers) == 1:
    y_center = y_centers[0]
    if y_center[1] > ny//2:
      offset = 0
    else:
      offset = 1
    label_offsets.append((y_center[0], offset))
  elif len(y_centers) == 2:
    label_offsets.append((y_centers[0][0], 1))
    label_offsets.append((y_centers[1][0], 0))
  else:
    print('Number of kindeys out of handling capability!')

  ml_labels3d = np.zeros_like(gc_labels3d)
  for label_offset in label_offsets:
    gc_select, offset = label_offset
    gc_mask = gc_labels3d == gc_select
    for subseg_select in range(1,4):
      subseg_mask = prediction3d == subseg_select
      ml_labels3d[gc_mask * subseg_mask] = subseg_select*2 + offset

  return ml_labels3d



def extract_features(im4d, spacing, time_stamps, kidney_mask):
  # im4d:           np.array containing the dynamic images [x,y,z,t].
  # spacing:        np.array containing the spatial resolution [x,y,z]
  # time_stamps:    np.array containing the time stamps corresponding to the last axis of im4d in seconds.
  # kidney_mask:    np.array containing the bulk kidney mask obtained from GrabCut.

  # Get the shape of the dataset.
  nx, ny, nz, nt = im4d.shape

  if time_stamps.shape[0] != nt:
    raise ValueError("time_stamps should have the same length as the last dimension of im4d!")

  # # Generate a convex hull for each kidney.
  # convex_hull_labels3d = np.zeros_like(kidney_labels3d)
  # for label_id in np.unique(kidney_labels3d):
  #   if label_id == 0: # Background
  #     continue
  #   label_mask = kidney_labels3d == label_id
  #   convex_hull_labels3d[convex_hull_image_3d(label_mask)] = label_id

  # Typically this function is called on the bounding box surrounding one kidney.
  im4d_bbox = im4d
  kidney_mask_bbox = kidney_mask

  # Convert data to 8-bit integer representation for faster processing.
  im4d_bbox[im4d_bbox < 0] = 0 # clip negative values if exists.
  if issubclass(im4d_bbox.dtype.type, np.integer):
    # Use look up table for quantization
    lut = np.arange(np.amax(im4d_bbox)+1).astype(np.float)
    lut = (lut/np.amax(lut)*255).astype(np.uint8)
    im4d_bbox = lut[im4d_bbox]
  else:
    im4d_bbox /= np.amax(im4d_bbox)
    im4d_bbox = (im4d_bbox*255).astype(np.uint8)

  sig = im4d_bbox.reshape(-1, nt)
  mean_sig = np.mean(sig, axis=0, keepdims=True)
  t_10_percent = get_first_crossing_time(mean_sig, 0.10)[0]
  t_10_percent = np.floor(t_10_percent).astype(np.int)
  t_start = max(t_10_percent, 0)

  # We can take samples every 30s upto 150s + the starting time.
  num_temporal_samples = min((time_stamps[-1] - time_stamps[t_start])//30, 5)+1
  sampling_times = time_stamps[t_start] + np.arange(num_temporal_samples)*30 # seconds

  # Interpolate the signal at sampling times
  sig_interpolator = interpolate.interp1d(time_stamps, sig)
  sig_samples = sig_interpolator(sampling_times)

  # Whiten the features to reduce intersubject variability.
  sig_samples -= np.mean(sig_samples, axis=0, keepdims=True)
  sig_samples /= np.std(sig_samples, axis=0, keepdims=True)

  # Calculate the depth of voxels from the surface of the kidney.
  dist = distance_transform_edt(kidney_mask_bbox, sampling=spacing).reshape(-1, 1)

  features = np.hstack((sig_samples, dist))
  return features


# def extract_labels(labels3d):
#   ## INPUT ##
#   # labels3d:     np.array containing the hand labeled segmentation masks 
#   #               0 = BG, 
#   #               1 = Aorta (optional)
#   #               2 = L Cortex
#   #               3 = R Cortex
#   #               4 = L Medulla
#   #               5 = R Medulla
#   #               6 = L Collecting System
#   #               7 = R Collecting System
#   ## OUTPUT ##
#   # labels:     1D labels array for classification for each voxel within the bounding box of each kidney.
#   #             0 = BG
#   #             1 = Cortex
#   #             2 = Medulla
#   #             3 = Collecting System

#   # Combine labels (Cortex + Medulla + CS) from each kiney for bounding box calculation.
#   kidney_labels3d = get_bulk_kidney_labels(labels3d)

#   # Combine L and R for each class of voxels (Cortex, Medulla, and CS).
#   class_labels3d = get_classification_labels(labels3d)

#   # Process each kidney
#   class_labels_list = []
#   for label_id in np.unique(kidney_labels3d):
#     if label_id == 0: # Background
#       continue

#     # Calculate the bounding box of the kidney
#     kidney_mask = kidney_labels3d == label_id
#     bbox = get_bbox(kidney_mask)

#     # Extract data from the bounding box
#     bb_l, bb_h = bbox
#     class_labels3d_bbox = class_labels3d[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2]].copy()
#     class_labels_list.append(class_labels3d_bbox.ravel())
#   class_labels = np.hstack(class_labels_list)
#   return class_labels


def extract_features_and_labels(im4d, spacing, time_stamps, labels3d):
  ## INPUT ##
  # im4d:         np.array containing the dynamic images [x,y,z,t].
  # spacing:      np.array containing the spatial resolution [x,y,z]
  # time_stamps:  np.array containing the time stamps corresponding to the last axis of im4d in seconds.
  # labels3d:     np.array containing the hand labeled segmentation masks 
  #               0 = BG, 
  #               1 = Aorta (optional)
  #               2 = L Cortex
  #               3 = R Cortex
  #               4 = L Medulla
  #               5 = R Medulla
  #               6 = L Collecting System
  #               7 = R Collecting System
  ## OUTPUT ##
  # features:     Extracted features for all voxels within bounding box of the kidneys (one row per voxel).
  # labels:       Corresponding label for each row of features.
  #               0 = BG
  #               1 = Cortex
  #               2 = Medulla
  #               3 = Collecting System

  # Combine labels (Cortex + Medulla + CS) from each kiney for feature extractor.
  kidney_labels3d = get_bulk_kidney_labels(labels3d)

  # Combine L and R for each class of voxels (Cortex, Medulla, and CS).
  class_labels3d = get_classification_labels(labels3d)

  # Process each kidney
  features_list = []
  labels_list = []
  for label_id in np.unique(kidney_labels3d):
    if label_id == 0: # Background
      continue

    # Calculate the bounding box of the kidney
    kidney_mask = kidney_labels3d == label_id
    bbox = get_bbox(kidney_mask)

    # Extract data from the bounding box
    bb_l, bb_h = bbox
    im4d_bbox = im4d[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2], :].copy()
    kidney_mask_bbox = kidney_mask[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2]].copy()
    class_labels3d_bbox = class_labels3d[bb_l[0]:bb_h[0], bb_l[1]:bb_h[1], bb_l[2]:bb_h[2]].copy()

    features_list.append(extract_features(im4d_bbox, spacing, time_stamps, kidney_mask_bbox))
    labels_list.append(class_labels3d_bbox.ravel())

  features = np.vstack(features_list)
  labels = np.hstack(labels_list)
  return features, labels

def get_classification_labels(labels3d):
  # Relabel the data as 1 = Cortex, 2 = Medulla, and 3 = Collecting System
  class_labels3d = np.zeros_like(labels3d)
  class_labels3d[labels3d == 2] = 1
  class_labels3d[labels3d == 3] = 1
  class_labels3d[labels3d == 4] = 2
  class_labels3d[labels3d == 5] = 2
  class_labels3d[labels3d == 6] = 3
  class_labels3d[labels3d == 7] = 3
  return class_labels3d

def get_bulk_kidney_labels(labels3d):
  # Combine labels (Cortex + Medulla + CS) from each kiney for feature extractor.
  kidney_labels3d = np.zeros_like(labels3d)
  kidney_labels3d[labels3d == 2] = 1
  kidney_labels3d[labels3d == 4] = 1
  kidney_labels3d[labels3d == 6] = 1
  kidney_labels3d[labels3d == 3] = 2
  kidney_labels3d[labels3d == 5] = 2
  kidney_labels3d[labels3d == 7] = 2
  return kidney_labels3d
