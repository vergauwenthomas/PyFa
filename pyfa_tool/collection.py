#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module that holds the FaCollection class

@author: thoverga
"""

import sys
import xarray as xr
import numpy as np
from pyfa_tool.dataset import FaDataset as FaDatasetClass
import pyfa_tool.modules.IO as IO


class FaCollection():
    """This class holds methods and data for combining FaDatasets to one object."""

    def __init__(self, FaDatasets=[], combine=False):
        """
        Initialize a FaCollection.

        Parameters
        ----------
        FaDatasets : list, optional
            A list of FaDatasets. The default is [].
        combine : bool, optional
            If True, setting FaDatasets will also automatically combined them by validate to one xarray.Dataset object. Default is False.

        Returns
        -------
        None.

        """
        self.ds = None
        self.FaDatasets = FaDatasets
        self.combine = combine

    # =========================================================================
    # Specials
    # =========================================================================
    def __repr__(self):
        """String representation."""
        return str(self.ds)

    def __str__(self):
        """String typecaste representation."""
        return str(self.ds)

    # =============================================================================
    # Getters/setters
    # =============================================================================

    def set_fadatasets(self, FaDatasets=[]):
        """
        Update the FaDatasets of this collection.

        Parameters
        ----------
        FaDatasets : list, optional
            list of (multiple) FaDatasets to add to the collection. The default
            is [].

        Returns
        -------
        None.

        """
        if len(FaDatasets) == 0:
            sys.exit('No FaDatasets are provided.')
        if len(FaDatasets) < 2:
            sys.exit(f'Only one FaDatasets is provided: {FaDatasets[0]}')

        # type testing
        for dataset in FaDatasets:
            if not isinstance(dataset, FaDatasetClass):
                sys.exit(f'{dataset} is not an instance of FaDataset.')

        # TODO: check for duplicates here

        self.FaDatasets = FaDatasets

        # Combine if specified
        if self.combine:
            self.combine_by_validate()

    def set_fadatasets_by_file_regex(self, searchdir, filename_regex='*', **kwargs):
        """
        Update the FaDatasets of this collection by using regex expression of filenames.

        This methods will select the FA files, according to the regex expression,
        import the data and update the datasets of this collection.

        Parameters
        ----------
        searchdir : str
            Path to the directory where the regex search query is executed.
            This is most often the direcotry where the FA files are stored.
        filename_regex : str, optional
            Regex expression to match filenames. The default is '*'.
        **kwargs :
            kwargs passed to the FaDataset.import_fa() method to specify which
            fields are imported.

        Returns
        -------
        None.

        """
        # Get paths to the FA files
        filepaths = IO.get_paths_using_regex(searchdir=searchdir,
                                             filename_regex=filename_regex)
        # Read the FaFiles
        fadatasets = []
        for file in filepaths:
            Dataset = FaDatasetClass(fafile=file)
            Dataset.import_fa(**kwargs)
            fadatasets.append(Dataset)

        # Add them as attribute
        self.set_fadatasets(FaDatasets=fadatasets)

        # Combine if specified
        if self.combine:
            self.combine_by_validate()

    def combine_by_validate(self):
        """
        Combine all datasets by mergeing on the validate-dimension.

        This method wil create a xarray.Dataset objectect containing all the
        data of the FaDatasets stored in this object and merged along the
        validate dimension.

        All FaDataset must share the same metadata attribute except for 'origin'
        and 'filepath'. The combined xarray.Dataset will have these attribtutes
        and the values are lists of the respectively attributes of the collection
        of FaDatasets.

        All FaDatasets are sorted along the validate dimension before merging.

        Returns
        -------
        None.

        Note
        ------
        For NWP and ensemble applications, the validate does not make an FA file
        unique. So a combine on multiple dimensions is prefered for some of these
        applications.

        """
        FaDatasets = self.FaDatasets

        if len(FaDatasets) == 0:
            sys.exit('No FaDatasets are provided.')
        if len(FaDatasets) < 2:
            sys.exit(f'Only one FaDatasets is provided: {FaDatasets[0]}')

        # Sort Datasets by increasing validate
        FaDatasets.sort(key=lambda x: x.get_validate(), reverse=False)
        # TODO: For NWP there is need for an additional sorting on basetime!

        # Prepare the attributes for merging
        # 1. check if the vertical level defenitions is the same (A and B list)
        comp_a = FaDatasets[0].ds.attrs['A_list']  # to compare with
        comp_b = FaDatasets[0].ds.attrs['B_list']  # to copare with
        for dataset in FaDatasets[1:]:
            if not _check_lists_are_equal(comp_a, dataset.ds.attrs['A_list']):
                sys.exit('Combining not possible since other defenition of levels is used (A_lists)')
            if not _check_lists_are_equal(comp_b, dataset.ds.attrs['B_list']):
                sys.exit('Combining not possible since other defenition of levels is used (B_lists)')

            # Since they are equal, drop these attributes in all (but one) datasets
            dataset._drop_attr('B_list')
            dataset._drop_attr('A_list')

        # get all attributes that are specific to one dataset
        specific_comb_attributes = {'origins': [],
                                    'filepaths': [],
                                    }

        # Make all Fadataset ready for merging on time coordinate
        for dataset in FaDatasets:
            specific_comb_attributes['origins'].append(dataset.ds.attrs['origin'])
            dataset._drop_attr('origin')

            specific_comb_attributes['filepaths'].append(dataset.ds.attrs['filepath'])
            dataset._drop_attr('filepath')

        ds = xr.concat(objs=[x.ds for x in FaDatasets],
                       dim='validate',  # For NWP, 'basetime' must be added as dimension!
                       data_vars='all',
                       coords='all',
                       compat='equals',
                       positions=None,  # sort in advance !!
                       fill_value=np.nan,
                       join='outer',
                       combine_attrs='no_conflicts'
                       )

        self.ds = ds
        self._clean()
        self.ds.attrs.update(specific_comb_attributes)

    def _clean(self):
        """Force a specific data format."""
        self.ds = self.ds.transpose('y', 'x', 'level', 'validate', 'basedate')


def _check_lists_are_equal(list_a, list_b):
    return set(list_a) == set(list_b)
