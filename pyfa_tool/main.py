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
    * -p, --plot (make as spatial plot of an FA file.)
    * -d, --describe (print out information of a FA file.)
    * -c, -- convert (convert a FA file to netCDF)""",

                                     epilog='''
                                                Add kwargs as you like as arguments. The position of these arguments is not of importance.
                                                These will be added to the plot functions (matplotlib).
                                                Example: .... vmin=288 vmax=294 cmap=?? ... '''
                                     )

    parser.add_argument("file", help="FA filename of path.", default='') #argument without prefix

    # Which mode arguments
    parser.add_argument('-p', '--plot', help='Make as spatial plot.',
                        default=True, action='store_true')
    parser.add_argument('-d', '--describe', help='Print out overview info of the FA file',
                        default=False, action='store_true')
    parser.add_argument('-c', '--convert', help='Convert a FA file to netCDF',
                        default=False, action='store_true')




    parser.add_argument("--print_fields", help="print available fields",
                        default=False, action="store_true")
    parser.add_argument("-f", "--file", help="FA filename of path.", default='')
    parser.add_argument("--field", help="fieldname", default='SFX.T2M')
    # parser.add_argument("--get_fieldnames", help="Write fieldnames to a file in the cwd.",
    #                     default=False, action="store_true")

    parser.add_argument("--proj", help="Reproject to this crs (ex: EPSG:4326)", default='EPSG:4326')



    parser.add_argument("--save", help="Save plot to file",
                        default=False, action='store_true')

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
    from modules import to_xarray, plotting, IO, describe
    import subprocess
    import matplotlib.pyplot as plt


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

    assert IO.check_file_exist(fa_file), f'{args.file} not found.'


    # =============================================================================
    # Convert FA to json
    # =============================================================================

    # 1  create tmp workdir
    tmpdir = IO.create_tmpdir(location=os.getcwd()) #create a temporary (unique) directory
    # Launch Rfa to convert FA to json
    r_script = os.path.join(main_path, 'modules', 'Fa_to_file.R')
    subprocess.call(["/usr/bin/Rscript", r_script, fa_file, args.field, tmpdir])

    # =============================================================================
    # Paths to output
    # =============================================================================
    json_data_path = os.path.join(tmpdir, 'FAdata.json')
    json_metadata_path = os.path.join(tmpdir, 'FAmetadata.json')
    fields_json_path = os.path.join(tmpdir, 'fields.json')





    # # =============================================================================
    # # Write fieldnames info to file if needed
    # # =============================================================================

    # if args.get_fieldnames:
    #     # fieldnames json is alway created, convert them to csv and write in cwd
    #     all_fields_csv_path = os.path.join(os.getcwd(), 'fieldnames.csv')
    #     fielddata = IO.read_json(jsonpath=fields_json_path,
    #                              to_dataframe=True)
    #     IO.write_to_csv(fielddata, all_fields_csv_path)
    #     print(f'All available fields are writen to {all_fields_csv_path}.')






    # =============================================================================
    # Describe mode
    # =============================================================================
    if args.describe:
        describe.describe_fa_from_json(metadatajson_path=json_metadata_path,
                                       fieldsjson_path=fields_json_path)

    # =============================================================================
    # Make xarray from json
    # =============================================================================
    if (args.plot | args.convert):

        # =============================================================================
        # Test if field exists
        # =============================================================================
        print(f'args fieldname: {args.field}')
        fieldexists=to_xarray._field_exists(fieldname=args.field,
                                            field_json_path=fields_json_path)
        if not fieldexists:
            print(f'{args.field} not found in {fa_file}.')

            # # print available fields
            fieldsdf = IO.read_json(jsonpath=fields_json_path,
                                    to_dataframe=True)
            n = 10
            print(f'A total of {fieldsdf.shape[0]} fiels are found, here are the first {n}: \n')
            print(fieldsdf['name'].to_list()[:n])
            print('To list all fields, use the -d (--describe) argument.')

            shutil.rmtree(tmpdir)
            sys.exit(f'{args.field} not found in {fa_file}.')


        if args.proj == '':
            reproj_bool = False
        else:
            reproj_bool = True

        data = to_xarray.json_to_rioxarray(json_data_path=json_data_path,
                                           json_metadata_path=json_metadata_path,
                                           reproject=reproj_bool,
                                           target_epsg=args.proj)


        if args.plot:


            # =============================================================================
            # make plot
            # =============================================================================

            kwargs = IO.make_kwarg_dict(args.kwargs)

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

        else:
            # =============================================================================
            # Write to netCDF file
            # =============================================================================
            print('to netcdf --> TODO')

    # =============================================================================
    # Delete json data
    # =============================================================================

    shutil.rmtree(tmpdir)

