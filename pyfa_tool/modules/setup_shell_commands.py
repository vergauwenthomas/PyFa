#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:07:00 2023

@author: thoverga
"""

import os
from pathlib import Path

executor_directory = Path(__file__).resolve().parents[1]
executor_file = os.path.join(executor_directory, 'bash_executor.sh')

# Append to Bashrc
file = os.path.join(os.getenv('HOME'), '.bashrc')

# Only append if not yet appended
if "# <<<  PyFa  >>>" in open(file, "r").read():
    print('It seems that PyFa is already in you .bashrc')
else:
    file1 = open(file, "a")  # append mode
    file1.write("\n")
    file1.write("\n")
    file1.write("# <<<  PyFa  >>> \n")
    file1.write(f'PYFA_BASH="{executor_file}"\n')
    file1.write('alias pyfa="source ${PYFA_BASH} "$@""')
    file1.close()

    print('Done! pyfa is now a shell command.')
    print('Try it out: pyfa -h')
