# calc_broad

calc_broad: calculates voigt broadened theoritical calc spectrum

* usage: calc_broad 
                       [-h] [--scale_energy] [-o OUT]
                       peak e_min e_max e_step A fwhm_G fwhm_L peak_factor



* positional arguments:
  * peak               filename for calculated line shape spectrum
  * e_min              minimum energy
  * e_max              maximum energy
  * e_step             energy step
  * A                  scale factor
  * fwhm_G             Full Width at Half Maximum of gaussian shape
  * fwhm_L             Full Width at Half Maximum of lorenzian shape

* optional arguments:
  * -h, --help            show this help message and exit
  * --policy {shift,scale,both}
    Policy to match discrepency between experimental data and theoretical spectrum. 
    
    * 'shift': constant shift peak position 
    * 'scale': constant scale peak position 
    * 'both': shift and scale peak position

  * --shift_factor SHIFT_FACTOR
                        parameter to shift peak position of thoretical spectrum
  * --scale_factor SCALE_FACTOR
                        paramter to scale peak position of theoretical spectrum
  * -o OUT, --out OUT     prefix for output files


