# Adaptive-Price Combinatorial Auctions

This project contains an implementation of an adaptevely-priced combinatorial auction.  For sufficiently
complex settings, linear prices will fail to clear combinatorial preferences.  To address this, the auction
implemented here starts with linear prices and then adds
a modest set of non-linear terms such that market-clearing
is achieved.  The mechanism can also switch from anonymous
to non-anonymous prices if and when this is necessary for
clearing.

This implementation is the companion to the following paper.  Please cite any use or reference to this work accordingly:

{
Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive Pricing in Combinatorial Auctions."]() In _Management Science_, Forthcoming.
}

For reference, this paper is in turn based on an earlier conference paper:

{
Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive-price Combinatorial Auctions."](https://dl.acm.org/doi/abs/10.1145/3328526.3329615) In _Proceedings of the 2019 ACM Conference on Economics and Computation_, pp. 749-750. 2019.
}