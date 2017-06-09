import numpy as np

def preprocess(im4d):
	nx, ny, nz, nt = im4d.shape

	mean_signal = np.mean(im4d.reshape(-1, nt), axis=0)

	# Temporally align the signals
	onset_thresh = 0.02
	onset_thresh_val = onset_thresh*np.amax(mean_signal) + (1 - onset_thresh)*np.amin(mean_signal)
	onset = np.where(mean_signal <= onset_thresh_val)[0][-1]  # Last value before the threshold

	nt_new = 25  # number of time-points to analyze.

	# Truncate im4d to the new range
	new4d = np.abs(im4d[:, :, :, onset:onset+nt_new])

	return new4d