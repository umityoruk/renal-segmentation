import os
import errno
import dicom
import numpy as np

from Source.util import dicom2hdf5, roi_export
from Source.segmentation import renal_segment_v4
from Source.classification import make_predictions, relabel_predictions


def autoSegmentFromDicom(input_dir, output_dir=None, threshold_multiplier=1,
                         models_path=None, root_path=None):
	# ml_labels:    np.array containing the segmentation masks 
	#               0 = BG, 
	#               1 = Aorta (reserved)
	#               2 = L Cortex
	#               3 = R Cortex
	#               4 = L Medulla
	#               5 = R Medulla
	#               6 = L Collecting System
	#               7 = R Collecting System

	# dicom output: Dicom files containing the segmentation masks
	#               0 = BG, 
	#               300 = Aorta (reserved)
	#               350 = L Cortex
	#               400 = R Cortex
	#               450 = L Medulla
	#               500 = R Medulla
	#               550 = L Collecting System
	#               600 = R Collecting System

	# Setup the root_path and models_path if not given.
	if root_path is None:
		source_path = os.path.dirname(os.path.realpath(__file__))
		root_path = os.path.abspath(os.path.join(source_path, '..'))
	print('root_path =', root_path)
	if models_path is None:
		models_path = os.path.join(root_path, 'Models')
	print('models_path =', models_path)

	# Load the dataset from input_dir
	dataset = dicom2hdf5(input_dir)
	recon = dataset['recon']
	temp_res = dataset['temp_res']/1000 # Conversion from ms to s
	spacing = dataset['spacing']

	nx, ny, nz, nt = recon.shape

	# Subsampling factor for [x,y,z,t]
	ss_f = [2, 2, 2, 1]

	recon_ss = recon[::ss_f[0],::ss_f[1],::ss_f[2],::ss_f[3]]
	spacing = np.array([ss_f[0],ss_f[1],ss_f[2]])*spacing
	temp_res = temp_res*ss_f[3]

	print('Running GC segmentation ...')
	gc_labels_ss = renal_segment_v4(recon_ss, temp_res, spacing, threshold_multiplier=threshold_multiplier, root_path=root_path)

	gc_labels = np.repeat(np.repeat(np.repeat(gc_labels_ss, ss_f[0], axis=0), ss_f[1], axis=1), ss_f[2], axis=2)
	gc_labels = gc_labels[:nx, :ny, :nz]
	gc_labels = gc_labels.astype(np.uint8)
	print('GC segmentation completed.')

	print('Running ML segmentation ...')
	time_stamps = np.arange(nt)*temp_res
	prediction3d_ss = make_predictions(recon_ss, spacing, time_stamps, gc_labels_ss, models_path=models_path)
	prediction3d = np.repeat(np.repeat(np.repeat(prediction3d_ss, ss_f[0], axis=0), ss_f[1], axis=1), ss_f[2], axis=2)
	prediction3d = prediction3d[:nx, :ny, :nz]
	ml_labels = relabel_predictions(prediction3d, gc_labels)
	print('ML segmentation completed.')

	if output_dir is not None:
		print('Saving segmentation masks ...')	
		
		# Create the output directory
		try:
			os.makedirs(output_dir)
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise


		# Get the list of input files
		dicom_list = dataset['dicom_list']

		# Change series uid
		seriesInstanceUID = dicom.UID.generate_uid()
		# ds.SeriesInstanceUID = dicom.UID.generate_uid()

		for zz in range(ml_labels.shape[-1]):
			filename = os.path.join(output_dir, str(zz) + '.dcm')

			img = ml_labels[:,:,zz]
			pixel_array = img.astype(np.uint16)*50 + 250
			pixel_array[img==0] = 0

			ds = dicom.read_file(dicom_list[zz])
			ds.SeriesInstanceUID = seriesInstanceUID

			ds.SeriesDescription = 'Automatic_Segmentation_Maps'
			ds.InstanceNumber = zz+1
			ds.SOPInstanceUID = dicom.UID.generate_uid()

			ds.HighBit = 15
			ds.BitsStored = 16
			ds.BitsAllocated = 16

			if pixel_array.dtype != np.uint16:
				pixel_array = pixel_array.astype(np.uint16)
			ds.PixelData = pixel_array.tostring()

			ds.SmallestImagePixelValue = 0
			ds.LargestImagePixelValue = 600
			ds[0x0028,0x0106].VR = 'US' # Set value representation of SmallestImagePixelValue to unsigned short.
			ds[0x0028,0x0107].VR = 'US' # Set value representation of LargestImagePixelValue to unsigned short.
			ds.save_as(filename)

		print('Segmentation masks saved to "' + output_dir + '"')

	return recon, ml_labels

