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
  year={2023, forthcoming},
  publisher={{INFORMS}},
}
```

For reference, this paper is based on an earlier conference paper:

> Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive-price Combinatorial Auctions."](https://dl.acm.org/doi/abs/10.1145/3328526.3329615) In _Proceedings of the 20th ACM Conference on Economics and Computation (EC-19)_, pp. 749-750. 2019.
