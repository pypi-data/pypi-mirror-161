#-*-encoding:utf-8-*-

"""
Read The _config.json file.
"""

import json
import hashlib

MODULE_VERSION="0.0.0"
PATH=__file__[:-18]

__FILE=open(PATH+"resources\\_config.json","rb")
__STRC__=json.loads(__FILE.read())
#print(__STRC__)

DISABLEOUT=__STRC__["DISABLE_OUTPUT"]
INSTRUMENT_LIST=__STRC__["DEFAULT_INSTRUMENTS"]
__FILE.close()
