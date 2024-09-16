#!/bin/bash

# First make sure the commands are ok in a OS specific way:
if [[ "$OSTYPE" == "cygwin" ]]; then
    function python() { /cygdrive/c/Python27/python.exe $@; }
    function pytest() { /cygdrive/c/Python27/Scripts/pytest.exe $@; }
else
    function python() { /usr/local/bin/python2.7 $@; }
    function pytest() {
	#Attempt to extrapolate where pytest is from python location:
	pytest=/usr/local/bin/python2.7  # Provide python path
	pytest=`readlink -n $pytest`     # Expand symlink to true path
	pytest="$(dirname $pytest)"      # Get the directory
	pytest=$pytest/Scripts/pytest    # append the subpath to pytest
	$pytest $@;                      # execute
    }
fi

# Next you can override this if you need to in a machine specific way:
# Edit the below if you need to...
if [ $HOSTNAME == "SOMETHING" ]; then
    function python() { /path/to/python2.7 $@; }
    function pytest() { /path/to/pytest $@; }
fi
