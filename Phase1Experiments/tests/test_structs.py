from adaptiveCA.structs import Bundle
from adaptiveCA.structs import Allocation
from adaptiveCA.structs import Demand
from adaptiveCA.structs import Polynomial
from adaptiveCA.structs import Xor


class TestBundle:

    def test_is_empty(self):
        b0 = Bundle(set())
        b1 = Bundle(set([0]))
        assert b0.is_empty()
        assert not b1.is_empty()

    def test_hash(self):
        b0 = Bundle([0, 1, 2])
        b1 = Bundle([0, 1, 2])
        b2 = Bundle([2, 3])
        assert hash(b0) == hash(b1)
        assert not hash(b0) == hash(b2)

    def test_eq(self):
        b0 = Bundle([0, 1, 2])
        b1 = Bundle([0, 1, 2])
        b2 = Bundle([2, 3])
        assert b0 == b1
        assert not b0 == b2
        assert not b0 == [0, 1, 2]
        assert b0 != b2

    def test_le(self):
        b0 = Bundle([0, 1])
        b1 = Bundle([0, 1, 2])
        assert b0 <= b1
        assert not b1 <= b0
        assert b0 < b1
        assert b1 > b0
        assert b1 >= b0

    def test_iter(self):
        b1 = Bundle([0, 1, 2])
        assert set(b1.items) == set(i for i in b1)

    def test_len(self):
        b0 = Bundle([0, 1])
        b1 = Bundle([0, 1, 2])
        assert len(b0) == 2
        assert len(b1) == 3

    def test_str(self):
        b = Bundle([0, 1, 2])
        assert str(b) == '(0,1,2)'

    def test_repr(self):
        b = Bundle([0, 1, 2])
        print repr(b)
        assert repr(b) == 'Bundle([0, 1, 2])'


class TestAllocation:

    def test_init(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        alloc1 = Allocation()
        alloc1.assign_bundle(b1, 1)
        alloc1.assign_bundle(b2, 2)
        alloc2 = Allocation({1: b1, 2: b2})
        assert alloc1 == alloc2

    def test_assign_bundle(self):
        bundle = Bundle([0, 1, 2])
        allocation = Allocation()
        allocation.assign_bundle(bundle, 2)
        assert allocation[2] == bundle

    def test_assign_item(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        allocation = Allocation()
        allocation.assign_bundle(b1, 1)
        allocation.assign_item(2, 1)
        assert allocation[1] == b2
        allocation.assign_item(5, 0)
        assert allocation[0] == Bundle([5])

    def test_assigned(self):
        b1 = Bundle([0, 1])
        allocation = Allocation()
        allocation.assign_bundle(b1, 1)
        assert allocation.assigned(1)
        assert not allocation.assigned(2)

    def test_iter(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        allocation = Allocation()
        allocation.assign_bundle(b1, 1)
        allocation.assign_bundle(b2, 2)
        assert set([b1, b2]) == set(b for b in allocation)

    def test_eq(self):
        b1 = Bundle([0, 1])
        a1, a2 = Allocation(), Allocation()
        a1.assign_bundle(b1, 1)
        a1.assign_item(2, 2)
        a2.assign_bundle(b1, 1)
        a2.assign_item(2, 2)
        assert a1 == a2

    def test_str(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        allocation = Allocation()
        allocation.assign_bundle(b1, 1)
        allocation.assign_bundle(b2, 2)
        astr = '\n'.join(['1: (0,1)', '2: (0,1,2)'])
        assert str(allocation) == astr

    def test_repr(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        allocation = Allocation()
        allocation.assign_bundle(b1, 1)
        allocation.assign_bundle(b2, 2)
        rstr = 'Allocation({1: Bundle([0, 1]), 2: Bundle([0, 1, 2])})'
        assert repr(allocation) == rstr


class TestDemand(object):

    def test_init(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        dem1 = Demand()
        dem1.record(b1, 1)
        dem1.record(b2, 1)
        dem1.record(b2, 2)
        dem2 = Demand({1: set([b1, b2]), 2: set([b2])})
        print dem1
        print dem2
        assert dem1 == dem2

    def test_record(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        demand = Demand()
        demand.record(b1, 1)
        demand.record(b2, 1)
        demand.record(b2, 2)
        assert demand[1] == set([b2, b1])
        assert demand[2] == set([b2])
        assert demand[3] == set()

    def test_str(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        demand = Demand()
        demand.record(b1, 1)
        demand.record(b2, 1)
        demand.record(b2, 2)
        dstr = '\n'.join(['1: (0,1) (0,1,2)', '2: (0,1,2)'])
        assert str(demand) == dstr

    def test_repr(self):
        b1 = Bundle([0, 1])
        b2 = Bundle([0, 1, 2])
        demand = Demand()
        demand.record(b1, 1)
        demand.record(b2, 1)
        demand.record(b2, 2)
        rstr = "Demand({1: set([Bundle([0, 1, 2]), Bundle([0, 1])]), 2: set([Bundle([0, 1, 2])])})"
        assert repr(demand) == rstr


class TestPolynomial(object):

    def test_init(self):
        poly = Polynomial({(1,): 2.0, (2, 3): 4.0, (3, 2): 1.0, (3,): 0.0})
        assert sorted(poly.monomials()) == [(1,), (2, 3), (3,)]
        assert sorted(poly.nonzero_monomials()) == [(1,), (2, 3)]
        assert sorted(poly.list_terms()) == [
            ((1,), 2.0), ((2, 3), 5.0), ((3,), 0.0)]
        assert set(poly.variables()) == set([1, 2, 3])

    def test_iter(self):
        poly = Polynomial({(1,): 2.0, (2, 3): 4.0, (3, 2): 1.0, (3,): 0.0})
        monoms = [monom for monom in poly]
        assert sorted(monoms) == [(1,), (2, 3), (3,)]

    def test_sub(self):
        p1 = Polynomial({(1,): 2.0, (2, 3): 1.0})
        p2 = Polynomial({(1,): 1.0, (1, 3): 1.0})
        p3 = p1 - p2
        result = {(1,): 1.0, (2, 3): 1.0, (1, 3): -1.0}
        assert p3.terms == result

    def test_eq(self):
        p1 = Polynomial({(1,): 2.0, (2, 3): 1.0})
        p2 = Polynomial({(1,): 1.0, (1, 3): 1.0})
        p3 = Polynomial({(1,): 1.0, (1, 3): 1.0})
        p4 = Polynomial({(1,): 1.0})
        p5 = Polynomial({(1,): 2.0, (1, 3): 5.0})
        assert p2 == p3
        assert p2 != p1
        assert not p1 == p4
        assert p1 != p5
        assert p1 != [1, 2, 3]

    def test_getset(self):
        poly = Polynomial({(1,): 2.0, (2, 3): 4.0, (3, 2): 1.0, (3,): 0.0})
        assert poly[(2, 3)] == 5.0
        assert poly[(3, 2)] == 5.0
        poly[(1,)] = 5.0
        assert poly[(1,)] == 5.0
        poly[(8, 5)] = 8.0
        assert poly[(8, 5)] == 8.0
        assert poly[(5, 8)] == 8.0

    def test_list_terms(self):
        poly = Polynomial({(1,): 2.0, (2, 3): 4.0, (3, 2): 1.0, (3,): 0.0})
        assert sorted(poly.list_terms()) == [
            ((1,), 2.0), ((2, 3), 5.0), ((3,), 0.0)]
        assert sorted(poly.list_terms(1)) == [((1,), 2.0), ((3,), 0.0)]
        assert sorted(poly.list_terms(2)) == [((2, 3), 5.0)]

    def test_singletons(self):
        poly = Polynomial({(1,): 2.0, (2, 3): 4.0, (3, 2): 1.0, (3,): 0.0})
        assert set([(1,), (3,)]) == set(poly.singletons())


class TestXOR(object):

    def test_general(self):
        xor = Xor({(1,): 2.0, (2, 3): 1.0, Bundle([1, 3]): 2.0})
        assert len(xor) == 3
        assert set(xor.bundles()) == set(
            [Bundle([1]), Bundle([2, 3]), Bundle([1, 3])])
        assert set(xor.values()) == set([2.0, 1.0])
        assert set([term for term in xor.list_terms()]) == set(
            [(Bundle([1]), 2.0),
             (Bundle([2, 3]), 1.0),
             (Bundle([1, 3]), 2.0)])
        assert xor[2, 3] == 1.0
        assert xor[Bundle([1])] == 2.0
        xor[1, 2] = 5.0
        assert xor[[1, 2]] == 5.0
        assert xor[(3,)] == 0.0
        xor[(5, 6)] += 5.0
        assert xor[Bundle([5, 6])] == 5.0

    def test_eq(self):
        xor1 = Xor({(1,): 2.0, (2, 3): 1.0, Bundle([1, 3]): 2.0})
        xor2 = Xor({(1,): 2.0, (2, 3): 1.0, Bundle([1, 3]): 2.0})
        xor3 = Xor({(1,): 2.0, (2,): 1.0, Bundle([1, 3]): 2.0})
        xor4 = Xor({(1,): 2.0, (2, 3): 2.0, Bundle([1, 3]): 2.0})
        xor5 = Xor({(1,): 2.0, (2, 3): 1.0})
        assert xor1 == xor2
        assert xor1 != xor3
        assert xor1 != xor4
        assert xor1 != 'xor'
        assert xor1 != xor5

    def test_str(self):
        xor = Xor({(1,): 2.0, (1, 3): 1.0})
        assert str(xor) == "(1,):2.0;(1,3):1.0"
