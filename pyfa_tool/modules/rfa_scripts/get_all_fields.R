
#!/usr/bin/env Rscript
library(meteogrid)
library(Rfa)


library(data.table)
library(jsonlite)

#filename = "/home/thoverga/Documents/github/PyFa-tool/development/fa_files/20200801/PFAR07csm07+0004"
#outputdir="/home/thoverga/Documents/github/PyFa-tool/tests/data"




# -----------------------IO -------------------------------------------
# args

args = commandArgs(trailingOnly=TRUE)
filename = args[1]
outputdir = args[2]

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



# Collect metadata
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



#Loop over all fields
for (fieldname in fieldnames2D) {
  print(fieldname)
  tryCatch(
    #try to do this
    {
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


for (basename in basenames3D) {
  print(basename)
  tryCatch(
    #try to do this
    {
      y = FAdec3d(x, par=basename, plevels.out = NULL)
      # Specific 3dfield data attr
      nx = attr(y, "domain")$nx
      ny = attr(y, "domain")$ny
      nlev=attr(x,  'frame')$nlev
      #write data
      print("write data of")
      print(basename)
      toadd <- list('data'=array(y, dim=c(nx, ny, nlev)),
                    'type'='3d')
      data[basename] = list(toadd)
      print('writing done')
    },
    #if an error occurs, tell me the error
    error=function(e) {
      message('An Error Occurred for this 3d field')
      print(e)
    }
  )

}


# write to json
exportJSON <- toJSON(data)
write(exportJSON, file.path(outputdir, "FA.json"))
end_time <- Sys.time()
