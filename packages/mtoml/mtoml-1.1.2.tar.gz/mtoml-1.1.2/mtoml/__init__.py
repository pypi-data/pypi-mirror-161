#######################################################################
# Copyright (c) 2022 Jordan Schaffrin                                 #
#                                                                     #
# This Source Code Form is subject to the terms of the Mozilla Public #
# License, v. 2.0. If a copy of the MPL was not distributed with this #
# file, You can obtain one at http://mozilla.org/MPL/2.0/.            #
#######################################################################

__all__ = (r'set', r'get', r'save_all', r'save', r'is_loaded', r'load', r'set_dir', r'get_dir', r'mtomlc')

from .mtoml import (mtomlc, get_dir, set_dir, load, is_loaded, save, save_all, get, set)