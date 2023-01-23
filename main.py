#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 16:29:28 2023

@author: thoverga
"""

import os, shutil
import argparse
import to_xarray
import subprocess
import xarray 
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='FA plotting')
parser.add_argument("-p","--plot", help="Make plot", default=True, action="store_true")
parser.add_argument("--print_fields", help="print available fields (T/F)", default=False, action="store_true")
parser.add_argument("--file", help="FA filename of path.", default='')
parser.add_argument("--field", help="fieldname", default='SFX.T2M')
parser.add_argument("--proj", help="Reproject to this crs (ex: epsg:4326)", default='EPSG:4326')
parser.add_argument("--save", help="Save plot to file", default=False, action='store_true')

args = parser.parse_args()

# =============================================================================
# Check arguments
# =============================================================================

assert args.file!="", 'No file specified in arguments.'

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

#1  create tmp workdir 
tmpdir=os.path.join(os.getcwd(),'tmp')
tmpdir_available=False
while tmpdir_available == False:
    if os.path.exists(tmpdir): #Do not overwrite if this dir exists already
        tmpdir += '_a'
    else:
        tmpdir_available=True

os.makedirs(tmpdir)

# Launch Rfa to convert FA to json
subprocess.call (["/usr/bin/Rscript", f'/home/thoverga/Documents/github/PyFa/Fa_to_file.R',fa_file, args.field, tmpdir])





# =============================================================================
# Make xarray from json
# =============================================================================
if args.proj == '':
    reproj_bool=False
else: 
    reproj_bool=True

data = to_xarray.json_to_rioxarray(json_path=os.path.join(tmpdir, 'FAdata.json'), 
                                   reproject=reproj_bool,
                                   target_epsg=args.proj)


# =============================================================================
# Delete json data
# =============================================================================

shutil.rmtree(tmpdir)

# =============================================================================
# make plot
# =============================================================================
print(data.attrs['origin'])
if args.save:
    # make output filepath
    origin = data.attrs['origin']
    if origin[-4:] == '.sfx':
        filename=f'{origin[:-4]}_{args.field}_.png'
    elif origin[-3:] == '.FA':
        filename=f'{origin[:-3]}_{args.field}_.png'
    else:
        filename=f'{origin}_{args.field}_.png'

    filepath = os.path.join(os.getcwd(), filename)


fig, axs = plt.subplots()
data.plot(ax=axs)

if args.save:
    plt.savefig(filepath)


plt.show()
