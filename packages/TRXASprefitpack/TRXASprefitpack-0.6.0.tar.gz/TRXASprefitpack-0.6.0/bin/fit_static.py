# fit static py
# Wrapper script for fit_static()
# Date: 2022. 7. 25.
# Author: pistack
# Email: pistack@yonsei.ac.kr

import os
import sys

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path+"/../src/")

from TRXASprefitpack.tools._fit_static import fit_static

if __name__ == "__main__":
    fit_static()

