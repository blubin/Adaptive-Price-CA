#!/bin/bash

# First make sure the commands are ok in a OS specific way:
if [[ "$OSTYPE" == "cygwin" ]]; then
    function python() { /cygdrive/c/Python27/python.exe $@; }
else
    function python() { /usr/local/bin/python2.7 $@; }
fi

# Next you can override this if you need to in a machine specific way:
# Edit the below if you need to...
if [ $HOSTNAME == "SOMETHING" ]; then
    function python() { /usr/local/bin/python2.7 $@; }
fi
