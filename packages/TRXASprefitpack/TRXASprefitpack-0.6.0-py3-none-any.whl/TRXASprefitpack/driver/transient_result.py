'''
transient_result:
submodule for reporting fitting process of time scan result

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

import h5py as h5
import numpy as np

class TransientResult(dict):
      '''
      Represent results for fitting driver routine

      Attributes:
       model ({'decay', 'dmp_osc', 'both'}): model used for fitting

              `decay`: sum of the convolution of exponential decay and instrumental response function

              `dmp_osc`: sum of the convolution of damped oscillation and instrumental response function

              `both`: sum of `decay` and `dmp_osc` model
       name_of_dset (sequence of str): name of each dataset
       t (sequence of np.ndarray): time range for each dataset
       intensity (sequence of np.ndarray): sequence of datasets of intensity of time delay scan
       eps (sequence of np.ndarray): sequence of datasets for estimated error of time delay scan
       fit (sequence of np.ndarray): fitting curve for each data set
       fit_decay (sequence of np.ndarray): decay part of fitting curve for each data set [model = 'both']
       fit_osc (sequence of np.ndarray): oscillation part of fitting curve for each data set [model = 'both']
       res (sequence of np.ndarray): residual curve (data-fit) for each data set
       irf ({'g', 'c', 'pv'}): shape of instrument response function

            'g': gaussian instrumental response function

            'c': cauchy (lorenzian) instrumental response function

            'pv': pseudo voigt instrumental response function (linear combination of gaussian and lorenzian function)
       fwhm (float): unifrom fwhm parameter for pseudo voigt function :math:`((1-\\eta)*g(t, {fwhm})+\\eta*c{t, {fwhm}})`
       eta (float): mixing parameter for pseudo voigt function :math:`((1-\\eta)*g(t, {fwhm})+\\eta*c{t, {fwhm}})`
       param_name (np.ndarray): name of parameter
       n_decay (int): number of decay components (except baseline feature)
       n_osc (int): number of damped oscillation components
       x (np.ndarray): best parameter
       bounds (sequence of tuple): boundary of each parameter
       base (bool): whether or not use baseline feature in fitting process
       c (sequence of np.ndarray): best weight of each component of each datasets 
       phase (sequence of np.ndarray): phase factor of each oscillation component of each datasets [mode = 'dmp_osc', 'both']
       chi2 (float): total chi squared value of fitting
       aic (float): Akaike Information Criterion statistic: :math:`N\\log(\\chi^2/N)+2N_{parm}`
       bic (float): Bayesian Information Criterion statistic: :math:`N\\log(\\chi^2/N)+N_{parm}\log(N)`
       chi2_ind (np.ndarray): chi squared value of individual time delay scan
       red_chi2 (float): total reduced chi squared value of fitting
       red_chi2_ind (np.ndarray): reduced chi squared value of individul time delay scan
       nfev (int): total number of function evaluation
       n_param (int): total number of effective parameter
       n_param_ind (int): number of parameter which affects fitting quality of indiviual time delay scan
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
            Report TransientResult class

            Args:
            result: TransientResult class instance which has fitting result
            corr_tol: parameter correlation greather `corr_tol` would be reported
      
            Returns:
             string which reports fitting results
            '''

            doc_lst = []
            doc_lst.append("[Model information]")
            doc_lst.append(f"    model : {self['model']}")
            doc_lst.append(f"    irf: {self['irf']}")
            doc_lst.append(f"    fwhm: {self['fwhm']: .4f}")
            doc_lst.append(f"    eta: {self['eta']: .4f}")
            doc_lst.append(f"    base: {self['base']}")
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
            doc_lst.append(f"    Total Data points: {self['num_pts']}")
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

            if self['model'] in ['dmp_osc', 'both']:
                  doc_lst.append("[Phase Factor]")
                  for i in range(len(self['phase'])):
                        doc_lst.append(f"    DataSet {self['name_of_dset'][i]}:")
                        row = ['     #tscan']
                        for j in range(self['c'][i].shape[1]):
                              row.append(f'tscan_{j+1}')
                        doc_lst.append('\t'.join(row))
                  for o in range(self['n_osc']):
                        row = [f"     dmp_osc {o+1}"]
                        for l in range(self['phase'][i].shape[1]):
                              row.append(f"{self['phase'][i][o, l]/np.pi: .4f} π")
                        doc_lst.append('\t'.join(row))
            doc_lst.append(' ')

            doc_lst.append("[Component Contribution]")
            for i in range(len(self['c'])):
                  doc_lst.append(f"    DataSet {self['name_of_dset'][i]}:")
                  row = ['     #tscan']
                  coeff_abs = np.abs(self['c'][i])
                  coeff_sum = np.sum(coeff_abs, axis=0)
                  coeff_contrib = np.einsum('j,ij->ij', 100/coeff_sum, self['c'][i])
                  for j in range(coeff_contrib.shape[1]):
                      row.append(f'tscan_{j+1}')
                  doc_lst.append('\t'.join(row))
                  for d in range(self['n_decay']):
                      row = [f"     decay {d+1}"]
                      for l in range(coeff_contrib.shape[1]):
                        row.append(f'{coeff_contrib[d, l]: .2f}%')
                      doc_lst.append('\t'.join(row))
                  if self['base']:
                        tot_decay = self['n_decay']+1
                        row = [f'     base']
                        for l in range(coeff_contrib.shape[1]):
                              row.append(f"{coeff_contrib[self['n_decay'],l]: .2f}%")
                        doc_lst.append('\t'.join(row))
                  else:
                        tot_decay = self['n_decay']
                  for o in range(tot_decay, tot_decay+self['n_osc']):
                        row =[f"    dmp_osc {o+1-self['n_decay']}"]
                        for l in range(coeff_contrib.shape[1]):
                              row.append(f'{coeff_contrib[o, l]: .2f}%')
                        doc_lst.append('\t'.join(row))
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

def save_TransientResult(result: TransientResult, filename: str):
      '''
      save transient fitting result to the h5 file

      Args:
       result: transient fitting result
       filename: filename to store result. It will store result to filename.h5

      Returns:
       h5 file which stores result
      '''

      model_key_lst = ['model', 'irf', 'fwhm', 'eta', 'n_decay', 'n_osc',
      'base', 'chi2', 'n_param', 'n_param_ind', 'num_pts', 'red_chi2',
      'aic', 'bic', 'nfev', 
      'method_lsq', 'success_lsq', 'message_lsq', 'status']

      exp_key_lst = ['t', 'intensity', 'eps'] 
      fit_key_lst = ['fit', 'res', 'c', 'chi2_ind', 'red_chi2_ind']
      exp_dir_lst = ['time_delay', 'intensity', 'error']
      fit_dir_lst = ['fit', 'res', 'weight', 'chi2_ind', 'red_chi2_ind']

      name_of_dset = result['name_of_dset']

      with h5.File(f'{filename}.h5', 'w') as f:

            f.create_dataset("name_of_time_delay_scan_datasets", data=name_of_dset.astype('S100'), dtype='S100')
            expt = f.create_group("experiment")
            fit_res = f.create_group("fitting_result")
            for i in range(len(name_of_dset)):
                  expt_dset = expt.create_group(name_of_dset[i])
                  fit_res_dset = fit_res.create_group(name_of_dset[i])
                  for k, d in zip(exp_key_lst, exp_dir_lst):
                        expt_dset.create_dataset(d, data=result[k][i])
                  for k, d in zip(fit_key_lst, fit_dir_lst):
                        fit_res_dset.create_dataset(d, data=result[k][i])
                  if result['model'] == 'both':
                        fit_res_dset.create_dataset("fit_osc", data=result['fit_osc'][i])
                        fit_res_dset.create_dataset("fit_decay", data=result['fit_decay'][i])
                  if result['model'] in ['dmp_osc', 'both']:
                        fit_res_dset.create_dataset('phase', data=result['phase'][i])


            for k in model_key_lst:
                  fit_res.attrs[k] = result[k]
            if result['method_glb'] is None:
                  fit_res.attrs['method_glb'] = 'no'
            else:
                  fit_res.attrs['method_glb'] = result['method_glb']
                  fit_res.attrs['message_glb'] = result['message_glb']

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

def load_TransientResult(filename: str) -> TransientResult:
      '''
      load transient fitting result from h5 file

      Args:
       filename: filename to load result. It will load filename.h5
       
      Returns:
       transient fitting result loaded from h5 file
      '''

      model_key_lst = ['model', 'irf', 'fwhm', 'eta', 'n_decay', 'n_osc',
      'base', 'chi2', 'n_param', 'n_param_ind', 'num_pts', 'red_chi2',
      'aic', 'bic', 'nfev', 'method_lsq', 'success_lsq', 'message_lsq', 'status']

      exp_key_lst = ['intensity', 'eps'] 
      fit_key_lst = ['fit', 'res', 'c', 'chi2_ind', 'red_chi2_ind']
      exp_dir_lst = ['intensity', 'error']
      fit_dir_lst = ['fit', 'res', 'weight', 'chi2_ind', 'red_chi2_ind']

      result = TransientResult()

      with h5.File(f'{filename}.h5', 'r') as f:

            expt = f['experiment']
            fit_res = f['fitting_result']

            for k in model_key_lst:
                  result[k] = fit_res.attrs[k]
            
            if fit_res.attrs['method_glb'] == 'no':
                  result['method_glb'] = None
                  result['message_glb'] = None
            else:
                  result['method_glb'] = fit_res.attrs['method_glb']
                  result['message_glb'] = fit_res.attrs['message_glb']

            result['name_of_dset'] = np.atleast_1d(f['name_of_time_delay_scan_datasets'])

            result['t'] = np.empty(len(result['name_of_dset']), dtype=object)

            for k in exp_key_lst:
                  result[k] = np.empty(len(result['name_of_dset']), dtype=object)
            
            for k in fit_key_lst:
                  result[k] = np.empty(len(result['name_of_dset']), dtype=object)
            
            if result['model'] in ['dmp_osc', 'both']:
                  result['phase'] = np.empty(len(result['name_of_dset']), dtype=object)
            
            if result['model'] == 'both':
                  result['fit_osc'] = np.empty(len(result['name_of_dset']), dtype=object)
                  result['fit_decay'] = np.empty(len(result['name_of_dset']), dtype=object)
            
            for i in range(len(result['name_of_dset'])):
                  expt_dset = expt[result['name_of_dset'][i]]
                  fit_res_dset = fit_res[result['name_of_dset'][i]]
                  result['t'][i] = np.atleast_1d(expt_dset['time_delay'])
                  for k, d in zip(exp_key_lst, exp_dir_lst):
                        result[k][i] = np.atleast_2d(expt_dset[d])
                  for k,d in zip(fit_key_lst, fit_dir_lst):
                        result[k][i] = np.atleast_2d(fit_res_dset[d])
                  
                  if result['model'] in ['both', 'dmp_osc']:
                        result['phase'][i] = np.atleast_2d(fit_res_dset['phase'])

                  if result['model'] == 'both':
                        result['fit_osc'][i] = fit_res_dset['fit_osc']
                        result['fit_decay'][i] = fit_res_dset['fit_decay']

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