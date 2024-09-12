from adaptiveCA.structs import Bundle, Allocation, Demand
from adaptiveCA.wd import WDError
from adaptiveCA.wd import PolynomialPriceWD, BundlePriceWD
from adaptiveCA.wd import QuadraticAgentWD, BundleAgentWD
from adaptiveCA.prices import LinearPrices, QuadraticPrices
from adaptiveCA.prices import BundlePrices
from adaptiveCA.prices import PersonalizedPrices
import sys
import pytest
from adaptiveCA.mpsolve import is_cplex
from adaptiveCA.agents import MultiMinded, QuadraticValuation


def setup_module(module):
    # items
    module.items = [1, 2, 3]
    # agent ids
    module.aids = [1, 2, 3]
    # bundles
    module.b000 = Bundle([])
    module.b100 = Bundle([1])
    module.b010 = Bundle([2])
    module.b001 = Bundle([3])
    module.b110 = Bundle([1, 2])
    module.b101 = Bundle([1, 3])
    module.b011 = Bundle([2, 3])
    module.b111 = Bundle([1, 2, 3])


class TestPersBundleWD:

    def test_tie_breaking(self):
        """Prices:
        1: (010, 2) ; (100, 2) ; (110, 4)
        2: (011, 2) ; (010, 2) ; (101, 3)
        3: (100, 1) ; (001, 1) ; (111, 5)

        Demands:
        1: {100, 110}
        2: {010, 101}
        3: {001, 111}

        Expected allocation:
        [100, 010, 001]
        """
        # prices
        prices = PersonalizedPrices.init_bundle(aids)
        prices[1].update(b010, 2)
        prices[1].update(b100, 2)
        prices[1].update(b110, 4)
        prices[2].update(b011, 2)
        prices[2].update(b010, 2)
        prices[2].update(b101, 3)
        prices[3].update(b100, 1)
        prices[3].update(b001, 1)
        prices[3].update(b111, 5)
        # demands
        demand = Demand()
        demand.record(b100, 1)
        demand.record(b110, 1)
        demand.record(b010, 2)
        demand.record(b101, 2)
        demand.record(b001, 3)
        demand.record(b111, 3)
        # expected allocation
        allocation = Allocation()
        allocation.assign_bundle(b100, 1)
        allocation.assign_bundle(b010, 2)
        allocation.assign_bundle(b001, 3)
        # run wd
        packing = BundlePriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation

    def test_unique_soln(self):
        """Prices:
        1: (010, 1) ; (100, 2) ; (110, 5)
        2: (011, 2) ; (010, 2) ; (101, 4)
        3: (100, 1) ; (001, 2) ; (111, 5)

        Demands:
        1: {100, 110}
        2: {010, 101}
        3: {001, 111}

        Expected allocation:
        [110, 000, 001]
        """
        # prices
        prices = PersonalizedPrices.init_bundle(aids)
        prices[1].update(b010, 1)
        prices[1].update(b100, 2)
        prices[1].update(b110, 5)
        prices[2].update(b011, 2)
        prices[2].update(b010, 2)
        prices[2].update(b101, 4)
        prices[3].update(b100, 1)
        prices[3].update(b001, 2)
        prices[3].update(b111, 5)
        # demands
        demand = Demand()
        demand.record(b100, 1)
        demand.record(b110, 1)
        demand.record(b010, 2)
        demand.record(b101, 2)
        demand.record(b001, 3)
        demand.record(b111, 3)
        # expected allocation
        allocation = Allocation()
        allocation.assign_bundle(b110, 1)
        allocation.assign_bundle(b000, 2)
        allocation.assign_bundle(b001, 3)
        # run wd
        packing = BundlePriceWD(items, aids)
        packing.formulate(prices, demand)
        print packing._model
        result = packing.solve()
        assert result == allocation

    def test_zero_prices(self):
        """Demands:
        1: {010}
        2: {100}
        3: {111}

        Expected allocation:
        [010, 100, 000]

        """
        # prices
        prices = PersonalizedPrices.init_bundle(aids)
        # demand
        demand = Demand()
        demand.record(b010, 1)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # expected allocation
        allocation = Allocation()
        allocation.assign_bundle(b010, 1)
        allocation.assign_bundle(b100, 2)
        allocation.assign_bundle(b000, 3)
        # run wd
        packing = BundlePriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation
        assert packing.size() == (3, 6)


class TestBundleWD:

    def test_tie_breaking(self):
        """Bundle prices:
        (110, 2) ; (011, 2) ; (100, 1) ; (111, 3)

        Demands:
        1: {011}
        2: {110, 100}
        3: {111}

        Expected allocation:
        [011, 100, 000]

        """
        # prices
        prices = BundlePrices.initial()
        prices.update(b110, 2)
        prices.update(b011, 2)
        prices.update(b100, 1)
        prices.update(b111, 3)
        # demand
        demand = Demand()
        demand.record(b011, 1)
        demand.record(b110, 2)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # expected allocation
        allocation = Allocation()
        allocation.assign_bundle(b011, 1)
        allocation.assign_bundle(b100, 2)
        allocation.assign_bundle(b000, 3)
        # run wd
        packing = BundlePriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation

    def test_unique_soln(self):
        """Bundle prices:
        (110, 2) ; (011, 2) ; (100, 1) ; (111, 4)

        Demands:
        1: {011}
        2: {110, 100}
        3: {111}

        Expected allocation:
        [000, 000, 111]

        """
        # prices
        prices = BundlePrices.initial()
        prices.update(b110, 2)
        prices.update(b011, 2)
        prices.update(b100, 1)
        prices.update(b111, 4)
        # demand
        demand = Demand()
        demand.record(b011, 1)
        demand.record(b110, 2)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # expected allocation
        allocation = Allocation()
        allocation.assign_bundle(b000, 1)
        allocation.assign_bundle(b000, 2)
        allocation.assign_bundle(b111, 3)
        # run wd
        packing = BundlePriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation

    def test_zero_prices_1(self):
        """Demands:
        1: {010}
        2: {100}
        3: {111}

        Expected allocation:
        [010, 100, 000]

        """
        # prices
        prices = BundlePrices.initial()
        # demand
        demand = Demand()
        demand.record(b010, 1)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # expected allocation
        allocation = Allocation()
        allocation.assign_bundle(b010, 1)
        allocation.assign_bundle(b100, 2)
        allocation.assign_bundle(b000, 3)
        # run wd
        packing = BundlePriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation

    def test_zero_prices_2(self):
        """Demands:
        1: {010}
        2: {100}
        3: {001, 111}

        Expected allocation:
        [010, 100, 001]

        """
        # prices
        prices = BundlePrices.initial()
        # demand
        demand = Demand()
        demand.record(b010, 1)
        demand.record(b100, 2)
        demand.record(b111, 3)
        demand.record(b001, 3)
        # expected allocation
        allocation = Allocation()
        allocation.assign_bundle(b010, 1)
        allocation.assign_bundle(b100, 2)
        allocation.assign_bundle(b001, 3)
        # run wd
        packing = BundlePriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation

    def test_wd_error(self):
        """Bundle prices:
        (011, MAXFLOAT/2) ; (100, MAXFLOAT/2)

        Demands:
        1: {000}
        2: {000}
        3: {000}

        """
        if not is_cplex():
            # under cplex this segfaults
            with pytest.raises(WDError):
                # prices
                prices = BundlePrices.initial()
                val = sys.float_info.max / 2
                prices.update(b011, val)
                prices.update(b100, val)
                # demand
                demand = Demand()
                demand.record(b000, 1)
                demand.record(b000, 2)
                demand.record(b000, 3)
                # run wd
                packing = BundlePriceWD(items, aids)
                packing.formulate(prices, demand)
                packing.solve()


class TestLinearWD:

    def test_tie_breaking(self):
        """Prices:
         1  2  3
        [2, 3, 4]

        Demands:
        1: {011}
        2: {110, 100}
        3: {111}

        Expected allocation:
        [011, 100, 000]
        """
        # prices
        prices = LinearPrices.initial(items)
        prices.update([1], 2.0)
        prices.update([2], 3.0)
        prices.update([3], 4.0)
        # demand
        demand = Demand()
        demand.record(b011, 1)
        demand.record(b110, 2)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # allocation
        allocation = Allocation()
        allocation.assign_bundle(b011, 1)
        allocation.assign_bundle(b100, 2)
        allocation.assign_bundle(b000, 3)
        # run wd
        packing = PolynomialPriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation
        assert packing.size() == (22, 36)

    def test_zero_prices(self):
        """Prices:
         1  2  3
        [0, 0, 0]

        Demands:
        1: {011}
        2: {110, 100}
        3: {111}

        Expected allocation:
        [011, 100, 000]
        """
        # prices
        prices = LinearPrices.initial(items)
        # demand
        demand = Demand()
        demand.record(b011, 1)
        demand.record(b110, 2)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # allocation
        allocation = Allocation()
        allocation.assign_bundle(b011, 1)
        allocation.assign_bundle(b100, 2)
        allocation.assign_bundle(b000, 3)
        # run wd
        packing = PolynomialPriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation


class TestQuadraticWD:

    def test_tie_breaking(self):
        """Prices:
         1  2  3  12  13  23
        [1, 1, 1,  1,  0,  0]

        Demands:
        1: {011, 001}
        2: {110, 100}
        3: {111}

        Expected allocation:
        [001, 110, 000]
        """
        # prices
        prices = QuadraticPrices.initial(items)
        prices.update([1, 2], 1)
        prices.update([3], 1)
        # demand
        demand = Demand()
        demand.record(b011, 1)
        demand.record(b001, 1)
        demand.record(b110, 2)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # allocation
        allocation = Allocation()
        allocation.assign_bundle(b001, 1)
        allocation.assign_bundle(b110, 2)
        allocation.assign_bundle(b000, 3)
        # run wd
        packing = PolynomialPriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation

    def test_unique_soln(self):
        """Prices:
         1  2  3  12  13  23
        [1, 2, 2,  1,  0,  1]

        Demands:
        1: {011, 001}
        2: {110, 100}
        3: {111}

        Expected allocation:
        [000, 000, 111]
        """
        # prices
        prices = QuadraticPrices.initial(items)
        prices.update([1, 2], 1)
        prices.update([3], 1)
        prices.update([2, 3], 1)
        # demand
        demand = Demand()
        demand.record(b011, 1)
        demand.record(b001, 1)
        demand.record(b110, 2)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # allocation
        allocation = Allocation()
        allocation.assign_bundle(b000, 1)
        allocation.assign_bundle(b000, 2)
        allocation.assign_bundle(b111, 3)
        # run wd
        packing = PolynomialPriceWD(items, aids)
        packing.formulate(prices, demand)
        print packing._model
        result = packing.solve()
        assert result == allocation

    def test_zero_prices(self):
        """Prices:
         1  2  3  12  13  23
        [0, 0, 0,  0,  0,  0]

        Demands:
        1: {011}
        2: {110, 100}
        3: {111}

        Expected allocation:
        [011, 100, 000]
        """
        # prices
        prices = QuadraticPrices.initial(items)
        # demand
        demand = Demand()
        demand.record(b011, 1)
        demand.record(b110, 2)
        demand.record(b100, 2)
        demand.record(b111, 3)
        # allocation
        allocation = Allocation()
        allocation.assign_bundle(b011, 1)
        allocation.assign_bundle(b100, 2)
        allocation.assign_bundle(b000, 3)
        # run wd
        packing = PolynomialPriceWD(items, aids)
        packing.formulate(prices, demand)
        result = packing.solve()
        assert result == allocation


class TestBundleAgentWD:

    def test_solve(self):
        """Agents:
        1: (110, 2.0) ; (100, 1.0)
        2: (101, 2.5) ; (001, 2.0)
        3: (111, 3.0) ; (010, 0.5)

        Expected allocation:
        [110, 001, 000]

        """
        # agents
        xor1 = {b110: 2.0, b100: 1.0}
        agent1 = MultiMinded(xor1)
        xor2 = {b101: 2.5, b001: 2.0}
        agent2 = MultiMinded(xor2)
        xor3 = {b111: 3.0, b010: 0.5}
        agent3 = MultiMinded(xor3)
        agents = {1: agent1, 2: agent2, 3: agent3}
        # allocation
        allocation = Allocation({1: b110, 2: b001, 3: b000})
        # solve
        packing = BundleAgentWD(items, aids)
        packing.formulate(agents)
        result = packing.solve()
        assert result == allocation
        assert packing.size() == (6, 6)


class TestQuadraticAgentWD:

    def test_solve(self):
        """Agents:
        1: (1,): 1.0 ; (1,2): 1.0
        2: (3,): 2.0 ; (1,3): 0.5
        3: (2,): 0.5 ; (1,3): 2.0

        Expected allocation:
        [110, 001, 000]

        """
        # agents
        poly1 = {(1,): 1.0, (1, 2): 1.0}
        agent1 = QuadraticValuation(poly1)
        poly2 = {(3,): 2.0, (1, 3): 0.5}
        agent2 = QuadraticValuation(poly2)
        poly3 = {(2,): 0.5, (1, 3): 2.0}
        agent3 = QuadraticValuation(poly3)
        agents = {1: agent1, 2: agent2, 3: agent3}
        # allocation
        allocation = Allocation({1: b110, 2: b001, 3: b000})
        # solve
        packing = QuadraticAgentWD(items, aids)
        packing.formulate(agents)
        result = packing.solve()
        assert result == allocation
        assert packing.size() == (15, 21)
