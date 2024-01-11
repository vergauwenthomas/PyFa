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
assert data.ds[fieldname].dims == ('level', 'y', 'x'), 'dimension order not correct'
assert data._get_physical_variables() == [fieldname], 'Something wrong with data variables'
assert int(data.ds[fieldname].min()) == -11, 'Something wrong with data values'


# =============================================================================
# Test whitelist/blacklist multi import (NWP file)
# =============================================================================
print('General data import test NWP')
data = pyfa.FaDataset()
data.set_fafile(nwp_fa)
whitelist = ['WIND.U.PHYS', 'CLSTEMPERATURE', 'fakename', "SURFACCPLUIE"]

blacklist = ['WIND.U.PHYS', 'fakename2']

data.import_fa(
               whitelist=whitelist,
               blacklist=blacklist,
               reproj=False)


assert data._get_physical_variables() == ['CLSTEMPERATURE', 'SURFACCPLUIE'], 'Something wrong with data variables'
assert list(data.ds.dims) == ['y', 'x', 'level'], 'something wrong with dimensions'
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
assert list(data.ds.dims) == ['y', 'x', 'level'], 'something wrong with dimensions after reproj'
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
assert data2._get_physical_variables() == ['CLSTEMPERATURE', 'SURFACCPLUIE'], '(read netCDF) Something wrong with data variables'
assert list(data2.ds.dims) == ['y', 'x', 'level'], '(read netCDF) something wrong with dimensions'



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
assert data.ds[fieldname].dims == ('y', 'x'), 'dimension order not correct'

# =============================================================================
# Test 3D import (climate file)
# =============================================================================
print('3D field import test climate')
data = pyfa.FaDataset()
data.set_fafile(climate_fa)
fieldname = 'WIND.U.PHYS'

data.import_3d_field(fieldname=fieldname,
                     reproj=False)
assert data.ds[fieldname].dims == ('level', 'y', 'x'), 'dimension order not correct'
assert data._get_physical_variables() == [fieldname], 'Something wrong with data variables'
assert int(data.ds[fieldname].min()) == -35, 'Something wrong with data values'


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
assert list(data.ds.dims) == ['y', 'x', 'level'], 'something wrong with dimensions'
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
assert list(data.ds.dims) == ['y', 'x', 'level'], 'something wrong with dimensions after reproj'
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
assert set(data._get_physical_variables()) == set(['CLSTEMPERATURE', "SURFAEROS.LAND"]), 'Something wrong with data variables'
assert list(data2.ds.dims) == ['y', 'x', 'level'], '(read netCDF) something wrong with dimensions'




print('DONE !! ')
