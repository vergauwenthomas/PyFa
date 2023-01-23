#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 09:15:09 2023

@author: thoverga
"""


import matplotlib.pyplot as plt
import xarray as xr
import geopandas as gpd

# =============================================================================
# Define plt constant styling attributes
# =============================================================================



# =============================================================================
# Plotting functions
# =============================================================================

def make_plot(dxr, ax, contour=False):
    ax = dxr.plot(ax=ax)
    return ax
    









# =============================================================================
# Saving functions
# =============================================================================

def save_plot(fig, filepath, fmt='png'):
    
    # Check if filepath and fmt are compatible
    assert filepath[-len(fmt):] == fmt, f'{filepath} not compatible with format: {fmt}'
    
    fig.savefig(filepath)
    
    return 

    




