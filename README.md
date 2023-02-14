# Adaptive-Price Combinatorial Auctions

This project contains an implementation of an adaptevely-priced combinatorial auction.  For sufficiently
complex settings, linear prices will fail to clear combinatorial preferences.  To address this, the auction
implemented here starts with linear prices and then adds
a modest set of non-linear terms such that market-clearing
is achieved.  The mechanism can also switch from anonymous
to non-anonymous prices if and when this is necessary for
clearing.

This implementation is the companion to the following paper, please cite any reference or use accordingly:

> Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive Pricing in Combinatorial Auctions."]() In _Management Science_, Forthcoming.

Correspondinb BibTex is as follows:

```
@article{lahaielubin23adaptive,
  author={Lahaie, S{\'e}bastien and Lubin, Benjamin},
  title={Adaptive Pricing in Combinatorial Auctions},
  journal={Management Science},
  year={2023, forthcoming},
  publisher={{INFORMS}},
}
```

For reference, this paper is in turn based on an earlier conference paper:

> Lahaie, Sébastien, and Benjamin Lubin. ["Adaptive-price Combinatorial Auctions."](https://dl.acm.org/doi/abs/10.1145/3328526.3329615) In _Proceedings of the 2019 ACM Conference on Economics and Computation_, pp. 749-750. 2019.
