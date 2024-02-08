#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 13:50:41 2024

@author: thoverga
"""

import os
import sys
from collections.abc import Iterable
import subprocess
import pandas as pd
import xarray as xr
import rioxarray #Do not remove this import!


import pyfa_tool.modules.IO as IO
import pyfa_tool.modules.geospatial_functions as geospatial_func
import pyfa_tool.modules.reading_fa as reading_fa
import pyfa_tool.modules.plotting as plotting

from pyfa_tool import package_path
from pyfa_tool.file import FaFile





class FaDataset():
    """A Class that holds data, and methods, of an FA file."""

    def __init__(self, fafile=None, nodata=-999):
        """
        Initiate of an FaDataset object.

        Parameters
        ----------
        fafile : str, optional
            Path of the target FA-file. The default is None.
        nodata : int, optional
            The Nodata value to be used by (rio)xarray. The default is -999.

        Returns
        -------
        None.

        Note
        -------
        Rasterio uses an integer value of the nodata, so make sure an
        integer-casting of the nodata value exists.

        """
        # test if file exist
        if not fafile is None:
            if not IO.check_file_exist(fafile):
                sys.exit(f'{fafile} is not a file.')

        self.fafile = fafile
        self.ds = None # xarray.Dataset
        self.nodata = nodata


    # =========================================================================
    # Specials
    # =========================================================================
    def __repr__(self):
        return str(self.ds)

    def __str__(self):
        return str(self.ds)


    # =========================================================================
    # Setters / Getters
    # =========================================================================
    def set_fafile(self, fafile):
        """
        Update the path to the FA-file.

        Parameters
        ----------
        fafile : str
            Path to the FA-file.

        Returns
        -------
        None.

        """
        if not IO.check_file_exist(fafile):
            sys.exit(f'{fafile} is not a file.')
        self.fafile = fafile

    def get_fieldnames(self):
        """
        Get all present variables

        Returns
        -------
        list
            A list of all the availabel variables.

        """
        return self._get_physical_variables()


    def get_validate(self):
        """
        Get the validate of the FA data.

        Returns
        -------
        datetime.datetime or aray of datetimes
            The validate of the FA data.

        """

        valid_coordinates = self.ds.coords['validate'].data
        if len(valid_coordinates) == 1:
            #Typecast to pandas datetime for incorporation in MetObs-toolkit
            return pd.Timestamp(valid_coordinates[0])
        else:
            return [pd.Timestamp(t) for t in valid_coordinates]

    def get_basedate(self):
        """
        Get the baseate of the FA data.

        Returns
        -------
        pandas.Timestamp or list of them
            The validate of the FA data.

        """
        base_coordinates = self.ds.coords['basedate'].data
        if len(base_coordinates) == 1:
            return pd.Timestamp(base_coordinates[0])
        else:
            return [pd.Timestamp(t) for t in base_coordinates]

    def get_timestep(self):
        """
        Get the delta-t (timestep) of the model.

        Returns
        -------
        pandas.Timedelta
            The model timeresolution.

        """
        return pd.Timedelta(int(self.ds.attrs['timestep']), unit='seconds')

    def get_leadtime(self):
        """
        Get the model leadtime at the current data.

        Returns
        -------
        pandas.Timedelta
            The leadtime of the model.

        """
        return self.get_validate() - self.get_basedate()







    # =========================================================================
    # Importing data
    # =========================================================================
    def import_fa(self, whitelist=None, blacklist=None,
                  rm_tmpdir=True, reproj=False, target_epsg='EPSG:4326',
                  ):
        """
        Import a FA file and make a xarray.Dataset of it.

        The creation of this dataset is done by:

            * Reading all fieldnames of the FA file.
            * Constructing a whitelist (fieldnames to be read by RFa)
            * Construct a blacklist (fieldnames to be skipped by RFa)
            * Use RFa to read all desired fields, and write them to json
            * Read the jsons and feed the data to a xarray.Dataset.
            * Add metadata to the xarray.Dataset
            * Reproject (if needed) the xarray.Dataset


        Parameters
        ----------
        whitelist : list or (fieldname)str, optional
            A list of (or a single) fieldname to read from a FA file. If None,
            all fieldnames are read. The default is None.
        blacklist : list or (fieldname)str, optional
            A list of (or a single) fieldname to skip from the FA file. If None,
            the blacklist is empty. The blacklist surpasses the whitelist. The default is None.
        rm_tmpdir : bool, optional
            If True, the directory where the json files are stored will be
            removed. The default is True.
        reproj : bool, optional
            If True, the data will be reproject to the CRS specified by the
            target_epsg. The default is False.
        target_epsg : str, optional
            EPSG code to reproject the data to. The default is 'EPSG:4326'.


        Returns
        -------
        None.

        Note
        ------
        Pseudo 3d fields are read as seperate 2D fields. So if you want to add
        them to the white/black lists, do this by specifying there full name (
        thus with the S00x prefix.)

        """

        assert not self.fafile is None, 'First set a FAfile path, using the set_fafile() method.'

        # Get all available fields
        FA = FaFile(self.fafile)
        subset_fields = {'2d_white': [],
                         '3d_white': [],
                         '2d_black': [],
                         '3d_black': []} # to add black and whitelist fields

        # ---------- Whilelist creation -------------------


        if not (whitelist is None):
            # test if the whitelist is an iterable (list/series/array):
            if isinstance(whitelist, str):
                whitelist = [whitelist]
            if not isinstance(whitelist, Iterable):
                sys.exit(f'{whitelist} is not an Iterable (like a list/array/...)')


            # Find the 2d-whitelist fields
            all_available_fields = FA._list_all_fieldnames_as_2d_fields()
            subset_fields['2d_white'] = [field for field in whitelist if field in all_available_fields]

            # Find the pseudo 3d-fields and add them to the 2d white lists
            all_available_fields = FA._list_all_pseudo_3d_fieldnames_as_2d_fields()
            pseudo_2d_extension = [field for field in whitelist if field in all_available_fields]
            subset_fields['2d_white'].extend(pseudo_2d_extension)

            # Find the 3d-whitelist fields
            all_available_3dfields = FA._list_all_3d_fieldnames_as_basenames()
            subset_fields['3d_white'] = [field for field in whitelist if field in all_available_3dfields]

            # Single level of 3d field (into the 2d white list)
            all_available_3dfields = FA._list_all_3d_fieldnames_as_2d_fields()
            specific_level_of_3d = [field for field in whitelist if field in all_available_3dfields]
            subset_fields['2d_white'].extend(specific_level_of_3d)



            # Check at leas one field is included in the whitelists
            if ((len(subset_fields['2d_white']) == 0) & (len(subset_fields['3d_white']) == 0)):
                sys.exit(f'None of these fields are found in the FA file: {whitelist}')
        else:
            subset_fields['2d_white'] = FA._list_all_2d_fieldnames_as_2d_fields()
            subset_fields['2d_white'].extend(FA._list_all_pseudo_3d_fieldnames_as_2d_fields())
            subset_fields['3d_white'] = FA._list_all_3d_fieldnames_as_basenames()

        # ---------- Blacklist creation -------------------

        if not (blacklist is None):
            # test if the blacklist is an iterable (list/series/array):
            if isinstance(blacklist, str):
                blacklist = [blacklist]
            if not isinstance(blacklist, Iterable):
                sys.exit(f'{blacklist} is not an Iterable (like a list/array/...)')

            # Get all available fields (if not yet made in the whitelist part)
            if FA is None:
                FA = FaFile(self.fafile)


            # Find the 2d-blacklist fields
            all_available_fields = FA._list_all_fieldnames_as_2d_fields()
            subset_fields['2d_black'] = [field for field in blacklist if field in all_available_fields]

            # Find the pseudo 3d-fields and add them to the 2d black lists
            all_available_fields = FA._list_all_pseudo_3d_fieldnames_as_2d_fields()
            pseudo_2d_extension = [field for field in blacklist if field in all_available_fields]
            subset_fields['2d_black'].extend(pseudo_2d_extension)

            # Find the 3d-blacklist fields
            all_available_3dfields = FA._list_all_3d_fieldnames_as_basenames()
            subset_fields['3d_black'] = [field for field in blacklist if field in all_available_3dfields]


            # Check at leas one field is included in the blacklists
            if ((len(subset_fields['2d_white']) == 0) & (len(subset_fields['3d_white']) == 0)):
                print(f'WARNING: None of these fields are found in the FA file: {blacklist}')


        # create at tmpdir if not provided
        tmpdir = IO.create_tmpdir(location=os.getcwd())


        # There is no clean way i found to parse multiple lists as arguments
        #for an R script. So write them to json, and read them in the Rscript.

        Rfa_attr_json=os.path.join(tmpdir, 'Rfa_extra_attrs.json')
        IO.write_json(datadict=subset_fields,
                      jsonpath=Rfa_attr_json,
                      force=True)

        # Run Rscript to generete a nc file with data and meta info
        r_script = os.path.join(package_path, 'modules',
                                'rfa_scripts', 'get_all_fields.R')

        convert_fa = subprocess.Popen([os.path.join(IO._get_rbin(), 'Rscript'),
                                       r_script,
                                       FA.fafile,
                                       tmpdir,
                                       Rfa_attr_json])

        _ = convert_fa.wait()  # wait until finished before continuing

        # read in the netCDF4 file
        ncfile = os.path.join(tmpdir, "FA.nc")

        # Convert to a xarray dataset

        ds = reading_fa.read_and_format_nc(ncfile)
        if rm_tmpdir:
            IO.remove_tempdir(tmpdir)

        # Update attribute
        self.ds = ds
        self._clean()

        if reproj:
            self.reproject(target_epsg=target_epsg)


    def import_2d_field(self, fieldname,
                        rm_tmpdir=True, reproj=False, target_epsg='EPSG:4326'):
        """
        Import a 2D field of a FA file into an xarray.Dataset.

        This method is a wrapper on the more general .import_fa() method.

        Parameters
        ----------
        fieldname : str
            The fieldname of a 2D field in the FA file.
        rm_tmpdir : bool, optional
            If True, the directory where the json files are stored will be
            removed. The default is True.
        reproj : bool, optional
            If True, the data will be reproject to the CRS specified by the
            target_epsg. The default is False.
        target_epsg : str, optional
            EPSG code to reproject the data to. The default is 'EPSG:4326'.

        Returns
        -------
        None.

        """


        assert not self.fafile is None, 'First set a FAfile path, using the set_fafile() method.'

        # Get all available fields
        FA = FaFile(self.fafile)

        # Check if fieldname is a 2d field
        if fieldname not in FA._list_all_2d_fieldnames_as_2d_fields():
            sys.exit(f'{fieldname} not found in the possible 2D fields: {FA._list_all_2d_fieldnames_as_2d_fields()}')

        self.import_fa(whitelist=fieldname,
                       blacklist=None,
                       rm_tmpdir=rm_tmpdir,
                       reproj=reproj)


    def import_3d_field(self, fieldname,
                        rm_tmpdir=True, reproj=False, target_epsg='EPSG:4326'):
        """
        Import a 3D field of a FA file into an xarray.Dataset.

        This method is a wrapper on the more general .import_fa() method.

        Parameters
        ----------
        fieldname : str
            The basisfieldname of a 3D field. 'TEMPERATURE' is an example of a
            basisfieldname IF 2D fieldnames as S001TEMPERATURE and
            S002TEMPERATURE and ... are found.
        rm_tmpdir : bool, optional
            If True, the directory where the json files are stored will be
            removed. The default is True.
        reproj : bool, optional
            If True, the data will be reproject to the CRS specified by the
            target_epsg. The default is False.
        target_epsg : str, optional
            EPSG code to reproject the data to. The default is 'EPSG:4326'.

        Returns
        -------
        None.

        """

        assert not self.fafile is None, 'First set a FAfile path, using the set_fafile() method.'

        # Get all available fields
        FA = FaFile(self.fafile)

        # Check if fieldname is a 2d field
        if fieldname not in FA._list_all_3d_fieldnames_as_basenames():
            sys.exit(f'{fieldname} not found in the possible 3D fields: {FA._list_all_3d_fieldnames_as_basenames()}')

        self.import_fa(whitelist=fieldname,
                       blacklist=None,
                       rm_tmpdir=rm_tmpdir,
                       reproj=reproj,
                       target_epsg=target_epsg)


    def save_nc(self, outputfolder, filename, overwrite=False, **kwargs):
        """
        Save the xarray.Dataset as a netCDF file.


        Parameters
        ----------
        outputfolder : str
            Path to the folder to write the netCDF file to.
        filename : str
            Name of the netCDF file.
        overwrite : bool, optional
            If the path of the target netCDF file exist, an error will be
            thrown unles overwrite is True. Then the file will be overwritten.
            The default is False.
        **kwargs : kwargs
            Kwargs will be passed to the xarray.to_netcdf() method.

        Returns
        -------
        None.

        """
        assert not (self.ds is None), 'Empty instance of FaDataset.'

        self._clean()
        saveds = self.ds

        IO.save_as_nc(xrdata=saveds,
                   outputfolder=outputfolder,
                   filename=filename,
                   overwrite=overwrite,
                   **kwargs)


    def read_nc(self, file, **kwargs):
        """
        Read a netCDF file and import it to an xarray.Dataset()

        Parameters
        ----------
        file : str
            Path tho the netCDF file.
        **kwargs : kwargs
            Kwargs will be passed to the xarray.open_dataset() method.

        Returns
        -------
        None.

        """


        if not (self.ds is None):
            sys.exit('The dataset is not empty! Use read_nc() only on an empty Dataset.')
        ds = IO.read_netCDF(file, **kwargs)

        #TODO: Setup the rio projection!!

        self.ds = ds
        self._clean()
        print('netCDF loaded.')


    # =============================================================================
    # Data manipulation
    # =============================================================================

    def reproject(self, target_epsg='EPSG:4326'):
        """
        Reproject the dataset to a target CRS.

        (This can only be applied when sufficient current projection
         information is available.)

        Parameters
        ----------
        target_epsg : str, optional
            Target epsg code to project to. The default is 'EPSG:4326'.

        Returns
        -------
        None.

        """
        assert not (self.ds is None), 'Empty instance of FaDataset.'

        #to make shure itereative reprojection is possible
        if 'lat' in self.ds.coords:
            self.ds = self.ds.rename({'lat': 'y'})
        if 'lon' in self.ds.coords:
            self.ds = self.ds.rename({'lon': 'x'})



        ds = geospatial_func.reproject(dataset=self.ds,
                                       target_epsg=target_epsg,
                                       nodata=self.nodata)



        #Time dimensions are not projected, and are removed by rio, so
        # add these dimesions back to te reprojected dataset
        if 'validate' not in ds.dims:
            ds = ds.assign_coords({'validate': self.ds.coords['validate'].data})
        if 'basedate' not in ds.dims:
            ds = ds.assign_coords({'basedate': self.ds.coords['basedate'].data})

        if target_epsg=='EPSG:4326':
            ds = ds.rename({'x': 'lon', 'y': 'lat'})



        self.ds = ds
        self._clean()




    # =============================================================================
    # Analysis of data
    # =============================================================================
    def plot(self, variable, level=None, title=None, grid=False, land=None,
             coastline=None, contour=False,
             contour_levels=10, **kwargs):
        """
        Make a 2D spatial plot of a Dataset.


        Parameters
        ----------
        variable : str
            A 2D fieldname or a 3D basisfieldname (level is required) to plot.
        level : int, optional
            The level to plot if a 3D basisfieldname is provided. The default
            is None.
        title : str, optional
            The title of the plot. If None, a default title is constructed. The
            default is None.
        grid : bool, optional
            Add gridlines to plot. The default is False.
        land : bool, optional
            If True, and if the dataset is in a latlon projection (EPSG:4326),
            then land boarders are drawn. If None, it will be set to True if
            the projection is latlon, else False. The default is None.
        coastline : bool, optional
            If True, and if the dataset is in a latlon projection (EPSG:4326),
            then coastlines are drawn. If None, it will be set to True if
            the projection is latlon, else False. The default is None.
        contour : bool, optional
            If True, the contourf() method is used as a plotting backend, else
            the default xarray.Dataset.plot(). The default is False.
        contour_levels : int, optional
            Number of contour levels to use, if contour=True. The default is 10.
        **kwargs : kwargs
            Kwargs will be passed to the xarray.plot() method.

        Returns
        -------
        ax : matplotlib.pyplot.axes
            The geospatial axes of the plot.

        """



        assert not (self.ds is None), 'Empty instance of FaDataset.'

        if self._is_3d_field(variable):
            assert not (level is None), f'{variable} is a 3D field. Specify a level.'
            xarr = self.ds[variable].sel(level=level)
        elif self._is_2d_field(variable):
            xarr = self.ds[variable]
        else:
            sys.exit('something unforseen is wrong.')

        # setup default values for coastline and land features
        islatlon = self. _in_latlon()
        if land is None:
            if islatlon:
                land=True
            else:
                land=False

        if coastline is None:
             if islatlon:
                 coastline=True
             else:
                 coastline=False

        if (land) | (coastline):
            if not islatlon:
                sys.exit('Adding land and coastline features is only available in latlon coordinates')

        if islatlon:
            fig, ax = plotting.make_platcarree_fig()
        else:
            fig, ax = plotting.make_regular_fig()

        # create title
        if title is None:
            title =  title=f'{variable} at {self.get_validate()} (UTC, LT={self.get_leadtime()})'


        ax = plotting.make_plot(dxr = xarr,
                        ax=ax,
                        title=title,
                        grid=grid,
                        land=land,
                        coastline=coastline,
                        contour=contour,
                        levels=contour_levels,
                        **kwargs)

        return ax




    def describe(self):
        pass

    # =============================================================================
    # Helpers
    # =============================================================================
    # def _format_pseudo_3d_fields(self):
    #     """
    #     Convert 2d representation of pseudo 3D fields to 3D fields.

    #     By default pseudo-3D fields are read as multiple 2D fields. This method
    #     will combine all levels of pseudo fields and convert them into a 3D
    #     field.

    #     The level coordinate is set by using the variable name

    #     The 2D representations of the pseudo 3d fields are removed from the ds
    #     attribute.

    #     Returns
    #     -------
    #     None.

    #     """
    #     ds = self.ds

    #     # get a list of all variable that are pseudofields
    #     all_variables = [var for var in ds.variables if var not in ds.dims]
    #     pseudo_vars = [var for var in all_variables if (var.startswith('S') & var[1:3].isnumeric())]
    #     pseudo_basenames = list(set([var[4:].strip() for var in pseudo_vars]))

    #     for basename in pseudo_basenames:
    #         print(basename)
    #         # If basename already present than skip (we assume that the basename
    #         # contains all the data)
    #         if basename in all_variables:
    #             print(f'WARNING: {basename} is already a field and will not be the target of pseudo fields.')
    #             continue

    #         # get all pseudovars for this basename
    #         cur_pseudo_vars = [var for var in pseudo_vars if var[4:].strip() == basename]
    #         cur_levels = [int(var[1:4]) for var in cur_pseudo_vars]

    #         #assign coordinates to the level dimension
    #         coorddict = dict(zip(cur_pseudo_vars, cur_levels))
    #         for pseudo_var, lvl in coorddict.items():
    #             ds[pseudo_var] = ds[pseudo_var].assign_coords({'level': [lvl]})


    #         ds[basename] = xr.concat([ds[var] for var in cur_pseudo_vars],
    #                          pd.Index(cur_levels, name='level'))

    #         ds = ds.drop_vars(cur_pseudo_vars, errors='ignore')
    #     self.ds = ds

    def _set_time_dimensions(self):
        """
        Set up of the time dimension: validate and basedate.

        The timedimension are (in FA files) stored as attributes. In the context
        of creating datasets of multiple FA files, we must convert these time-
        attributes to dimensions and coordinates.

        In addition, the leadtime attribute is removed since it is time variant
        and blocking a merge on time.

        (Conversion to leadtime is availabel with the corresponding
         get methods.)


        Returns
        -------
        None.

        """

        # set basedate and validdate as coordinates (required for merging)
        if (('validate' in self.ds.attrs.keys()) & ('validate' not in self.ds.coords)):
            self.ds = self.ds.assign_coords({"validate": [self.ds.attrs['validate']]})
        if (('basedate' in self.ds.attrs.keys()) & ('basedate' not in self.ds.coords)):
            self.ds = self.ds.assign_coords({"basedate": [self.ds.attrs['basedate']]})

        # Create time-attribute-invarials
        # (When merging multiple files on a time coordinate, the attributes
        #  must be the same ---> validdate, leadtime, timestep cannot be stored
        # as attributes! (basedate aswell for nwp applications).

        # SO: validdate and basedata are coordinates, so we need only the
        # timestep as invariant so merging is possible, Drop variant time attributes
        to_drop = ['validate', 'basedate', 'leadtime']
        for dropkey in to_drop:
           self._drop_attr(dropkey)

    def _clean(self):
        # make sure the validate and basedate are dimensions with coordinates
        self._set_time_dimensions()
        # Convert pseudo 3d fields to 3d fields
        # self._format_pseudo_3d_fields()
        # Fix dimension order
        # self.ds = self.ds.transpose('y', 'x', 'level', 'validate', 'basedate')


    def field_exist(self, fieldname):
        """ Check if a variable exist in the xarray.Dataset (2D and 3D)"""
        if self.ds is None:
            sys.exit('Empty FaDataset object.')
        phys_variables = self._get_physical_variables()

        if fieldname in phys_variables:
            return True
        else:
            return False

    def _is_2d_field(self, fieldname):
        """ Check if a fieldname is an available 2D field."""
        if not self.field_exist(fieldname):
            return False #field does not exist at all
        if len(self.ds[fieldname].data.shape) == 2:
            return True
        else:
            return False

    def _is_3d_field(self, fieldname):
        """ Check if a fieldname is an available 3D field."""
        if not self.field_exist(fieldname):
            return False #field does not exist at all
        if len(self.ds[fieldname].data.shape) == 3:
            return True
        else:
            return False

    def _in_latlon(self):
        """ Check if a dataset is in latitude-longitude spatial coordinates."""
        if self.ds is None:
            return False #data does not exist at all
        if str(self.ds.rio.crs) == 'EPSG:4326':
            return True
        else:
            return False

    def _get_physical_variables(self):
        blacklist=['spatial_ref']

        var_list = [var for var in list(self.ds.variables) if var not in blacklist]
        var_list = [var for var in var_list if var not in list(self.ds.dims)]
        var_list = [var for var in var_list if var not in list(self.ds.coords)]

        return var_list


    def _drop_attr(self, key):
        """Drop a key in the attrs, if it exists."""
        try:
            del self.ds.attrs[key]
        except KeyError:
            pass










