# Fitting with time delay scan (model: exponential decay)

## Objective
1. Fitting with exponential decay model
2. Save and Load fitting result
3. Calculates species associated coefficent from fitting result
4. Evaluates F-test based confidence interval


In this example, we only deal with gaussian irf 


```python
# import needed module
import numpy as np
import matplotlib.pyplot as plt
import TRXASprefitpack
from TRXASprefitpack import solve_seq_model, rate_eq_conv 
plt.rcParams["figure.figsize"] = (12,9)
```

## Version information


```python
print(TRXASprefitpack.__version__)
```

    0.6.0


## Fitting with exponential decay model


```python
# Generates fake experiment data
# Model: 1 -> 2 -> GS
# lifetime tau1: 500 ps, tau2: 10 ns
# fwhm paramter of gaussian IRF: 100 ps

tau_1 = 500
tau_2 = 10000
fwhm = 100

# initial condition
y0 = np.array([1, 0, 0])

# set time range (mixed step)
t_seq1 = np.arange(-2500, -500, 100)
t_seq2 = np.arange(-500, 1500, 50)
t_seq3 = np.arange(1500, 5000, 250)
t_seq4 = np.arange(5000, 50000, 2500)

t_seq = np.hstack((t_seq1, t_seq2, t_seq3, t_seq4))

eigval_seq, V_seq, c_seq = solve_seq_model(np.array([tau_1, tau_2]), y0)

# Now generates measured transient signal
# Last element is ground state

abs_1 = [1, 1, 0]
abs_2 = [0.5, 0.8, 0]
abs_3 = [-0.5, 0.7, 0]
abs_4 = [0.6, 0.3, 0]

t0 = np.random.normal(0, fwhm, 4) # perturb time zero of each scan

# generate measured data

y_obs_1 = rate_eq_conv(t_seq-t0[0], fwhm, abs_1, eigval_seq, V_seq, c_seq, irf='g')
y_obs_2 = rate_eq_conv(t_seq-t0[1], fwhm, abs_2, eigval_seq, V_seq, c_seq, irf='g')
y_obs_3 = rate_eq_conv(t_seq-t0[2], fwhm, abs_3, eigval_seq, V_seq, c_seq, irf='g')
y_obs_4 = rate_eq_conv(t_seq-t0[3], fwhm, abs_4, eigval_seq, V_seq, c_seq, irf='g')

# generate random noise with (S/N = 20)

# Define noise level (S/N=20) w.r.t peak
eps_obs_1 = np.max(np.abs(y_obs_1))/20*np.ones_like(y_obs_1)
eps_obs_2 = np.max(np.abs(y_obs_2))/20*np.ones_like(y_obs_2)
eps_obs_3 = np.max(np.abs(y_obs_3))/20*np.ones_like(y_obs_3)
eps_obs_4 = np.max(np.abs(y_obs_4))/20*np.ones_like(y_obs_4)

# generate random noise
noise_1 = np.random.normal(0, eps_obs_1, t_seq.size)
noise_2 = np.random.normal(0, eps_obs_2, t_seq.size)
noise_3 = np.random.normal(0, eps_obs_3, t_seq.size)
noise_4 = np.random.normal(0, eps_obs_4, t_seq.size)


# generate measured intensity
i_obs_1 = y_obs_1 + noise_1
i_obs_2 = y_obs_2 + noise_2
i_obs_3 = y_obs_3 + noise_3
i_obs_4 = y_obs_4 + noise_4

# print real values

print('-'*24)
print(f'fwhm: {fwhm}')
print(f'tau_1: {tau_1}')
print(f'tau_2: {tau_2}')
for i in range(4):
    print(f't_0_{i+1}: {t0[i]}')
print('-'*24)
print('Excited Species contribution')
print(f'scan 1: {abs_1[0]} \t {abs_1[1]}')
print(f'scan 2: {abs_2[0]} \t {abs_2[1]}')
print(f'scan 3: {abs_3[0]} \t {abs_3[1]}')
print(f'scan 4: {abs_4[0]} \t {abs_4[1]}')

param_exact = [fwhm, t0[0], t0[1], t0[2], t0[3], tau_1, tau_2]
```

    ------------------------
    fwhm: 100
    tau_1: 500
    tau_2: 10000
    t_0_1: -93.0396119572383
    t_0_2: 38.815806904268705
    t_0_3: 31.07625235504534
    t_0_4: -95.75692103034174
    ------------------------
    Excited Species contribution
    scan 1: 1 	 1
    scan 2: 0.5 	 0.8
    scan 3: -0.5 	 0.7
    scan 4: 0.6 	 0.3



```python
# plot model experimental data

plt.errorbar(t_seq, i_obs_1, eps_obs_1, label='1')
plt.errorbar(t_seq, i_obs_2, eps_obs_2, label='2')
plt.errorbar(t_seq, i_obs_3, eps_obs_3, label='3')
plt.errorbar(t_seq, i_obs_4, eps_obs_4, label='4')
plt.legend()
plt.show()
```


    
![png](Fit_Transient_Exp_files/Fit_Transient_Exp_6_0.png)
    



```python
# import needed module for fitting
from TRXASprefitpack import fit_transient_exp

# time, intensity, eps should be sequence of numpy.ndarray
t = [t_seq] 
intensity = [np.vstack((i_obs_1, i_obs_2, i_obs_3, i_obs_4)).T]
eps = [np.vstack((eps_obs_1, eps_obs_2, eps_obs_3, eps_obs_4)).T]

# set initial guess
irf = 'g' # shape of irf function
fwhm_init = 100
t0_init = np.array([0, 0, 0, 0])
# test with one decay module
tau_init = np.array([15000])

fit_result_decay_1 = fit_transient_exp(irf, fwhm_init, t0_init, tau_init, False, do_glb=True, t=t, intensity=intensity, eps=eps)

```


```python
# print fitting result
print(fit_result_decay_1)
```

    [Model information]
        model : decay
        irf: g
        fwhm:  160.5049
        eta:  0.0000
        base: False
     
    [Optimization Method]
        global: basinhopping
        leastsq: trf
     
    [Optimization Status]
        nfev: 781
        status: 0
        global_opt msg: requested number of basinhopping iterations completed successfully
        leastsq_opt msg: `ftol` termination condition is satisfied.
     
    [Optimization Results]
        Total Data points: 368
        Number of effective parameters: 10
        Degree of Freedom: 358
        Chi squared:  2982.3453
        Reduced chi squared:  8.3306
        AIC (Akaike Information Criterion statistic):  789.9967
        BIC (Bayesian Information Criterion statistic):  829.0775
     
    [Parameters]
        fwhm_G:  160.50485365 +/-  30.07549216 ( 18.74%)
        t_0_1_1: -96.15617378 +/-  16.24443868 ( 16.89%)
        t_0_1_2:  81.75561525 +/-  15.49174901 ( 18.95%)
        t_0_1_3:  200.00000000 +/-  19.17535540 ( 9.59%)
        t_0_1_4: -132.51360113 +/-  23.94351677 ( 18.07%)
        tau_1:  13346.99367982 +/-  959.69336043 ( 7.19%)
     
    [Parameter Bound]
        fwhm_G:  50 <=  160.50485365 <=  200
        t_0_1_1: -200 <= -96.15617378 <=  200
        t_0_1_2: -200 <=  81.75561525 <=  200
        t_0_1_3: -200 <=  200.00000000 <=  200
        t_0_1_4: -200 <= -132.51360113 <=  200
        tau_1:  3200 <=  13346.99367982 <=  51200
     
    [Component Contribution]
        DataSet dataset_1:
         #tscan	tscan_1	tscan_2	tscan_3	tscan_4
         decay 1	 100.00%	 100.00%	 100.00%	 100.00%
     
    [Parameter Correlation]
        Parameter Correlations >  0.1 are reported.



```python
# plot fitting result and experimental data

color_lst = ['red', 'blue', 'green', 'black']

for i in range(4):
    plt.errorbar(t[0], intensity[0][:, i], eps[0][:, i], label=f'expt {i+1}', color=color_lst[i])
    plt.errorbar(t[0], fit_result_decay_1['fit'][0][:, i], label=f'fit {i+1}', color=color_lst[i])

plt.legend()
plt.show()
```


    
![png](Fit_Transient_Exp_files/Fit_Transient_Exp_9_0.png)
    


For scan 1 and 2, experimental data and fitting data match well. However for scan 3 and 4, they do not match at shorter time region (< 10000).


```python
# plot with shorter time range

for i in range(4):
    plt.errorbar(t[0], intensity[0][:, i], eps[0][:, i], label=f'expt {i+1}', color=color_lst[i])
    plt.errorbar(t[0], fit_result_decay_1['fit'][0][:, i], label=f'fit {i+1}', color=color_lst[i])

plt.legend()
plt.xlim(-10*fwhm_init, 20*fwhm_init)
plt.show()

```


    
![png](Fit_Transient_Exp_files/Fit_Transient_Exp_11_0.png)
    


There may exists shorter lifetime component.


```python
# try with double exponential decay
# set initial guess
irf = 'g' # shape of irf function
fwhm_init = 100
t0_init = np.array([0, 0, 0, 0])
# test with two decay module
tau_init = np.array([300, 15000])

fit_result_decay_2 = fit_transient_exp(irf, fwhm_init, t0_init, tau_init, False, do_glb=True, t=t, intensity=intensity, eps=eps)

```


```python
# print fitting result
print(fit_result_decay_2)
```

    [Model information]
        model : decay
        irf: g
        fwhm:  104.7125
        eta:  0.0000
        base: False
     
    [Optimization Method]
        global: basinhopping
        leastsq: trf
     
    [Optimization Status]
        nfev: 1085
        status: 0
        global_opt msg: requested number of basinhopping iterations completed successfully
        leastsq_opt msg: `ftol` termination condition is satisfied.
     
    [Optimization Results]
        Total Data points: 368
        Number of effective parameters: 15
        Degree of Freedom: 353
        Chi squared:  352.7762
        Reduced chi squared:  0.9994
        AIC (Akaike Information Criterion statistic):  14.4524
        BIC (Bayesian Information Criterion statistic):  73.0736
     
    [Parameters]
        fwhm_G:  104.71245991 +/-  8.74636550 ( 8.35%)
        t_0_1_1: -95.55454917 +/-  5.01009098 ( 5.24%)
        t_0_1_2:  35.91244388 +/-  7.34089597 ( 20.44%)
        t_0_1_3:  39.36590392 +/-  6.17818029 ( 15.69%)
        t_0_1_4: -93.10612763 +/-  4.44973137 ( 4.78%)
        tau_1:  487.90314761 +/-  18.31579044 ( 3.75%)
        tau_2:  10590.01652058 +/-  293.64560698 ( 2.77%)
     
    [Parameter Bound]
        fwhm_G:  50 <=  104.71245991 <=  200
        t_0_1_1: -200 <= -95.55454917 <=  200
        t_0_1_2: -200 <=  35.91244388 <=  200
        t_0_1_3: -200 <=  39.36590392 <=  200
        t_0_1_4: -200 <= -93.10612763 <=  200
        tau_1:  50 <=  487.90314761 <=  800
        tau_2:  3200 <=  10590.01652058 <=  51200
     
    [Component Contribution]
        DataSet dataset_1:
         #tscan	tscan_1	tscan_2	tscan_3	tscan_4
         decay 1	-5.44%	-30.39%	-62.74%	 48.42%
         decay 2	 94.56%	 69.61%	 37.26%	 51.58%
     
    [Parameter Correlation]
        Parameter Correlations >  0.1 are reported.
        (tau_1, fwhm_G) = -0.173
        (tau_1, t_0_1_3) = -0.351
        (tau_1, t_0_1_4) = -0.127
        (tau_2, tau_1) = -0.353



```python
# plot fitting result and experimental data

color_lst = ['red', 'blue', 'green', 'black']

for i in range(4):
    plt.errorbar(t[0], intensity[0][:, i], eps[0][:, i], label=f'expt {i+1}', color=color_lst[i])
    plt.errorbar(t[0], fit_result_decay_2['fit'][0][:, i], label=f'fit {i+1}', color=color_lst[i])

plt.legend()
plt.show()


```


    
![png](Fit_Transient_Exp_files/Fit_Transient_Exp_15_0.png)
    



```python
# plot with shorter time range

for i in range(4):
    plt.errorbar(t[0], intensity[0][:, i], eps[0][:, i], label=f'expt {i+1}', color=color_lst[i])
    plt.errorbar(t[0], fit_result_decay_2['fit'][0][:, i], label=f'fit {i+1}', color=color_lst[i])

plt.legend()
plt.xlim(-10*fwhm_init, 20*fwhm_init)
plt.show()
```


    
![png](Fit_Transient_Exp_files/Fit_Transient_Exp_16_0.png)
    


Two decay model fits well


```python
# Compare fitting value and exact value
for i in range(len(fit_result_decay_2['x'])):
    print(f"{fit_result_decay_2['param_name'][i]}: {fit_result_decay_2['x'][i]} (fit) \t {param_exact[i]} (exact)")
```

    fwhm_G: 104.71245991082807 (fit) 	 100 (exact)
    t_0_1_1: -95.55454917448591 (fit) 	 -93.0396119572383 (exact)
    t_0_1_2: 35.912443883340934 (fit) 	 38.815806904268705 (exact)
    t_0_1_3: 39.36590391968899 (fit) 	 31.07625235504534 (exact)
    t_0_1_4: -93.10612762609641 (fit) 	 -95.75692103034174 (exact)
    tau_1: 487.90314761113535 (fit) 	 500 (exact)
    tau_2: 10590.016520577483 (fit) 	 10000 (exact)


Fitting result and exact result are match well.
For future use or transfer your fitting result to your collaborator or superviser, you want to save or load fitting result from file.


```python
# save fitting result to file
from TRXASprefitpack import save_TransientResult, load_TransientResult

save_TransientResult(fit_result_decay_2, 'example_decay_2') # save fitting result to example_decay_2.h5
loaded_result = load_TransientResult('example_decay_2') # load fitting result from example_decay_2.h5
```

Now deduce species associated difference coefficient from sequential decay model


```python
y0 = np.array([1, 0, 0]) # initial cond
eigval, V, c = solve_seq_model(loaded_result['x'][5:], y0)

# compute scaled V matrix
V_scale = np.einsum('j,ij->ij', c, V)
diff_abs_fit = np.linalg.solve(V_scale[:-1, :-1].T, loaded_result['c'][0]) # slice last column and row corresponding to ground state

# compare with exact result
print('-'*24)
print('[Species Associated Difference Coefficent]')
print('scan # \t ex 1 (fit) \t ex 1 (exact) \t ex 2 (fit) \t ex 2 (exact)')
print(f'1 \t {diff_abs_fit[0,0]} \t {abs_1[0]}  \t {diff_abs_fit[1,0]} \t {abs_1[1]}')
print(f'2 \t {diff_abs_fit[0,1]} \t {abs_2[0]}  \t {diff_abs_fit[1,1]} \t {abs_2[1]}')
print(f'3 \t {diff_abs_fit[0,2]} \t {abs_3[0]}  \t {diff_abs_fit[1,2]} \t {abs_3[1]}')
print(f'4 \t {diff_abs_fit[0,3]} \t {abs_4[0]}  \t {diff_abs_fit[1,3]} \t {abs_4[1]}')

```

    ------------------------
    [Species Associated Difference Coefficent]
    scan # 	 ex 1 (fit) 	 ex 1 (exact) 	 ex 2 (fit) 	 ex 2 (exact)
    1 	 0.9757362905756569 	 1  	 0.9876141169252006 	 1
    2 	 0.4800552069439707 	 0.5  	 0.8128607523384913 	 0.8
    3 	 -0.4924221441952984 	 -0.5  	 0.6871993798829517 	 0.7
    4 	 0.5986150010542517 	 0.6  	 0.29455451213376227 	 0.3


It also matches well, as expected.

The error of paramter reported from `Transient` Driver is based on Asymptotic Standard Error.
However, strictly, ASE cannot be used in non-linear regression.
TRXASprefitpack provides alternative error estimation based on `F-test`.


```python
from TRXASprefitpack import confidence_interval

ci_result = confidence_interval(loaded_result, 0.05) # set significant level: 0.05 -> 95% confidence level
print(ci_result) # report confidence interval
```

    [Report for Confidence Interval]
        Method: f
        Significance level:  5.000000e-02
     
    [Confidence interval]
        104.71245991 -  17.2423326 <= b'fwhm_G' <=  104.71245991 +  18.8326056
        -95.55454917 -  9.90590253 <= b't_0_1_1' <= -95.55454917 +  9.64014804
        35.91244388 -  17.63761307 <= b't_0_1_2' <=  35.91244388 +  16.42968355
        39.36590392 -  11.63745069 <= b't_0_1_3' <=  39.36590392 +  11.72819974
        -93.10612763 -  8.66008546 <= b't_0_1_4' <= -93.10612763 +  8.63848049
        487.90314761 -  35.8040143 <= b'tau_1' <=  487.90314761 +  38.23433676
        10590.01652058 -  564.99522237 <= b'tau_2' <=  10590.01652058 +  587.56747294



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
    104.71245991 - 17.14256138 <= b'fwhm_G' <= 104.71245991 + 17.14256138
    -95.55454917 - 9.81959788 <= b't_0_1_1' <= -95.55454917 + 9.81959788
    35.91244388 - 14.38789172 <= b't_0_1_2' <= 35.91244388 + 14.38789172
    39.36590392 - 12.10901087 <= b't_0_1_3' <= 39.36590392 + 12.10901087
    -93.10612763 - 8.72131322 <= b't_0_1_4' <= -93.10612763 + 8.72131322
    487.90314761 - 35.89828961 <= b'tau_1' <= 487.90314761 + 35.89828961
    10590.01652058 - 575.53481389 <= b'tau_2' <= 10590.01652058 + 575.53481389


However, as you can see, in many case, ASE does not much different from more sophisticated `f-test` based error estimation.
