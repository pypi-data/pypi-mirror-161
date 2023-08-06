# match scale
# match scaling of each energy scan data via one reference time scan data

import argparse
import numpy as np

from ..mathfun.irf import calc_fwhm, calc_eta
from ..mathfun import fact_anal_exp_conv
from ..mathfun.A_matrix import make_A_matrix_exp
from .misc import read_data

description = '''
match scale: match scaling of each energy scan data to one reference time delay scan data.
Experimentally measured time delay scan data has unsystematic error, which makes correct scaling of
each energy scan data ambiguous. To reduce such ambiguity, it fits reference time delay scan with the sum of
the convolution of exponential decay and instrumental response function.  
'''

epilog = '''
*Note

1. Fitting parameters (time_zero, fwhm, tau) are should be evaluated previosuly from fit_tscan utility.
2. Time zero of reference time delay scan and energy scan should be same.
3. Energy scan range contains energy of reference time delay scan.
4. if you set shape of irf to pseudo voigt (pv), then you should provide two full width at half maximum
   value for gaussian and cauchy parts, respectively.
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


def match_scale():

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
    parser.add_argument('prefix',
                        help='prefix for energy scan files ' +
                        'It will read prefix_i.txt')
    parser.add_argument('--ref_tscan_energy', type=float,
    help='energy of reference time delay scan')
    parser.add_argument('--ref_tscan_file',
    help='filename for reference time delay scan data')
    parser.add_argument('--escan_time', type=float, nargs='+',
                         help='time points for energy scan data')
    parser.add_argument('-t0', '--time_zero', type=float,
                        help='time zero for reference time scan')
    parser.add_argument('--tau', type=float, nargs='*',
                        help='lifetime of each component')
    parser.add_argument('--no_base', action='store_false',
                        help='exclude baseline')
    parser.add_argument('-o', '--out', default='out',
                        help='prefix for scaled energy scan and error')
    args = parser.parse_args()

    prefix = args.prefix
    out_prefix = args.out

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
    else:
        if (args.fwhm_G is None) or (args.fwhm_L is None):
            raise Exception('You are using pseudo voigt irf,' +
            'so you should set both fwhm_G and fwhm_L!\n')
        else:
            fwhm = calc_fwhm(args.fwhm_G, args.fwhm_L)
            eta = calc_eta(args.fwhm_G, args.fwhm_L)

    if args.tau is None:
        base = True
    else:
        tau = np.array(args.tau)
        base = args.no_base

    if (args.time_zero is None):
        print('You should set time_zeros!\n')
        return
    else:
        time_zero = args.time_zero
    
    ref_tscan_energy = args.ref_tscan_energy
    ref_tscan_data = np.genfromtxt(args.ref_tscan_file)
    escan_time = np.array(args.escan_time)
    e = np.genfromtxt(f'{prefix}_1.txt')[:, 0]
    escan_data, escan_eps = read_data(prefix, escan_time.size, e.size, 10)
    print(f'It reads {escan_time.size} number of energy scan!\n')

    escan_data_scaled = np.empty((escan_data.shape[0], escan_data.shape[1]+1))
    escan_data_scaled[:, 0] = e
    e_ref_idx = np.argwhere(e == ref_tscan_energy)[0][0]

    c = fact_anal_exp_conv(ref_tscan_data[:,0]-time_zero, fwhm, tau, base, irf, eta,
    intensity=ref_tscan_data[:, 1], eps=ref_tscan_data[:, 2])
    A_slec = make_A_matrix_exp(escan_time-time_zero, fwhm, tau, base, irf)
    fit_slec = c@A_slec
    sample_e = escan_data[e_ref_idx, :]
    scale_factor = fit_slec/sample_e
    escan_data_scaled[:, 1:] = np.einsum('j,ij->ij', scale_factor, escan_data)
    escan_eps_scaled = np.einsum('j,ij->ij', scale_factor, escan_eps)

    header_escan = '\t'.join(list(map(str,escan_time)))
    

    np.savetxt(f'{out_prefix}_escan_scaled.txt', escan_data_scaled, header='energy \t'+header_escan)
    np.savetxt(f'{out_prefix}_eps_scaled.txt', escan_eps_scaled, fmt=len(escan_time)*['%.8e'], header=header_escan)
    np.savetxt(f'{out_prefix}_escan_time.txt', escan_time)

    return