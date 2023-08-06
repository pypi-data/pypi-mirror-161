# fit tscan
# fitting tscan data
# Using sum of exponential decay convolved with
# normalized gaussian distribution
# normalized cauchy distribution
# normalized pseudo voigt profile
# (Mixing parameter eta is fixed according to
#  Journal of Applied Crystallography. 33 (6): 1311–1316.)

from typing import Optional
import os
from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from ..driver import TransientResult, save_TransientResult
from ..driver import fit_transient_exp, fit_transient_dmp_osc, fit_transient_both
from .misc import read_data

plt.rcParams['figure.figsize'] = (10, 5)

FITDRIVER = {'decay': fit_transient_exp, 'osc': fit_transient_dmp_osc, 'both': fit_transient_both}

def save_TransientResult_txt(result: TransientResult, dirname: str):
      '''
      save fitting result to the text file

      Args:
       result: fitting result
       dirname: name of the directory in which text files for fitting result are saved.
       name_of_dset: name of each data sets. If `name_of_dset` is None then it is set to [1,2,3,....]
       t: sequence of scan range
       eps: sequence of estimated error of each datasets
      
      Returns:
       `fit_summary.txt`: Summary for the fitting result
       `weight_{name_of_dset[i]}.txt`: Weight of each model component of i th dataset
       `phase_{name_of_dset[i]}.txt`: Phase factor of each oscillation component of i th dataset
       `fit_{name_of_dset[i]}.txt`: fitting curve for i th dataset
       `fit_osc_{name_of_dset[i]}.txt`: oscillation part of fitting curve for i th dataset [model = 'both']
       `fit_decay_{name_of_dset[i]}.txt`: decay part of fitting curve for i th dataset [model = 'both']
       `res_{name_f_dset[i]}_j.txt`: residual (fit-data) curve for j th scan of i th data
                                     The format of text file is (t, res, eps)

      
      Note:
       If `dirname` directory is not exists, it creates `dirname` directory.
      '''
      if not (Path.cwd()/dirname).exists():
            os.mkdir(dirname)
      
      with open(f'{dirname}/fit_summary.txt', 'w') as f:
            f.write(str(result))
      
      for i in range(len(result['t'])):
            coeff_fmt = result['eps'][i].shape[1]*['%.8e']
            fit_fmt = (1+result['eps'][i].shape[1])*['%.8e']
            coeff_header_lst = []
            fit_header_lst = ['time_delay']
            for j in range(result['eps'][i].shape[1]):
                  res_save = np.vstack((result['t'][i], result['res'][i][:,j], result['eps'][i][:,j])).T
                  np.savetxt(f"{dirname}/res_{result['name_of_dset'][i]}_{j+1}.txt", res_save,
                  fmt=['%.8e', '%.8e', '%.8e'], 
                  header=f"time_delay \t res_{result['name_of_dset'][i]}_{j+1} \t eps")
                  fit_header_lst.append(f"fit_{result['name_of_dset'][i]}_{j+1}")
                  coeff_header_lst.append(f"tscan_{result['name_of_dset'][i]}_{j+1}")
            
            fit_header = '\t'.join(fit_header_lst)
            coeff_header = '\t'.join(coeff_header_lst)

            np.savetxt(f"{dirname}/weight_{result['name_of_dset'][i]}.txt", result['c'][i], fmt=coeff_fmt,
            header=coeff_header)
            if result['model'] in ['dmp_osc', 'both']:
                np.savetxt(f"{dirname}/phase_{result['name_of_dset'][i]}.txt", result['phase'][i], fmt=coeff_fmt,
                header=coeff_header)   
            fit_save = np.vstack((result['t'][i], result['fit'][i].T)).T
            np.savetxt(f"{dirname}/fit_{result['name_of_dset'][i]}.txt", fit_save, fmt=fit_fmt, header=fit_header)
            if result['model'] == 'both':
                  fit_decay_save = np.vstack((result['t'][i], result['fit_decay'][i].T)).T
                  np.savetxt(f"{dirname}/fit_decay_{result['name_of_dset'][i]}.txt", fit_decay_save, fmt=fit_fmt, header=fit_header)
                  fit_osc_save = np.vstack((result['t'][i], result['fit_osc'][i].T)).T
                  np.savetxt(f"{dirname}/fit_osc_{result['name_of_dset'][i]}.txt", fit_osc_save, fmt=fit_fmt, header=fit_header)

      return

def plot_TransientResult(result: TransientResult, save_fig: Optional[str] = None):
      '''
      plot fitting Result

      Args:
       result: fitting result
       save_fig: prefix of saved png plots. If `save_fig` is `None`, plots are displayed instead of being saved.
      '''
      
      start = 0
      for i in range(len(result['t'])):
            for j in range(result['intensity'][i].shape[1]):
                  fig = plt.figure(start+j+1)
                  title = f'{result["name_of_dset"][i]} scan #{j+1}'
                  subtitle = f"Chi squared: {result['red_chi2_ind'][i][j]: .2f}"
                  plt.suptitle(title)
                  sub1 = fig.add_subplot(221)
                  sub1.set_title(subtitle)
                  sub1.errorbar(result['t'][i], result['intensity'][i][:, j], result['eps'][i][:, j], marker='o', mfc='none',
                  label=f'expt {title}', linestyle='none', color='black')
                  sub1.plot(result['t'][i], result['fit'][i][:, j], label=f'fit {title}', color='red')
                  sub1.legend()
                  sub2 = fig.add_subplot(222)
                  sub2.set_title(subtitle)
                  sub2.errorbar(result['t'][i], result['intensity'][i][:, j], result['eps'][i][:, j], marker='o', mfc='none',
                  label=f'expt {title}', linestyle='none', color='black')
                  sub2.plot(result['t'][i], result['fit'][i][:, j], label=f'fit {title}', color='red')
                  sub2.legend()
                  sub2.set_xlim(-10*result['fwhm'], 20*result['fwhm'])
                  sub3 = fig.add_subplot(223)
                  if result['model'] in ['decay', 'osc']:
                        sub3.errorbar(result['t'][i], result['res'][i][:, j], 
                        result['eps'][i][:, j], marker='o', mfc='none', 
                        label=f'res {title}', linestyle='none', color='black')
                  else:
                        sub3.errorbar(result['t'][i], result['intensity'][i][:, j]-result['fit_decay'][i][:, j], 
                        result['eps'][i][:, j], marker='o', mfc='none', label=f'expt osc {title}', 
                        linestyle='none', color='black')
                        sub3.plot(result['t'][i], result['fit_osc'][i][:, j], 
                        label=f'fit osc {title}', color='red')
                  sub3.legend()

                  sub4 = fig.add_subplot(224)
                  if result['model'] in ['decay', 'osc']:
                        sub4.errorbar(result['t'][i], result['res'][i][:, j], 
                        result['eps'][i][:, j], marker='o', mfc='none', 
                        label=f'res {title}', linestyle='none', color='black')
                  else:
                        sub4.errorbar(result['t'][i], result['intensity'][i][:, j]-result['fit_decay'][i][:, j], 
                        result['eps'][i][:, j], marker='o', mfc='none', 
                        label=f'expt osc {title}', linestyle='none', color='black')
                        sub4.plot(result['t'][i], result['fit_osc'][i][:, j], 
                        label=f'fit osc {title}', color='red')
                  sub4.set_xlim(-10*result['fwhm'], 20*result['fwhm'])
                  sub4.legend()
                  if save_fig is not None:
                        plt.savefig(f'./{save_fig}/{result["name_of_dset"][i]}_{j+1}.png')
            start = start + result['intensity'][i].shape[1]
      if save_fig is None:
            plt.show()
      return


description = '''
fit tscan: fitting experimental time trace spectrum data with the convolution of the sum of 
1. exponential decay (mode = decay)
2. damped oscillation (mode = osc)
3. exponential decay, damped oscillation (mode=both)
and irf function
There are three types of irf function (gaussian, cauchy, pseudo voigt)
To calculate the contribution of each life time component, it solve least linear square problem via scipy linalg lstsq module.
'''

epilog = '''
*Note

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

8. If you set `mode=both` then you should set `tau`, `tau_osc` and `period_osc`. However the number of `tau` and `tau_osc` need not to be same.
'''

mode_help = '''
Mode of fitting
 `decay`: fitting with the sum of the convolution of exponential decay and instrumental response function
 `osc`: fitting with the sum of the convolution of damped oscillation and instrumental response function
 `both`: fitting with the sum of both decay and osc
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

do_glb_help='''
Whether or not use Global optimization Method.
When do_glb option is set then `basinhopping` global optimization algorithm will be used.
'''


def fit_tscan():

    tmp = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=tmp,
                                     description=description,
                                     epilog=epilog)
    parser.add_argument('--mode', default='decay', choices=['decay', 'osc', 'both'],
    help=mode_help)
    parser.add_argument('--irf', default='g', choices=['g', 'c', 'pv'],
                        help=irf_help)
    parser.add_argument('--fwhm_G', type=float,
                        help=fwhm_G_help)
    parser.add_argument('--fwhm_L', type=float,
                        help=fwhm_L_help)
    parser.add_argument('prefix', nargs='+',
                        help='prefix for tscan files ' +
                        'It will read prefix_i.txt')
    parser.add_argument('--num_file', type=int, nargs='+',
                         help='number of scan file corresponding to each prefix')
    parser.add_argument('-t0', '--time_zeros', type=float, nargs='+',
                        help='time zeros for each tscan')
    parser.add_argument('-t0f', '--time_zeros_file',
                        help='filename for time zeros of each tscan')
    parser.add_argument('--tau', type=float, nargs='*',
                        help='lifetime of each decay component [mode: decay, both]')
    parser.add_argument('--tau_osc', type=float, nargs='+',
                        help='lifetime of each damped oscillation component [mode: osc, both]')
    parser.add_argument('--period_osc', type=float, nargs='+',
                        help='period of the vibration of each damped oscillation component [mode: osc, both]')
    parser.add_argument('--no_base', action='store_false',
                        help='exclude baseline for fitting [mode: decay, both]')
    parser.add_argument('--fix_irf', action='store_true',
    help='fix irf parameter (fwhm_G, fwhm_L) during fitting process')
    parser.add_argument('--fix_t0', action='store_true',
    help='fix time zero parameter during fitting process.')
    parser.add_argument('--do_glb', action='store_true',
    help=do_glb_help)
    parser.add_argument('-o', '--outdir', default='out',
                        help='name of directory to store output files')
    parser.add_argument('--save_fig', action='store_true',
    help='save plot instead of display')
    args = parser.parse_args()

    prefix = np.array(args.prefix, dtype=str)
    num_file = np.array(args.num_file, dtype=int)

    irf = args.irf
    if irf == 'g':
        if args.fwhm_G is None:
            raise Exception('You are using gaussian irf, so you should set fwhm_G!\n')
        else:
            fwhm_init = args.fwhm_G
    elif irf == 'c':
        if args.fwhm_L is None:
            raise Exception('You are using cauchy/lorenzian irf,' +
            'so you should set fwhm_L!\n')
        else:
            fwhm_init = args.fwhm_L
    else:
        if (args.fwhm_G is None) or (args.fwhm_L is None):
            raise Exception('You are using pseudo voigt irf,' +
            'so you should set both fwhm_G and fwhm_L!\n')
        else:
            fwhm_init = np.array([args.fwhm_G, args.fwhm_L])

    if (args.time_zeros is None) and (args.time_zeros_file is None):
        raise Exception('You should set either time_zeros or time_zeros_file!\n')

    elif args.time_zeros is None:
        t0_init = np.genfromtxt(args.time_zeros_file)
    else:
        t0_init = np.array(args.time_zeros)

    t = np.empty(prefix.size, dtype=object)
    intensity = np.empty(prefix.size, dtype=object)
    eps = np.empty(prefix.size, dtype=object)
    num_scan = np.sum(num_file)

    if num_scan != t0_init.size:
        raise Exception('Number of initial time zero parameter should be same as num_file parameter')

    for i in range(prefix.size):
        t[i] = np.genfromtxt(f'{prefix[i]}_1.txt')[:, 0]
        num_data_pts = t[i].size
        intensity[i], eps[i] = read_data(prefix[i], num_file[i], num_data_pts, 10)

    print(f'fitting with total {num_scan} data set!\n')

    bound_fwhm = None
    if args.fix_irf:
        if irf in ['g', 'c']:
            bound_fwhm = [(fwhm_init, fwhm_init)]
        else:
            bound_fwhm = [(fwhm_init[0], fwhm_init[0]), (fwhm_init[1], fwhm_init[1])]
    
    bound_t0 = None
    if args.fix_t0:
        bound_t0 = t0_init.size*[None]
        for i in range(t0_init.size):
            bound_t0[i] = (t0_init[i], t0_init[i])
    dargs = []
    base = False
    if args.mode in ['decay', 'both']:
        if args.tau is None:
            base = True
            tau_init = None
        else:
            tau_init = np.array(args.tau)
            base = args.no_base
        dargs.append(tau_init)
        if args.mode == 'decay':
            dargs.append(base)
    if args.mode in ['osc', 'both']:
        tau_osc_init = np.array(args.tau_osc)
        period_osc_init = np.array(args.period_osc)
        dargs.append(tau_osc_init)
        dargs.append(period_osc_init)
    
    if args.mode == 'both':
        dargs.append(base)

    result = FITDRIVER[args.mode](irf, fwhm_init, t0_init, *dargs, do_glb=args.do_glb, 
    bound_fwhm=bound_fwhm, bound_t0=bound_t0, name_of_dset=prefix, t=t, intensity=intensity, eps=eps)

    save_TransientResult(result, args.outdir)
    save_TransientResult_txt(result, args.outdir)
    print(result)
    if args.save_fig:
        plot_TransientResult(result, args.outdir)
    else:
        plot_TransientResult(result)

    return
