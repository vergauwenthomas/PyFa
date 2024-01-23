#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 16:29:28 2023

@author: thoverga
"""


import os
import sys
import shutil
import argparse

main_path = os.path.dirname(__file__)
sys.path.append(main_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='PyFA-tool',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
PyFA: a tool for scientist working with ACCORD-FA files.
--------------------------------------------------------

The following functionality is available:
    * -p, --plot (make as spatial plot of an 2D field.)
    * -d, --describe (print out information of a FA file.)
    * -c, -- convert (convert a FA file to netCDF)""",

                                     epilog='''
                                                Add kwargs as you like as arguments. The position of these arguments is not of importance.
                                                These will be added to the plot functions (matplotlib).
                                                Example: .... vmin=288 vmax=294 cmap=?? ... '''
                                     )

    parser.add_argument("file", help="FA filename, path of FA file or similar regex expression on filenames.", default='')  # argument without prefix

    # Which mode arguments
    parser.add_argument('-p', '--plot', help='Make as spatial plot of a 2D field.',
                        default=True, action='store_true')
    parser.add_argument('-d', '--describe', help='Print out overview info of the FA file',
                        default=False, action='store_true')
    parser.add_argument('-c', '--convert', help='Convert to netCDF',
                        default=False, action='store_true')

    parser.add_argument('--whitelist', help='list of fieldnames to read (seperated by ,). If emtpy, all fields are read.',
                        default='')

    parser.add_argument("--combine_by_validate", help="If file is a regex expression, matching multiple FA files, they are combined on the validate dimension if True.",
                        default=True, action="store_true")

    default_2dfieldname = 'SFX.T2M'
    parser.add_argument("--field", help="fieldname", default=default_2dfieldname)
    parser.add_argument("--proj", help="Reproject to this crs (ex: EPSG:4326)", default='') #default no reproj

    parser.add_argument('kwargs', help='Extra arguments passed to the plot function. (must follow directly the file argurment, and as last arg)', nargs='*')

    args = parser.parse_args()

    # =============================================================================
    # Setup PyFA mode
    # =============================================================================
    if (args.describe | args.convert):
        # no plotting when describing or converting
        args.plot = False

    # Check if mode is unique
    _selected = [count for count in [args.plot, args.describe, args.convert] if count is True]
    if len(_selected) > 1:
        sys.exit("Select either one of --plot, --describe or --convert.")
    if len(_selected) == 0:
        # Because of default true for plot this should never be triggered.
        sys.exit("Select either one of --plot, --describe or --convert.")

    # =============================================================================
    # Import required modules (so they are not loaded with --help)
    # =============================================================================
    import pyfa_tool as pyfa
    # from pyfa_tool.modules import plotting
    import matplotlib.pyplot as plt
    import numpy as np
    from pathlib import Path


    # =============================================================================
    # Check arguments
    # =============================================================================

    assert args.file != "", 'No file specified in arguments.'

    #construct whitelist
    whitelist = args.whitelist
    if whitelist != "":
        whitelist = str(args.whitelist).replace(' ', '').split(',')
    else:
        whitelist = []

    # =============================================================================
    # Create kwargs
    # =============================================================================

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    #attention: If a regex expression is given as filename, the first match is set to the
    # args.file and the others are set to the kwargs !!! So the kwargs are a list with
    #matching filenames and method kwargs that have the = symbol in them.

    #So split the method kwargs from the filename regexes


    kwarg_list_str = args.kwargs
    kwargs = {}

    matching_paths = []

    for kwargstr in kwarg_list_str:
        #1. check if kwargstr has the = sighn in it, if so add in to the methodkwargs
        if '=' in str(kwargstr):
            key=kwargstr.split('=')[0]
            val=kwargstr.split('=')[1]
            if is_number(val):
                val = float(val)

            kwargs[key] = val
        #2. test if the kwargstr represent a filename
        else:
            testfilepath = os.path.join(os.getcwd(), str(kwargstr))
            if os.path.isfile(testfilepath):
                matching_paths.append(testfilepath)
            else:
                print(f'WARNING: {kwargstr} is skipped as kwarg since it is not formatted with a "=" character.')

    # add the file arg to the list of file_matches if there are filematches
    if bool(matching_paths):
        matching_paths.insert(0, os.path.join(os.getcwd(), str(args.file)))
        is_fafile=False #True for a single FA file, false for a pointer to multiple FA files
    else:
        is_fafile=True


    # =============================================================================
    # Forming the path
    # =============================================================================
    if is_fafile:
        file_expr = str(args.file)
        # 1. Check if argument is the path to a file --> use this if True
        if os.path.isfile(file_expr):
            fa_file = file_expr

        # 2. Check if argument is the name of a single Fafile in the cwd --> use this if True
        elif (os.path.isfile(os.path.join(os.getcwd(), file_expr))):
            fa_file = os.path.join(os.getcwd(), file_expr)

        else:
            sys.exit(f'{file_expr} is not found.')



    # Sanity checks
    if is_fafile:
        assert pyfa.modules.IO.check_file_exist(fa_file), f'{file_expr} not found.'

    else:
        assert len(matching_paths) > 0, f'No file candidates found for by searching candidates on {file_expr}'

    #if regext matches only one Fafile, interpret is as a single Fafile
    if (not is_fafile):
        if (len(matching_paths) == 1):
            print('WARNING: only a single file matches the {file_expr} expression, so interpret it as a single FA-file: {matching_paths[0]}')
            fa_file = matching_paths[0]
            is_fafile=True
            assert pyfa.modules.IO.check_file_exist(fa_file), f'{file_expr} not found.' #Overkill?


    if np.array(['whitelist' in faP for faP in matching_paths]).any():
        print("WARNING: could it be that you added a whitelist without the '--' prefix?")


    # =============================================================================
    # Describe mode
    # =============================================================================
    if args.describe:
        if is_fafile:
            FA = pyfa.FaFile(fa_file)
            FA.describe()
        else:
            sys.exit('Describe is not implemented for multiple FA-files.')


    # =============================================================================
    # Plot (2d) mode
    # =============================================================================

    if args.plot:
        if is_fafile:
            ds = pyfa.FaDataset(fa_file, nodata=-999) #Create dataset

            if args.proj == '':
                reproj_bool = False
            else:
                reproj_bool = True

            if ((len(whitelist)==1) & (str(args.field) == default_2dfieldname)):
                d2fieldname = whitelist[0]
            else:
                d2fieldname = str(args.field)

            # import the 2d field
            ds.import_2d_field(fieldname=d2fieldname,
                               rm_tmpdir=True,
                               reproj=reproj_bool,
                               target_epsg=args.proj,
                               )
            print(ds)
            # plot the 2d field
            ds.plot(variable=d2fieldname,
                    **kwargs)
            plt.show()
        else:
            sys.exit('Plot is not implemented for multiple FA-files.')


    # =============================================================================
    # Convert to netCDF mode
    # =============================================================================
    if args.convert:

        #construct arguments to pass to FaDataset import Fa methods
        if args.proj == '':
            reproj_bool = False
        else:
            reproj_bool = True

        trg_epsg = args.proj
        whitelist = whitelist
        blacklist=[]

        if is_fafile:
            ds = pyfa.FaDataset(fa_file) #Create dataset

            # Write to netCDF file
            target_dir = str(Path(fa_file).parent)
            target_file = str(Path(fa_file).stem) + '.nc'

            # import all field
            ds.import_fa(whitelist=whitelist,
                         blacklist=blacklist,
                         reproj=reproj_bool,
                         target_epsg=trg_epsg)

            # save to nc
            ds.save_nc(outputfolder=target_dir,
                       filename=target_file,
                       )
        else:
            if args.combine_by_validate:

                col = pyfa.FaCollection() # 1. init colleciton
                # 2: set Fadatasets
                datasets = []
                for fafilepath in matching_paths:
                    ds = pyfa.FaDataset(fafilepath) #Create dataset
                    # import all field
                    ds.import_fa(whitelist=whitelist,
                                 blacklist=blacklist,
                                 reproj=reproj_bool,
                                 target_epsg=trg_epsg)
                    datasets.append(ds)

                col.set_fadatasets(FaDatasets=datasets)

                # 3: combine by validate
                col.combine_by_validate()

                # 4. save to nc
                target_file = f"collection.nc"
                col.save_nc(outputfolder=os.getcwd(),
                           filename=target_file,
                           )

            else:
                sys.exit('In the CLI only the "combine by validate" combinatin technique is implented for a colleciton of FA-files.')

