# calc_dads
# Calculate decay associated difference spectrum from experimental 
# energy scan data and the convolution of sum of exponential decay and
# instrumental response function.

import argparse
import numpy as np
import matplotlib.pyplot as plt
from ..driver import dads
from ..mathfun.irf import calc_eta, calc_fwhm

description = '''
calc dads: Calculate decay associated difference spectrum from experimental energy scan data and
the convolution of sum of exponential decay and instrumental response function
'''

epilog = '''
*Note
1. if you set shape of irf to pseudo voigt (pv), then you should provide two full width at half maximum value for gaussian and cauchy parts, respectively.
'''

irf_help = '''
shape of instrument response functon
g: gaussian distribution
c: cauchy distribution
pv: pseudo voigt profile, linear combination of gaussian distribution and cauchy distribution 
    pv = eta*c+(1-eta)*g 
    the uniform fwhm parameter and 
    mixing parameter are determined according to Journal of Applied Crystallography. 33 (6): 1311–1316. 
'''

fwhm_G_help = '''
full width at half maximum for gaussian shape
It would not be used when you set cauchy irf function
'''

fwhm_L_help = '''
full width at half maximum for cauchy shape
It would not be used when you did not set irf or use gaussian irf function
'''



def calc_dads():

    tmp = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=tmp,
                                     description=description,
                                     epilog=epilog)
    parser.add_argument('--irf', default='g', choices=['g', 'c', 'pv'],
                        help=irf_help)
    parser.add_argument('--fwhm_G', type=float,
                        help=fwhm_G_help)
    parser.add_argument('--fwhm_L', type=float,
                        help=fwhm_L_help)
    parser.add_argument('escan_file',
                        help='filename for scale corrected energy scan file')
    parser.add_argument('escan_err_file',
    help='filename for the scaled estimated experimental error of energy scan file')
    parser.add_argument('-t0', '--time_zero', type=float,
                        help='time zero of energy scan')
    parser.add_argument('--escan_time', type=float, nargs='+',
    help='time delay for each energy scan')
    parser.add_argument('--tau', type=float, nargs='+',
                        help='lifetime of each decay component')
    parser.add_argument('--no_base', action='store_false',
    help='Exclude baseline (i.e. very long lifetime component)')
    parser.add_argument('-o', '--out', default='out',
                        help='prefix for output files')
    args = parser.parse_args()

    irf = args.irf
    if irf == 'g':
        if args.fwhm_G is None:
            raise Exception('You are using gaussian irf, so you should set fwhm_G!\n')
        else:
            fwhm = args.fwhm_G
            eta = 0
    elif irf == 'c':
        if args.fwhm_L is None:
            raise Exception('You are using cauchy/lorenzian irf,' + 
            'so you should set fwhm_L!\n')
        else:
            fwhm = args.fwhm_L
            eta = 1
    else:
        if (args.fwhm_G is None) or (args.fwhm_L is None):
            raise Exception('You are using pseudo voigt irf,' +
            'so you should set both fwhm_G and fwhm_L!\n')
        else:
            fwhm = calc_fwhm(args.fwhm_G, args.fwhm_L)
            eta = calc_eta(args.fwhm_G, args.fwhm_L)

    if args.tau is None:
        raise Exception('Please set lifetime constants for each decay')
    else:
        tau = np.array(args.tau)
    
    if (args.time_zero is None):
        raise Exception('You should set time_zero for energy scan \n')
    else:
        time_zero = args.time_zero

    escan_data = np.genfromtxt(args.escan_file)
    escan_err = np.genfromtxt(args.escan_err_file)
    escan_time = np.array(args.escan_time)
    out_prefix = args.out
    base = args.no_base
    
    ads, ads_eps, fit = dads(escan_time-time_zero, fwhm, tau, base, irf, eta,
    intensity=escan_data[:,1:], eps=escan_err)

    e = escan_data[:,0]

    out_ads = np.vstack((e, ads)).T

    ads_header_lst = []
    for i in range(ads.shape[0]):
        ads_header.append(f'ex{i+1}')
    ads_header = '\t'.join(ads_header_lst)
    fit_header = '\t'.join(list(map(str, escan_time)))

    # save calculated dads results
    np.savetxt(f'{out_prefix}_dads.txt', out_ads, fmt=out_ads.shape[1]*['%.8e'], header='energy \t'+ads_header)
    np.savetxt(f'{out_prefix}_dads_eps.txt', ads_eps.T, fmt=ads_eps.shape[0]*['%.8e'], header=ads_header)
    np.savetxt(f'{out_prefix}_dads_fit.txt', fit, fmt=(len(escan_time)+1)*['%.8e'], header='energy \t'+fit_header)

    # plot dads results
    plt.figure(1)
    plt.title('Decay Associated Difference Spectrum')
    for i in range(ads.shape[0]):
        plt.errorbar(e, ads[i,:], ads_eps[i,:], label=f'decay {i+1}')
    plt.legend()

    offset = 2*np.max(np.abs(escan_data[:, 1:]))
    plt.figure(2)
    plt.title(f'Retrieved Energy Scan (time_zero: {time_zero:.3e}')
    for i in range(escan_time.size):
        plt.errorbar(e, escan_data[:, i+1]+i*offset, escan_err[:, i], marker='o', mfc='none',
        label=f'{escan_time[i]: .3e} (expt)')
        plt.plot(e, fit[:, i]+i*offset, label=f'{escan_time[i]: .3e} (fit)')
    plt.legend()
    plt.show()

    return