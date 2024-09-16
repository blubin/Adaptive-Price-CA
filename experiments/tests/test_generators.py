import copy, os
import pytest
from pytest import approx
from numpy import mean
from scipy.stats import lomax
from adaptiveCA.generators import *
from adaptiveCA.generatorfactory import *

class TestQuadValue:

    def setup_method(self, method):
        # Eliminate existing file if it exists
        self.gensmall = GeneratorFactory.get(QUAD_VALUE_UNIT_SMALL)
        self.filename1 = self.gensmall._filename_for_index(1)
        self.filename2 = self.gensmall._filename_for_index(2)
        if os.path.isfile(self.filename1):
            print "Removing:", self.filename1
            os.remove(self.filename1)
        if os.path.isfile(self.filename2):
            print "Removing:", self.filename2
            os.remove(self.filename2)
        
    def test_QuadValueAgent(self):
        assert not os.path.isfile(self.filename1)
        instance1a = self.gensmall.get_instance(1)
        assert os.path.isfile(self.filename1)
        instance1b = self.gensmall.get_instance(1)
        assert instance1a == instance1b

        assert not os.path.isfile(self.filename2)
        instance2a = self.gensmall.get_instance(2)
        assert os.path.isfile(self.filename2)
        instance2b = self.gensmall.get_instance(2)
        assert instance2a == instance2b

        assert instance1a != instance2a

        assert instance1a.goods == [1,2,3,4,5]
        assert set(instance1a.agents.keys()) == set([1,2])
        assert len(instance1a.agents[1].get_terms_by_size(1)) == 5
        assert len(instance1a.agents[2].get_terms_by_size(1)) == 5
        assert len(instance1a.agents[1].get_terms_by_size(1)) == 5
        assert len(instance1a.agents[1].get_terms_by_size(2)) == 3
        assert len(instance1a.agents[2].get_terms_by_size(2)) == 3


class TestCATSGenerator:

    def setup_method(self, method):
        # Eliminate existing file if it exists
        self.gensmall = GeneratorFactory.get(CATS_UNIT_SMALL)
        self.filename1 = self.gensmall._filename_for_index(1)
        self.filename2 = self.gensmall._filename_for_index(2)
        if os.path.isfile(self.filename1):
            print "Removing:", self.filename1
            os.remove(self.filename1)
        if os.path.isfile(self.filename2):
            print "Removing:", self.filename2
            os.remove(self.filename2)

    def test_SingleMind(self):
        # Get a Single Minded version:
        CATS_UNIT_SMALL_SINGLEMINDED = copy.copy(CATS_UNIT_SMALL)
        CATS_UNIT_SMALL_SINGLEMINDED['type'] = 'SingleMinded'
        self.gensmall = GeneratorFactory.get(CATS_UNIT_SMALL_SINGLEMINDED)
        # Remaining Setup should be okay.

        assert not os.path.isfile(self.filename1)
        instance1a = self.gensmall.get_instance(1)
        assert os.path.isfile(self.filename1)
        instance1b = self.gensmall.get_instance(1)
        assert instance1a == instance1b

        assert not os.path.isfile(self.filename2)
        instance2a = self.gensmall.get_instance(2)
        assert os.path.isfile(self.filename2)
        instance2b = self.gensmall.get_instance(2)
        assert instance2a == instance2b

        assert instance1a != instance2a

        assert instance1a.goods == [0,1,2,3,4]
        assert set(instance1a.agents.keys()) == set(range(1,11))
        for i in range(1,11):
            assert len(instance1a.agents[i].xor) == 1

    def test_MultiMind(self):
        assert not os.path.isfile(self.filename1)
        instance1a = self.gensmall.get_instance(1)
        assert os.path.isfile(self.filename1)
        instance1b = self.gensmall.get_instance(1)
        assert instance1a == instance1b

        assert not os.path.isfile(self.filename2)
        instance2a = self.gensmall.get_instance(2)
        assert os.path.isfile(self.filename2)
        instance2b = self.gensmall.get_instance(2)
        assert instance2a == instance2b

        assert instance1a != instance2a

        assert instance1a.goods == [0,1,2,3,4]
        # This is a mapping to the particular instance in the CATS file:
        def get_bundle(inst, aid, bund):
            return inst.agents[aid].xor.list_terms()[bund][0]
        def get_bundles(inst, aid, bunds):
            return set([get_bundle(inst, aid, b) for b in bunds])

        assert get_bundle(instance1a,1,0) == Bundle([0, 1, 3])
        assert get_bundles(instance1a,2,[0,1]) == \
               set([Bundle([0, 1, 3]), Bundle([1, 2, 3])])
        assert get_bundle(instance1a,3,0) == Bundle([0, 1, 2, 3])
        assert get_bundle(instance1a,4,0) == Bundle([4])
        assert get_bundle(instance1a,5,0) == Bundle([3])
        assert get_bundle(instance1a,6,0) == Bundle([0, 2])
        assert get_bundle(instance1a,7,0) == Bundle([0, 1, 2, 3, 4])
        assert get_bundles(instance1a,8,[0,1]) == \
               set([Bundle([1,2,3,4]), Bundle([0,1,2,3])])

class TestExpansionDistribution:

    def test_lomax_exp_dist(self):
        obs_value = 1e8
        exp_dist = LomaxExpansionDistribution(3, .5)
        samples = [exp_dist.expand_value(obs_value) for i in range(0,100000)]
        assert mean(samples) == approx(obs_value, .01)

    def test_lognorm_exp_dist(self):
        obs_value = 1e8
        exp_dist = LognormExpansionDistribution(.25, .5)
        samples = [exp_dist.expand_value(obs_value) for i in range(0,10000)]
        assert mean(samples) == approx(obs_value, .01)

    def test_gamma_exp_dist(self):
        obs_value = 1e8
        exp_dist = GammaExpansionDistribution(3, .5)
        samples = [exp_dist.expand_value(obs_value) for i in range(0,10000)]
        assert mean(samples) == approx(obs_value, .01)

