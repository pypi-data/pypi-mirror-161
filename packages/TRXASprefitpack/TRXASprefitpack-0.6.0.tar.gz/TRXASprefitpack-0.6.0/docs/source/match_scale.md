# match_scale

match scale: match scaling of each energy scan data to one reference time delay scan data.
Experimentally measured time delay scan data has unsystematic error, which makes correct scaling of
each energy scan data ambiguous. To reduce such ambiguity, it fits reference time delay scan with the sum of
the convolution of exponential decay and instrumental response function.

```{Note}
1. Fitting parameters (time_zero, fwhm, tau) are should be evaluated previosuly from fit_tscan utility.
2. Time zero of reference time delay scan and energy scan should be same.
3. Energy scan range contains energy of reference time delay scan.
4. if you set shape of irf to pseudo voigt (pv), then you should provide two full width at half maximum
   value for gaussian and cauchy parts, respectively.
```

* usage: match_scale 
                      [-h] [--irf {g,c,pv}] [--fwhm_G FWHM_G] [--fwhm_L FWHM_L] [--ref_tscan_energy REF_TSCAN_ENERGY] [--ref_tscan_file REF_TSCAN_FILE] [--escan_time ESCAN_TIME [ESCAN_TIME ...]]
                      [-t0 TIME_ZERO] [--tau [TAU ...]] [--no_base] [-o OUT]
                      prefix



* positional arguments:
  * prefix                prefix for energy scan files It will read prefix_i.txt

* optional arguments:
  * -h, --help            show this help message and exit
  * --irf {g,c,pv}
  shape of instrument response functon

    * g: gaussian distribution
    * c: cauchy distribution
    * pv: pseudo voigt profile ${PV}(f_G, f_L) = \eta(f_G, f_L) C(f(f_G, f_L)) + (1-\eta(f_G, f_L)) G(f(f_G, f_L))$
      The uniform fwhm parameter $f(f_G, f_L)$ and mixing parameter $\eta(f_G, f_L)$ are determined according to 
      Journal of Applied Crystallography. 33 (6): 1311–1316.
  * --fwhm_G FWHM_G       
                        full width at half maximum for gaussian shape
                        It would not be used when you set cauchy irf function
  * --fwhm_L FWHM_L       
                        full width at half maximum for cauchy shape
                        It would not be used when you did not set irf or use gaussian irf function
  * --ref_tscan_energy REF_TSCAN_ENERGY
                        energy of reference time delay scan
  * --ref_tscan_file REF_TSCAN_FILE
                        filename for reference time delay scan data
  * --escan_time ESCAN_TIME [ESCAN_TIME ...]
                        time points for energy scan data
  * -t0 TIME_ZERO, --time_zero TIME_ZERO
                        time zero for reference time scan
  * --tau [TAU ...]       lifetime of each component
  * --no_base             exclude baseline
  * -o OUT, --out OUT     prefix for scaled energy scan and error

