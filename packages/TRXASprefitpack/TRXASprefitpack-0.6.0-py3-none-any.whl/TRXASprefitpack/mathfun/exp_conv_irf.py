'''
exp_conv_irf:
submodule for the mathematical functions for
exponential decay convolved with irf

:copyright: 2021-2022 by pistack (Junho Lee).
:license: LGPL3.
'''

from typing import Union, Optional, Tuple
import numpy as np
from scipy.special import erfc, erfcx, wofz, exp1

# special function: scaled expoential integral
# if scipy starts to support scaled expoential integral I will delete this function 

def exp1x_asymp(z: Union[complex, np.ndarray]) -> Union[complex, np.ndarray]:
    return z*(1+z*(1+2*z*(1+3*z*(1+4*z*(1+5*z*(1+6*z*(1+7*z*(1+8*z*(1+9*z*(1+10*z))))))))))

def exp1x(z: Union[complex, np.ndarray]) -> Union[complex, np.ndarray]:
    
    if not isinstance(z, np.ndarray):
            if np.abs(z.real) < 200:
                # ans = np.exp(z)*exp1(z)
                ans = complex(np.cos(z.imag), np.sin(z.imag))*exp1(z)
                ans = np.exp(z.real)*ans
            else:
                ans = -exp1x_asymp(-1/z)
    else:
        mask = np.abs(z.real) < 200
        inv_mask = np.invert(mask)
        ans = np.empty(z.size, dtype=np.complex128)
        
        # abs(Re z) < 200
        ans[mask] = (np.cos(z[mask].imag)+complex(0,1)*np.sin(z[mask].imag))*exp1(z[mask])
        ans[mask] = np.exp(z.real[mask])*ans[mask]

        # abs(Re z) > 200, use asymptotic series
        ans[inv_mask] = -exp1x_asymp(-1/z[inv_mask])
    return ans

# calculate convolution of exponential decay and instrumental response function

def exp_conv_gau(t: Union[float, np.ndarray], fwhm: float,
                 k: float) -> Union[float, np.ndarray]:

    '''
    Compute exponential function convolved with normalized gaussian
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of gaussian distribution
      k: rate constant (inverse of life time)

    Returns:
     Convolution of normalized gaussian distribution and exponential
     decay :math:`(\\exp(-kt))`.
    '''

    sigma = fwhm/(2*np.sqrt(2*np.log(2)))
    ksigma = k*sigma
    z = ksigma - t/sigma

    if not isinstance(t, np.ndarray):
        if z > 0:
            ans = 1/2*np.exp(-(t/sigma)**2/2) * \
                erfcx(z/np.sqrt(2))
        else:
            ans = 1/2*np.exp(ksigma*z-ksigma**2/2) * \
                erfc(z/np.sqrt(2))
    else:
        mask = z > 0
        inv_mask = np.invert(mask)
        ans = np.empty(t.size, dtype=np.float64)
        ans[mask] = 1/2*np.exp(-(t[mask]/sigma)**2/2) * \
            erfcx(z[mask]/np.sqrt(2))
        ans[inv_mask] = 1/2*np.exp(ksigma*z[inv_mask]-ksigma**2/2) * \
            erfc(z[inv_mask]/np.sqrt(2))

    return ans

def exp_conv_cauchy(t: Union[float, np.ndarray],
                    fwhm: float,
                    k: float) -> Union[float, np.ndarray]:

    '''
    Compute exponential function convolved with normalized cauchy
    distribution

    Args:
       t: time
       fwhm: full width at half maximum of cauchy distribution
       k: rate constant (inverse of life time)

    Returns:
      Convolution of normalized cauchy distribution and
      exponential decay :math:`(\\exp(-kt))`.
    '''

    if k == 0:
        ans = 0.5+1/np.pi*np.arctan(2*t/fwhm)
    else:
        z = -k*t - complex(0, k*fwhm/2)
        ans = exp1x(z).imag/np.pi
    return ans

def exp_conv_pvoigt(t: Union[float, np.ndarray],
                    fwhm: float,
                    eta: float,
                    k: float) -> Union[float, np.ndarray]:

    '''
    Compute exponential function convolved with normalized pseudo
    voigt profile (i.e. linear combination of normalized gaussian and
    cauchy distribution)

    :math:`\\eta C(\\mathrm{fwhm}, t) + (1-\\eta)G(\\mathrm{fwhm}, t)`

    Args:
       t: time
       fwhm: full width at half maximum parameter for pseudo voigt irf
       eta: mixing parameter
       k: rate constant (inverse of life time)

    Returns:
       Convolution of normalized pseudo voigt profile and
       exponential decay :math:`(\\exp(-kt))`.
    '''

    u = exp_conv_gau(t, fwhm, k)
    v = exp_conv_cauchy(t, fwhm, k)

    return u + eta*(v-u)

# calculate derivative of the convolution of exponential decay and instrumental response function

def deriv_exp_conv_gau(t: Union[float, np.ndarray], fwhm: float,
                 k: float) -> np.ndarray:

    '''
    Compute derivative of exponential function convolved with normalized gaussian
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of gaussian distribution
      k: rate constant (inverse of life time)

    Returns:
     Derivative of Convolution of normalized gaussian distribution and exponential
     decay :math:`(\\exp(-kt))`.
    Note:

     * 1st column: df/dt
     * 2nd column: df/d(fwhm)
     * 3rd column: df/dk

    '''

    sigma = fwhm/(2*np.sqrt(2*np.log(2)))
    f = exp_conv_gau(t, fwhm, k)
    g = np.exp(-(t/sigma)**2/2)/np.sqrt(2*np.pi)

    if not isinstance(t, np.ndarray):
        grad = np.empty(3)
        grad[0] = g/sigma - k*f
        grad[1] = ((k**2*sigma)*f - (k+t/sigma**2)*g)/(2*np.sqrt(2*np.log(2)))
        grad[2] = (sigma**2*k-t)*f - sigma*g
    else:
        grad = np.empty((t.size, 3))
        grad[:, 0] = g/sigma - k*f
        grad[:, 1] = ((k**2*sigma)*f - (k+t/sigma**2)*g)/(2*np.sqrt(2*np.log(2)))
        grad[:, 2] = (sigma**2*k-t)*f - sigma*g

    return grad

def deriv_exp_conv_cauchy(t: Union[float, np.ndarray],
                    fwhm: float,
                    k: float) -> Union[float, np.ndarray]:

    '''
    Compute derivative of the convolution of exponential function and normalized cauchy
    distribution

    Args:
       t: time
       fwhm: full width at half maximum of cauchy distribution
       k: rate constant (inverse of life time)

    Returns:
      Derivative of convolution of normalized cauchy distribution and
      exponential decay :math:`(\\exp(-kt))`.
    
    Note:

     * 1st column: df/dt
     * 2nd column: df/d(fwhm)
     * 3rd column: df/dk
    '''

    if not isinstance(t, np.ndarray):
        grad = np.empty(3)
        if k == 0:
            grad[0] = 2/(np.pi*fwhm*(1+(2*t/fwhm)**2))
            grad[1] = -t/fwhm*grad[0]
            grad[2] = 0
        else:
            z = (t+complex(0, fwhm/2))
            f = exp1x(-k*z)
            tmp = -(k*f+1/z)/np.pi
            grad[0] = tmp.imag
            grad[1] = tmp.real/2
            grad[2] = -(t*f.imag+fwhm*f.real/2)/np.pi
    else:
        grad = np.empty((t.size, 3))
        if k == 0:
            grad[:, 0] = 2/(np.pi*fwhm*(1+(2*t/fwhm)**2))
            grad[:, 1] = -t/fwhm*grad[:, 0]
            grad[:, 2] = 0
        else:
            z = (t+complex(0, fwhm/2))
            f = exp1x(-k*z)
            tmp = -(k*f+1/z)/np.pi
            grad[:, 0] = tmp.imag
            grad[:, 1] = tmp.real/2
            grad[:, 2] = -(t*f.imag+fwhm*f.real/2)/np.pi
    return grad

# calculate derivative of the convolution of sum of exponential decay and instrumental response function

def deriv_exp_sum_conv_gau(t: np.ndarray, fwhm: float,
                 k: np.ndarray, c: np.ndarray, base: Optional[bool] = True) -> np.ndarray:

    '''
    Compute derivative of sum of exponential function convolved with normalized gaussian
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of gaussian distribution
      k: rate constant (inverse of life time)
      c: coefficient
      base: include baseline (i.e. k=0)

    Returns:
     Derivative of Convolution of normalized gaussian distribution and sum of exponential
     decay :math:`(\\exp(-kt))`.
    Note:

     * 1st column: df/dt
     * 2nd column: df/d(fwhm)
     * 2+i th column: df/dk_i
    '''
    grad = np.zeros((t.size, 2+k.size))
    for i in range(k.size):
        grad_i = deriv_exp_conv_gau(t, fwhm, k[i])
        grad[:, 0] = grad[:, 0] + c[i]*grad_i[:, 0]
        grad[:, 1] = grad[:, 1] + c[i]*grad_i[:, 1]
        grad[:, 2+i] = c[i]*grad_i[:, 2]
    if base:
        grad_i = deriv_exp_conv_gau(t, fwhm, 0)
        grad[:, 0] = grad[:, 0] + c[-1]*grad_i[:, 0]
        grad[:, 1] = grad[:, 1] + c[-1]*grad_i[:, 1]

    return grad

def deriv_exp_sum_conv_cauchy(t: np.ndarray, fwhm: float,
                 k: np.ndarray, c: np.ndarray, base: Optional[bool] = True) -> np.ndarray:

    '''
    Compute derivative of sum of exponential function convolved with normalized cauchy
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of cauchy distribution
      k: rate constant (inverse of life time)
      c: coefficient
      base: include baseline (i.e. k=0)

    Returns:
     Derivative of Convolution of normalized cauchy distribution and sum of exponential
     decay :math:`(\\exp(-kt))`.
    Note:

     * 1st column: df/dt
     * 2nd column: df/d(fwhm)
     * 2+i th column: df/dk_i
    '''
    grad = np.zeros((t.size, 2+k.size))
    for i in range(k.size):
        grad_i = deriv_exp_conv_cauchy(t, fwhm, k[i])
        grad[:, 0] = grad[:, 0] + c[i]*grad_i[:, 0]
        grad[:, 1] = grad[:, 1] + c[i]*grad_i[:, 1]
        grad[:, 2+i] = c[i]*grad_i[:, 2]
    if base:
        grad_i = deriv_exp_conv_cauchy(t, fwhm, 0)
        grad[:, 0] = grad[:, 0] + c[-1]*grad_i[:, 0]
        grad[:, 1] = grad[:, 1] + c[-1]*grad_i[:, 1]

    return grad

def exp_mod_gau_cplx(t: Union[float, np.ndarray], sigma: float,
                     kr: float, ki: float) -> \
                        Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:
    '''
    Complex version of exponentially (exp(-krt+i*kit)) modified gaussian function

    Args:
     t: time
     sigma: deviation of gaussian distribution
     kr: real part of decay constant
     ki: imag part of decay constant
    
    Returns:
     complex version of exponentially modified gaussian distribution with mean = 0
    
    Note:
     first element is cosine and second element is sine.
    '''

    isigmak_cplx = complex(ki*sigma, kr*sigma)
    iz = isigmak_cplx - complex(0,1)*t/sigma

    if not isinstance(t, np.ndarray):
        if iz.imag > 0:
            ans = 1/2*np.exp(-(t/sigma)**2/2) * \
                wofz(iz/np.sqrt(2))
        else:
            ans = np.exp(isigmak_cplx**2/2-isigmak_cplx*iz) - \
                1/2*np.exp(-(t/sigma)**2/2)*wofz(-iz/np.sqrt(2)) 
    else:
        mask = iz.imag > 0
        inv_mask = np.invert(mask)
        ans = np.empty(t.size, dtype=np.complex128)
        ans[mask] = 1/2*np.exp(-(t[mask]/sigma)**2/2) * \
            wofz(iz[mask]/np.sqrt(2))
        ans[inv_mask] = np.exp(isigmak_cplx**2/2-isigmak_cplx*iz[inv_mask]) - \
            1/2*np.exp(-(t[inv_mask]/sigma)**2/2)*wofz(-iz[inv_mask]/np.sqrt(2))

    return ans.real, ans.imag

def dmp_osc_conv_cauchy_pair(t: Union[float, np.ndarray], fwhm: float,
k: float, T: float) -> Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:

    '''
    Compute damped oscillation convolved with normalized cauchy
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of cauchy distribution
      k: damping constant (inverse of life time)
      T: period of vibration 
      phase: phase factor

    Returns:
     Tuple of convolution of normalized cauchy distribution and 
     damped oscillation 
     :math:`(\\exp(-kt)cos(2\\pi t/T))` and :math:`(\\exp(-kt)sin(2\\pi t/T))`.
    '''

    gamma = fwhm/2; omega = 2*np.pi/T 
    z1 = (-k*t-omega*gamma) + complex(0,1)*(-k*gamma+omega*t)
    z2 = (-k*t+omega*gamma) + complex(0,-1)*(k*gamma+omega*t)
    ans1 = exp1x(z1)/(2*np.pi)+\
        np.exp(z1.real)*(-np.sin(z1.imag)+complex(0, 1)*np.cos(z1.imag))*np.heaviside(z1.imag, 1)
    ans2 = exp1x(z2)/(2*np.pi)
    return ans1.imag + ans2.imag, ans2.real - ans1.real

def dmp_osc_conv_gau(t: Union[float, np.ndarray], fwhm: float,
k: float, T: float, phase: float) -> Union[float, np.ndarray]:

    '''
    Compute damped oscillation convolved with normalized gaussian
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of gaussian distribution
      k: damping constant (inverse of life time)
      T: period of vibration 
      phase: phase factor

    Returns:
     Convolution of normalized gaussian distribution and 
     damped oscillation :math:`(\\exp(-kt)cos(2\\pi t/T+phase))`.
    '''

    sigma = fwhm/(2*np.sqrt(2*np.log(2)))
    cosine, sine = exp_mod_gau_cplx(t, sigma, k, 2*np.pi/T)

    return cosine*np.cos(phase)-sine*np.sin(phase)

def dmp_osc_conv_cauchy(t: Union[float, np.ndarray], fwhm: float,
k: float, T: float, phase: float) -> Union[float, np.ndarray]:

    '''
    Compute damped oscillation convolved with normalized cauchy
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of cauchy distribution
      k: damping constant (inverse of life time)
      T: period of vibration 
      phase: phase factor

    Returns:
     Convolution of normalized cauchy distribution and 
     damped oscillation :math:`(\\exp(-kt)cos(2\\pi t/T+phase))`.
    '''

    cosine, sine = dmp_osc_conv_cauchy_pair(t, fwhm, k, T)

    return cosine*np.cos(phase)-sine*np.sin(phase)

def dmp_osc_conv_pvoigt(t: Union[float, np.ndarray], fwhm: float, eta: float,
k: float, T: float, phase: float) -> Union[float, np.ndarray]:

    '''
    Compute damped oscillation convolved with normalized pseudo
    voigt profile (i.e. linear combination of normalized gaussian and
    cauchy distribution)

    :math:`\\eta C(\\mathrm{fwhm}, t) + (1-\\eta)G(\\mathrm{fwhm}, t)`

    Args:
       t: time
       fwhm: uniform full width at half maximum parameter
       eta: mixing parameter
       k: damping constant (inverse of life time)
       T: period of vibration 
       phase: phase factor

    Returns:
     Convolution of normalized pseudo voigt profile and
     damped oscillation :math:`(\\exp(-kt)cos(2\\pi t/T+phase))`.
    '''

    u = dmp_osc_conv_gau(t, fwhm, k, T, phase)
    v = dmp_osc_conv_cauchy(t, fwhm, k, T, phase)

    return u + eta*(v-u)

def deriv_dmp_osc_conv_gau(t: Union[float, np.ndarray], fwhm: float,
k: float, T: float, phase: float) -> np.ndarray:

    '''
    Compute derivative of the convolution of damped oscillation and 
    normalized gaussian distribution

    Args:
      t: time
      fwhm: full width at half maximum of gaussian distribution
      k: damping constant (inverse of life time)
      T: period of vibration 
      phase: phase factor

    Returns:
     Derivative of Convolution of normalized gaussian distribution and 
     damped oscillation :math:`(\\exp(-kt)cos(2\\pi t/T+phase))`.
    
    Note:

     * 1st column: df/dt
     * 2nd column: df/d(fwhm)
     * 3rd column: df/dk
     * 4th column: df/dT
     * 5th column: df/d(phase)
    '''

    sigma = fwhm/(2*np.sqrt(2*np.log(2))); omega = 2*np.pi/T
    tmp1, tmp2 = exp_mod_gau_cplx(t, sigma, k, omega)
    freal = np.cos(phase)*tmp1 - np.sin(phase)*tmp2
    fimag = np.cos(phase)*tmp2 + np.sin(phase)*tmp1
    tmp3 = np.exp(-(t/sigma)**2/2)/np.sqrt(2*np.pi)
    greal = np.cos(phase)*tmp3; gimag = np.sin(phase)*tmp3

    if not isinstance(t, np.ndarray):
        grad = np.empty(5)
        grad[0] = greal/sigma - k*freal-omega*fimag
        grad[1] = (sigma*((k**2-omega**2)*freal + 2*k*omega*fimag) - 
        omega*gimag - (k+t/sigma**2)*greal)/(2*np.sqrt(2*np.log(2)))
        grad[2] = sigma**2*(k*freal+omega*fimag)-t*freal - sigma*greal
        grad[3] = -omega/T*(sigma**2*(k*fimag-omega*freal)-t*fimag - sigma*gimag)
        grad[4] = -fimag
    else:
        grad = np.empty((t.size, 5))
        grad[:, 0] = greal/sigma - k*freal-omega*fimag
        grad[:, 1] = (sigma*((k**2-omega**2)*freal + 2*k*omega*fimag) - 
        omega*gimag - (k+t/sigma**2)*greal)/(2*np.sqrt(2*np.log(2)))
        grad[:, 2] = sigma**2*(k*freal+omega*fimag)-t*freal - sigma*greal
        grad[:, 3] = -omega/T*(sigma**2*(k*fimag-omega*freal)-t*fimag - sigma*gimag)
        grad[:, 4] = -fimag
    
    return grad

def deriv_dmp_osc_conv_cauchy(t: Union[float, np.ndarray], fwhm: float,
k: float, T: float, phase: float) -> Union[float, np.ndarray]:

    '''
    Compute derivative of convolution of damped oscillation and normalized cauchy
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of cauchy distribution
      k: damping constant (inverse of life time)
      T: period of vibration 
      phase: phase factor

    Returns:
     Gradient of Convolution of normalized cauchy distribution and 
     damped oscillation :math:`(\\exp(-kt)cos(2\\pi t/T+phase))`.

    Note:

     * 1st column: df/dt
     * 2nd column: df/d(fwhm)
     * 3rd column: df/dk
     * 4th column: df/dT
     * 5th column: df/d(phase)
    '''

    gamma = fwhm/2; omega = 2*np.pi/T 
    z1 = (-k*t-omega*gamma) + complex(0,1)*(-k*gamma+omega*t)
    z2 = (-k*t+omega*gamma) + complex(0,-1)*(k*gamma+omega*t)

    f1 = complex(np.cos(phase), np.sin(phase))*exp1x(z1)/(2*np.pi)+np.exp(z1.real)*(-np.sin(z1.imag+phase)+complex(0,1)*np.cos(z1.imag+phase))*\
        np.heaviside(z1.imag, 1)
    f2 = complex(np.cos(phase), -np.sin(phase))*exp1x(z2)

    grad_z1 = f1 - complex(np.cos(phase), np.sin(phase))/(2*np.pi*z1)
    grad_z2 = (f2 - complex(np.cos(phase), -np.sin(phase))/z2)/(2*np.pi)
    sum = grad_z1 + grad_z2; diff = grad_z1 - grad_z2
    grad_t = -k*sum.imag + omega*diff.real
    grad_fwhm = -(omega*diff.imag+k*sum.real)/2
    grad_k = -(t*sum.imag+gamma*sum.real)
    grad_T = omega/T*(gamma*diff.imag-t*diff.real)
    grad_phase = f1.real-f2.real/(2*np.pi)

    if not isinstance(t, np.ndarray):
        grad = np.empty(5)
        grad[0] = grad_t
        grad[1] = grad_fwhm
        grad[2] = grad_k
        grad[3] = grad_T
        grad[4] = grad_phase
    else:
        grad = np.empty((t.size, 5))
        grad[:, 0] = grad_t
        grad[:, 1] = grad_fwhm
        grad[:, 2] = grad_k
        grad[:, 3] = grad_T
        grad[:, 4] = grad_phase
    
    return grad

def deriv_dmp_osc_sum_conv_gau(t: np.ndarray, fwhm: float,
k: np.ndarray, T: np.ndarray, phase: np.ndarray, c: np.ndarray) -> np.ndarray:

    '''
    Compute derivative of sum of damped oscillation function convolved with normalized gaussian
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of gaussian distribution
      k: rate constant (inverse of life time)
      T: period
      phase: phase factor
      c: coefficient

    Returns:
     Derivative of Convolution of normalized gaussian distribution and 
     damped oscillation :math:`(\\exp(-kt)cos(2\\pi t/T+phase))`.
    Note:
     * 1st column: df/dt
     * 2nd column: df/d(fwhm)
     * 2+i th column: df/dk_i :math:`(1 \\leq i \\leq {num}_{comp})`
     * 2+num_comp+i th column: df/dT_i :math:`(1 \\leq i \\leq {num}_{comp})`
     * :math:`2+2{num}_{comp}+i` th column: df/d(phase_i) :math:`(1 \\leq i \\leq {num}_{comp})`
    '''
    grad = np.zeros((t.size, 2+3*k.size))
    for i in range(k.size):
        grad_i = deriv_dmp_osc_conv_gau(t, fwhm, k[i], T[i], phase[i])
        grad[:, 0] = grad[:, 0] + c[i]*grad_i[:, 0]
        grad[:, 1] = grad[:, 1] + c[i]*grad_i[:, 1]
        grad[:, 2+i] = c[i]*grad_i[:, 2]
        grad[:, 2+k.size+i] = c[i]*grad_i[:, 3]
        grad[:, 2+2*k.size+i] = c[i]*grad_i[:, 4]

    return grad

def deriv_dmp_osc_sum_conv_cauchy(t: np.ndarray, fwhm: float,
k: np.ndarray, T: np.ndarray, phase: np.ndarray, c: np.ndarray) -> np.ndarray:

    '''
    Compute derivative of sum of damped oscillation function convolved with normalized cauchy
    distribution

    Args:
      t: time
      fwhm: full width at half maximum of cauchy distribution
      k: rate constant (inverse of life time)
      T: period
      phase: phase factor
      c: coefficient

    Returns:
     Derivative of Convolution of normalized cauchy distribution and 
     damped oscillation :math:`(\\exp(-kt)cos(2\\pi t/T+phase))`.
    Note:
     * 1st column: df/dt
     * 2nd column: df/d(fwhm)
     * 2+i th column: df/dk_i :math:`(1 \\leq i \\leq {num}_{comp})`
     * 2+num_comp+i th column: df/dT_i :math:`(1 \\leq i \\leq {num}_{comp})`
     * :math:`2+2{num}_{comp}+i` th column: df/d(phase_i) :math:`(1 \\leq i \\leq {num}_{comp})`
    '''
    grad = np.zeros((t.size, 2+3*k.size))
    for i in range(k.size):
        grad_i = deriv_dmp_osc_conv_cauchy(t, fwhm, k[i], T[i], phase[i])
        grad[:, 0] = grad[:, 0] + c[i]*grad_i[:, 0]
        grad[:, 1] = grad[:, 1] + c[i]*grad_i[:, 1]
        grad[:, 2+i] = c[i]*grad_i[:, 2]
        grad[:, 2+k.size+i] = c[i]*grad_i[:, 3]
        grad[:, 2+2*k.size+i] = c[i]*grad_i[:, 4]

    return grad




