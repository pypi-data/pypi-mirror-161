'''
anal_fit:
submodule for 
1. comparing two different fitting model
2. calculating confidence interval of parameter
based on f_test

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''
import numpy as np
from scipy.stats import f, norm
from scipy.optimize import brenth, minimize
from ..res import res_grad_decay, res_grad_dmp_osc, res_grad_both
from ..res import res_grad_voigt, res_grad_thy

def res_scan_opt(p, *args) -> float:
    '''
    res_scan
    Scans minimal value of residual function with constraint
    ith value of parameter is fixed to p.

    Args:
     p: value of ith parameter
     args: arguments

           * 1st: i, index of parameter to scan
           * 2nd: parameter
           * 3rd: bounds
           * 4th: objective function which also gives its gradient
           * 5th to last: arguments for objective function
           * :math:`last-3`: fixed_param_idx
    
    Returns:
     residual value at params[i] = p
    '''
    param = np.atleast_1d(args[1]).copy()
    param[args[0]] = p
    bounds = len(args[2])*[None]
    for i in range(len(args[2])):
        bounds[i] = args[2][i]
    bounds[args[0]] = (p, p)
    func = args[3]
    fixed_param_idx = np.atleast_1d(args[-4]).copy()
    fixed_param_idx[args[0]] = True
    fargs_lst = (len(args)-4)*[None]
    for i in range(4, len(args)):
        fargs_lst[i-4] = args[i]
    fargs_lst[-4] = fixed_param_idx
    fargs = tuple(fargs_lst)
    res = minimize(func, param, args=fargs, bounds=bounds, method='L-BFGS-B', jac=True)

    return res['fun']

def ci_scan_opt_f(p, *args):
    '''
    Confidence interval scan with ith parameter is fixed to p. (for f-test based method)
    '''
    F_alpha, dfn, dfd, chi2_opt = args[:4]
    fargs = tuple(args[4:])
    return (res_scan_opt(p, *fargs)-chi2_opt/2)/dfn/(chi2_opt/(2*dfd))-F_alpha


class CIResult(dict):
    '''
    Class for represent confidence interval of each parameter

    Attributes:
     method ({'f'}): method to calculate confidance interval of each parameter
     alpha (float): significant level
     param_name (sequence of str): name of parameter
     x (np.ndarray): best parameter
     ci (sequence of tuple): confidence interval of each parameter at significant level alpha
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
    
    def __str__(self):
        doc_lst = []
        doc_lst.append("[Report for Confidence Interval]")
        doc_lst.append(f"    Method: {self['method']}")
        doc_lst.append(f"    Significance level: {self['alpha']: 4e}")
        doc_lst.append(' ')
        doc_lst.append("[Confidence interval]")
        for pn, pv, ci in zip(self['param_name'], self['x'], self['ci']):
            if ci[0] != 0 and ci[1] != 0:
                tmp_doc_lst = []
                tmp_doc_lst.append(f"    {pv:.8f}".rstrip('0').rstrip('.'))
                tmp_doc_lst.append(f"- {-ci[0]: .8f}".rstrip('0').rstrip('.'))
                tmp_doc_lst.append(f"<= {pn} <=")
                tmp_doc_lst.append(f"{pv: .8f}".rstrip('0').rstrip('.'))
                tmp_doc_lst.append(f"+ {ci[1]: .8f}".rstrip('0').rstrip('.'))
                doc_lst.append(' '.join(tmp_doc_lst))
        return '\n'.join(doc_lst)



def is_better_fit(result1, result2) -> float:
    '''
    Compare fit based on f-test

    Args:
     result1 ({'StaticResult', 'TransientResult'}): fitting result class
      which has more parameter than result2
     result2 ({'StaticResult', 'TransientResult'}): fitting result class
      which has less parameter than result1

    Returns:
     p value of test, If p is smaller than your significant level,
     result1 is may better fit than result2.
     Otherwise, you cannot say resul1 is better fit than result2.
    
    Note:

     * The number of parameters in result1 should be greather than the number of parameters in result2.
     * The result1 and result2 should be different model for same data.

    '''
    chi2_1 = result1['chi2']; chi2_2 = result2['chi2']
    num_param_1 = result1['n_param']; num_param_2 = result2['n_param']
    num_pts_1 = result1['num_pts']; num_pts_2 = result2['num_pts']

    if num_param_1 <= num_param_2:
        raise Exception(f'Number of parameter in model 1: {num_param_1}' + 
        ' should be strictly greather than' + 
        f' the number of parameter in model 2: {num_param_2}')
    
    if num_pts_1 != num_pts_2:
        raise Exception('The result1 and result2 should be different model for same data')
    
    dfn = num_param_1 - num_param_2
    dfd = num_pts_1 - num_param_1

    F_test = (chi2_2-chi2_1)/dfn/(chi2_1/dfd)
    p = 1- f.cdf(F_test, dfn, dfd)
    return p

def confidence_interval(result, alpha: float) -> CIResult:
    '''
    Calculate 1d confidence interval of each parameter at significance level alpha
    Based on F-test method

    Args:
     result ({'StaticResult', 'TransientResult'}): fitting result class
     alpha (float): significance level

    Returns:
     CIResult class instance
    '''
    params = np.atleast_1d(result['x'])
    fix_param_idx = np.zeros(len(result['x']), dtype=bool)
    for i in range(params.size):
        fix_param_idx[i] = (result['bounds'][i][0] == result['bounds'][i][1])
    select_idx = fix_param_idx.copy()
    scan_idx = np.array(range(len(result['x'])))
    ci_lst = len(result['x'])*[(0, 0)]
    num_param = result['n_param']
    num_pts = result['num_pts']

    chi2_opt = result['chi2']
    dfn = 1; dfd = num_pts - num_param
    F_alpha = f.ppf(1-alpha, dfn, dfd)
    norm_alpha = np.ceil(norm.ppf(1-alpha/2))

    if result['model'] == 'decay':
        args = [F_alpha, dfn, dfd, chi2_opt, 0, params, result['bounds'], 
        res_grad_decay, result['n_decay'],
        result['base'], result['irf'], fix_param_idx, 
        result['t'], result['intensity'], result['eps']]
    elif result['model'] == 'dmp_osc':
        args = [F_alpha, dfn, dfd, chi2_opt, 0, params, result['bounds'],
        res_grad_dmp_osc, result['n_osc'], 
        result['irf'], fix_param_idx,
        result['t'], result['intensity'], result['eps']]
    elif result['model'] == 'both':
        args = [F_alpha, dfn, dfd, chi2_opt, 0, params, result['bounds'],
        res_grad_both,
        result['n_decay'], result['n_osc'], result['base'], result['irf'], fix_param_idx,
        result['t'], result['intensity'], result['eps']]
    elif result['model'] == 'voigt':
        args = [F_alpha, dfn, dfd, chi2_opt, 0, params, result['bounds'],
        res_grad_voigt,
        result['n_voigt'], result['edge'], result['base_order'], fix_param_idx,
        result['e'], result['intensity'], result['eps']]
    elif result['model'] == 'thy':
        args = [F_alpha, dfn, dfd, chi2_opt, 0, params, result['bounds'],
        res_grad_thy,
        result['policy'], result['thy_peak'], 
        result['edge'], result['base_order'], fix_param_idx,
        result['e'], result['intensity'], result['eps']]
    
    sub_scan_idx = scan_idx[~select_idx]
    for idx in sub_scan_idx:
        p0 = params[idx]
        args[4] = idx
        fargs = tuple(args)
        p_eps = result['x_eps'][idx]
        p_lb = p0-norm_alpha*p_eps; p_ub = p0+norm_alpha*p_eps

        while ci_scan_opt_f(p_lb, *fargs) < 0:
            p_lb = p_lb - p_eps
            
        while ci_scan_opt_f(p_ub, *fargs) < 0:
            p_ub = p_ub + p_eps
            
        z1 = brenth(ci_scan_opt_f, p0, p_ub, args=fargs)
        z2 = brenth(ci_scan_opt_f, p_lb, p0, args=fargs)

        ci_lst[idx] = (z2-p0, z1-p0)
    
    ci_res = CIResult()
    ci_res['method'] = 'f'
    ci_res['alpha'] = alpha
    ci_res['param_name'] = result['param_name']
    ci_res['x'] = result['x']
    ci_res['ci'] = ci_lst
    return ci_res




    