# -*- coding: utf-8 -*-
from __future__ import print_function
#from ._version import get_versions

__author__ = 'Mike Hagerty'
__email__ = 'mhagerty@isti.com'
__version__ = '0.0.2'
#__version__ = get_versions()['version']
#del get_versions

import os
def installation_dir():
  return os.path.dirname(os.path.realpath(__file__))

from .iris_validate import stationxml_validator
