#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 14:46:48 2023

@author: thoverga
"""

import xarray as xr
import numpy as np
import rioxarray
from datetime import datetime
import os
import json
import rasterio



json_file_path = '/home/thoverga/Documents/github/PyFa/FAdata.json'



def json_to_rioxarray(json_path, reproject=True, target_epsg="EPSG:4326"):
    
    print('reproject: ', reproject)
    print('epsg: ', target_epsg)
    # =============================================================================
    #  Read json file
    # =============================================================================
    
    # Opening JSON file
    f = open(json_path)
    data = json.load(f)
    
    
    # =============================================================================
    # Data to xarray
    # =============================================================================
    
    # dt_fmt = '%Y-%m-%d %H:%M:%S'
    # fieldname = data['name'][0].rstrip()
    # validdate = datetime.strptime(data['validate'][0], dt_fmt)
    
    
    
    data_xr = xr.DataArray(np.asarray(data['data']).transpose(), 
                        coords={'x': np.asarray(data['xcoords']),
                                'y': np.asarray(data['ycoords']),
                                }, 
                        dims=["y", "x"])
    
    
    # =============================================================================
    # add metadata
    # =============================================================================
    meta_dict = {key:val[0] for key, val in data.items() if key in ['name', 'basedate', 'validate', 'leadtime', 'timestep', 'origin']}
    data_xr.attrs.update(meta_dict)
    
    
    # =============================================================================
    # add projection info
    # =============================================================================
    
    proj_dict = {key:val[0] for key, val in data.items() if key in ['projection', 'lon_0', 'lat_1', 'lat_2', 'proj_R', 'nx', 'ny', 'dx', 'dy', 'ex', 'ey']}
    
    
    proj4str = f'+proj={proj_dict["projection"]} +lat_1={proj_dict["lat_1"]} +lat_2={proj_dict["lat_2"]} ' + \
        f'+lon_0={proj_dict["lon_0"]} +R={proj_dict["proj_R"]}'
    
    data_xr = data_xr.rio.write_crs(proj4str)
    
    
    # =============================================================================
    # Reproject to latlon
    # =============================================================================
    if reproject:
        data_xr = data_xr.rio.reproject(target_epsg)
    
    # remove no data
    data_xr = data_xr.where(data_xr != data_xr.rio.nodata)
    
    return data_xr



#%%


