#!/bin/bash

# A script to analyze experiments

source ./common.sh

if [ "$#" -gt 1 ]; then
    echo "Usage: Basic.sh"
    exit 1
fi

if [ ! -d ./tables ]; then
   echo "Creating tables directory"
   mkdir ./tables
fi

if [ ! -d ./tables/XorPrices ]; then
   echo "Creating tables/XorPrices directory"
   mkdir ./tables/XorPrices
fi

if [ ! -d ./plots ]; then
   echo "Creating plots directory"
   mkdir ./plots
fi

if [ ! -d ./plots/XorPrices ]; then
   echo "Creating plots/XorPrices directory"
   mkdir ./plots/XorPrices
fi

#Rscript -e "Sys.getenv('R_LIBS_USER')"
#Rscript -e ".libPaths()"

program=XorPrices.R
if [ -f $program ]; then
   echo "running R..."
   #R CMD BATCH $program $@
   Rscript $program $@
   exit 0
else
   echo "Unknown file: $program"
   exit 1
fi
