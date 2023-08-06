# fit static
# fitting static spectrum

import os
from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from ..driver import StaticResult, save_StaticResult
from ..driver import fit_static_voigt, fit_static_thy


def save_StaticResult_txt(result: StaticResult, dirname: str):
      '''
      save static fitting result to the text file

      Args:
       result: static fitting result
       dirname: name of the directory in which text files for fitting result are saved.
       e: energy range of static spectrum
       eps: estimated error of static spectrum
      
      Returns:
       `fit_summary.txt`: Summary for the fitting result
       `weight.txt`: Weight of each voigt and edge component
       `fit.txt`: fitting, each voigt, edge and baseline curve for static spectrum
       `res.txt`: residual (fit-data) curve for static spectrum

      Note:
       If `dirname` directory is not exists, it creates `dirname` directory.
      '''
      if not (Path.cwd()/dirname).exists():
            os.mkdir(dirname)
      
      with open(f'{dirname}/fit_summary.txt', 'w') as f:
            f.write(str(result))

      tot_comp = result['n_voigt']
      if result['edge'] is not None:
            tot_comp = tot_comp+1
      if result['base_order'] is not None:
            tot_comp = tot_comp+1
      coeff_fmt = ['%.8e']
      fit_fmt = (2+tot_comp)*['%.8e']
      fit_header_lst = ['energy', 'fit']
      for i in range(result['n_voigt']):
            fit_header_lst.append(f'voigt_{i}')
      if result['edge'] is not None:
            fit_header_lst.append(f"{result['edge']}_type_edge")
      if result['base'] is not None:
            fit_header_lst.append("base")
            fit_save = np.vstack((result['e'], result['fit'], result['fit_comp'], result['base'])).T
      else:
            fit_save = np.vstack((result['e'], result['fit'], result['fit_comp'])).T
      res_save = np.vstack((result['e'], result['res'], result['eps'])).T
      np.savetxt(f'{dirname}/res.txt', res_save, fmt=['%.8e', '%.8e', '%.8e'], 
      header=f'energy \t res \t eps')
      fit_header = '\t'.join(fit_header_lst)
      coeff_header = 'static'

      np.savetxt(f'{dirname}/weight.txt', result['c'], fmt=coeff_fmt, header=coeff_header)
      np.savetxt(f'{dirname}/fit.txt', fit_save, fmt=fit_fmt, header=fit_header)
      
      return

def plot_StaticResult(result: StaticResult):
      '''
      plot static fitting Result

      Args:
       result: static fitting result
       name_of_dset: name of each dataset
       x_min: minimum x range
       x_max: maximum x range
       save_fig: prefix of saved png plots. If `save_fig` is `None`, plots are displayed istead of being saved.
       e: scan range of data
       data: static spectrum (it should not contain energy scan range)
       eps: estimated errors of static spectrum
      '''
      
      fig = plt.figure(0)
      title = 'Static Spectrum'
      subtitle = f"Chi squared: {result['red_chi2']: .2f}"
      plt.suptitle(title)
      sub1 = fig.add_subplot(211)
      sub1.set_title(subtitle)
      sub1.errorbar(result['e'], result['intensity'], result['eps'], 
      marker='o', mfc='none', label=f'expt {title}', linestyle='none')
      sub1.plot(result['e'], result['fit'], label=f'fit {title}')
      for i in range(result['n_voigt']):
            sub1.plot(result['e'], result['fit_comp'][i, :], label=f'{i+1}th voigt component', linestyle='dashed')
      if result['edge'] is not None:
            sub1.plot(result['e'], result['fit_comp'][-1, :], label=f"{result['edge']} type edge", linestyle='dashed')
      if result['base_order'] is not None:
        sub1.plot(result['e'], result['base'], label=f"base [order {result['base_order']}]", linestyle='dashed')
      sub1.legend()
      sub2 = fig.add_subplot(212)
      sub2.errorbar(result['e'], result['res'], result['eps'], 
      marker='o', mfc='none', label=f'res {title}', linestyle='none')
      sub2.legend()
      plt.show()
      return

description = '''
fit static: fitting static spectrum with 
 'voigt': some of voigt component
  'thy' : theoretically calculated line spectrum broadened by voigt function
It also include edge and polynomial type baseline feature.
'''

epilog = ''' 
*Note
 If fwhm_G of voigt component is zero then this voigt component is treated as lorenzian
 If fwhm_L of voigt component is zero then this voigt component is treated as gaussian
'''

do_glb_help='''
Whether or not use Global optimization Method.
When do_glb option is set then `basinhopping` global optimization algorithm will be used.
'''

edge_help = '''
Type of edge function if not set, edge is not included.
 'g': gaussian type edge function
 'l': lorenzian type edge function
'''

mode_help = '''
Mode of static spectrum fitting
 'voigt': fitting with sum of voigt componenty
 'thy': fitting with voigt broadend thoretical spectrum
'''

policy_help = '''
Policy to match discrepency between experimental data and theoretical spectrum.
 'shift': constant shift peak position
 'scale': constant scale peak position
 'both': shift and scale peak position
'''


def fit_static():

    tmp = argparse.RawDescriptionHelpFormatter
    parse = argparse.ArgumentParser(formatter_class=tmp,
                                    description=description,
                                    epilog=epilog)
    parse.add_argument('filename', help='filename for experimental spectrum')
    parse.add_argument('--mode', type=str, choices=['voigt', 'thy'],
    help = mode_help)
    parse.add_argument('--e0_voigt', type=float, nargs='*',
    help='peak position of each voigt component')
    parse.add_argument('--fwhm_G_voigt', type=float, nargs='*',
                        help='full width at half maximum for gaussian shape ' +
                        'It would be not used when you set lorenzian line shape')
    parse.add_argument('--fwhm_L_voigt', type=float, nargs='*',
                        help='full width at half maximum for lorenzian shape ' +
                        'It would be not used when you use gaussian line shape')
    parse.add_argument('--thy_file', type=str, help='filename which stores thoretical peak position and intensity.')
    parse.add_argument('--fwhm_G_thy', type=float, default=0, help='gaussian part of uniform' +
    ' broadening parameter for theoretical line shape spectrum')
    parse.add_argument('--fwhm_L_thy', type=float, default=0, help='lorenzian part of uniform' +
    ' broadening parameter for theoretical line shape spectrum')
    parse.add_argument('--policy', choices=['shift', 'scale', 'both'], help=policy_help)
    parse.add_argument('--peak_scale', type=float, help='inital peak position scale parameter')
    parse.add_argument('--peak_shift', type=float, help='inital peak position shift parameter')
    parse.add_argument('--edge', type=str, choices=['g', 'l'],
    help=edge_help)
    parse.add_argument('--e0_edge', type=float,
    help='edge position')
    parse.add_argument('--fwhm_edge', type=float,
    help='full width at half maximum parameter of edge')
    parse.add_argument('--base_order', type=int,
    help ='Order of polynomial to correct baseline feature. If it is not set then baseline is not corrected')
    parse.add_argument('-o', '--outdir', default='out', help='directory to store output file')
    parse.add_argument('--do_glb', action='store_true', help=do_glb_help)

    args = parse.parse_args()

    filename = args.filename
    if args.mode == 'voigt' and args.e0_voigt is None:
        e0_init = None
        fwhm_G_init = None
        fwhm_L_init = None
    elif args.mode == 'voigt' and args.e0_voigt is not None:
        e0_init = np.array(args.e0_voigt)
        if args.fwhm_G_voigt is None:
            fwhm_G_init = np.zeros_like(e0_init)
        else:
            fwhm_G_init = np.array(args.fwhm_G_voigt)
        if args.fwhm_L_voigt is None:
            fwhm_L_init = np.zeros_like(e0_init)
        else:
            fwhm_L_init = np.array(args.fwhm_L_voigt)
        if args.fwhm_G_voigt is None and args.fwhm_L_voigt is None:
            raise Exception("Please set both initial fwhm_G and fwhm_L for each voigt component")
        if fwhm_G_init.size != fwhm_L_init.size:
            raise Exception("The number of initial fwhm_G and fwhm_L parameter should be same")
    elif args.mode == 'thy':
        fwhm_G_init = args.fwhm_G_thy
        fwhm_L_init = args.fwhm_L_thy
        thy_peak = np.genfromtxt(args.thy_file)[:,:2]
        if args.policy is None:
            raise Exception("Please set policy to solve descrepency between theoretical and experimental spectrum.")
        if args.policy in ['shift', 'both'] and args.peak_shift is None:
            raise Exception(f"Your policy is {args.policy}, please set initial peak_shift parameter.")
        if args.policy in ['scale', 'both'] and args.peak_scale is None:
            raise Exception(f"Your policy is {args.policy}, please set peak_scale parameter.")   
    
    edge = args.edge
    e0_edge_init = args.e0_edge
    fwhm_edge_init = args.fwhm_edge
    base_order = args.base_order
    outdir = args.outdir

    tmp = np.genfromtxt(filename)
    e = tmp[:, 0]
    intensity = tmp[:, 1]
    if tmp.shape[1] == 2:
        eps = np.max(np.abs(intensity))/1000*np.ones_like(e)
    else:
        eps = tmp[:, 2]
    
    if args.mode == 'voigt':
        result = fit_static_voigt(e0_init, fwhm_G_init, fwhm_L_init, edge, e0_edge_init, fwhm_edge_init,
        base_order, args.do_glb, e=e, intensity=intensity, eps=eps)
    
    elif args.mode == 'thy':
        result = fit_static_thy(thy_peak, fwhm_G_init, fwhm_L_init, args.policy, args.peak_shift, args.peak_scale,
        edge, e0_edge_init, fwhm_edge_init,
        base_order, args.do_glb, e=e, intensity=intensity, eps=eps)

    save_StaticResult_txt(result, outdir)
    save_StaticResult(result, outdir)
    print(result)
    plot_StaticResult(result)

    return
