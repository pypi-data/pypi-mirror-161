'''
static_result:
submodule for reporting fitting process of static spectrum result

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

from typing import Callable
import numpy as np
from scipy.special import erfc, wofz
import h5py as h5
from ..mathfun.peak_shape import voigt, \
      edge_gaussian, edge_lorenzian

class StaticResult(dict):
      '''
      Represent results for fitting static driver routine

      Attributes:
       model ({'thy', 'voigt'}): model used for fitting

              `voigt`: sum of voigt function, edge function and base funtion

              `thy`: sum of voigt broadened theoretical lineshape spectrum, edge function and base function
       thy_peak (np.ndarray): theoretical calculated peak position and intensity [model: `thy`]
       policy ({'shift', 'scale', 'both'}): policy to match discrepancy between theoretical spectrum and
        experimental static spectrum.
       e (np.ndarray): energy range
       intensity (np.ndarray): intensity of static spectrum
       eps (np.ndarray): estimated error of static spectrum
       fit (np.ndarray): fitting curve for data (n,)
       fit_comp (np.ndarray): curve for each voigt component and edge
       base (np.ndaray): fitting curve for baseline
       res (np.ndarray): residual curve (data-fit) for static spectrum (n,)
       edge ({'g', 'l'}): type of edge function, if edge is None then edge function is not
        included in the fitting model

            'g': gaussian type edge function

            'l': lorenzian type edge function
       base_order (int): order of baseline function
                         if base_order is None then baseline is not included in the fitting model
       param_name (np.ndarray): name of parameter
       n_voigt (int): number of voigt component
       x (np.ndarray): best parameter
       bounds (sequence of tuple): boundary of each parameter
       c (np.ndarray): best weight of each voigt component and edge of data
       chi2 (float): chi squared value of fitting
       aic (float): Akaike Information Criterion statistic: :math:`N\\log(\\chi^2/N)+2N_{parm}`
       bic (float): Bayesian Information Criterion statistic: :math:`N\\log(\\chi^2/N)+N_{parm}\log(N)`
       red_chi2 (float): total reduced chi squared value of fitting
       nfev (int): total number of function evaluation
       n_param (int): total number of effective parameter
       num_pts (int): total number of data points 
       jac (np.ndarray): jacobian of objective function at optimal point
       cov (np.ndarray): covariance matrix (i.e. inverse of (jac.T @ jac))
       cov_scaled (np.ndarray): scaled covariance matrix (i.e. `red_chi2` * `cov`)
       corr (np.ndarray): parameter correlation matrix
       x_eps (np.ndarray): estimated error of parameter
        (i.e. square root of diagonal element of `conv_scaled`)
       method_glb ({'basinhopping'}): 
        method of global optimization used in fitting process
       message_glb (str): messages from global optimization process
       method_lsq ({'trf', 'dogbox', 'lm'}): method of local optimization for least_squares
                                             minimization (refinement of global optimization solution)
       success_lsq (bool): whether or not local least square optimization is successed
       message_lsq (str): messages from local least square optimization process
       status ({0, -1}): status of optimization process

                     `0` : normal termination

                     `-1` : least square optimization process is failed
      '''

      def __getattr__(self, name):
            try:
                  return self[name]
            except KeyError as e:
                  raise AttributeError(name) from e
      
      __setattr__ = dict.__setitem__
      __delattr__ = dict.__delitem__
      
      def __dir__(self):
            return list(self.keys())
      
      def __str__(self, corr_tol: float = 1e-1):
            '''
            Report StaticResult
            Args:
            corr_tol: parameter correlation greather than `corr_tol` would be reported
            '''
            doc_lst = []
            doc_lst.append("[Model information]")
            doc_lst.append(f"    model : {self['model']}")
            if self['model'] == 'thy':
                  doc_lst.append(f"    policy: {self['policy']}")
            if self['edge'] is not None:
                  doc_lst.append(f"    edge: {self['edge']}")
            if self['base_order'] is not None:
                  doc_lst.append(f"    base_order: {self['base_order']}")
            doc_lst.append(' ')
            doc_lst.append("[Optimization Method]")
            if self['method_glb'] is not None:
                  doc_lst.append(f"    global: {self['method_glb']}")
            doc_lst.append(f"    leastsq: {self['method_lsq']}")
            doc_lst.append(' ')
            doc_lst.append("[Optimization Status]")
            doc_lst.append(f"    nfev: {self['nfev']}")
            doc_lst.append(f"    status: {self['status']}")
            if self['method_glb'] is not None:
                  doc_lst.append(f"    global_opt msg: {self['message_glb']}")
            doc_lst.append(f"    leastsq_opt msg: {self['message_lsq']}")
            doc_lst.append(' ')
            doc_lst.append("[Optimization Results]")
            doc_lst.append(f"    Data points: {self['num_pts']}")
            doc_lst.append(f"    Number of effective parameters: {self['n_param']}")
            doc_lst.append(f"    Degree of Freedom: {self['num_pts']-self['n_param']}")
            doc_lst.append(f"    Chi squared: {self['chi2']: .4f}".rstrip('0').rstrip('.'))
            doc_lst.append(f"    Reduced chi squared: {self['red_chi2']: .4f}".rstrip('0').rstrip('.'))
            doc_lst.append(f"    AIC (Akaike Information Criterion statistic): {self['aic']: .4f}".rstrip('0').rstrip('.'))
            doc_lst.append(f"    BIC (Bayesian Information Criterion statistic): {self['bic']: .4f}".rstrip('0').rstrip('.'))
            doc_lst.append(' ')
            doc_lst.append("[Parameters]")
            for pn, pv, p_err in zip(self['param_name'], self['x'], self['x_eps']):
                  doc_lst.append(f"    {pn}: {pv: .8f} +/- {p_err: .8f} ({100*np.abs(p_err/pv): .2f}%)".rstrip('0').rstrip('.'))
            doc_lst.append(' ')
            doc_lst.append("[Parameter Bound]")
            for pn, pv, bd in zip(self['param_name'], self['x'], self['bounds']):
                  doc_lst.append(f"    {pn}: {bd[0]: .8f}".rstrip('0').rstrip('.')+f" <= {pv: .8f} <= {bd[1]: .8f}".rstrip('0').rstrip('.'))
            doc_lst.append(' ')

            doc_lst.append("[Component Contribution]")
            doc_lst.append(f"    Static spectrum")
            if self['base_order'] is None:
                  coeff_abs = np.abs(self['c'])
                  coeff_contrib = 100*self['c']
            else:
                  coeff_abs = np.abs(self['c'][:-self['base_order']-1])
                  coeff_contrib = 100*self['c'][:-self['base_order']-1]
            coeff_sum = np.sum(coeff_abs)
            coeff_contrib = coeff_contrib/coeff_sum
            for v in range(self['n_voigt']):
                  row = [f"     {self['model']} {v+1}:"]
                  row.append(f'{coeff_contrib[v]: .2f}%')
                  doc_lst.append(' '.join(row))
            if self['edge'] is not None:
                  row = [f"     {self['edge']} type edge:"]
                  row.append(f"{coeff_contrib[self['n_voigt']]: .2f}%")
                  doc_lst.append(' '.join(row))
            doc_lst.append(' ')

            doc_lst.append("[Parameter Correlation]")
            doc_lst.append(f"    Parameter Correlations > {corr_tol: .3f}".rstrip('0').rstrip('.') + " are reported.")

            A = np.empty((len(self['x']), len(self['x'])), dtype=object)
            for i in range(len(self['x'])):
                  for j in range(len(self['x'])):
                        A[i,j] = (i,j)
            
            mask = (np.abs(self['corr']) > corr_tol)

            for pair in A[mask]:
                  if pair[0] > pair[1]:
                        tmp_str_lst = [f"    ({self['param_name'][pair[0]]},"]
                        tmp_str_lst.append(f"{self['param_name'][pair[1]]})")
                        tmp_str_lst.append('=')
                        tmp_str_lst.append(f"{self['corr'][pair]: .3f}".rstrip('0').rstrip('.'))
                        doc_lst.append(' '.join(tmp_str_lst))

            return '\n'.join(doc_lst)


def save_StaticResult(result: StaticResult, filename: str):
      '''
      save static fitting result to the h5 file

      Args:
       result: static fitting result
       filename: filename to store result. It will store result to filename.h5

      Returns:
       h5 file which stores result
      '''
      model_key_lst = ['chi2', 'n_param', 'num_pts', 'red_chi2',
      'aic', 'bic', 'nfev', 'method_lsq', 'success_lsq', 'message_lsq', 'status']

      with h5.File(f'{filename}.h5', 'w') as f:
            expt = f.create_group("experiment")
            fit_res = f.create_group("fitting_result")
            if result['model'] == 'thy':
                  f.create_dataset("theoretical_peaks", data=result['thy_peak'])
                  fit_res.attrs['policy'] = result['policy']
            expt.create_dataset("energy", data=result['e'])
            expt.create_dataset("intensity", data=result['intensity'])
            expt.create_dataset("error", data=result['eps'])
            fit_res.attrs['model'] = result['model']
            fit_res.attrs['n_voigt'] = result['n_voigt']
            if result['edge'] is not None:
                  fit_res.attrs['edge'] = result['edge']
            else:
                  fit_res.attrs['edge'] = 'no'
            if result['base_order'] is not None:
                  fit_res.attrs['base_order'] = result['base_order']
            else:
                  fit_res.attrs['base_order'] = 'no'
            if result['method_glb'] is not None:
                  fit_res.attrs['method_glb'] = result['method_glb']
                  fit_res.attrs['message_glb'] = result['message_glb']
            else:
                  fit_res.attrs['method_glb'] = 'no'

            for k in model_key_lst:
                  fit_res.attrs[k] = result[k]

            fit_res_curve = fit_res.create_group("fit_curve")
            fit_res_curve.create_dataset("fit", data=result['fit'])
            fit_res_curve.create_dataset("fit_comp", data=result['fit_comp'])
            fit_res_curve.create_dataset("weight", data=result['c'])
            if result['base_order'] is not None:
                  fit_res_curve.create_dataset("base", data=result['base'])
            fit_res_curve.create_dataset("res", data=result['res'])
            fit_res_param = fit_res.create_group("parameter")
            fit_res_param.create_dataset("param_opt", data=result['x'])
            fit_res_param.create_dataset("param_eps", data=result['x_eps'])
            fit_res_param.create_dataset("param_name", data=result['param_name'].astype("S100"), dtype='S100')
            fit_res_param.create_dataset("param_bounds", data=result['bounds'])
            fit_res_param.create_dataset("correlation", data=result['corr'])
            fit_res_mis = fit_res.create_group("miscellaneous")
            fit_res_mis.create_dataset("jac", data=result['jac'])
            fit_res_mis.create_dataset('cov', data=result['cov'])
            fit_res_mis.create_dataset('cov_scaled', data=result['cov_scaled'])
      return

def load_StaticResult(filename: str) -> StaticResult:
      '''
      load static fitting result from h5 file

      Args:
       filename: filename to load result. It will load result to filename.h5
       
      Returns:
       loaded StaticResult instance
      '''
      model_key_lst = ['chi2', 'n_param', 'num_pts', 'red_chi2',
      'aic', 'bic', 'nfev',
      'method_lsq', 'success_lsq', 'message_lsq', 'status']

      result = StaticResult()

      with h5.File(f'{filename}.h5', 'r') as f:
            expt = f['experiment']
            fit_res = f['fitting_result']
            result['e'] = np.atleast_1d(expt['energy'])
            result['intensity'] = np.atleast_1d(expt['intensity'])
            result['eps'] = np.atleast_1d(expt['error'])
            result['model'] = fit_res.attrs['model']
            if result['model'] == 'thy':
                  result['thy_peak'] = np.atleast_2d(f['theoretical_peaks'])
                  result['policy'] = fit_res.attrs['policy']
            result['n_voigt'] = fit_res.attrs['n_voigt']
            if fit_res.attrs['edge'] != 'no':
                  result['edge'] = fit_res.attrs['edge']
            else:
                  result['edge'] = None
            if fit_res.attrs['base_order'] != 'no':
                  result['base_order'] = fit_res.attrs['base_order']
            else:
                  result['base_order'] = None
            
            if fit_res.attrs['method_glb'] == 'no':
                  result['method_glb'] = None
                  result['message_glb'] = None
            else:
                  result['method_glb'] = fit_res.attrs['method_glb']
                  result['message_glb'] = fit_res.attrs['message_glb']


            for k in model_key_lst:
                  result[k] = fit_res.attrs[k]
            fit_res_curve = fit_res['fit_curve']

            result['fit'] = np.atleast_1d(fit_res_curve['fit'])
            result['fit_comp'] = np.atleast_1d(fit_res_curve['fit_comp'])
            result['c'] = np.atleast_1d(fit_res_curve['weight'])
            if result['base_order'] is not None:
                  result['base'] = np.atleast_1d(fit_res_curve['base'])
            else:
                  result['base'] = None
            result['res'] = np.atleast_1d(fit_res_curve['res'])

            fit_res_param = fit_res['parameter']
            result['x'] = np.atleast_1d(fit_res_param['param_opt'])
            result['x_eps'] = np.atleast_1d(fit_res_param['param_eps'])
            result['param_name'] = np.atleast_1d(fit_res_param['param_name'])
            tmp = np.atleast_2d(fit_res_param['param_bounds'])
            lst = tmp.shape[0]*[None]
            for i in range(tmp.shape[0]):
                  lst[i] = (tmp[i,0], tmp[i, 1])
            result['bounds'] = lst
            result['corr'] = np.atleast_2d(fit_res_param['correlation'])

            fit_res_mis = fit_res['miscellaneous']
            result['jac'] = np.atleast_2d(fit_res_mis['jac'])
            result['cov'] = np.atleast_2d(fit_res_mis['cov'])
            result['cov_scaled'] = np.atleast_2d(fit_res_mis['cov_scaled'])
      return result

def deriv_edge_g_aux(e: np.ndarray, fwhm_G: float) -> np.ndarray:
    '''
    derivative of gaussian type edge

    Args:
     e: energy
     fwhm_G: full width at half maximum
    
    Returns:
     first derivative of gaussian edge function
    '''
    tmp = np.exp(-4*np.log(2)*(e/fwhm_G)**2)/np.sqrt(np.pi)

    return 2*np.sqrt(np.log(2))/fwhm_G*tmp

def dderiv_edge_g_aux(e: np.ndarray, fwhm_G: float) -> np.ndarray:
    '''
    2nd derivative of gaussian type edge

    Args:
     e: energy
     fwhm_G: full width at half maximum
    
    Returns:
     2nd derivative of gaussian edge function
    '''
    tmp = -8*np.log(2)*e*np.exp(-4*np.log(2)*(e/fwhm_G)**2)/(np.sqrt(np.pi)*fwhm_G**2)

    return 2*np.sqrt(np.log(2))/fwhm_G*tmp

def deriv_edge_l_aux(e: np.ndarray, fwhm_L: float) -> np.ndarray:
    '''
    1st derivative of lorenzian type edge

    Args:
     e: energy
    
    Returns:
     first derivative of lorenzian type function
    '''
    tmp = 1/np.pi/(e**2+fwhm_L**2/4)
    return fwhm_L*tmp/2

def dderiv_edge_l_aux(e: np.ndarray, fwhm_L: float) -> np.ndarray:
    '''
    2nd derivative of lorenzian type edge

    Args:
     e: energy
    
    Returns:
     second derivative of lorenzian type function
    '''
    tmp = -e/np.pi/(e**2+fwhm_L**2/4)**2
    return fwhm_L*tmp

def deriv_voigt_aux(e: np.ndarray, fwhm_G: float, fwhm_L: float) -> np.ndarray:
    '''
    1st derivative of voigt profile

    Args:
     e: energy
     fwhm_G: full width at half maximum of gaussian part :math:(2\\sqrt{2\\log(2)}\\sigma)
     fwhm_L: full width at half maximum of lorenzian part :math:(2\\gamma)
    
    Returns:
     first derivative of voigt profile 
    '''
    if fwhm_G < 1e-8:
        tmp = fwhm_L/np.pi/(e**2+fwhm_L**2/4)**2
        return -e*tmp
    
    sigma = fwhm_G/(2*np.sqrt(2*np.log(2)))
    if fwhm_L < 1e-8:
        tmp = np.exp(-(e/sigma)**2/2)/(sigma*np.sqrt(2*np.pi))
        return -e/sigma**2*tmp
    
    z = (e+complex(0,fwhm_L/2))/(sigma*np.sqrt(2))
    return -(z*wofz(z)).real/(sigma**2*np.sqrt(np.pi))

def dderiv_voigt_aux(e: np.ndarray, fwhm_G: float, fwhm_L: float) -> np.ndarray:
    '''
    2nd derivative of voigt profile

    Args:
     e: energy
     fwhm_G: full width at half maximum of gaussian part :math:(2\\sqrt{2\\log(2)}\\sigma)
     fwhm_L: full width at half maximum of lorenzian part :math:(2\\gamma)
    
    Returns:
     second derivative of voigt profile 
    '''

    if fwhm_G < 1e-8:
        tmp = fwhm_L/np.pi/(e**2+fwhm_L**2/4)**2
        return (4*e**2/(e**2+fwhm_L**2/4)-1)*tmp
    
    sigma = fwhm_G/(2*np.sqrt(2*np.log(2)))
    if fwhm_L < 1e-8:
        tmp = np.exp(-(e/sigma)**2/2)/(sigma*np.sqrt(2*np.pi))
        return 1/sigma**2*((e/sigma)**2-1)*tmp
    
    z = (e+complex(0,fwhm_L/2))/(sigma*np.sqrt(2))
    f = wofz(z)/(sigma*np.sqrt(2*np.pi))
    return 1/sigma**4*\
      ((e**2-fwhm_L**2/4-sigma**2)*f.real - e*fwhm_L*f.imag + fwhm_L/(2*np.pi))

def static_spectrum(e: np.ndarray, 
                    result: StaticResult, deriv_order: int = 0) -> Callable:
      '''
      Evaluates static spectrum from static spectrum
      fitting result.

      Args:
       e: energy at which evaulate static spectrum
       result: static spectrum fitting result
       deriv_order ({0, 1, 2}): order of derivative. [default: 0]
      
      Returns:
       Evaluated static spectrum
      
      Note:

       1. Currently, it only supports `model == voigt`.
       2. Baseline feature is removed.
      '''
      if result['n_voigt'] == 0:
            tmp = 0
      else:
            e0_voigt = result['x'][:result['n_voigt']]
            fwhm_G_voigt = result['x'][result['n_voigt']:2*result['n_voigt']]
            fwhm_L_voigt = result['x'][2*result['n_voigt']:3*result['n_voigt']]
            V = np.empty((result['n_voigt'], e.size))
            if deriv_order == 0:
                  for i in range(result['n_voigt']):
                        V[i, :] = voigt(e-e0_voigt[i], fwhm_G_voigt[i], fwhm_L_voigt[i])
            elif deriv_order == 1:
                  for i in range(result['n_voigt']):
                        V[i, :] = deriv_voigt_aux(e-e0_voigt[i], fwhm_G_voigt[i],
                        fwhm_L_voigt[i])
            else:
                  for i in range(result['n_voigt']):
                        V[i, :] = dderiv_voigt_aux(e-e0_voigt[i], fwhm_G_voigt[i],
                        fwhm_L_voigt[i])
            tmp = (result['c'][:result['n_voigt']]@V).flatten()

      if result['edge'] == 'g':
            if deriv_order == 0:
                  tmp = tmp + result['c'][result['n_voigt']]*\
                        edge_gaussian(e-result['x'][-2],
                        result['x'][-1])
            elif deriv_order == 1:
                  tmp = tmp + result['c'][result['n_voigt']]*\
                        deriv_edge_g_aux(e-result['x'][-2],
                        result['x'][-1])
            else:
                  tmp = tmp + result['c'][result['n_voigt']]*\
                        dderiv_edge_g_aux(e-result['x'][-2],
                        result['x'][-1])
      elif result['edge'] == 'l':
            if deriv_order == 0:
                  tmp = tmp + result['c'][result['n_voigt']]*\
                        edge_lorenzian(e-result['x'][-2],
                        result['x'][-1])
            elif deriv_order == 1:
                  tmp = tmp + result['c'][result['n_voigt']]*\
                        deriv_edge_l_aux(e-result['x'][0],
                        result['x'][1])
            else:
                  tmp = tmp + result['c'][result['n_voigt']]*\
                        dderiv_edge_l_aux(e-result['x'][0],
                        result['x'][1])

      return tmp
