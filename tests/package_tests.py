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
fielddf = pyfa.get_fieldnames(climate_fa)
assert fielddf.shape[0] == 410, f'The climate FA fields are not extracted correctly'
assert len(fielddf.columns) > 1, 'only one fieldcolumn is extracted for climate FA'



fielddf = pyfa.get_fieldnames(nwp_fa)
assert fielddf.shape[0] == 1375, 'The climate FA fields are not extracted correctly'
assert len(fielddf.columns) > 1, 'only one fieldcolumn is extracted for climate FA'



# =============================================================================
# 2D fields
# =============================================================================


# --------------- 2D fields --------------------

print('Extracting 2D fields')
data = pyfa.get_2d_field(fa_filepath=climate_fa,
                         fieldname='SURFTEMPERATURE',
                         target_crs='EPSG:4326')
assert int(data.max(skipna=True)) == 313, 'Error in climate FA 2D import in to xarray'


nwpdata = pyfa.get_2d_field(fa_filepath=nwp_fa,
                            fieldname='S004WIND.U.PHYS',
                            target_crs='EPSG:4326')
assert int(nwpdata.max(skipna=True)) == 15, 'Error in NWP FA 2D import in to xarray'


# =============================================================================
# saving to netCDF
# =============================================================================
print("Saving to nc test")

savefolder=os.path.join(rootfolder,'tests', 'data')
savefile='dummy'


pyfa.save_as_nc(xrdata=data,
                outputfolder=savefolder,
                filename=savefile)

# test if file is created
filepath = os.path.join(savefolder, savefile+'.nc')
if not os.path.isfile(filepath):
    sys.exit('Data not saved as nc.')

os.remove(filepath)



# =============================================================================
# 3D fields
# =============================================================================
print("Extracting 3D fields")


d3_data = pyfa.get_3d_field(fa_filepath=climate_fa,
                            fieldname='WIND.U.PHYS',
                            target_crs='EPSG:4326')
assert d3_data.dims == ('level', 'y', 'x'), 'Error in climate FA 3D import in to xarray'

assert int(d3_data.sel(level=12).max(skipna=True)) == 44, 'Error in the climate 3D import'


d3_data_bis = pyfa.get_3d_field(fa_filepath=climate_fa,
                            fieldname='S013wind.U.Phys',
                            target_crs='EPSG:4326')

assert d3_data_bis.dims == ('level', 'y', 'x'), 'Error in climate FA 3D import in to xarray (probably name formatiting)'

assert int(d3_data_bis.sel(level=12).max(skipna=True)) == 44, 'Error in the climate 3D import (probably name formatiting)'



print('DONE !! ')
