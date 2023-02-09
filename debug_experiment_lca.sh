#!/bin/bash

# A script to debug one of our experiments in python

# First Make sure the commands are ok in a machine-specific way:
if [ $HOSTNAME == "SOMETHING" ]; then
    function python() { /usr/local/bin/python2.7 $@; }
fi

program=debug_experiment_lca
python -m $program $@
