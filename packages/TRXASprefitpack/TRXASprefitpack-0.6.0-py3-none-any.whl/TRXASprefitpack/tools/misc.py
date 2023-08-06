# misc
# submodule for miscellaneous function of
# tools subpackage

from typing import Tuple
import numpy as np

def read_data(prefix: str, num_scan: int, num_data_pts: int, default_SN: float) -> Tuple[np.ndarray, np.ndarray]:
    '''
    Read data from prefix_i.txt (1 <= i <= num_scan)

    Args:
     prefix: prefix of scan_file
     num_scan: the number of scan file to read
     num_data_pts: the number of data points per each scan file
     default_SN: Default Signal/Noise
    
    Return:
     Tuple of data of eps
    '''
    data = np.zeros((num_data_pts, num_scan))
    eps = np.zeros((num_data_pts, num_scan))

    for i in range(num_scan):
        A = np.genfromtxt(f'{prefix}_{i+1}.txt')
        data[:, i] = A[:, 1]
        if A.shape[1] == 2:
            eps[:, i] = np.max(np.abs(data[:, i]))*np.ones(num_data_pts)/default_SN
        else:
            eps[:, i] = A[:, 2]
    return data, eps

def parse_matrix(mat_str: np.ndarray, tau_rate: np.ndarray) -> np.ndarray:
    '''
    Parse user supplied rate equation matrix

    Args:
     mat_str: user supplied rate equation (lower triangular matrix)
     tau_rate: time constants for rate equation parameter (1/ki)
    
    Return:
     parsed rate equation matrix.
     the value of lifetime 
     parameters (1/ki) used to define rate equation matrix
    
    Note:
     Every entry in the rate equation matrix should be
     '0', '1*ki', '-x.xxx*ki', 'x.xxx*ki' or '-(x.xxx*ki+y.yyy*kj+...)'
     Number of non zero diagonal elements and size of tau should be same
     Number of parameter used to define rate equation and size of tau should 
     be same.
    '''

    L = np.zeros_like(mat_str, dtype=float)
    mask = (mat_str != '0')
    red_mat_str = mat_str[mask]
    red_L = np.zeros_like(red_mat_str, dtype=float)

    for i in range(red_mat_str.size):
        tmp = red_mat_str[i]
        if '-' in tmp:
            tmp = tmp.strip('-')
            tmp = tmp.strip('('); tmp = tmp.strip(')')
            k_lst = tmp.split('+')
            for k in k_lst:
                k_pair = k.split('*')
                red_L[i] = red_L[i] - float(k_pair[0])/tau_rate[int(k_pair[1][1:])-1]
        else:
            tmp_pair = tmp.split('*')
            red_L[i] = float(tmp_pair[0])/tau_rate[int(tmp_pair[1][1:])-1]
    
    L[mask] = red_L
    
    return L