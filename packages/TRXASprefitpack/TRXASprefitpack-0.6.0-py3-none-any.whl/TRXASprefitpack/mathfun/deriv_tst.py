'''
deriv_tst:
submodule to test derivative routine of mathfun subpackage

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

import numpy as np

def test_num_deriv(func: callable, *args, eps_rel=1e-8, eps_abs=5e-6):
    '''
    Test implementation of derivative via finite difference
    i th column: derivative of f w.r.t ith argument
    '''
    n = len(args)
    if isinstance(args[0], np.ndarray):
        num_grad = np.empty((args[0].size, n))
        for i in range(n):
            f_args = list(args)
            b_args = list(args)
            f_args[i] = f_args[i]*(1+eps_rel)+eps_abs
            b_args[i] = b_args[i]*(1-eps_rel)-eps_abs
            f_args = tuple(f_args)
            b_args = tuple(b_args)
            dx = f_args[i] - b_args[i]
            num_grad[:, i] = (func(*f_args)-func(*b_args))/dx
    else:
        num_grad = np.empty(n)
        for i in range(n):
            f_args = list(args)
            b_args = list(args)
            f_args[i] = f_args[i]*(1+eps_rel)+eps_abs
            b_args[i] = b_args[i]*(1-eps_rel)-eps_abs
            f_args = tuple(f_args)
            b_args = tuple(b_args)
            dx  = f_args[i] - b_args[i]
            num_grad[i] = (func(*f_args)-func(*b_args))/dx
    
    return num_grad