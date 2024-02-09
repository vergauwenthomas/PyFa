#!/usr/bin/env Rscript
library(meteogrid)
library(Rfa)
library(ncdf4)


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

#filename='/home/thoverga/Documents/github/PyFa-tool/tests/data/PFAR07csm07+0002'
#outputdir = '/home/thoverga/Documents/github/PyFa-tool/development/tmp_fajson'
#extra_attr_file='/home/thoverga/Documents/github/PyFa-tool/development/tmp_fajson/Rfa_extra_attrs.json'

# ---------------------------------------------
# ------------ read special attributes -------------
#----------------------------------------------
extra_attrs = fromJSON(extra_attr_file)
d2_whitelist=extra_attrs$`2d_white`
d3_whitelist=extra_attrs$`3d_white`
d2_blacklist=extra_attrs$`2d_black`
d3_blacklist=extra_attrs$`3d_black`

## ----------__DEBUG__------------------

#d2_whitelist = c("PROFTEMPERATURE", "PROFRESERV.EAU", "PROFRESERV.GLACE",
#                 "SURFRESERV.NEIGE", "SURFALBEDO NEIGE", "SURFDENSIT.NEIGE",
#                 "SURFALBEDO HISTO", "SURFTEMPERATURE", 'S036HUMI.SPECIFI')
#d3_whitelist = c("WIND.U.PHYS")
#d2_blacklist=c()
#d3_blacklist=c()

## ---------END DEBUG --------------------

# ---------------------------------------------
# ------------ Create a target -------------
#----------------------------------------------
fillvalue <- 1e32
var_precision='double'
trg_file=file.path(outputdir, "FA.nc")

# ---------------------------------------------
# ------------ Get all fieldnames -------------
#----------------------------------------------

# open file
x = Rfa::FAopen(filename)
# data = copy(x)

#Extract all fieldnames
fieldnames = x$list$name

#filter to 2D fields and 3d fields
fieldnames3D = fieldnames[grep("S\\d\\d\\d", fieldnames)] #start with S and followd by three digits
fieldnames2D = fieldnames[!(fieldnames %in% fieldnames3D)]

#Get the basenames of the 3D fields (S002TEMPERATURE ---> TEMPERATURE)
basenames3D = gsub("S\\d\\d\\d", "", fieldnames3D) #drop the Sxxx part
basenames3D = unique(basenames3D) #avoid to read in a 3d field multiple times



# Get all the specific 2D fields in the whitelist that are levels
# of the 3D field.
specific_2d = c()
for (d3_level in fieldnames3D) {
    if (trimws(d3_level) %in% d2_whitelist){
        specific_2d = c(specific_2d, d3_level)
    }
}


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
    specific_2d = specific_2d[!(specific_2d %in% d2_levels)] #drop pseudo fields from specific 3d levels
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

attrs <- list('basedate'=toString(attr(y, "info")$time$basedate),
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



# ---------------------------------------------
# ------------Define dimension -------------
#----------------------------------------------
xdim <<- ncdim_def(name="xdim", units="see_proj",vals=as.double(xcoords))
ydim <<- ncdim_def(name="ydim",units="see_proj",vals=as.double(ycoords))
zdim <<- ncdim_def(name="zdim",units="level",vals=seq(1, attr(x,  'frame')$nlev, by=1))

nxdim <<- length(xcoords)
nydim <<- length(ycoords)
nlev <<- attr(x,  'frame')$nlev
# ---------------------------------------------
# ------------ Constructor functions -------------
#----------------------------------------------
make_2d_nc_variable <- function(geofieldname) {
  return(ncvar_def(name=geofieldname,
                  units="_undef",
                  dim=list(xdim,ydim),
                  missval=fillvalue,
                  longname="",
                  prec=var_precision))
}

make_2d_array <- function(geofield) {
  return(array(as.vector(geofield),
                   dim=c(nxdim,nydim)))
  
}

make_3d_nc_variable <- function(geofieldbasename) {
  return(ncvar_def(name=geofieldbasename,
                  units="_undef",
                  dim=list(xdim,ydim, zdim),
                  missval=fillvalue,
                  longname="",
                  prec=var_precision))
}

make_3d_array <- function(geofield) {
  #write data
  # toadd <- list('data'=array(y, dim=c(nx, ny, nlev)),
  #               'type'='3d')
  
  return(array(as.vector(geofield),
                   dim=c(nxdim,nydim, nlev)))
}


# ---------------------------------------------
# ------------ Collect data -------------
#----------------------------------------------


nc_vars_to_add = list() #stores all variable metadata
nc_data_to_add = list() #stores data
nc_vars_attr_to_add = list() #stores attribute specific to a field



#Loop over all 2d fields
for (fieldname in fieldnames2D) {
  fieldname = trimws(fieldname)
  if (fieldname %in% d2_whitelist){
    if (fieldname %in% d2_blacklist){
      print(paste0(fieldname, ' rejected by blacklist'))
    }else{
      tryCatch(
        #try to do this
        {
          print(paste0(fieldname, ' reading ...'))
          y = FAdec(x, fieldname)

          nc_vars_to_add[[fieldname]] = make_2d_nc_variable(fieldname)
          nc_data_to_add[[fieldname]] = make_2d_array(y)
          nc_vars_attr_to_add[[fieldname]] = list('type'="2d")


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
  fieldname = trimws(fieldname)
  if (fieldname %in% d2_whitelist){ #Keep in mind pseudo 3D whitelist are interpreted as 2d whitelist
    if (fieldname %in% d2_blacklist){  #Keep in mind pseudo 3D blacklist are interpreted as 2d whitelist
      print(paste0(fieldname, ' (pseudo3D) rejected by blacklist'))
    }else{
      tryCatch(
        #try to do this
        {
          print(paste0(fieldname, ' (pseudo3D) reading ...'))
          y = FAdec(x, fieldname)
          nc_vars_to_add[[fieldname]] = make_2d_nc_variable(fieldname)
          nc_data_to_add[[fieldname]] = make_2d_array(y)
          nc_vars_attr_to_add[[fieldname]] = list('type'="pseudo_3d")

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


#Loop over specific whitelist fields that are levels of 3d fields
for (fieldname in specific_2d) {
  fieldname = trimws(fieldname)
  if (fieldname %in% d2_whitelist){ #Keep in mind pseudo 3D whitelist are interpreted as 2d whitelist
    if (fieldname %in% d2_blacklist){  #Keep in mind pseudo 3D blacklist are interpreted as 2d whitelist
      print(paste0(fieldname, ' (Specific level of 3D) rejected by blacklist'))
    }else{
      tryCatch(
        #try to do this
        {
          print(paste0(fieldname, ' (Specific level of 3D) reading ...'))
          y = FAdec(x, fieldname)
          nc_vars_to_add[[fieldname]] = make_2d_nc_variable(fieldname)
          nc_data_to_add[[fieldname]] = make_2d_array(y)
          nc_vars_attr_to_add[[fieldname]] = list('type'="pseudo_3d")
          # toadd <- list('data'=array(y[]), 'type'='pseudo_3d')
          # data[fieldname] = list(toadd)

        },
        #if an error occurs, tell me the error
        error=function(e) {
          message('An Error Occurred for this (Specific level of 3D) field')
          print(e)
        }
      )
    }
  }else{
    print(paste0(fieldname, '(Specific level of 3D) not in whitelist'))
  }
}

#loop over all 3d basename fields

for (basename in basenames3D) {
  basename = trimws(basename)
  if (basename %in% d3_whitelist){
    if (basename %in% d3_blacklist){
      print(paste0(basename, ' rejected by blacklist'))
    }else{
      tryCatch(
        #try to do this
        {
          print(paste0(basename, ' reading ...'))
          y = FAdec3d(x, par=basename, plevels.out = NULL)

          nc_vars_to_add[[basename]] = make_3d_nc_variable(basename)
          nc_data_to_add[[basename]] = make_3d_array(y)
          nc_vars_attr_to_add[[basename]] = list('type'="3d")

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



#-------- Construct the netcdf ------------------
# create netCDF file and put arrays
ncout <- nc_create(filename=trg_file,
                   vars=nc_vars_to_add,
                   force_v4=TRUE)
#add variables
for (name in names(nc_data_to_add)) {
  print(name)
  ncvar_put(nc=ncout, varid=name,
            vals=nc_data_to_add[[name]],
            na_replace='fast')
}
ncatt_put(nc=ncout, varid=0, attname="fillvalue", attval=fillvalue)
# nc_close(ncout)
# put additional attributes into dimension and data variables (specified by varid)
ncatt_put(nc=ncout,
          varid="xdim", #point to name already in the nc vars/dims
          attname="axis",
          attval="X") #,verbose=FALSE) #,definemode=FALSE)
ncatt_put(nc=ncout,
          varid="ydim", #point to name already in the nc vars/dims
          attname="axis",
          attval="Y") #,verbose=FALSE) #,definemode=FALSE)


#add attributes specific to the fields
for (name in names(nc_vars_attr_to_add)) {
  for (key in names(nc_vars_attr_to_add[[name]])){
    ncatt_put(nc=ncout,
              varid=name, #point to name already in the nc vars/dims
              attname=key,
              attval=nc_vars_attr_to_add[[name]][[key]]) #,verbose=FALSE) #,definemode=FALSE)
  }
}

# add global attributes (because varid == 0 --> makes this attribute global for the nc)
#add attributes specific to the fields
for (name in names(attrs)) {

    ncatt_put(nc=ncout,
              varid=0,
              attname=name,
              attval=attrs[[name]]) #,verbose=FALSE) #,definemode=FALSE)
}
ncatt_put(nc=ncout, varid=0, attname="var_presision", attval=var_precision)
ncatt_put(nc=ncout, varid=0, attname="fillvalue", attval=fillvalue)
# Get a summary of the created file:
#ncout

# close the file, writing data to disk
nc_close(ncout)


