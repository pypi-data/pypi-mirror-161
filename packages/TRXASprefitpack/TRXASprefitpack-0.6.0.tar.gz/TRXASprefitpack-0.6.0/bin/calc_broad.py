# calc_broad py
# Wrapper script for calc_broad()
# Date: 2022. 7. 25.
# Author: pistack
# Email: pistatex@yonsei.ac.kr

import os
import sys

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path+"/../src/")

from TRXASprefitpack.tools._calc_broad import calc_broad

if __name__ == "__main__":
    calc_broad()
