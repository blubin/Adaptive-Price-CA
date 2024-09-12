#!/bin/bash

# A script to analyze experiments

source ./common.sh

if [ "$#" -gt 1 ]; then
    echo "Usage: Basic.sh"
    exit 1
fi

program=Strategy.R
if [ -f $program ]; then
   echo "running R..."
   #R CMD BATCH $program $@
   Rscript $program $@
   exit 0
else
   echo "Unknown file: $program"
   exit 1
fi
