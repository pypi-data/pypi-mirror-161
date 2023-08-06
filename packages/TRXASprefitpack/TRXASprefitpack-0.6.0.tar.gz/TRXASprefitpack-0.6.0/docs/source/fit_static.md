# fit_static

fit static: fitting static spectrum with

 * 'voigt': some of voigt component
 * 'thy' : theoretically calculated line spectrum broadened by voigt function


It also include edge and polynomial type baseline feature.

```{Note}
 1. If fwhm_G of voigt component is zero then this voigt component is treated as lorenzian
 2. If fwhm_L of voigt component is zero then this voigt component is treated as gaussian
 ```

* usage: fit_static
                     [-h] [--mode {voigt,thy}] [--e0_voigt [E0_VOIGT ...]] [--fwhm_G_voigt [FWHM_G_VOIGT ...]] [--fwhm_L_voigt [FWHM_L_VOIGT ...]] [--thy_file THY_FILE] [--fwhm_G_thy FWHM_G_THY] [--fwhm_L_thy FWHM_L_THY] [--policy {shift,scale,both}] [--peak_scale PEAK_SCALE] [--peak_shift PEAK_SHIFT] [--edge {g,l}] [--e0_edge E0_EDGE] [--fwhm_edge FWHM_EDGE]
                     [--base_order BASE_ORDER] [-o OUTDIR] [--do_glb]
                     filename



* positional arguments:
  * filename              filename for experimental spectrum

* optional arguments:
  * -h, --help            show this help message and exit
  * --mode {voigt,thy}    Mode of static spectrum fitting 
  
     * 'voigt': fitting with sum of voigt componenty 
     * 'thy': fitting with voigt broadend thoretical spectrum

  * --e0_voigt [E0_VOIGT ...]
                        peak position of each voigt component
  * --fwhm_G_voigt [FWHM_G_VOIGT ...]
                        full width at half maximum for gaussian shape It would be not used when you set lorenzian line shape
  * --fwhm_L_voigt [FWHM_L_VOIGT ...]
                        full width at half maximum for lorenzian shape It would be not used when you use gaussian line shape
  * --thy_file THY_FILE   filename which stores thoretical peak position and intensity.
  * --fwhm_G_thy FWHM_G_THY
                        gaussian part of uniform broadening parameter for theoretical line shape spectrum
  * --fwhm_L_thy FWHM_L_THY
                        lorenzian part of uniform broadening parameter for theoretical line shape spectrum
  * --policy {shift,scale,both}
                        Policy to match discrepency between experimental data and theoretical spectrum. 

      * 'shift': constant shift peak position 
      * 'scale': constant scale peak position 
      * 'both': shift and scale peak position

  * --peak_scale PEAK_SCALE
                        inital peak position scale parameter
  * --peak_shift PEAK_SHIFT
                        inital peak position shift parameter
  * --edge {g,l}          Type of edge function if not set, edge is not included. 
     * 'g': gaussian type edge function 
     * 'l': lorenzian type edge function

  * --e0_edge E0_EDGE     edge position
  * --fwhm_edge FWHM_EDGE
                        full width at half maximum parameter of edge
  * --base_order BASE_ORDER
                        Order of polynomial to correct baseline feature. If it is not set then baseline is not corrected
  * -o OUTDIR, --outdir OUTDIR
                        directory to store output file
  * --do_glb              Whether or not use Global optimization Method. When do_glb option is set then `basinhopping` global optimization algorithm will be used.