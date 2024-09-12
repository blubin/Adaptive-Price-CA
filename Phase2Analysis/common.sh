#!/bin/bash

# First Make sure the commands are ok in a machine-specific way:

# The following line fixes R Locale complaints on windows, comment for Unix/Mac
unset LC_CTYPE
export TMPDIR=/tmp
export R_USER=./user
export R_LIBS_USER=./packages
if [[ "$OSTYPE" == "cygwin" ]]; then
 function R() { /cygdrive/c/Program\ Files/R/R-4.4.1/bin/R.exe $@; }
 function Rscript() { /cygdrive/c/Program\ Files/R/R-4.4.1/bin/Rscript.exe $@; }
else
 function R() { /usr/local/bin/R $@; }
 function Rscript() { /usr/local/bin/Rscript $@; }
fi
 

