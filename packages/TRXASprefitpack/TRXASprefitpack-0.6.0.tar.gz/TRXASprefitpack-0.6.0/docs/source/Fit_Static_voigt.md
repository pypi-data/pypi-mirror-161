# Fitting with Static spectrum
## Objective
1. Fitting with sum of voigt profile model
2. Save and Load fitting result
3. Retrieve or interpolate experimental spectrum based on fitting result and calculates its derivative up to 2.


```python
# import needed module
import numpy as np
import matplotlib.pyplot as plt
import TRXASprefitpack
from TRXASprefitpack import voigt, edge_gaussian
plt.rcParams["figure.figsize"] = (12,9)
```

## Version information


```python
print(TRXASprefitpack.__version__)
```

    0.6.0
    


```python
# Generates fake experiment data
# Model: sum of 3 voigt profile and one gaussian edge fature

e0_1 = 8987
e0_2 = 9000
e0_edge = 8992
fwhm_G_1 = 0.8
fwhm_G_2 = 0.9
fwhm_L_1 = 3
fwhm_L_2 = 9
fwhm_edge = 7

# set scan range
e = np.linspace(8960, 9020, 160)

# generate model spectrum
model_static = 0.1*voigt(e-e0_1, fwhm_G_1, fwhm_L_1) + \
    0.7*voigt(e-e0_2, fwhm_G_2, fwhm_L_2) + \
        0.2*edge_gaussian(e-e0_edge, fwhm_edge)

# set noise level
eps = 1/1000
# generate random noise
noise_static = np.random.normal(0, eps, model_static.size)

# generate measured static spectrum
obs_static = model_static + noise_static
eps_static = eps*np.ones_like(model_static)
```


```python
# plot model experimental data

plt.errorbar(e, obs_static, eps_static, label='static')
plt.legend()
plt.show()
```


    
![png](Fit_Static_voigt_files/Fit_Static_voigt_5_0.png)
    



```python
# import needed module for fitting
from TRXASprefitpack import fit_static_voigt

# set initial guess 
e0_init = np.array([9000]) # initial peak position
fwhm_G_init = np.array([0]) # fwhm_G = 0 -> lorenzian
fwhm_L_init = np.array([8])

e0_edge = 8995 # initial edge position
fwhm_edge = 15 # initial edge width

fit_result_static = fit_static_voigt(e0_init, fwhm_G_init, fwhm_L_init, edge='g', edge_pos_init=e0_edge,
 edge_fwhm_init = fwhm_edge, do_glb=True, e=e, intensity=obs_static, eps=eps_static)

```


```python
# print fitting result
print(fit_result_static)
```

    [Model information]
        model : voigt
        edge: g
     
    [Optimization Method]
        global: basinhopping
        leastsq: trf
     
    [Optimization Status]
        nfev: 1630
        status: 0
        global_opt msg: requested number of basinhopping iterations completed successfully
        leastsq_opt msg: `xtol` termination condition is satisfied.
     
    [Optimization Results]
        Data points: 160
        Number of effective parameters: 6
        Degree of Freedom: 154
        Chi squared:  821.7233
        Reduced chi squared:  5.3359
        AIC (Akaike Information Criterion statistic):  273.7968
        BIC (Bayesian Information Criterion statistic):  292.2478
     
    [Parameters]
        e0_1:  8998.83756990 +/-  0.14369391 ( 0.00%)
        fwhm_(G, 1):  0.00000000 +/-  0.00000000 ( 0.00%)
        fwhm_(L, 1):  10.98042009 +/-  0.33685176 ( 3.07%)
        E0_g:  8992.31652251 +/-  0.07898415 ( 0.00%)
        fwhm_(G, edge):  8.93716972 +/-  0.14320764 ( 1.60%)
     
    [Parameter Bound]
        e0_1:  8996 <=  8998.83756990 <=  9004
        fwhm_(G, 1):  0 <=  0.00000000 <=  0
        fwhm_(L, 1):  4 <=  10.98042009 <=  16
        E0_g:  8965 <=  8992.31652251 <=  9025
        fwhm_(G, edge):  7.5 <=  8.93716972 <=  30
     
    [Component Contribution]
        Static spectrum
         voigt 1:  83.02%
         g type edge:  16.98%
     
    [Parameter Correlation]
        Parameter Correlations >  0.1 are reported.
        (fwhm_(L, 1), e0_1) = -0.217
        (E0_g, e0_1) = -0.843
        (E0_g, fwhm_(L, 1)) =  0.466
        (fwhm_(G, edge), e0_1) = -0.534
        (fwhm_(G, edge), fwhm_(L, 1)) = -0.309
        (fwhm_(G, edge), E0_g) =  0.443
    

Using `static_spectrum` function in TRXASprefitpack, you can directly evaluates fitted static spectrum from fitting result


```python
# plot fitting result and experimental data
from TRXASprefitpack import static_spectrum

plt.errorbar(e, obs_static, eps_static, label=f'expt', color='black')
plt.errorbar(e, static_spectrum(e, fit_result_static), label=f'fit', color='red')

plt.legend()
plt.show()
```


    
![png](Fit_Static_voigt_files/Fit_Static_voigt_9_0.png)
    


There exists one more peak near 8985 eV Region. To check this peak feature plot residual.


```python
# plot residual

plt.errorbar(e, obs_static-static_spectrum(e, fit_result_static), eps_static, label=f'residual', color='black')

plt.legend()
plt.xlim(8980, 8990)
plt.show()

```


    
![png](Fit_Static_voigt_files/Fit_Static_voigt_11_0.png)
    



```python
# try with two voigt feature 
# set initial guess from previous fitting result and
# current observation

# set initial guess 
e0_init = np.array([8987, 8999]) # initial peak position
fwhm_G_init = np.array([0, 0]) # fwhm_G = 0 -> lorenzian
fwhm_L_init = np.array([3, 11])

e0_edge = 8992.3 # initial edge position
fwhm_edge = 9 # initial edge width

fit_result_static_2 = fit_static_voigt(e0_init, fwhm_G_init, fwhm_L_init, edge='g', edge_pos_init=e0_edge,
 edge_fwhm_init = fwhm_edge, do_glb=True, e=e, intensity=obs_static, eps=eps_static)

```


```python
# print fitting result
print(fit_result_static_2)
```

    [Model information]
        model : voigt
        edge: g
     
    [Optimization Method]
        global: basinhopping
        leastsq: trf
     
    [Optimization Status]
        nfev: 2336
        status: 0
        global_opt msg: requested number of basinhopping iterations completed successfully
        leastsq_opt msg: `xtol` termination condition is satisfied.
     
    [Optimization Results]
        Data points: 160
        Number of effective parameters: 9
        Degree of Freedom: 151
        Chi squared:  133.1312
        Reduced chi squared:  0.8817
        AIC (Akaike Information Criterion statistic): -11.4142
        BIC (Bayesian Information Criterion statistic):  16.2624
     
    [Parameters]
        e0_1:  8987.00803091 +/-  0.05119092 ( 0.00%)
        e0_2:  8999.93625358 +/-  0.04990511 ( 0.00%)
        fwhm_(G, 1):  0.00000000 +/-  0.00000000 ( 0.00%)
        fwhm_(G, 2):  0.00000000 +/-  0.00000000 ( 0.00%)
        fwhm_(L, 1):  3.15526097 +/-  0.16440273 ( 5.21%)
        fwhm_(L, 2):  9.07517127 +/-  0.17038338 ( 1.88%)
        E0_g:  8992.00682571 +/-  0.01757046 ( 0.00%)
        fwhm_(G, edge):  7.11511594 +/-  0.07541568 ( 1.06%)
     
    [Parameter Bound]
        e0_1:  8985.5 <=  8987.00803091 <=  8988.5
        e0_2:  8993.5 <=  8999.93625358 <=  9004.5
        fwhm_(G, 1):  0 <=  0.00000000 <=  0
        fwhm_(G, 2):  0 <=  0.00000000 <=  0
        fwhm_(L, 1):  1.5 <=  3.15526097 <=  6
        fwhm_(L, 2):  5.5 <=  9.07517127 <=  22
        E0_g:  8974.3 <=  8992.00682571 <=  9010.3
        fwhm_(G, edge):  4.5 <=  7.11511594 <=  18
     
    [Component Contribution]
        Static spectrum
         voigt 1:  9.99%
         voigt 2:  69.96%
         g type edge:  20.05%
     
    [Parameter Correlation]
        Parameter Correlations >  0.1 are reported.
        (e0_2, e0_1) =  0.275
        (fwhm_(L, 1), e0_1) =  0.396
        (fwhm_(L, 1), e0_2) =  0.397
        (fwhm_(L, 2), e0_1) = -0.175
        (fwhm_(L, 2), e0_2) = -0.534
        (fwhm_(L, 2), fwhm_(L, 1)) = -0.426
        (E0_g, e0_1) =  0.235
        (E0_g, e0_2) = -0.478
        (E0_g, fwhm_(L, 1)) =  0.126
        (E0_g, fwhm_(L, 2)) =  0.527
        (fwhm_(G, edge), e0_1) = -0.508
        (fwhm_(G, edge), e0_2) = -0.718
        (fwhm_(G, edge), fwhm_(L, 1)) = -0.579
        (fwhm_(G, edge), fwhm_(L, 2)) =  0.539
        (fwhm_(G, edge), E0_g) =  0.162
    


```python
# plot fitting result and experimental data

plt.errorbar(e, obs_static, eps_static, label=f'expt', color='black')
plt.errorbar(e, static_spectrum(e, fit_result_static_2), label=f'fit', color='red')

plt.legend()
plt.show()


```


    
![png](Fit_Static_voigt_files/Fit_Static_voigt_14_0.png)
    



```python
# save and load fitting result
from TRXASprefitpack import save_StaticResult, load_StaticResult

save_StaticResult(fit_result_static_2, 'static_example') # save fitting result to static_example.h5
loaded_result = load_StaticResult('static_example') # load fitting result from static_example.h5
```


```python
# plot static spectrum
plt.plot(e, static_spectrum(e, loaded_result), label='static', color='black')
plt.plot(e, static_spectrum(e-1, loaded_result), label='static (1 eV shift)', color='blue')
plt.plot(e, static_spectrum(e+1, loaded_result), label='static (-1 eV shift)', color='red')
plt.legend()
plt.show()
```


    
![png](Fit_Static_voigt_files/Fit_Static_voigt_16_0.png)
    



```python
# plot its derivative up to second
plt.plot(e, static_spectrum(e, loaded_result, deriv_order=1), label='1st deriv', color='red')
plt.plot(e, static_spectrum(e, loaded_result, deriv_order=2), label='2nd deriv', color='blue')
plt.legend()
plt.show()
```


    
![png](Fit_Static_voigt_files/Fit_Static_voigt_17_0.png)
    


Optionally, you can calculated `F-test` based confidence interval


```python
from TRXASprefitpack import confidence_interval

ci_result = confidence_interval(loaded_result, 0.05) # set significant level: 0.05 -> 95% confidence level
print(ci_result) # report confidence interval
```

    [Report for Confidence Interval]
        Method: f
        Significance level:  5.000000e-02
     
    [Confidence interval]
        8987.00803091 -  0.10054262 <= b'e0_1' <=  8987.00803091 +  0.1040399
        8999.93625358 -  0.10109791 <= b'e0_2' <=  8999.93625358 +  0.09500443
        3.15526097 -  0.31563079 <= b'fwhm_(L, 1)' <=  3.15526097 +  0.33284129
        9.07517127 -  0.32642719 <= b'fwhm_(L, 2)' <=  9.07517127 +  0.33896081
        8992.00682571 -  0.03405656 <= b'E0_g' <=  8992.00682571 +  0.03514928
        7.11511594 -  0.14656975 <= b'fwhm_(G, edge)' <=  7.11511594 +  0.15095364
    


```python
# compare with ase
from scipy.stats import norm

factor = norm.ppf(1-0.05/2)

print('[Confidence interval (from ASE)]')
for i in range(loaded_result['param_name'].size):
    print(f"{loaded_result['x'][i] :.8f} - {factor*loaded_result['x_eps'][i] :.8f}", 
          f"<= {loaded_result['param_name'][i]} <=", f"{loaded_result['x'][i] :.8f} + {factor*loaded_result['x_eps'][i] :.8f}")
```

    [Confidence interval (from ASE)]
    8987.00803091 - 0.10033236 <= b'e0_1' <= 8987.00803091 + 0.10033236
    8999.93625358 - 0.09781222 <= b'e0_2' <= 8999.93625358 + 0.09781222
    0.00000000 - 0.00000000 <= b'fwhm_(G, 1)' <= 0.00000000 + 0.00000000
    0.00000000 - 0.00000000 <= b'fwhm_(G, 2)' <= 0.00000000 + 0.00000000
    3.15526097 - 0.32222343 <= b'fwhm_(L, 1)' <= 3.15526097 + 0.32222343
    9.07517127 - 0.33394528 <= b'fwhm_(L, 2)' <= 9.07517127 + 0.33394528
    8992.00682571 - 0.03443746 <= b'E0_g' <= 8992.00682571 + 0.03443746
    7.11511594 - 0.14781202 <= b'fwhm_(G, edge)' <= 7.11511594 + 0.14781202
    

In many case, ASE does not much different from more sophisticated `f-test` based error estimation.
