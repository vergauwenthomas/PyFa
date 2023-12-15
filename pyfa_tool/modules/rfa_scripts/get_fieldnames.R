#!/usr/bin/env Rscript
library(meteogrid)
library(Rfa)


library(jsonlite)

# -----------------------IO -------------------------------------------
args = commandArgs(trailingOnly=TRUE)
filename = args[1]
outputdir = args[2]

#-------------------Open geofield ------------------------------------

x = Rfa::FAopen(filename)

# ----------------- Write available fields to file -----------------

avail_fields = x$list

sink(file.path(outputdir, "fields.json"))
cat(toJSON(avail_fields))
sink()