#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 16:29:28 2023

@author: thoverga
"""

from modules import to_xarray, plotting, IO
import os
import sys
import shutil
import argparse
import json

import subprocess
import xarray
import matplotlib.pyplot as plt

main_path = os.path.dirname(__file__)
sys.path.append(main_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='FA plotting as a python wrapper',
                                     epilog='''
                                                Add kwargs as you like as arguments. The position of these arguments is not of importance.
                                                These will be added to the plot functions (matplotlib).
                                                Example: .... vmin=288 vmax=294 cmap=?? ... '''
                                     )

    parser.add_argument("file", help="FA filename of path.", default='') #argument without prefix

    # parser.add_argument("-p", "--plot", help="Make plot",
    #                     default=True, action="store_true")
    parser.add_argument("--print_fields", help="print available fields",
                        default=False, action="store_true")
    parser.add_argument("-f", "--file", help="FA filename of path.", default='')
    parser.add_argument("--field", help="fieldname", default='SFX.T2M')
    parser.add_argument("--get_fieldnames", help="Write fieldnames to a file in the cwd.",
                        default=False, action="store_true")

    parser.add_argument("--proj", help="Reproject to this crs (ex: EPSG:4326)", default='EPSG:4326')



    parser.add_argument("--save", help="Save plot to file",
                        default=False, action='store_true')

    parser.add_argument('kwargs', help='Extra arguments passed to the plot function.', nargs='*')

    args = parser.parse_args()

    # =============================================================================
    # Check arguments
    # =============================================================================

    assert args.file != "", 'No file specified in arguments.'

    # =============================================================================
    # Forming the path
    # =============================================================================

    fa_file = str(args.file)
    if not os.path.isfile(fa_file):
        # test if relative path is given
        fa_file = os.path.join(os.getcwd(), args.file)

    assert os.path.isfile(fa_file), f'{args.file} not found.'


    # =============================================================================
    # Convert FA to json
    # =============================================================================

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
    subprocess.call(["/usr/bin/Rscript", r_script, fa_file, args.field, tmpdir])

    # =============================================================================
    # Paths to output
    # =============================================================================
    json_path = os.path.join(tmpdir, 'FAdata.json')
    fields_json_path = os.path.join(tmpdir, 'fields.json')

    # =============================================================================
    # Write fieldnames info to file if needed
    # =============================================================================

    if args.get_fieldnames:
        # fieldnames json is alway created, convert them to csv and write in cwd
        all_fields_csv_path = os.path.join(os.getcwd(), 'fieldnames.csv')
        fielddata = IO.read_json(jsonpath=fields_json_path,
                                 to_dataframe=True)
        IO.write_to_csv(fielddata, all_fields_csv_path)
        print(f'All available fields are writen to {all_fields_csv_path}.')


    # =============================================================================
    # check if json file is created
    # =============================================================================

    if not os.path.isfile(json_path):
        print(f'{args.field} not found in {fa_file}.')

        # print available fields
        fieldsdf = IO.read_json(jsonpath=fields_json_path,
                                to_dataframe=True)

        if fieldsdf.shape[0] > 100:
            fieldsdf = fieldsdf[0:100]
            print(
                f'There are {fieldsdf.shape[0]} stored in the {fa_file}. Here are the first 100 fields:')
        else:
            print(f'There are {fieldsdf.shape[0]} stored in the {fa_file}:')
        print(fieldsdf)
        print('To list all fields, add the --get_fieldnames argument so that all fieldnames will be writen to file.')

        shutil.rmtree(tmpdir)
        sys.exit(f'{args.field} not found in {fa_file}.')


    # =============================================================================
    # Make xarray from json
    # =============================================================================
    if args.proj == '':
        reproj_bool = False
    else:
        reproj_bool = True

    data = to_xarray.json_to_rioxarray(json_path=json_path,
                                       reproject=reproj_bool,
                                       target_epsg=args.proj)

    # =============================================================================
    # Delete json data
    # =============================================================================

    shutil.rmtree(tmpdir)


    # =============================================================================
    # Check for plotting kwargs
    # =============================================================================
    kwargs = IO.make_kwarg_dict(args.kwargs)


    # =============================================================================
    # make plot
    # =============================================================================


    if args.save:
        # make output filepath
        origin = data.attrs['origin']
        if origin[-4:] == '.sfx':
            filename = f'{origin[:-4]}_{args.field}.png'
        elif origin[-3:] == '.FA':
            filename = f'{origin[:-3]}_{args.field}.png'
        else:
            filename = f'{origin}_{args.field}.png'

        filepath = os.path.join(os.getcwd(), filename)



    fig, axs = plotting.make_fig()
    plotting.make_plot(dxr=data,
                       ax=axs,
                       #TODO pass arguments as kwargs
                       **kwargs
                       )

    if args.save:
        plotting.save_plot(fig=fig, filepath=filepath, fmt='png')


    plt.show()
