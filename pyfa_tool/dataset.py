#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 13:50:41 2024

@author: thoverga
"""

import os
import sys

import numpy as np
import xarray as xr
import rioxarray
from datetime import datetime, timedelta


from pyfa_tool.lib_functions import get_full_fa, field_exists
from pyfa_tool.modules.to_xarray import reproject, save_as_nc, read_netCDF
from pyfa_tool.modules.plotting import make_regular_fig, make_platcarree_fig, make_plot


class FaFile():
    """For interacting with FA files without storing data."""
    def __init__(self, fafile):
        self.fafile = fafile







class FaDataset():
    """For storing and analysing FA data as xarray."""
    def __init__(self, nodata=-999):
        self.ds = None # xarray.Dataset
        self.nodata = nodata


    # =============================================================================
    # Specials
    # =============================================================================
    def __repr__(self):
        return str(self.ds)

    def __str__(self):
        return str(self.ds)


    # =============================================================================
    # Setters / Getters
    # =============================================================================

    def get_fieldnames(self):
        return self._get_physical_variables()


    # =============================================================================
    # Importing data
    # =============================================================================

    def get_full_fa(self, fa_filepath, rm_tmpdir=True,
                    reproj=False, target_epsg='EPSG:4326'):

        self.ds = get_full_fa(fa_filepath=fa_filepath,
                              rm_tmpdir=rm_tmpdir,
                              reproj=reproj,
                              target_epsg='EPSG:4326',
                              nodata=self.nodata)


    def get_2d_field(self):
        pass


    def get_3d_field(self):
        pass


    def save_nc(self, outputfolder, filename, overwrite=False, **kwargs):

        assert not (self.ds is None), 'Empty instance of FaDataset.'

        saveds = self.ds
        #serialise special attributes
        saveds.attrs['basedate'] = datetime.strftime(saveds.attrs['basedate'],
                                                     '%Y-%m-%d %H:%M:%S' )
        saveds.attrs['validate'] = datetime.strftime(saveds.attrs['validate'],
                                                     '%Y-%m-%d %H:%M:%S' )
        saveds.attrs['leadtime'] = saveds.attrs['leadtime'].seconds


        save_as_nc(xrdata=saveds,
                   outputfolder=outputfolder,
                   filename=filename,
                   overwrite=overwrite,
                   **kwargs)

    def read_nc(self, file, **kwargs):
        if not (self.ds is None):
            sys.exit('The dataset is not empty! Use read_nc() only on an empty Dataset.')
        ds = read_netCDF(file, **kwargs)

        #un-serialise special attributes
        ds.attrs['basedate'] = datetime.strptime(ds.attrs['basedate'],
                                                 '%Y-%m-%d %H:%M:%S' )
        ds.attrs['validate'] = datetime.strptime(ds.attrs['validate'],
                                                     '%Y-%m-%d %H:%M:%S' )
        ds.attrs['leadtime'] = timedelta(seconds=int(ds.attrs['leadtime']))


        self.ds = ds
        print('netCDF loaded.')

    # =============================================================================
    # Data manipulation
    # =============================================================================

    def reproject(self, target_epsg='EPSG:4326'):
        assert not (self.ds is None), 'Empty instance of FaDataset.'
        ds = reproject(dataset=self.ds,
                       target_epsg=target_epsg,
                       nodata=self.nodata)
        self.ds = ds




    # =============================================================================
    # Analysis of data
    # =============================================================================
    def plot(self, variable, level=None, title=None, grid=False, land=True,
             coastline=True, contour=False, legend=True,
             levels=10, **kwargs):


        assert not (self.ds is None), 'Empty instance of FaDataset.'

        if self._is_3d_field(variable):
            assert not (level is None), f'{variable} is a 3D field. Specify a level.'
            xarr = self.ds[variable].sel(level=level)
        elif self._is_2d_field(variable):
            xarr = self.ds[variable]
        else:
            sys.exit('something unforseen is wrong.')

        islatlon = self. _in_latlon()
        if (land) | (coastline):
            if not islatlon:
                sys.exit('Adding land and coastline features is only available in latlon coordinates')


        if islatlon:
            fig, ax = make_platcarree_fig()
        else:
            fig, ax = make_regular_fig()

        # create title
        if title is None:
            title =  title=f'{variable} at {self.ds.attrs["validate"]} (UTC, LT={self.ds.attrs["leadtime"]}h)'


        ax = make_plot(dxr = xarr,
                        ax=ax,
                        title=title,
                        grid=grid,
                        land=land,
                        coastline=coastline,
                        contour=contour,
                        legend=legend,
                        levels=levels,
                        **kwargs)

        return ax




    def describe(self):
        pass

    # =============================================================================
    # Helpers
    # =============================================================================

    def field_exist(self, fieldname):
        if self.ds is None:
            sys.exit('Empty FaDataset object.')
        phys_variables = self._get_physical_variables()

        if fieldname in phys_variables:
            return True
        else:
            return False

    def _is_2d_field(self, fieldname):
        if not self.field_exist(fieldname):
            return False #field does not exist at all
        if len(self.ds[fieldname].data.shape) == 2:
            return True
        else:
            return False

    def _is_3d_field(self, fieldname):
        if not self.field_exist(fieldname):
            return False #field does not exist at all
        if len(self.ds[fieldname].data.shape) == 3:
            return True
        else:
            return False

    def _in_latlon(self):
       if self.ds is None:
           return False #data does not exist at all
       if str(self.ds.rio.crs) == 'EPSG:4326':
           return True
       else:
           return False

    def _get_physical_variables(self):
        blacklist=['spatial_ref']
        dims = list(self.ds.dims)
        var_list = [var for var in list(self.ds.variables) if var not in blacklist]
        var_list = [var for var in var_list if var not in dims]
        return var_list












