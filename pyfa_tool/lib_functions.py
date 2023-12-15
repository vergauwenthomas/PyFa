#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for using pyfa as a python library

Created on Tue Jan 24 17:11:14 2023

@author: thoverga
"""
import os, sys
import subprocess
import shutil


from .modules import IO, to_xarray

main_path = os.path.dirname(__file__)

def setup_shell_command():
    from .modules import setup_shell_commands


def get_fields(fa_filepath):
    """
    Get all the fields from an FA file.

    Parameters
    ----------
    fa_filepath : Str
        Path to the FA-file.

    Returns
    -------
    fielddata : pandas.DataFrame
        Available fields information.

    """

    _json_data_path, _json_metadata_path, fields_json_path, tmpdir = _Fa_to_json(fafile=fa_filepath,
                                                                                fieldname='_dummy')


    fielddata = IO.read_json(jsonpath=fields_json_path, to_dataframe=True)

    shutil.rmtree(tmpdir)
    return fielddata



def get_rbin():
    """Funtion to extract the Rbin of your environment"""
    #Write very simple R script in curdir
    r_miniscript = os.path.join(os.getcwd(), 'mini_R_script.R')
    with open(r_miniscript, 'w') as f:
        f.write('R.home("bin")')


    #Execure script and extract the rbin
    result = subprocess.run(['Rscript', r_miniscript], capture_output=True, text=True)
    rbin = result.stdout.split('"')[1]


    #Delete basic r script

    try:
        os.remove(r_miniscript)
    except OSError:
        pass

    return rbin



def _Fa_to_json(fafile, fieldname):
    """
    This function will launch an R script, that uses Rfa to extract a field from an FA file.
    The data is writen to a json, that is temporarely stored in a tmp folder.

    The return are the paths to relevant locations (json files and tmp folder).


    Parameters
    ----------
    fafile : Str
        Path to the FA-file.
    fieldname : Str
        Name of the spatial field to extract from the FA file.

    Returns
    -------
    json_path : Str
        Path to the json containing the data.
    fields_json_path : Str
        Path to the json containing the available fields in the FA file.
    tmpdir : Str
        Path of the temp direcotry where the jsons are stored.

    """

    # 1  create tmp workdir
    tmpdir = IO.create_tmpdir(location=os.getcwd()) #create a temporary (unique) directory


    # Launch Rfa to convert FA to json
    r_script = os.path.join(main_path, 'modules', 'Fa_to_file.R')

    #Locate the R bin on your system and lauch the Rscript
    rbin = get_rbin()
    subprocess.call([os.path.join(rbin, 'Rscript'), r_script, fafile, fieldname, tmpdir])



    # =============================================================================
    # Paths to output
    # =============================================================================

    json_data_path = os.path.join(tmpdir, 'FAdata.json')
    json_metadata_path = os.path.join(tmpdir, 'FAmetadata.json')
    fields_json_path = os.path.join(tmpdir, 'fields.json')

    return json_data_path, json_metadata_path, fields_json_path, tmpdir





def FA_to_Xarray(fa_filepath, fieldname='SFX.T2M', target_crs='EPSG:4326'):
    """
    This function imports a field from an FA file into an Xarray.DataArray. If needed,
    the data is reprojected to another CRS.

    Parameters
    ----------
    fa_filepath : Str
        Path to the FA-file.
    fieldname : TYPE, optional
        Name of the spatial field to extract from the FA file. The default is 'SFX.T2M'.
    target_crs : Str, optional
        EPSG identifier for the target CRS. The data will be reprojected to this if needed. The default is 'EPSG:4326'.

    Returns
    -------
    data : Xarray.DataArray
        A DataArray containing the data in the target_crs. Meta data + CRS info is added to the data.attrs.

    """

    json_data_path, json_metadata_path, fields_json_path, tmpdir = _Fa_to_json(fafile=fa_filepath,
                                                                               fieldname=fieldname)



    # =============================================================================
    # Test if field exists
    # =============================================================================

    fieldexists=to_xarray._field_exists(fieldname=fieldname,
                                        field_json_path=fields_json_path)
    if not fieldexists:
        print(f'{fieldname} not found in {fa_filepath}.')

        # # print available fields
        fieldsdf = IO.read_json(jsonpath=fields_json_path,
                                to_dataframe=True)
        n = 10
        print(f'A total of {fieldsdf.shape[0]} fiels are found, here are the first {n}: \n')
        print(fieldsdf['name'].to_list()[:n])
        print('To list all fields, use the -d (--describe) argument.')

        shutil.rmtree(tmpdir)
        sys.exit(f'{fieldname} not found in {fa_filepath}.')

    # =============================================================================
    # Make xarray from json
    # =============================================================================

    reproj_bool = True

    data = to_xarray.json_to_rioxarray(json_data_path=json_data_path,
                                       json_metadata_path=json_metadata_path,
                                       reproject=reproj_bool,
                                       target_epsg=target_crs)

    shutil.rmtree(tmpdir)
    return data