#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 09:04:32 2024

@author: thoverga
"""


import os
import sys
import xarray as xr
import numpy as np
from datetime import timedelta

import pyfa_tool.modules.IO as IO
from pyfa_tool.modules.describe_module import _str_to_dt
# =============================================================================
# Formatters
# =============================================================================

def _create_proj4_str(metadict):
    proj4str = f'+proj={metadict["projection"][0]} +lat_1={metadict["lat_1"][0]} +lat_2={metadict["lat_2"][0]} ' + \
        f'+lon_0={metadict["lon_0"][0]} +R={metadict["proj_R"][0]}'
    return proj4str

def _fmt_fieldname(string):
    return string.strip()



def _fmt_2d_field_to_matrix(datalist, xcoords):
    xlen = xcoords.shape[0]
    # ylen = ycoords.shape[0]

    ncols=xlen #test 1

    test = np.asarray(datalist)
    test.shape = (test.size//ncols, ncols)
    return test



def _fmt_3d_field_to_matrix(datalist):
    # convert to matrix with these dimensions: (y, x, levels)
    mat =np.asarray(datalist).transpose((1,0,2))
    return mat


def _make_level_dimension(nlev):
    return np.arange(1, nlev+1)

# =============================================================================
#  Json to xarray
# =============================================================================



def json_to_full_dataset(jsonfile):
    print('Reading json data')
    data = IO.read_json(jsonfile)

    metadict = {
        'basedate': _str_to_dt(data['pyfa_metadata']['basedate'][0]),
        'validate': _str_to_dt(data['pyfa_metadata']['validate'][0]),
        'leadtime': timedelta(hours = float(data['pyfa_metadata']['leadtime'][0])),

        'timestep': int(data['pyfa_metadata']['timestep'][0]),
        'origin': str(data['pyfa_metadata']['origin'][0]),

        'projection': _create_proj4_str(data['pyfa_metadata']),
        'nx': int(data['pyfa_metadata']['nx'][0]),
        'ny': int(data['pyfa_metadata']['ny'][0]),
        'dx': int(data['pyfa_metadata']['dx'][0]),
        'dy': int(data['pyfa_metadata']['dy'][0]),
        'ex': int(data['pyfa_metadata']['ex'][0]),
        'ey': int(data['pyfa_metadata']['ey'][0]),
        'center_lon': float(data['pyfa_metadata']['center_lon'][0]),
        'center_lat': float(data['pyfa_metadata']['center_lat'][0]),
        'nfields': int(data['pyfa_metadata']['nfields'][0]),
        'filepath': str(data['pyfa_metadata']['filepath'][0]),
        'ndlux': int(data['pyfa_metadata']['ndlux'][0]),
        'ndgux': int(data['pyfa_metadata']['ndgux'][0]),
        'nsmax': int(data['pyfa_metadata']['nsmax'][0]),
        'nlev': int(data['pyfa_metadata']['nlev'][0]),
        'refpressure': float(data['pyfa_metadata']['refpressure'][0]),
        'A_list': np.array(data['pyfa_metadata']['A_list']),
        'B_list': np.array(data['pyfa_metadata']['A_list']),
        }

    xcoords=np.asarray(data['pyfa_metadata']['xcoords'])
    ycoords=np.asarray(data['pyfa_metadata']['ycoords'])


    data_vars_2d = {}
    data_vars_3d = {}
    # data_vars_pseudo_3d = {}

    # def _construct_pseudo_3d_data(all_data, nlev, xcoords):
    #     pseudo_fieds_dict = {}
    #     for key, val in all_data.items():
    #         if isinstance(val, dict):
    #             if 'type' in val.keys():
    #                 if val['type'] == ['pseudo_3d']:
    #                     fieldname = _fmt_fieldname(key[4:])
    #                     pseudo_fieds_dict[fieldname] = {'type': 'formatted_pseudo'}
    #                     # get all other keys that repr the same pseudo 3d field
    #                     all_pseudo_keys = [otherkey for otherkey in all_data.keys() if otherkey[4:] == key[4:]]
    #                     total_array = np.arange(1, nlev+1) # (nlev, matrix)
    #                     for pseudo_key in all_pseudo_keys:
    #                         level=int(pseudo_key[1:4])
    #                         data =  _fmt_2d_field_to_matrix(datalist = all_data[pseudo_key]["data"],
    #                                                         xcoords=xcoords)









    for key, val in data.items():
        if isinstance(val, dict):
            if 'type' in val.keys():
                if val['type'] == ['2d']:
                    fieldname = _fmt_fieldname(key)
                    dataarray = _fmt_2d_field_to_matrix(datalist=val['data'],
                                                        xcoords = xcoords)
                    data_vars_2d[fieldname] = (["y", "x"], dataarray)
                elif val['type'] == ['3d']:
                    fieldname = _fmt_fieldname(key)
                    dataarray = _fmt_3d_field_to_matrix(datalist=val['data'])
                    data_vars_3d[fieldname] = (["y", "x", 'level'], dataarray)
                elif val['type'] == ['pseudo_3d']:
                    # # level = int(key[1:4])
                    # fieldname = _fmt_fieldname(key[4:])
                    # dataarray = _construct_pseudo_3d_dataa(datalist=val['data'],
                    #                                           )
                    fieldname = _fmt_fieldname(key)
                    dataarray = _fmt_2d_field_to_matrix(datalist=val['data'],
                                                        xcoords = xcoords)
                    data_vars_2d[fieldname] = (["y", "x"], dataarray)


                else:
                    sys.exit(f'unknown type {val["type"]} for {key}')

    # Combine 2D and 3D fields
    data_vars_2d.update(data_vars_3d)

    # Create the xarray Dataset
    ds = xr.Dataset(data_vars=data_vars_2d,
                    coords={'x': xcoords,
                            'y': ycoords,
                            'level': _make_level_dimension(metadict['nlev'])
                            },
                    )
    # Set dimension order (this is a convention (rioxarray likes the spatial coordiantes as last))
    ds = ds.transpose('level', 'y', 'x')

    # Metadata
    # meta_dict = {key: val[0] for key, val in data.items() if key in ['name', 'basedate', 'validate', 'leadtime', 'timestep', 'origin']}
    ds.attrs.update(metadict)

    # Set projection crs
    ds = ds.rio.write_crs(ds.attrs['projection'])
    ds = ds.rio.set_spatial_dims('x', 'y', inplace=True)

    return ds