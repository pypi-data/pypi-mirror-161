# Features

## Utilites

* Match Utility
  1. match_scale: Match the scaling of each energy scan data to one reference time delay scan data
* Calc Utility
  1. calc_broad: broaden theoretically calculated line shape spectrum with voigt profile
  2. calc_dads: Calculates decay associated difference spectrum from experimental energy scan and sum of exponential decay model
  3. calc_sads: Calculates species associated difference spectrum frim experimental energy scan and 1st order rate equation model
* Fit Utility
  1. fit_static: fitting sum of voigt component or voigt broadened experimental spectrum with experimental static spectrum
  2. fit_tscan: Find lifetime constants or oscillation period from experimental time delay spectrum

## Libraries

* mathfun

  1. provides exact function for the convolution of exponential decay or exponentially damped oscillation and instrumental response function.
   There are three type of instrumental response function (gaussian, cauchy and pseudo voigt).
  2. provides factor analysis routine of time delay scan data, when time zero, lifetime constant and irf parameter (i.e. fwhm)
   are given.
  3. Solve diagonalizable 1st order rate equation exactly with arbitrary initial condition.
  4. Special fast solver for certain type (sequential decay and lower triangular rate equation) of 1st order rate equation

* res
 1. Provides scalar residual function and its gradient for 5 fitting model based on seperation scheme in least square regression.
  Such models are

    1. sum of voigt function, edge and polynomial baseline
    2. voigt broadened theoretical spectrum, edge and polynomial baseline
    3. Convolution of exponential decay and (gaussian, cauchy, pseudo voigt approximation) instrumental response function.
    4. Convolution of damped oscillation and (gaussian, cauchy, pseudo voigt approximation) instrumental response function.
    5. Sum of above two model.

 2. Provides lmfit compatible layer (`res_lmfit`) to directly use vector residual function defined in `TRXASprefitpack` to `lmfit`.
  However, currently only supports linear loss function. 

* driver
 1. Provides driver routine to fit static spectrum with two model based on seperation scheme in least square regression.

    1. sum of voigt function, edge and polynomial baseline
    2. voigt broadened theoretical spectrum, edge and polynomial baseline
 
 2. Provides driver routine to fit a number of time delay scan data sets with shared lifetime paramter based on seperation scheme in least square regression.

    1. Convolution of exponential decay and (gaussian, cauchy, pseudo voigt approximation) instrumental response function.
    2. Convolution of damped oscillation and (gaussian, cauchy, pseudo voigt approximation) instrumental response function.
    3. Sum of above two model.
 
 3. Save and load fitting result through `hdf5` format

 4. Provides routine to evaluate confidence interval and compare two fit based on `f-test`.

