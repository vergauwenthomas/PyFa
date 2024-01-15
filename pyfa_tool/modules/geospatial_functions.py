#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 09:07:27 2024

@author: thoverga
"""

import copy

def reproject(dataset, target_epsg='EPSG:4326', nodata=-999):
    print(f'Reprojecting dataset to {target_epsg}.')
    # I am not a fan of -999 as nodata, but it must be a value that
    # can be typecast to integer (rasterio thing?)

    ds = dataset.transpose('level', 'validate', 'basedate', 'y', 'x')

    # Reprojecting removes the time dimensions, so save first
    #TODO is ok for collection with multiple validates
    validates_copy = copy.copy(ds['validate'].data)
    basedates_copy = copy.copy(ds['basedate'].data)


    for fieldname in list(ds.variables):
        if fieldname not in ds.dims:
            # only applicable on xarray, not on dataset
            ds[fieldname].rio.write_nodata(nodata, inplace=True)

    # ds.rio.write_nodata(np.nan, inplace=True)
    ds = ds.rio.reproject(target_epsg, nodata=nodata)

    # remove no data
    ds = ds.where(ds != nodata)
    return ds