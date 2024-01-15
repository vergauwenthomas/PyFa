#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 17:02:06 2024

@author: thoverga
"""

import os
import sys
import xarray as xr
import numpy as np
from pyfa_tool.dataset import FaDataset as FaDatasetClass
import pyfa_tool.modules.IO as IO

class FaCollection():
    def __init__(self, FaDatasets=[]):
        self.ds = None
        self.FaDatasets = FaDatasets

     # =========================================================================
     #     Special functions ------------
     # =========================================================================


    # =============================================================================
    # Getters/setters
    # =============================================================================
    def set_fadatasets(self, FaDatasets=[]):
        if len(FaDatasets) == 0:
            sys.exit('No FaDatasets are provided.')
        if len(FaDatasets) < 2:
            sys.exit(f'Only one FaDatasets is provided: {FaDatasets[0]}')

        # type testing
        for dataset in FaDatasets:
            if not isinstance(dataset, FaDatasetClass):
                sys.exit(f'{dataset} is not an instance of FaDataset.')
        self.FaDatasets = FaDatasets


    def set_fadatasets_by_file_regex(self, searchdir, filename_regex='*', **kwargs):
        # Get paths to the FA files
        filepaths = IO.get_paths_using_regex(searchdir=searchdir,
                                             filename_regex=filename_regex)
        # Read the FaFiles
        fadatasets =  []
        for file in filepaths:
            Dataset = FaDatasetClass(fafile=file)
            Dataset.import_fa(**kwargs)
            fadatasets.append(Dataset)

        #add them as attribute
        self.set_fadatasets()




    # =========================================================================
    # Specials
    # =========================================================================
    def __repr__(self):
        return str(self.ds)

    def __str__(self):
        return str(self.ds)



    def combine_by_validate(self):
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
        comp_a = FaDatasets[0].ds.attrs['A_list'] #to compare with
        comp_b = FaDatasets[0].ds.attrs['B_list'] #to copare with
        for dataset in FaDatasets[1:]:
            if not _check_lists_are_equal(comp_a, dataset.ds.attrs['A_list']):
                sys.exit(f'Combining not possible since other defenition of levels is used (A_lists)')
            if not _check_lists_are_equal(comp_b, dataset.ds.attrs['B_list']):
                sys.exit(f'Combining not possible since other defenition of levels is used (B_lists)')

            # Since they are equal, drop these attributes in all (but one) datasets
            dataset._drop_attr('B_list')
            dataset._drop_attr('A_list')


        # get all attributes that are specific to one dataset
        specific_comb_attributes = {'origins' : [],
                                    'filepaths' : [],
                                    }
        # Make all Fadataset ready for merging on time coordinate
        for dataset in FaDatasets:
            specific_comb_attributes['origins'].append(dataset.ds.attrs['origin'])
            dataset._drop_attr('origin')

            specific_comb_attributes['filepaths'].append(dataset.ds.attrs['filepath'])
            dataset._drop_attr('filepath')



        ds = xr.concat(objs = [x.ds for x in FaDatasets],
                       dim='validate', #For NWP, 'basetime' must be added as dimension!
                       data_vars='all',
                       coords='all',
                       compat='equals',
                       positions=None, #sort in advance !!
                       fill_value= np.nan,
                       join='outer',
                       combine_attrs='no_conflicts'
                       )

        ds = ds.transpose('y', 'x', 'level', 'validate', 'basedate')

        self.ds = ds
        self.ds.attrs.update(specific_comb_attributes)



# def _check_if_datasets_are_unique(FaDatasets):


def _check_lists_are_equal(list_a, list_b):
    return set(list_a) == set(list_b)