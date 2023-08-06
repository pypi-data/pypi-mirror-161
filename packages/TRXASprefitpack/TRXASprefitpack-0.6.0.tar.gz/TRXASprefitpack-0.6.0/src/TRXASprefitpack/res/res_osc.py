'''
res_osc:
submodule for residual function and gradient for fitting time delay scan with the
convolution of sum of damped oscillation and instrumental response function 

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

from typing import Tuple, Optional, Sequence
import numpy as np
from ..mathfun.irf import calc_eta, deriv_eta
from ..mathfun.irf import calc_fwhm, deriv_fwhm
from ..mathfun.A_matrix import make_A_matrix_gau_osc, make_A_matrix_cauchy_osc, fact_anal_A
from ..mathfun.exp_conv_irf import deriv_dmp_osc_sum_conv_gau, deriv_dmp_osc_sum_conv_cauchy

# residual and gradient function for damped oscillation model 

def residual_dmp_osc(x0: np.ndarray, num_comp: int, irf: str, 
                    t: Optional[Sequence[np.ndarray]] = None, 
                    intensity: Optional[Sequence[np.ndarray]] = None, eps: Optional[Sequence[np.ndarray]] = None) -> np.ndarray:
    '''
    residual_dmp_osc
    `scipy.optimize.least_squares` compatible gradient of vector residual function for fitting multiple set of time delay scan with the
    sum of convolution of damped oscillation and instrumental response function  

    Args:
     x0: initial parameter,
      if irf == 'g','c':

        * 1st: fwhm_(G/L)
        * 2nd to :math:`2+N_{scan}`: time zero of each scan
        * :math:`2+N_{scan}+i`: time constant of each damped oscillation
        * :math:`2+N_{scan}+N_{osc}+i`: period of each damped oscillation

      if irf == 'pv':

        * 1st and 2nd: fwhm_G, fwhm_L
        * 3rd to :math:`3+N_{scan}`: time zero of each scan
        * :math:`3+N_{scan}+i`: time constant of each damped oscillation
        * :math:`3+N_{scan}+N_{osc}+i`: period of each damped oscillation
           
     num_comp: number of damped oscillation component
     irf: shape of instrumental response function

          * 'g': normalized gaussian distribution,
          * 'c': normalized cauchy distribution,
          * 'pv': pseudo voigt profile :math:`(1-\\eta)g(f) + \\eta c(f)`

        For pseudo voigt profile, the mixing parameter :math:`\\eta(f_G, f_L)` and
        uniform fwhm paramter :math:`f(f_G, f_L)` are calculated by `calc_eta` and `calc_fwhm` routine
     t: time points for each data set
     intensity: sequence of intensity of datasets
     eps: sequence of estimated error of datasets
    
    Returns:
     Residual vector
    '''

    x0 = np.atleast_1d(x0)
    
    if irf in ['g', 'c']:
        num_irf = 1
        fwhm = x0[0]
    else:
            num_irf = 2
            fwhm = calc_fwhm(x0[0], x0[1])
            eta = calc_eta(x0[0], x0[1])

    num_t0 = 0; sum = 0
    for d in intensity:
        num_t0 = d.shape[1] + num_t0
        sum = sum + d.size
    
    chi = np.empty(sum)
    
    tau = x0[num_irf+num_t0:num_irf+num_t0+num_comp]
    period = x0[num_irf+num_t0+num_comp:num_irf+num_t0+2*num_comp]

    end = 0; t0_idx = num_irf
    for ti,d,e in zip(t,intensity,eps):
        for j in range(d.shape[1]):
            t0 = x0[t0_idx]
            if irf == 'g':
                A = make_A_matrix_gau_osc(ti-t0, fwhm, 1/tau, period)
            elif irf == 'c':
                A = make_A_matrix_cauchy_osc(ti-t0, fwhm, 1/tau, period)
            else:
                A_gau = make_A_matrix_gau_osc(ti-t0, fwhm, 1/tau, period)
                A_cauchy = make_A_matrix_cauchy_osc(ti-t0, fwhm, 1/tau, period)
                A = A_gau + eta*(A_cauchy-A_gau)
            c = fact_anal_A(A, d[:,j], e[:,j])
            chi[end:end+d.shape[0]] = ((c@A) - d[:, j])/e[:, j]

            end = end + d.shape[0]
            t0_idx = t0_idx + 1

    return chi
    
def res_grad_dmp_osc(x0: np.ndarray, num_comp: int, irf: str, 
                     fix_param_idx: Optional[np.ndarray] = None,
                     t: Optional[Sequence[np.ndarray]] = None, 
                     intensity: Optional[Sequence[np.ndarray]] = None, 
                     eps: Optional[Sequence[np.ndarray]] = None) -> Tuple[np.ndarray, np.ndarray]:
    '''
    res_grad_dmp_osc
    scipy.optimize.minimize compatible pair of scalar residual function and its gradient for fitting multiple set of time delay scan with the
    sum of convolution of damped oscillation and instrumental response function  

    Args:
     x0: initial parameter,
      if irf == 'g','c':

        * 1st: fwhm_(G/L)
        * 2nd to :math:`2+N_{scan}`: time zero of each scan
        * :math:`2+N_{scan}+i`: time constant of each damped oscillation
        * :math:`2+N_{scan}+N_{osc}+i`: period of each damped oscillation

      if irf == 'pv':

        * 1st and 2nd: fwhm_G, fwhm_L
        * 3rd to :math:`3+N_{scan}`: time zero of each scan
        * :math:`3+N_{scan}+i`: time constant of each damped oscillation
        * :math:`3+N_{scan}+N_{osc}+i`: period of each damped oscillation
           
     num_comp: number of damped oscillation component
     irf: shape of instrumental response function

          * 'g': normalized gaussian distribution,
          * 'c': normalized cauchy distribution,
          * 'pv': pseudo voigt profile :math:`(1-\\eta)g(f) + \\eta c(f)`

        For pseudo voigt profile, the mixing parameter :math:`\\eta(f_G, f_L)` and
        uniform fwhm paramter :math:`f(f_G, f_L)` are calculated by `calc_eta` and `calc_fwhm` routine
     fix_param_idx: index for fixed parameter (masked array for `x0`)
     t: time points for each data set
     intensity: sequence of intensity of datasets
     eps: sequence of estimated error of datasets

    Returns:
     Tuple of scalar residual function :math:`(\\frac{1}{2}\\sum_i {res}^2_i)` and its gradient
    '''
    x0 = np.atleast_1d(x0)
    
    if irf in ['g', 'c']:
            num_irf = 1 
            fwhm = x0[0]
    else:
        num_irf = 2
        eta = calc_eta(x0[0], x0[1])
        fwhm = calc_eta(x0[0], x0[1])
        dfwhm_G, dfwhm_L = deriv_fwhm(x0[0], x0[1])
        deta_G, deta_L = deriv_eta(x0[0], x0[1])

    num_t0 = 0; sum = 0
    for d in intensity:
        num_t0 = num_t0 + d.shape[1]
        sum = sum + d.size

    tau = x0[num_irf+num_t0:num_irf+num_t0+num_comp]
    period = x0[num_irf+num_t0+num_comp:num_irf+num_t0+2*num_comp]
    
    num_param = num_irf+num_t0+2*num_comp
    chi = np.empty(sum)
    df = np.zeros((sum, num_irf+2*num_comp))
    grad = np.empty(num_param)

    end = 0; t0_idx = num_irf

    for ti,d,e in zip(t, intensity, eps):
        step = d.shape[0]
        for j in range(d.shape[1]):
            t0 = x0[t0_idx]
            if irf == 'g':
                A = make_A_matrix_gau_osc(ti-t0, fwhm, 1/tau, period)
            elif irf == 'c':
                A = make_A_matrix_cauchy_osc(ti-t0, fwhm, 1/tau, period)
            else:
                A_gau = make_A_matrix_gau_osc(ti-t0, fwhm, 1/tau, period)
                A_cauchy = make_A_matrix_cauchy_osc(ti-t0, fwhm, 1/tau, period)
                diff = A_cauchy-A_gau
                A = A_gau + eta*diff
            c = fact_anal_A(A, d[:,j], e[:,j])
            chi[end:end+step] = (c@A-d[:,j])/e[:, j]

            c_amp = np.sqrt(c[:num_comp]**2+c[num_comp:]**2)
            phase = -np.arctan2(c[num_comp:], c[:num_comp])
                
            if irf == 'g':
                grad_tmp = deriv_dmp_osc_sum_conv_gau(ti-t0, fwhm, 1/tau, period, phase, c_amp)
            elif irf == 'c':
                grad_tmp = deriv_dmp_osc_sum_conv_cauchy(ti-t0, fwhm, 1/tau, period, phase, c_amp)
            else:
                grad_gau = deriv_dmp_osc_sum_conv_gau(ti-t0, fwhm[0], 1/tau, period, phase, c_amp)
                grad_cauchy = deriv_dmp_osc_sum_conv_cauchy(ti-t0, fwhm[1], 1/tau, period, phase, c_amp)
                grad_tmp = grad_gau + eta*(grad_cauchy-grad_gau)
   
            grad_tmp = np.einsum('i,ij->ij', 1/e[:, j], grad_tmp)
            if irf in ['g', 'c']:
                df[end:end+step, 0] = grad_tmp[:, 1]
            else:
                cdiff = (c@diff)/e[:, j]
                df[end:end+step, 0] = dfwhm_G*grad_tmp[:, 1]+deta_G*cdiff
                df[end:end+step, 1] = dfwhm_L*grad_tmp[:, 1]+deta_L*cdiff

            grad[t0_idx] = -chi[end:end+step]@grad_tmp[:, 0]
            df[end:end+step, :num_irf+num_comp] = \
                np.einsum('j,ij->ij', -1/tau**2, grad_tmp[:, 2:2+num_comp])
            df[end:end+step, num_irf+num_comp:] = grad_tmp[:, 2+num_comp:2+2*num_comp]

                
            end = end + step
            t0_idx = t0_idx + 1
    
    mask = np.ones(num_param, dtype=bool)
    mask[num_irf:num_irf+num_t0] = False
    grad[mask] = chi@df

    if fix_param_idx is not None:
        df[:, fix_param_idx] = 0

    return np.sum(chi**2)/2, grad