"""M2M Daemons

M2M Daemons

Note:

    This project is in beta stage.

Viewing documentation using IPython
-----------------------------------
To see which functions are available in `m2m`, type ``m2m.<TAB>`` (where
``<TAB>`` refers to the TAB key), or use ``m2m.*get_version*?<ENTER>`` (where
``<ENTER>`` refers to the ENTER key) to narrow down the list.  To view the
docstring for a function, use ``m2m.get_version?<ENTER>`` (to view the
docstring) and ``m2m.get_version??<ENTER>`` (to view the source code).
"""

import m2m.config
import m2m.path
import m2m.mqtt2influx
#import m2m.meteofrance2mqtt

# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# Generic release markers:
# X.Y
# X.Y.Z # For bugfix releases  
# 
# Admissible pre-release markers:
# X.YaN # Alpha release
# X.YbN # Beta release         
# X.YrcN # Release Candidate   
# X.Y # Final release
#
# Dev branch marker is: 'X.Y.dev' or 'X.Y.devN' where N is an integer.
# 'X.Y.dev0' is the canonical version of 'X.Y.dev'
#
__version__ = '0.3.dev8'

def get_version():
    return __version__

__all__ = ['TODO']
