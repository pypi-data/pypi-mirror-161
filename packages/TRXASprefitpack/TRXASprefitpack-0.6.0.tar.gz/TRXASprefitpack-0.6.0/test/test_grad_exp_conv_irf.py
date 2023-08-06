import os
import sys
import unittest
import numpy as np

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path+"/../src/")

from TRXASprefitpack import calc_eta, calc_fwhm, deriv_eta, deriv_fwhm
from TRXASprefitpack.mathfun.deriv_tst import test_num_deriv
from TRXASprefitpack import exp_conv_gau, exp_conv_cauchy
from TRXASprefitpack import deriv_exp_conv_gau, deriv_exp_conv_cauchy
from TRXASprefitpack import deriv_exp_sum_conv_gau, deriv_exp_sum_conv_cauchy

class TestDerivExpConvIRF(unittest.TestCase):
    def test_deriv_exp_conv_gau_1(self):
        '''
        Test gradient of convolution of exponenetial decay and gaussian irf (tau: 1, fwhm: 0.15)
        '''
        tau = 1
        fwhm = 0.15
        t = np.linspace(-1, 100, 2001)
        tst = deriv_exp_conv_gau(t, fwhm, 1/tau)
        ref = test_num_deriv(exp_conv_gau, t, fwhm, 1/tau)
        result = np.allclose(tst, ref)
        self.assertEqual(result, True)
    
    def test_deriv_exp_sum_conv_gau_1(self):
        '''
        Test gradient of convolution of sum of exponenetial decay and gaussian irf (tau1: 1, tau2: 100, fwhm: 0.15, base: True)
        '''
        tau_1 = 1
        tau_2 = 100
        k = np.array([1/tau_1, 1/tau_2])
        fwhm = 0.15
        base = True
        t = np.linspace(-1, 1000, 20001)
        c = np.array([1, 1, 1])
        tst = deriv_exp_sum_conv_gau(t, fwhm, k, c, base)
        ref = test_num_deriv(lambda t, fwhm, k1, k2: exp_conv_gau(t, fwhm, k1)+exp_conv_gau(t, fwhm, k2)+exp_conv_gau(t, fwhm, 0),
        t, fwhm, 1/tau_1, 1/tau_2)
        result = np.allclose(tst, ref)
        self.assertEqual(result, True)

    def test_deriv_exp_sum_conv_gau_2(self):
        '''
        Test gradient of convolution of sum of exponenetial decay and gaussian irf (tau1: 1, tau2: 100, fwhm: 0.15, base: False)
        '''
        tau_1 = 1
        tau_2 = 100
        k = np.array([1/tau_1, 1/tau_2])
        fwhm = 0.15
        base = False
        t = np.linspace(-1, 1000, 20001)
        c = np.array([1, 1, 1])
        tst = deriv_exp_sum_conv_gau(t, fwhm, k, c, base)
        ref = test_num_deriv(lambda t, fwhm, k1, k2: exp_conv_gau(t, fwhm, k1)+exp_conv_gau(t, fwhm, k2),
        t, fwhm, 1/tau_1, 1/tau_2)
        result = np.allclose(tst, ref)
        self.assertEqual(result, True)

    def test_deriv_exp_conv_cauchy(self):
        '''
        Test gradient of convolution of exponenetial decay and cauchy irf (tau: 1, fwhm: 0.15)
        '''
        tau = 1
        fwhm = 0.15
        t = np.linspace(-1, 100, 2001)
        tst = deriv_exp_conv_cauchy(t, fwhm, 1/tau)
        ref = test_num_deriv(exp_conv_cauchy, t, fwhm, 1/tau)
        result = np.allclose(tst, ref)
        self.assertEqual(result, True)
    
    def test_deriv_exp_sum_conv_cauchy_1(self):
        '''
        Test gradient of convolution of sum of exponenetial decay and cauchy irf (tau1: 1, tau2: 100, fwhm: 0.15, base: True)
        '''
        tau_1 = 1
        tau_2 = 100
        k = np.array([1/tau_1, 1/tau_2])
        fwhm = 0.15
        base = True
        t = np.linspace(-1, 1000, 20001)
        c = np.array([1, 1, 1])
        tst = deriv_exp_sum_conv_cauchy(t, fwhm, k, c, base)
        ref = test_num_deriv(lambda t, fwhm, k1, k2: exp_conv_cauchy(t, fwhm, k1)+
        exp_conv_cauchy(t, fwhm, k2)+exp_conv_cauchy(t, fwhm, 0),
        t, fwhm, 1/tau_1, 1/tau_2)
        result = np.allclose(tst, ref)
        self.assertEqual(result, True)

    def test_deriv_exp_sum_conv_cauchy_2(self):
        '''
        Test gradient of convolution of sum of exponenetial decay and gaussian irf (tau1: 1, tau2: 100, fwhm: 0.15, base: False)
        '''
        tau_1 = 1
        tau_2 = 100
        k = np.array([1/tau_1, 1/tau_2])
        fwhm = 0.15
        base = False
        t = np.linspace(-1, 1000, 20001)
        c = np.array([1, 1])
        tst = deriv_exp_sum_conv_cauchy(t, fwhm, k, c, base)
        ref = test_num_deriv(lambda t, fwhm, k1, k2: exp_conv_cauchy(t, fwhm, k1)+
        exp_conv_cauchy(t, fwhm, k2),
        t, fwhm, 1/tau_1, 1/tau_2)
        result = np.allclose(tst, ref)
        self.assertEqual(result, True)
    
    def test_deriv_exp_conv_pvoigt(self):
        '''
        Test gradient of convolution of exponenetial decay and pseudo voigt irf (tau: 1, fwhm_G: 0.1, fwhm_L: 0.15)
        Note.
         Not implemented in mathfun module, check implemenetation in res_grad_decay function
        '''

        def tmp_fun(t, fwhm_G, fwhm_L, k):
            fwhm = calc_fwhm(fwhm_G, fwhm_L)
            eta = calc_eta(fwhm_G, fwhm_L)
            gau = exp_conv_gau(t, fwhm, k)
            cauchy = exp_conv_cauchy(t, fwhm, k)
            return gau + eta*(cauchy-gau)
        
        tau_1 = 1
        fwhm_G = 0.1
        fwhm_L = 0.15
        t = np.linspace(-1, 200, 2001)

        grad = np.empty((t.size, 4))
        fwhm = calc_fwhm(fwhm_G, fwhm_L)
        eta = calc_eta(fwhm_G, fwhm_L)
        dfwhm_G, dfwhm_L = deriv_fwhm(fwhm_G, fwhm_L)
        deta_G, deta_L = deriv_eta(fwhm_G, fwhm_L)
        diff = exp_conv_cauchy(t, fwhm, 1/tau_1) - \
            exp_conv_gau(t, fwhm, 1/tau_1)
        grad_gau = deriv_exp_conv_gau(t, fwhm, 1/tau_1)
        grad_cauchy = deriv_exp_conv_cauchy(t, fwhm, 1/tau_1)
        grad_tot = grad_gau + eta*(grad_cauchy-grad_gau)
        grad[:, 0] = grad_tot[:, 0]; grad[:, 3] = grad_tot[:, 2]
        grad[:, 1] = dfwhm_G*grad_tot[:, 1] + deta_G*diff
        grad[:, 2] = dfwhm_L*grad_tot[:, 1] + deta_L*diff

        ref = test_num_deriv(tmp_fun, t, fwhm_G, fwhm_L, 1/tau_1)

        result = np.allclose(grad, ref)
        self.assertEqual(result, True)



if __name__ == '__main__':
    unittest.main()
