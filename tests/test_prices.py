from adaptiveCA.structs import Bundle, Polynomial
from adaptiveCA.prices import LinearPrices
from adaptiveCA.prices import QuadraticPrices
from adaptiveCA.prices import PolynomialPrices
from adaptiveCA.prices import BundlePrices
from adaptiveCA.prices import PersonalizedPrices
import pytest


class TestPolynomialPrices:

    def test_price(self):
        prices = PolynomialPrices({(1,): 1.0, (1, 2): 1.0, (2, 1): 1.0})
        b1 = Bundle([1, 2])
        assert prices.price(b1) == 3.0
        assert prices[0].price(b1) == 3.0
        b2 = Bundle([2])
        assert prices.price(b2) == 0.0
        assert isinstance(prices.struct, Polynomial)

    def test_update(self):
        prices = PolynomialPrices({(1,): 1.0, (1, 2): 1.0, (2, 1): 1.0})
        prices.update([2, 1], 1.0)
        assert prices.poly[(1, 2)] == 3.0
        assert prices.poly[(1,)] == 2.0

    def test_monomials(self):
        prices = PolynomialPrices(
            {(1,): 1.0, (1, 2): 1.0, (2, 1): 1.0, (0,): 0.0})
        assert sorted(prices.poly.monomials()) == [(0,), (1,), (1, 2)]
        assert sorted(prices.poly.nonzero_monomials()) == [(1,), (1, 2)]


class TestLinearPrices:

    def test_update(self):
        items = [0, 1, 2]
        prices = LinearPrices.initial(items)
        prices.update([1], 5)
        prices.update([1, 2], 3.0)
        assert prices.poly[1, ] == 8.0
        assert prices.poly[2, ] == 3.0
        assert prices.poly[0, ] == 0.0
        prices = LinearPrices.initial(items, 10)
        prices.update([1], 5)
        prices.update([1, 2], 3.0)
        assert prices.poly[1, ] == 18.0
        assert prices.poly[2, ] == 13.0
        assert prices.poly[0, ] == 10.0

    def test_price(self):
        items = [0, 1, 2]
        b1 = Bundle([1])
        b2 = Bundle([0, 1, 2])
        prices = LinearPrices.initial(items)
        prices.update([1], 5)
        prices. update([2], 3.0)
        assert prices.price(b1) == 5.0
        assert prices.price(b2) == 8.0
        prices = LinearPrices.initial(items, 10)
        prices.update([1], 5)
        prices. update([2], 3.0)
        assert prices.price(b1) == 15.0
        assert prices.price(b2) == 38.0
        # test personalization
        assert prices[0].price(b1) == 15.0
        assert prices[1].price(b2) == 38.0

    def test_str(self):
        items = [1, 2]
        prices = LinearPrices.initial(items)
        prices.update([1, 2], 1.5012)
        pstr = '\n'.join(['1: 1.50', '2: 1.50'])
        assert str(prices) == pstr

    def test_init(self):
        with pytest.raises(ValueError):
            LinearPrices({(1,): 1.0, (2, 3): 1.0})

    def test_monomials(self):
        items = [0, 1, 2]
        prices = LinearPrices.initial(items)
        prices.update([1, 2], 1.0)
        assert sorted(prices.poly.monomials()) == [(0,), (1,), (2,)]
        assert sorted(prices.poly.nonzero_monomials()) == [(1,), (2,)]


class TestQuadraticPrices:

    def test_update(self):
        items = [0, 1, 2]
        prices = QuadraticPrices.initial(items)
        prices.update([1], 5)
        prices.update([1, 2], 3.0)
        assert prices.poly[1, ] == 8.0
        assert prices.poly[2, ] == 3.0
        assert prices.poly[0, ] == 0.0
        assert prices.poly[1, 2] == 3.0
        assert prices.poly[0, 2] == 0.0
        prices = QuadraticPrices.initial(items, 10)
        prices.update([1], 5)
        prices.update([1, 2], 3.0)
        assert prices.poly[1, ] == 18.0
        assert prices.poly[2, ] == 13.0
        assert prices.poly[0, ] == 10.0
        assert prices.poly[1, 2] == 3.0
        assert prices.poly[0, 2] == 0.0

    def test_price(self):
        items = [0, 1, 2]
        b1 = Bundle([1])
        b2 = Bundle([0, 1, 2])
        prices = QuadraticPrices.initial(items)
        prices.update([1], 5)
        prices.update([1, 2], 3.0)
        assert prices.price(b1) == 8.0
        assert prices.price(b2) == 14.0
        prices = QuadraticPrices.initial(items, 10)
        prices.update([1], 5)
        prices.update([1, 2], 3.0)
        assert prices.price(b1) == 18.0
        assert prices.price(b2) == 44.0
        # test personalization
        assert prices[0].price(b1) == 18.0
        assert prices[1].price(b2) == 44.0

    def test_str(self):
        items = [1, 2]
        prices = QuadraticPrices.initial(items)
        prices.update([1, 2], 1.5012)
        pstr = '\n'.join(['1,: 1.50', '2,: 1.50', '1,2: 1.50'])
        assert str(prices) == pstr

    def test_init(self):
        with pytest.raises(ValueError):
            QuadraticPrices({(1,): 1.0, (2, 3): 1.0, (1, 2, 3): 2.0})

    def test_monomials(self):
        items = [0, 1, 2]
        prices = QuadraticPrices.initial(items)
        prices.update([2, 1], 1.0)
        assert sorted(prices.poly.monomials()) == [
            (0,), (0, 1), (0, 2), (1,), (1, 2), (2,)]
        assert sorted(prices.poly.nonzero_monomials()) == [(1,), (1, 2), (2,)]


class TestBundlePrices:

    def test_update(self):
        b1 = Bundle([1])
        b2 = Bundle([1, 2])
        b3 = Bundle([0, 1])
        prices = BundlePrices.initial()
        prices.update([1], 3)
        prices.update([1, 2], 5.0)
        assert prices.xor[b1] == 3.0
        assert prices.xor[b2] == 5.0
        assert prices.xor[b3] == 0.0
        prices.update(b2, 1.0)
        assert prices.xor[b2] == 6.0

    def test_price(self):
        b1 = Bundle([1])
        b2 = Bundle([1, 2])
        b3 = Bundle([0, 1])
        prices = BundlePrices.initial()
        prices.update([1], 3)
        prices.update([1, 2], 5.0)
        assert prices.price(b1) == 3.0
        assert prices.price(b2) == 5.0
        assert prices.price(b3) == 3.0
        b4 = Bundle([2])
        assert prices.price(b4) == 0.0
        # test personalization
        assert prices[0].price(b1) == 3.0
        assert prices[1].price(b2) == 5.0
        assert prices[2].price(b3) == 3.0
        assert prices[4].price(b4) == 0.0

    def test_bundles(self):
        prices = BundlePrices.initial()
        prices.update([1, 2], 1.0)
        prices.update([2, 3], 1.0)
        assert prices.xor.bundles() == [Bundle([1, 2]), Bundle([2, 3])]

    def test_str(self):
        prices = BundlePrices.initial()
        prices.update([1, 2], 1.5012)
        prices.update([1], 1.5012)
        pstr = '\n'.join(['(1,): 1.50', '(1,2): 1.50'])
        assert str(prices) == pstr


class TestPersonalizedPrices:

    def test_update(self):
        aids = [1, 2, 3]
        b1 = Bundle([1])
        b2 = Bundle([1, 2])
        b3 = Bundle([0, 1])
        prices = PersonalizedPrices.init_bundle(aids)
        prices[1].update([1], 5)
        prices[2].update([1, 2], 3.0)
        assert prices[1].xor[b1] == 5.0
        assert prices[2].xor[b2] == 3.0
        assert prices[1].xor[b3] == 0.0
        assert prices[3].xor[b1] == 0.0
        assert prices[3].xor[b2] == 0.0
        assert prices[3].xor[b2] == 0.0
        prices[2].update(b2, 1.0)
        assert prices[2].xor[b2] == 4.0

    def test_price(self):
        aids = [1, 2, 3]
        b1 = Bundle([1])
        b2 = Bundle([1, 2])
        b3 = Bundle([0, 1])
        prices = PersonalizedPrices.init_bundle(aids)
        prices[1].update([1], 5)
        prices[2].update([1, 2], 3.0)
        assert prices[1].price(b1) == 5.0
        assert prices[2].price(b2) == 3.0
        assert prices[3].price(b3) == 0.0
        assert prices[3].price(b1) == 0.0
        assert prices[3].price(b2) == 0.0
        assert prices[3].price(b3) == 0.0

    def test_str(self):
        prices = PersonalizedPrices.init_bundle([1, 2])
        prices[1].update([1, 2], 1.5012)
        prices[2].update([1], 1.5012)
        pstr = '\n'.join(['1:(1,2): 1.50', '2:(1,): 1.50'])
        assert str(prices) == pstr

    def test_inits(self):
        aids = [1, 2, 3]
        items = [1, 2, 3]
        pers_linear = PersonalizedPrices.init_linear(aids, items)
        assert pers_linear[1].price(items) == 0.0
        pers_quadratic = PersonalizedPrices.init_quadratic(aids, items)
        assert pers_quadratic[1].price(items) == 0.0
