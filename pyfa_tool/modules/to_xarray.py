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


def read_netCDF(file, **kwargs):
    # Check if file exist
    if not IO.check_file_exist(file):
        sys.exit(f'{file} does not exist.')

    ds = xr.open_dataset(file, **kwargs)
    return ds



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



def _fmt_3d_field_to_matrix(datalist):
    # convert to matrix with these dimensions: (y, x, levels)
    mat =np.asarray(datalist).transpose((1,0,2))
    return mat


def _make_level_dimension(nlev):
    levlist = list(np.arange(nlev))
    return np.asarray(levlist)


def reproject(dataset, target_epsg='EPSG:4326', nodata=-999):
    print(f'Reprojecting dataset to {target_epsg}.')
    # I am not a fan of -999 as nodata, but it must be a value that
    # can be typecast to integer (rasterio thing?)

    ds = dataset.transpose('level', 'y', 'x')
    for fieldname in list(ds.variables):
        # only applicable on xarray, not on dataset
        ds[fieldname].rio.write_nodata(nodata, inplace=True)

    # ds.rio.write_nodata(np.nan, inplace=True)
    ds = ds.rio.reproject(target_epsg, nodata=nodata)
    # remove no data
    ds = ds.where(ds != nodata)
    return ds



def json_to_full_dataset(jsonfile, reproj=True, target_epsg='EPSG:4326', nodata=-999):
    print('Reading json data')
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

    if reproj:
        ds = reproject(dataset=ds,
                       target_epsg=target_epsg,
                       nodata=nodata)

    return ds

