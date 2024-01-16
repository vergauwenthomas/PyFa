#!/usr/bin/env Rscript
library(meteogrid)
library(Rfa)


library(data.table)
library(jsonlite)


# ==============================================================================
# This script will:
#
# 1. Open an FA file with Rfa
# 2. find ALL 2D and 3D fields
# 3. find general metadata + coordinates from the first 2D field and add it to a list
# 3. Read all 2D fields and add it to the list
# 4. Read all 3D fields + construct the coordinates and add it to the list
# 5. All data is writed to a json file ('FA.json') in the output folder
# ==============================================================================


# -----------------------IO -------------------------------------------

args = commandArgs(trailingOnly=TRUE)
filename = args[1]
outputdir = args[2]
extra_attr_file = args[3]


# ---------------------------------------------
# ------------ read special attributes -------------
#----------------------------------------------
extra_attrs = fromJSON(extra_attr_file)
d2_whitelist=extra_attrs$`2d_white`
d3_whitelist=extra_attrs$`3d_white`
d2_blacklist=extra_attrs$`2d_black`
d3_blacklist=extra_attrs$`3d_black`


# ---------------------------------------------
# ------------ Get all fieldnames -------------
#----------------------------------------------

# open file
x = Rfa::FAopen(filename)
data = copy(x)

#Extract all fieldnames
fieldnames = x$list$name

#filter to 2D fields and 3d fields
fieldnames3D = fieldnames[grep("S\\d\\d\\d", fieldnames)] #start with S and followd by three digits
fieldnames2D = fieldnames[!(fieldnames %in% fieldnames3D)]

#Get the basenames of the 3D fields (S002TEMPERATURE ---> TEMPERATURE)
basenames3D = gsub("S\\d\\d\\d", "", fieldnames3D) #drop the Sxxx part
basenames3D = unique(basenames3D) #avoid to read in a 3d field multiple times


#filter pseudo 3d fields (fields defined at multiple but not all levels).
#These must be read in by Fadec and not Fadec3d !!
nlev = attr(x,  'frame')$nlev
fieldnames_pseudo3D = c()
for (basename in basenames3D) {
  d2_levels = fieldnames3D[grep(paste0("S\\d\\d\\d",basename), fieldnames3D)] #get 2D according fields
  if (length(d2_levels) < nlev){
    fieldnames_pseudo3D = c(fieldnames_pseudo3D, d2_levels)
    basenames3D = basenames3D[basenames3D != basename] #drop pseudo field from 3d basenames
    fieldnames3D = fieldnames3D[!(fieldnames3D %in% d2_levels)] #drop pseudo fields from 3d fieldnames
  }
}




# ---------------------------------------------
# ------------ Collect metadata -------------
#----------------------------------------------


dummy_field = fieldnames2D[1]
y = FAdec(x, dummy_field)
#check if x and y are chosing correctly and not verwisseld
coords = DomainPoints(y, type="xy")
ycoords = as.numeric(data.frame(coords[2])[12,]) #select an arbirary row
xcoords = as.numeric(data.frame(coords[1])[,12]) #select an arbirary column

toadd <- list('basedate'=toString(attr(y, "info")$time$basedate),
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
              'xcoords'=xcoords,
              'ycoords'=ycoords,

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

data['pyfa_metadata'] = list(toadd)

# ---------------------------------------------
# ------------ Collect data -------------
#----------------------------------------------


#Loop over all 2d fields
for (fieldname in fieldnames2D) {
  if (trimws(fieldname) %in% d2_whitelist){
    if (trimws(fieldname) %in% d2_blacklist){
      print(paste0(fieldname, ' rejected by blacklist'))
    }else{
      tryCatch(
        #try to do this
        {
          print(paste0(fieldname, ' reading ...'))
          y = FAdec(x, fieldname)
          toadd <- list('data'=array(y[]), 'type'='2d')
          data[fieldname] = list(toadd)

        },
        #if an error occurs, tell me the error
        error=function(e) {
          message('An Error Occurred for this 2D field')
          print(e)
        }
      )
    }
  }else{
    print(paste0(fieldname, ' not in whitelist'))
  }
}


#Loop over all pseudo 3D fields
for (fieldname in fieldnames_pseudo3D) {
  if (trimws(fieldname) %in% d2_whitelist){ #Keep in mind pseudo 3D whitelist are interpreted as 2d whitelist
    if (trimws(fieldname) %in% d2_blacklist){  #Keep in mind pseudo 3D blacklist are interpreted as 2d whitelist
      print(paste0(fieldname, ' (pseudo3D) rejected by blacklist'))
    }else{
      tryCatch(
        #try to do this
        {
          print(paste0(fieldname, ' (pseudo3D) reading ...'))
          y = FAdec(x, fieldname)
          toadd <- list('data'=array(y[]), 'type'='pseudo_3d')
          data[fieldname] = list(toadd)

        },
        #if an error occurs, tell me the error
        error=function(e) {
          message('An Error Occurred for this (pseudo3D) field')
          print(e)
        }
      )
    }
  }else{
    print(paste0(fieldname, '(pseudo3D) not in whitelist'))
  }
}


#loop over all 3d basename fields

for (basename in basenames3D) {
  if (trimws(basename) %in% d3_whitelist){
    if (trimws(basename) %in% d3_blacklist){
      print(paste0(basename, ' rejected by blacklist'))
    }else{
      tryCatch(
        #try to do this
        {
          print(paste0(basename, ' reading ...'))
          y = FAdec3d(x, par=basename, plevels.out = NULL)
          # Specific 3dfield data attr
          nx = attr(y, "domain")$nx
          ny = attr(y, "domain")$ny
          nlev=attr(x,  'frame')$nlev
          #write data
          toadd <- list('data'=array(y, dim=c(nx, ny, nlev)),
                        'type'='3d')
          data[basename] = list(toadd)
        },
        #if an error occurs, tell me the error
        error=function(e) {
          message('An Error Occurred for this 3d field')
          print(e)
        }
      )
    }
  }else{
    print(paste0(basename, ' not in whitelist'))
  }
}


# write to json
exportJSON <- toJSON(data)
write(exportJSON, file.path(outputdir, "FA.json"))

