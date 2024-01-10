#!/usr/bin/env Rscript
library(meteogrid)
library(Rfa)


library(data.table)
library(jsonlite)


# ==============================================================================
# This script will:
#
# 1. Open an FA file with Rfa
# 2. find all 2D and 3D fields
# 3. find general metadata + coordinates from the first field and add it to a list
# 3. Read all 2D fields and add it to the list
# 4. Read all 3D fields + construct the coordinates and add it to the list
# 5. All data is writed to a json file ('FA.json') in the output folder
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
dummy_field = fieldnames[1]

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


