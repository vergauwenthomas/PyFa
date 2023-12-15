#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of functions for reading/writing/copying/... files


@author: thoverga
"""
import os
import json
import string
import random
import pandas as pd



# =============================================================================
# Creating/chekking paths
# =============================================================================

def check_file_exist(filepath):
    """Check if a filepath exists."""
    return os.path.isfile(filepath)

def create_tmpdir(location, tmpdir_name='tmp_fajson'):
    """
    Create a new (temporary) directory in the location, that serves as a cache.

    tmpdir_name is used as the direcotry name, if this directory already exists,
    then some random characters are appended to the name until the tmdir_name
    is not any existing direcotry.

    Parameters
    ----------
    location : str
        Path to the location where to create a new directory.
    tmpdir_name : str, optional
        Name of the direcory. Random chars are appended as long as the folder
        exists. The default is 'tmp_fajson'.

    Returns
    -------
    tmpdir_path : str
        Path to the created directory.

    """
    tmpdir_path = os.path.join(location, tmpdir_name)
    tmpdir_available = False
    while tmpdir_available == False:
        if os.path.exists(tmpdir_path):  # Do not overwrite if this dir exists already
            # add some random characters if the directory exists
            tmpdir_path += ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        else:
            tmpdir_available = True

    os.makedirs(tmpdir_path)
    return tmpdir_path

# =============================================================================
# Kwargs handling
# =============================================================================

def make_kwarg_dict(kwargstring):
    seperators = ['=', ':']

    kwa_dict = {}
    for item in kwargstring:
        for sep in seperators:
            kwarg_item = item.split(sep)
            if len(kwarg_item) == 2:
                break

        # check if argument is numeric
        key, value = kwarg_item[0], kwarg_item[1]
        if value.isnumeric():
            value=float(value)
        kwa_dict[key] = value

    return kwa_dict


# =============================================================================
# Json IO
# =============================================================================

def read_json(jsonpath, to_dataframe=False):
    f = open(jsonpath)
    data = json.load(f)
    f.close()

    if to_dataframe:
        data = pd.DataFrame(data)
    return data


# =============================================================================
# tabular data IO
# =============================================================================

def write_to_csv(data, filepath):
    if isinstance(data, type(pd.DataFrame)):
        data.to_csv(filepath, index=False)
    else:
        data = pd.DataFrame(data)
        data.to_csv(filepath,  index=False)



