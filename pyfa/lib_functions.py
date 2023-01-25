#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for using pyfa as a python library

Created on Tue Jan 24 17:11:14 2023

@author: thoverga
"""
import os
import subprocess
import shutil


from .modules import IO, to_xarray

main_path = os.path.dirname(__file__)

def setup_shell_command():
    from .modules import setup_shell_commands
    
    
def get_fieldnames():
    print('TODO')
    
def FA_to_Xarray(fa_filepath, fieldname='SFX.T2M', target_crs='EPSG:4326'):
    
    # 1  create tmp workdir
    tmpdir = os.path.join(os.getcwd(), 'tmp_fajson')
    tmpdir_available = False
    while tmpdir_available == False:
        if os.path.exists(tmpdir):  # Do not overwrite if this dir exists already
            tmpdir += '_a'
        else:
            tmpdir_available = True
    
    os.makedirs(tmpdir)
    

    # Launch Rfa to convert FA to json
    r_script = os.path.join(main_path, 'modules', 'Fa_to_file.R')
    subprocess.call(["/usr/bin/Rscript", r_script, fa_filepath, fieldname, tmpdir])
    
    # =============================================================================
    # Paths to output
    # =============================================================================
    json_path = os.path.join(tmpdir, 'FAdata.json')
    fields_json_path = os.path.join(tmpdir, 'fields.json')
    
    # =============================================================================
    # Write fieldnames info to file if needed
    # =============================================================================
    
    # if args.get_fieldnames:
    #     # fieldnames json is alway created, convert them to csv and write in cwd
    #     all_fields_csv_path = os.path.join(os.getcwd(), 'fieldnames.csv')
    #     fielddata = IO.read_json(jsonpath=fields_json_path,
    #                              to_dataframe=True)
    #     IO.write_to_csv(fielddata, all_fields_csv_path)
    #     print(f'All available fields are writen to {all_fields_csv_path}.')
    
    # =============================================================================
    # check if json file is created
    # =============================================================================
    
    if not os.path.isfile(json_path):
        print(f'{fieldname} not found in {fa_filepath}.')
    
        # print available fields
        fieldsdf = IO.read_json(jsonpath=fields_json_path,
                                to_dataframe=True)
    
        if fieldsdf.shape[0] > 100:
            fieldsdf = fieldsdf[0:100]
            print(
                f'There are {fieldsdf.shape[0]} stored in the {fa_filepath}. Here are the first 100 fields:')
        else:
            print(f'There are {fieldsdf.shape[0]} stored in the {fa_filepath}:')
        print(fieldsdf)
        print('To list all fields, add the --get_fieldnames argument so that all fieldnames will be writen to file.')
    
    
        #TODO: define errors
        shutil.rmtree(tmpdir)
        # sys.exit(f'{fieldname} not found in {fa_filepath}.')
        return None
    
    # =============================================================================
    # Make xarray from json
    # =============================================================================
   
    reproj_bool = True
    
    data = to_xarray.json_to_rioxarray(json_path=json_path,
                                       reproject=reproj_bool,
                                       target_epsg=target_crs)
    return data