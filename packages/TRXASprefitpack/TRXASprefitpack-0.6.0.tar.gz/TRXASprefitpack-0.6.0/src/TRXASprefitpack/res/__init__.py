'''
res:
subpackage for resdiual function for
fitting time delay scan data or static spectrum data

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''
from .parm_bound import set_bound_t0, set_bound_tau
from .parm_bound import set_bound_e0
from .res_gen import res_lmfit, residual_scalar
from .res_decay import residual_decay, res_grad_decay
from .res_osc import residual_dmp_osc, res_grad_dmp_osc
from .res_both import residual_both, res_grad_both
from .res_voigt import residual_voigt, res_grad_voigt
from .res_thy import residual_thy, res_grad_thy

__all__ = ['set_bound_t0', 'set_bound_tau',
           'set_bound_e0',
           'res_lmfit', 'residual_scalar',
           'residual_decay', 'res_grad_decay',
           'residual_dmp_osc', 'res_grad_dmp_osc',
           'residual_both', 'res_grad_both',
           'residual_voigt', 'res_grad_voigt',
           'residual_thy', 'res_grad_thy']