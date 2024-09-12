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

### Bash
To run the scripts, you will need a modern `Bash` shell
interpreter.  The scripts were origionally run on linux, but
they should also work on a Mac or on a PC with the [cygwin](https://www.cygwin.com/) 
environment (which provides `bash` on that OS), 

### Python
To run the auction, you will need 
[Python 2.7](https://www.python.org/downloads/release/python-2718/),
when installing please note where your python has been installed
(or if you already have Python 2.7 installed, note its location
on your machine).

### Python Packages
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

### CPLEX (Optional for running spot instances, required for large-scale experiments)
To run a spot instance, the opensource solver loaded as part of the pcakages is likely
sufficient.  To run the full experiments it will be unacceptably slow.  Accordingly
you will need to download and install the
[CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio)
solver.  If CPLEX is properly installed with the appropriate environment
variables, the code will automatically pick it up and start using it.  If you are 
indoubt about which version of the solver the code is using, uncomment
the print statement in the `solve(pulp_problem, ...)` call in 
`experiments/adaptiveCA/mpsolve.py` and the code will indicate if it has found
CPLEX or fallen back on the default (slow) solver.

### CATS (Optional) 
If you want to use [CATS](https://www.cs.ubc.ca/~kevinlb/CATS/) to create 
new domain instances beyond those included in the paper, you will need to ensure that
your environment is setup to run the binary.  The binary is included in the `experiments/cats` 
directory.  Please follow the link above for instructions on configuring CATS.

### Pytest (Optional) 
If you want to be able to use [pytest](https://docs.pytest.org/en/stable/getting-started.html)
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

- `experiments/`: Top level scripts and documentation
- `experiments/adaptiveCA`: python source files
- `experiments/cats`: binaries for the [CATS Domain](https://www.cs.ubc.ca/~kevinlb/CATS/) generator
- `experiments/data`: cached instance files for each domain instance used in the experiments
- `experiments/tests`: unit tests
- `experiments/exeriments`: output files for the experiments.

### Generator and input file details

The auctions implemented herein are run on several different *instance generators* as part of 
the experimental setup.  To facilitate this, the auction instances are obtained by the experimental
code via `experiments/adaptiveCA/generatorfactory.py`.  Via this interface, calling code can request a particular
generator, i.e., [CATS](https://www.cs.ubc.ca/~kevinlb/CATS/) or the *Quadratic Value* generator, with 
a particular parameterization (i.e., for cats, the `PATHS` domain with a certain number of goods and 
a certain number of bids), and then request a particular auction *instance* from that configuration.  
Instances are indexed by whole numbers.  In the case of CATS, the code will run the CATS binary to 
generate the the instance, configured as specified.  In the case of the *Quadratic Value* generator, 
we have our own python implementation that is called (see `adaptiveCA/generators.py`).  

Regardless of which generator is used, when an instance is requested, after creating the instance, 
we cache its data as a file in the `experiments/data` directory.  When the instance is subsequently requested, 
the python code will hydrate the data from this cache file rather than calling the generator again.  
This caching speeds runtime when running multile auctions over the same instance (since the instance 
only has to be generated once).  It also guarantees repeatable results (this is belt-and-suspenders, 
since effort has been taken to ensure that the generator code is deterministic such that re-requesting 
the same instance index on the same setup should produce an idential instance). 

Because the generators are deterministic, the `experiments/data` directory will be recreated if it 
is removed and the experiments are rerun.  However, to ensure repeatability, and to save the user from
having to ensure that the CATS binary will run on their computer, we include all of the cached generator 
data files used in our experiments in the `experiments/data` directory.  These will thus be auto-loaded
by the code if you clone the full repository.

### Output file details

The experiments consist of running multiple domains each with multiple instances on mechanisms parameterized
in multiple ways.  The output of the experiments will appear in the `experiments/experiments` directory
when an experiment is run.  Each experimental run will produce a subdirectory with the name of the experiment. 
The subdirectory will contain two types of CSV files, one type is created per auction instance (in the
`instances` subdirectory), and the other is a "rollup" of data across all of the instances of the same 
configuration.

In our experimental pipeline, we then `zip` each subdirectory of the `experiments/experiments` directory
and move the `.zip` file to the `analysis/results` directory (i.e. we place the `.zip` file in the analysis 
branch of the repository tree for further processing by the analysis scripts).  Because this is a straightforward
zipping operation, we handle this directly at the command line, rather than creating a specific script for it.

Because of this structure, instead of including an `experiments/experiments` directory, we have instead
included all of the `.zip` files for the experiments included in the paper in the `analysis/results` directory
where they are ready for processing by that stage of the process.  None the less, if you run the experimental 
code yourself, the `experiments/experiments` directory will be created and populated.

Because both of the raw output file types are in CSV format, it is easy to inspect the results of experiments.

### Code Details

The auction code is rather involved, but we here provide a high-level overview of the included code files.

#### Auction and Math Programming 

- `experiments/adaptiveCA/agents.py': 
- `experiments/adaptiveCA/auctions.py': 
- `experiments/adaptiveCA/generatorfactory.py': 
- `experiments/adaptiveCA/generators.py': 
- `experiments/adaptiveCA/instrumentation.py': 
- `experiments/adaptiveCA/mpsolve.py': 
- `experiments/adaptiveCA/prices.py': 
- `experiments/adaptiveCA/structs.py': 
- `experiments/adaptiveCA/wd.py':
- `experiments/adaptiveCA/util/modcsv.py`:

#### Experimental Setup

- `experiments/adaptiveCA/experiments/experiment.py`:
- `experiments/adaptiveCA/experiments/cpurestrict.py`:
- `experiments/adaptiveCA/experiments/debug_experiment.py`:

- `experiments/adaptiveCA/experiments/basic.py`: Run the *basic* experiment for most auction types
- `experiments/adaptiveCA/experiments/cutting.py`: Run the *basic* experiment for the *Adaptive Cutting* auction
- `experiments/adaptiveCA/experiments/lca.py`: Run the *basic* experiment for the *Linear Clock* auction
- `experiments/adaptiveCA/experiments/strategy.py`: Run the *strategy* experiment to investigate bidder manipulation.
- `experiments/adaptiveCA/experiments/xorprices.py`: Run the *xorprices* experiment that gathers additional pricing information.

## The Scripts

### Spot Instances

### (Advanced) Full Experiments

### (Optional) Running Pytest
