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

    parser.add_argument("file", help="FA filename of path.", default='')  # argument without prefix

    # Which mode arguments
    parser.add_argument('-p', '--plot', help='Make as spatial plot of a 2D field.',
                        default=True, action='store_true')
    parser.add_argument('-d', '--describe', help='Print out overview info of the FA file',
                        default=False, action='store_true')
    parser.add_argument('-c', '--convert', help='Convert a FA file to netCDF',
                        default=False, action='store_true')

    parser.add_argument("--print_fields", help="print available fields",
                        default=False, action="store_true")
    # parser.add_argument("-f", "--file", help="FA filename of path.", default='')
    parser.add_argument("--field", help="fieldname", default='SFX.T2M')
    parser.add_argument("--proj", help="Reproject to this crs (ex: EPSG:4326)", default='') #default no reproj

    # parser.add_argument("--save", help="Save plot to file",
    #                     default=False, action='store_true')
    parser.add_argument('kwargs', help='Extra arguments passed to the plot function.', nargs='*')

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
    from pathlib import Path

    # =============================================================================
    # Check arguments
    # =============================================================================

    assert args.file != "", 'No file specified in arguments.'

    # =============================================================================
    # Create kwargs
    # =============================================================================

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False


    kwarg_list_str = args.kwargs
    kwargs = {}

    for kwargstr in kwarg_list_str:
        key=kwargstr.split('=')[0]
        val=kwargstr.split('=')[1]
        if is_number(val):
            val = float(val)

        kwargs[key] = val



    # =============================================================================
    # Forming the path
    # =============================================================================

    fa_file = str(args.file)
    if not os.path.isfile(fa_file):
        # test if relative path is given
        fa_file = os.path.join(os.getcwd(), args.file)

    assert pyfa.modules.IO.check_file_exist(fa_file), f'{args.file} not found.'


    # =============================================================================
    # Describe mode
    # =============================================================================
    if args.describe:
        FA = pyfa.FaFile(fa_file)
        FA.describe()

    # =============================================================================
    # Plot (2d) mode
    # =============================================================================

    if args.plot:
        ds = pyfa.FaDataset(fa_file) #Create dataset

        if args.proj == '':
            reproj_bool = False
        else:
            reproj_bool = True

        # import the 2d field
        ds.import_2d_field(fieldname=str(args.field),
                           rm_tmpdir=True,
                           reproj=reproj_bool,
                           target_epsg=args.proj,
                           nodata=-999)

        # plot the 2d field
        ds.plot(variable=str(args.field),
                **kwargs)
        plt.show()

    # =============================================================================
    # Convert to netCDF mode
    # =============================================================================
    if args.convert:
        ds = pyfa.FaDataset(fa_file) #Create dataset

        # Write to netCDF file
        target_dir = str(Path(fa_file).parent)
        target_file = str(Path(fa_file).stem) + '.nc'

        # import all field
        ds.import_fa(**kwargs)

        # save to nc
        ds.save_nc(outputfolder=target_dir,
                   filename=target_file,
                   )
