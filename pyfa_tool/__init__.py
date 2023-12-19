#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 17:20:08 2023

@author: thoverga
"""

# from .lib_functions import setup_shell_command, FA_to_Xarray, get_fields


__version__ = "0.0.2a"



from .lib_functions import setup_shell_command


from .lib_functions import (get_fieldnames, field_exists, describe_fa,
                            get_2d_field, get_3d_field,
                           )

from .modules.to_xarray import save_as_nc