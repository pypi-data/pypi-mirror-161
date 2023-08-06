import argparse
import numpy as np
from ..mathfun import voigt_thy

policy_help = '''
Policy to match discrepency between experimental data and theoretical spectrum.
 'shift': constant shift peak position
 'scale': constant scale peak position
 'both': shift and scale peak position
'''


def calc_broad():
    description = '''
    calc_broad: Evaluates voigt broadened theoritical calc spectrum
    '''

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('peak',
                        help='filename for calculated line shape spectrum')
    parser.add_argument('e_min', type=float,
                        help='minimum energy')
    parser.add_argument('e_max', type=float,
                        help='maximum energy')
    parser.add_argument('e_step', type=float,
    help='energy step')
    parser.add_argument('A', type=float,
                        help='scale factor')
    parser.add_argument('fwhm_G', type=float,
                        help='Full Width at Half Maximum of gaussian shape')
    parser.add_argument('fwhm_L', type=float,
                        help='Full Width at Half Maximum of lorenzian shape')
    parser.add_argument('--shift_factor', type=float,
    help='parameter to shift peak position of thoretical spectrum')
    parser.add_argument('--scale_factor', type=float,
    help='paramter to scale peak position of theoretical spectrum')
    parser.add_argument('-o', '--out', help='prefix for output files')
    parser.add_argument('--policy', choices=['shift', 'scale', 'both'], type=str,
    help=policy_help)
    args = parser.parse_args()

    peak = np.genfromtxt(args.peak)[:,:2]
    if args.out is None:
        out = args.prefix
    else:
        out = args.out
    e_min = args.e_min
    e_max = args.e_max
    e_step = args.e_step
    A = args.A
    fwhm_G = args.fwhm_G
    fwhm_L = args.fwhm_L
    if args.policy is None:
        policy = 'shift'
        peak_factor = 0
    else:
        policy = args.policy
    
    if policy in ['shift', 'both'] and args.peak_shift is None:
        raise Exception(f"Your policy is {args.policy}, please set initial peak_shift parameter.")
    if policy in ['scale', 'both'] and args.peak_scale is None:
        raise Exception(f"Your policy is {args.policy}, please set peak_scale parameter.")

    if args.policy == 'shift':
        peak_factor = args.shift_factor
    elif args.policy == 'scale':
        peak_factor = args.scale_factor
    else:
        peak_factor = np.array([args.shift_factor, args.scale_factor])

    e = np.linspace(e_min, e_max, int((e_max-e_min)/e_step)+1)

    broadened_thy = A*voigt_thy(e, peak, fwhm_G, fwhm_L, peak_factor, policy)

    rescaled_stk = peak.copy()
    if policy == 'scale':
        rescaled_stk[:, 0] = rescaled_stk[:, 0]*peak_factor
    elif policy == 'shift':
        rescaled_stk[:, 0] = rescaled_stk[:, 0] - peak_factor
    else:
        rescaled_stk[:, 0] = peak_factor[1]*rescaled_stk[:, 0] - peak_factor[0]
    rescaled_stk[:, 1] = A*rescaled_stk[:, 1]/np.sum(rescaled_stk[:, 1])
    spec_thy = np.vstack((e, broadened_thy)).T

    np.savetxt(f'{out}_thy_stk.txt', rescaled_stk, fmt=['%.8e', '%.8e'], header='energy \t abs')
    np.savetxt(f'{out}_thy.txt', spec_thy, fmt=['%.8e', '%.8e'], header='energy \t abs')

    return
