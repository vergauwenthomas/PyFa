#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 09:16:18 2023

@author: thoverga
"""


import sys, os
from pathlib import Path


rootfolder = Path(__file__).parents[1].resolve()


climate_fa=os.path.join(rootfolder,'tests', 'data', 'ICMSHABOF+0732')
nwp_fa =os.path.join(rootfolder, 'tests', 'data', 'ICMSHAR13+0014')

sys.path.insert(0, rootfolder)

import pyfa_tool as pyfa
#%%
# =============================================================================
# Setup shell commands
# =============================================================================
print('Running setup shell command in python')
pyfa.setup_shell_command()
print('Done')


# =============================================================================
# Get fieldnames
# =============================================================================
print('Running get_fieldnames in python')
fielddf = pyfa.get_fields(climate_fa)
assert fielddf.shape[0] == 410, f'The climate FA fields are not extracted correctly'
assert len(fielddf.columns) > 1, 'only one fieldcolumn is extracted for climate FA'



fielddf = pyfa.get_fields(nwp_fa)
assert fielddf.shape[0] == 1375, 'The climate FA fields are not extracted correctly'
assert len(fielddf.columns) > 1, 'only one fieldcolumn is extracted for climate FA'



# =============================================================================
# Convert to xarray
# =============================================================================


print('Running FA_to_Xarray in python')
data = pyfa.FA_to_Xarray(fa_filepath=climate_fa,
                  fieldname='SURFTEMPERATURE',
                  target_crs='EPSG:4326')
assert int(data.max(skipna=True)) == 313, 'Error in climate FA import in to xarray'


nwpdata = pyfa.FA_to_Xarray(fa_filepath=nwp_fa,
                  fieldname='S004WIND.U.PHYS',
                  target_crs='EPSG:4326')
assert int(nwpdata.max(skipna=True)) == 15, 'Error in NWP FA import in to xarray'



print('TEST COMPLETED!')