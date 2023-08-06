'''
param_bound:
submodule for setting default parameter boundary of
irf parameter, time zero and lifetime constant tau
:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''
from typing import Tuple, Union
import numpy as np


def set_bound_t0(t0: float, fwhm: Union[float, np.ndarray]) -> Tuple[float, float]:
    '''
    Setting bound for time zero

    Args:
     t0: initial guess for time zero
     fwhm: initial guess for full width at half maximum of instrumental response function
           `float` for gaussian and cauchy shape, `np.ndarray` with two element `(fwhm_G, fwhm_L)` for pseudo voigt shape.
    
    Returns:
     Tuple of upper and lower bound of time zero
    '''
    if not isinstance(fwhm, np.ndarray):
        bound = (t0-2*fwhm, t0+2*fwhm)
    else:
        fwhm_eff = 0.5346*fwhm[1] + \
                np.sqrt(0.2166*fwhm[1]**2+fwhm[0]**2)
        bound = (t0-2*fwhm_eff, t0+2*fwhm_eff)
    
    return bound

def set_bound_e0(e0: float, fwhm_G: float, fwhm_L: float) -> Tuple[float, float]:
    '''
    Setting bound for peak position and edge position

    Args:
     e0: initial guess for peak position
     fwhm_G: initial guess of fwhm_G parameter of voigt component
     fwhm_L: initial guess of fwhm_L parameter of voigt component
    
    Returns:
     Tuple of upper and lower bound of time zero
    '''
    if fwhm_G == 0:
        bound = (e0-fwhm_L/2, e0+fwhm_L/2)
    elif fwhm_L == 0:
        bound = (e0-fwhm_G/2, e0+fwhm_G/2)
    else:
        fwhm_eff = 0.5346*fwhm_L+np.sqrt(0.2166*fwhm_L**2+fwhm_G**2)
        bound = (e0-fwhm_eff/2, e0+fwhm_eff/2)
    
    return bound


def set_bound_tau(tau: float, fwhm: Union[float, np.ndarray]) -> Tuple[float, float]:
    '''
    Setting bound for lifetime constant

    Args:
      tau: initial guess for lifetime constant
      fwhm: initial guess for full width at half maximum of instrumental response function
           `float` for gaussian and cauchy shape, `np.ndarray` with two element `(fwhm_G, fwhm_L)` for pseudo voigt shape.

    Returns:
     Tuple of upper bound and lower bound of tau
    '''
    if not isinstance(fwhm, np.ndarray):
        fwhm_eff = fwhm
    else:
        fwhm_eff = 0.5346*fwhm[1] + \
                np.sqrt(0.2166*fwhm[1]**2+fwhm[0]**2)


    bound = (tau/2, 2*fwhm_eff)
    if fwhm_eff <= tau < 4*fwhm_eff:
        bound = (fwhm_eff/2, 8*fwhm_eff)
    elif 4*fwhm_eff <= tau < 16*fwhm_eff:
        bound = (2*fwhm_eff, 32*fwhm_eff)
    elif 16*fwhm_eff <= tau < 64*fwhm_eff:
        bound = (8*fwhm_eff, 128*fwhm_eff)
    elif 64*fwhm_eff <= tau < 256*fwhm_eff:
        bound = (32*fwhm_eff, 512*fwhm_eff)
    elif 256*fwhm_eff <= tau < 1024*fwhm_eff:
        bound = (128*fwhm_eff, 2048*fwhm_eff)
    elif 1024*fwhm_eff <= tau < 4096*fwhm_eff:
        bound = (512*fwhm_eff, 8192*fwhm_eff)
    elif 4096*fwhm_eff <= tau < 16384*fwhm_eff:
        bound = (2048*fwhm_eff, 32768*fwhm_eff)
    elif 16384*fwhm_eff <= tau < 65536*fwhm_eff:
        bound = (8192*fwhm_eff, 131072*fwhm_eff)
    elif 65536*fwhm_eff <= tau < 262144*fwhm_eff:
        bound = (32768*fwhm_eff, 524288*fwhm_eff)
    elif tau >= 262144*fwhm_eff:
        bound = (131072*fwhm_eff, 2*tau)
    return bound