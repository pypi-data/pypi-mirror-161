# fit_static Basic Example

Basic usage example ``fit_static`` utility.
Yon can find example file from [TRXASprefitpack-example](https://github.com/pistack/TRXASprefitpack-example/tree/v0.6.0) fit_static subdirectory.

## Fitting with voigt profile

1. In  `fit_static` sub directory,  you can find ``example_static.txt`` file.
This example is generated from Library example, fitting with static spectrum.
2. Type ``fit_static -h`` Then it prints help message. You can find detailed description of arguments in the utility section of this document.
3. First find edge feature. Type ``fit_static example_static.txt  --mode voigt --edge g --e0_edge 8992 --fwhm_edge 10 -o edge --do_glb``.

The first and the only one positional argument is the filename of static spectrum file to read.

Second optional argument ``--mode`` sets fitting model, we set ``--mode voigt`` that is fitting with sum of voigt component. 

Third optional argument ``--edge``, if it is not set, it does not include edge feature. In this example we set `--edge g`, that is gaussian type edge.

Fourth optional argument ``--e0_edge`` is initial edge position.

Fifth optional argument is ``--fwhm_edge`` initial guess for fwhm paramter of edge. 

Last optional argument is `-o` it sets name of `hdf5` file to save fitting result and directory to save text file format of fitting result.

4. After fitting process is finished, you can see both fitting result plot and report for fitting result in the console. Upper part of plot shows fitting curve and experimental data. Lower part of plot shows residual of fit (data-fit).

5. Inspecting residual panel, we can find two voigt component centered near 8985 and 9000

![png](fit_static_example_file/find_edge.png)

1. Based on this now add two voigt component.

2. Type ``fit_static example_static.txt  --mode voigt --e0_voigt 8985 9000 --fwhm_L_voigt 2 6  --edge g --e0_edge 8992 --fwhm_edge 10 -o fit --do_glb``.

First additional optional argument ``--e0_voigt`` sets initial peak position of voigt component

Second additional optional argument ``--fwhm_L_voigt`` sets initial fwhm parameter of voigt component. In this example we only set lorenzian part of voigt componnet, so our voigt component is indeed lorenzian component.

3. After fitting process is finished, you can see fitting result plot.

![png](fit_static_example_file/fit_voigt.png)

## Description for Output file in fit directory.

* ``fit.txt`` contains fitting and each component curve

* ``weight.txt`` weight of each fitting component

* ``fit_summary.txt`` Summary of fitting result.

* ``res.txt`` contains residual of fit



## Fitting with theoretical calculated line spectrum

Comming Soon... 