import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import widgets
from IPython.display import display, clear_output
import warnings
from skimage.morphology import binary_erosion, disk

def overlayShow(recon, overlay3d, zz=0, tt=0, th=0, oa=1, oe=True, im_range=None, o_range=None, out=None):
	plt.figure(figsize=(12,9))
	if im_range is None:
		im_min = np.amin(recon)
		im_max = np.amax(recon)
	else:
		im_min = im_range[0]
		im_max = im_range[1]
	im = recon[:,:,zz,tt]
	plt.imshow(im, interpolation='none', cmap=plt.cm.gray, vmin=im_min, vmax=im_max)
	# plt.imshow(recon[:,:,zz,tt], interpolation='none', cmap=plt.cm.gray)
	if oe:
		if overlay3d.ndim == 4: # Temporary feature for convenience
			overlay_im = overlay3d[:,:,zz,tt]
		else:
			overlay_im = overlay3d[:,:,zz]
		overlay_im_masked = overlay_im < th
		if not np.all(overlay_im_masked):
			overlay_mask = np.ma.masked_where(overlay_im_masked, overlay_im)
			if o_range is None:
				o_min = np.amin(overlay3d)
				o_max = np.amax(overlay3d)
			else:
				o_min = o_range[0]
				o_max = o_range[1]
			plt.imshow(overlay_mask, interpolation='none', cmap=plt.cm.jet, vmin=o_min, vmax=o_max, alpha=oa)
			# overlay_border = overlay_im > th
			# overlay_border[binary_erosion(overlay_border, disk(1))] = 0
			# overlay_border_mask = np.ma.masked_where(overlay_border <= 0, overlay_border)
			# plt.imshow(overlay_border_mask, interpolation='none', cmap=plt.cm.terrain, vmin=o_min, vmax=o_max)
	# Display the plot in the output widget (if given)
	if out != None:
		ax=plt.gca()
		with out:
			clear_output(wait=True)
			display(ax.figure)
		plt.close()

def overlayViewer(im4d, overlay3d, zz=0, tt=0, th=0, oa=1, im_range=None, o_range=None):
	tt_enable = True
	if im4d.ndim == 3:
	    im4d = im4d[:,:,:,np.newaxis]
	    tt_enable = False
	out = widgets.Output()
	zz_slider = widgets.IntSlider(min=0, max=im4d.shape[2]-1, step=1, value=zz)
	tt_slider = widgets.IntSlider(min=0, max=im4d.shape[3]-1, step=1, value=tt)
	oa_slider = widgets.FloatSlider(min=0, max=1, step=0.1, value=oa)
	if issubclass(overlay3d.dtype.type, np.integer) or overlay3d.dtype == np.bool:
		th = 1
		th_slider = widgets.IntSlider(min=np.amin(overlay3d), max=np.amax(overlay3d), step=1, value=th)
		th_slider.visible = False
		oa_slider.visible = True
	else:
		th_slider = widgets.FloatSlider(min=np.amin(overlay3d), max=np.amax(overlay3d), step=0.01, value=th)
		oa_slider.visible = False
	overlay_button = widgets.ToggleButton(description='Overlay', value=True)
	if not tt_enable:
		tt_slider.visible = False
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')
		w = widgets.interactive(overlayShow, recon=widgets.fixed(im4d), overlay3d=widgets.fixed(overlay3d), 
		              zz=zz_slider, tt=tt_slider, th=th_slider, oa=oa_slider, oe=overlay_button, 
		              im_range=widgets.fixed(im_range), o_range=widgets.fixed(o_range), out=widgets.fixed(out))
	wo = widgets.HBox(children=(w,out))
	display(wo)


def reconShow(recon, zz, tt, rgb=False, out=None):
    plt.figure(figsize=(12,9))
    if not rgb:
    	im_min = np.amin(recon)
    	im_max = np.amax(recon)
    	plt.imshow(recon[:,:,zz,tt], interpolation='none', cmap=plt.cm.gray, vmin=im_min, vmax=im_max)
    else:
    	plt.imshow(recon[:,:,zz,:], interpolation='none')
    # Display the plot in the output widget (if given)
    if out != None:
	    ax=plt.gca()
	    with out:
	    	clear_output(wait=True)
	    	display(ax.figure)
	    plt.close()

def reconViewer(im4d, zz=0, tt=0, rgb=False):
	tt_enable = True
	if im4d.ndim == 3:
	    im4d = im4d[:,:,:,np.newaxis]
	    tt_enable = False
	if rgb:
		tt_enable = False
	out = widgets.Output()
	zz_slider = widgets.IntSlider(min=0, max=im4d.shape[2]-1, step=1, value=zz)
	tt_slider = widgets.IntSlider(min=0, max=im4d.shape[3]-1, step=1, value=tt)
	if not tt_enable:
		tt_slider.visible = False
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')
		w = widgets.interactive(reconShow, recon=widgets.fixed(im4d), zz=zz_slider, tt=tt_slider, 
								rgb=widgets.fixed(rgb), out=widgets.fixed(out))
	wo = widgets.HBox(children=(w,out))
	display(wo)
