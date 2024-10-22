#!/usr/bin/env Rscript
library(meteogrid)
library(Rfa)


library(data.table)
library(jsonlite)


# ==============================================================================
# This script will:
#
# 1. Open an FA file with Rfa and get all the fieldnames
# 2. Write all fieldnames (tabular data) to a json file ('fields.json') in the output folder
# 3. Find general metadata + coordinates from the first field (as dummy)
# 4. Write the metadata and coordinates to a json file ('metadata.json') in the output folder
# ==============================================================================



# -----------------------IO -------------------------------------------

args = commandArgs(trailingOnly=TRUE)
filename = args[1]
outputdir = args[2]

# --------------------------------------------------------------
# ------------ Get all fieldnames and write to Json-------------
#---------------------------------------------------------------

# open file
x = Rfa::FAopen(filename)


avail_fields = x$list

sink(file.path(outputdir, "fields.json"))
cat(toJSON(avail_fields))
sink()



# ------------------------------------------
# --------------- Get metadata -------------
#-------------------------------------------


#Extract all fieldnames
fieldnames = x$list$name
if ("SFX.XX" %in% sapply(fieldnames, trimws)){
	dummy_field="SFX.XX" #alway use the same regular field as dummy if present
}else{
	dummy_field = avail_fields$name[avail_fields$length == max(avail_fields$length)][1]
}

y = FAdec(x, dummy_field)

#coords = DomainPoints(y, type="xy")
#ycoords = as.numeric(data.frame(coords[2])[12,]) #select an arbirary row
#xcoords = as.numeric(data.frame(coords[1])[,12]) #select an arbirary column

metadata <- list('basedate'=toString(attr(y, "info")$time$basedate),
              'validate'=toString(attr(y, "info")$time$validdate),
              'leadtime'=toString(attr(y, "info")$time$leadtime),
              'timestep'=toString(attr(y, "info")$time$tstep),
              'origin'=toString(attr(y, "info")$origin),

              #about the projection
              'projection'=attr(y, "domain")$projection$proj,
              'lon_0'=attr(y, "domain")$projection$lon_0,
              'lat_1'=attr(y, "domain")$projection$lat_1,
              'lat_2'=attr(y, "domain")$projection$lat_2,
              'proj_R'=attr(y, "domain")$projection$R,

              'nx'=attr(y, "domain")$nx,
              'ny'=attr(y, "domain")$ny,
              'dx'=attr(y, "domain")$dx,
              'dy'=attr(y, "domain")$dy,
              'ex'=attr(y, "domain")$ex,
              'ey'=attr(y, "domain")$ey,

              'center_lon'=attr(y, "domain")$clonlat[1],
              'center_lat'=attr(y, "domain")$clonlat[2],

              #-------- grid --------
             # 'xcoords'=xcoords,
             # 'ycoords'=ycoords,

              # ------------------ Extract attributes of FA (not field) ------------------
              'nfields'=attr(x, 'nfields'),
              'filepath'=attr(x, 'filename'),

              #spectral settings
              'ndlux'=attr(x, 'frame')$ndlux,
              'ndgux'=attr(x, 'frame')$ndgux,
              'nsmax'=attr(x, 'frame')$nsmax,

              #vertical settings
              'nlev'=attr(x, 'frame')$nlev,
              'refpressure'=attr(x, 'frame')$levels$refpressure,
              'A_list'=attr(x, 'frame')$levels$A,
              'B_list'=attr(x, 'frame')$levels$B)


# write to json
exportJSON <- toJSON(metadata)
write(exportJSON, file.path(outputdir, "metadata.json"))


