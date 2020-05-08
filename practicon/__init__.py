# __init__.py - initialization for practicon question checkin
#
# Author: M. M. (Rene) van Paassen
# Date: 8 May 2020
#
# This file contains the initialization of the practicon control theory/
# calculation checking package
#
# Copyright (c) 2020 Delft University of Technology
# All rights reserved.
#
from .check_numeric import CheckNumeric
from .check_transferfunction import CheckTransferFunction
try:
    from ._version import __version__, __commit__
except ImportError:
    __version__ = "dev"

