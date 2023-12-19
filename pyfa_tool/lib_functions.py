#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for using pyfa as a python library

Created on Tue Jan 24 17:11:14 2023

@author: thoverga
"""
import os
import sys
import subprocess
import shutil


from .modules import IO, to_xarray
from .modules.describe_module import describe_fa_from_json


main_path = os.path.dirname(__file__)


# =============================================================================
# CLI
# =============================================================================

def setup_shell_command():
    """
    When colling this function, the CLI PyFa is activated on your system.

    Returns
    -------
    None.

    Note
    -------
    Only support for UNIX and writing right on the .bashrc.

    """
    from .modules import setup_shell_commands

# =============================================================================
# Helpers
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


def _get_fa_metadata(fa_filepath, fieldsdf=None,
                     tmpdir=None, rm_tmpdir=True):
    """
    Get the list of metadata attributes of an FA file.

    The metadata is extracted by extracting a (dummy) field form the FA file.

    Parameters
    ----------
    fa_filepath : str
        The path of the FA file.
    fieldsdf : pandas.DataFrame, optional
        Available fields information in a Dataframe. If None, this will be
        extracted from the FA file. The default is None.
    tmpdir : str, optional
        The path to a temporary storage location for the json files. If None,
        a new temporary folder is created. The default is None.
    rm_tmpdir : bool, optional
        Wether to remove the temporary storage direction, with all its content (= json
        files) at the end of this function. The default is True.

    Returns
    -------
    metadata : list
        A list of metadata attributes (in dict form).

    """
    if not IO.check_file_exist(fa_filepath):
        sys.exit(f'{fa_filepath} is not a file.')

    # create at tmpdir if not provided
    if tmpdir is None:
        tmpdir = IO.create_tmpdir(location=os.getcwd())

    # Get all available fields
    if fieldsdf is None:
        fieldsdf = get_fieldnames(fa_filepath=fa_filepath,
                                tmpdir=tmpdir,
                                rm_tmpdir=False)

    # Select the first present field
    fieldname = fieldsdf['name'].iloc[0]

    # Run Rscript to generete a json file with meta info
    r_script = os.path.join(main_path, 'modules', 'rfa_scripts', 'get_field.R')
    subprocess.call(["/usr/bin/Rscript", r_script,
                     fa_filepath, fieldname, '2dfield', tmpdir])

    # check if json is created
    jsonpath = os.path.join(tmpdir, "FAmetadata.json")
    if not IO.check_file_exist(jsonpath):
        if rm_tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(f'Something went wrong in the execution of get_field.R, the file {jsonpath} is not found.')

    # Read the json file to a dataframe
    metadata = IO.read_json(jsonpath=jsonpath,
                            to_dataframe=False)

    if rm_tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return metadata


def _list_3d_fieldnames(fielddf):
    """
    Create a list of all basisfieldnames which occures at multiple levels.

    (The basisfieldname is the fieldname without the level identifier. So
     S012TEMPERATURE has TEMPERATURE as basisfieldname)

    Parameters
    ----------
    fielddf : pandas.DataFrame
        Available fields information in a Dataframe.

    Returns
    -------
    basis_3d_names : list
        List of basisnames for present 3D fields.

    """
    # find 3d fieldnames in the fielddf
    basis_3d_names = list(set([f[4:] for f in fielddf['name'] if ((f.startswith('S')) & (f[1:3].isnumeric()))]))
    return basis_3d_names


def _find_3d_fieldname(fielddf, fieldname):
    """
    Find the basisfieldname for a fieldname, and test if it is present.

    Parameters
    ----------
    fielddf : pandas.DataFrame
        Available fields information in a Dataframe.
    fieldname : str
        The fieldname to find the basisfieldname form of and to test if it is
        present.

    Returns
    -------
    basisfieldname : str
        The basisname fo the 3D field.
    bool
        Wether the basisfieldname is a present field.

    """
    fieldname = str(fieldname).upper()

    # find 3d fieldnames in the fielddf
    basis_3d_names = _list_3d_fieldnames(fielddf)

    # remove level indicater if present in fieldname
    if ((fieldname.startswith('S')) & (fieldname[1:3].isnumeric())):
        fieldname = fieldname[4:]

    if fieldname in basis_3d_names:
        return fieldname, True
    else:
        return fieldname, False


# =============================================================================
# User callabels
# =============================================================================


def describe_fa(fa_filepath, tmpdir=None, rm_tmpdir=True):
    """
    Print out an overview of the content (fields, validity, ... ) of an FA file.

    This is done by:
        * Extracting all fields from the FA file
        * Using an existing field, to extract the metadata from the FA.


    Parameters
    ----------
    fa_filepath : str
        The path of the FA file.
    tmpdir : str, optional
        The path to a temporary storage location for the json files. If None,
        a new temporary folder is created. The default is None.
    rm_tmpdir : bool, optional
        Wether to remove the temporary storage direction, with all its content (= json
        files) at the end of this function. The default is True.

    Returns
    -------
    None.

    """
    if not IO.check_file_exist(fa_filepath):
        sys.exit(f'{fa_filepath} is not a file.')

    # create at tmpdir if not provided
    if tmpdir is None:
        tmpdir = IO.create_tmpdir(location=os.getcwd())

    # Get all fields info
    fieldsdf = get_fieldnames(fa_filepath=fa_filepath,
                              tmpdir=tmpdir,
                              rm_tmpdir=False)

    # Get metadata
    metadata = _get_fa_metadata(fa_filepath=fa_filepath,
                                fieldsdf=fieldsdf,
                                tmpdir=tmpdir,
                                rm_tmpdir=False)

    # Call the describe function for formatted printing
    describe_fa_from_json(metadata=metadata,
                          fieldslist=fieldsdf.to_dict('records'))

    if rm_tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return None


def get_fieldnames(fa_filepath, tmpdir=None, rm_tmpdir=True):
    """
    Get all the fields information from an FA file.

    Parameters
    ----------
    fa_filepath : Str
        Path to the FA-file.
    tmpdir : str, optional
        The path to a temporary storage location for the json files. If None,
        a new temporary folder is created. The default is None.
    rm_tmpdir : bool, optional
        Wether to remove the temporary storage direction, with all its content (= json
        files) at the end of this function. The default is True.

    Returns
    -------
    fielddata : pandas.DataFrame
        Available fields information in a Dataframe.

    """
    if not IO.check_file_exist(fa_filepath):
        sys.exit(f'{fa_filepath} is not a file.')

    # create at tmpdir if not provided
    if tmpdir is None:
        tmpdir = IO.create_tmpdir(location=os.getcwd())

    # Run Rscript to generete a json file with all info
    r_script = os.path.join(main_path, 'modules', 'rfa_scripts', 'get_fieldnames.R')
    subprocess.call(["/usr/bin/Rscript", r_script, fa_filepath, tmpdir])

    # check if json is created
    jsonpath = os.path.join(tmpdir, 'fields.json')
    if not IO.check_file_exist(jsonpath):
        if rm_tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(f'Something went wrong in the execution of get_fieldnames.R, the file {jsonpath} is not found.')

    # Read the json file to a dataframe
    fielddata = IO.read_json(jsonpath=jsonpath,
                             to_dataframe=True)

    # Format the names
    fielddata['name'] = [f.strip() for f in fielddata['name']]

    if rm_tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return fielddata


def field_exists(fielddf, fieldname):
    """
    Test if a fieldname is present.

    Parameters
    ----------
    fielddf : pandas.DataFrame
        Available fields information in a Dataframe.
    fieldname : str
        The fieldname to test.

    Returns
    -------
    bool
        True if the fieldname is found, else False.

    """
    return (fieldname.upper() in [f.upper().strip() for f in fielddf['name']])


# =============================================================================
# To Xarray convertors
# =============================================================================


def get_2d_field(fa_filepath, fieldname, fieldnamesdf=None,
                 reproj=True, target_crs='EPSG:4326',
                 tmpdir=None, rm_tmpdir=True):
    """
    Imports a 2D- field from an FA file into an Xarray.DataArray.

    If needed the data is reprojected to another CRS.
    The fieldname provided is upper/lower case insensitive; it will be formatted.

    Parameters
    ----------
    fa_filepath : str
        The path of the FA file.
    fieldname : str
        The name of the 2D field to extract.
    fieldnamesdf : pandas.DataFrame, optional
        Available fields information in a Dataframe. If None, this will be
        extracted from the FA file. The default is None.
    reproj : bool, optional
        If True, the field will be reprojected by using the target_crs. The
        default is True.
    target_crs : str, optional
        EPSG code for the desired CRS of the xarray.DataArray. The default is
        'EPSG:4326'.
    tmpdir : str, optional
        The path to a temporary storage location for the json files. If None,
        a new temporary folder is created. The default is None.
    rm_tmpdir : bool, optional
        Wether to remove the temporary storage direction, with all its content (= json
        files) at the end of this function. The default is True.

    Returns
    -------
    data : xarray.DataArray
        The 2D field contained in a xarray object.
    """
    if not IO.check_file_exist(fa_filepath):
        sys.exit(f'{fa_filepath} is not a file.')

    # create at tmpdir if not provided
    if tmpdir is None:
        tmpdir = IO.create_tmpdir(location=os.getcwd())

    # Check if fieldname exists
    if fieldnamesdf is None:
        fieldnamesdf = get_fieldnames(fa_filepath=fa_filepath,
                                      tmpdir=tmpdir,
                                      rm_tmpdir=False)

    fieldname = str(fieldname).upper()  # format to capital letters
    if not field_exists(fielddf=fieldnamesdf, fieldname=fieldname):
        if rm_tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(f'{fieldname} not found in the FA file: {fa_filepath}')

    # Run Rscript to generete json files with data and meta info
    r_script = os.path.join(main_path, 'modules', 'rfa_scripts', 'get_field.R')
    subprocess.call(["/usr/bin/Rscript", r_script,
                     fa_filepath, fieldname, '2dfield', tmpdir])

    # check if json is created
    metadatapath = os.path.join(tmpdir, "FAmetadata.json")
    datapath = os.path.join(tmpdir, "FAdata.json")

    if (not IO.check_file_exist(metadatapath)) | (not IO.check_file_exist(datapath)):
        if rm_tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(f'Something went wrong in the execution of get_field.R, the files {metadatapath} and {datapath} are not found.')

    data = to_xarray.json_to_rioxarray(json_data_path=datapath,
                                       json_metadata_path=metadatapath,
                                       reproject=reproj,
                                       target_epsg=target_crs)
    if rm_tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return data


def get_3d_field(fa_filepath, fieldname, fieldnamesdf=None,
                 target_crs='EPSG:4326',
                 tmpdir=None, rm_tmpdir=True):
    """
    Imports a 3D-field from an FA file into an Xarray.DataArray.

    A 3D-field is a field which is present at multiple levels, or for which a
    level indicator is present in the fieldname. The vertical coordinates
    are model coordinates.

    If needed the data is reprojected to another CRS.
    The fieldname provided is upper/lower case insensitive and both
    basisfieldnames (i.g.TEMPERATURE) and fieldnames (i.g. S012TEMPERATURE)
    can be provided, it will be formatted accordingly.


    Parameters
    ----------
    fa_filepath : str
        The path of the FA file.
    fieldname : str
        The name of the 3D field to extract. Both basisfieldnames or equivalent
        2D fieldname or possible.
    fieldnamesdf : pandas.DataFrame, optional
        Available fields information in a Dataframe. If None, this will be
        extracted from the FA file. The default is None.
    reproj : bool, optional
        If True, the field will be reprojected by using the target_crs. The
        default is True.
    target_crs : str, optional
        EPSG code for the desired CRS of the xarray.DataArray. The default is
        'EPSG:4326'.
    tmpdir : str, optional
        The path to a temporary storage location for the json files. If None,
        a new temporary folder is created. The default is None.
    rm_tmpdir : bool, optional
        Wether to remove the temporary storage direction, with all its content (= json
        files) at the end of this function. The default is True.

    Returns
    -------
    data : xarray.DataArray
        The 3D field contained in a xarray object. The vertical coordinates are
        modellevels.

    """
    if not IO.check_file_exist(fa_filepath):
        sys.exit(f'{fa_filepath} is not a file.')

    # create at tmpdir if not provided
    if tmpdir is None:
        tmpdir = IO.create_tmpdir(location=os.getcwd())

    if fieldnamesdf is None:
        fieldnamesdf = get_fieldnames(fa_filepath=fa_filepath,
                                      tmpdir=tmpdir,
                                      rm_tmpdir=False)

    # Create a 3d fieldname and check if it exists
    d3_fieldname, exist = _find_3d_fieldname(fielddf=fieldnamesdf,
                                             fieldname=fieldname)
    if not exist:
        if rm_tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(f'A 3D version of {fieldname} is not found in the FA file: {fa_filepath} \n {_list_3d_fieldnames(fieldnamesdf)}')

    # Run Rscript to generete json files with data and meta info
    r_script = os.path.join(main_path, 'modules', 'rfa_scripts', 'get_field.R')
    subprocess.call(["/usr/bin/Rscript", r_script,
                     fa_filepath, d3_fieldname, '3dfield', tmpdir])

    # TODO: check if the rbin is required! If so use the following expression as example:
    # rbin is the output of _get_rbin()
    # subprocess.call([os.path.join(rbin, 'Rscript'), r_script, fafile, fieldname, tmpdir])

    # check if json is created
    metadatapath = os.path.join(tmpdir, "FAmetadata.json")
    datapath = os.path.join(tmpdir, "FAdata.json")

    if (not IO.check_file_exist(metadatapath)) | (not IO.check_file_exist(datapath)):
        if rm_tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(f'Something went wrong in the execution of get_field.R, the files {metadatapath} and {datapath} are not found.')

    data = to_xarray.json_to_rioxarray(json_data_path=datapath,
                                       json_metadata_path=metadatapath,
                                       reproject=True,
                                       target_epsg=target_crs)
    if rm_tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return data
