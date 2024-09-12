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

"""Module definining basic auction data structures.

"""

from collections import defaultdict
from collections import OrderedDict

class Bundle(object):
    """A bundle consists of a set of items.

    Attributes:
      - items (frozenset): items in the bundle.

    """

    def __init__(self, items):
        self.items = frozenset(items)

    def __hash__(self):
        return hash(self.items)

    def __str__(self):
        string = str(tuple(self.items)).replace(' ', '')
        return string

    def __repr__(self):
        return "Bundle(%r)" % sorted(list(self.items))

    def __eq__(self, other):
        if not type(other) is type(self):
            return False
        return self.items == other.items

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.items < other.items

    def __le__(self, other):
        return self.items <= other.items

    def __gt__(self, other):
        return self.items > other.items

    def __ge__(self, other):
        return self.items >= other.items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def is_empty(self):
        """Checks whether the bundle contains no items."""
        return not self.items

    def csvable(self):
        string = ""
        for i in self.items:
            string += str(i) + "|"
        return string[:-1]


class Allocation(object):
    """An allocation assigns a bundle (possibly empty) to agents.

   Attributes:
      - alloc (dict[int: Bundle]): mapping from agent ids to bundles.

    """

    def __init__(self, alloc=None):
        if alloc is None:
            self.alloc = {}
        else:
            self.alloc = alloc

    def assign_bundle(self, bundle, aid):
        """Assigns a bundle to an agent.

        Args:
          bundle (Bundle): bundle to assign
          aid (int): agent id

        """
        self.alloc[aid] = bundle

    def assign_item(self, item, aid):
        """Allocates an items to an agent.

        Args:
          item (int): item to allocate
          aid (int): agent id

        """
        if aid in self.alloc:
            items = set(self.alloc[aid].items)
        else:
            items = set()
        items.add(item)
        self.assign_bundle(Bundle(items), aid)

    def assigned(self, aid):
        """Returns whether an agent is assigned a bundle (possibly empty).

        """
        return aid in self.alloc

    def covers(self, items):
        """Returns the bundle in the allocation that contains the set of
        items, or None if there isn't any.

        """
        bundle = Bundle(items)
        for aid in self.alloc:
            if bundle <= self.alloc[aid]:
                return self.alloc[aid]
        return None

    def __eq__(self, other):
        if isinstance(other, Allocation):
            return self.alloc == other.alloc
        return False

    def __iter__(self):
        return iter(self.alloc.values())

    def __getitem__(self, aid):
        return self.alloc[aid]

    def __repr__(self):
        return "Allocation(%r)" % self.alloc

    def __str__(self):
        return '\n'.join('{}: {}'.format(i, b)
                         for i, b in self.alloc.items())

    def summary(self):
        return '{Alloc ' + ','.join('{}:{}'.format(i, len(b))
                                    for i, b in self.alloc.items()) + '}'

class Demand(object):
    """A demand instance maps agents to sets of demanded bundles.

    Attributes:
      demands (dict[int: set[Bundle]]): demand sets of the agents.

    """

    def __init__(self, demands=None):
        if demands is None:
            self.demands = {}
        else:
            self.demands = demands
    
    @staticmethod
    def empty(agents):
        return Demand({aid: set() for aid in agents})

    def record(self, bundle, aid):
        """Records a bundle to an agent's demand set.

        Args:
          bundle (Bundle): bundle to record
          aid (int): agent id

        """
        if aid not in self.demands:
            self.demands[aid] = set()
        self.demands[aid].add(bundle)

    def __eq__(self, other):
        return self.demands == other.demands

    def __getitem__(self, aid):
        if aid in self.demands:
            return self.demands[aid]
        else:
            return set()

    def __repr__(self):
        return "Demand(%r)" % self.demands

    def __str__(self):
        def format_set(s):
            rstr = sorted(str(elt) for elt in s)
            return ' '.join(rstr)
        return '\n'.join('{}: {}'.format(i, format_set(d))
                         for i, d in sorted(self.demands.items()))

    def summary(self):
        return self.__repr__()
        # return '{Demand ' + ','.join('{}:{}'.format(i, len(d))
        #                              for i, d in sorted(self.demands.items())) + '}'

class Polynomial(object):
    """A polynomial consists of terms, which are monomials together with
    coefficients.

    Attributes:
      - terms (dict[tuple, float]): terms in the polynomial

    """

    def __init__(self, terms):
        super(Polynomial, self).__init__()
        self.terms = {}
        for monom in terms:
            canon_monom = tuple(sorted(monom))
            self.terms.setdefault(canon_monom, 0.0)
            self.terms[canon_monom] += terms[monom]

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        if len(self.terms) != len(other.terms):
            return False
        for a, b in zip(sorted(self.terms.keys()),
                        sorted(other.terms.keys())):
            if a != b:
                return False
            va = self.terms[a]
            vb = other.terms[b]
            if abs(va - vb) > 1e-8:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def monomials(self):
        """Provides all monomials."""
        return self.terms.keys()

    def singletons(self):
        """Provides all singleton monomials."""
        return [m for m in self.monomials() if len(m) == 1]

    def nonzero_monomials(self):
        """Provides the monomials with nonzero coefficients."""
        return [monom for monom in self.terms if self.terms[monom]]

    def list_terms(self, size=None):
        """Provides the terms in the polynomial as a list of tuple-float pairs.

        """
        if size is None:
            return self.terms.items()
        ret = {}
        for k in self.terms.keys():
            if len(k) == size:
                ret[k] = self.terms[k]
        return ret.items()

    def variables(self):
        """Provides the variables in the polynomial."""
        vars = set()
        for monom in self.monomials():
            vars |= set(monom)
        return vars

    def __sub__(self, other):
        result = defaultdict(float)
        for (m, c) in self.list_terms():
            result[m] += c
        for (m, c) in other.list_terms():
            result[m] -= c
        return Polynomial(result)

    def __iter__(self):
        return iter(self.monomials())

    def __getitem__(self, monom):
        monom = tuple(sorted(monom))
        return self.terms[monom]

    def __setitem__(self, monom, coef):
        monom = tuple(sorted(monom))
        self.terms[monom] = coef

    def as_ordered_dict(self):
        def _make_string(monoms):
            return '_'.join([str(monom) for monom in monoms])
        lst = [(_make_string(k),self.terms[k]) for k in 
               self.nonzero_monomials()]
        lst.sort(key=lambda x: x[1])
        return OrderedDict(lst)

class Xor(object):
    """An XOR consists of distinct bundles associated with non-negative values.

    Attributes:
      - coefs (dict[Bundle: float]): bundle coefficients

    """

    def __init__(self, coefs):
        super(Xor, self).__init__()
        self.coefs = defaultdict(float)
        self.coefs.update({Bundle(b): coefs[b] for b in coefs})

    def bundles(self):
        """Provides the bundles in the XOR."""
        return self.coefs.keys()

    def values(self):
        """Provides the values in the XOR."""
        return self.coefs.values()

    def __getitem__(self, bundle):
        return self.coefs[Bundle(bundle)]

    def __setitem__(self, bundle, coefficient):
        self.coefs[Bundle(bundle)] = coefficient

    def list_terms(self):
        """Provides the terms in the XOR as a list of bundle-value pairs."""
        return self.coefs.items()

    def __len__(self):
        return len(self.coefs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        def sortkey(kv):
            # Default sort on a set doesn't do the right thing, so convert
            # to a tuple and include the length.
            ret = [len(kv[0])]
            ret.extend(kv[0])
            return tuple(ret)
        return ";".join(str(b) + ":" + str(v)
                        for b, v in sorted(self.coefs.items(), key=sortkey))

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        if len(self.coefs) != len(other.coefs):
            return False
        for a, b in zip(sorted(self.coefs.keys()),
                        sorted(other.coefs.keys())):
            if a != b:
                return False
            va = self.coefs[a]
            vb = other.coefs[b]
            if abs(va - vb) > 1e-8:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def nonzero_bundles(self, eps=1e-9):
        """Provides the monomials with nonzero coefficients."""
        return [b for b in self.bundles() if abs(self.coefs[b])>eps]

    def as_ordered_dict(self):
        def _make_string(b):
            return '_'.join([str(b) for b in b.items])
        lst = [(_make_string(b),self.coefs[b]) for b in 
               self.nonzero_bundles()]
        lst.sort(key=lambda x: x[1])
        return OrderedDict(lst)
