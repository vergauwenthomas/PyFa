#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 09:07:27 2024

@author: thoverga
"""



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