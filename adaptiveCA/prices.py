# Copyright (c) 2023 Benjamin Lubin and Sebastien Lahaie.
#
# This file is part of Adaptive-Price-CA
# (see https://github.com/blubin/Adaptive-Price-CA).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Module defining price structures.

"""

from adaptiveCA.structs import Bundle
from adaptiveCA.structs import Polynomial
from adaptiveCA.structs import Xor
import itertools
from collections import OrderedDict

class Prices(object):
    """Prices provide functionality to price bundles and update the prices."""

    def __init__(self):
        super(Prices, self).__init__()

    def price(self, bundle):
        """Prices a bundle.

        Args:
          - bundle (Bundle): bundle to price

        Returns:
          (float) Price of given bundle.

        """
        raise NotImplementedError("Not implemented.")

    def update(self, items, delta):
        """Updates the coefficients contained in a set of items by a given increment.

        Args:
          - items (sequence[int]): items to update
          - delta (float): price increment

        """
        raise NotImplementedError("Not implemented.")

    def update_relative(self, items, gamma, init_delta):
        """Updates the coefficients for a set of items by a given
        relative factor

        Args:
          - items (sequence[int]): items to update
          - gamma (float): relative price increment in (0,1)
          - init_delta (float) : the absolute initial value to use 
            if there is no existing price
        """
        raise NotImplementedError("Not implemented.")

    @property
    def struct(self):
        """Returns the core underlying data structure for the prices."""
        raise NotImplementedError("Not implemented.")

    @property
    def personalized(self):
        """Returns whether the prices are personalized."""
        raise NotImplementedError("Not implemented.")

    @property
    def degree(self):
        """Returns degree of the price representation."""
        raise NotImplementedError("Not implemented.")
    
    @property
    def sparsity(self):
        """Returns sparsity of the price representation."""
        raise NotImplementedError("Not implemented.")
    
    def as_ordered_dict(self):
        """ Convert the prices into a dictionary (e.g. for inclusion
            in a CSV file.  Note we opt to not implement the mapping
            interface (keys(), __getitem__) because the prices might
            not "naturally" be a dict -- but needs be messily
            converted into one.
        """
        raise NotImplementedError("Not imlemented.")
    
class PolynomialPrices(Prices):
    """Polynomial prices price combinations of items. The price of a
    bundle is the sum of all coefficients for terms contained in the
    bundle.

    Attributes:
      - poly (Polynomial): polynomial defining the prices

    """

    def __init__(self, terms):
        super(PolynomialPrices, self).__init__()
        self.poly = Polynomial(terms)

    def __repr__(self):
        return "PolynomialPrices(%r)" % self.poly.terms

    def __str__(self):
        def key((k, v)):
            return (len(k), k[0])
        elts = sorted(self.poly.list_terms(), key=key)
        return '\n'.join("%s: %.2f" %
                         (str(k).translate(None, '( )'), v)
                         for (k, v) in elts)

    def __getitem__(self, key):
        return self

    @property
    def struct(self):
        return self.poly

    def price(self, bundle):
        return sum(self.poly[monom]
                   for monom in self.poly
                   if set(monom) <= set(bundle))

    def update(self, items, delta):
        for monom in self.poly:
            if set(monom) <= set(items):
                self.poly[monom] += delta

    @property
    def degree(self):
        nonzero_monomials = self.poly.nonzero_monomials()
        if not nonzero_monomials:
            return 0
        return max(len(m) for m in nonzero_monomials)

    @property
    def sparsity(self):
        return len(self.poly.nonzero_monomials())
    
    @property
    def personalized(self):
        return False

    def as_ordered_dict(self):
        return self.poly.as_ordered_dict()

class LinearPrices(PolynomialPrices):
    """Linear prices price each individual item. The price of a bundle is
    the sum of its item prices.

    Attributes:
      - poly (Polynomial): the item prices--monomials are of size 1.

    """

    def __init__(self, terms):
        super(LinearPrices, self).__init__(terms)
        for monom in terms:
            if len(monom) > 1 or len(monom) == 0:
                raise ValueError("Linear prices must only have item terms.")

    @classmethod
    def initial(cls, items, initp=0.0):
        """Creates linear prices over the given items, with a given initial value.

        Args:
          - items (seq): the collection of items.
          - initp (float, optional): initial price of each item.
        """
        terms = {(item,): initp for item in items}
        return cls(terms)

    def __repr__(self):
        return "LinearPrices(%r)" % self.poly.terms

    def __str__(self):
        return '\n'.join(sorted("%s: %.2f" % (k[0], v)
                                for (k, v) in sorted(self.poly.list_terms())))
    
    def update_relative(self, items, gamma, init_delta):
        #print 'Linear Relative Update'
        #print 'init_delta: ' + str(init_delta)
        #print 'Gamma: ' + str(gamma)
        for monom in self.poly:
            if set(monom) <= set(items):
                if abs(self.poly[monom]) < 1e-4:
                    self.poly[monom] = init_delta
                else:
                    self.poly[monom] *= (1+gamma)

class QuadraticPrices(PolynomialPrices):
    """Quadratic prices price each item and combination of two items. The
    price of a bundle is the sum of its singleton and pairwise coefficients.

    Attributes:
      - poly (Polynomial): the item and pairwise terms

    """

    def __init__(self, terms):
        super(QuadraticPrices, self).__init__(terms)
        for monom in terms:
            if len(monom) > 2:
                raise ValueError(
                    "Quadratic prices can only have item and pair terms.")

    @classmethod
    def initial(cls, items, initp=0.0):
        """Creates quadratic prices over the given items, with a given initial
        value for the item terms.

        Args:
          - items (seq): the collection of items.
          - initp (float, optional): initial price of each item.

        """
        terms = {(item,): initp for item in items}
        for pair in itertools.combinations(items, 2):
            terms[pair] = 0.0
        return cls(terms)
    
class BundlePrices(Prices):
    """Bundle prices price each bundle explicitly.

    Attributes:
      - xor (XOR): bundle coefficients

    """

    def __init__(self, coefs):
        super(BundlePrices, self).__init__()
        self.xor = Xor(coefs)

    def __str__(self):
        return '\n'.join(sorted("%s: %.2f" % (k, v)
                                for (k, v) in self.xor.list_terms()))

    @classmethod
    def initial(cls):
        """Creates initial bundle prices of zero.

        """
        return cls({})

    def __getitem__(self, key):
        return self

    @property
    def struct(self):
        return self.xor

    def price(self, bundle):
        pri = max([v for (b, v) in self.xor.list_terms() if b <= bundle] +
                  [0.0])
        return pri

    def update(self, items, delta):
        bundle = Bundle(items)
        self.xor[bundle] += delta

    def update_relative(self, items, gamma, init_delta):
        #print 'Bundle Relative Update'
        #print 'init_delta: ' + str(init_delta)
        #print 'Gamma: ' + str(gamma)
        bundle = Bundle(items)
        if bundle in self.xor and abs(self.xor[bundle]) >= 1e-4:
            self.xor[bundle] *= (1+gamma)
        else:
            self.xor[bundle] = init_delta

    def as_ordered_dict(self):
        return self.xor.as_ordered_dict()

    @property
    def personalized(self):
        return False

    @property
    def degree(self):
        degrees = [len(b) for b in self.xor.nonzero_bundles()]
        return max(degrees) if len(degrees) > 0 else 0

    @property
    def sparsity(self):
        return len(self.xor.nonzero_bundles())
    
class SimpleBundlePrices(BundlePrices):
    """Bundle prices for explicit list of bundles, undefined for bundles not listed.

    """

    def __init__(self, coefs):
        super(SimpleBundlePrices, self).__init__(coefs)

    def price(self, bundle):
        if bundle in self.xor.coefs:
            return self.xor.coefs[bundle]
        raise Exception("SimpleBundlePrices failed to price %s" % bundle)
            
class PersonalizedPrices(dict):
    """Personalized prices.

    Attributes:
      - aprices (dict[Prices]): personalized agent prices.

    """

    def __init__(self, aprices):
        super(PersonalizedPrices, self).__init__(aprices)

    @classmethod
    def init_bundle(cls, aids):
        """Creates personalized bundle prices for the agents.

        Args:
          - aids (seq): agent ids

        """
        return cls({aid: BundlePrices.initial() for aid in aids})

    @classmethod
    def init_linear(cls, aids, items):
        """Creates personalized linear prices for the agents.

        Args:
          - aids (seq): agent ids
          - items (seq): collection of items

        """
        return cls({aid: LinearPrices.initial(items) for aid in aids})

    @classmethod
    def init_quadratic(cls, aids, items):
        """Creates personalized quadratic prices for the agents.

        Args:
          - aids (seq): agent ids
          - items (seq): collection of items

        """
        return cls({aid: QuadraticPrices.initial(items) for aid in aids})
    
    @property
    def personalized(self):
        """Returns whether the prices are personalized."""
        return True

    @property
    def degree(self):
        return max(p.degree for p in self.values())

    @property
    def sparsity(self):
        return sum(p.sparsity for p in self.values())
    
    def __str__(self):
        pstr = ['\n'.join(sorted("%s:%s: %.2f" % (aid, k, v)
                                 for (k, v) in
                                 self[aid].struct.list_terms()))
                for aid in self]
        return '\n'.join(pstr)

    def as_ordered_dict(self):
        ret = OrderedDict()
        for aid in sorted(self.keys()):
            sub = self[aid].as_ordered_dict()
            sub = self._prepend_to_keys(sub, str(aid)+"_")
            ret.update(sub)
        return ret

    def _prepend_to_keys(self, dictionary, prepend):
        return OrderedDict([(prepend+k,v) for (k,v) in dictionary.items()])

    def all_agents_str(self, bundle):
        s=""
        for aid in sorted(self.keys()):
            s += str(aid) + ":" + str(self[aid].price(bundle)) + "|"
        return "Pers["+s[:-1]+"]"

