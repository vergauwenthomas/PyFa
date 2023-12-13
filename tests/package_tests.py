#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 09:16:18 2023

@author: thoverga
"""


import pyfa_tool as pyfa

# =============================================================================
# Setup shell commands
# =============================================================================
print('Running setup shell command in python')
pyfa.setup_shell_command()
print('Done')




# =============================================================================
# FA handling
# =============================================================================
import os

testfolder = os.path.dirname(__file__)
fa_file = os.path.join(testfolder, 'data', 'ICMSHAR13+0014' )


# =============================================================================
# Get fieldnames
# =============================================================================
print('Running get_fieldnames in python')
fielddf = pyfa.get_fields(fa_file)

print('Here the fieldinfo: ', fielddf)


print('Done')


# =============================================================================
# Convert to xarray
# =============================================================================


print('Running FA_to_Xarray in python')
data = pyfa.FA_to_Xarray(fa_filepath=fa_file,
                  fieldname='SURFTEMPERATURE',
                  target_crs='EPSG:4326')

print('Here is the data info: ', data)

print('Done')







print('TEST COMPLETED!')