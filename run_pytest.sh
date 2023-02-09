#!/bin/bash

# A script to run one of our experiments in python

# First Make sure the commands are ok in a machine-specific way:
if [ $HOSTNAME == "SOMETHING" ]; then
    function pytest() { /usr/local/bin/py.test $@; }
fi

pytest $@
