from adaptiveCA.structs import Bundle
from adaptiveCA.structs import Allocation
from adaptiveCA.agents import SingleMinded
from adaptiveCA.auctions import LinearSubgradientAuction
from adaptiveCA.auctions import QuadraticSubgradientAuction
from adaptiveCA.auctions import IBundle
from adaptiveCA.instrumentation import AuctionInstrumentation
from adaptiveCA.prices import PolynomialPrices
from adaptiveCA.agents import QuadraticValuation
import pytest


def setup_module(module):
    """Items:
    [1, 2, 3]

    Agents:
    1: (110, 3)
    2: (101, 3)
    3: (011, 3)
    4: (111, 4)

    Allocation:
    (110, 000, 000, 111)
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
    module.allocation = Allocation({1: b110, 2: b000,
                                    3: b000, 4: b111})


def test_linear_instrument():
    auction = LinearSubgradientAuction(items, agents, 0.0, 1.0)
    instr = AuctionInstrumentation(auction)
    auction.round()
    assert instr._rounds() == 1
    assert instr._total_value(allocation) == 7
    assert instr._current_value() in [3, 4]
    assert instr._efficient_value() == 4
    assert instr._total_revenue(allocation) == 10
    assert instr._current_revenue() in [4, 6]
    assert instr._current_ind_util() in [4, 6]
    assert instr._winners() in [1, 2, 3]
    assert instr._price_degree() == 1
    assert instr._price_sparsity() == 3
    assert instr._max_agent_value() == 4
    assert instr._imbalance() == 6
    assert instr._wd_size() == (16, 19)


def test_quadratic_instrument():
    auction = QuadraticSubgradientAuction(items, agents, 0.0, 1.0)
    instr = AuctionInstrumentation(auction)
    auction.round()
    assert instr._rounds() == 1
    assert instr._total_value(allocation) == 7
    assert instr._current_value() in [3, 4]
    assert instr._efficient_value() == 4
    assert instr._winners() in [1, 2, 3]
    assert instr._price_degree() == 2
    assert instr._price_sparsity() == 6
    assert instr._max_agent_value() == 4
    assert instr._imbalance() == 6
    assert instr._wd_size() == (16, 19)


def test_ibundle_instrument():
    auction = IBundle(items, agents, 1.0)
    instr = AuctionInstrumentation(auction)
    auction.round()
    assert instr._rounds() == 1
    assert instr._total_value(allocation) == 7
    assert instr._current_value() in [3, 4]
    assert instr._efficient_value() == 4
    assert instr._current_revenue() == 0
    assert instr._current_ind_util() == 10
    assert instr._winners() == 1
    assert instr._price_degree() == 'NA'
    assert instr._price_sparsity() == 3
    assert instr._max_agent_value() == 4
    assert instr._imbalance() in [6, 7]
    assert instr._wd_size() == (4, 7)


def test_price_errors():
    auction = IBundle(items, agents, 1.0)
    auction.prices = None
    instr = AuctionInstrumentation(auction)
    with pytest.raises(ValueError):
        instr._price_degree()
    with pytest.raises(ValueError):
        instr._price_sparsity()


def test_with_quadagents():
    qitems = [1, 2]
    qagent1 = QuadraticValuation({(1,): 1.0, (2,): 1.0, (1, 2): 1.0}, 1)
    qagent2 = QuadraticValuation({(1,): 1.0, (2,): 1.0, (1, 2): 1.0}, 2)
    qagents = {1: qagent1, 2: qagent2}
    b00, b11 = Bundle([]), Bundle(qitems)
    qalloc = Allocation({1: b11, 2: b00})
    auction = LinearSubgradientAuction(qitems, qagents, 0.0, 1.0)
    instr = AuctionInstrumentation(auction)
    auction.round()
    assert instr._rounds() == 1
    assert instr._total_value(qalloc) == 3
    assert instr._current_value() in [2, 3]
    assert instr._efficient_value() == 3
    assert instr._total_revenue(qalloc) == 2
    assert instr._current_revenue() == 2
    assert instr._current_ind_util() == 4
    assert instr._winners() in [1, 2]
    assert instr._price_degree() == 1
    assert instr._price_sparsity() == 2
    assert instr._max_agent_value() == 3


def test_efficient_error():
    auction = IBundle(items, agents, 1.0)
    auction.agents[1] = None
    instr = AuctionInstrumentation(auction)
    with pytest.raises(ValueError):
        instr._efficient_value()
