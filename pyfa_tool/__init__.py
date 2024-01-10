#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 17:20:08 2023

@author: thoverga
"""



__version__ = "0.0.2a"


from pathlib import Path
package_path=str(Path(__file__).parent.resolve())


from pyfa_tool.dataset import FaDataset, FaFile


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