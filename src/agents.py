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

"""Module defining different kinds of agents.

"""

from string import split
import json
import pulp
import random
from adaptiveCA.structs import Bundle
from adaptiveCA.structs import Demand
from adaptiveCA.structs import Polynomial
from adaptiveCA.structs import Xor
from adaptiveCA.prices import BundlePrices
from adaptiveCA.prices import PolynomialPrices
from adaptiveCA.prices import LinearPrices
from adaptiveCA.wd import PolynomialPriceWD
from adaptiveCA.wd import WDError
import adaptiveCA.wd as wd

class Agent(object):
    """Base class for all agents.

    Attributes:
      - aid (int): agent id

    """

    def __init__(self, aid=None):
        self.aid = aid

    def __eq__(self, other):
        # This is a generic eq, that just compares all the slots
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def max_value(self):
        """ Find the maximum value the agent can have"""
        maxbundle = self.demandq(LinearPrices({}))
        return self.valueq(maxbundle)

    def valueq(self, bundle):
        """Issues a value query to the agent.

        Args:
          - bundle (Bundle): bundle whose value is queried

        Returns:
          float: value of the bundle

        """
        raise NotImplementedError("Must implement valueq")

    def demandq(self, prices, proposed=None, epsilon=0.0):
        """Issues a demand query to the agent.

        Args:
          - prices (Prices): the bundle prices
          - proposed (optional[Bundle]): proposed bundle
          - epsilon (float): tolerance for accepting proposed bundle

        Returns:
          Bundle: a utility-maximizing bundle, or the proposed
          bundle if it maximizes utility to within the given
          epsilon tolerance.

        """
        raise NotImplementedError("Must implement demandq")

    def demandsetq(self, prices, proposed=None, epsilon=0.0):
        raise NotImplementedError("Must implement demandsetq")
    
    def serialize(self):
        """Serialize the agent."""
        raise NotImplementedError("Serialization must be supported by agent.")

    @classmethod
    def deserialize(cls, string):
        """Factory method for all subclasses based on a string."""
        for cls in cls.__subclasses__():
            if cls._is_serialization(string):
                return cls._deserialize(string)
        raise Exception("Could not find deserialization class for: " + string)

    @classmethod
    def _deserialize(cls, string):
        """Factory method for the class based on a string."""
        raise NotImplementedError(
            "Deserialization must be supported by agent.")

    @classmethod
    def _is_serialization(cls, string):
        """Is the given string a serialization of this class."""
        raise NotImplementedError("IsSerialization check not implemented")


class MultiMinded(Agent):
    """A multi-minded agent's valuation is defined by an XOR of valued bundles.

    Attributes:
      - xor (XOR): values for distinct bundles

    """

    rand = random.Random(1) # Make a consistent random number generator

    def __init__(self, terms, aid=None):
        super(MultiMinded, self).__init__(aid)
        self.xor = Xor(dict(terms))
        self.items = set()
        for (b, v) in self.xor.list_terms():
            self.items.update(b.items)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{%s %s}" % (self.__class__.__name__, str(self.xor))

    def valueq(self, bundle):
        """Issues a value query to the agent.

        Args:
          - bundle (Bundle): bundle whose value is queried

        Returns:
          float: value of the bundle

        """
        val = max([v for (b, v) in self.xor.list_terms()
                   if b <= bundle] + [0.0])
        return float(val)

    def demandq(self, prices, proposed=None, epsilon=0.0):
        """Issues a demand query to the agent.

        Args:
          - prices (Prices): the bundle prices
          - proposed (optional[Bundle]): proposed bundle
          - epsilon (float): tolerance for accepting proposed bundle

        Returns:
          Bundle: a utility-maximizing bundle, or the proposed
          bundle if it maximizes utility to within the given
          epsilon tolerance.

        """
        max_util = max(v - prices.price(b) for (b, v) in self.xor.list_terms())
        max_util = max(float(max_util), 0.0)
        if proposed is not None:
            proposed_util = self.valueq(proposed) - prices.price(proposed)
            if proposed_util >= max_util - epsilon - 1e-6:
                return proposed
        demand_set = [b for (b, v) in self.xor.list_terms()
                      if v - prices.price(b) >= max_util - 1e-6]
        return demand_set[0] if demand_set else Bundle([])

    def demandq_heuristic(self, prices, pool_num,
                          proposed=None, epsilon=0.0):
        """Randomly select a bundle from a pool of the top best bundles by
        utility."""
        max_util = max(v - prices.price(b) for (b, v) in self.xor.list_terms())
        max_util = max(float(max_util), 0.0)
        if proposed is not None:
            proposed_util = self.valueq(proposed) - prices.price(proposed)
            if proposed_util >= max_util - epsilon - 1e-6:
                return proposed
        all_utils = [(v - prices.price(b), b) for (b, v) in self.xor.list_terms()]
        all_utils.sort(reverse=True)
        top_bundles = [b for (u,b) in all_utils[:pool_num]]
        if all_utils[0][0] >= epsilon - 1e-6:
            return MultiMinded.rand.choice(top_bundles)
        else:
            return Bundle([])

    def demandq_chain(self, prices, proposed=None, epsilon=0.0):
        """Chooses a bundle using the BestChain method."""
        max_util = max(v - prices.price(b) for (b, v) in self.xor.list_terms())
        max_util = max(float(max_util), 0.0)
        if proposed is not None:
            proposed_util = self.valueq(proposed) - prices.price(proposed)
            if proposed_util >= max_util - epsilon - 1e-6:
                return proposed
        bundles = []
        for item in self.items:
            bundle = set([item])
            remaining_items = set(self.items)
            remaining_items.remove(item)
            while remaining_items:
                candidate_bundles = [(bundle | set([i]), i) for i in remaining_items]
                candidate_aus = [(self.valueq(Bundle(b))/len(b), b, i) for (b, i) in candidate_bundles]
                best_au = max(candidate_aus)
                if best_au[0] >= self.valueq(Bundle(bundle))/len(bundle):
                    bundle = best_au[1]
                    remaining_items.remove(best_au[2])
                else:
                    break
            bundles.append(bundle)
        best_bundle = max((self.valueq(Bundle(b)) - prices.price(b), b) for b in bundles)
        if best_bundle[0] >= epsilon - 1e-6:
            return Bundle(best_bundle[1])
        else:
            return Bundle([])
        
    def demandsetq(self, prices, proposed=None, epsilon=0.0):
        max_util = max(v - prices.price(b) for (b, v) in self.xor.list_terms())
        max_util = max(float(max_util), 0.0)
        # demand_set = set(b for (b, v) in self.xor.list_terms()
        #                  if v - prices.price(b) >= max_util - 1e-6)
        demand_set = set(b for (b, v) in self.xor.list_terms()
                         if v - prices.price(b) >= max_util - epsilon - 1e-6)
        if max_util <= 1e-6 + epsilon:
            demand_set.add(Bundle([]))
        if proposed is not None:
            proposed_util = self.valueq(proposed) - prices.price(proposed)
            if proposed_util >= max_util - epsilon - 1e-6:
                demand_set.add(proposed)
        return demand_set

    def serialize(self):
        """Serializes the agent."""
        def bundletostr(b):
            return str(sorted(b.items))\
                .replace('[','(').replace(']',')').replace(' ','')
        def sortkey(kv):
            # Default sort on a set doesn't do the right thing, so convert
            # to a tuple and include the length.
            ret = [len(kv[0])]
            ret.extend(kv[0])
            return tuple(ret)
            
        xorstr = ";".join([bundletostr(b)+":"+str(v) \
                           for b,v in sorted(self.xor.list_terms(),\
                                                 key=sortkey)])
        return "{" + self.__class__.__name__ + " {" + xorstr + "}}"

    @classmethod
    def _deserialize(cls, string):
        """Factory for this class based on a string."""
        def inbracket(s): # substring to inside brackets
            start_idx = s.find('{')
            end_idx = s.rfind('}')
            if start_idx == -1 or end_idx == -1:
                raise ValueError("String should contain brackets: "+s)
            return s[start_idx+1:end_idx]
        def tuplify(s):
            return tuple(map(int, s[1:-1].split(',')))
        xorstr = inbracket(inbracket(string)) # the xor portion
        xordict = {tuplify(k):float(v) for k,v in \
                       (s.split(':') for s in split(xorstr, ';'))}
        return cls(xordict)

    @classmethod
    def _is_serialization(cls, string):
        """Is the given string a serialization of this class."""
        return string.startswith("{"+cls.__name__)

class SingleMinded(MultiMinded):
    """A single-minded agent's valuation is defined by a bundle and value.

    Attributes:
      - bundle (Bundle): desired bundle
      - value (float): value of desired bundle
      - Can also be called with a single argument that contains a dictionary
        that must have a single entry which is a bundle/value pair
    """

    def __init__(self, bundle, value=None, aid=None):
        if value==None:
            if not isinstance(bundle, dict):
                raise ValueError("Single argument version must be a dict")
            if len(bundle) != 1:
                raise ValueError("Single argument must be size 1 dict")
            self.bundle = next(iter(mydict))
            self.value = bundle[self.bundle]
        else:
            self.bundle = bundle
            self.value = value
        MultiMinded.__init__(self, [(self.bundle, self.value)], aid)

class QuadraticValuation(Agent):
    """A quadratic agent's valuation is defined by a quadratic polynomial.

    Args:
      - poly (Polynomial): quadratic polynomial

    """

    def __init__(self, terms, aid=None, cap=None):
        super(QuadraticValuation, self).__init__(aid)
        self.poly = Polynomial(dict(terms))
        self.cap = cap

    def __repr__(self):
        if self.cap == None:
            return "QuadraticValuation(%r)" % self.poly.terms
        else:
            return "QuadraticValuation(%r cap %i)" % (self.poly.terms, self.cap)

    def __eq__(self, other):
        # agent ids not compared for equality
        if type(self) is not type(other):
            return False
        return (self.poly == other.poly and
                self.cap == other.cap)

    def get_terms_by_size(self, size):
        return self.poly.list_terms(size=size)

    def valueq(self, bundle):
        if self.cap is None or len(bundle) <= self.cap:
            return self._valueq_simple(bundle)
        else:
            return self._valueq_mip(bundle)

    def _valueq_mip(self, bundle):
        items = self.poly.variables()
        bignum = 2 * self._valueq_simple(Bundle(items))
        prices = LinearPrices.initial({(i,): (0.0 if i in bundle else bignum)
                                       for i in items})
        result = self.demandq(prices)
        if not len(result) <= self.cap:
            raise WDError(
                "Demanded bundle does not satisfy cap.")  # pragma: no cover
        return self._valueq_simple(result)

    def _valueq_simple(self, bundle):
        return sum(self.poly[monom]
                   for monom in self.poly
                   if set(monom) <= set(bundle))

    def demandq(self, prices, proposed=None, epsilon=0.0):
        bundle = None
        prices = prices[self.aid]
        if isinstance(prices, PolynomialPrices):
            bundle = self._demandq_polynomial(prices)
        elif isinstance(prices, BundlePrices):
            bundle = self._demandq_bundle(prices)
        else:
            raise ValueError("Prices are unknown type: " + str(prices))
        if proposed is not None:
            util_bundle = self.valueq(bundle) - prices.price(bundle)
            util_proposed = self.valueq(proposed) - prices.price(proposed)
            if util_proposed >= util_bundle - epsilon:
                return proposed
        return bundle
    
    def demandsetq(self, prices, proposed=None, epsilon=0.0):
        return set([self.demandq(prices, proposed, epsilon)])
    
    def _demandq_polynomial(self, prices):
        diff = self.poly - prices.poly
        obj = PolynomialPrices(diff.terms)
        solver = PolynomialPriceWD(obj.poly.variables(), [self.aid])
        demand = Demand()
        demand.demands[self.aid] = []
        solver.formulate(obj, demand)
        # introduce cap on bundle size
        if self.cap is not None:
            lhs = [solver._ivar(item, self.aid) for item in solver.items]
            solver._model += (pulp.lpSum(lhs) <= self.cap)
        # solve
        solution = solver.solve()
        return solution[self.aid]

    def _demandq_bundle(self, prices):
        obj = PolynomialPrices(self.poly.terms)
        solver = PolynomialPriceWD(obj.poly.variables(), [self.aid])
        demand = Demand()
        demand.record(Bundle([]), self.aid)
        solver.formulate(obj, demand)
        # introduce cap on bundle size
        if self.cap is not None:
            lhs = [solver._ivar(item, self.aid) for item in solver.items]
            solver._model += (pulp.lpSum(lhs) <= self.cap)
        # create new special variable
        mvar = pulp.LpVariable('M', lowBound=0)
        # create bundle variables
        bnames = [wd._varname(bundle, self.aid)
                  for bundle in prices.xor.bundles()]
        solver._bvars = pulp.LpVariable.dicts('B', bnames,
                                              lowBound=0, upBound=1,
                                              cat=pulp.LpInteger)
        # constraints linking bundles and items
        constraint = "Price LB, agent {} bundle {}"
        for bundle in prices.xor.bundles():
            lhs = [1.0 * solver._ivar(item, self.aid) for item in bundle]
            lhs += [-1.0 * solver._bvar(bundle, self.aid)]
            solver._model += (pulp.lpSum(lhs) <= len(bundle) - 1,
                              constraint.format(self.aid, bundle))
        # constraints linking special and bundle variables
        constraint = "Special UB, agent {} bundle {}"
        for (b, v) in prices.xor.list_terms():
            solver._model += (v * solver._bvar(b, self.aid) - mvar <= 0,
                              constraint.format(self.aid, b))
        # formulate objective and solve
        solver._model += sum([obj.poly[monom] * solver._tvar(monom, self.aid)
                              for monom in obj.poly.nonzero_monomials()] +
                             [-1.0 * mvar])
        solution = solver.solve()
        return solution[self.aid]

    def serialize(self):
        """Serializes the agent."""
        def monom_str(m):
            if len(m) == 1:
                return str(m).translate(None, "(),")
            else:
                return str(m).replace(' ', '')
        s = "QuadraticValuation "
        term_strs = ['*'.join([repr(c), monom_str(m)])
                     for (m, c) in self.poly.list_terms()]
        s += '+'.join(term_strs)
        # write out any extra variables as json:
        s += " " + json.dumps({'aid': self.aid, 'cap': self.cap})
        return "{" + s + "}"

    @classmethod
    def _deserialize(cls, string):
        """Factory for this class based on a string."""
        def parse_term(t):
            c, m = t.split('*')
            if '(' in t and ')' in t:
                return (eval(m), float(c))
            else:
                return ((int(m),), float(c))
        string = string[1:-1]  # eliminate brackets
        start_idx = string.find('{')
        end_idx = string.find('}')
        if start_idx == -1 or end_idx == -1:
            raise ValueError("String should contain variable dicts.")
        else:
            vardictstr = string[start_idx:end_idx + 1]
            string = string[:start_idx]
            vardict = json.loads(vardictstr)
        _, terms = string.split()
        terms = [parse_term(t) for t in terms.split('+')]
        return cls(dict(terms), aid=vardict['aid'], cap=vardict['cap'])

    @classmethod
    def _is_serialization(cls, string):
        """Is the given string a serialization of this class."""
        return string.startswith("{QuadraticValuation")
