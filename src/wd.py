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

"""Module providing functionality to formulate and solve winner
determination problems as integer programs.

"""

import pulp
import adaptiveCA.mpsolve as mpsolve
from adaptiveCA.structs import Bundle
from adaptiveCA.structs import Allocation
from adaptiveCA.structs import Demand
from adaptiveCA.prices import BundlePrices
from adaptiveCA.prices import QuadraticPrices
from adaptiveCA.prices import PersonalizedPrices

EQUALITY = 1e-4


class WDError(Exception):
    """Error related to winner determination."""
    pass


def _varname(items, aid):
    """Provides the variable name corresponding to a sequence of items and
    an agent.

    """
    vname = "{}_{}".format(items, aid)
    if len(vname) > 80:
        return str(abs(hash(vname)) % (10**20))
    return vname
    # return "{}_{}".format(items, aid)


def _epsilon(vals):
    """Computes tie-breaking coefficient on demand terms in the objective.

    Args:
      - vals: values to use in setting coefficient

    """
    epsilon = min([abs(v) for v in vals]) / 1e3 if vals else 0.0
    epsilon += 1e-3
    return epsilon


# -------------------------------------------------------------------------- #

class WD(object):
    """Winner determination instance using a MIP solver.

    Attributes:
      - items (set[int]): set of items to allocate
      - aids (list[int]): agent ids
      - allocation (Allocation): result of winner determination
      - title (str): name for logging

    """

    def __init__(self, items, aids):
        super(WD, self).__init__()
        self.items = items
        self.aids = aids
        self.title = "Price WD"
        self.allocation = None
        # private
        self._model = None

    def formulate(self, prices, demand):
        """Formulates the WD instance with price objective.

        Args:
          - prices (Prices): prices
          - demand (Demand): agent demands for tie breaking

        """
        self._model = pulp.LpProblem(self.title, pulp.LpMaximize)
        self._form_variables(prices, demand)
        self._form_constraints(prices, demand)
        self._form_objective(prices, demand)

    def solve(self):
        """Solves the WD instance.

        Returns
          (Allocation) The computed allocation.

        Raises:
          WDError: If solve status is not optimal.

        """
        wdstatus = mpsolve.solve(self._model, False)
        if wdstatus != 'Optimal':
            raise WDError("Non-optimal WD status: " + wdstatus)
        self._form_allocation()
        return self.allocation

    def _form_variables(self, prices, demand):
        """Formulates the program variables.

        Args:
          - prices (Prices): current prices
          - demand (Demand): agent demands

        """
        raise NotImplementedError("Not Implemented.")

    def _form_constraints(self, prices, demand):
        """Formulates the program constraints.

        Args:
          - prices (Prices): current prices
          - demand (Demand): agent demands

        """

        raise NotImplementedError("Not Implemented.")

    def _form_objective(self, prices, demand):
        """Formulates the program objective.

        Args:
          - prices (Prices): current prices
          - demand (Demand): agent demands

        """
        raise NotImplementedError("Not Implemented.")

    def _form_allocation(self):
        """Forms the allocation given the program solution."""
        raise NotImplementedError("Not Implemented.")

    def size(self):
        """Returns number of variables and constraints."""
        raise NotImplementedError("Not Implemented.")

# -------------------------------------------------------------------------- #


class BundlePriceWD(WD):
    """Winner determination instance for personalized bundle price
    objective.

    """

    def __init__(self, items, aids):
        super(BundlePriceWD, self).__init__(items, aids)
        self.title = "Bundle Price WD"
        # private
        self._vars = None
        self._pbundles = None

    def _var(self, bundle, aid):
        """Defines the bundle variables."""
        return self._vars[_varname(bundle, aid)]

    def _form_variables(self, prices, demand):
        self._pbundles = set([(bundle, aid)
                              for aid in self.aids
                              for bundle in prices[aid].xor.bundles()])
        for aid in self.aids:
            self._pbundles.update((bundle, aid)
                                  for aid in self.aids
                                  for bundle in demand[aid])
        names = [_varname(bundle, aid) for (bundle, aid) in self._pbundles]
        self._vars = pulp.LpVariable.dicts('B', names,
                                           lowBound=0, upBound=1,
                                           cat=pulp.LpInteger)
        return

    def _form_constraints(self, prices, demand):
        # supply constraints
        for item in self.items:
            self._model += (pulp.lpSum(self._var(bundle, aid)
                                       for (bundle, aid) in self._pbundles
                                       if item in bundle) <= 1,
                            "Item {} supply".format(item))
        # demand constraints
        for aid in self.aids:
            self._model += (pulp.lpSum(self._var(bundle, aid)
                                       for (bundle, oid) in self._pbundles
                                       if aid == oid) <= 1,
                            "Agent {} demand".format(aid))
        return

    def _form_objective(self, prices, demand):
        def coeff(bundle, aid):
            bonus = epsilon if bundle in demand[aid] else 0.0
            return prices[aid].price(bundle) + bonus
        values = [v for aid in self.aids
                  for v in prices[aid].xor.values()]
        epsilon = _epsilon(values)
        self._model += pulp.lpSum(coeff(bundle, aid) * self._var(bundle, aid)
                                  for (bundle, aid) in self._pbundles)
        return

    def _form_allocation(self):
        allocation = Allocation()
        empty = Bundle([])
        for aid in self.aids:
            allocation.assign_bundle(empty, aid)
        for (bundle, aid) in self._pbundles:
            if abs(self._var(bundle, aid).value() - 1.0) <= EQUALITY:
                allocation.assign_bundle(bundle, aid)
        self.allocation = allocation

    def size(self):
        nvars = len(self._vars)
        ncons = len(self._model.constraints)
        return nvars, ncons

# -------------------------------------------------------------------------- #


class PolynomialPriceWD(WD):
    """Winner determination instance for polynomial price objective
    (possibly personalized).

    """

    def __init__(self, items, aids):
        super(PolynomialPriceWD, self).__init__(items, aids)
        self.items = items
        self.aids = aids
        # private
        self._ivars = None
        self._bvars = None
        self._tvars = None

    def _ivar(self, item, aid):
        """Provides the variable for a given item and agent id."""
        return self._ivars[_varname(item, aid)]

    def _bvar(self, bundle, aid):
        """Provides the variable for a given bundle and agent id."""
        return self._bvars[_varname(bundle, aid)]

    def _tvar(self, monom, aid):
        """Provides the variable for a given monomial and agent id."""
        return self._tvars[_varname(monom, aid)]

    def _form_variables(self, prices, demand):
        # item variables
        inames = [_varname(item, aid)
                  for aid in self.aids
                  for item in self.items]
        self._ivars = pulp.LpVariable.dicts('I', inames,
                                            lowBound=0, upBound=1,
                                            cat=pulp.LpInteger)
        # monom variables
        tnames = [_varname(monom, aid)
                  for aid in self.aids
                  for monom in prices[aid].poly.nonzero_monomials()]
        self._tvars = pulp.LpVariable.dicts('T', tnames,
                                            lowBound=0, upBound=1,
                                            cat=pulp.LpInteger)
        # bundle variables
        bnames = [_varname(bundle, aid)
                  for aid in self.aids
                  for bundle in demand[aid]]
        self._bvars = pulp.LpVariable.dicts('D', bnames,
                                            lowBound=0, upBound=1,
                                            cat=pulp.LpInteger)
        return

    def _form_constraints(self, prices, demand):
        # supply constraints
        for item in self.items:
            self._model += (pulp.lpSum(self._ivar(item, aid)
                                       for aid in self.aids) <= 1,
                            "Item {} supply".format(item))
        # demand constraints
        for aid in self.aids:
            self._model += (pulp.lpSum(self._bvar(bundle, aid)
                                       for bundle in demand[aid]) <= 1,
                            "Agent {} demand".format(aid))
        # constraints linking items and bundles
        for aid in self.aids:
            for bundle in demand[aid]:
                for item in self.items:
                    constraint = "Link UB, agent {} bundle {} item {}"
                    if item in bundle:
                        self._model += (pulp.lpSum(
                            [1.0 * self._bvar(bundle, aid),
                             -1.0 * self._ivar(item, aid)]) <= 0,
                            constraint.format(aid, bundle, item))
                    else:
                        self._model += (pulp.lpSum(
                            [1.0 * self._bvar(bundle, aid),
                             1.0 * self._ivar(item, aid)]) <= 1,
                            constraint.format(aid, bundle, item))

        # constraints linking items and terms
        for aid in self.aids:
            monoms = prices[aid].poly.nonzero_monomials()
            for monom in monoms:
                lhs = [self._ivar(item, aid) for item in monom]
                lhs += [-1.0 * self._tvar(monom, aid)]
                self._model += (pulp.lpSum(lhs) <= len(monom) - 1,
                                "Term LB, agent {} monom {}".format(aid,
                                                                    monom))
                for item in monom:
                    constraint = "Term UB, agent {} monom {} item {}"
                    self._model += (pulp.lpSum(
                        [1.0 * self._tvar(monom, aid),
                         -1.0 * self._ivar(item, aid)]) <= 0,
                        constraint.format(aid, monom, item))
        return

    def _form_objective(self, prices, demand):
        epsilon = _epsilon([prices[aid].price(Bundle([item]))
                            for item in self.items
                            for aid in self.aids])
        telts = [prices[aid].poly[monom] * self._tvar(monom, aid)
                 for aid in self.aids
                 for monom in prices[aid].poly.nonzero_monomials()]
        belts = [epsilon * self._bvar(bundle, aid)
                 for aid in self.aids
                 for bundle in demand[aid]]
        self._model += pulp.lpSum(telts + belts)

    def _form_allocation(self):
        allocation = Allocation()
        empty = Bundle([])
        for aid in self.aids:
            allocation.assign_bundle(empty, aid)
        for aid in self.aids:
            for item in self.items:
                if abs(self._ivar(item, aid).value() - 1.0) <= EQUALITY:
                    allocation.assign_item(item, aid)
        self.allocation = allocation

    def size(self):
        nvars = len(self._ivars) + len(self._bvars) + len(self._tvars)
        ncons = len(self._model.constraints)
        return nvars, ncons


# -------------------------------------------------------------------------- #

class BundleAgentWD(WD):
    """Winner determination among multi-minded agents.

    """

    def __init__(self, items, aids):
        super(BundleAgentWD, self).__init__(items, aids)
        self.title = "Bundle Agent WD"
        # private
        self._packing = None

    def formulate(self, agents):
        """Formulates the WD instance with agent valuation objective.

        Args:
          - agents (dict[int: MultiMinded) the multiminded agents

        """
        prices = PersonalizedPrices(
            {aid: BundlePrices(agents[aid].xor.coefs)
             for aid in agents})
        self._packing = BundlePriceWD(self.items, self.aids)
        self._packing.formulate(prices, demand=Demand())

    def solve(self):
        """Solves the WD instance.

        Returns
          (Allocation) The computed allocation.

        Raises:
          WDError: If solve status is not optimal.

        """
        return self._packing.solve()

    def size(self):
        return self._packing.size()

# -------------------------------------------------------------------------- #


class QuadraticAgentWD(WD):
    """Winner determination among quadratic agents.

    """

    def __init__(self, items, aids):
        super(QuadraticAgentWD, self).__init__(items, aids)
        self.title = "Polynomial Agent WD"
        # private
        self._packing = None

    def formulate(self, agents):
        """Formulates the WD instance with agent valuation objective.

        Args:
          - agents (dict[int: QuadraticValuation) the quadratic agents.

        """
        prices = PersonalizedPrices(
            {aid: QuadraticPrices(agents[aid].poly.terms)
             for aid in agents})
        self._packing = PolynomialPriceWD(self.items, self.aids)
        self._packing.formulate(prices, demand=Demand())

    def solve(self):
        """Solves the WD instance.

        Returns
          (Allocation) The computed allocation.

        Raises:
          WDError: If solve status is not optimal.

        """
        return self._packing.solve()

    def size(self):
        return self._packing.size()
