# Fitting with time delay scan (model: sum of exponential decay and damped oscillation)
## Objective
1. Fitting with sum of exponential decay model and damped oscillation model
2. Save and Load fitting result
3. Calculates species associated coefficent from fitting result
4. Evaluates F-test based confidence interval


In this example, we only deal with gaussian irf 


```python
# import needed module
import numpy as np
import matplotlib.pyplot as plt
import TRXASprefitpack
from TRXASprefitpack import solve_seq_model, rate_eq_conv, dmp_osc_conv_gau 
plt.rcParams["figure.figsize"] = (12,9)
```

## Version information


```python
print(TRXASprefitpack.__version__)
```

    0.6.0
    

## Detecting oscillation feature


```python
# Generates fake experiment data
# Model: 1 -> 2 -> 3 -> GS
# lifetime tau1: 500 fs, tau2: 10 ps, tau3: 1000 ps
# oscillation: tau_osc: 1 ps, period_osc: 300 fs, phase: pi/4
# fwhm paramter of gaussian IRF: 100 fs

tau_1 = 0.5
tau_2 = 10
tau_3 = 1000
fwhm = 0.100
tau_osc = 1
period_osc = 0.3
phase = np.pi/4

# initial condition
y0 = np.array([1, 0, 0, 0])

# set time range (mixed step)
t_seq1 = np.arange(-2, -1, 0.2)
t_seq2 = np.arange(-1, 1, 0.02)
t_seq3 = np.arange(1, 5, 0.2)
t_seq4 = np.arange(5, 10, 1)
t_seq5 = np.arange(10, 100, 10)
t_seq6 = np.arange(100, 1000, 100)
t_seq7 = np.linspace(1000, 2000, 2)

t_seq = np.hstack((t_seq1, t_seq2, t_seq3, t_seq4, t_seq5, t_seq6, t_seq7))

eigval_seq, V_seq, c_seq = solve_seq_model(np.array([tau_1, tau_2, tau_3]), y0)

# Now generates measured transient signal
# Last element is ground state

abs_1 = [1, 1, 1, 0]; abs_1_osc = 0.05
abs_2 = [0.5, 0.8, 0.2, 0]; abs_2_osc = 0.001
abs_3 = [-0.5, 0.7, 0.9, 0]; abs_3_osc = -0.002
abs_4 = [0.6, 0.3, -1, 0]; abs_4_osc = 0.0018

t0 = np.random.normal(0, fwhm, 4) # perturb time zero of each scan

# generate measured data

y_obs_1 = rate_eq_conv(t_seq-t0[0], fwhm, abs_1, eigval_seq, V_seq, c_seq, irf='g')+\
    abs_1_osc*dmp_osc_conv_gau(t_seq-t0[0], fwhm, 1/tau_osc, period_osc, phase)
y_obs_2 = rate_eq_conv(t_seq-t0[1], fwhm, abs_2, eigval_seq, V_seq, c_seq, irf='g')+\
    abs_2_osc*dmp_osc_conv_gau(t_seq-t0[1], fwhm, 1/tau_osc, period_osc, phase)
y_obs_3 = rate_eq_conv(t_seq-t0[2], fwhm, abs_3, eigval_seq, V_seq, c_seq, irf='g')+\
    abs_3_osc*dmp_osc_conv_gau(t_seq-t0[2], fwhm, 1/tau_osc, period_osc, phase)
y_obs_4 = rate_eq_conv(t_seq-t0[3], fwhm, abs_4, eigval_seq, V_seq, c_seq, irf='g')+\
    abs_4_osc*dmp_osc_conv_gau(t_seq-t0[3], fwhm, 1/tau_osc, period_osc, phase)

# generate random noise with (S/N = 200)

# Define noise level (S/N=200) w.r.t peak
eps_obs_1 = np.max(np.abs(y_obs_1))/200*np.ones_like(y_obs_1)
eps_obs_2 = np.max(np.abs(y_obs_2))/200*np.ones_like(y_obs_2)
eps_obs_3 = np.max(np.abs(y_obs_3))/200*np.ones_like(y_obs_3)
eps_obs_4 = np.max(np.abs(y_obs_4))/200*np.ones_like(y_obs_4)

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
print(f'tau_3: {tau_3}')
print(f'tau_osc: {tau_osc}')
print(f'period_osc: {period_osc}')
print(f'phase_osc: {phase}')
for i in range(4):
    print(f't_0_{i+1}: {t0[i]}')
print('-'*24)
print('Excited Species contribution')
print(f'scan 1: {abs_1[0]} \t {abs_1[1]} \t {abs_1[2]}')
print(f'scan 2: {abs_2[0]} \t {abs_2[1]} \t {abs_2[2]}')
print(f'scan 3: {abs_3[0]} \t {abs_3[1]} \t {abs_3[2]}')
print(f'scan 4: {abs_4[0]} \t {abs_4[1]} \t {abs_4[2]}')

param_exact = [fwhm, t0[0], t0[1], t0[2], t0[3], tau_1, tau_2, tau_3, tau_osc, period_osc, phase]

data1 = np.vstack((t_seq, i_obs_1, eps_obs_1)).T
data2 = np.vstack((t_seq, i_obs_2, eps_obs_2)).T
data3 = np.vstack((t_seq, i_obs_3, eps_obs_3)).T
data4 = np.vstack((t_seq, i_obs_4, eps_obs_4)).T

np.savetxt('./fit_tscan/osc/example_osc_1.txt', data1)
np.savetxt('./fit_tscan/osc/example_osc_2.txt', data2)
np.savetxt('./fit_tscan/osc/example_osc_3.txt', data3)
np.savetxt('./fit_tscan/osc/example_osc_4.txt', data4)
```

    ------------------------
    fwhm: 0.1
    tau_1: 0.5
    tau_2: 10
    tau_3: 1000
    tau_osc: 1
    period_osc: 0.3
    phase_osc: 0.7853981633974483
    t_0_1: 0.05053956334459484
    t_0_2: -0.07163546673750752
    t_0_3: -0.004390946806632458
    t_0_4: 0.13670418243246096
    ------------------------
    Excited Species contribution
    scan 1: 1 	 1 	 1
    scan 2: 0.5 	 0.8 	 0.2
    scan 3: -0.5 	 0.7 	 0.9
    scan 4: 0.6 	 0.3 	 -1
    


```python
# plot model experimental data

plt.errorbar(t_seq, i_obs_1, eps_obs_1, label='1')
plt.errorbar(t_seq, i_obs_2, eps_obs_2, label='2')
plt.errorbar(t_seq, i_obs_3, eps_obs_3, label='3')
plt.errorbar(t_seq, i_obs_4, eps_obs_4, label='4')
plt.legend()
plt.show()
```


    
![png](Fit_Transient_Both_files/Fit_Transient_Both_6_0.png)
    



```python
plt.errorbar(t_seq, i_obs_1, eps_obs_1, label='1')
plt.errorbar(t_seq, i_obs_2, eps_obs_2, label='2')
plt.errorbar(t_seq, i_obs_3, eps_obs_3, label='3')
plt.errorbar(t_seq, i_obs_4, eps_obs_4, label='4')
plt.legend()
plt.xlim(-10*fwhm, 20*fwhm)
plt.show()
```


    
![png](Fit_Transient_Both_files/Fit_Transient_Both_7_0.png)
    


We can show oscillation feature at scan 1. First try fitting without oscillation.


```python
# import needed module for fitting
from TRXASprefitpack import fit_transient_exp

# time, intensity, eps should be sequence of numpy.ndarray
t = [t_seq] 
intensity = [np.vstack((i_obs_1, i_obs_2, i_obs_3, i_obs_4)).T]
eps = [np.vstack((eps_obs_1, eps_obs_2, eps_obs_3, eps_obs_4)).T]

# set initial guess
irf = 'g' # shape of irf function
fwhm_init = 0.15
t0_init = np.array([0, 0, 0, 0])
# test with one decay module
tau_init = np.array([0.2, 20, 1500])

fit_result_decay = fit_transient_exp(irf, fwhm_init, t0_init, tau_init, False, do_glb=True, t=t, intensity=intensity, eps=eps)

```


```python
# print fitting result
print(fit_result_decay)
```

    [Model information]
        model : decay
        irf: g
        fwhm:  0.1008
        eta:  0.0000
        base: False
     
    [Optimization Method]
        global: basinhopping
        leastsq: trf
     
    [Optimization Status]
        nfev: 3456
        status: 0
        global_opt msg: requested number of basinhopping iterations completed successfully
        leastsq_opt msg: `ftol` termination condition is satisfied.
     
    [Optimization Results]
        Total Data points: 600
        Number of effective parameters: 20
        Degree of Freedom: 580
        Chi squared:  1060.8466
        Reduced chi squared:  1.829
        AIC (Akaike Information Criterion statistic):  381.9358
        BIC (Bayesian Information Criterion statistic):  469.8743
     
    [Parameters]
        fwhm_G:  0.10077973 +/-  0.00091351 ( 0.91%)
        t_0_1_1:  0.05003520 +/-  0.00042857 ( 0.86%)
        t_0_1_2: -0.07119986 +/-  0.00060856 ( 0.85%)
        t_0_1_3: -0.00538671 +/-  0.00076649 ( 14.23%)
        t_0_1_4:  0.13664093 +/-  0.00066225 ( 0.48%)
        tau_1:  0.50197077 +/-  0.00270331 ( 0.54%)
        tau_2:  10.00304080 +/-  0.05645921 ( 0.56%)
        tau_3:  1003.82449967 +/-  4.76296335 ( 0.47%)
     
    [Parameter Bound]
        fwhm_G:  0.075 <=  0.10077973 <=  0.3
        t_0_1_1: -0.3 <=  0.05003520 <=  0.3
        t_0_1_2: -0.3 <= -0.07119986 <=  0.3
        t_0_1_3: -0.3 <= -0.00538671 <=  0.3
        t_0_1_4: -0.3 <=  0.13664093 <=  0.3
        tau_1:  0.075 <=  0.50197077 <=  1.2
        tau_2:  4.8 <=  10.00304080 <=  76.8
        tau_3:  307.2 <=  1003.82449967 <=  4915.2
     
     
    [Component Contribution]
        DataSet dataset_1:
         #tscan	tscan_1	tscan_2	tscan_3	tscan_4
         decay 1	-1.29%	-28.41%	-51.13%	 8.89%
         decay 2	-0.71%	 54.18%	-9.62%	 52.56%
         decay 3	 97.99%	 17.41%	 39.25%	-38.55%
     
    [Parameter Correlation]
        Parameter Correlations >  0.1 are reported.
        (t_0_1_1, fwhm_G) =  0.106
        (t_0_1_2, fwhm_G) =  0.103
        (tau_1, t_0_1_2) =  0.118
        (tau_1, t_0_1_3) = -0.347
        (tau_2, t_0_1_2) =  0.101
        (tau_2, t_0_1_4) =  0.145
        (tau_3, tau_2) = -0.156
    


```python
# plot fitting result and experimental data

color_lst = ['red', 'blue', 'green', 'black']

for i in range(4):
    plt.errorbar(t[0], intensity[0][:, i], eps[0][:, i], label=f'expt {i+1}', color=color_lst[i])
    plt.errorbar(t[0], fit_result_decay['fit'][0][:, i], label=f'fit {i+1}', color=color_lst[i])

plt.legend()
plt.show()
```


    
![png](Fit_Transient_Both_files/Fit_Transient_Both_11_0.png)
    



```python
# plot with shorter time range

for i in range(4):
    plt.errorbar(t[0], intensity[0][:, i], eps[0][:, i], label=f'expt {i+1}', color=color_lst[i])
    plt.errorbar(t[0], fit_result_decay['fit'][0][:, i], label=f'fit {i+1}', color=color_lst[i])

plt.legend()
plt.xlim(-10*fwhm_init, 20*fwhm_init)
plt.show()

```


    
![png](Fit_Transient_Both_files/Fit_Transient_Both_12_0.png)
    


There may exists oscillation in experimental scan 1. To show oscillation feature plot residual (expt-fit)


```python
# To show oscillation feature plot residual
for i in range(4):
    plt.errorbar(t[0], fit_result_decay['res'][0][:, i], eps[0][:, i], label=f'res {i+1}', color=color_lst[i])

plt.legend()
plt.xlim(-10*fwhm_init, 20*fwhm_init)
plt.show()
```


    
![png](Fit_Transient_Both_files/Fit_Transient_Both_14_0.png)
    


Only residual for experimental scan 1 shows clear oscillation feature, Now add oscillation feature.


```python
from TRXASprefitpack import fit_transient_both
tau_osc_init = np.array([1.5])
period_osc_init = np.array([0.5])

fit_result_decay_osc = fit_transient_both(irf, fwhm_init, t0_init, tau_init, 
tau_osc_init, period_osc_init,
False, do_glb=True, t=t, intensity=intensity, eps=eps)

```


```python
# print fitting result
print(fit_result_decay_osc)
```

    [Model information]
        model : both
        irf: g
        fwhm:  0.0998
        eta:  0.0000
        base: False
     
    [Optimization Method]
        global: basinhopping
        leastsq: trf
     
    [Optimization Status]
        nfev: 13494
        status: 0
        global_opt msg: requested number of basinhopping iterations completed successfully
        leastsq_opt msg: `ftol` termination condition is satisfied.
     
    [Optimization Results]
        Total Data points: 600
        Number of effective parameters: 30
        Degree of Freedom: 570
        Chi squared:  638.1717
        Reduced chi squared:  1.1196
        AIC (Akaike Information Criterion statistic):  97.0066
        BIC (Bayesian Information Criterion statistic):  228.9145
     
    [Parameters]
        fwhm_G:  0.09984398 +/-  0.00075909 ( 0.76%)
        t_0_1_1:  0.05061665 +/-  0.00039406 ( 0.78%)
        t_0_1_2: -0.07132916 +/-  0.00051803 ( 0.73%)
        t_0_1_3: -0.00474142 +/-  0.00064774 ( 13.66%)
        t_0_1_4:  0.13670938 +/-  0.00056220 ( 0.41%)
        tau_1:  0.50172568 +/-  0.00215798 ( 0.43%)
        tau_2:  10.00631278 +/-  0.04434765 ( 0.44%)
        tau_3:  1002.83212275 +/-  3.72071882 ( 0.37%)
        tau_osc_1:  1.28461622 +/-  0.25058768 ( 19.51%)
        period_osc_1:  0.29797454 +/-  0.00220269 ( 0.74%)
     
    [Parameter Bound]
        fwhm_G:  0.075 <=  0.09984398 <=  0.3
        t_0_1_1: -0.3 <=  0.05061665 <=  0.3
        t_0_1_2: -0.3 <= -0.07132916 <=  0.3
        t_0_1_3: -0.3 <= -0.00474142 <=  0.3
        t_0_1_4: -0.3 <=  0.13670938 <=  0.3
        tau_1:  0.075 <=  0.50172568 <=  1.2
        tau_2:  4.8 <=  10.00631278 <=  76.8
        tau_3:  307.2 <=  1002.83212275 <=  4915.2
        tau_osc_1:  0.3 <=  1.28461622 <=  4.8
        period_osc_1:  0.075 <=  0.29797454 <=  1.2
     
    [Phase Factor]
        DataSet dataset_1:
         #tscan	tscan_1	tscan_2	tscan_3	tscan_4
         dmp_osc 1	 0.2120 π	 0.4132 π	 0.8410 π	 0.2091 π
     
    [Component Contribution]
        DataSet dataset_1:
         #tscan	tscan_1	tscan_2	tscan_3	tscan_4
         decay 1	 0.01%	-28.40%	-51.00%	 8.90%
         decay 2	-1.21%	 54.11%	-9.61%	 52.46%
         decay 3	 94.45%	 17.39%	 39.18%	-38.48%
        dmp_osc 1	 4.34%	 0.11%	 0.22%	 0.16%
     
    [Parameter Correlation]
        Parameter Correlations >  0.1 are reported.
        (t_0_1_1, fwhm_G) =  0.241
        (t_0_1_2, fwhm_G) =  0.154
        (t_0_1_4, fwhm_G) =  0.116
        (tau_1, t_0_1_2) =  0.111
        (tau_1, t_0_1_3) = -0.348
        (tau_2, t_0_1_2) =  0.103
        (tau_2, t_0_1_4) =  0.133
        (tau_3, tau_2) = -0.156
        (period_osc_1, fwhm_G) = -0.251
        (period_osc_1, t_0_1_1) = -0.451
    


```python
# plot residual and oscilation fit

for i in range(1):
    plt.errorbar(t[0], intensity[0][:, i]-fit_result_decay_osc['fit_decay'][0][:, i], eps[0][:, i], label=f'res {i+1}', color='black')
    plt.errorbar(t[0], fit_result_decay_osc['fit_osc'][0][:, i], label=f'osc {i+1}', color='red')

plt.legend()
plt.xlim(-10*fwhm_init, 20*fwhm_init)
plt.show()

print()


```


    
![png](Fit_Transient_Both_files/Fit_Transient_Both_18_0.png)
    


    
    


```python
# Compare fitting value and exact value
for i in range(len(fit_result_decay_osc['x'])):
    print(f"{fit_result_decay_osc['param_name'][i]}: {fit_result_decay_osc['x'][i]} (fit) \t {param_exact[i]} (exact)")
```

    fwhm_G: 0.09984398023073539 (fit) 	 0.1 (exact)
    t_0_1_1: 0.050616647691810734 (fit) 	 0.05053956334459484 (exact)
    t_0_1_2: -0.07132916197304762 (fit) 	 -0.07163546673750752 (exact)
    t_0_1_3: -0.004741422504451592 (fit) 	 -0.004390946806632458 (exact)
    t_0_1_4: 0.1367093818502816 (fit) 	 0.13670418243246096 (exact)
    tau_1: 0.5017256765256979 (fit) 	 0.5 (exact)
    tau_2: 10.006312781399181 (fit) 	 10 (exact)
    tau_3: 1002.8321227541483 (fit) 	 1000 (exact)
    tau_osc_1: 1.284616223329954 (fit) 	 1 (exact)
    period_osc_1: 0.29797453736969626 (fit) 	 0.3 (exact)
    


```python
# save fitting result to file
from TRXASprefitpack import save_TransientResult, load_TransientResult

save_TransientResult(fit_result_decay_osc, 'example_decay_osc') # save fitting result to example_decay_2.h5
loaded_result = load_TransientResult('example_decay_osc') # load fitting result from example_decay_2.h5
```

Now deduce species associated difference coefficient from sequential decay model


```python
y0 = np.array([1, 0, 0, 0]) # initial cond
eigval, V, c = solve_seq_model(loaded_result['x'][5:-2], y0)

# compute scaled V matrix
V_scale = np.einsum('j,ij->ij', c, V)
diff_abs_fit = np.linalg.solve(V_scale[:-1, :-1].T, loaded_result['c'][0][:-1,:]) 
# slice last column and row corresponding to ground state
# exclude oscillation factor

# compare with exact result
print('-'*24)
print('[Species Associated Difference Coefficent]')
print('scan # \t ex 1 (fit) \t ex 1 (exact) \t ex 2 (fit) \t ex 2 (exact) \t ex 3 (exact)')
print(f'1 \t {diff_abs_fit[0,0]} \t {abs_1[0]}  \t {diff_abs_fit[1,0]} \t {abs_1[1]} \t {diff_abs_fit[2,0]} \t {abs_1[2]}')
print(f'2 \t {diff_abs_fit[0,1]} \t {abs_2[0]}  \t {diff_abs_fit[1,1]} \t {abs_2[1]} \t {diff_abs_fit[2,1]} \t {abs_2[2]}')
print(f'3 \t {diff_abs_fit[0,2]} \t {abs_3[0]}  \t {diff_abs_fit[1,2]} \t {abs_3[1]} \t {diff_abs_fit[2,2]} \t {abs_3[2]}')
print(f'4 \t {diff_abs_fit[0,3]} \t {abs_4[0]}  \t {diff_abs_fit[1,3]} \t {abs_4[1]} \t {diff_abs_fit[2,3]} \t {abs_4[2]}')

```

    ------------------------
    [Species Associated Difference Coefficent]
    scan # 	 ex 1 (fit) 	 ex 1 (exact) 	 ex 2 (fit) 	 ex 2 (exact) 	 ex 3 (exact)
    1 	 0.999814728016317 	 1  	 0.9998813520856183 	 1 	 1.0020621741915658 	 1
    2 	 0.5013994541791791 	 0.5  	 0.8002106071258839 	 0.8 	 0.20017964124729995 	 0.2
    3 	 -0.498563790521078 	 -0.5  	 0.6989863593941319 	 0.7 	 0.9022594839616441 	 0.9
    4 	 0.6007902340276545 	 0.6  	 0.29855248807181206 	 0.3 	 -1.0000321282616873 	 -1
    

It also matches well, as expected.

Now calculates `F-test` based confidence interval.


```python
from TRXASprefitpack import confidence_interval

ci_result = confidence_interval(loaded_result, 0.05) # set significant level: 0.05 -> 95% confidence level
print(ci_result) # report confidence interval
```

    [Report for Confidence Interval]
        Method: f
        Significance level:  5.000000e-02
     
    [Confidence interval]
        0.09984398 -  0.00147569 <= b'fwhm_G' <=  0.09984398 +  0.00147812
        0.05061665 -  0.00076623 <= b't_0_1_1' <=  0.05061665 +  0.00076005
        -0.07132916 -  0.00102483 <= b't_0_1_2' <= -0.07132916 +  0.00099725
        -0.00474142 -  0.00126688 <= b't_0_1_3' <= -0.00474142 +  0.00127079
        0.13670938 -  0.00110796 <= b't_0_1_4' <=  0.13670938 +  0.001104
        0.50172568 -  0.00418296 <= b'tau_1' <=  0.50172568 +  0.00422175
        10.00631278 -  0.08543495 <= b'tau_2' <=  10.00631278 +  0.08629124
        1002.83212275 -  7.26121914 <= b'tau_3' <=  1002.83212275 +  7.33143627
        1.28461622 -  0.40931793 <= b'tau_osc_1' <=  1.28461622 +  0.75237185
        0.29797454 -  0.00397536 <= b'period_osc_1' <=  0.29797454 +  0.00455939
    


```python
# compare with ase
from scipy.stats import norm

factor = norm.ppf(1-0.05/2)

print('[Confidence interval (from ASE)]')
for i in range(loaded_result['param_name'].size):
    print(f"{loaded_result['x'][i]: .8f} - {factor*loaded_result['x_eps'][i] :.8f}", 
          f"<= {loaded_result['param_name'][i]} <=", f"{loaded_result['x'][i] :.8f} + {factor*loaded_result['x_eps'][i]: .8f}")
```

    [Confidence interval (from ASE)]
     0.09984398 - 0.00148779 <= b'fwhm_G' <= 0.09984398 +  0.00148779
     0.05061665 - 0.00077233 <= b't_0_1_1' <= 0.05061665 +  0.00077233
    -0.07132916 - 0.00101533 <= b't_0_1_2' <= -0.07132916 +  0.00101533
    -0.00474142 - 0.00126955 <= b't_0_1_3' <= -0.00474142 +  0.00126955
     0.13670938 - 0.00110190 <= b't_0_1_4' <= 0.13670938 +  0.00110190
     0.50172568 - 0.00422955 <= b'tau_1' <= 0.50172568 +  0.00422955
     10.00631278 - 0.08691980 <= b'tau_2' <= 10.00631278 +  0.08691980
     1002.83212275 - 7.29247489 <= b'tau_3' <= 1002.83212275 +  7.29247489
     1.28461622 - 0.49114282 <= b'tau_osc_1' <= 1.28461622 +  0.49114282
     0.29797454 - 0.00431719 <= b'period_osc_1' <= 0.29797454 +  0.00431719
    

However, as you can see, in many case, ASE does not much different from more sophisticated `f-test` based error estimation.
