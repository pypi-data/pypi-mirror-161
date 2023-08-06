'''
res_thy:
submodule for residual function and dfient for fitting static spectrum with the
sum of voigt broadened theoretical spectrum, edge function and base function

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''
from typing import Optional
import numpy as np
from numpy.polynomial.legendre import legval
from ..mathfun.A_matrix import fact_anal_A
from ..mathfun.peak_shape import voigt_thy, edge_gaussian, edge_lorenzian
from ..mathfun.peak_shape import deriv_voigt_thy, deriv_edge_gaussian, deriv_edge_lorenzian

def residual_thy(x0: np.ndarray, policy: str, thy_peak: np.ndarray, edge: Optional[str] = None,
                 base_order: Optional[int] = None, 
                 e: np.ndarray = None, 
                 intensity: np.ndarray = None, eps: np.ndarray = None) -> np.ndarray:
    '''
    residual_thy
    `scipy.optimize.least_squares` compatible vector residual function for fitting static spectrum with the 
    sum of voigt broadend theoretical spectrum, edge function base function

    Args:
     x0: initial parameter

      * 1st and 2nd: fwhm_G and fwhm_L

      if policy == 'scale':

      * 3rd: peak_scale

      if policy == 'shift':

      * 3rd: peak_shift

      if policy == 'both':

      * 3rd: peak_shift
      * 4th: peak_scale

      if edge is not None:
      
      * :math:`{last}-1`: edge position
      * last: fwhm of edge

     policy ({'shift', 'scale', 'both'}): Policy to match discrepency 
      between experimental data and theoretical spectrum.

      * 'shift' : Default option, shift peak position by peak_factor
      * 'scale' : scale peak position by peak_factor
      * 'both' : both shift and scale peak postition, peak_factor should be a tuple of `shift_factor` and `scale_factor`.

     thy_peak: theoretically calculated peak position and intensity
     edge ({'g', 'l'}): type of edge shape function
      if edge is not set, it does not include edge function.
     base_order (int): polynomial order of baseline function
      if base_order is not set, it does not include baseline function.
     e: 1d array of energy points of data (n,)
     intensity: intensity of static data (n,)
     eps: estimated error of data (n,)

    Returns:
     Residucal vector
    
    Note:
     * If fwhm_G of ith voigt component is zero then it is treated as lorenzian function with fwhm_L
     * If fwhm_L of ith voigt component is zero then it is treated as gaussian function with fwhm_G

    '''
    x0 = np.atleast_1d(x0)

    if policy in ['scale', 'shift']:
        peak_factor = x0[2]
    elif policy == 'both':
        peak_factor = np.ndarray([x0[2], x0[3]])
    
    tot_comp = 1
    
    if edge is not None:
        tot_comp = tot_comp+1
    if base_order is not None:
        tot_comp = tot_comp+base_order+1
    
    A = np.empty((tot_comp, e.size))

    A[0, :] = voigt_thy(e, thy_peak, x0[0], x0[1], peak_factor, policy)
    
    base_start = 1
    if edge is not None:
        base_start = base_start+1
        if edge == 'g':
            A[1, :] = edge_gaussian(e-x0[-2], x0[-1])
        elif edge == 'l':
            A[1, :] = edge_lorenzian(e-x0[-2], x0[-1])
    
    if base_order is not None:
        e_max = np.max(e); e_min = np.min(e)
        e_norm = 2*(e-(e_max+e_min)/2)/(e_max-e_min)
        tmp = np.eye(base_order+1)
        A[base_start:, :] = legval(e_norm, tmp, tensor=True)
    
    c = fact_anal_A(A, intensity, eps)

    chi = (c@A-intensity)/eps

    return chi

def res_grad_thy(x0: np.ndarray, policy: str, thy_peak: np.ndarray, edge: Optional[str] = None,
                 base_order: Optional[int] = None, 
                 fix_param_idx: Optional[np.ndarray] = None,
                 e: np.ndarray = None, 
                 intensity: np.ndarray = None, eps: np.ndarray = None) -> np.ndarray:
    '''
    res_grad_thy
    `scipy.optimize.minimize` compatible scalar residual function and its gradient for fitting static spectrum with the 
    sum of voigt broadend theoretical spectrum, edge function base function

    Args:
     x0: initial parameter

      * 1st and 2nd: fwhm_G and fwhm_L

      if policy == 'scale':

      * 3rd: peak_scale

      if policy == 'shift':

      * 3rd: peak_shift

      if policy == 'both':

      * 3rd: peak_shift
      * 4th: peak_scale

      if edge is not None:
      
      * :math:`{last}-1`: edge position
      * last: fwhm of edge

     policy ({'shift', 'scale', 'both'}): Policy to match discrepency 
      between experimental data and theoretical spectrum.

      * 'shift' : Default option, shift peak position by peak_factor
      * 'scale' : scale peak position by peak_factor
      * 'both' : both shift and scale peak postition, peak_factor should be a tuple of `shift_factor` and `scale_factor`.

     thy_peak: theoretically calculated peak position and intensity
     edge ({'g', 'l'}): type of edge shape function
      if edge is not set, it does not include edge function.
     base_order (int): polynomial order of baseline function
      if base_order is not set, it does not include baseline function.
     fix_param_idx: idx for fixed parameter (masked array for `x0`)
     e: 1d array of energy points of data (n,)
     intensity: intensity of static data (n,)
     eps: estimated error of data (n,)

    Returns:
     Tuple of scalar residual function :math:`(\\frac{1}{2}\\sum_i {res}^2_i)` and its gradient
    
    Note:
     * If fwhm_G of ith voigt component is zero then it is treated as lorenzian function with fwhm_L
     * If fwhm_L of ith voigt component is zero then it is treated as gaussian function with fwhm_G

    '''
    x0 = np.atleast_1d(x0)

    if policy in ['scale', 'shift']:
        peak_factor = x0[2]
    elif policy == 'both':
        peak_factor = np.ndarray([x0[2], x0[3]])
    
    tot_comp = 1
    
    if edge is not None:
        tot_comp = tot_comp+1
    if base_order is not None:
        tot_comp = tot_comp+base_order+1
    
    A = np.empty((tot_comp, e.size))

    A[0, :] = voigt_thy(e, thy_peak, x0[0], x0[1], peak_factor, policy)
    
    base_start = 1
    if edge is not None:
        base_start = base_start+1
        if edge == 'g':
            A[1, :] = edge_gaussian(e-x0[-2], x0[-1])
        elif edge == 'l':
            A[1, :] = edge_lorenzian(e-x0[-2], x0[-1])
    
    if base_order is not None:
        e_max = np.max(e); e_min = np.min(e)
        e_norm = 2*(e-(e_max+e_min)/2)/(e_max-e_min)
        tmp = np.eye(base_order+1)
        A[base_start:, :] = legval(e_norm, tmp, tensor=True)
    
    c = fact_anal_A(A, intensity, eps)
    chi = (c@A - intensity)/eps
    df = np.empty((intensity.size, x0.size))

    deriv_thy = c[0]*deriv_voigt_thy(e, thy_peak, x0[0], x0[1], peak_factor, policy)
    df[:, :2] = deriv_thy[:, :2]
    if policy in ['scale', 'shift']:
        df[:, 2] = deriv_thy[:, 2]
    elif policy == 'both':
        df[:, 2:4] = deriv_thy[:, 2:] 

    if edge is not None:
        if edge == 'g':
            df_edge = c[1]*deriv_edge_gaussian(e-x0[-2], x0[-1])
        elif edge == 'l':
            df_edge = c[1]*deriv_edge_lorenzian(e-x0[-2], x0[-1]) 
        
        df[:, -2] = -df_edge[:, 0]
        df[:, -1] = df_edge[:, 1]
    
    df = np.einsum('i,ij->ij', 1/eps, df)

    df[:, fix_param_idx] = 0

    return np.sum(chi**2)/2, chi@df