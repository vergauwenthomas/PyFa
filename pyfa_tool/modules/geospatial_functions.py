#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 09:07:27 2024

@author: thoverga
"""
from pyproj import CRS

def reproject(dataset, target_epsg='EPSG:4326', nodata=-999):
    """
    Reproject a Dataset to an other CRS by EPSG code.

    The x and y coordinates are transformed to a target EPSG code.


    Parameters
    ----------
    dataset : xarray.Dataset
        A Dataset with x and y coordinates and with a rio.crs attribute indicating
        the current projection.
    target_epsg : str, optional
        The CRS to project to in EPSG format. The default is 'EPSG:4326'.
    nodata : int, optional
        Numeric value for nodata (will be introduced when reprojecting). For
        some reason this value must be typecasted to integer ???
        The default is -999.

    Returns
    -------
    ds : xarray.Dataset
        The Dataset with x and y coords now in the target CRS.

    Note
    ------
    All 0-size dimensions (like datetime dimensions for FaDataset) are removed
    by the reprojection! So make shure to copy them over.

    """
    print(f'Reprojecting dataset to {target_epsg}.')
    # I am not a fan of -999 as nodata, but it must be a value that
    # can be typecast to integer (rasterio thing?)

    if 'spatial_ref' in list(dataset.variables):
        dataset = dataset.drop_vars('spatial_ref')




    #dimensions and coordinate must have the same name
    # for rioxarray !!!!!!!!

    dataset = dataset.rename({'xdim': 'x', 'ydim': 'y'})
    dataset = dataset.rio.set_spatial_dims('x', 'y')


    #rasterio requires y, x as last dims
    if 'zdim' in dataset.dims:
        dataset = dataset.transpose('validate', 'basedate','zdim', 'y', 'x')
    else:
        dataset = dataset.transpose('validate', 'basedate', 'y', 'x')


    dataset = dataset.rio.write_crs(dataset.attrs['proj4str'])
    dataset = dataset.rio.reproject(target_epsg, nodata=nodata)

    #overwrite the current proj4 string
    dataset.attrs['proj4str'] = CRS.from_string(target_epsg).to_proj4()

    #cleanup
    # remove no data
    dataset = dataset.where(dataset != nodata)

    if 'spatial_ref' in list(dataset.variables):
        dataset = dataset.drop_vars('spatial_ref')

    dataset = dataset.rename_dims({'x': 'xdim', 'y': 'ydim'})
    return dataset
