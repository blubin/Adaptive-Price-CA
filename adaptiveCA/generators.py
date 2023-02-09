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

"""Create a auction instances, and cache them for consistency"""

import abc
import os
import sys
import subprocess
import csv
import random
import logging
import numpy
import scipy
from scipy.stats import lomax
from scipy.stats import lognorm
from scipy.stats import gamma
from time import strftime
from collections import namedtuple
from agents import Agent, QuadraticValuation, SingleMinded, MultiMinded
from structs import Bundle

""" Define the instance tuple.
    Goods is a list of goods (usually integers).
    Agents is a dictionary from integers to agent objects.
"""
Instance = namedtuple('Instance', "goods agents")


class Generator(object):
    """ Abstract Base class for all generators. """

    @classmethod
    def generator_name(cls):
        """ Return the generator name string."""
        raise NotImplementedError("Must Implement generator_name")

    def __init__(self, params):
        """ Generators should offer a constructor that takes a parameter dict
        """
        if not 'subdir' in params:  # pragma: no cover
            raise ValueError('Parameters must have a subdirectory.')
        if not 'prefix' in params:  # pragma: no cover
            raise ValueError('Parameters must have a prefix.')
        self.params = params
        self._setup()

    @classmethod
    def is_generator_for(cls, params):
        """ Return True iff this is the generator for these params. """
        if not 'generator' in params:  # pragma: no cover
            raise ValueError('Parameters must specify the generator.')
        return params['generator'] == cls.generator_name()

    def _setup(self):
        """ Internal Method.
            Setup generator, including the file system.
        """
        if not os.path.exists(self._datadir()):
            try:
                os.mkdir(self._datadir())  # pragma: no cover
            except OSError, e:
                print 'Warning', e
        if not os.path.exists(self._datasubdir()):
            try:
                os.mkdir(self._datasubdir())  # pragma: no cover
            except OSError, e:
                print 'Warning', e

    def get_instance(self, index):
        """ Get the auction instance indicated by the given index.
            Such indices should be stable across program invocations.
            By 

        Args:
          - index

        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of integers.
            Agents is a dictionary from integers to agent objects.
        """
        if self._is_existing_instance(index):
            instance = self._read_instance(self._filename_for_index(index))
        else:
            instance = self._create_instance(index)
            self._write_instance(self._filename_for_index(index), instance)
        return instance

    def _is_existing_instance(self, index):
        """ Internal Method.
        Returns: True iff the instance already exists.
        """
        return os.path.isfile(self._filename_for_index(index))

    def _filename_for_index(self, index):
        """ Internal Method.
        Returns: The filename associated with the given index
        """
        name = self.params['prefix'] + "_" + str(index) + ".auc"
        return os.path.join(self._datasubdir(), name)

    def _rootdir(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        rootdir = os.path.dirname(current_directory)
        return rootdir

    def _datadir(self):
        return os.path.join(self._rootdir(), "data")

    def _datasubdir(self):
        return os.path.join(self._datadir(), self.params['subdir'])

    def _write_instance(self, filename, instance):
        """ Internal Method.
            Write the instance in the given file.
        Args:
          - A filename to write the instance to
          - The instance to write.
            A NamedTuple(goods, agents).  
            Goods is a list of goods (usually integers).
            Agents is a dictionary from integers to agent objects.
        """
        with open(filename, "w") as file:
            self._write_header(file, instance)
            self._write_goods(file, instance.goods)
            self._write_agents(file, instance.agents)

    def _write_header(self, file, instance):
        file.write("Auction generated by " + self.params['generator'] +
                   " on " + strftime("%Y-%m-%d %H:%M:%S") + "\n")

    def _write_goods(self, file, goods):
        file.write("Goods," + ",".join(map(str, goods)) + "\n")

    def _write_agents(self, file, agents):
        file.write("Agents Start\n")
        for aid in sorted(agents.keys()):
            aout = agents[aid].serialize()
            file.write(str(aid) + "," + aout + "\n")
        file.write("Agents End\n")

    def _read_instance(self, filename):
        """ Internal Method.
            Read the instance in.
        Args:
          - A filename to read the instance from
        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of goods (usually integers).
            Agents is a dictionary from integers to agent objects.
        """
        with open(filename, "r") as file:
            self._read_header(file)
            goods = self._read_goods(file)
            agents = self._read_agents(file)
            return Instance(goods, agents)

    def _read_header(self, file):
        line = file.readline()
        line = line[21:]  # drop constant
        gen = line.split(" on ")[0]
        if gen != self.params['generator']:  # pragma: no cover
            raise Exception("Unexpected generator data file: " + gen)

    def _read_goods(self, file):
        line = file.readline()
        line = line[6:]  # drop constant
        return map(int, line.split(","))

    def _read_agents(self, file):
        line = file.readline().strip()
        if line != "Agents Start":  # pragma: no cover
            raise Exception("Unexpected line: " + line)
        agents = {}
        line = file.readline().strip()
        while line != "Agents End":
            # first get the aid
            idx = line.find(',')
            if idx == -1:  # pragma: no cover
                raise Exception("Misformatted Agent: " + line)
            aid = int(line[:idx])
            line = line[idx + 1:]
            agent = Agent.deserialize(line)
            agents[aid] = agent
            line = file.readline().strip()
        return agents

    @abc.abstractmethod
    def _create_instance(self, index):
        """ Create a new instance at the given index.
        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of goods (usually integers).
            Agents is a dictionary from integers to agent objects.
        """
        raise NotImplementedError("Must Implement _create_instance")


class QuadValueGenerator(Generator):
    """ Generate QuadValue Agents. """

    @classmethod
    def generator_name(cls):
        """ Return the generator name string."""
        return "quadvalue"

    def __init__(self, params):
        super(QuadValueGenerator, self).__init__(params)
        if not 'agents' in params:  # pragma: no cover
            raise ValueError('Parameters must have a number of agents.')
        if not 'goods' in params:  # pragma: no cover
            raise ValueError('Parameters must have a number of goods.')
        if not 'subset' in params:  # pragma: no cover
            raise ValueError('Parameters must have a subset size.')
        if not 'cap' in params:  # pragma: no cover
            raise ValueError('Parameters must have a cap size.')

    def _create_instance(self, index):
        """ Create a new instance at the given index.
        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of integers.
            Agents is a dictionary from integers to agent objects.
        """
        random.seed(index)  # Init to the index for the random seed.
        goods = range(1, self.params['goods'] + 1)
        agents = {}
        for aid in range(1, self.params['agents'] + 1):
            # Create linear values:
            terms = {}
            for g in goods:
                terms[(g,)] = random.random()
            # Now draw a subset of the goods:
            subset = random.sample(goods, self.params['subset'])
            # Create a quadratic term for all pairs in the subset:
            for i in range(len(subset)):
                for j in range(i + 1, len(subset)):
                    a = subset[i]
                    b = subset[j]
                    # value multiplies the terms
                    v = terms[(a,)] * terms[(b,)]
                    terms[(a, b)] = v
            cap = self.params['cap']
            agent = QuadraticValuation(terms, cap)
            agents[aid] = agent
        return Instance(goods, agents)


class CATSGenerator(Generator):
    """ Generate CATS-Based Agents. 
        Data will be stored in standard CATS files
    """

    @classmethod
    def generator_name(cls):
        """ Return the generator name string."""
        return "CATS"

    def __init__(self, params):
        super(CATSGenerator, self).__init__(params)
        if not 'distribution' in params:  # pragma: no cover
            raise ValueError('Parameters must have a distribution.')
        if not 'goods' in params:  # pragma: no cover
            raise ValueError('Parameters must have a number of goods.')
        if not 'bids' in params:  # pragma: no cover
            raise ValueError('Parameters must have a number of bids.')
        if not 'int_prices' in params:  # pragma: no cover
            raise ValueError('Parameters must have int_prices (boolean).')
        if not 'type' in params:  # pragma: no cover
            raise ValueError('Parameters must have type ' +
                             '(SingleMinded | MultiMinded).')

    # Overrides from the super class:

    def _create_instance(self, index):
        """ Create a new instance at the given index.
            We don't have an existing instance.  
            Get CATS to make one.
        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of integers.
            Agents is a dictionary from integers to agent objects.
        """
        self.__runcats(index, output=False)
        return self._read_instance(self._filename_for_index(index))

    def _filename_for_index(self, index):
        """ Internal Method.
        Returns: The filename associated with the given index
        """
        name = self.params['prefix']
        name += '-' + self.params['distribution']
        name += '-G' + str(self.params['goods'])
        name += '-B' + str(self.params['bids'])
        name += '_' + str(index)
        name += '.cats'
        return os.path.join(self._datasubdir(), name)

    def _write_instance(self, filename, instance):
        """ Internal Method.
            Write the instance in the given file.
            No-Op for cats since its all in the CATS file
        """
        pass

    def _read_instance(self, filename):
        """ Internal Method.
            Read the instance in.
            In this case from a CATS file.
        Args:
          - A filename to read the instance from
        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of goods (usually integers).
            Agents is a dictionary from integers to agent objects.
        """
        if self.params['type'] == 'SingleMinded':
            return self.__parse_single_minded(filename)
        elif self.params['type'] == 'MultiMinded':
            return self.__parse_multi_minded(filename)
        else:
            raise Exception('Unknown CATS agent type', params[
                            'type'])  # pragma: no cover

    # Internal methods:

    def __catsdir(self):
        return os.path.join(self._rootdir(), "cats")

    def __catsexecfile(self):
        if sys.platform == 'cygwin' or sys.platform == 'win32':
            executable = 'CATS20WIN.exe'  # pragma: no cover
        else:
            executable = 'CATS20LINUX'  # pragma: no cover
        return os.path.join(self.__catsdir(), executable)

    def __catscmd(self, count=1, output=False, seed=None, seed2=None,
                  prefix=None):
        cmd = [self.__catsexecfile(),
               '-d',     self.params['distribution'],
               '-goods', str(self.params['goods']),
               '-bids',  str(self.params['bids']),
               '-n',     str(count)]
        if self.params['int_prices']:  # pragma: no cover
            cmd.append('-int_prices')
        if not output:  # pragma: no cover
            cmd.append('-no_output')
        if seed:  # pragma: no cover
            cmd.extend(['-seed', str(seed)])
        if seed2:  # pragma: no cover
            cmd.extend(['-seed2', str(seed2)])
        if prefix:  # pragma: no cover
            cmd.extend(['-filename', str(prefix)])
        return cmd

    def __cats_output_filename(self, cidx, prefix=None):
        postfix = (4 - len(str(cidx))) * '0' + str(cidx) + '.txt'
        if prefix:
            return str(prefix) + postfix
        return postfix  # pragma: no cover

    def __runcats(self, index, output=False):
        prefix = 'I' + str(index) + '_'
        cats_output_filename = \
            os.path.join(self._datasubdir(),
                         self.__cats_output_filename(0, prefix=prefix))
        # First ensure the file isn't there:
        if os.path.isfile(cats_output_filename):
            raise Exception('Cats outputfile exists',
                            cats_output_filename)  # pragma: no cover
        # Build the command
        cmd = self.__catscmd(count=1, output=output,
                             seed=index, seed2=index,
                             prefix=prefix)
        # Run it and check the result
        result = subprocess.call(cmd, cwd=self._datasubdir())
        if result != 0:
            raise Exception("Cats returned status", result)  # pragma: no cover
        # Now check outputfile is there:
        if not os.path.isfile(cats_output_filename):
            raise Exception('Cats outputfile not found',
                            cats_output_filename)  # pragma: no cover
        # Now rename the output file
        newname = self._filename_for_index(index)
        os.rename(cats_output_filename, newname)

    def __parse_single_minded(self, filename):
        ''' Parse the CATS file as if it is single minded. '''
        goods = set()
        agents = {}
        with open(filename, 'r') as file:
            aid = 1
            for line in file:
                if line.startswith('goods'):
                    num_goods = int(line.split().pop())
                if not line[0].isdigit():
                    continue
                data = line.strip().split()
                data.pop(0)  # the leading index
                data.pop()  # the trailing hash
                value = float(data.pop(0))
                items = [int(i) for i in data if int(i) < num_goods]
                goods.update(items)
                agent = SingleMinded(Bundle(items), value, aid)
                agents[aid] = agent
                aid += 1
        goods = sorted(list(goods))
        return Instance(goods, agents)

    def __parse_multi_minded(self, filename):
        ''' Parse the CATS file into full multiminded agents '''
        agents = {}
        with open(filename, 'r') as file:
            aid = 1
            active_dummy = None
            xor_bundles = dict()
            for line in file:
                if line.startswith('goods'):
                    num_goods = int(line.split().pop())
                    goods = range(0, num_goods)
                    # print "Num Goods:", num_goods
                if not line[0].isdigit():
                    continue
                data = line.strip().split()
                idx = data.pop(0)              # the leading index
                value = float(data.pop(0))     # the bundle value
                data.pop()                     # the trailing hash
                dummy = int(data.pop())        # the dummy good for agent
                items = [int(i) for i in data]  # the bundle items
                if dummy < num_goods:
                    # print "Found single-minded bid w/o dummy: " + idx
                    # Add the dummy back in, as it's real
                    items.append(dummy)
                    dummy = None
                if dummy <> active_dummy or dummy == None:  # agent complete
                    if len(xor_bundles) > 0:
                        agent = MultiMinded(xor_bundles.items(), aid)
                        agents[aid] = agent
                        aid += 1
                    xor_bundles = dict()
                    active_dummy = dummy
                # Empty bundle assumed to be 0
                if len(items) > 0:  # pragma: no cover
                    xor_bundles[Bundle(items)] = value
            # In case we stopped without a trailing line in the file
            if len(xor_bundles) > 0:  # pragma: no cover
                agent = MultiMinded(xor_bundles.items(), aid)
                agents[aid] = agent
        return Instance(goods, agents)

def remove_dominated(xor_bundles):
    """ Take a dictionary of bundle->value, and remove all the dominated ones"""
    to_remove = []
    for b1 in xor_bundles:
        for b2 in xor_bundles:
            if b1 <= b2 and xor_bundles[b1] > xor_bundles[b2]:
                to_remove.append(b2)
    return {k: v for k,v in xor_bundles.items() if k not in to_remove}

class CanadianGenerator(Generator):
    """ Generate Canadian Auction-Based Agents. 
        For now, just use the supplemental round information.
    """

    @classmethod
    def generator_name(cls):
        """ Return the generator name string."""
        return "CASupplement"

    def __init__(self, params):
        params['subdir']='CASupplement'
        params['prefix']='CASupplement'
        super(CanadianGenerator, self).__init__(params)

    # Overrides from the super class:

    def _create_instance(self, index):
        """ Create the one and only instance.
            If index is anything other than 1, throw an exception.
        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of integers.
            Agents is a dictionary from integers to agent objects.
        """
        return self._read_instance(self._filename_for_index(index))

    def _filename_for_index(self, index):
        """ Internal Method.
        Returns: The filename associated with the given index
        """
        if index != 1:
            raise Exception('Only 1 is a valid index')
        return os.path.join(self.__canadiandir(), 'b_supp_en.csv')

    def _write_instance(self, filename, instance):
        """ Internal Method.
            Write the instance in the given file.
            No-Op since we use the raw file.
        """
        pass

    def _read_instance(self, filename):
        """ Internal Method.
            Read the instance in.
            In this case from a CA auction file file.
        Args:
          - A filename to read the instance from
        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of goods (usually integers).
            Agents is a dictionary from integers to agent objects.
        """
        return self.__parse_multi_minded(filename)

    # Internal methods:

    def __canadiandir(self):
        return os.path.join(self._rootdir(), "canadian")

    def __parse_multi_minded(self, filename):
        ''' Parse the Canadian Auction CSV file into multiminded agents '''
        ''' NOTE: The auction auction has TWO license in the BC, C1C2 and DE
            bands.  Here we ignore this.  We assume there is only a single
            license available, and all bids are for single liceneses.
            This reduces the total goods from 98 by 42 to 56.
        '''
        agents = {}
        goods = None
        with open(filename, 'r') as file:
            ca_reader = csv.reader(file)
            xor_bundles = dict()
            aid = 1
            header = ca_reader.next()
            COMPANY = header.index('Company ID')
            VALUE = header.index('Price ($)')
            FIRST_GOOD = \
                header.index('A-Newfoundland & Labrador')
            LAST_GOOD = \
                header.index('C1C2-Yukon & Northwest Territories & Nunavut')
            goods = range(0, LAST_GOOD - FIRST_GOOD+1)
            last_company = None
            for line in ca_reader:
                company = line[COMPANY]
                value = int(line[VALUE])
                if last_company == company:
                    items = [i for i in goods if line[FIRST_GOOD+i] in {'1','2'}]
                    xor_bundles[Bundle(items)] = value
                else:
                    if len(xor_bundles) > 0:
                        xor_bundles = remove_dominated(xor_bundles)
                        agent = MultiMinded(xor_bundles.items(), aid)
                        agents[aid] = agent
                        aid += 1
                    xor_bundles = dict()
                last_company = company
        return Instance(goods, agents)

class ExpansionDistribution(object):
    """ Helper class for the CanadianGeneratorExpanded distributions """
    def __init__(self, shape, locationpct):
        self.shape = shape
        self.locationpct = locationpct

    def get_location(self, obs_value):
        # lower support of dist, for distributions who are [0,_] 
        return self.locationpct*obs_value

    @abc.abstractmethod
    def get_scale(self, obs_less_loc):
        pass

    @abc.abstractmethod
    def dist_class(self):
        pass

    def get_sample(self, shape, scale, location):
        return self.dist_class().rvs(shape, scale=scale, loc=location)

    def expand_value(self, obs_value):
        """compute the expanded value for the given value"""
        shape = self.shape
        location = self.get_location(obs_value)
        scale = self.get_scale(obs_value-location)
        sample = self.get_sample(shape, scale, location)
        return sample

class LomaxExpansionDistribution(ExpansionDistribution):
    def __init__(self, shape, locationpct):
        super(LomaxExpansionDistribution, self).__init__(shape, locationpct)

    def get_scale(self, obs_less_loc):
        return obs_less_loc*(self.shape-1)

    def dist_class(self):
        return scipy.stats.lomax

class LognormExpansionDistribution(ExpansionDistribution):
    def __init__(self, shape, locationpct):
        super(LognormExpansionDistribution, self).__init__(shape, locationpct)

    def get_scale(self, obs_less_loc):
        return obs_less_loc / numpy.sqrt(numpy.exp(self.shape**2))  

    def dist_class(self):
        return scipy.stats.lognorm

class GammaExpansionDistribution(ExpansionDistribution):
    def __init__(self, shape, locationpct):
        super(GammaExpansionDistribution, self).__init__(shape, locationpct)

    def get_scale(self, obs_less_loc):
        return obs_less_loc / self.shape

    def dist_class(self):
        return scipy.stats.gamma

class CanadianGeneratorExpanded(Generator):
    """ Generate Canadian Auction-Based Agents. 
        For now, just use the supplemental round information.
        This class goes beyond the basic CanadianGenerator by allowing
        for a random perturbation of the values.
        The way the perturbation works is described in a Latex Note stored
        separately in source repository.
    """

    @classmethod
    def generator_name(cls):
        """ Return the generator name string."""
        return "CASupplementExpanded"

    def __init__(self, params):
        super(CanadianGeneratorExpanded, self).__init__(params)

        if not 'shape' in params:  # pragma: no cover
            raise ValueError('Parameters must have shape.')
        # The distribution shape parameter:
        # Lomax: alpha 
        # Log-Normal: sigma^2
        # Gamma: k 
        shape = params['shape']

        #scale:
        # We don't include as a parameter, as we set the scale to 
        # match the observed data.

        if not 'locationpct' in params:  # pragma: no cover
            raise ValueError('Parameters must have locationpct.')
        # Percentage in [0,1]
        # Distribution support lower bound will be locationpct*observed
        # (i.e. locationpct*observed will be the location param)
        locationpct = params['locationpct']

        if not 'distribution' in params:  # pragma: no cover
            raise ValueError('Parameters must have a distribution.')
        if 'lomax' == params['distribution']:
            self.dist = LomaxExpansionDistribution(shape,locationpct)
        elif 'lognorm' == params['distribution']:
            self.dist = LognormExpansionDistribution(shape,locationpct)
        elif 'gamma' == params['distribution']:
            self.dist = GammaExpansionDistribution(shape,locationpct)
        else:
            raise ValueError("Unknown distribution" + params['distribution'])
        
        # We don't subclass -- we just create a CanadianGenerator and
        # use it to get the fundamental instance which we then perturb
        from generatorfactory import GeneratorFactory, CANADIAN_SUPPLEMENT
        self.ca_supp_inst = \
            GeneratorFactory.get(CANADIAN_SUPPLEMENT).get_instance(1)

    # Overrides from the super class:

    def _create_instance(self, index):
        """ Create a new instance at the given index.
        Returns:
            A NamedTuple(goods, agents).  
            Goods is a list of integers.
            Agents is a dictionary from integers to agent objects.
        """
        random.seed(index)       # Init to the index for the random seed.
        numpy.random.seed(index) # Make sure to cover numpy too
        goods = list(self.ca_supp_inst.goods)
        agents = {}
        for aid in self.ca_supp_inst.agents.keys():
            real_agent = self.ca_supp_inst.agents[aid]
            terms = { b : self.dist.expand_value(v) \
                          for (b,v) in real_agent.xor.list_terms()}
            terms = remove_dominated(terms)
            agent = MultiMinded(terms, aid)
            agents[aid] = agent
        return Instance(goods, agents)
