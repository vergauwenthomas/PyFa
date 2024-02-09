#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 09:16:18 2023

@author: thoverga
"""


import sys, os
import numpy as np
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
# Test the FaFile class functionality
# =============================================================================

Fa=pyfa.FaFile(nwp_fa)
# Test all methods
df = Fa.get_fieldnames()

assert df.shape[0] == 1375, 'The climate FA fields are not extracted correctly'
assert len(df.columns) > 1, 'only one fieldcolumn is extracted for climate FA'

metadata = Fa.get_metadata()
assert bool(metadata), 'metadata is empty'

# describe
Fa.describe()

# sepecial
print(Fa)



Fa=pyfa.FaFile(climate_fa)
# Test all methods
df = Fa.get_fieldnames()

assert df.shape[0] == 410, f'The climate FA fields are not extracted correctly'
assert len(df.columns) > 1, 'only one fieldcolumn is extracted for climate FA'

metadata = Fa.get_metadata()
assert bool(metadata), 'metadata is empty'

# describe
Fa.describe()

# sepecial
print(Fa)



#%%
# =============================================================================
# Test 2D import (NWP file)
# =============================================================================
print('2D field import test NWP')
data = pyfa.FaDataset()
data.set_fafile(nwp_fa)
fieldname = 'CLSVENT.ZONAL'

data.import_2d_field(fieldname=fieldname,
                     reproj=False)


assert set(data.ds.dims) == set(['x','y', 'basedate', 'validate']), 'dimensions not correct'
assert data._get_physical_variables() == [fieldname], 'Something wrong with data variables'
assert int(data.ds[fieldname].min()) == -5, 'Something wrong with data values'
assert data.ds[fieldname].dims == ('y', 'x'), 'dimension order not correct'

# =============================================================================
# Test 3D import (NWP file)
# =============================================================================
print('3D field import test NWP')
data = pyfa.FaDataset()
data.set_fafile(nwp_fa)
fieldname = 'WIND.U.PHYS'

data.import_3d_field(fieldname=fieldname,
                     reproj=False)

assert set(data.ds.dims) == set(['x','y','lvl', 'basedate', 'validate']), 'dimensions not correct'
assert 'lvl' in data.ds.variables, 'lvl not in the coordinates'
assert set(data.ds[fieldname].dims) == set(['lvl', 'y', 'x']), 'dimensions of 3d field not correct'
assert data._get_physical_variables() == [fieldname], 'Something wrong with data variables'
assert int(data.ds[fieldname].min()) == -11, 'Something wrong with data values'



# =============================================================================
# Test whitelist/blacklist multi import (NWP file)
# =============================================================================
print('General data import test NWP')
data = pyfa.FaDataset()
data.set_fafile(nwp_fa)
whitelist = ['WIND.U.PHYS', #test 3d field
             'CLSTEMPERATURE', #test 2d field
             'fakename', # test fake field
             "SURFACCPLUIE", #test multiple fields
             'S001RAYT SOL CL', 'S087RAYT SOL CL', 'S001RAYT THER CL', #test pseudo fields
             "S004WIND.U.PHYS", "S032WIND.U.PHYS", "S018TEMPERATURE", #test specific fields of 3d
             ]

blacklist = ['WIND.U.PHYS', 'fakename2']

data.import_fa(
               whitelist=whitelist,
               blacklist=blacklist,
               reproj=False)


assert set(data._get_physical_variables()) == set(['CLSTEMPERATURE','SURFACCPLUIE','S001RAYT SOL CL','S087RAYT SOL CL','S001RAYT THER CL','S004WIND.U.PHYS','S018TEMPERATURE','S032WIND.U.PHYS']), 'Something wrong with data variables'
assert set(data.ds.dims) == set(['x','y', 'basedate', 'validate']), 'dimensions not correct'


# #Test pseudo fields
# assert 'RAYT THER CL' in data.ds.variables, 'pseudo field not read properly'
# assert 'RAYT SOL CL' in data.ds.variables, 'pseudo field not read properly'
# assert not np.isnan(data.ds['RAYT SOL CL'].sel(level=1).data).any() ,'pseudo field not read properly'
# assert not np.isnan(data.ds['RAYT SOL CL'].sel(level=87).data).any() ,'pseudo field not read properly'
# assert np.isnan(data.ds['RAYT SOL CL'].sel(level=2).data).any() ,'pseudo field not read properly'
# assert np.isnan(data.ds['RAYT THER CL'].sel(level=2).data).any() ,'pseudo field not read properly'
# assert np.isnan(data.ds['RAYT THER CL'].sel(level=87).data).any() ,'pseudo field not read properly'
# assert not np.isnan(data.ds['RAYT THER CL'].sel(level=1).data).any() ,'pseudo field not read properly'

# =============================================================================
# Test converting 2d crossections to 3d fields
# =============================================================================

data.convert_2d_crossections_to_3d_variables()



assert np.isnan(data.ds['WIND.U.PHYS'].sel(lvl=1).data).any() ,'2d field of 3dfield not read properly'
assert not np.isnan(data.ds['WIND.U.PHYS'].sel(lvl=32).data).any() ,'2d field of 3dfield not read properly'
assert not np.isnan(data.ds['WIND.U.PHYS'].sel(lvl=4).data).any() ,'2d field of 3dfield not read properly'
assert np.isnan(data.ds['TEMPERATURE'].sel(lvl=1).data).any() ,'2d field of 3dfield not read properly'
assert not np.isnan(data.ds['TEMPERATURE'].sel(lvl=18).data).any() ,'2d field of 3dfield not read properly'

assert 'RAYT THER CL' in data.ds.variables, 'pseudo field not read properly'
assert 'RAYT SOL CL' in data.ds.variables, 'pseudo field not read properly'
assert not np.isnan(data.ds['RAYT SOL CL'].sel(lvl=1).data).any() ,'pseudo field not read properly'
assert not np.isnan(data.ds['RAYT SOL CL'].sel(lvl=87).data).any() ,'pseudo field not read properly'
assert np.isnan(data.ds['RAYT SOL CL'].sel(lvl=2).data).any() ,'pseudo field not read properly'
assert np.isnan(data.ds['RAYT THER CL'].sel(lvl=2).data).any() ,'pseudo field not read properly'
assert np.isnan(data.ds['RAYT THER CL'].sel(lvl=87).data).any() ,'pseudo field not read properly'
assert not np.isnan(data.ds['RAYT THER CL'].sel(lvl=1).data).any() ,'pseudo field not read properly'




# =============================================================================
# Test describe (NWP file)
# =============================================================================
print("Describe test NWP")
data.describe()

# =============================================================================
# Test reproject (NWP file)
# =============================================================================
print('Reprojection test NWP')

data.reproject(target_epsg='EPSG:4326')

assert int(data.ds.coords['y'].max()) == 54 , 'something wrong with reprojecting'
assert int(data.ds.coords['x'].max()) == 10, ' Something wrong with reprojecting'
assert set(data.ds.dims) == set(['x','y', 'basedate', 'validate', 'lvl']), 'dimensions not correct'
assert 'lon' in data.ds.coords, 'longitude coordinate not created'
assert 'lat' in data.ds.coords, 'latitude coordinate not created'
assert data.ds.attrs['proj4str'].startswith('+proj=longlat'), 'proj4 str not update'


# =============================================================================
# Test plot (NWP file)
# =============================================================================
print("Plot testing NWP")
data.plot(variable='CLSTEMPERATURE',
          level=None,
          title=None,
          grid=True,
          land=True,
          coastline=True,
          contour=True,
          contour_levels=10,
          cmap='viridis')


# =============================================================================
# Test saveing/reading (NWP file)
# =============================================================================
print("Saving to nc test NWP")
savefolder=os.path.join(rootfolder,'tests', 'data')
savefile='dummy'
data.save_nc(outputfolder=savefolder,
             filename='dummy',
             overwrite=True)


data2 = pyfa.FaDataset()
data2.read_nc(file=os.path.join(savefolder, savefile+'.nc'))

assert int(data2.ds.coords['y'].max()) == 54 , '(read netCDF) something wrong with reprojecting '
assert int(data2.ds.coords['x'].max()) == 10, '(read netCDF) Something wrong with reprojecting'
assert set(data2._get_physical_variables()) == set(['CLSTEMPERATURE','SURFACCPLUIE','RAYT SOL CL','WIND.U.PHYS','RAYT THER CL','TEMPERATURE']), 'Something wrong with data variables'
assert set(data2.ds.dims) == set(['x','y', 'basedate', 'validate', 'lvl']), 'dimensions not correct'



#%%
# =============================================================================
# Test 2D import (climate file)
# =============================================================================
print('2D field import test climate')
data = pyfa.FaDataset()
data.set_fafile(climate_fa)
fieldname = 'CLSVENT.ZONAL'

data.import_2d_field(fieldname=fieldname,
                     reproj=False)


assert data._get_physical_variables() == [fieldname], 'Something wrong with data variables'
assert int(data.ds[fieldname].min()) == -21, 'Something wrong with data values'
assert set(data.ds[fieldname].dims) == set(['y', 'x']), 'dimension of 2d field not correct'
assert set(data.ds.dims) == set(['x','y', 'basedate', 'validate']), 'dimensions not correct'

# =============================================================================
# Test 3D import (climate file)
# =============================================================================
print('3D field import test climate')
data = pyfa.FaDataset()
data.set_fafile(climate_fa)
fieldname = 'WIND.U.PHYS'

data.import_3d_field(fieldname=fieldname,
                     reproj=False)
assert set(data.ds[fieldname].dims) == set(['lvl', 'y', 'x']), 'dimension of 3d not correct'
assert data._get_physical_variables() == [fieldname], 'Something wrong with data variables'
assert int(data.ds[fieldname].min()) == -35, 'Something wrong with data values'
assert set(data.ds.dims) == set(['x','y', 'basedate', 'validate', 'lvl']), 'dimensions not correct'

# =============================================================================
# Test whitelist/blacklist multi import (climate file)
# =============================================================================
print('General data import test climate')
data = pyfa.FaDataset()
data.set_fafile(climate_fa)
whitelist = ['WIND.U.PHYS', 'CLSTEMPERATURE', 'fakename', "SURFAEROS.LAND"]

blacklist = ['WIND.U.PHYS', 'fakename2']

data.import_fa(
               whitelist=whitelist,
               blacklist=blacklist,
               reproj=False)


assert set(data._get_physical_variables()) == set(['CLSTEMPERATURE', "SURFAEROS.LAND"]), 'Something wrong with data variables'
assert set(data.ds.dims) == set(['x','y', 'basedate', 'validate']), 'dimensions not correct'
# =============================================================================
# Test describe (climate file)
# =============================================================================
print("Describe test climate")
data.describe()

# =============================================================================
# Test reproject (climate file)
# =============================================================================
print('Reprojection test climate')

data.reproject(target_epsg='EPSG:4326')

assert int(data.ds.coords['y'].max()) == 75 , 'something wrong with reprojecting'
assert int(data.ds.coords['x'].max()) == 79, ' Something wrong with reprojecting'
assert set(data.ds.dims) == set(['x','y', 'basedate', 'validate']), 'dimensions not correct'
# =============================================================================
# Test plot (climate file)
# =============================================================================
print("Plot testing climate")
data.plot(variable='CLSTEMPERATURE',
          level=None,
          title=None,
          grid=True,
          land=True,
          coastline=True,
          contour=True,
          contour_levels=10,
          cmap='viridis')


# =============================================================================
# Test saveing/reading (climate file)
# =============================================================================
print("Saving to nc test climate")
savefolder=os.path.join(rootfolder,'tests', 'data')
savefile='dummy'
data.save_nc(outputfolder=savefolder,
             filename='dummy',
             overwrite=True)


data2 = pyfa.FaDataset()
data2.read_nc(file=os.path.join(savefolder, savefile+'.nc'))

assert int(data2.ds.coords['y'].max()) == 75 , '(read netCDF) something wrong with reprojecting '
assert int(data2.ds.coords['x'].max()) == 79, '(read netCDF) Something wrong with reprojecting'
assert set(data2._get_physical_variables()) == set(['CLSTEMPERATURE', "SURFAEROS.LAND"]), 'Something wrong with data variables'
assert set(data2.ds.dims) == set(['x','y', 'basedate', 'validate']), 'read netCDF dimensions not correct'



print('DONE !! ')
