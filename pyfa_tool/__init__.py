#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 17:20:08 2023

@author: thoverga
"""



__version__ = "0.0.2c"

#Important paths
from pathlib import Path
package_path=str(Path(__file__).parent.resolve())


#Demo path
import os
demo_fa_climate = os.path.join(str(Path(package_path).parent.resolve()),
                               'tests', 'data', 'ICMSHABOF+0732')
demo_fa_nwp_1 = os.path.join(str(Path(package_path).parent.resolve()),
                               'tests', 'data', 'PFAR07csm07+0002')
demo_fa_nwp_2 = os.path.join(str(Path(package_path).parent.resolve()),
                               'tests', 'data', 'PFAR07csm07+0003')



#User accesable classes
from pyfa_tool.file import FaFile
from pyfa_tool.dataset import FaDataset
from pyfa_tool.collection import FaCollection



#User accesable functions
def setup_shell_command():
    """
    When calling this function, the CLI PyFa is activated on your system.

    Returns
    -------
    None.

    Note
    -------
    Only support for UNIX and writing right on the .bashrc.

    """
    from pyfa_tool.modules import setup_shell_commands
