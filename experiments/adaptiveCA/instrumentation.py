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

"""Module defining instrumentation functionality to track auction metrics.

"""

from adaptiveCA.structs import Bundle
from adaptiveCA.prices import PolynomialPrices
from adaptiveCA.prices import PersonalizedPrices
from adaptiveCA.wd import QuadraticAgentWD
from adaptiveCA.wd import BundleAgentWD
from adaptiveCA.agents import MultiMinded
from adaptiveCA.agents import QuadraticValuation
import collections


class AbstractInstrumentation(object):
    """ Abstract class that defines the instrumentation of an auction."""

    def pre_run(self, auction):  # pragma: no cover
        """ Before the auction runs. """
        raise NotImplementedError("Abstract")

    def pre_round(self, auction):  # pragma: no cover
        """ Before a single auction round. """
        raise NotImplementedError("Abstract")

    def post_round(self, auction):  # pragma: no cover
        """ Before a single auction round. """
        raise NotImplementedError("Abstract")

    def post_run(self, auction):  # pragma: no cover
        """ After the auction is over. """
        raise NotImplementedError("Abstract")


class AuctionInstrumentation(AbstractInstrumentation):
    """Instrumentation to keep track of auction metrics.

    Attributes:
      - auction (Auction): auction being tracked

    """

    def __init__(self, auction):
        super(AuctionInstrumentation, self).__init__()
        self.auction = auction

    def _rounds(self):
        """Returns current number of auction rounds."""
        return self.auction.rounds

    def _prices(self):
        """Returns the current prices in the auction if any. """
        return self.auction.prices

    def _total_value(self, allocation):
        """Determines the total value of an allocation.

        Args:
          - allocation (Allocation): the given allocation

        Returns:
          (float) Total value of the allocation to auction agents.

        """
        agents = self.auction.agents
        return sum(agents[aid].valueq(allocation[aid]) for aid in agents)

    def _current_value(self):
        """Returns total value of current auction allocation."""
        return self._total_value(self.auction.allocation)

    def _efficient_value(self):
        """Computes value of efficient allocation for auction agents.

        Returns:
          (float) Value of the efficient allocation.

        """
        items, aids = self.auction.items, self.auction.agents.keys()
        agents = self.auction.agents.values()
        if all(isinstance(agent, MultiMinded) for agent in agents):
            packing = BundleAgentWD(items, aids)
        elif all(isinstance(agent, QuadraticValuation) for agent in agents):
            packing = QuadraticAgentWD(items, aids)
        else:
            raise ValueError("Invalid agent types for WD.")
        packing.formulate(self.auction.agents)
        allocation = packing.solve()
        return self._total_value(allocation)

    def _total_price(self, allocation):
        """Computes the total price of an allocation.

        Returns:
          (float) The price of a given allocation.

        """
        return self.auction.total_price(allocation)


    def _total_revenue(self, allocation):
        """Computes the revenue of an allocation.

        Returns:
          (float) Revenue of a given allocation.

        """
        return self.auction.total_revenue(allocation)

    def _current_total_price(self):
        """Returns the total revenue of current auction allocation."""
        return self._total_price(self.auction.allocation)


    def _current_revenue(self):
        """Returns the total revenue of current auction allocation."""
        return self._total_revenue(self.auction.allocation)

    def _current_ind_util(self):
        """Computes the indirect utility at current auction prices."""
        agents = self.auction.agents
        prices = self.auction.prices
        bundles = {aid: agents[aid].demandq(prices[aid]) for aid in agents}
        agent_util = sum(agents[aid].valueq(bundles[aid]) -
                         prices[aid].price(bundles[aid])
                         for aid in agents)
        seller_util = self._current_revenue()
        return agent_util + seller_util

    def _winners(self):
        """Returns number of winners in the current allocation"""
        return sum(not b.is_empty() for b in self.auction.allocation)

    def _price_degree(self):
        """Returns degree of current prices, if applicable."""
        return self.auction.prices.degree

    def _price_sparsity(self):
        """Returns the number of terms in price description."""
        return self.auction.prices.sparsity

    def _max_agent_value(self):
        """Returns the maximum bundle value over all agents."""
        grand = Bundle(self.auction.items)
        agents = self.auction.agents.values()
        return max(agent.valueq(grand) for agent in agents)

    def _imbalance(self):
        """Returns discrepancy between supply and demand."""
        supply = self.auction.allocation
        demand = self.auction.demand
        diffs = [min(len(supply[i].items ^ d.items) for d in demand[i])
                 for i in self.auction.agents]
        return sum(diffs)

    def _wd_size(self):
        """Returns number of variables and constraints for winner
        determination.

        """
        return self.auction.packing.size()
