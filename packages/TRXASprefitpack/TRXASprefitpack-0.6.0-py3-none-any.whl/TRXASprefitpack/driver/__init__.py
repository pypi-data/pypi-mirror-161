'''
driver:
subpackage for driver routine of TRXASprefitpack
convolution of sum of exponential decay and instrumental response function 

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

from .ads import sads, dads
from .transient_result import TransientResult, save_TransientResult, load_TransientResult
from .static_result import StaticResult, save_StaticResult, load_StaticResult
from .static_result import static_spectrum
from ._transient_exp import fit_transient_exp
from ._transient_dmp_osc import fit_transient_dmp_osc
from ._transient_both import fit_transient_both
from ._static_voigt import fit_static_voigt
from ._static_thy import fit_static_thy
from .anal_fit import CIResult, is_better_fit, confidence_interval

__all__ = ['sads', 'dads',
           'TransientResult', 'save_TransientResult', 'load_TransientResult',
           'StaticResult', 'save_StaticResult', 'load_StaticResult',
           'static_spectrum',
           'fit_transient_exp', 'fit_transient_dmp_osc', 'fit_transient_both',
           'fit_static_voigt', 'fit_static_thy'
           ,'CIResult', 'is_better_fit', 'confidence_interval']