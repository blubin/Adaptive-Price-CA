#!/bin/bash

# A script to run one of our experiments in python

source ./common.sh

if [ "$#" -lt 2 ]; then
    echo "Usage: experiment.sh run name {arguments}"
    exit 1
fi

if [ "$1" == 'run' ]; then
    program=adaptiveCA.experiments.$2
    if [ -f adaptiveCA/experiments/$2.py ]; then
        shift 2
        python -m $program $@
        exit 0
    else
        echo "Unknown file: $program"
        exit 1
    fi
fi

echo "Unknown option $1"
exit 1
