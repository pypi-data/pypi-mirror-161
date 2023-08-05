#!/usr/bin/python

import numpy as np
from scipy.interpolate import interp1d, interp2d

def oxy_b(dt, tau):
    inv_b = 1 + 2*(tau/dt)
    return 1/inv_b

def oxy_a(dt, tau):
    return 1 - 2*oxy_b(dt, tau)

def correct_response_time_Tconst(t, DO, tau):

    # array for the loop
    N = DO.shape[0]
    mean_oxy  = np.array((N-1)*[np.nan])
    mean_time = np.array((N-1)*[np.nan])

    # convert time to seconds
    t_sec = t*24*60*60

    # loop through oxygen data
    for i in range(N-1):
        dt = t_sec[i+1] - t_sec[i]

        # do the correction using the mean filter, get the mean time
        mean_oxy[i]  = (1/(2*oxy_b(dt, tau)))*(DO[i+1] - oxy_a(dt, tau)*DO[i])
        mean_time[i] = t_sec[i] + dt/2
    
    # interpolate back to original times for output
    f = interp1d(mean_time, mean_oxy, kind='linear', bounds_error=False, fill_falue='extrapolate')
    DO_out = f(t_sec)

    return DO_out

from lut import lut as lut_data

def correct_response_time(t, DO, T, thickness):

    # convert time to seconds
    t_sec = t*24*60*60

    # array for the loop
    N = DO.shape[0]
    mean_oxy  = np.array((N-1)*[np.nan])
    mean_time = t_sec[:-1] + np.diff(t_sec)/2
    mean_temp = T[:-1] + np.diff(T)/2

    # load temperature, boundary layer thickness, and tau matrix from 
    # look-up table provided in the supplement to Bittig and Kortzinger (2017)
    lut_lL = lut_data[0,1:]
    lut_T  = lut_data[1:,0]
    tau100 = lut_data[1:,1:]
    thickness = thickness*np.ones((N-1,))

    # translate boundary layer thickness to temperature dependent tau
    f_thickness = interp2d(lut_T, lut_lL, tau100.T, bounds_error=False)
    tau_T = np.squeeze(f_thickness(mean_temp, thickness))[0,:]
    # loop through oxygen data 
    for i in range(N-1):
        dt = t_sec[i+1] - t_sec[i]

        # do the correction using the mean filter, get the mean time
        mean_oxy[i]  = (1/(2*oxy_b(dt, tau_T[i])))*(DO[i+1] - oxy_a(dt, tau_T[i])*DO[i])
    
    # interpolate back to original times for output
    f = interp1d(mean_time, mean_oxy, kind='linear', bounds_error=False, fill_value='extrapolate')
    DO_out = f(t_sec)

    return DO_out

def sample_Tconst(t, DO, tau):
    # convert time to seconds
    t_sec = t*24*60*60

    N = DO.shape[0]
    c_filt = np.nan*np.ones((N,))
    c_filt[0] = DO[0]

    for i in range(N-1):
        dt = t_sec[i+1] - t_sec[i]
        c_filt[i+1] = oxy_a(dt, tau)*c_filt[i] + oxy_b(dt, tau)*(DO[i+1]+DO[i])
    
    return c_filt

def sample(t, DO, T, thickness):
    # convert time to seconds
    t_sec = t*24*60*60

    mean_temp = T[:-1] + np.diff(T)/2

    N = DO.shape[0]
    c_filt = np.nan*np.ones((N,))
    c_filt[0] = DO[0]

    # load temperature, boundary layer thickness, and tau matrix from 
    # look-up table provided in the supplement to Bittig and Kortzinger (2017)
    lut_lL = lut_data[0,1:]
    lut_T  = lut_data[1:,0]
    tau100 = lut_data[1:,1:]
    thickness = thickness*np.ones((N-1,))

    # translate boundary layer thickness to temperature dependent tau
    f_thickness = interp2d(lut_T, lut_lL, tau100.T, bounds_error=False)
    tau_T = np.squeeze(f_thickness(mean_temp, thickness))[0,:]
    # loop through oxygen data 
    for i in range(N-1):
        dt = t_sec[i+1] - t_sec[i]

        c_filt[i+1] = oxy_a(dt, tau_T[i])*c_filt[i] + oxy_b(dt, tau_T[i])*(DO[i+1]+DO[i])
    
    return c_filt