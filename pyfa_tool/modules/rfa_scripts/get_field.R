#!/usr/bin/env Rscript
library(meteogrid)
library(Rfa)


library(jsonlite)
library(data.table)
library(readr)

# -----------------------IO -------------------------------------------
# args

args = commandArgs(trailingOnly=TRUE)
filename = args[1]
field = args[2]
fieldtype = args[3]
outputdir = args[4]



#-------------------Open geofield ------------------------------------

x = Rfa::FAopen(filename)


# init storage lists
metainfo <- vector(mode="list")
datainfo <- vector(mode="list")


if (fieldtype == '2dfield'){
    y = FAdec(x, field)

    # Specific 2dfield metadata attr
    metainfo[['name']] = toString(attr(y, "info")$variable)

    # Specific 2dfield data attr
    datainfo[['data']] = y[]
}

if (fieldtype == '3dfield'){
    y = FAdec3d(fa=x,
                par=field,
                plevels.out = NULL)

    # Specific 3dfield metadata attr
    metainfo[['name']] = toString(attr(y, "info")$name)
    metainfo[['z_type']] = toString(attr(y, "info")$z_type)

    # Specific 3dfield data attr
    nx = attr(y, "domain")$nx
    ny = attr(y, "domain")$ny
    nlev=attr(x, 'frame')$nlev

    datainfo[['data']] = array(y, dim=c(nx, ny, nlev))
    datainfo[['zcoords']] = seq(1:nlev)


}



# -----------------Extract Projection info -----------------------------


# get all field info
#about the field

metainfo[['basedate']] = toString(attr(y, "info")$time$basedate)
metainfo[['validate']] = toString(attr(y, "info")$time$validdate)
metainfo[['leadtime']] = toString(attr(y, "info")$time$leadtime)
metainfo[['timestep']] = toString(attr(y, "info")$time$tstep)
metainfo[['origin']] = toString(attr(y, "info")$origin)

#about the projection
metainfo[['projection']] = attr(y, "domain")$projection$proj
metainfo[['lon_0']] = attr(y, "domain")$projection$lon_0
metainfo[['lat_1']] = attr(y, "domain")$projection$lat_1
metainfo[['lat_2']] = attr(y, "domain")$projection$lat_2
metainfo[['proj_R']] = attr(y, "domain")$projection$R

metainfo[['nx']] = attr(y, "domain")$nx
metainfo[['ny']] = attr(y, "domain")$ny
metainfo[['dx']] = attr(y, "domain")$dx
metainfo[['dy']] = attr(y, "domain")$dy
metainfo[['ex']] = attr(y, "domain")$ex
metainfo[['ey']] = attr(y, "domain")$ey

metainfo[['center_lon']] = attr(y, "domain")$clonlat[1]
metainfo[['center_lat']] = attr(y, "domain")$clonlat[2]

# ------------------ Extract attributes of FA (not field) ------------------
metainfo[['nfields']] = attr(x, 'nfields')
metainfo[['filepath']] = attr(x, 'filename')

#spectral settings
metainfo[['ndlux']] = attr(x, 'frame')$ndlux
metainfo[['ndgux']] = attr(x, 'frame')$ndgux
metainfo[['nsmax']] = attr(x, 'frame')$nsmax

#vertical settings
metainfo[['nlev']] = attr(x, 'frame')$nlev
metainfo[['refpressure']] = attr(x, 'frame')$levels$refpressure
metainfo[['A_list']] = attr(x, 'frame')$levels$A
metainfo[['B_list']] = attr(x, 'frame')$levels$B



# --------------- write meta to file --------------------
exportJSON <- toJSON(metainfo)
write(exportJSON, file.path(outputdir, "FAmetadata.json"))



# -----------------Extract Data info -----------------------------


#check if x and y are chosing correctly and not verwisseld
coords = DomainPoints(y, type="xy")
datainfo[['ycoords']] = as.numeric(data.frame(coords[2])[12,]) #select an arbirary row
datainfo[['xcoords']] = as.numeric(data.frame(coords[1])[,12]) #select an arbirary column


exportJSON <- toJSON(datainfo)
write(exportJSON, file.path(outputdir, "FAdata.json"))




