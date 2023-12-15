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
from .modules.describe_module import describe_fa_from_json

main_path = os.path.dirname(__file__)

def setup_shell_command():
    from .modules import setup_shell_commands


def _get_fa_metadata(fa_filepath, fieldsdf=None,
                     tmpdir=None, rm_tmpdir=True):

    if not IO.check_file_exist(fa_filepath):
        sys.exit(f'{fa_filepath} is not a file.')

    # create at tmpdir if not provided
    if tmpdir is None:
        tmpdir = IO.create_tmpdir(location=os.getcwd())

    # Get all available fields
    if fieldsdf is None:
        fieldsdf=get_fieldnames(fa_filepath=fa_filepath,
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


def describe_fa(fa_filepath, tmpdir=None, rm_tmpdir=True):

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
    TODO update


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
    return (fieldname.upper() in [f.upper().strip() for f in fielddf['name']])



def _list_3d_fieldnames(fielddf):
    # find 3d fieldnames in the fielddf
    basis_3d_names = list(set([f[4:] for f in fielddf['name'] if ((f.startswith('S')) & (f[1:3].isnumeric()))]))
    return basis_3d_names


def find_3d_fieldname(fielddf, fieldname):
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
# To Xarray convertors
# =============================================================================

def get_2d_field(fa_filepath, fieldname, fieldnamesdf=None,
                 reproj=True, target_crs='EPSG:4326',
                 tmpdir=None, rm_tmpdir=True):
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

    fieldname = str(fieldname).upper() #format to capital letters
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
    d3_fieldname, exist = find_3d_fieldname(fielddf=fieldnamesdf,
                                            fieldname=fieldname)
    if not exist:
        if rm_tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(f'A 3D version of {fieldname} is not found in the FA file: {fa_filepath} \n {_list_3d_fieldnames(fieldnamesdf)}')


    # Run Rscript to generete json files with data and meta info
    r_script = os.path.join(main_path, 'modules', 'rfa_scripts', 'get_field.R')
    subprocess.call(["/usr/bin/Rscript", r_script,
                     fa_filepath, d3_fieldname, '3dfield', tmpdir])


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



# def _Fa_to_json(fafile, fieldname):
#     """
#     This function will launch an R script, that uses Rfa to extract a field from an FA file.
#     The data is writen to a json, that is temporarely stored in a tmp folder.

#     The return are the paths to relevant locations (json files and tmp folder).


#     Parameters
#     ----------
#     fafile : Str
#         Path to the FA-file.
#     fieldname : Str
#         Name of the spatial field to extract from the FA file.

#     Returns
#     -------
#     json_path : Str
#         Path to the json containing the data.
#     fields_json_path : Str
#         Path to the json containing the available fields in the FA file.
#     tmpdir : Str
#         Path of the temp direcotry where the jsons are stored.

#     """

#     # 1  create tmp workdir
#     tmpdir = IO.create_tmpdir(location=os.getcwd()) #create a temporary (unique) directory


#     # Launch Rfa to convert FA to json
#     r_script = os.path.join(main_path, 'modules', 'Fa_to_file.R')

#     #Locate the R bin on your system and lauch the Rscript
#     rbin = get_rbin()
#     subprocess.call([os.path.join(rbin, 'Rscript'), r_script, fafile, fieldname, tmpdir])



#     # =============================================================================
#     # Paths to output
#     # =============================================================================

#     json_data_path = os.path.join(tmpdir, 'FAdata.json')
#     json_metadata_path = os.path.join(tmpdir, 'FAmetadata.json')
#     fields_json_path = os.path.join(tmpdir, 'fields.json')

#     return json_data_path, json_metadata_path, fields_json_path, tmpdir





# def FA_to_Xarray(fa_filepath, fieldname='SFX.T2M', target_crs='EPSG:4326'):
#     """
#     This function imports a field from an FA file into an Xarray.DataArray. If needed,
#     the data is reprojected to another CRS.

#     Parameters
#     ----------
#     fa_filepath : Str
#         Path to the FA-file.
#     fieldname : TYPE, optional
#         Name of the spatial field to extract from the FA file. The default is 'SFX.T2M'.
#     target_crs : Str, optional
#         EPSG identifier for the target CRS. The data will be reprojected to this if needed. The default is 'EPSG:4326'.

#     Returns
#     -------
#     data : Xarray.DataArray
#         A DataArray containing the data in the target_crs. Meta data + CRS info is added to the data.attrs.

#     """

#     json_data_path, json_metadata_path, fields_json_path, tmpdir = _Fa_to_json(fafile=fa_filepath,
#                                                                                fieldname=fieldname)



#     # =============================================================================
#     # Test if field exists
#     # =============================================================================

#     fieldexists=to_xarray._field_exists(fieldname=fieldname,
#                                         field_json_path=fields_json_path)
#     if not fieldexists:
#         print(f'{fieldname} not found in {fa_filepath}.')

#         # # print available fields
#         fieldsdf = IO.read_json(jsonpath=fields_json_path,
#                                 to_dataframe=True)
#         n = 10
#         print(f'A total of {fieldsdf.shape[0]} fiels are found, here are the first {n}: \n')
#         print(fieldsdf['name'].to_list()[:n])
#         print('To list all fields, use the -d (--describe) argument.')

#         shutil.rmtree(tmpdir)
#         sys.exit(f'{fieldname} not found in {fa_filepath}.')

#     # =============================================================================
#     # Make xarray from json
#     # =============================================================================

#     reproj_bool = True

#     data = to_xarray.json_to_rioxarray(json_data_path=json_data_path,
#                                        json_metadata_path=json_metadata_path,
#                                        reproject=reproj_bool,
#                                        target_epsg=target_crs)

#     shutil.rmtree(tmpdir)
#     return data