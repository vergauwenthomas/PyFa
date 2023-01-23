#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:48:13 2023

@author: thoverga
"""

import json
import pandas as pd


def read_json(jsonpath, to_dataframe=False):
    f = open(jsonpath)
    data = json.load(f)
    f.close()
    
    if to_dataframe:
        data = pd.DataFrame(data)
    return data



def write_to_csv(data, filepath):
    if isinstance(data, type(pd.DataFrame)):
        data.to_csv(filepath, index=False)
    else:
        data = pd.DataFrame(data)
        data.to_csv(filepath,  index=False)
        
        
        
        
    