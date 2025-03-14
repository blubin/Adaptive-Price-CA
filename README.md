# Adaptive-Price Combinatorial Auction

Combinatorial Auctions have been developed over the past 25 years to facilitate trade in settings where bidders have complex 
(complement and/or substitute) preferences over indivisible items.  There is a long literature on various mechanisms within
this class.  One important question that arises in this literature is how to price the packages that are sold in such auctions.

For sufficiently complex settings, linear prices will fail to clear combinatorial preferences.  To address this, the auction
implemented here starts with linear prices and then adaptively adds non-linear terms such that market-clearing
is achieved.  The mechanism can also switch from anonymous to non-anonymous prices if and when this is necessary for
clearing.

This implementation is the companion to the following paper, available via open access.  Please cite any reference or use accordingly:

> Sébastien Lahaie, Benjamin Lubin (2025) [Adaptive Pricing in Combinatorial Auctions](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.4993). _Management Science_ (Forthcoming).

Corresponding BibTex is as follows:

```
@article{lahaielubin25adaptive,
  author={Lahaie, S{\'e}bastien and Lubin, Benjamin},
  title={Adaptive Pricing in Combinatorial Auctions},
  journal={Management Science},
  year={2025, forthcoming},
  publisher={{INFORMS}},
}
```

For reference, this paper is based on an earlier conference paper:

> Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive-price Combinatorial Auctions."](https://dl.acm.org/doi/abs/10.1145/3328526.3329615) In _Proceedings of the 20th ACM Conference on Economics and Computation (EC-19)_, pp. 749-750. 2019.

## Overview of Experimental Pipeline and This Codebase

This repository contains an implementation of the adaptive-price
combinatorial auction described in the above paper.  It also contains an 
experimental harness to test it, and a set of scripts for analyzing the 
resulting data. 

The experimental pipeline used to provide the results 
presented in the paper has two phases.

### Experiments

The first phase is stored in the [experiments](https://github.com/blubin/Adaptive-Price-CA/blob/main/experiments/) 
directory of the 
repository.  In this phase, we run a set of experiments, each focusing on a
different aspect of the proposed mechanism, including the core
behavior, and specialized experiments on strategic behavior and on
price trajectories.  Each of these experiments involves running
multiple mechanisms (not just the mechanism being evaluated, but 
also benchmark mechanisms as well) across hundreds of instances 
drawn from several domains.  Consequently, running the experiments 
takes months of compute time on a high-end workstation, or access to 
grid infrastructure. Reproducing the results in the paper as faithfully
as possible requires configuration and access to the 
[CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio)
solver, though individual auction instances can typically be run with
an open source solver.  

The input to this phase is data from domain generators 
from the literature (e.g. CATS and QuadraticValuation).  We include both the 
generator code/binaries and the resulting input data 
in the `experiments` directory.  The output of this phase are large `.zip` files
containing data about each experimental run.  This output is
stored in the `analysis` directory (i.e., the second phase), where it is the input.

Please see the [readme](https://github.com/blubin/Adaptive-Price-CA/blob/main/experiments/readme.md) 
file in the `experiments` directory for more details on spot checking 
and/or running experiments using this implementation.

#### Runtime

The following table lists the average runtime in seconds over 100 runs for each combination of auction and instance generator in the experiments from the paper. To obtain an approximate runtime to reproduce the experiments for a generator, multiply the _Total_ for that row by 100. For example, running the full experiments for the Arbitrary generator takes approximately 43 hours of CPU time. Note that these runtimes were achieved using the CPLEX solver. 

| Generator | IBundle | Linear Clock | Linear Exact | Linear Packing | Adaptive | *Total* |
|-----------|---------|--------------|--------------|----------------|----------|-------|
| Arbitrary | 12.1 | 32.2 | 1357.0 | 107.3 | 48.3 | 1556.9 |
| Paths | 5.9 | 224.5 | 2712.8 | 30.1 | 171.5 | 3144.8 |
| Regions | 7.9 | 34.4 | 1113.2 | 50.2 | 39.1 | 1244.8 |
| Quadratic | 10813.9 | 50.1 | 236.7 | 897.9 | 137.5 | 12136.1 |
| *Mean* | 2710.0 | 85.3 | 1354.9 | 271.4 | 99.1 |  |



### Analysis

The second phase is stored in the [analysis](https://github.com/blubin/Adaptive-Price-CA/blob/main/analysis/) 
directory of the repository
In this phase, we use a set of Bash and R scripts to
process the `.zip` files created in the *experiments* (described above), 
in order to create the plots and tables presented in the paper.  
The `analysis` directory thus includes both the 
`.zip` files (output from the experimental phase) and the scripts used to process them.  
The output of the analysis phase is a set of `.tex`, `.eps` and `.pdf` 
files that summarize and collate the experimental data into a form suitable 
for inclusion in the paper.

Please see the [readme](https://github.com/blubin/Adaptive-Price-CA/blob/main/analysis/readme.md) 
file in the `analysis` directory for more details on how
to run the analysis scripts from a checked-out copy of the repository.
