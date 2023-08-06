# calc_dads.py
# Wrapper script for calc_dads()
# Date: 2022. 7. 25.
# Author: pistack
# Email: pistack@yonsei.ac.kr

import os
import sys

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path+"/../src/")

from TRXASprefitpack.tools._calc_dads import calc_dads

if __name__ == "__main__":
    calc_dads()
