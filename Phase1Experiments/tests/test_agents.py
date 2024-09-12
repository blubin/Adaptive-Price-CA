from adaptiveCA.agents import Agent
from adaptiveCA.agents import QuadraticValuation
from adaptiveCA.agents import SingleMinded
from adaptiveCA.agents import MultiMinded
from adaptiveCA.structs import Bundle
from adaptiveCA.prices import LinearPrices
from adaptiveCA.prices import QuadraticPrices
from adaptiveCA.prices import BundlePrices
from adaptiveCA.prices import PersonalizedPrices
import pytest


class TestAgent:

    def test(self):
        a = Agent()
        Agent(0)
        with pytest.raises(NotImplementedError):
            a.valueq(None)
        with pytest.raises(NotImplementedError):
            a.demandq(None)
        with pytest.raises(Exception):
            Agent.deserialize('')


class TestMultiMinded:

    def test_eq(self):
        a1 = MultiMinded([(Bundle([0, 1]), 1)])
        a2 = MultiMinded([(Bundle([0, 1]), 1)])
        b1 = MultiMinded([(Bundle([0, 2]), 2)])
        b2 = MultiMinded([(Bundle([0, 2]), 2)])
        assert a1 == a2
        assert b1 == b2
        assert a1 is not True
        assert a1 != b1
        assert a1 != 'agent'

    def test_valueq(self):
        b1 = Bundle([3])
        b2 = Bundle([1, 2])
        b3 = Bundle([1, 2, 3])
        agent = MultiMinded([(b1, 3), (b2, 4), (b3, 6)])
        tb1 = Bundle([1, 2])
        tb2 = Bundle([1, 3])
        tb3 = Bundle([1])
        assert agent.valueq(tb1) == 4.0
        assert agent.valueq(tb2) == 3.0
        assert agent.valueq(tb3) == 0.0

    def test_demandq(self):
        b1 = Bundle([3])
        b2 = Bundle([1, 2])
        b3 = Bundle([1, 2, 3])
        agent = MultiMinded([(b1, 3), (b2, 4), (b3, 6)])
        prices = LinearPrices.initial([1, 2, 3])
        prices.update([1, 2, 3], 1)
        assert agent.demandq(prices) == b3
        prices.update([1, 2, 3], 1)
        assert agent.demandq(prices) == b1
        assert agent.demandq(prices, b2, 1.0) == b2
        empty = Bundle([])
        prices.update([1, 2, 3], 10)
        assert agent.demandq(prices) == empty

    def test_str(self):
        b1 = Bundle([3])
        agent = MultiMinded([(b1, 3)])
        assert str(agent) == "{MultiMinded (3,):3}"
        assert repr(agent) == "{MultiMinded (3,):3}"


class TestSingleMinded:

    def test_valueq(self):
        b1 = Bundle([3])
        b2 = Bundle([1, 2])
        b3 = Bundle([1, 2, 3])
        agent = SingleMinded(b2, 4)
        assert agent.valueq(b1) == 0.0
        assert agent.valueq(b2) == 4.0
        assert agent.valueq(b3) == 4.0

    def test_demandq(self):
        bundle = Bundle([1, 2])
        empty = Bundle([])
        agent = SingleMinded(bundle, 4)
        prices = LinearPrices.initial([1, 2, 3])
        prices.update([1, 2, 3], 1)
        assert agent.demandq(prices) == bundle
        prices.update([1, 2, 3], 1)
        assert agent.demandq(prices, bundle, 0.5) == bundle
        assert agent.demandq(prices, empty, 0.5) == empty
        prices.update([1, 2, 3], 1)
        assert agent.demandq(prices, bundle, 0.5) == empty


class TestQuadraticValuation:

    def setup_method(self, method):
        self.qv = QuadraticValuation(
            {(1, 0): 1, (0, 2): 2, (0,): 1, (2,): 2}, aid=0)
        self.qvcap = QuadraticValuation(
            {(1, 0): 1, (0, 2): 2, (0,): 1, (2,): 2}, aid=0, cap=2)

    def test_eq(self):
        qvsame = QuadraticValuation(
            {(1, 0): 1, (0, 2): 2, (0,): 1, (2,): 2}, aid=0)
        qv2 = QuadraticValuation(
            {(1, 0): 1, (0, 2): 2, (0,): 1, (2,): 2}, aid=2)
        assert not self.qv == self.qvcap
        assert self.qv == qv2
        assert not self.qv == 'agent'
        assert self.qv == qvsame

    def test_init(self):
        assert self.qv.poly.terms == {(0, 1): 1, (0, 2): 2, (0,): 1, (2,): 2}
        qv = QuadraticValuation(
            {(0, 1): 1, (0, 2): 2, (0,): 1, (2,): 2}, aid=1)
        assert qv.poly.terms == {(0, 1): 1, (0, 2): 2, (0,): 1, (2,): 2}

    def test_serialize(self):
        serial = self.qvcap.serialize()
        recovered = Agent.deserialize(serial)
        assert self.qvcap == recovered
        serial = self.qv.serialize()
        recovered = Agent.deserialize(serial)
        assert self.qv == recovered

    def test_str(self):
        qv = QuadraticValuation({(0, 1): 1.0})
        assert str(qv) == "QuadraticValuation({(0, 1): 1.0})"

    def test_get_terms(self):
        assert sorted(self.qv.get_terms_by_size(1)) == [((0,), 1), ((2,), 2)]
        assert sorted(self.qv.get_terms_by_size(2)) == [
            ((0, 1), 1), ((0, 2), 2)]

    def test_valueq(self):
        assert self.qv.valueq(Bundle([0, 2])) == 5
        assert self.qv.valueq(Bundle([5])) == 0
        # test cap
        assert self.qv.valueq(Bundle([0, 1, 2])) == 6
        assert self.qvcap.valueq(Bundle([0, 1, 2])) == 5
        assert self.qvcap.valueq(Bundle([0, 1])) == 2

    def test_demandq(self):
        with pytest.raises(ValueError):
            self.qv.demandq({0: object()})
        # Linear
        assert self.qv.demandq(LinearPrices.initial(
            [0, 1, 2])) == Bundle([0, 1, 2])
        assert self.qv.demandq(LinearPrices(
            {(0,): 10, (1,): 10, (2,): 10})) == Bundle([])
        assert self.qv.demandq(LinearPrices(
            {(1,): 10, (2,): 10})) == Bundle([0])
        assert self.qv.demandq(LinearPrices(
            {(0,): 1, (1,): 2, (2,): 4})) == Bundle([0, 2])
        assert self.qv.demandq(LinearPrices(
            {(0,): 1, (1,): 2, (2,): 4, (3,): 0})) == Bundle([0, 2])
        # Quadratic
        assert self.qv.demandq(QuadraticPrices.initial(
            [0, 1, 2])) == Bundle([0, 1, 2])
        assert self.qv.demandq(QuadraticPrices(
            {(0,): 10, (1,): 10, (2,): 10})) == Bundle([])
        assert self.qv.demandq(QuadraticPrices(
            {(1,): 10, (2,): 10})) == Bundle([0])
        assert self.qv.demandq(QuadraticPrices(
            {(0,): 1, (1,): 2, (2,): 4})) == Bundle([0, 2])
        # More Quadratic
        assert self.qv.demandq(QuadraticPrices.initial(
            [0, 1, 2])) == Bundle([0, 1, 2])
        assert self.qv.demandq(QuadraticPrices(
            {(0, 2): 10, (2,): 1})) == Bundle([0, 1])
        assert self.qv.demandq(QuadraticPrices({(1, 2): 10})) == Bundle([0, 2])
        # Bundle
        assert self.qv.demandq(BundlePrices.initial()) == Bundle([0, 1, 2])
        assert self.qv.demandq(BundlePrices({(2,): 1})) == Bundle([0, 1, 2])
        assert self.qv.demandq(BundlePrices({(0, 1, 2): 10})) == Bundle([0, 2])
        # Personal Bundle
        bund_prices = BundlePrices({(0, 1, 2): 10})
        pers_prices = PersonalizedPrices({0: bund_prices})
        assert self.qv.demandq(pers_prices) == Bundle([0, 2])
        # Test invalid prices:
        with pytest.raises(ValueError):
            self.qv.demandq({0: PersonalizedPrices({})})

        # Test Proposal for linear
        # Call could give 0,1,2 or 0,2.  Happens to do the former:
        assert self.qv.demandq(LinearPrices({(0,): 1, (1,): 1, (2,): 1}),
                               proposed=Bundle([0, 1, 2])) == Bundle([0, 1, 2])
        # But we can force it to the latter:
        assert self.qv.demandq(LinearPrices({(0,): 1, (1,): 1, (2,): 1}),
                               proposed=Bundle([0, 2])) == Bundle([0, 2])
        # But if you propose something else, it will stick to optimal:
        assert self.qv.demandq(LinearPrices({(0,): 1, (1,): 1, (2,): 1}),
                               proposed=Bundle([0])) in set([Bundle([0, 1, 2]),
                                                             Bundle([0, 2])])

        # Test Proposal for Personal Bundle:
        pers_prices = PersonalizedPrices({0: BundlePrices({(0, 1, 2): 10})})
        assert self.qv.demandq(
            pers_prices, proposed=Bundle([0, 2])) == Bundle([0, 2])

    def test_cap_demandq(self):
        with pytest.raises(ValueError):
            self.qvcap.demandq({0: object()})
        # Linear
        assert self.qvcap.demandq(LinearPrices.initial(
            [0, 1, 2])) == Bundle([0, 2])
        assert self.qvcap.demandq(LinearPrices(
            {(0,): 10, (1,): 10, (2,): 10})) == Bundle([])
        assert self.qvcap.demandq(LinearPrices(
            {(1,): 10, (2,): 10})) == Bundle([0])
        assert self.qvcap.demandq(LinearPrices(
            {(0,): 1, (1,): 2, (2,): 4})) == Bundle([0, 2])
        assert self.qvcap.demandq(LinearPrices(
            {(0,): 1, (1,): 2, (2,): 4, (3,): 0})) == Bundle([0, 2])
        # Quadratic
        assert self.qvcap.demandq(QuadraticPrices.initial(
            [0, 1, 2])) == Bundle([0, 2])
        assert self.qvcap.demandq(QuadraticPrices(
            {(0,): 10, (1,): 10, (2,): 10})) == Bundle([])
        assert self.qvcap.demandq(QuadraticPrices(
            {(1,): 10, (2,): 10})) == Bundle([0])
        assert self.qvcap.demandq(QuadraticPrices(
            {(0,): 1, (1,): 2, (2,): 4})) == Bundle([0, 2])
        # More Quadratic
        assert self.qvcap.demandq(QuadraticPrices.initial(
            [0, 1, 2])) == Bundle([0, 2])
        assert self.qvcap.demandq(QuadraticPrices(
            {(0, 2): 10, (2,): 1})) == Bundle([0, 1])
        assert self.qvcap.demandq(
            QuadraticPrices({(1, 2): 10})) == Bundle([0, 2])
        # Bundle
        assert self.qvcap.demandq(BundlePrices.initial()) == Bundle([0, 2])
        assert self.qvcap.demandq(BundlePrices({(2,): 1})) == Bundle([0, 2])
        assert self.qvcap.demandq(BundlePrices(
            {(0, 1, 2): 10})) == Bundle([0, 2])
        # Personal Bundle
        bund_prices = BundlePrices({(0, 1, 2): 10})
        pers_prices = PersonalizedPrices({0: bund_prices})
        assert self.qvcap.demandq(pers_prices) == Bundle([0, 2])
        assert self.qvcap.demandq(LinearPrices({(0,): 1, (1,): 1, (2,): 1}),
                                  proposed=Bundle([0, 2])) == Bundle([0, 2])
        assert self.qvcap.demandq(LinearPrices({(0,): 1, (1,): 1, (2,): 1}),
                                  proposed=Bundle([0])) in set([Bundle([0, 1, 2]),
                                                                Bundle([0, 2])])
        pers_prices = PersonalizedPrices({0: BundlePrices({(0, 1, 2): 10})})
        assert self.qvcap.demandq(
            pers_prices, proposed=Bundle([0, 2])) == Bundle([0, 2])
