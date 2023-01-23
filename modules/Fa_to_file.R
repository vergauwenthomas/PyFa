#!/usr/bin/env Rscript



#tailing arguments (without - sign!):

#1 Filename
#2 field
#3 location of outputfiles


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
outputdir = args[3]

print(filename)

#datafile = paste0(outputdir, "field_data_", LT, ".txt")
#infofile = paste0(outputdir, "field_info_", LT, ".txt")
#coordxfile = paste0(outputdir, "coord_x_data_", LT, ".txt")
#coordyfile = paste0(outputdir, "coord_y_data_", LT, ".txt")


#-------------------Open geofield ------------------------------------

x = Rfa::FAopen(filename)

# ----------------- Write available fields to file -----------------

avail_fields = x$list
sink(file.path(outputdir, "fields.json"))
cat(toJSON(avail_fields))
sink()




# ----------------Extract field -----------------------------
y = FAdec(x, field)

# -----------------Extract Projection info -----------------------------

metainfo <- vector(mode="list")
# get all field info
#about the field
metainfo[['name']] = toString(attr(y, "info")$variable)
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


#coordinates

#check if x and y are chosing correctly and not verwisseld
coords = DomainPoints(y, type="xy")
metainfo[['ycoords']] = as.numeric(data.frame(coords[2])[12,]) #select an arbirary row
metainfo[['xcoords']] = as.numeric(data.frame(coords[1])[,12]) #select an arbirary column


metainfo[['data']] = y[]



# --------------- write to file --------------------
exportJSON <- toJSON(metainfo)
write(exportJSON, file.path(outputdir, "FAdata.json"))

