# Experiments For *Adpative Pricing in Combinatorial Auctions*

## Overview 

This directory contains the implementation of an *Adaptive Price
Combinatorial Auction*, as well as alternative auctions used as
benchmarks.  It also contains the domain generators
used to create instances on which to experiment on the auction, 
code for defining particular experiments, scripts for running
both individual auction instances as a spot check, as well as full 
experiments.

Details on this content and how to use them are provided below.

## Requirements

To run the scripts, you will need a modern `Bash` shell
interpreter.  The scripts were origionally run on linux, but
they should also work on a Mac or on a PC with the [cygwin](https://www.cygwin.com/) 
environment (which provides `bash` on that OS), 

To run the auction, you will need 
[Python 2.7](https://www.python.org/downloads/release/python-2718/),
when installing please note where your python has been installed
(or if you already have Python 2.7 installed, note its location
on your machine).

You will also need install several packages, as specified in 
[requirements.txt](https://github.com/blubin/Adaptive-Price-CA/blob/main/experiments/requirements.txt).
Please install these packages using `pip` as usual in python:

> pip install -r requirements.txt

Note: for this command make sure you are using the python 2.7 version 
of pip, not python 3 if you also have python 3 installed on your system
(i.e. you may need to use the fully qualified path to pip in the above command).

Note that virtual environments in Python 2.7 are not
as sophisticated as Python 3, and we don't generally consider
it worth creating them.  If you do wish to pursue this route,
you can do so via [virtualenv](https://pypi.org/project/virtualenv/).

(Optional) If you want to be able to use [pytest](https://docs.pytest.org/en/stable/getting-started.html)
you will need to install it following the instructions at this link.

## Setup

The bash scripts need to know where your `python` executable is.  They all source
the `common.sh` script to determine this.  `common.sh` is coded to use
the default location for Python 2.7 on most operating systems, but if you
have Python installed in a diffferent location, please edit common.sh to point
to the correct location

## Directories & Files

### Directory Details

The directory tree is organized as follows:

- `file` -- explanation

### Generator and input file details

### Output file details

## The Scripts

### Spot Instances

### (Advanced) Full Experiments

### (Optional) Running Pytest
