# coding: utf-8
# instruwav - Python instrumental library
# Copyright (C) 2000-2001  Gino Zhang
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Gino Zhang
# gino_redlight@163.com

from instruwav.Core import __config__
from instruwav.Core import Exceptions

import sys
import re

ANCHOR_INDICATOR = " anchor"
ANCHOR_NOTE_REGEX = re.compile(r"\s[abcdefg]$")
DESCRIPTOR_32BIT = "FLOAT"
BITS_32BIT = 32
AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED = 0
SOUND_FADE_MILLISECONDS = 50
CYAN = (0, 255, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

AUDIO_ASSET_PREFIX = "audio_files/"
KEYBOARD_ASSET_PREFIX = "keyboards/"
BLACK_INDICES_C_SCALE = [1, 3, 6, 8, 10]
LETTER_KEYS_TO_INDEX = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}

VERSION_INFO=float(sys.version[:3])

if VERSION_INFO>3.0:
    if not __config__.DISABLEOUT:
        print(f"Thank you for using instruwav {__config__.MODULE_VERSION}. Email: gino_redlight@163.com")
else:
    raise Exceptions.VersionError("Version does not support instruwav")

try:
    import instrusound
    import instruwav.instrusound
except ModuleNotFoundError:
    raise Exceptions.LostModuleError("Module not found")
    
