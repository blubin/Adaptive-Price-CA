# Adaptive-Price Combinatorial Auction

This project contains an implementation of an adaptively-priced combinatorial auction.  For sufficiently
complex settings, linear prices will fail to clear combinatorial preferences.  To address this, the auction
implemented here starts with linear prices and then adaptively adds a modest set of non-linear terms such that market-clearing
is achieved.  The mechanism can also switch from anonymous to non-anonymous prices if and when this is necessary for
clearing.

This implementation is the companion to the following paper.
Please cite any reference or use accordingly:

> Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive Pricing in Combinatorial Auctions."]() In _Management Science_, Forthcoming.

Corresponding BibTex is as follows:

```
@article{lahaielubin23adaptive,
  author={Lahaie, S{\'e}bastien and Lubin, Benjamin},
  title={Adaptive Pricing in Combinatorial Auctions},
  journal={Management Science},
  year={2024, forthcoming},
  publisher={{INFORMS}},
}
```

For reference, this paper is based on an earlier conference paper:

> Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive-price Combinatorial Auctions."](https://dl.acm.org/doi/abs/10.1145/3328526.3329615) In _Proceedings of the 20th ACM Conference on Economics and Computation (EC-19)_, pp. 749-750. 2019.



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
