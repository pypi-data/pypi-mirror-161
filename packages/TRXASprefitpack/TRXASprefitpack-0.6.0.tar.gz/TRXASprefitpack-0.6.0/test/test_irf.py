import os
import sys
import unittest
import numpy as np

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path+"/../src/")

from TRXASprefitpack.mathfun.deriv_tst import test_num_deriv
from TRXASprefitpack import calc_eta, deriv_eta
from TRXASprefitpack import calc_fwhm, deriv_fwhm
from TRXASprefitpack import pvoigt_irf
from TRXASprefitpack import voigt

class TestPvoigtIRF(unittest.TestCase):
    def test_pvoigt_irf_1(self):
        '''
         Test pseudo voigt approximation (fwhm_L = 3 fwhm_G)
        '''
        t = np.linspace(-1, 1, 201)
        fwhm_G = 0.1; fwhm_L = 0.3
        fwhm = calc_fwhm(fwhm_G, fwhm_L)
        eta = calc_eta(fwhm_G, fwhm_L)
        ref = voigt(t, fwhm_G, fwhm_L)
        tst = pvoigt_irf(t, fwhm, eta)
        result = np.max(np.abs(tst-ref))/np.max(ref) < 2e-2
        self.assertEqual(result, True)

    def test_pvoigt_irf_2(self):
        '''
         Test pseudo voigt approximation (fwhm_L = 1.5 fwhm_G)
        '''
        t = np.linspace(-1, 1, 201)
        fwhm_G = 0.1; fwhm_L = 0.15
        fwhm = calc_fwhm(fwhm_G, fwhm_L)
        eta = calc_eta(fwhm_G, fwhm_L)
        ref = voigt(t, fwhm_G, fwhm_L)
        tst = pvoigt_irf(t, fwhm, eta)
        result = np.max(np.abs(tst-ref))/np.max(ref) < 2e-2
        self.assertEqual(result, True)

    def test_pvoigt_irf_3(self):
        '''
         Test pseudo voigt approximation (fwhm_L = 1 fwhm_G)
        '''
        t = np.linspace(-1, 1, 201)
        fwhm_G = 0.1; fwhm_L = 0.1
        fwhm = calc_fwhm(fwhm_G, fwhm_L)
        eta = calc_eta(fwhm_G, fwhm_L)
        ref = voigt(t, fwhm_G, fwhm_L)
        tst = pvoigt_irf(t, fwhm, eta)
        result = np.max(np.abs(tst-ref))/np.max(ref) < 2e-2
        self.assertEqual(result, True)

    def test_pvoigt_irf_4(self):
        '''
         Test pseudo voigt approximation (fwhm_G = 1.5 fwhm_L)
        '''
        t = np.linspace(-1, 1, 201)
        fwhm_G = 0.15; fwhm_L = 0.1
        fwhm = calc_fwhm(fwhm_G, fwhm_L)
        eta = calc_eta(fwhm_G, fwhm_L)
        ref = voigt(t, fwhm_G, fwhm_L)
        tst = pvoigt_irf(t, fwhm, eta)
        result = np.max(np.abs(tst-ref))/np.max(ref) < 2e-2
        self.assertEqual(result, True)

    def test_pvoigt_irf_5(self):
        '''
         Test pseudo voigt approximation (fwhm_G = 3 fwhm_L)
        '''
        t = np.linspace(-1, 1, 201)
        fwhm_G = 0.3; fwhm_L = 0.1
        fwhm = calc_fwhm(fwhm_G, fwhm_L)
        eta = calc_eta(fwhm_G, fwhm_L)
        ref = voigt(t, fwhm_G, fwhm_L)
        tst = pvoigt_irf(t, fwhm, eta)
        result = np.max(np.abs(tst-ref))/np.max(ref) < 2e-2
        self.assertEqual(result, True)
    
    def test_deriv_eta_1(self):
        '''
         Test gradient of mixing parameter eta (fwhm_L = 3 fwhm_G)
        '''
        fwhm_G = 0.1; fwhm_L = 0.3
        d_G, d_L = deriv_eta(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_eta, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_eta_2(self):
        '''
         Test gradient of mixing parameter eta (fwhm_L = 1.5 fwhm_G)
        '''
        fwhm_G = 0.1; fwhm_L = 0.15
        d_G, d_L = deriv_eta(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_eta, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_eta_3(self):
        '''
         Test gradient of mixing parameter eta (fwhm_L = fwhm_G)
        '''
        fwhm_G = 0.1; fwhm_L = 0.1
        d_G, d_L = deriv_eta(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_eta, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_eta_4(self):
        '''
         Test gradient of mixing parameter eta (fwhm_G = 1.5 fwhm_L)
        '''
        fwhm_G = 0.15; fwhm_L = 0.1
        d_G, d_L = deriv_eta(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_eta, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_eta_5(self):
        '''
         Test gradient of mixing parameter eta (fwhm_G = 3 fwhm_L)
        '''
        fwhm_G = 0.3; fwhm_L = 0.1
        d_G, d_L = deriv_eta(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_eta, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_fwhm_1(self):
        '''
         Test gradient of unifrom fwhm parameter (fwhm_L = 3 fwhm_G)
        '''
        fwhm_G = 0.1; fwhm_L = 0.3
        d_G, d_L = deriv_fwhm(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_fwhm, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_fwhm_2(self):
        '''
         Test gradient of unifrom fwhm parameter (fwhm_L = 1.5 fwhm_G)
        '''
        fwhm_G = 0.1; fwhm_L = 0.15
        d_G, d_L = deriv_fwhm(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_fwhm, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_fwhm_3(self):
        '''
         Test gradient of unifrom fwhm parameter (fwhm_L = fwhm_G)
        '''
        fwhm_G = 0.1; fwhm_L = 0.1
        d_G, d_L = deriv_fwhm(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_fwhm, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_fwhm_4(self):
        '''
         Test gradient of uniform fwhm parameter (fwhm_G = 1.5 fwhm_L)
        '''
        fwhm_G = 0.15; fwhm_L = 0.1
        d_G, d_L = deriv_fwhm(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_fwhm, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

    def test_deriv_fwhm_5(self):
        '''
         Test gradient of unifrom fwhm parameter (fwhm_G = 3 fwhm_L)
        '''
        fwhm_G = 0.3; fwhm_L = 0.1
        d_G, d_L = deriv_fwhm(fwhm_G, fwhm_L)
        
        result = np.allclose(np.array([d_G, d_L]), 
        test_num_deriv(calc_fwhm, fwhm_G, fwhm_L))
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()
