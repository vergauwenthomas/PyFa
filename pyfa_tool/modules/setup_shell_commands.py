#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:07:00 2023

@author: thoverga
"""

import os

main_path = os.path.dirname(__file__)
executor_file = os.path.join(main_path, 'bash_executor.sh')


# Append to Bashrc
file = os.path.join(os.getenv('HOME'), '.bashrc')
file1 = open(file, "a")  # append mode


file1.write("\n")
file1.write("\n")
file1.write("# <<<  PyFa  >>> \n")
file1.write(f'PYFY_BASH="{executor_file}"\n')
file1.write('alias pyfa="source ${PYFY_BASH} "$@""')
file1.close()

print('Done! pyfy is now a shell command.')
print('Try it out: pyfa -h')