# fit_tscan

fit tscan: fitting experimental time trace spectrum data with the convolution of the sum of 
1. exponential decay (mode = decay)
2. damped oscillation (mode = osc)
3. exponential decay, damped oscillation (mode=both)


and irf function. There are three types of irf function (gaussian, cauchy, pseudo voigt) are supported.
To calculate the contribution of each life time component, it solve least linear square problem via `scipy.linalg.lstsq` function.

* usage: fit_tscan 
                    [-h] [--mode {decay,osc,both}] [--irf {g,c,pv}] [--fwhm_G FWHM_G] [--fwhm_L FWHM_L] [--num_file NUM_FILE [NUM_FILE ...]] [-t0 TIME_ZEROS [TIME_ZEROS ...]] [-t0f TIME_ZEROS_FILE]
                    [--tau [TAU ...]] [--tau_osc TAU_OSC [TAU_OSC ...]] [--period_osc PERIOD_OSC [PERIOD_OSC ...]] [--no_base] [--fix_irf] [--fix_t0] [--do_glb]
                    [-o OUTDIR] [--save_fig]
                    prefix [prefix ...]



* positional arguments:
  * prefix                prefix for tscan files It will read prefix_i.txt

* optional arguments:
  * -h, --help            show this help message and exit
  * --mode {decay,osc,both}
   Mode of fitting
    * `decay`: fitting with the sum of the convolution of exponential decay and instrumental response function
    * `osc`: fitting with the sum of the convolution of damped oscillation and instrumental response function
    * `both`: fitting with the sum of both decay and osc

  * --irf {g,c,pv}
  shape of instrument response functon

    * g: gaussian distribution
    * c: cauchy distribution
    * pv: pseudo voigt profile ${PV}(f_G, f_L) = \eta(f_G, f_L) C(f(f_G, f_L)) + (1-\eta(f_G, f_L)) G(f(f_G, f_L))$
      The uniform fwhm parameter $f(f_G, f_L)$ and mixing parameter $\eta(f_G, f_L)$ are determined according to 
      Journal of Applied Crystallography. 33 (6): 1311–1316.

  * --fwhm_G FWHM_G
   full width at half maximum for gaussian shape. It would not be used when you set cauchy irf function
  * --fwhm_L FWHM_L
   full width at half maximum for cauchy shape. It would not be used when you did not set irf or use gaussian irf function
  * --num_file NUM_FILE [NUM_FILE ...]
   number of scan file corresponding to each prefix
  * -t0 TIME_ZEROS [TIME_ZEROS ...], --time_zeros TIME_ZEROS [TIME_ZEROS ...]
   time zeros for each tscan
  * -t0f TIME_ZEROS_FILE, --time_zeros_file TIME_ZEROS_FILE
   filename for time zeros of each tscan
  * --tau [TAU ...]       lifetime of each decay component [mode: decay, both]
  * --tau_osc TAU_OSC [TAU_OSC ...]
   lifetime of each damped oscillation component [mode: osc, both]
  * --period_osc PERIOD_OSC [PERIOD_OSC ...]
   period of the vibration of each damped oscillation component [mode: osc, both]
  * --no_base             exclude baseline for fitting [mode: decay, both]
  * --fix_irf             fix irf parameter (fwhm_G, fwhm_L) during fitting process
  * --fix_t0              fix time zero parameter during fitting process.
  * --do_glb
   Whether or not use Global optimization Method. 
   When do_glb option is set then `basinhopping` global optimization algorithm will be used.
  * -o OUTDIR, --outdir OUTDIR
   name of directory to store output files
  * --save_fig            save plot instead of display

```{Note}

1. The number of time zero parameter should be same as the
   total number of scan to fit.

2. Every scan file whose prefix of filename is same should have same scan range

3. if you set shape of irf to pseudo voigt (pv), then
   you should provide two full width at half maximum
   value for gaussian and cauchy parts, respectively.

4. If you did not set tau and `mode=decay` then `--no_base` option is discouraged.

5. If you set `mode=decay` then any parameter whoose subscript is `osc` is discarded (i.e. tau_osc, period_osc).

6. If you set `mode=osc` then `tau` parameter is discarded. Also, baseline feature is not included in fitting function.

7. The number of tau_osc and period_osc parameter should be same

8. If you set `mode=both` then you should set `tau`, `tau_osc` and `period_osc`. 
 However the number of `tau` and `tau_osc` need not to be same.
```
