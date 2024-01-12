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

from pyfa_tool.dataset import FaFile, FaDataset



# def what_is_wrong(ds1, ds2):
#     for key in ds1.attrs.keys():
#         if key not in ds2.attrs.keys():
#             print(f'{key} not in ds2')

#         val1 = ds1.attrs[key]
#         val2 = ds1.attrs[key]

#         if val1 != val2:
#             print("values not equal: ")
#             print(f'val1: {val1}')
#             print(f'val2: {val2}')




class FaCollection():
    def __init__(self):
        self.ds = None


    def combine_by_validate(self, FaDatasets=[]):
        if len(FaDatasets) == 0:
            sys.exit('No FaDatasets are provided.')
        if len(FaDatasets) < 2:
            sys.exit(f'Only one FaDatasets is provided: {FaDatasets[0]}')


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
                       dim='validate',
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





def _check_lists_are_equal(list_a, list_b):
    return set(list_a) == set(list_b)