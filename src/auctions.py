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

"""Module defining various auctions schemes.

"""

from adaptiveCA.structs import Bundle, Allocation, Demand
from adaptiveCA.prices import LinearPrices
from adaptiveCA.prices import QuadraticPrices
from adaptiveCA.prices import BundlePrices
from adaptiveCA.prices import SimpleBundlePrices
from adaptiveCA.prices import PolynomialPrices
from adaptiveCA.prices import PersonalizedPrices
from adaptiveCA.wd import PolynomialPriceWD
from adaptiveCA.wd import BundlePriceWD
from adaptiveCA.wd import WDError
import adaptiveCA.mpsolve as mpsolve

import math
import logging
import time
from collections import defaultdict
import pulp
import itertools
from numpy import median

class PriceExpansionError(Exception):
    pass

class PriceExpressivityError(PriceExpansionError):
    pass

def xvarname(items, aid):
    """Provides the variable name corresponding to a sequence of items and
    an agent.

    """
    vname = "{}_{}".format(items, aid)
    if len(vname) > 80:
        return str(abs(hash(vname)) % (10**20))
    return vname

def yvarname(allocation, agents):
    vname = "_".join(str(allocation[agent]) for agent in agents)
    if len(vname) > 80:
        return str(abs(hash(vname)) % (10**20))
    return vname

class Auction(object):
    """Implementation of generic auction procedure.

    Attributes:
      - items (list[int]): items to allocate
      - agents (dict[int: Agent]): agents indexed by id
      - rounds (int): number of elapsed rounds
      - allocation (Allocation): current allocation
      - demand (Demand): current agent demands

    """

    def __init__(self, items, agents, instrumentation=None):
        super(Auction, self).__init__()
        self.items = items
        self.agents = agents
        self.instrumentation = instrumentation
        self.rounds = 0
        self.demand = Demand()
        self.prices = None
        self.epsilon = None
        self.maxiter = 1000
        self.maxtime = 1e9
        self.status = 'NotRun'
        # initialize allocation
        self.allocation = Allocation()
        empty = Bundle([])
        for aid in agents:
            self.allocation.assign_bundle(empty, aid)

    def set_instrumentation(self, instrumentation):
        self.instrumentation = instrumentation

    def run(self):
        """Runs the auction.

        Returns:
          (Allocation) Allocation of items to the agents.

        """
        if self.instrumentation:
            self.instrumentation.pre_run(self)
        self.start_time = time.clock()
        for round_count in range(self.maxiter):

            rem_time = time.clock()
            if self.instrumentation:
                self.instrumentation.pre_round(self)
            rem_time = time.clock() - rem_time
            self.start_time += rem_time
            
            try:
                balance = self.round()
            except PriceExpressivityError:
                self.status = 'PersonalPriceRequired'
                break;

            rem_time = time.clock()
            if self.instrumentation:
                self.instrumentation.post_round(self)
            rem_time = time.clock() - rem_time
            self.start_time += rem_time

            if balance:
                self.status = 'Balance'
                break
            curr_time = time.clock()
            if curr_time - self.start_time > self.maxtime:
                print 'Time limit Exceeded:', (curr_time - self.start_time)
                self.status = 'MaxTime'
                break
        if round_count == self.maxiter - 1:
            self.status = 'MaxIter'
        if self.instrumentation:
            self.instrumentation.post_run(self)
        return self.allocation

    def round(self):
        """Executes an auction round.

        Returns:
          (bool) Whether supply matches demand at this round.

        """
        self.rounds += 1
        logging.info('-' * 10 + " ROUND %d " + '-' * 10, self.rounds)
        logging.info("Prices\n%s\n", self.prices)
        # collect agent bids
        self._bids()
        #logging.info("Bids\n%s\n", self.demand)
        logging.info("Bids\n%s", self.demand.summary())
        # solve winner determination
        self._wd()
        logging.info("Allocation\n%s", self.allocation)
        #logging.info("Allocation %s", self.allocation.summary())
        
        # check whether supply matches demand
        if self.instrumentation:
            logging.info("Revenue\n%s\n",
                         self.instrumentation._current_revenue())
        if self._balance():
            return True
        # update prices
        self._update()
        return False

    def _balance(self):
        """Checks whether each agent is satisfied with the current allocation.

        Returns:
          (bool) Whether each bundle in the allocation is in
          the respective agent's epsilon-demand set.

        """
        for aid in self.agents:
            allocated = self.allocation[aid]
            demanded = self.agents[aid].demandq(self.prices[aid],
                                                proposed=allocated,
                                                epsilon=self.epsilon)
            if demanded != allocated:
                return False
        return True

    def _bids(self):
        """Records each agent's bid at the current prices."""
        raise NotImplementedError("Not implemented.")

    def _wd(self):
        """Solves the winner determination problem at the current prices."""
        raise NotImplementedError("Not implemented.")

    def _update(self):
        """Updates prices given current allocation and demands."""
        raise NotImplementedError("Not implemented.")

    def total_price(self, allocation=None):
        """ Calculate the total price of allocation at the current prices.
            Use current allocation if no allocation specified.
        """
        if allocation == None:
            allocation = self.allocation
        return sum(self.prices[aid].price(allocation[aid])
                   for aid in self.agents)

    def total_revenue(self, allocation=None):
        """ Calculate the total revenue of allocation at the current prices.
            Use current allocation if no allocation specified.
         """
        if allocation == None:
            allocation = self.allocation

        total = 0
        for aid in self.agents:
            demanded = self.agents[aid].demandq(self.prices[aid],
                                                proposed=allocation[aid],
                                                epsilon=self.epsilon)
            if allocation[aid] == demanded:
                p = self.prices[aid].price(allocation[aid])
                total += p
                total -= min(self.epsilon, max(0, p))
        return total
# -------------------------------------------------------------------------- #


class SubgradientAuction(Auction):
    """Implementation of subgradient auction procedure.

    Attributes:
      - epsilon (float): tolerance for best-response
      - scale (float): step size scaling

    """

    def __init__(self, items, agents, epsilon, scale):
        super(SubgradientAuction, self).__init__(items, agents)
        self.epsilon = epsilon
        self.scale = scale
        self.packing = None
        # One of 'default', 'heuristic', 'chain'
        self.bidding_strategy = 'default'
        # Number of bundles to choose from for heuristic strategy.
        self.heuristic_pool_num = 5

    def _bids(self):
        self.demand = Demand()
        for aid in self.agents:
            if self.bidding_strategy == 'default':
                bid = self.agents[aid].demandq(self.prices[aid], epsilon=0.0)
                self.demand.record(bid, aid)
            elif self.bidding_strategy == 'heuristic':
                bid = self.agents[aid].demandq_heuristic(self.prices[aid],
                                                         self.heuristic_pool_num,
                                                         epsilon=0.0)
                self.demand.record(bid, aid)
            elif self.bidding_strategy == 'chain':
                bid = self.agents[aid].demandq_chain(self.prices[aid], epsilon=0.0)
                self.demand.record(bid, aid)
            else:
                raise ValueError("Invalid bidding strategy.")
        return

    def _wd(self):
        self.packing = PolynomialPriceWD(self.items, self.agents.keys())
        self.packing.formulate(self.prices, self.demand)

        logger = logging.getLogger("WD")
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug("WD Formulation: %s", self.packing._model)

        self.allocation = self.packing.solve()

    def _update(self):
        increment = self.scale / math.sqrt(self.rounds)
        logging.debug("Increment = %.8f", increment)
        demand_side = [list(self.demand[aid]).pop()
                       for aid in self.agents]
        supply_side = self.allocation
        for bundle in demand_side:
            self.prices.update(bundle, increment)
        for bundle in supply_side:
            self.prices.update(bundle, -increment)
        return


class LinearSubgradientAuction(SubgradientAuction):
    """Implementation of linear-price subgradient auction.

    Attributes:
      - prices (LinearPrices): current prices

    """

    def __init__(self, items, agents, epsilon, stepc, **kwargs):
        super(LinearSubgradientAuction, self).__init__(
            items, agents, epsilon, stepc)
        self.prices = LinearPrices.initial(items)

class QuadraticSubgradientAuction(SubgradientAuction):
    """Implementation of quadratic-price subgradient auction.

    Attributes:
      - prices (QuadraticPrices): current prices

    """

    def __init__(self, items, agents, epsilon, stepc, **kwargs):
        super(QuadraticSubgradientAuction, self).__init__(
            items, agents, epsilon, stepc)
        self.prices = QuadraticPrices.initial(items)


class AdaptiveSubgradientAuction(SubgradientAuction):
    """Implementation of polynomial price auction with adaptive monomial expansion.

    Attributes:
      - prices (PolynomialPrices): current prices
      - epoch (int): epoch length for price expansion
      - expanded (set[tuple]): expanded terms

    """

    def __init__(self, items, agents, epsilon, stepc, epoch, **kwargs):
        super(AdaptiveSubgradientAuction, self).__init__(
            items, agents, epsilon, stepc)
        self.prices = PolynomialPrices({(item,): 0.0 for item in items})
        self.epoch = epoch
        self.expanded = set()

    def _update(self):
        super(AdaptiveSubgradientAuction, self)._update()
        # only update at epoch end
        if self.rounds % self.epoch != 0:
            return
        # find top monomial by coefficient weight
        terms = self.prices.poly.terms
        monoms = sorted([(abs(terms[m]), m) for m in terms
                         if m not in self.expanded],
                        reverse=True)
        # exit if no monomial to expand
        if not monoms:
            return
        # expand monomial
        _, top = monoms[0]
        logging.info("Price expansion\n%s\n", top)
        # for m in list(terms):
        for m in self.prices.poly.singletons():
            expm = tuple(sorted(set(m + top)))
            if expm not in terms:
                terms[expm] = 0.0
            # self.expanded.add(expm)
        self.expanded.add(top)

# -------------------------------------------------------------------------- #


class HeuristicAuction(Auction):
    """Implementation of subgradient auction with heuristic winner
    determination which only seeks to allocate bundles that have been
    bid on in past rounds.

    Attributes:
      - epsilon (float): tolerance for best-response
      - scale (float): step size scaling

    """

    def __init__(self, items, agents, epsilon, scale):
        super(HeuristicAuction, self).__init__(items, agents)
        self.epsilon = epsilon
        self.scale = scale
        self.packing = None
        # to record bundles bid on
        self._observed = Demand()
        # One of 'default', 'heuristic', 'chain'
        self.bidding_strategy = 'default'
        # Number of bundles to choose from for heuristic strategy.
        self.heuristic_pool_num = 5

    def _bids(self):
        self.demand = Demand()
        for aid in self.agents:
            if self.bidding_strategy == 'default':
                bids = self.agents[aid].demandsetq(self.prices[aid], epsilon=0.0)
                for bid in bids:
                    self.demand.record(bid, aid)
                    self._observed.record(bid, aid)
            elif self.bidding_strategy == 'heuristic':
                bid = self.agents[aid].demandq_heuristic(self.prices[aid],
                                                         self.heuristic_pool_num,
                                                         epsilon=0.0)
                self.demand.record(bid, aid)
                self._observed.record(bid, aid)
            elif self.bidding_strategy == 'chain':
                bid = self.agents[aid].demandq_chain(self.prices[aid], epsilon=0.0)
                self.demand.record(bid, aid)
                self._observed.record(bid, aid)
            else:
                raise ValueError("Invalid bidding strategy.")
        return

    def _wd(self):
        self.packing = BundlePriceWD(self.items, self.agents.keys())
        agent_xors = {}
        for aid in self.agents:
            bterms = {bundle: self.prices[aid].price(bundle)
                      for bundle in self._observed[aid]}
            #agent_xors[aid] = BundlePrices(bterms)
            agent_xors[aid] = SimpleBundlePrices(bterms)
        objective = PersonalizedPrices(agent_xors)
        self.packing.formulate(objective, self.demand)
        self.allocation = self.packing.solve()

    def _update(self):
        increment = self.scale / math.sqrt(self.rounds)
        logging.debug("Increment = %.8f", increment)
        for aid in self.agents:
            demanded = list(self.demand[aid]).pop()
            self.prices[aid].update(demanded, increment)
            supplied = self.allocation[aid]
            self.prices[aid].update(supplied, -increment)
        return


class LinearHeuristicAuction(HeuristicAuction):
    """Implementation of linear-price heuristic subgradient auction.

    Attributes:
      - prices (LinearPrices): current prices

    """

    def __init__(self, items, agents, epsilon, stepc, **kwargs):
        super(LinearHeuristicAuction, self).__init__(
            items, agents, epsilon, stepc)
        self.prices = LinearPrices.initial(items)


class QuadraticHeuristicAuction(HeuristicAuction):
    """Implementation of quadratic-price heuristic subgradient auction.

    Attributes:
      - prices (QuadraticPrices): current prices

    """

    def __init__(self, items, agents, epsilon, stepc, **kwargs):
        super(QuadraticHeuristicAuction, self).__init__(
            items, agents, epsilon, stepc)
        self.prices = QuadraticPrices.initial(items)


class AdaptiveHeuristicAuction(HeuristicAuction):
    """Implementation of polynomial price heuristic auction with adaptive
    monomial expansion.

    Attributes:
      - prices (PolynomialPrices): current prices
      - epoch (int): epoch length for price expansion
      - expanded (set[tuple]): expanded terms

    """

    def __init__(self, items, agents, epsilon, stepc, epoch, **kwargs):
        super(AdaptiveHeuristicAuction, self).__init__(
            items, agents, epsilon, stepc)
        self.prices = PolynomialPrices({(item,): 0.0 for item in items})
        self.epoch = epoch
        self.expanded = set()

    def _update(self):
        super(AdaptiveHeuristicAuction, self)._update()
        # only update at epoch end
        if self.rounds % self.epoch != 0:
            return
        # find top monomial by coefficient weight
        terms = self.prices.poly.terms
        monoms = sorted([(abs(terms[m]), m) for m in terms
                         if m not in self.expanded],
                        reverse=True)
        # exit if no monomial to expand
        if not monoms:
            return
        # expand monomial
        _, top = monoms[0]
        logging.info("Price expansion\n%s\n", top)
        # for m in list(terms):
        for m in self.prices.poly.singletons():
            expm = tuple(sorted(set(m + top)))
            if expm not in terms:
                terms[expm] = 0.0
            # self.expanded.add(expm)
        self.expanded.add(top)


class AdaptiveCuttingAuction(HeuristicAuction):
    """Implementation of polynomial price auction with constraint
    generation (cutting plane) price expansion.

    Attributes:
      - prices (PolynomialPrices): current prices
      - epoch (int): epoch length for price expansion

    """
    class RPStruct:
        def __init__(self):
            self.model = None
            self.obj = None
            self.ds_cons = None
            self.agent_cons = None
            self.alloc_cons = None
            self.demand_vars = None
            self.supply_vars = None
            self.last_column_reduced_cost = None

    def __init__(self, items, agents, epsilon, stepc, epoch,
                 expstrat='min',
                 personalized=False,
                 **kwargs):
        super(AdaptiveCuttingAuction, self).__init__(
            items, agents, epsilon, stepc)
        # initialize with anonymous prices
        self.prices = PolynomialPrices({(item,): 0.0 for item in items})
        self.epoch = epoch
        self.rp = None
        self.expstrat = expstrat # min, max, abs
        self.personalized = personalized

    def _update(self):
        super(AdaptiveCuttingAuction, self)._update()
        # only update at epoch end
        if self.rounds % self.epoch == 0:
            expansions = self._price_expansion()
            logging.info("Expansions: %s" % expansions)
            # if expansions:
            #     self.rounds = 0
            for aid, bundle in expansions:
                terms = self.prices[aid].poly.terms
                term = tuple(sorted(set(bundle)))
                if term in terms:
                    raise PriceExpansionError("Expansion term already in polynomial prices: %s, %.8f"
                                              % (term, self.rp.last_column_reduced_cost))
                terms[term] = 0.0

    def _convert_to_personalized_prices(self):
        if self.prices.personalized:
            raise PriceExpansionError("Prices are already personalized.")
        prices = PersonalizedPrices({})
        for aid in self.agents:
            prices[aid] = PolynomialPrices(self.prices.poly.terms)
        self.prices = prices
    
    def _price_expansion(self):
        expansions = set()
        self._solve_restricted_primal()
        if self._rp_test_fractional():
            ds_cons_aids = self.rp.ds_cons.keys()
            if not self.prices.personalized:
                ds_cons_aids = [self.rp.ds_cons.keys()[0]]
            for aid in ds_cons_aids:
                for monom in self.rp.ds_cons[aid]:
                    logging.info("Splitting constraint %s" % (str(monom) + '_' + str(aid)))
                    cuts = self._split_constraint(monom)
                    logging.info("Cuts found %s" % cuts)
                    if self.expstrat == 'min':
                        cuts.sort(key=lambda (b,d): len(b))
                    elif self.expstrat == 'max':
                        cuts.sort(key=lambda (b,d): len(b), reverse=True)
                    elif self.expstrat == 'abs':
                        cuts.sort(key=lambda (b,d): abs(d), reverse=True)
                    else:
                        raise PriceExpansionError("Invalid expansion strategy.")
                    if cuts:
                        expansions.add( (aid, cuts[0][0]) )
            if not expansions:
                #print "Need personalized prices!"
                if self.personalized:
                    self._convert_to_personalized_prices()
                else:
                    raise PriceExpressivityError("No cut found--Need personalized prices.")
        return expansions

    def _formulate_restricted_primal(self):
        self.rp = self.RPStruct()
        self.rp.model = pulp.LpProblem("Restricted Primal", pulp.LpMaximize)
        # objective
        obj = pulp.LpConstraintVar("obj")
        self.rp.model.setObjective(obj)
        self.rp.obj = obj
        # demand=supply constraints
        ds_cons = {}
        if self.prices.personalized:
            for aid in self.agents:
                ds_cons[aid] = {monom: pulp.LpConstraintVar("Monomial_{}_{}".format(monom, aid),
                                                            pulp.LpConstraintEQ, 0)
                                for monom in self.prices[aid].poly.monomials()}
                for monom in ds_cons[aid]:
                    self.rp.model += ds_cons[aid][monom]
        else:
            ds_cons_anon = {monom: pulp.LpConstraintVar("Monomial_{}".format(monom), pulp.LpConstraintEQ, 0)
                            for monom in self.prices.poly.monomials()}
            for monom in ds_cons_anon:
                self.rp.model += ds_cons_anon[monom]
            for aid in self.agents:
                ds_cons[aid] = ds_cons_anon
        self.rp.ds_cons = ds_cons
        # agent constraints
        agent_cons = {aid: pulp.LpConstraintVar("Agent_{}".format(aid), pulp.LpConstraintLE, 1)
                      for aid in self.agents}
        for aid in agent_cons:
            self.rp.model += agent_cons[aid]
        self.rp.agent_cons = agent_cons
        # allocation constraints
        alloc_cons = pulp.LpConstraintVar("Allocation", pulp.LpConstraintLE, 1)
        self.rp.model += alloc_cons
        self.rp.alloc_cons = alloc_cons
        # demand variables
        demand_vars = {}
        for aid in self.agents:
            for bundle in self._observed[aid]:
                dv = pulp.LpVariable(xvarname(bundle, aid), 0, None, pulp.LpContinuous,
                                     pulp.lpSum([int(bundle in self.demand[aid])*obj] +
                                                [int(Bundle(monom) <= bundle)*ds_cons[aid][monom]
                                                 for monom in ds_cons[aid]] +
                                                [int(aid == i)*agent_cons[i] for i in agent_cons] +
                                                [0*alloc_cons]))
                demand_vars[(aid, bundle)] = dv
        self.rp.demand_vars = demand_vars
        # supply variables
        self.rp.supply_vars = {}
        #self._add_column(self.allocation)
        return self.rp

    def _rp_test_fractional(self):
        # print "RP Model Variables"
        # for v in self.rp.model.variables():
        #     print v, v.value()
        for v in self.rp.model.variables():
            if v.value() > 1e-6 and v.value() < 1-1e-6:
                return True
        return False

    def _add_column(self, alloc):
        sv = None
        if self.prices.personalized:
            sv = pulp.LpVariable(yvarname(alloc, self.agents), 0, None, pulp.LpContinuous,
                                 pulp.lpSum([1*self.rp.obj] +
                                            [-int(Bundle(monom) <= alloc[aid])*self.rp.ds_cons[aid][monom]
                                             for aid in self.agents for monom in self.rp.ds_cons[aid]] +
                                            [0*self.rp.agent_cons[i] for i in self.rp.agent_cons] +
                                            [1*self.rp.alloc_cons]))
        else:          
            common_ds_cons = self.rp.ds_cons[self.rp.ds_cons.keys()[0]]
            sv = pulp.LpVariable(yvarname(alloc, self.agents), 0, None, pulp.LpContinuous,
                                 pulp.lpSum([1*self.rp.obj] +
                                            [-int(alloc.covers(monom) is not None)*common_ds_cons[monom]
                                             for monom in common_ds_cons] +
                                            [0*self.rp.agent_cons[i] for i in self.rp.agent_cons] +
                                            [1*self.rp.alloc_cons]))            
        self.rp.supply_vars[alloc] = sv
        return sv

    def _solve_restricted_primal(self):
        self._formulate_restricted_primal()
        max_cols_generated = ( sum(len(self.rp.ds_cons[aid]) for aid in self.rp.ds_cons)
                               + len(self.rp.agent_cons) + 1 + 1e4 )
        cols_generated = 0
        observed_columns = []
        column = self.allocation
        while column is not None:
            logging.info("Generating column\n%s\n", column)
            if column in observed_columns:
              raise PriceExpansionError("Column already generated: %s, %.8f",
                                        column, self.rp.last_column_reduced_cost)
            self._add_column(column)
            observed_columns.append(column)
            cols_generated += 1
            if cols_generated > max_cols_generated:
                raise PriceExpansionError("Too many columns generated.")
            mpsolve.solve(self.rp.model, False, False)

            #import cplex
            #n = [con for con in self.rp.model.constraints]
            #print 'Cplex: ' + str(self.rp.model.solverModel.solution.get_dual_values(n))
            column = self._rp_column_generation()

    def _rp_create_prices(self):
        prices = {}
        if not self.prices.personalized:
            aid0 = self.rp.ds_cons.keys()[0]
            terms = {monom: self.rp.ds_cons[aid0][monom].constraint.pi
                     for monom in self.rp.ds_cons[aid0]}
            prices = PolynomialPrices(terms)
        else:
            terms = {}
            for aid in self.agents:
                terms = {monom: self.rp.ds_cons[aid][monom].constraint.pi
                         for monom in self.rp.ds_cons[aid]}
                prices[aid] = PolynomialPrices(terms)
        return prices

    def _rp_column_generation(self):
        optrev = sum(self.prices[aid].price(self.allocation[aid]) for aid in self.agents)
        M = 100*optrev
        pi_s = self.rp.alloc_cons.constraint.pi
        # formulate rev-maximization problem
        rp_prices = self._rp_create_prices()
        packing = BundlePriceWD(self.items, self.agents.keys())
        agent_xors = {}
        for aid in self.agents:
            bterms = {bundle: rp_prices[aid].price(bundle)
                      for bundle in self._observed[aid]}
            agent_xors[aid] = SimpleBundlePrices(bterms)
        objective = PersonalizedPrices(agent_xors)
        packing.formulate(objective, Demand.empty(self.agents))
        # introduce indicator variable for rev-max allocation
        z = pulp.LpVariable("z", 0, 1, pulp.LpInteger)
        packing._model += (pulp.lpSum(
            [-self.prices[aid].price(bundle)*packing._var(bundle, aid)
             for (bundle, aid) in packing._pbundles] + [M*z]) <= M - optrev + 1e-5,
            "Rev-Max Selection")
        # adjust objective and solve
        packing._model.objective += z - pi_s
        #return packing
        try:
          allocation = packing.solve()
        except WDError as err:
          raise PriceExpansionError("WD Error generating column: %s\n%s" %
                                    (err, packing._model))
        objvalue = packing._model.objective.value()
        #print 'ColGen: Objective value', objvalue
        #print 'M', M
        #print 'optrev', optrev
        #print 'pi_s', pi_s
        self.rp.last_column_reduced_cost = objvalue
        return allocation if (objvalue > 1e-5) else None

    def _split_constraint(self, monom):
        # compute weights
        weights = defaultdict(float)
        for (aid, bundle) in self.rp.demand_vars:
            if Bundle(monom) <= bundle:
                weights[bundle] += self.rp.demand_vars[(aid, bundle)].value()
        for alloc in self.rp.supply_vars:
            coverb = alloc.covers(monom)
            if coverb is not None:
                weights[coverb] -= self.rp.supply_vars[alloc].value()
        # compute discrepancies
        discrepancy = {}
        nodes = weights.keys()
        for n in nodes:
            discrepancy[n] = weights[n]
        for (n1, n2) in itertools.combinations(nodes, 2):
            if n1 < n2:
                discrepancy[n1] += weights[n2]
            if n2 < n1:
                discrepancy[n2] += weights[n1]
        # return split candidates
        return [(b, d) for (b, d) in discrepancy.items() if abs(d) > 1e-6]

# -------------------------------------------------------------------------- #


class IBundle(Auction):
    """Implementation of the iBundle auction.

    Attributes:
      - epsilon (float): step size
      - prices (PersBundlePrices): current prices

    """

    def __init__(self, items, agents, epsilon, **kwargs):
        super(IBundle, self).__init__(items, agents)
        self.epsilon = epsilon
        self.prices = PersonalizedPrices.init_bundle(agents.keys())
        self.demand = Demand()
        self.packing = None

    def _bids(self):
        for aid in self.agents:
            #bids = self.agents[aid].demandsetq(self.prices[aid], epsilon=0.0)
            bids = self.agents[aid].demandsetq(self.prices[aid],
                                               self.allocation[aid],
                                               self.epsilon)
            for bid in bids:
                self.demand.record(bid, aid)
        return

    def _wd(self):
        self.packing = BundlePriceWD(self.items, self.agents.keys())
        self.packing.formulate(self.prices, self.demand)
        self.allocation = self.packing.solve()

    def _update(self):
        increment = self.epsilon
        for aid in self.agents:
            if not self.allocation[aid] in self.demand[aid]:
                for bundle in self.demand[aid]:
                    # self.prices[aid].update(bundle, increment)
                    if (self.agents[aid].valueq(bundle) -
                        self.prices[aid].price(bundle) > -1e-6):
                        self.prices[aid].update(bundle, increment)
                    else:
                        logging.debug('Skipping non-IR price update for agent'+\
                                      ' %d on bundle %s.', aid, bundle)
        return

    def _balance(self):
        return all(self.allocation[aid] in self.demand[aid]
                   for aid in self.agents)

    def total_revenue(self, allocation=None):
        """ Calculate the total revenue of allocation at the current prices.
            Use current allocation if no allocation specified.
         """
        if allocation == None:
            allocation = self.allocation

        total = 0
        for aid in self.agents:
            #demanded = self.agents[aid].demandq(self.prices[aid],
            #                                    proposed=allocation[aid],
            #                                    epsilon=self.epsilon)
            #if allocation[aid] == demanded:
            if allocation[aid] in self.demand[aid]:
                p = self.prices[aid].price(allocation[aid])
                total += p
                total -= min(self.epsilon, max(0, p))
        return total

class LinearClockAuction(LinearSubgradientAuction):
    """ Implements a linear clock auction that works similar to the
        clock phase of the CCA spectrum auctions.

       Note if updating is relative, it is controlled by gamma, if
       it is additive, continue to use stepc
    """

    def __init__(self, items, agents, epsilon, stepc, gamma, \
                 update_prop_excess_demand = False,
                 update_increment_absolute = False,
                 reserve_type = 'max',
                 update_lower=0, update_upper=1e9, **kwargs):
        super(LinearClockAuction, self).__init__(
            items, agents, epsilon, stepc)
        self.stepc = stepc
        self.gamma = gamma
        self.update_prop_excess_demand = update_prop_excess_demand
        self.update_increment_absolute = update_increment_absolute
        self.update_lower = update_lower
        self.update_upper = update_upper

        ### Set the initial value to 1/100 of the maximum sale price.
        if reserve_type == 'max':
            self.init_delta = max([a.max_value() for a in agents.values()])
        elif reserve_type == 'median':
            self.init_delta = median([a.max_value() for a in agents.values()])
        else:
            raise ValueError('unknown reserve_type', reserve_type)
        self.init_delta *= 0.01

    def _balance(self):
        """Checks whether each agent is satisfied with the current allocation.

        Returns:
          (bool) Whether each bundle in the allocation is in
          the respective agent's epsilon-demand set.

        """
        for aid in self.agents:
            allocated = self.allocation[aid]
            demanded = self.agents[aid].demandq(self.prices[aid],
                                                proposed=allocated,
                                                epsilon=self.epsilon)
            #print 'Agent: ' + str(aid)
            #print 'Demanded: ' + str(demanded)
            #print 'Allocated: ' + str(allocated)
            if demanded > allocated:
                return False
        return True

    def _update(self):
        #Figure out what items have excess demand and should be updated:
        excess_demand = defaultdict(int)
        for aid in self.agents:
            for bundle in self.demand[aid]:
                #print 'D: '+str(aid)+": "+str(bundle)+": "+\
                #    str(self.allocation[aid])
                if bundle != self.allocation[aid]:
                    #Don't just check for null alloc: agent may prefer
                    #  a different bundle
                    #print 'Bundle demanded for ' + str(aid) + ": "+ str(bundle)
                    for item in bundle:
                        excess_demand[item]+=1
        #print "Excess Demanded: " + str(excess_demand)

        #Now update the prices
        for item in [item for item in excess_demand if excess_demand[item]!=0]:
            # Pick a price guarded by the stepsize
            increment = \
                (self.stepc if self.update_increment_absolute else self.gamma)*\
                (excess_demand[item] if self.update_prop_excess_demand else 1)
            increment = min(self.update_upper, increment)
            increment = max(self.update_lower, increment)

            #print 'gamma: ' + str(self.gamma)
            #print 'update_upper: ' + str(self.update_upper)
            #print 'update_lower: ' + str(self.update_lower)
            #print 'Updating Prices for: ' + str(item) + " by " + str(increment)

            if self.update_increment_absolute:
                self.prices.update(Bundle([item]), increment)
            else:
                self.prices.update_relative(Bundle([item]), \
                                                increment, self.init_delta)
