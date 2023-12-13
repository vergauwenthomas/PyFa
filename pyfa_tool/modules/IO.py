#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:48:13 2023

@author: thoverga
"""

import json
import pandas as pd

# =============================================================================
# Kwargs handling
# =============================================================================

def make_kwarg_dict(kwargstring):
    seperators = ['=', ':']

    kwa_dict = {}
    for item in kwargstring:
        for sep in seperators:
            kwarg_item = item.split(sep)
            if len(kwarg_item) == 2:
                break
            
        # check if argument is numeric
        key, value = kwarg_item[0], kwarg_item[1]
        if value.isnumeric():
            value=float(value)
        kwa_dict[key] = value

    return kwa_dict

    

# =============================================================================
# Json IO
# =============================================================================

def read_json(jsonpath, to_dataframe=False):
    f = open(jsonpath)
    data = json.load(f)
    f.close()
    
    if to_dataframe:
        data = pd.DataFrame(data)
    return data


# =============================================================================
# tabular data IO
# =============================================================================

def write_to_csv(data, filepath):
    if isinstance(data, type(pd.DataFrame)):
        data.to_csv(filepath, index=False)
    else:
        data = pd.DataFrame(data)
        data.to_csv(filepath,  index=False)
        
        
        
        
    