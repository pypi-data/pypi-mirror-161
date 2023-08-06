import os
import sys
import unittest
import numpy as np
from scipy.signal import convolve

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path+"/../src/")

from TRXASprefitpack import calc_eta
from TRXASprefitpack import calc_fwhm
from TRXASprefitpack import gau_irf, cauchy_irf
from TRXASprefitpack import voigt
from TRXASprefitpack import exp_conv_pvoigt, exp_conv_gau, exp_conv_cauchy

def decay(t, k):
    return np.exp(-k*t)*np.heaviside(t, 1)

class TestExpConvIRF(unittest.TestCase):

    def test_exp_conv_gau(self):
        fwhm_G = 0.15; tau = 0.3
        t = np.linspace(-2, 2, 2000)
        t_sample = np.hstack((np.arange(-1, -0.5, 0.1),
        np.arange(-0.5, 0.5, 0.05), np.linspace(0.5, 1, 6)))
        sample_idx = np.searchsorted(t, t_sample)
        gau_ref = gau_irf(t, fwhm_G)
        decay_ref = decay(t, 1/tau)
        ref = convolve(gau_ref, decay_ref, mode='same')*4/2000
        tst = exp_conv_gau(t_sample, fwhm_G, 1/tau)
        cond = np.max(np.abs(ref[sample_idx]-tst))/np.max(ref) < 1e-3
        self.assertEqual(cond, True)


    def test_exp_conv_cauchy(self):
        fwhm_L = 0.15; tau = 0.3
        t = np.linspace(-2, 2, 2000)
        t_sample = np.hstack((np.arange(-1, -0.5, 0.1),
        np.arange(-0.5, 0.5, 0.05), np.linspace(0.5, 1, 6)))
        sample_idx = np.searchsorted(t, t_sample)
        cauchy_ref = cauchy_irf(t, fwhm_L)
        decay_ref = decay(t, 1/tau)
        ref = convolve(cauchy_ref, decay_ref, mode='same')*4/2000
        tst = exp_conv_cauchy(t_sample, fwhm_L, 1/tau)
        cond = np.max(np.abs(ref[sample_idx]-tst))/np.max(ref) < 1e-3
        self.assertEqual(cond, True)

    def test_exp_conv_pvoigt(self):
        fwhm_G = 0.15; fwhm_L = 0.10; tau = 0.3
        fwhm = calc_fwhm(fwhm_G, fwhm_L)
        eta = calc_eta(fwhm_G, fwhm_L)
        t = np.linspace(-2, 2, 2000)
        t_sample = np.hstack((np.arange(-1, -0.5, 0.1),
        np.arange(-0.5, 0.5, 0.05), np.linspace(0.5, 1, 6)))
        sample_idx = np.searchsorted(t, t_sample)
        voigt_ref = voigt(t, fwhm_G, fwhm_L)
        decay_ref = decay(t, 1/tau)
        ref = convolve(voigt_ref, decay_ref, mode='same')*4/2000
        tst = exp_conv_pvoigt(t_sample, fwhm, eta, 1/tau)
        cond = np.max(np.abs(ref[sample_idx]-tst))/np.max(ref) < 1e-2
        self.assertEqual(cond, True)

if __name__ == '__main__':
    unittest.main()

