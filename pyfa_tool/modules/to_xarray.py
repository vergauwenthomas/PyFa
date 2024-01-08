#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of functions to tranfer to/from xarray objects.

@author: thoverga
"""
import os
import sys
import xarray as xr
import numpy as np
import rioxarray
from datetime import datetime, timedelta

from . import IO


def save_as_nc(xrdata, outputfolder, filename, overwrite=False, **kwargs):
    """
    Save an Xarray object to a NetCDF file.

    Parameters
    ----------
    xrdata : xarray.DataArray or xarray.DataSet
        The Xarray data object to save.
    outputfolder : str
        Path of the directory to save the NetCDF.
    filename : str
        Name of the netCDF file. (.nc extenstion is added if not provided.)
    overwrite : bool, optional
        If False, the xarray object is not saved if the netCDF file already
        exists. The default is False.
    **kwargs : optional
        kwargs are passed to the .to_netcdf() method of the xarray object.

    Returns
    -------
    None.

    """
    # check fileneme extension
    if not filename.endswith('.nc'):
        filename = filename + '.nc'

    # check if outputfolder exists
    if not IO.check_folder_exist(outputfolder):
        sys.exit(f'{outputfolder} directory not found.')

    # check if file exist
    target_file = os.path.join(outputfolder, filename)
    if (IO.check_file_exist(target_file) & (not overwrite)):
        sys.exit(f'{target_file} already exists.')

    # Remove file if ovrwrite is True
    if (IO.check_file_exist(target_file) & (overwrite)):
        os.remove(target_file)

    # convert to nc
    xrdata.to_netcdf(path=target_file,
                     mode='w',
                     **kwargs)
    print(f'Data saved to {target_file}')
    return None


# =============================================================================
# Formatters
# =============================================================================


def _fmt_basedate(string, fmt="%Y-%m-%d"):
    return datetime.strptime(string, fmt)

def _fmt_validate(string, fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.strptime(string, fmt)

def _create_proj4_str(metadict):
    proj4str = f'+proj={metadict["projection"][0]} +lat_1={metadict["lat_1"][0]} +lat_2={metadict["lat_2"][0]} ' + \
        f'+lon_0={metadict["lon_0"][0]} +R={metadict["proj_R"][0]}'
    return proj4str

def _fmt_fieldname(string):
    return string.strip().lower()


def _fmt_2d_field_to_matrix(datalist, xcoords):
    xlen = xcoords.shape[0]
    # ylen = ycoords.shape[0]

    ncols=xlen #test 1

    test = np.asarray(datalist)
    test.shape = (test.size//ncols, ncols)
    return test







def json_to_full_dataset(jsonfile):
    data = IO.read_json(jsonfile)

    metadict = {
        'basedate': _fmt_basedate(data['pyfa_metadata']['basedate'][0]),
        'validate': _fmt_validate(data['pyfa_metadata']['validate'][0]),
        'leadtime': timedelta(hours = float(data['pyfa_metadata']['leadtime'][0])),

        'timestep': int(data['pyfa_metadata']['timestep'][0]),
        'origin': str(data['pyfa_metadata']['origin'][0]),

        'projection': _create_proj4_str(data['pyfa_metadata']),
        'nx': int(data['pyfa_metadata']['nx'][0]),
        'ny': int(data['pyfa_metadata']['ny'][0]),
        'dx': int(data['pyfa_metadata']['dx'][0]),
        'dy': int(data['pyfa_metadata']['ny'][0]),
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
    for key, val in data.items():
        if isinstance(val, dict):
            if 'type' in val.keys():
                if val['type'] == ['2d']:
                    fieldname = _fmt_fieldname(key)
                    dataarray = _fmt_2d_field_to_matrix(datalist=val['data'],
                                                        xcoords = xcoords)
                    data_vars_2d[fieldname] = (["y", "x"], dataarray)
                elif val['type'] == ['3d']:
                    sys.exit('nog te implementeren')
                else:
                    sys.exit(f'unknown type {val["type"]} for {key}')


    ds = xr.Dataset(data_vars=data_vars_2d,
                    coords={'x': xcoords,
                            'y': ycoords,
                            },
                    # dims=["y", "x"]
                    )
    return ds




# def json_to_rioxarray(json_data_path, json_metadata_path, reproject=True, target_epsg="EPSG:4326"):
#     """
#     Create a xarray.DataArray from the data and metadata files (jsons).

#     The data can be reprojected to other CRS if required.

#     Parameters
#     ----------
#     json_data_path : str
#         Path to the json file containing the data.
#     json_metadata_path : str
#         Path to the json file containing the metadata.
#     reproj : bool, optional
#         If True, the field will be reprojected by using the target_crs. The
#         default is True.
#     target_crs : str, optional
#         EPSG code for the desired CRS of the xarray.DataArray. The default is
#         'EPSG:4326'.

#     Returns
#     -------
#     data_xr : xarray.DataArray
#         The data from the json files contained in a xarray.DataArray object.

#     """
#     # =============================================================================
#     #  Read json file
#     # =============================================================================

#     # Opening JSON files
#     data = IO.read_json(json_data_path)
#     metadata = IO.read_json(json_metadata_path)
#     data.update(metadata)

#     # =============================================================================
#     # Data to xarray
#     # =============================================================================

#     if len(np.array(data['data']).shape) == 2:
#         # 2D field
#         data_xr = xr.DataArray(np.asarray(data['data']).transpose(),
#                                coords={'x': np.asarray(data['xcoords']),
#                                        'y': np.asarray(data['ycoords']),
#                                        },
#                                dims=["y", "x"])

#     elif len(np.array(data['data']).shape) == 3:
#         # 3D field
#         data_xr = xr.DataArray(np.array(data['data']).transpose((1, 0, 2)),
#                                coords={'x': np.asarray(data['xcoords']),
#                                        'y': np.asarray(data['ycoords']),
#                                        'level': np.asarray(data['zcoords'])
#                                        },
#                                dims=["y", "x", "level"])

#         data_xr = data_xr.transpose('level', 'y', 'x')  # reorder for transformating

#     data_xr.rio.set_spatial_dims('x', 'y', inplace=True)

#     # =============================================================================
#     # add metadata
#     # =============================================================================
#     meta_dict = {key: val[0] for key, val in data.items() if key in ['name', 'basedate', 'validate', 'leadtime', 'timestep', 'origin']}
#     data_xr.attrs.update(meta_dict)

#     # =============================================================================
#     # add projection info
#     # =============================================================================

#     proj_dict = {key: val[0] for key, val in data.items() if key in ['projection', 'lon_0', 'lat_1', 'lat_2', 'proj_R', 'nx', 'ny', 'dx', 'dy', 'ex', 'ey']}

#     proj4str = f'+proj={proj_dict["projection"]} +lat_1={proj_dict["lat_1"]} +lat_2={proj_dict["lat_2"]} ' + \
#         f'+lon_0={proj_dict["lon_0"]} +R={proj_dict["proj_R"]}'

#     data_xr = data_xr.rio.write_crs(proj4str)

#     # =============================================================================
#     # Reproject to latlon
#     # =============================================================================
#     if reproject:
#         data_xr = data_xr.rio.reproject(target_epsg)

#     # remove no data
#     data_xr = data_xr.where(data_xr != data_xr.rio.nodata)

#     return data_xr
