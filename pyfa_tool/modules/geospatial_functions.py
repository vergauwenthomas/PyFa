#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 09:07:27 2024

@author: thoverga
"""


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

    ds = dataset.transpose('level', 'validate', 'basedate', 'y', 'x')

    for fieldname in list(ds.variables):
        if fieldname not in ds.dims:
            # only applicable on xarray, not on dataset
            ds[fieldname].rio.write_nodata(nodata, inplace=True)

    # ds.rio.write_nodata(np.nan, inplace=True)
    ds = ds.rio.reproject(target_epsg, nodata=nodata)

    # remove no data
    ds = ds.where(ds != nodata)
    return ds
