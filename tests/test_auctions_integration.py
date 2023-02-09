from adaptiveCA.structs import Bundle
from adaptiveCA.structs import Allocation
from adaptiveCA.auctions import LinearSubgradientAuction
from adaptiveCA.auctions import QuadraticSubgradientAuction
from adaptiveCA.auctions import LinearHeuristicAuction
from adaptiveCA.auctions import QuadraticHeuristicAuction
from adaptiveCA.auctions import AdaptiveSubgradientAuction
from adaptiveCA.auctions import AdaptiveHeuristicAuction
from adaptiveCA.auctions import IBundle
from adaptiveCA.agents import SingleMinded
from adaptiveCA.agents import MultiMinded


def setup_module(module):
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


def test_all_clear():
    """Agents:
    1: (110, 3)
    2: (101, 3)
    3: (011, 3)
    4: (111, 5)

    Expected allocation:
    [000, 000, 000, 111]

    All auctions should succeed in computing the solution.

    """
    agent1 = SingleMinded(b110, 3, 1)
    agent2 = SingleMinded(b101, 3, 2)
    agent3 = SingleMinded(b011, 3, 3)
    agent4 = SingleMinded(b111, 5, 4)
    agents = {1: agent1,
              2: agent2,
              3: agent3,
              4: agent4}
    allocation = Allocation({1: b000, 2: b000, 3: b000, 4: b111})
    # linear subgradient auction
    linear = LinearSubgradientAuction(
        items, agents, epsilon=0.0, stepc=1.0)
    linear.run()
    assert linear.allocation == allocation
    assert linear.rounds < linear.maxiter
    # quadratic subgradient auction
    quadratic = QuadraticSubgradientAuction(
        items, agents, epsilon=0.0, stepc=1.0)
    quadratic.run()
    assert quadratic.allocation == allocation
    assert quadratic.rounds < quadratic.maxiter
    # iBundle auction
    ibundle = IBundle(items, agents, epsilon=0.1)
    ibundle.run()
    assert ibundle.allocation == allocation
    assert ibundle.rounds < ibundle.maxiter
    # linear heuristic auction
    linear = LinearHeuristicAuction(
        items, agents, epsilon=0.0, stepc=1.0)
    linear.run()
    assert linear.allocation == allocation
    assert linear.rounds < linear.maxiter
    # quadratic heuristic auction
    quadratic = QuadraticHeuristicAuction(
        items, agents, epsilon=0.0, stepc=1.0)
    quadratic.run()
    assert quadratic.allocation == allocation
    assert quadratic.rounds < quadratic.maxiter
    # adaptive subgradient auction
    adaptive = AdaptiveSubgradientAuction(items, agents,
                                          epsilon=0.0, stepc=1.0,
                                          epoch=20)
    adaptive.run()
    assert adaptive.allocation == allocation
    assert adaptive.rounds < adaptive.maxiter
    # adaptive heuristic auction
    adaptive = AdaptiveHeuristicAuction(items, agents,
                                        epsilon=0.0, stepc=1.0,
                                        epoch=20)
    adaptive.run()
    assert adaptive.allocation == allocation
    assert adaptive.rounds < adaptive.maxiter


def test_single_minded_fail():
    """Agents:
    1: (110, 3)
    2: (101, 3)
    3: (011, 3)
    4: (111, 4)

    Expected allocation:
    [000, 000, 000, 111]

    Neither linear nor quadratic subgradient auction should terminate.
    Linear heuristic should fail, but quadratic should pass.

    """
    agent1 = SingleMinded(b110, 3, 1)
    agent2 = SingleMinded(b101, 3, 2)
    agent3 = SingleMinded(b011, 3, 3)
    agent4 = SingleMinded(b111, 4, 4)
    agents = {1: agent1,
              2: agent2,
              3: agent3,
              4: agent4}
    allocation = Allocation({1: b000, 2: b000, 3: b000, 4: b111})
    # linear subgradient auction
    linear = LinearSubgradientAuction(items, agents, epsilon=0.0, stepc=1.0)
    linear.run()
    assert linear.rounds == linear.maxiter
    # quadratic subgradient auction
    quadratic = QuadraticSubgradientAuction(
        items, agents, epsilon=0.0, stepc=1.0)
    quadratic.run()
    assert quadratic.rounds == quadratic.maxiter
    # iBundle auction
    ibundle = IBundle(items, agents, epsilon=0.1)
    ibundle.run()
    assert ibundle.allocation == allocation
    assert ibundle.rounds < ibundle.maxiter
    # linear heuristic auction
    linear = LinearHeuristicAuction(items, agents, epsilon=0.0, stepc=1.0)
    linear.run()
    assert linear.rounds == linear.maxiter
    # quadratic heuristic auction
    quadratic = QuadraticHeuristicAuction(
        items, agents, epsilon=0.0, stepc=1.0)
    quadratic.run()
    assert quadratic.rounds < quadratic.maxiter
    # adaptive subgradient auction
    adaptive = AdaptiveSubgradientAuction(items, agents,
                                          epsilon=0.0, stepc=10.0,
                                          epoch=20)
    adaptive.run()
    assert adaptive.allocation == allocation
    assert adaptive.rounds < adaptive.maxiter
    # adaptive heuristic auction
    adaptive = AdaptiveHeuristicAuction(items, agents,
                                        epsilon=0.0, stepc=1.0,
                                        epoch=2)
    adaptive.run()
    assert adaptive.allocation == allocation
    assert adaptive.rounds < adaptive.maxiter


def test_multi_minded_fail():
    """Agents:
    1: (001, 1) ; (010, 1) ; (100, 1); (110, 3) ; (101, 3) ; (011, 3) ; (111, 4)
    2: (001, 1) ; (010, 1) ; (100, 1); (110, 3) ; (101, 3) ; (011, 3) ; (111, 4)

    Neither linear nor quadratic should terminate, for subgradient and
    heuristic auctions. Every allocation is optimal, so cannot predict
    outcome of iBundle run. Adaptive auction also failes, because
    personalized prices are needed.

    """
    xor1 = [(b001, 1), (b010, 1), (b100, 1),
            (b110, 3), (b101, 3), (b011, 3),
            (b111, 4)]
    agent1 = MultiMinded(xor1, 1)
    xor2 = [(b001, 1), (b010, 1), (b100, 1),
            (b110, 3), (b101, 3), (b011, 3),
            (b111, 4)]
    agent2 = MultiMinded(xor2, 2)
    agents = {1: agent1, 2: agent2}
    # linear subgradient auction
    linear = LinearSubgradientAuction(items, agents, epsilon=0.0, stepc=1.0)
    linear.run()
    assert linear.rounds == linear.maxiter
    # quadratic subgradient auction
    quadratic = QuadraticSubgradientAuction(
        items, agents, epsilon=0.0, stepc=1.0)
    quadratic.run()
    assert quadratic.rounds == quadratic.maxiter
    # iBundle auction
    ibundle = IBundle(items, agents, epsilon=0.1)
    ibundle.run()
    assert ibundle.rounds < ibundle.maxiter
    # linear heuristic auction
    linear = LinearHeuristicAuction(items, agents, epsilon=0.0, stepc=1.0)
    linear.run()
    assert linear.rounds == linear.maxiter
    # quadratic heuristic auction
    quadratic = QuadraticHeuristicAuction(
        items, agents, epsilon=0.0, stepc=1.0)
    quadratic.run()
    assert quadratic.rounds == quadratic.maxiter
    # adaptive subgradient auction
    adaptive = AdaptiveSubgradientAuction(items, agents,
                                          epsilon=0.0, stepc=10.0,
                                          epoch=20)
    adaptive.run()
    assert adaptive.rounds == adaptive.maxiter


def test_heuristic_fail_subgradient_pass():
    """Agents:
    1: (110, 20)
    2: (011, 19) ; (001, 1)

    If the heuristic auction is started with a large stepsize, the
    second agent's interest in 001 is never discovered (with both
    linear and quadratic prices), and the allocation is inefficient.

    Heuristic final allocation: [110, 000]
    Efficient allocation: [110, 001]

    """
    # agents
    xor1 = {b110: 20}
    agent1 = MultiMinded(xor1, 1)
    xor2 = {b011: 19, b001: 1}
    agent2 = MultiMinded(xor2, 2)
    agents = {1: agent1, 2: agent2}
    # efficient allocation
    efficient = Allocation({1: b110, 2: b001})
    # auctions
    linear_heuristic = LinearHeuristicAuction(
        items, agents, epsilon=0.0, stepc=10)
    linear_heuristic.run()
    assert linear_heuristic.allocation != efficient
    quadratic_heuristic = QuadraticHeuristicAuction(
        items, agents, epsilon=0.0, stepc=10)
    quadratic_heuristic.run()
    assert quadratic_heuristic.allocation != efficient
    linear_exact = LinearSubgradientAuction(
        items, agents, epsilon=0.0, stepc=10)
    linear_exact.run()
    assert linear_exact.allocation == efficient
    quadratic_exact = QuadraticSubgradientAuction(
        items, agents, epsilon=0.0, stepc=10)
    quadratic_exact.run()
    assert quadratic_exact.allocation == efficient
    # adaptive heuristic auction
    adaptive = AdaptiveHeuristicAuction(items, agents,
                                        epsilon=0.0, stepc=1.0,
                                        epoch=20)
    adaptive.run()
    assert adaptive.allocation != efficient


def test_linear_fail_quadratic_pass():
    """
    # TODO: Unit test where quadratic prices clear but linear prices fail.

    """
    pass
