#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of functions for reading/writing/copying/... files


@author: thoverga
"""
import os
import sys
import json
import string
import random
import pandas as pd
import subprocess
import shutil
import fnmatch
import xarray as xr






# =============================================================================
# Creating/chekking paths/deleting
# =============================================================================

def check_file_exist(filepath):
    """Check if a filepath exists."""
    return os.path.isfile(filepath)

def check_folder_exist(folderpath):
    return os.path.isdir(folderpath)

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

def remove_tempdir(tmpdirpath):
    """
    Delete a folder and all its branches.

    Parameters
    ----------
    tmpdirpath : str
        The folder to delete.

    Returns
    -------
    None.

    """
    shutil.rmtree(tmpdirpath, ignore_errors=True)


def get_paths_using_regex(searchdir, filename_regex='*'):
    """
    Get all files, from inside searchdir, that match a regex expression (unix wildcard accepted).

    Parameters
    ----------
    searchdir : str
        The path of the directory to scan all files of.
    filename_regex : str, optional
        Regex expression for matching filenames. The default is '*'.

    Returns
    -------
    matching_paths : list
        A list of the matching file paths.

    """
    if not os.path.isdir(searchdir):
        sys.exit(f'{searchdir} is not a directory.')

    #Get all filenames
    files = os.listdir(searchdir)

    # Get matching filenames
    matching_files = fnmatch.filter(files, str(filename_regex))

    # construct paths
    matching_paths = [os.path.join(searchdir, f) for f in matching_files]

    return matching_paths



# =============================================================================
# Json IO
# =============================================================================

def read_json(jsonpath, to_dataframe=False):
    """
    Read a json file.


    Parameters
    ----------
    jsonpath : str
        Path of the json file.
    to_dataframe : bool, optional
        If True, the data is converted to a pandas.DataFrame, else a
        dictionary is returned. The default is False.

    Returns
    -------
    data : dict or pandas.DataFrame
        The data of the json file.

    """
    f = open(jsonpath)
    data = json.load(f)
    f.close()

    if to_dataframe:
        data = pd.DataFrame(data)
    return data

def write_json(datadict, jsonpath, force=False):
    """
    Write a dictionary to a json file.

    Parameters
    ----------
    datadict : dict
        The dictionary to write to file.
    jsonpath : str
        The path of the target json file.
    force : bool, optional
        If True, the jsonpath file (if it already exists) will be overwritten,
        else an error will be thrown. The default is False.

    Returns
    -------
    None.

    """
    if check_file_exist(jsonpath):
        if not force:
            sys.exit(f'{jsonpath} already exists.')
    with open(jsonpath, 'w') as f:
        json.dump(datadict, f)

# =============================================================================
# tabular data IO
# =============================================================================

# def write_to_csv(data, filepath):

#     if isinstance(data, type(pd.DataFrame)):
#         data.to_csv(filepath, index=False)
#     else:
#         data = pd.DataFrame(data)
#         data.to_csv(filepath,  index=False)


# =============================================================================
# OS R related
# =============================================================================
def _get_rbin():
    """Funtion to extract the Rbin of your environment"""
    # Write very simple R script in curdir
    r_miniscript = os.path.join(os.getcwd(), 'mini_R_script.R')
    with open(r_miniscript, 'w') as f:
        f.write('R.home("bin")')

    # Execure script and extract the rbin
    result = subprocess.run(['Rscript', r_miniscript], capture_output=True, text=True)
    rbin = result.stdout.split('"')[1]

    # Delete basic r script
    try:
        os.remove(r_miniscript)
    except OSError:
        pass

    return rbin


# =============================================================================
# netCDF related
# =============================================================================


def save_as_nc(xrdata, outputfolder, filename, overwrite=False, **kwargs):
    """
    Save an Xarray object to a NetCDF file.

    Parameters
    ----------
    xrdata : xarray.DataArray or xarray.DataSet
        The Xarray data object to save.
    outputfolder : str
        Path of the directory to save the NetCDF.
    filename : str
        Name of the netCDF file. (.nc extenstion is added if not provided.)
    overwrite : bool, optional
        If False, the xarray object is not saved if the netCDF file already
        exists. The default is False.
    **kwargs : optional
        kwargs are passed to the .to_netcdf() method of the xarray object.

    Returns
    -------
    None.

    """
    # check fileneme extension
    if not filename.endswith('.nc'):
        filename = filename + '.nc'

    # check if outputfolder exists
    if not check_folder_exist(outputfolder):
        sys.exit(f'{outputfolder} directory not found.')

    # check if file exist
    target_file = os.path.join(outputfolder, filename)
    if (check_file_exist(target_file) & (not overwrite)):
        sys.exit(f'{target_file} already exists.')

    # Remove file if ovrwrite is True
    if (check_file_exist(target_file) & (overwrite)):
        os.remove(target_file)

    # convert to nc
    xrdata.to_netcdf(path=target_file,
                      mode='w',
                      **kwargs)
    print(f'Data saved to {target_file}')
    return None


def read_netCDF(file, **kwargs):
    """
    Import a netCDF file into a xarray Dataset.

    Parameters
    ----------
    file : str
        Path of the netCDF file to import.
    **kwargs : optional
        kwargs are passed to the xarray.open_dataset() function.

    Returns
    -------
    ds : xr.DataSet
        The Dataset object of the netCDF file.

    """
    # Check if file exist
    if not check_file_exist(file):
        sys.exit(f'{file} does not exist.')

    ds = xr.open_dataset(file, **kwargs)

    return ds

