#!/bin/bash

# A script to ensure the necessary packages are installed

source ./common.sh

if [ "$#" -gt 1 ]; then
    echo "Usage: packages.sh"
    exit 1
fi

#Rscript -e "Sys.getenv('R_LIBS_USER')"
#Rscript -e ".libPaths()"

if [ ! -d ./packages ]; then
   echo "Creating packages directory"
   mkdir ./packages
fi
 
program=Setup.R
if [ -f $program ]; then
   echo "running R..."
   #R CMD BATCH $program $@
   Rscript $program $@
   exit 0
else
   echo "Unknown file: $program"
   exit 1
fi
