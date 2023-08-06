'''
mathfun:
subpackage for the mathematical functions for TRXASprefitpack

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

from .peak_shape import voigt, edge_gaussian, edge_lorenzian
from .peak_shape import deriv_voigt, deriv_edge_gaussian, deriv_edge_lorenzian
from .peak_shape import voigt_thy, deriv_voigt_thy
from .irf import gau_irf, cauchy_irf, pvoigt_irf
from .irf import calc_eta, calc_fwhm, deriv_eta, deriv_fwhm
from .exp_conv_irf import exp_conv_gau, exp_conv_cauchy, exp_conv_pvoigt
from .exp_conv_irf import deriv_exp_conv_gau, deriv_exp_conv_cauchy
from .exp_conv_irf import deriv_exp_sum_conv_gau, deriv_exp_sum_conv_cauchy
from .exp_conv_irf import dmp_osc_conv_gau, dmp_osc_conv_cauchy, dmp_osc_conv_pvoigt
from .exp_conv_irf import deriv_dmp_osc_conv_gau, deriv_dmp_osc_conv_cauchy
from .rate_eq import solve_model, solve_seq_model, solve_l_model, compute_model
from .rate_eq import compute_signal_gau, compute_signal_cauchy
from .rate_eq import compute_signal_pvoigt
from .exp_decay_fit import exp_conv, fact_anal_exp_conv
from .exp_decay_fit import rate_eq_conv, fact_anal_rate_eq_conv
from .exp_decay_fit import dmp_osc_conv, fact_anal_dmp_osc_conv
from .exp_decay_fit import sum_exp_dmp_osc_conv, fact_anal_sum_exp_dmp_osc_conv


__all__ = ['voigt', 'edge_gaussian', 'edge_lorenzian', 'voigt_thy',
           'deriv_voigt', 'deriv_edge_gaussian', 'deriv_edge_lorenzian',
           'deriv_voigt_thy',
           'gau_irf', 'cauchy_irf', 'pvoigt_irf', 
           'calc_eta', 'calc_fwhm', 'deriv_eta', 'deriv_fwhm',
           'exp_conv_gau', 'exp_conv_cauchy', 'exp_conv_pvoigt',
           'deriv_exp_conv_gau', 'deriv_exp_conv_cauchy',
           'deriv_exp_sum_conv_gau', 'deriv_exp_sum_conv_cauchy',
           'dmp_osc_conv_gau', 'dmp_osc_conv_cauchy', 'dmp_osc_conv_pvoigt',
           'deriv_dmp_osc_conv_gau', 'deriv_dmp_osc_conv_cauchy',
           'solve_model', 'solve_seq_model', 'solve_l_model', 'compute_model',
           'compute_signal_gau', 'compute_signal_cauchy', 'compute_signal_pvoigt', 
           'exp_conv', 'fact_anal_exp_conv',
           'rate_eq_conv', 'fact_anal_rate_eq_conv',
           'dmp_osc_conv', 'fact_anal_dmp_osc_conv',
           'sum_exp_dmp_osc_conv', 'fact_anal_sum_exp_dmp_osc_conv']
