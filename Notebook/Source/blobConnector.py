import numpy as np
from scipy.spatial.distance import jaccard


def get_distance_list(blob_map):
    dist_list = []
    num_axial_slices = blob_map.shape[0]
    for xx in range(num_axial_slices-1):
        current_slice = blob_map[xx, :, :]
        next_slice = blob_map[xx+1, :, :]
        current_num_blobs = np.amax(current_slice)+1
        next_num_blobs = np.amax(next_slice)+1
        for cbb in range(1, current_num_blobs):
            current_blob = current_slice == cbb
            for nbb in range(1, next_num_blobs):
                next_blob = next_slice == nbb
                dist = jaccard(current_blob.ravel(), next_blob.ravel())
                if 1-dist:
                    dist_list.append(((xx, cbb), (xx+1, nbb), dist))
    return dist_list


def connect_blobs(blob_map, dist_list, threshold=1):
    connect_list = [x for x in dist_list if x[2] < threshold]
    connect_dict = {}
    token_list = []
    for connection in connect_list:
        blob_top = tuple(connection[0])
        blob_bottom = tuple(connection[1])
        if blob_top not in connect_dict:
            token_idx = len(token_list)
            token_val = len(token_list)
            token_list.append(token_val)
            connect_dict[blob_top] = token_idx
            token_val += 1
        if blob_bottom not in connect_dict:  # No collision
            connect_dict[blob_bottom] = connect_dict[blob_top]
        else:  # Collision: pick the smaller token value for both.
            idx1 = connect_dict[blob_bottom]
            idx2 = connect_dict[blob_top]
            token_val = min(token_list[idx1], token_list[idx2])
            token_list[idx1] = token_val
            token_list[idx2] = token_val

    token_to_blob = {}
    connected_blob_map = np.zeros_like(blob_map)
    num_axial_slices = blob_map.shape[0]
    blob_cnt = 1
    for xx in range(num_axial_slices):
        blob_map_slice = blob_map[xx, :, :]
        connected_slice = connected_blob_map[xx, :, :]
        num_blobs = np.amax(blob_map_slice)+1
        for bb in range(1, num_blobs):
            blob_tag = (xx, bb)
            if blob_tag in connect_dict:
                token_val = token_list[connect_dict[blob_tag]]
                if token_val not in token_to_blob:
                    token_to_blob[token_val] = blob_cnt
                    blob_cnt += 1
                blob_id = token_to_blob[token_val]
            else:
                blob_id = blob_cnt
                blob_cnt += 1
            connected_slice[blob_map_slice == bb] = blob_id
    return connected_blob_map


def filter_blobs(connected_blob_map, min_blob_size=1):
    blob_filter = np.bincount(connected_blob_map.ravel())
    num_blobs = blob_filter.shape[0]
    blob_cnt = 1
    blob_filter[0] = 0
    for cc in range(1, num_blobs):
        if blob_filter[cc] >= min_blob_size:
            blob_filter[cc] = blob_cnt
            blob_cnt += 1
        else:
            blob_filter[cc] = 0
    filtered_blob_map = blob_filter[connected_blob_map]
    return filtered_blob_map

