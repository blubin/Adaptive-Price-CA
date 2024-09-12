# Adaptive-Price Combinatorial Auction

Combinatorial Auctions have been developed over the past 25 years to facilitate trade in settings where bidders have complex 
(complement and/or substitute) preferences over indivisible items.  There is a long literature on various mechanisms within
this class.  One important question that arrises in this literature is how to price the packages that are sold in such auctions.

For sufficiently complex settings, linear prices will fail to clear combinatorial preferences.  To address this, the auction
implemented here starts with linear prices and then adaptively adds a modest set of non-linear terms such that market-clearing
is achieved.  The mechanism can also switch from anonymous to non-anonymous prices if and when this is necessary for
clearing.

This implementation is the companion to the following paper.  Please cite any reference or use accordingly:

> Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive Pricing in Combinatorial Auctions."](https://pubsonline.informs.org/action/doSearch?AllField=adaptive+pricing+in+combinatorial+auctions&SeriesKey=mnsc) In _Management Science_, Forthcoming.

Corresponding BibTex is as follows:

```
@article{lahaielubin24adaptive,
  author={Lahaie, S{\'e}bastien and Lubin, Benjamin},
  title={Adaptive Pricing in Combinatorial Auctions},
  journal={Management Science},
  year={2024, forthcoming},
  publisher={{INFORMS}},
}
```

For reference, this paper is based on an earlier conference paper:

> Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive-price Combinatorial Auctions."](https://dl.acm.org/doi/abs/10.1145/3328526.3329615) In _Proceedings of the 20th ACM Conference on Economics and Computation (EC-19)_, pp. 749-750. 2019.

## Overview of Experimental Pipeline and This Codebase

This repository contains an implementation of the adaptively-priced 
combinatorial auction described in the above paper.  It also contains an 
experimental harness to test it, and a set of scripts for analyzing the 
resulting data.  The motivation for the implementation and analysis are 
the results presented in the above paper.

The experimental pipeline captured herein and used to provide the results 
presented in the paper has two phases.

### Experiments

The first phase is stored in the [experiments](https://github.com/blubin/Adaptive-Price-CA/blob/main/experiments/)  directory of the 
repository.  In this phase, we run a set of experiments, each focusing on a
different aspect of the proposed mechanism, including the core
behavior, and specialized experiemnts on strategic behavior and on
price trajectories.  Each of these experiments invoves running
multiple mechanisms (not just the mechanism being evalauted, but 
also benchmark mechanisms as well) across hundreds of instances 
drawn from several domains.  Consequently, running the experiments 
takes months of compute time on a highend workstation, or access to 
grid infrastructure.  Running the full experiments also requires 
configuration and access to the
[CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio)
solver, though individual auction instances can typically be run with
an opensource solver.  

The input to this phase is data from domain generators 
from the literature (e.g. CATS and QuadraticValuation).  We include both the 
generator code/binaries and the resulting input data 
in the `experiments` directory.  The output of this phase are large `.zip` files
containing data about each experimental run.  This output is
stored in the `analysis` directory (i.e., Phase 2), where it is the input.

Please see the [readme](https://github.com/blubin/Adaptive-Price-CA/blob/main/experiments/readme.md) 
file in the `experiments` directory for more details on spot checking 
and/or running experiments using this implementation.

### Analysis

The second phase is stored in the `analysis` directory of the repository
In this phase, we use a set of Bash and R scripts to
process the `.zip` files created in the *experiments* (described above), 
in order to create the plots and tables presented in the paper.  
The `analysis` directory thus includes both the 
`.zip` files (output from the experimental phase, representing months 
of compute time, and reproducible as described above with comensurate 
computational effort) and the scripts used to process them.  
The output of the analysis phase is a set of `.tex`, `.eps` and `.pdf` 
files that summarize and colate the experimental data into a form suitable 
for inclusion in the paper.  There is a considerable amount of processing 
needed to convert the raw data into such a form, but it can still be 
run on a standard desktop/laptop in a reasonable amount of time.

Please see the [readme](https://github.com/blubin/Adaptive-Price-CA/blob/main/analysis/readme.md) 
file in the `analysis` directory for more details on how
to run the analysis scripts from a checked-out copy of the repository.
