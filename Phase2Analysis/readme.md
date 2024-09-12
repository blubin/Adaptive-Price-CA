# Phase 2: Data Analysis For *Adpative Price Combinatorial Auctions*

## Overview of Experimental Pipeline

The experimental pipeline in this work has two phases.

In phase 1, we run a set of experiments, each focusing on a
different aspect of the proposed mechanism, including the core
behavior, and specialized experiemnts on strategic behavior and on
price trajectories.  Each of these experiments invoves running
multiple mechanisms across hundreds of instances drawn from several
domains.  Consequently running the experiments takes months of compute
time on a highend workstation.  It also requires configuration and access to the
[CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio)
solver.  The input to this phase is data from domain generators.  We
include both the generator code/binaries and the resulting input data 
in the Phase 1 directory.  The output of Phase 1 is large zip files
containing data about each experimental run.  This output is
included in the Phase 2 directory (where it is the input).

In Phase 2, we use a set of Bash and R scripts to
process these zip files, in order to create the plots and tables
presented in the paper.  The Phase 2 directory thus includes both the 
.zip files (output from Phase 1, and input to Phase 2) and the
scripts used to process them.  The output of Phase 2 is a set of 
tex, eps and pdf files suitable for inclusion in the paper.  There 
is a considerable amount of processing needed to convert the raw
data into a form appropriate for the paper, but it can still be 
run on a standard desktop/laptop in a reasonable amount of time.

This directory contains the Phase 2 implementation, and is
described in detail below.

## Requirements

To run the phase 2 analysis, you will need a modern Bash shell
interpreter, and an install of R.  The scripts were origionally run on
a PC with the cygwin environment, but they should work on linux or mac
as well.

The R scripts were originally coded against R 4.1.2, but they have
been tested to work with R 4.4.1 with some ignorable warnings.

## Setup

The first step in running the analysis scripts is to configure your
environment.  To do this, edit the `common.sh` script and specify the
path to your R environment as indicated in the file.  

Next run the `Setup.sh` file to configure your R environment.  This
will download and install all of the needed R packages into a local
directory called `packages`.

## Directies & Files

### Directory Details

The directory tree is organized as follows:

- `analysis`: Contains this readme and the scripts themselves.
- `analysis/packages`: Created by the `Setup.sh` script, this contains the downloaded R packages
- `analysis/results`: Results of the *Phase 1* experiments, i.e., `.zip` files.  This is the *input* to the *Phase 2* analysis described herein. 
- `analysis/plots`: *Phase 2 Output* -- The plots needed for the paper
- `analysis/tables`: *Phase 2 Output* -- The tables needed for the paper

The `results` directory is further broken into the following
sub-directories:

- `basic`: The *basic* experiment, for most auction types.
- `cutting`: The *basic* experiment, specifically for the *cutting* auction.
- `lca`: The *basic* experiment, specifically for the *lca* auction.
- `strategy`: The *strategy* experiment, looking at bidder misreports.
- `xorprices`: The *xorprices* experiment, for examining pricing in the auction.

When output is created by the scripts in the `plots` and `tables`
directories, subdirectories mirroring the input directory structure
will be created.  (The first three input directories all map to `basic`
on the output side.)

### Data File Details

The `.zip` files contain .csv files.  So they can be extracted and
inpsected using standard tools.  Upon first run, the scripts will load
the data from the `.zip` files and create cached
[`feather`](https://github.com/wesm/feather) files that are used in
the actual analysis.  These `feather` files can be quite large, so you
may want to delete them after running the scripts.  The scripts are
smart enough to only create the `feather` files if the `.zip` files
have changed.  You will see some `.md5` hash files in the results
directory that are created to mediate this check.

### Output File Details

In the `analysis/plots` directory, each output is provided in both PDF 
and EPS format.

In the `analysis/tables` directory, the output is provided in two
formats.  First the scripts create a `.tex` form of the output, ready
for inclusion in the paper latex with a `\input{ ... }` call.  Second,
the scripts themselves run latex on this tex fragment and generate a
standalone PDF version of the table.  This allows for a quick
inspection of the tex content, and to verify the final paper content
is including the tables as expected.  This latex compiliation is only
run if the generated `.tex` file has changed, and an `.md5` file is
created as part of this check.  You will also see files with a 
`_doc.tex` suffix that are created to enable these preview PDFs.

### Referenced Statistics

Each of the output directories also includes a `ReferencedStats.tex`
file where we capture statistics from the tables/plots that are
referenced directly in the paper prose.

## The Scripts

Most scripts have a `.R` file that is the analysis code itself and a
`.sh` bash file to facilitate running that script.

The top level `analysis` directory contains the following scripts
intended for command-line use:

- `Setup.sh`: Script for configuring the R environment.  See above.
- `Analyze.sh`: Script for running all of the other analysis scripts in turn.
- `Basic.sh`: Script for running the *basic* experiment analysis.
- `Strategy.sh`: Script for running the *strategy* experiment analysis.
- `XorPrices.sh`: Script for running the *xorprices* experiement analysis.

The directory also contains:

- `comon.sh`: which is included in the other bash scripts to provide needed environment variables.

Please note that these scripts can take some time to run, especially
the `XorPricing.sh` script that has to build a histogram which is time
consuming.

### Advanced: Loading the data for inspection

Each of the experiement analysis bash scripts above has a
corresponding `.R` script that contains the actual analysis code.  If
you wish to inspect the experimental data in e.g. RStudio, you can run
the `.R` script in *interactive* mode inside the IDE.  The scripts
contain code to recognize that they are being loaded interactively
instead of being run from the command line.  When in this mode, they
will not produce the output data, but instead load the experimental
data into memory, ready for inspection within the IDE.
