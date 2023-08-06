# Copyright (C) DAPCOM Data Services S.L. - http://www.dapcom.es
# Contact: fapec@dapcom.es
#
# This wrapper has been prepared by DAPCOM
# for potential customers willing to use FAPEC in
# their Python code.
# It can be freely distributed and modified as needed,
# but this notice must be kept.
# Commercial use is only permitted if an adequate FAPEC
# license is acquired.
#

import sys

if sys.platform == "win32":
    import os
    lib_path = os.path.join(os.path.dirname(__file__), "lib")
    os.add_dll_directory(lib_path)

from ._fapyc import *
