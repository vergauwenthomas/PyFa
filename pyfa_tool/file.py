#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 10:16:36 2024

@author: thoverga
"""


import os
import sys
import subprocess


import pyfa_tool.modules.IO as IO
import pyfa_tool.modules.describe_module as describe_module
from pyfa_tool import package_path


class FaFile():
    """A Class that holds metadata and fieldnames of a FA file."""
    def __init__(self, fafile):
        """
        Initiate a FAFile object.

        (The fieldnames and metadata are read on initiation.)

        Parameters
        ----------
        fafile : str
            The path of the FA file.

        Returns
        -------
        None.

        """
        # test if file exist
        if not IO.check_file_exist(fafile):
            sys.exit(f'{fafile} is not a file.')

        self.fafile = fafile

        self.metadata = None #dict with metadata
        self.fielddf = None #df with fields

        self._read_metadata()
        self._filter_fieldname_types(fieldsdf=self.fielddf,
                                     nlev = self.metadata['nlev'][0])

    # =========================================================================
    #     Special functions ------------
    # =========================================================================

    def __str__(self):
        return f'FA-file at {self.fafile}'
    def __repr__(self):
        return f'FA-file at {self.fafile}'

    # =========================================================================
    #     Getters/Setters -------------
    # =========================================================================

    def get_fieldnames(self):
        """
        Get the possible fieldnames in a dataframe

        Returns
        -------
        pandas.DataFrame
            A Dataframe with all possible fields.

        """
        return self.fielddf

    def get_metadata(self):
        """
        Get general metadata (applicable to all fields).

        Returns
        -------
        dict
            Dictionary with all general metadata.

        """
        return self.metadata

    # =========================================================================
    #  Methods
    # =========================================================================

    def describe(self):
        """
        Print out a detailed description on the FA content.

        Returns
        -------
        None.

        """
        describe_module.describe_fa_from_json(metadata=self.metadata,
                                              fieldslist=self.fielddf.to_dict('records'),
                                              d2fieldnames=self._pure_2d_fieldnames,
                                              d3fieldnames=self._pure_3d_fieldnames,
                                              pseudod3fieldnames=self._pure_pseudo_3d_fieldnames)


    # =========================================================================
    #     Helpers --------------------
    # =========================================================================

    def _filter_fieldname_types(self, fieldsdf, nlev):
        """
        Filter all the fields into 2D, 3D and pseudo3D categories.

        The filtering is done by checking if the same field has also a
        representation at multiple levels. If this is the case for all levels,
        than this is a 3D field. If it is only available at one level it is a
        2D level. If a field has mulitple representations, but not on all levels,
        it is a pseudo 3D field.

        This methods will set list attributes indicating these categories for
        both fieldnames and basenames (fieldnames without the level prefix).

        Parameters
        ----------
        fieldsdf : pandas.Dataframe
            The dataframe with all the available fields information.
        nlev : int
            The number of modellevels.

        Returns
        -------
        None.

        """
        all_fields = fieldsdf['name'].to_list()


        d2_fieldnames = list(set([f for f in all_fields if (not((f.startswith('S')) & (f[1:3].isnumeric())))]))

        multilevels = list(set(all_fields) - set(d2_fieldnames))
        basenames_multilevels = [f[4:] for f in multilevels]

        d3_fieldnames = []
        d3_basenames = []
        pseudo_3d_fieldnames = []
        pseudo_3d_basenames = []
        for base in basenames_multilevels:
            d2_equivalent = [f for f in multilevels if f[4:] == base]
            if len(d2_equivalent) < nlev:
                pseudo_3d_basenames.append(base)
                pseudo_3d_fieldnames.extend(d2_equivalent)
            else:
                d3_basenames.append(base)
                d3_fieldnames.extend(d2_equivalent)

        d2_fieldnames = list(set(d2_fieldnames))
        d3_fieldnames = list(set(d3_fieldnames))
        d3_basenames = list(set(d3_basenames))
        pseudo_3d_fieldnames = list(set(pseudo_3d_fieldnames))
        pseudo_3d_basenames = list(set(pseudo_3d_basenames))

        self._pure_2d_fieldnames=d2_fieldnames
        self._pure_3d_fieldnames = d3_fieldnames
        self._pure_3d_basenames = d3_basenames
        self._pure_pseudo_3d_basenames = pseudo_3d_basenames
        self._pure_pseudo_3d_fieldnames = pseudo_3d_fieldnames


    def _list_all_2d_fieldnames_as_2d_fields(self):
        """
        Get a list of all pure-2D fields.

        (A pure 2D field is a field which is not defined at multiple levels.)

        Returns
        -------
        list
            list of 2D fieldnames.

        """

        return self._pure_2d_fieldnames

    def _list_all_pseudo_3d_fieldnames_as_2d_fields(self):
        """
        Get a list of all pseudo 3D fields as pure-2D fields.

        (A pseudo 3D field is a 3D field which is not defined at all levels.)
        (A pure 2D field is a field which is not defined at multiple levels.)

        Returns
        -------
        list
            list of 2D fieldnames.

        """

        return self._pure_pseudo_3d_fieldnames

    def _list_all_3d_fieldnames_as_2d_fields(self):
        """
        Get a list of all 3D fields as pure-2D fields.

        (A pure 2D field is a field which is not defined at multiple levels.)

        Returns
        -------
        list
            list of 2D fieldnames.

        """

        return self._pure_3d_fieldnames

    def _list_all_fieldnames_as_2d_fields(self):
        """
        Get a list of all fields.

        (Thus these include all the pure 2D fields, and the 2D parts of a 3D
         field (i.g. S013TEMPERATURE))
        Returns
        -------
        list
            list of all fieldnames

        """

        return list(set(self.fielddf['name'].to_list()))
    def _list_all_3d_fieldnames_as_basenames(self):
        """
        Create a list of all basisfieldnames which occures at multiple levels.

        (The basisfieldname is the fieldname without the level identifier. So
          S012TEMPERATURE has TEMPERATURE as basisfieldname)

        Returns
        -------
        list
            List of basisnames for present 3D fields.

        """
        # find 3d fieldnames in the fielddf

        return self._pure_3d_basenames



    def _read_metadata(self):
        """
        Extract the fieldnames and metadata from an fa_filepath.

        This function will execute get_all_metadata.R, that will write all the
        fielnames and the metadata to json files. These files are read and
        formatted.

        The .metadata and .fielddf attributes are set.

        Returns
        -------
        None

        """
        # create at tmpdir if not provided
        tmpdir = IO.create_tmpdir(location=os.getcwd())
        # Run Rscript to generete a json file with all info
        r_script = os.path.join(package_path, 'modules', 'rfa_scripts',
                                'get_all_metadata.R')
        subprocess.call([os.path.join(IO._get_rbin(), 'Rscript'), r_script,
                         self.fafile, tmpdir])


        fields_jsonpath = os.path.join(tmpdir, 'fields.json')
        metadata_jsonpath = os.path.join(tmpdir, 'metadata.json')

        # Read the json files
        fielddata = IO.read_json(jsonpath=fields_jsonpath,
                                 to_dataframe=True)
        metadata = IO.read_json(jsonpath=metadata_jsonpath,
                                 to_dataframe=False)

        # Remove trailing and leading whitespace from fieldnames
        fielddata['name'] = [fieldname.strip() for fieldname in fielddata['name']]

        # update attributes
        self.metadata = metadata
        self.fielddf = fielddata

        IO.remove_tempdir(tmpdir)