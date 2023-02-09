from adaptiveCA.structs import Bundle
from adaptiveCA.structs import Allocation
from adaptiveCA.structs import Demand
from adaptiveCA.agents import SingleMinded
from adaptiveCA.auctions import LinearSubgradientAuction
from adaptiveCA.auctions import QuadraticSubgradientAuction
from adaptiveCA.auctions import LinearHeuristicAuction
from adaptiveCA.auctions import QuadraticHeuristicAuction
from adaptiveCA.auctions import IBundle
from adaptiveCA.prices import LinearPrices
from adaptiveCA.prices import QuadraticPrices
from adaptiveCA.prices import PersonalizedPrices


def setup_module(module):
    """Agents:
    1: (110, 3)
    2: (101, 3)
    3: (011, 3)
    4: (111, 4)

    Demands:
    1: {000}
    2: {000}
    3: {000}
    4: {000}

    Allocation:
    [000, 000, 000, 000, 000]
    """
    # items
    module.items = [1, 2, 3]
    # bundles
    module.b000 = Bundle([])
    module.b100 = Bundle([1])
    module.b010 = Bundle([2])
    module.b001 = Bundle([3])
    module.b110 = Bundle([1, 2])
    module.b101 = Bundle([1, 3])
    module.b011 = Bundle([2, 3])
    module.b111 = Bundle([1, 2, 3])
    # agents
    agent1 = SingleMinded(b110, 3, 1)
    agent2 = SingleMinded(b101, 3, 2)
    agent3 = SingleMinded(b011, 3, 3)
    agent4 = SingleMinded(b111, 4, 4)
    module.agents = {1: agent1,
                     2: agent2,
                     3: agent3,
                     4: agent4}
    # demands
    module.demand = Demand()
    demand.record(b000, 1)
    demand.record(b000, 2)
    demand.record(b000, 3)
    demand.record(b000, 4)


class TestLinearSubgradientAuction():

    def setup_method(self, method):
        self.auction = LinearSubgradientAuction(items, agents, 0.0, 1.0)
        self.auction.demand = demand
        self.auction.prices = LinearPrices.initial(items)
        self.auction.prices.update(items, 1.0)

    def test_bid(self):
        self.auction._bids()
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        assert self.auction.demand == demand

    def test_wd(self):
        demand = Demand()
        demand.record(b000, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        allocation = Allocation({1: b000,
                                 2: b000,
                                 3: b000,
                                 4: b111})
        self.auction._wd()
        assert self.auction.allocation == allocation

    def test_balance(self):
        demand = Demand()
        demand.record(b000, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        assert not self.auction._balance()

    def test_update(self):
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        self.auction.rounds = 1
        self.auction._update()
        assert self.auction.prices.price(b100) == 4.0
        assert self.auction.prices.price(b010) == 4.0
        assert self.auction.prices.price(b001) == 4.0
        assert self.auction.prices.price(b110) == 8.0
        assert self.auction.prices.price(b101) == 8.0
        assert self.auction.prices.price(b011) == 8.0
        assert self.auction.prices.price(b111) == 12.0


class TestQuadraticSubgradientAuction():

    def setup_method(self, method):
        self.auction = QuadraticSubgradientAuction(items, agents, 0.0, 0.5)
        self.auction.demand = demand
        self.auction.prices = QuadraticPrices.initial(items)
        self.auction.prices.update(items, 0.5)

    def test_bid(self):
        self.auction._bids()
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        assert self.auction.demand == demand

    def test_wd(self):
        demand = Demand()
        demand.record(b000, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        allocation = Allocation({1: b000,
                                 2: b000,
                                 3: b000,
                                 4: b111})
        self.auction._wd()
        assert self.auction.allocation == allocation

    def test_balance(self):
        demand = Demand()
        demand.record(b000, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        assert not self.auction._balance()

    def test_update(self):
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        self.auction.rounds = 1
        self.auction._update()
        assert self.auction.prices.price(b100) == 2.0
        assert self.auction.prices.price(b010) == 2.0
        assert self.auction.prices.price(b001) == 2.0
        assert self.auction.prices.price(b110) == 5.5
        assert self.auction.prices.price(b101) == 5.5
        assert self.auction.prices.price(b011) == 5.5
        assert self.auction.prices.price(b111) == 10.5


class TestIBundle():

    def setup_method(self, method):
        self.auction = IBundle(items, agents, 2)
        self.auction.prices = PersonalizedPrices.init_bundle(agents.keys())
        self.auction.prices[4].update(items, 5)

    def test_bid(self):
        self.auction._bids()
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b000, 4)
        demand.record(b111, 4)
        assert self.auction.demand == demand

    def test_wd(self):
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        allocation = Allocation({1: b000,
                                 2: b000,
                                 3: b000,
                                 4: b111})
        self.auction._wd()
        assert self.auction.allocation == allocation

    def test_balance(self):
        demand = Demand()
        demand.record(b000, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        assert not self.auction._balance()

    def test_update(self):
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        allocation = Allocation({1: b000,
                                 2: b000,
                                 3: b000,
                                 4: b111})
        self.auction.allocation = allocation
        self.auction.rounds = 1
        self.auction._update()
        assert self.auction.prices[1].price(b110) == 2.0
        assert self.auction.prices[4].price(b110) == 0.0
        assert self.auction.prices[2].price(b101) == 2.0
        assert self.auction.prices[4].price(b101) == 0.0
        assert self.auction.prices[3].price(b011) == 2.0
        assert self.auction.prices[4].price(b011) == 0.0
        assert self.auction.prices[4].price(b111) == 5.0


class TestHeuristicLinearAuction():

    def setup_method(self, method):
        self.auction = LinearHeuristicAuction(items, agents, 0.0, 1.0)
        self.auction.demand = demand
        self.auction.prices = LinearPrices.initial(items)
        self.auction.prices.update(items, 1.0)

    def test_bid(self):
        self.auction._bids()
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        assert self.auction.demand == demand

    def test_wd(self):
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b000, 4)
        self.auction.demand = demand
        observed = Demand()
        observed.record(b110, 1)
        observed.record(b000, 2)
        observed.record(b000, 3)
        observed.record(b011, 3)
        observed.record(b000, 4)
        self.auction._observed = observed
        allocation = Allocation({1: b110,
                                 2: b000,
                                 3: b000,
                                 4: b000})
        self.auction._wd()
        assert self.auction.allocation == allocation

    def test_balance(self):
        demand = Demand()
        demand.record(b000, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        assert not self.auction._balance()

    def test_update(self):
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        self.auction.rounds = 1
        self.auction._update()
        assert self.auction.prices.price(b100) == 4.0
        assert self.auction.prices.price(b010) == 4.0
        assert self.auction.prices.price(b001) == 4.0
        assert self.auction.prices.price(b110) == 8.0
        assert self.auction.prices.price(b101) == 8.0
        assert self.auction.prices.price(b011) == 8.0
        assert self.auction.prices.price(b111) == 12.0


class TestHeuristicQuadraticAuction():

    def setup_method(self, method):
        self.auction = QuadraticHeuristicAuction(items, agents, 0.0, 0.5)
        self.auction.demand = demand
        self.auction.prices = QuadraticPrices.initial(items)
        self.auction.prices.update(items, 0.5)

    def test_bid(self):
        self.auction._bids()
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        assert self.auction.demand == demand

    def test_wd(self):
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b000, 4)
        self.auction.demand = demand
        observed = Demand()
        observed.record(b110, 1)
        observed.record(b000, 2)
        observed.record(b000, 3)
        observed.record(b011, 3)
        observed.record(b000, 4)
        self.auction._observed = observed
        allocation = Allocation({1: b110,
                                 2: b000,
                                 3: b000,
                                 4: b000})
        self.auction._wd()
        assert self.auction.allocation == allocation

    def test_balance(self):
        demand = Demand()
        demand.record(b000, 1)
        demand.record(b000, 2)
        demand.record(b000, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        assert not self.auction._balance()

    def test_update(self):
        demand = Demand()
        demand.record(b110, 1)
        demand.record(b101, 2)
        demand.record(b011, 3)
        demand.record(b111, 4)
        self.auction.demand = demand
        self.auction.rounds = 1
        self.auction._update()
        assert self.auction.prices.price(b100) == 2.0
        assert self.auction.prices.price(b010) == 2.0
        assert self.auction.prices.price(b001) == 2.0
        assert self.auction.prices.price(b110) == 5.5
        assert self.auction.prices.price(b101) == 5.5
        assert self.auction.prices.price(b011) == 5.5
        assert self.auction.prices.price(b111) == 10.5
