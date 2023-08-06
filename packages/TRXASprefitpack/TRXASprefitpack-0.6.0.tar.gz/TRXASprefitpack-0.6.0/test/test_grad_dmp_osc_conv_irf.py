import os
import sys
import unittest
import numpy as np

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path+"/../src/")

from TRXASprefitpack import calc_eta, calc_fwhm, deriv_eta, deriv_fwhm
from TRXASprefitpack.mathfun.deriv_tst import test_num_deriv
from TRXASprefitpack import dmp_osc_conv_gau, dmp_osc_conv_cauchy
from TRXASprefitpack import deriv_dmp_osc_conv_gau, deriv_dmp_osc_conv_cauchy

class TestDerivDmpOscConvIRF(unittest.TestCase):
    def test_deriv_dmp_osc_conv_gau_1(self):
        '''
        Test gradient of convolution of damped oscillation and gaussian irf (tau: 1, fwhm: 0.15, period: 0.5, phase: pi/4)
        '''
        tau = 1
        fwhm = 0.15
        period = 0.5
        phase = np.pi/4
        t = np.linspace(-1, 100, 2001)
        tst = deriv_dmp_osc_conv_gau(t, fwhm, 1/tau, period, phase)
        ref = test_num_deriv(dmp_osc_conv_gau, t, fwhm, 1/tau, period, phase)
        result = np.isclose(tst, ref)
        result = np.allclose(tst, ref)
        self.assertEqual(result, True)

    def test_deriv_dmp_osc_conv_cauchy_1(self):
        '''
        Test gradient of convolution of damped oscillation and cauchy irf (tau: 1, fwhm: 0.15, period: 0.5, phase: pi/4)
        '''
        tau = 1
        fwhm = 0.15
        period = 0.5
        phase = np.pi/4
        t = np.linspace(-1, 100, 2001)
        tst = deriv_dmp_osc_conv_cauchy(t, fwhm, 1/tau, period, phase)
        ref = test_num_deriv(dmp_osc_conv_cauchy, t, fwhm, 1/tau, period, phase)
        result = np.allclose(tst, ref)
        self.assertEqual(result, True)

    def test_deriv_exp_conv_pvoigt(self):
        '''
        Test gradient of convolution of damped oscillation and pseudo voigt irf (tau: 1, fwhm_G: 0.1, fwhm_L: 0.15, period: 0.5, phase: pi/4)
         Note. not implemented in mathfun module, check implementation in res_grad_osc function
        '''

        def tmp_fun(t, fwhm_G, fwhm_L, k, period, phase):
            fwhm = calc_fwhm(fwhm_G, fwhm_L)
            eta = calc_eta(fwhm_G, fwhm_L)
            gau = dmp_osc_conv_gau(t, fwhm, k, period, phase)
            cauchy = dmp_osc_conv_cauchy(t, fwhm, k, period, phase)
            return gau + eta*(cauchy-gau)
        
        tau_1 = 1
        fwhm_G = 0.1
        fwhm_L = 0.15
        period = 0.5
        phase = np.pi/4
        t = np.linspace(-1, 100, 2001)

        grad = np.empty((t.size, 6))
        fwhm = calc_fwhm(fwhm_G, fwhm_L)
        eta = calc_eta(fwhm_G, fwhm_L)
        dfwhm_G, dfwhm_L = deriv_fwhm(fwhm_G, fwhm_L)
        deta_G, deta_L = deriv_eta(fwhm_G, fwhm_L)
        diff = dmp_osc_conv_cauchy(t, fwhm, 1/tau_1, period, phase) - \
            dmp_osc_conv_gau(t, fwhm, 1/tau_1, period, phase)
        grad_gau = deriv_dmp_osc_conv_gau(t, fwhm, 1/tau_1, period, phase)
        grad_cauchy = deriv_dmp_osc_conv_cauchy(t, fwhm, 1/tau_1, period, phase)
        grad_tot = grad_gau + eta*(grad_cauchy-grad_gau)
        grad[:, 0] = grad_tot[:, 0]; grad[:, 3] = grad_tot[:, 2]
        grad[:, 4] = grad_tot[:, 3]; grad[:, 5] = grad_tot[:, 4]
        grad[:, 1] = dfwhm_G*grad_tot[:, 1] + deta_G*diff
        grad[:, 2] = dfwhm_L*grad_tot[:, 1] + deta_L*diff

        ref = test_num_deriv(tmp_fun, t, fwhm_G, fwhm_L, 1/tau_1, period, phase)

        result = np.allclose(grad, ref)
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()