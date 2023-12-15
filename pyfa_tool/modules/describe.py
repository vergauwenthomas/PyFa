#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 12:22:26 2023

@author: thoverga
"""

import sys
from datetime import datetime, timedelta
from .IO import read_json


def _split_fields(fieldslist):
    """Split the 2d fields from the 3d fields (other representation in describe)."""
    single_lvl_fields = []
    multi_lvl_fields = {}

    for field in fieldslist:
        fieldname = field['name'].strip()

        if (fieldname.startswith('S') & fieldname[1:3].isnumeric()):
            # For 3d fields
            basis_fieldname = fieldname[4:]
            if not basis_fieldname in multi_lvl_fields.keys():
                init_fielddict = field
                init_fielddict['full_name'] = fieldname
                init_fielddict['name'] = basis_fieldname
                init_fielddict['levels'] = [int(fieldname[1:4])]

                multi_lvl_fields[basis_fieldname] = init_fielddict #update dict

            else:
                # just add level to knonw levels
                multi_lvl_fields[basis_fieldname]['levels'].append(int(fieldname[1:4]))
        else:
            # For 2d fields
            single_lvl_fields.append(field)

    return multi_lvl_fields, single_lvl_fields


def _print_fields_table(fields_2d, fields_3d):
    """ Print out the fields information."""
    # First 2d fields
    print('########## 2D ######### \n')
    print(f'{"name".ljust(19)}{"index".ljust(8)}{"spectral".ljust(10)}{"nbits".ljust(6)}')
    print('------------------------------------------')
    for field in fields_2d:
        print(_format_2d_field(field))

    print('\n########## 3D ######### \n')
    print(f'{"Base-name".ljust(19)}{"Full-name example".ljust(19)}{"spectral".ljust(10)}{"nbits".ljust(6)}levels')
    print('-------------------------------------------------------------')
    for field in fields_3d.values():
        print(_format_3d_field(field))


def describe_fa_from_json(metadatajson_path, fieldsjson_path):
    """
    Print out an overview of the FA file content by reading the json FA files.

    Parameters
    ----------
    metadatajson_path : str
        Path to the json file containing the metadata.
    fieldsjson_path : str
        Path to the json file containing the information on the fields.

    Returns
    -------
    None.

    """
    # Reading the data jsonfile
    # Buffered reading?
    d = read_json(jsonpath=metadatajson_path, to_dataframe=False)
    fields = read_json(jsonpath=fieldsjson_path, to_dataframe=False)

    multi_lvl_fields, single_lvl_fields = _split_fields(fields)

    # formatting datetimes
    validdate = _str_to_dt(d['validate'][0])
    basedate = _str_to_dt(d['basedate'][0])
    timestep = timedelta(seconds=int(d['timestep'][0]))

    print(
    f'''
### File format : FA

## File name: {d['origin']}
## File path: {d['filepath']}

#################
##   VALIDITY  ##
#################

Validity               : {validdate}
Basedate               : {basedate}
Leadtime               : {validdate - basedate}

Timestep               : {timestep}
N time iterations      : {int((validdate - basedate)/timestep)}


#######################
## HORIZONTAL GEOMETRY
#######################

Points of C+I in X      : {d['nx'][0]}
Points of C+I in Y      : {d['ny'][0]}

Kind of projection      : {d['projection'][0]}
Reference lat (ELAT0)   : {d['lat_1'][0]}
Reference lon (ELON0)   : {d['lon_0'][0]}
Center lat              : {d['center_lat'][0]}
Center lon              : {d['center_lon'][0]}

Resolution in X (m)     : {d['dx'][0]}
Resolution in Y (m)     : {d['dy'][0]}


#######################
## Vertical GEOMETRY
#######################
N levels                : {d['nlev'][0]}
Ref pressure            : {d['refpressure'][0]}

Vert coords A           :
{d['A_list']}

Vert coords B           :
{d['B_list']}



#######################
## FIELDS
#######################

Number of fields        : {d['nfields']}

    ''')

    _print_fields_table(fields_2d=single_lvl_fields,
                        fields_3d=multi_lvl_fields)


# =============================================================================
# Text formatters
# =============================================================================

def _str_to_dt(strdatetime):
    """Format datetimes to string."""
    if len(strdatetime) == 19:
        return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')
    elif len(strdatetime) == 10:
        return datetime.strptime(strdatetime, '%Y-%m-%d')
    else:
        sys.exit(f'could not format {strdatetime} to a datetime')


def _format_2d_field(fielddict):
    """Text representation of a 2d field."""
    name = fielddict['name'].strip().ljust(20)

    try:
        idx = str(fielddict['index']).ljust(8)
    except KeyError:
        idx = 'Unknown'.ljust(8)

    try:
        spctr = str(fielddict['spectral']).ljust(8)
    except KeyError:
        spctr = 'Unknown'.ljust(8)

    try:
        nbit = str(fielddict['nbits']).ljust(4)
    except KeyError:
        nbit = 'Unknown'.ljust(4)

    return f"{name}{idx}{spctr}{nbit}"


def _format_3d_field(fielddict):
    """Text representation of a 3d field."""
    basename = fielddict['name'].strip().ljust(20)

    try:
        fullname = str(fielddict['full_name']).ljust(19)
    except KeyError:
        fullname = 'Unknown'.ljust(19)

    all_levels = list(range(min(fielddict['levels']),
                            max(fielddict['levels']) + 1))
    # how to specify the levels
    if set(all_levels) == set(fielddict['levels']):
        levels = f"{min(fielddict['levels'])} - {max(fielddict['levels'])}"
    else:
        levels = fielddict['levels']

    try:
        spctr = str(fielddict['spectral']).ljust(10)
    except KeyError:
        spctr = 'Unknown'.ljust(10)

    try:
        nbit = str(fielddict['nbits']).ljust(4)
    except KeyError:
        nbit = 'Unknown'.ljust(4)

    return f"{basename}{fullname}{spctr}{nbit}{levels}"