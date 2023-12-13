#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 09:15:09 2023

@author: thoverga
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature

import matplotlib.pyplot as plt
# import xarray as xr
# import geopandas as gpd

# =============================================================================
# Define plt constant styling attributes
# =============================================================================
# SMALL_SIZE = 8
# MEDIUM_SIZE = 8
# BIGGER_SIZE = 12

# plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
# plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
# plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
# plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
# plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


# =============================================================================
# Figure creator
# =============================================================================


def make_fig():
    fig, ax = plt.subplots(subplot_kw={'projection':ccrs.PlateCarree()})
    return fig, ax
    

# # =============================================================================
# Plotting functions
# =============================================================================


def make_plot(dxr, ax,title=None, grid=False, land=True, coastline=True, contour=False, legend=True, levels=10, **kwargs):
    if contour:
        dxr.plot.contourf(ax=ax, add_colorbar=legend,
                               levels=levels,  **kwargs)

    else:
        dxr.plot(ax=ax, **kwargs)

    if land:
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.BORDERS)
    if coastline:
        ax.add_feature(cfeature.COASTLINE)
    
    if grid:
        ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    
    if isinstance(title, type(None)):
        title=f'{dxr.attrs["name"].rstrip()} at {dxr.attrs["validate"]} (UTC, LT={dxr.attrs["leadtime"]}h)'
    
    ax.set_title(title)
    
    return ax









# =============================================================================
# Saving functions
# =============================================================================

def save_plot(fig, filepath, fmt='png'):
    
    # Check if filepath and fmt are compatible
    assert filepath[-len(fmt):] == fmt, f'{filepath} not compatible with format: {fmt}'
    
    fig.savefig(filepath)
    
    return 

    




