#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 12:22:26 2023

@author: thoverga
"""

import sys
from datetime import datetime, timedelta
from .IO import read_json




def _str_to_dt(strdatetime):
    if len(strdatetime) == 19:
        return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')
    elif len(strdatetime) == 10:
        return datetime.strptime(strdatetime, '%Y-%m-%d')
    else:
        sys.exit(f'could not format {strdatetime} to a datetime')



def _print_fields_table(fields):
    print(f'{"name".ljust(19)}{"index".ljust(8)}{"spectral".ljust(10)}{"nbits".ljust(6)}')

    for field in fields:
        name = field['name'].strip().ljust(20)

        try:
            idx = str(field['index']).ljust(8)
        except KeyError:
            idx = 'Unknown'.ljust(8)
        try:
            spctr = str(field['spectral']).ljust(8)
        except KeyError:
            spctr = 'Unknown'.ljust(8)
        try:
            nbit = str(field['nbits']).ljust(4)
        except KeyError:
            nbit='Unknown'.ljust(4)
        print(f"{name}{idx}{spctr}{nbit}")



def describe_fa_from_json(metadatajson_path, fieldsjson_path):
    # Reading the data jsonfile
    #buffered reading?
    d = read_json(jsonpath=metadatajson_path, to_dataframe=False)
    fields = read_json(jsonpath=fieldsjson_path, to_dataframe=False)

    # formatting datetimes
    validdate = _str_to_dt(d['validate'][0])
    basedate = _str_to_dt(d['basedate'][0])
    timestep = timedelta(seconds= int(d['timestep'][0]))


    print(
    f'''
### File format : FA

## File name: {d['origin']}

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
## FIELDS
#######################

Number of fields        : {len(fields)}

    ''')


    _print_fields_table(fields=fields)





