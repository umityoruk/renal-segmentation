import numpy as np
from scipy.integrate import cumtrapz
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from Source.util import get_first_crossing_time

def fit_renal_model(aorta_c, kidney_c, temp_res = 3.62, mode='two_compartment'):
	if aorta_c.shape[0] != kidney_c.shape[0]:
		raise ValueError('AIF and Kidney signals should have the same length!')
	nt = aorta_c.shape[0]
	acq_time = np.arange(nt)*temp_res

	interp_step = -1
	if interp_step > 0:
		acq_time_ip = np.arange(0, acq_time[-1], interp_step)
		f_a = interp1d(acq_time, aorta_c, kind='cubic')
		f_k = interp1d(acq_time, kidney_c, kind='cubic')
		aorta_ip = f_a(acq_time_ip)
		aorta_ip[aorta_ip < 0] = 0
		kidney_ip = f_k(acq_time_ip)
		kidney_ip[kidney_ip < 0] = 0
	else:
		acq_time_ip = acq_time
		aorta_ip = aorta_c
		kidney_ip = kidney_c

	# Time syc
	t0_thresh = 0.10  # threshold for starting time t0
	# before_t0 = int(5/interp_step)
	# after_t0 = int(90/interp_step)
	t0 = int(get_first_crossing_time(aorta_ip.reshape(1,-1), t0_thresh))
	# aorta_sync = aorta_ip[(t0-before_t0):(t0+after_t0)]
	# kidney_sync = kidney_ip[(t0-before_t0):(t0+after_t0)]
	# acq_time_sync = np.arange(0, before_t0+after_t0)*interp_step

	acq_time_sync = acq_time_ip
	aorta_sync = aorta_ip
	kidney_sync = kidney_ip

	xdata = np.vstack([acq_time_sync.ravel(), aorta_sync.ravel()]).T

	mode = mode.lower()
	if mode == 'two_compartment':
		if interp_step > 0:
			step_size = interp_step
		else:
			step_size = temp_res
		t_end = min(t0 + np.floor(300/step_size).astype(np.int), acq_time_sync.shape[0])
		# print(t_end)
		acq_time_sync = acq_time_sync[:t_end]
		aorta_sync = aorta_sync[:t_end]
		kidney_sync = kidney_sync[:t_end]
		xdata = np.vstack([acq_time_sync.ravel(), aorta_sync.ravel()]).T
		param_opt, chisqr = two_compartment_fit(acq_time_sync, aorta_sync, kidney_sync, chisqr=True)
		(C_fit, C_art, C_tub) = two_compartment_detailed(xdata, param_opt[0], param_opt[1], param_opt[2], param_opt[3])
	elif mode == 'three_compartment':
		param_opt, chisqr = three_compartment_fit(acq_time_sync, aorta_sync, kidney_sync, chisqr=True)
		(C_fit, C_art, C_tub) = three_compartment_detailed(xdata, param_opt[0], param_opt[1], param_opt[2], param_opt[3], param_opt[4])
	else:
		print('Invalid mode:', mode)
		raise ValueError('Invalid mode:' + mode)
	# ktrans = param_opt[0]

	
	y = kidney_sync

	param = {}
	param['param_opt'] = param_opt
	param['chisqr'] = chisqr
	param['xdata'] = xdata
	param['y'] = y
	param['mode'] = mode
	param['C_fit'] = C_fit
	param['C_art'] = C_art
	param['C_tub'] = C_tub


	return param


def two_compartment_detailed(xdata, ktrans_m, vb, delta, t_fwhm):
	# xdata is nt-by-2 matrix (first_col = time [s], second_col = Cb [mM])
	# Cb is the concentration of contrast in blood (i.e. AIF)
	# ktrans - transfer coefficient [1/min]
	# vb - blood fraction []
	# delta - delay of the Gaussian VIRF [s]
	# t_fwhm - full-width-half-maximum of the Gaussian VIRF [s]

	# if t_fwhm <= 0 or ktrans <= 0 or vb <= 0:
	# 	return np.zeros(xdata.shape[0])
	# delta = np.abs(delta)

	t = xdata[:, 0]
	Cb_art = xdata[:, 1]

	hct_large = 0.41
	hct_small = 0.24

	# Convert Ktrans to s^-1
	ktrans = np.abs(ktrans_m/60)

	# Calculate plasma concentration in Aorta
	Cp_art = Cb_art/(1-hct_large)

	# Calculate VIRF
	filter_width = 40  # seconds
	t_filter = t[t<=filter_width]  # limit the length
	g = np.exp(-(4*np.log(2))*((t_filter-delta)/t_fwhm)**2)
	g_area = np.sum(g)
	if g_area > 0:
		g /= np.sum(g)

	# Calculate delayed and dispersed AIF
	Cp_kid = np.convolve(Cp_art, g, mode='full')[:t.shape[0]]

	Cp_kid_integral = cumtrapz(Cp_kid, x=t, initial=0)

	vd_Cd = ktrans*Cp_kid_integral

	Ct = vb*(1-hct_small)*Cp_kid + vd_Cd

	# return Ct
	return (Ct, vb*(1-hct_small)*Cp_kid, vd_Cd)


def two_compartment(xdata, ktrans_m, vb, delta, t_fwhm):
	# xdata is nt-by-2 matrix (first_col = time [s], second_col = Cb [mM])
	# Cb is the concentration of contrast in blood (i.e. AIF)
	# ktrans - transfer coefficient [1/min]
	# vb - blood fraction []
	# delta - delay of the Gaussian VIRF [s]
	# t_fwhm - full-width-half-maximum of the Gaussian VIRF [s]

	# if t_fwhm <= 0 or ktrans <= 0 or vb <= 0:
	# 	return np.zeros(xdata.shape[0])
	# delta = np.abs(delta)

	(C_roi, C_art, C_tub) = two_compartment_detailed(xdata, ktrans_m, vb, delta, t_fwhm)
	return C_roi


from lmfit import minimize, Parameters, Parameter, report_fit
def two_compartment_fit(t, Cb, C_kidney, chisqr=False):
	params = Parameters()
	# params.add('ktrans', value=0.3, min=0)
	# params.add('vb', value=0.4, min=0)
	# params.add('delta', value=1, min=0, max=20)
	# params.add('t_fwhm', value=1, min=0.01)

	# params.add('ktrans', value=0.25, min=0)
	# params.add('vb', value=0.4, min=0)
	# params.add('delta', value=0, min=0, max=3)
	# params.add('t_fwhm', value=1, min=0.01)
	
	params.add('ktrans', value=0.66, min=0)
	params.add('vb', value=0.4, min=0)
	params.add('delta', value=0, min=0, max=10)
	params.add('t_fwhm', value=1, min=0.01)

	# # Single search
	# xdata = np.vstack([t.ravel(), Cb.ravel()]).T
	# result = minimize(two_compartment_cost_func, params, args=(xdata, C_kidney))

	# Random search
	best_chisqr = None
	best_result = None
	for i in range(300):
		params = Parameters()
		params.add('ktrans', value=np.random.randint(10)/10, min=0)
		params.add('vb', value=0.4, min=0)
		params.add('delta', value=np.random.randint(50), min=0, max=50)
		params.add('t_fwhm', value=1, min=0.01)

		# ktrans_fixed = 0.558273053571
		# params = Parameters()
		# params.add('ktrans', value=ktrans_fixed, min=ktrans_fixed, max=ktrans_fixed+1e-12)
		# params.add('vb', value=0.4, min=0)
		# params.add('delta', value=np.random.randint(50), min=0, max=50)
		# params.add('t_fwhm', value=1, min=0.01)

		xdata = np.vstack([t.ravel(), Cb.ravel()]).T
		result = minimize(two_compartment_cost_func, params, args=(xdata, C_kidney))

		if best_chisqr is None or result.chisqr < best_chisqr:
			best_chisqr = result.chisqr
			best_result = result
	result = best_result


	# # Grid Search
	# ktrans_list = np.linspace(0, 1, num=20)
	# vb_list = [0.4]
	# delta_list = np.linspace(0, 50, num=20)
	# t_fwhm_list = [1]
	# best_chisqr = None
	# best_result = None
	# for ktrans_init in ktrans_list:
	# 	for vb_init in vb_list:
	# 		for delta_init in delta_list:
	# 			for t_fwhm_init in t_fwhm_list:
	# 				params = Parameters()
	# 				params.add('ktrans', value=ktrans_init, min=0)
	# 				params.add('vb', value=vb_init, min=0)
	# 				params.add('delta', value=delta_init, min=0, max=50)
	# 				params.add('t_fwhm', value=t_fwhm_init, min=0.01)

	# 				# ktrans_fixed = 0.558273053571
	# 				# params = Parameters()
	# 				# params.add('ktrans', value=ktrans_fixed, min=ktrans_fixed, max=ktrans_fixed+1e-12)
	# 				# params.add('vb', value=vb_init, min=0)
	# 				# params.add('delta', value=delta_init, min=0, max=50)
	# 				# params.add('t_fwhm', value=t_fwhm_init, min=0.01)

	# 				xdata = np.vstack([t.ravel(), Cb.ravel()]).T
	# 				result = minimize(two_compartment_cost_func, params, args=(xdata, C_kidney))

	# 				if best_chisqr is None or result.chisqr < best_chisqr:
	# 					best_chisqr = result.chisqr
	# 					best_result = result
	# result = best_result
	

	param_opt = [result.params['ktrans'].value, 
				result.params['vb'].value,
				result.params['delta'].value,
				result.params['t_fwhm'].value]
	
	if chisqr:
		return param_opt, result.chisqr
	return param_opt


def two_compartment_cost_func(params, xdata, ydata):
	ktrans = params['ktrans'].value
	vb = params['vb'].value
	delta = params['delta'].value
	t_fwhm = params['t_fwhm'].value
	y_model = two_compartment(xdata, ktrans, vb, delta, t_fwhm)
	return y_model - ydata



def three_compartment_detailed(xdata, ktrans, k12, fa, tau, d):
	# xdata is nt-by-2 matrix (first_col = time [s], second_col = Cb [mM])
	# Cb is the concentration of contrast in blood (i.e. AIF)
	# ktrans - ktrans transfer coefficient [1/min]
	# k12 - transfer coefficient [1/min]
	# fa - blood fraction []
	# tau - delay of the AIF [s]
	# d - dispersion of the AIF [s]

	t = xdata[:, 0]
	Cb_art = xdata[:, 1]

	hct = 0.41

	# Convert Ktrans to s^-1
	k21 = np.abs(ktrans/60)
	k12 = np.abs(k12/60)

	# Calculate plasma concentration in Aorta
	Ca = Cb_art/(1-hct)

	# Apply delay (tau) to AIF
	Ca_delayed = Ca
	if tau > 1e-6:
		numpad = np.sum(t < tau)
		offset = t[numpad] - tau
		# offset = 0 # DEBUG REMOVE LATER
		if offset > 0:
			t_offset = t[:-1] + offset
			f_interp = interp1d(t, Ca, kind='linear')
			Ca_offset = f_interp(t_offset)
		else:
			Ca_offset = Ca
		Ca_delayed = np.hstack([np.zeros(numpad), Ca_offset])


	# Apply dispersion (d) to delayed AIF
	Ca_prime = Ca_delayed
	if (d > 0):
		filter_cutoff = 4*d  # seconds (4 time constants)
		t_filter = t[t<=filter_cutoff]  # limit the length
		g = 1/d*np.exp(-t_filter/d)
		g_area = np.sum(g)
		if g_area > 0:
			g /= g_area
		# Colvolve delayed AIF with dispersion filter
		Ca_prime = np.convolve(Ca_delayed, g, mode='full')[:t.shape[0]]

	# Apply lossy (k12) integration on the AIF (leakage to the third compartment)
	filter_cutoff = 4/k12 # seconds (4 time constants)
	t_filter = t[t<=filter_cutoff]  # limit the length
	g = np.exp(-t_filter*k12) # exponential decay over time
	# g = np.ones(t_filter.shape) # DEBUG REMOVE LATER
	# g_area = np.sum(g)
	# if g_area > 0:
	# 	g /= g_area
	Ca_prime_integral = (t[1])*np.convolve(Ca_prime, g, mode='full')[:t.shape[0]]

	C_roi = fa*Ca_prime + k21*Ca_prime_integral


	# Ca_prime = Ca_prime[:t.shape[0]]
	# Cp_kid_integral = cumtrapz(Ca_prime, x=t, initial=0)
	# vd_Cd = ktrans*Cp_kid_integral
	# Ct = fa*(1-hct)*Ca_prime + vd_Cd

	return (C_roi, fa*Ca_prime, k21*Ca_prime_integral)
	# return Ct



def three_compartment(xdata, ktrans, k12, fa, tau, d):
	# xdata is nt-by-2 matrix (first_col = time [s], second_col = Cb [mM])
	# Cb is the concentration of contrast in blood (i.e. AIF)
	# ktrans - ktrans transfer coefficient [1/min]
	# k12 - transfer coefficient [1/min]
	# fa - blood fraction []
	# tau - delay of the AIF [s]
	# d - dispersion of the AIF [s]
	(C_roi, C_art, C_tub) = three_compartment_detailed(xdata, ktrans, k12, fa, tau, d)
	return C_roi


def three_compartment_fit(t, Cb, C_kidney, chisqr=False):
	params = Parameters()

	# params.add('ktrans', value=0.9, min=0)
	# params.add('k12', value=0.9, min=0)
	# params.add('fa', value=0.35, min=0)
	# params.add('tau', value=0, min=0, max=10)
	# params.add('d', value=5, min=0)

	params.add('ktrans', value=0.66, min=0)
	params.add('k12', value=1.6, min=0)
	params.add('fa', value=0.4, min=0)
	params.add('tau', value=2.4, min=0, max=10)
	params.add('d', value=2.5, min=0)
	
	xdata = np.vstack([t.ravel(), Cb.ravel()]).T
	# result = minimize(three_compartment_cost_func, params, args=(xdata, C_kidney))	

	best_chisqr = None
	best_result = None
	for i in range(100):
		params = Parameters()
		params.add('ktrans', value=np.random.randint(10)/10, min=0)
		params.add('k12', value=np.random.randint(20)/10, min=0)
		params.add('fa', value=0.4, min=0)
		params.add('tau', value=np.random.randint(10), min=0, max=10)
		params.add('d', value=2.5, min=0)

		result = minimize(three_compartment_cost_func, params, args=(xdata, C_kidney))

		if best_chisqr is None or result.chisqr < best_chisqr:
			best_chisqr = result.chisqr
			best_result = result
	result = best_result


	param_opt = [result.params['ktrans'].value, 
				result.params['k12'].value,
				result.params['fa'].value,
				result.params['tau'].value,
				result.params['d'].value]
	
	if chisqr:
		return param_opt, result.chisqr
	return param_opt


def three_compartment_cost_func(params, xdata, ydata):
	ktrans = params['ktrans'].value
	k12 = params['k12'].value
	fa = params['fa'].value
	tau = params['tau'].value
	d = params['d'].value
	y_model = three_compartment(xdata, ktrans, k12, fa, tau, d)
	return y_model - ydata





# PARTIAL VOLUME MODEL #
from Source.util import SI2C
def fit_renal_model_pv(SIaorta, SIkidney, TR, FA, temp_res = 3.62, mode='two_compartment'):
	if SIaorta.shape[1] != SIkidney.shape[1]:
		raise ValueError('AIF and Kidney signals should have the same length!')
	nt = SIaorta.shape[1]
	acq_time = np.arange(nt)*temp_res

	hct_large = 0.41
	hct_small = 0.24
	r1 = 4.5 # s^-1 * mM^-1
	T10_blood = 1.4 # s
	T10_kidney = 1.2 # s

	other_params = {}
	other_params['hct_large'] = hct_large
	other_params['hct_small'] = hct_small
	other_params['TR'] = TR
	other_params['FA'] = FA
	other_params['r1'] = r1
	other_params['T10_blood'] = T10_blood
	other_params['T10_kidney'] = T10_kidney


	# Partial volume hct correction
	# Assume no enhancement in the rbc volume
	baseline_rbc = SIaorta[:,0]*hct_large
	SIaorta_plasma = SIaorta - baseline_rbc.reshape(-1,1)

	baseline = np.mean(SIaorta_plasma[:,0].astype(np.double))
	Cp_full = SI2C(SIaorta_plasma.astype(np.double), TR, FA, T10_blood, r1, baseline=baseline)
	Cp = np.mean(Cp_full, axis=0) # plasma concentration
	baseline_blood = baseline/(1-hct_large) # Average baseline for a full voxel.

	other_params['baseline_blood'] = baseline_blood

	mode = mode.lower()
	if mode == 'two_compartment':
		xdata = np.vstack([acq_time.ravel(), Cp.ravel()]).T
		param_opt, chisqr = two_compartment_fit_pv(acq_time, Cp, SIkidney, other_params, chisqr=True)
		# (C_fit, C_art, C_tub) = two_compartment_detailed(xdata, param_opt[0], param_opt[1], param_opt[2], param_opt[3])
	elif mode == 'three_compartment':
		xdata = np.vstack([acq_time.ravel(), Cp.ravel()]).T
		param_opt, chisqr = three_compartment_fit(acq_time_sync, aorta_sync, kidney_sync, chisqr=True)
		(C_fit, C_art, C_tub) = three_compartment_detailed(xdata, param_opt[0], param_opt[1], param_opt[2], param_opt[3], param_opt[4])
	else:
		print('Invalid mode:', mode)
		return -1, -1

	# ktrans = param_opt[0]
	
	# y = SIkidney

	param = {}
	param['param_opt'] = param_opt
	param['chisqr'] = chisqr
	param['xdata'] = xdata
	# param['y'] = y
	param['mode'] = mode
	# param['C_fit'] = C_fit
	# param['C_art'] = C_art
	# param['C_tub'] = C_tub


	return param


def two_compartment_fit_pv(t, Cp, SIkidney, other_params, chisqr=False):
	params = Parameters()
	
	params.add('ktrans', value=0.66, min=0)
	params.add('vp', value=0.4, min=0, max=0.6)
	params.add('delta', value=0, min=0, max=10)
	params.add('t_fwhm', value=1, min=0.01)

	# best_chisqr = None
	# best_result = None
	# for i in range(100):
	# 	params = Parameters()
	# 	params.add('ktrans', value=np.random.randint(10)/10, min=0)
	# 	params.add('vb', value=0.4, min=0)
	# 	params.add('delta', value=np.random.randint(10), min=0, max=10)
	# 	params.add('t_fwhm', value=1, min=0.01)

	# 	xdata = np.vstack([t.ravel(), Cb.ravel()]).T
	# 	result = minimize(two_compartment_cost_func, params, args=(xdata, C_kidney))

	# 	if best_chisqr is None or result.chisqr < best_chisqr:
	# 		best_chisqr = result.chisqr
	# 		best_result = result
	# result = best_result

	xdata = np.vstack([t.ravel(), Cp.ravel()]).T
	result = minimize(two_compartment_cost_func_pv, params, args=(xdata, SIkidney, other_params))


	param_opt = [result.params['ktrans'].value, 
				result.params['vp'].value,
				result.params['delta'].value,
				result.params['t_fwhm'].value]
	
	if chisqr:
		return param_opt, result.chisqr
	return param_opt


def two_compartment_cost_func_pv(params, xdata, SIkidney, other_params):
	Cd, Ctubule = two_compartment_advanced_pv(params, xdata, SIkidney, other_params)

	return Cd - Ctubule


def two_compartment_advanced_pv(params, xdata, SIkidney, other_params):
	ktrans = params['ktrans'].value
	vp = params['vp'].value
	delta = params['delta'].value
	t_fwhm = params['t_fwhm'].value
	Ct, vp_Ckp, vd_Cd = two_compartment_detailed_pv(xdata, ktrans, vp, delta, t_fwhm)

	baseline_blood = other_params['baseline_blood']
	hct_small = other_params['hct_small']
	TR = other_params['TR']
	FA = other_params['FA']
	r1 = other_params['r1']
	T10_kidney = other_params['T10_kidney']
	T10_blood = other_params['T10_blood']

	Ckp = vp_Ckp/vp
	vb = vp/(1-hct_small)
	vd = 1-vb
	Cd = vd_Cd/vd

	# Calculate signal from arterial compartment
	baseline_rbc = baseline_blood*vb*hct_small
	baseline_plasma = baseline_blood*vb*(1-hct_small)

	SIrbc = baseline_rbc
	SIplasma = C2SI(Ckp, baseline_plasma, T10_blood, TR, FA, r1)
	SIblood = SIrbc + SIplasma
	SItubule = SIkidney - SIblood.reshape(1,-1)

	voxel_mask = np.sum(SItubule <= 0, axis=1) == 0  # discard voxels that have negative signal intensity.

	baseline = np.mean(SItubule[voxel_mask, 0].astype(np.double))
	Ctubule_full = SI2C(SItubule[voxel_mask, :].astype(np.double), TR, FA, T10_kidney, r1, baseline=baseline)
	Ctubule = np.mean(Ctubule_full, axis=0)*(np.sum(voxel_mask)/voxel_mask.shape[0])

	# Cd from model, Ctubule from data
	return (Cd, Ctubule)


def two_compartment_detailed_pv(xdata, ktrans_m, vp, delta, t_fwhm):
	# xdata is nt-by-2 matrix (first_col = time [s], second_col = Cp [mM])
	# Cp is the concentration of contrast in plasma (hct corrected)
	# ktrans - transfer coefficient [1/min]
	# vp - plasma fraction []
	# delta - delay of the Gaussian VIRF [s]
	# t_fwhm - full-width-half-maximum of the Gaussian VIRF [s]

	# if t_fwhm <= 0 or ktrans <= 0 or vb <= 0:
	# 	return np.zeros(xdata.shape[0])
	# delta = np.abs(delta)

	t = xdata[:, 0]
	Cp_art = xdata[:, 1]

	# Convert Ktrans to s^-1
	ktrans = np.abs(ktrans_m/60)

	# Calculate VIRF
	filter_width = 40  # seconds
	t_filter = t[t<=filter_width]  # limit the length
	g = np.exp(-(4*np.log(2))*((t_filter-delta)/t_fwhm)**2)
	g_area = np.sum(g)
	if g_area > 0:
		g /= np.sum(g)

	# Calculate delayed and dispersed AIF
	Cp_kid = np.convolve(Cp_art, g, mode='full')[:t.shape[0]]

	Cp_kid_integral = cumtrapz(Cp_kid, x=t, initial=0)

	vd_Cd = ktrans*Cp_kid_integral

	vp_Ckp = vp*Cp_kid # kidney plasma concentration

	Ct =  vp_Ckp + vd_Cd

	return (Ct, vp_Ckp, vd_Cd)


def C2SI(C, SI0, T10, TR, FA_rad, r1):
	# C => mM
    # SI0 => unitless (initial signal level)
    # T10 => s
    # TR => s
    # FA_rad => rad
    # r1 => s^-1 * mM^-1
    
    R10 = 1/T10
    R1 = R10 + r1*C
    T1 = 1/R1

    S0 = SI0 * (1-np.exp(-TR/T1[0])*np.cos(FA_rad)) / ((1-np.exp(-TR/T1[0]))*np.sin(FA_rad))
    SI = S0 * ((1-np.exp(-TR/T1))*np.sin(FA_rad)) / (1-np.exp(-TR/T1)*np.cos(FA_rad))
    
    return SI
