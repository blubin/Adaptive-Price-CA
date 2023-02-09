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

""" Module defines the base classes for all of our experiments """

import abc
import sys
import os
import time
import copy
import csv
import itertools
import multiprocessing
import functools
import traceback
import argparse
import types
import inspect
import numpy as np

import adaptiveCA.generatorfactory
from adaptiveCA.agents import *
from adaptiveCA.auctions import *
from adaptiveCA.instrumentation import AuctionInstrumentation
#from adaptiveCA.mpsolve import restrict_to_cpu
from adaptiveCA.experiments.cpurestrict import restrict_to_cpu
from adaptiveCA.util.modcsv import ModifiableDictWriter

def poolinit(queue):
    ''' Initialize the current thread '''
    cpu = queue.get()
    restrict_to_cpu(cpu)

def trace_unhandled_exceptions(func):
    ''' Setup a wrapper that will cause exceptions to be tracable'''
    # See:
    # http://stackoverflow.com/questions/6728236/exception-thrown-in-multiprocessing-pool-not-detected
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print 'Exception in', func.__name__
            traceback.print_exc()
    return wrapped_func


@trace_unhandled_exceptions
def process_instance(experiment, params, idx):
    """ Internal method for processing an instance, but
        must be defined at the top level so it is paralelizable. """
    if experiment._is_instance_run(params, idx):
        try:
            experiment._pre_instance(params, idx)
            experiment._go_instance(params, idx)
            experiment._post_instance(params, idx)
        except Exception as e:
            print repr(e) + ' in groupstr="' + \
                str(experiment._get_group_string(params)) + \
                '" instance=' + str(idx) 
            raise
        return True
    return False


def process_instance_callback(status):
    sys.stdout.write('r' if status else 's')
    sys.stdout.flush()


class Experiment(object):
    __metaclass__ = abc.ABCMeta

    ASSUME_HYPERTHREAD = True
    RESERVE_ONE_CORE = False

    def __init__(self, shortname):
        super(Experiment, self).__init__()
        self.shortname = shortname
        self.parallel = True
        self.run_only_instance = None
        self.run_only_auctiongroupstr = None

    # Parameters:
    #############

    @abc.abstractproperty
    def _param_sets(self):  # pragma: no cover
        """ The parameter sets for this experiment.
            Should return a dictionary of dictionaries.
            Keys are Strings,
            Values of inner dict are basic types or a list of basic types.
              If they are a list, then multiple groups will occur,
              one for each value of the list.
        """
        raise NotImplementedError("Abstract")

    @abc.abstractproperty
    def _default_param_set_name(self):  # pragma: no cover
        """ The default parameter set for this experiment.
            Returns a string.
        """
        raise NotImplementedError("Abstract")

    def _check_parameters(self, params):
        """ Raise an exception if the parameters are invalid.
        """
        if not 'num_instances' in params:
            raise ValueError('Expected param: num_instances')

    def parse(self):
        """ Parse the command line arguments """
        parser = argparse.ArgumentParser(description='Run an experiment')
        parser.add_argument('--list_param_sets',
                            action='store_true',
                            help='list what param sets are available')
        parser.add_argument('--not_parallel',
                            dest='parallel', action='store_false',
                            help='run instances serial instead of parallel')
        parser.add_argument('param_set_name', nargs='?',
                            default=self._default_param_set_name(),
                            help='if absent, default will be: "' +
                                 self._default_param_set_name() + '"')
        args = parser.parse_args()
        if args.list_param_sets:
            print 'Available parameter sets:'
            for k in sorted(self._param_sets().keys()):
                print k
            sys.exit(0)
        self.parallel = args.parallel
        self._param_set_name = args.param_set_name
        if not self._param_set_name in self._param_sets():
            raise ValueError("Unexpected parameter set", self._param_set_name)
        self._params = self._param_sets()[self._param_set_name]
        self._check_parameters(self._params)
        return self

    def _get_list_param_keys(self):
        """ Get a sequence of those parameter keys whose value are lists."""
        return sorted([k for k in self._params.keys()
                       if isinstance(self._params[k], (list, tuple))])

    def _get_group_params(self):
        """ Generator function: the sequence of parameters for each group. """
        list_keys = self._get_list_param_keys()
        if len(list_keys) == 0:
            # No lists, so just use the params as is:
            yield self._params
        else:
            list_values = [params[k] for k in list_keys]
            for values in itertools.product(*list_values):
                p = copy.copy(params)
                for k, v in zip(list_keys, values):
                    p[k] = v
                yield p

    # Directories:
    ##############

    def _rootdir(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        adaptiveCAdir = os.path.dirname(current_directory)
        rootdir = os.path.dirname(adaptiveCAdir)
        return rootdir

    def _experimentsdir(self):
        return os.path.join(self._rootdir(), "experiments")

    def _experimentssubdir(self):
        return os.path.join(self._experimentsdir(),
                            self.shortname + "_" + self._param_set_name)

    def _instancessubsubdir(self):
        return os.path.join(self._experimentssubdir(), 'instances')

    def _ensuredirs(self):
        if not os.path.exists(self._experimentsdir()):
            try:
                os.mkdir(self._experimentsdir())  # pragma: no cover
            except OSError as e:
                print 'Warning', e
        if not os.path.exists(self._experimentssubdir()):
            try:
                os.mkdir(self._experimentssubdir())  # pragma: no cover
            except OSError as e:
                print 'Warning', e
        if not os.path.exists(self._instancessubsubdir()):
            try:
                os.mkdir(self._instancessubsubdir())  # pragma: no cover
            except OSError as e:
                print 'Warning', e

    # File Naming:
    ##############

    def _get_group_string(self, params):
        """ Get a string that captures the group name. """
        keys = self._get_list_param_keys()

        def shorten(str):
            return str + "_"

        def to_str(obj):
            return str(obj)
        # Because some keys get removed if they are not part of the
        # auction, remove them here too:
        keys = [k for k in keys if k in params]
        return "#".join([shorten(k) + to_str(params[k]) for k in keys])

    def _get_instance_string(self, params, idx):
        """ Get a string that captures the group and instance name."""
        grp = self._get_group_string(params)
        if len(grp) > 0:
            grp = "#" + grp
        return grp + "#Idx_" + str(idx)

    def _filename_for_instance(self, params, idx,
                               type_name, extension=".csv"):
        """ Get a filename for a given instance.
            type_name - an extra string to specify which file this is. """
        name = str(type_name)
        name += self._get_instance_string(params, idx)
        name += extension
        return os.path.join(self._instancessubsubdir(), name)

    def _filename_for_group(self, params,
                            type_name, extension=".csv"):
        """ Get a filename for a given group file.
            type_name - an extra string to specify which file this is. """
        name = str(type_name)
        name += "#"
        name += self._get_group_string(params)
        name += extension
        return os.path.join(self._experimentssubdir(), name)

    # Running:
    ##########

    def _pre_run(self):  # pragma: no cover
        """ Setup to run the full experiment """
        pass

    def _post_run(self):  # pragma: no cover
        """ Finish running the full experiment. """
        pass

    def _pre_group(self, params):  # pragma: no cover
        """ before group """
        pass

    def _post_group(self, params):  # pragma: no cover
        """ after group """
        pass

    def _pre_instance(self, params, idx):  # pragma: no cover
        """ before instance """
        pass

    def _post_instance(self, params, idx):  # pragma: no cover
        """ after instance """
        pass

    def _go_group(self, pool, params):
        """ Run the experiment itself. """
        if self.run_only_instance:
            # Used only for debugging to run a single instance:
            if self.parallel:
                pool.apply_async(process_instance,
                                 args=(self, params, self.run_only_instance),
                                 callback=process_instance_callback)
            else:
                ret = process_instance(self, params, self.run_only_instance)
                process_instance_callback(ret)
        else:
            # In all other cases, run a whole range of instances
            num_instances = int(params.get('num_instances', 1))
            if self.parallel:
                for idx in range(1, num_instances + 1):
                    pool.apply_async(process_instance,
                                     args=(self, params, idx),
                                     callback=process_instance_callback)
            else:
                for idx in range(1, num_instances + 1):
                    ret = process_instance(self, params, idx)
                    process_instance_callback(ret)

    def _is_instance_run(self, params, idx):  # pragma: no cover
        """ should the instance be run """
        return True

    @abc.abstractmethod
    def _go_instance(self, params, idx):  # pragma: no cover
        """ Run the experiment instance itself. """
        raise NotImplementedError("Abstract")

    def run(self):
        """ Run the experiment """
        print(" Experiment %s on %s params." %
              (self.shortname, self._param_set_name))

        print("Setup... ")
        self._ensuredirs()
        self._pre_run()

        for params in self._get_group_params_with_restriction():
            print(" Pre-Processing Group " +
                  self._get_group_string(params) + "...")
            self._pre_group(params)
        print "Done."

        print "Running Experiment..."
        # Setup the thread pool
        cores = multiprocessing.cpu_count()
        if self.ASSUME_HYPERTHREAD:
            # Python can't tell us if there are hyperthreads
            # So if instructed, we just assume there are:
            cores /= 2
        if self.RESERVE_ONE_CORE:
            cores = max(1, cores - 1)  # Set to one less than available
        # We need each thread to know its unique id so it can assign
        # work to a particular CPU.  So setup a queue to do this
        core_queue = multiprocessing.Queue()  # Queue for the threads
        for core in range(1, cores + 1):
            core_queue.put(core)
        pool = multiprocessing.Pool(cores, poolinit, (core_queue,))

        sys.stdout.write(" Submitting all groups to the thread pool... ")
        for params in self._get_group_params_with_restriction():
            #print(" Running Group " + self._get_group_string(params)+"...")
            #sys.stdout.write('  ')
            self._go_group(pool, params)
            # print
        print " Done."
        print " Waiting for completion "
        pool.close()
        pool.join()
        print "\nDone."

        print("Finalize... ")
        for params in self._get_group_params_with_restriction():
            print(" Post-Processing Group " +
                  self._get_group_string(params) + "...")
            self._post_group(params)

        self._post_run()
        print("Done.")


class AuctionExperiment(Experiment):
    """ An experiment specific to an auction. """
    __metaclass__ = abc.ABCMeta

    def __init__(self, shortname, 
                 include_round_file = False,
                 include_prices_file=False,
                 include_xorprices_file=False):
        super(AuctionExperiment, self).__init__(shortname)
        # Should we include the round file?
        self.include_round_file = include_round_file
        self.include_prices_file = include_prices_file
        self.include_xorprices_file = include_xorprices_file

    def _check_parameters(self, params):
        super(AuctionExperiment, self)._check_parameters(params)
        if not 'generator_param_name' in params:
            raise ValueError('Expected param: generator_param_name')

        if not 'auction_class' in params:
            raise ValueError('Expected param: auction_class')

        def all_subclasses(cls):
            return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                           for g in all_subclasses(s)]
        auction_classes = params['auction_class']
        if not isinstance(auction_classes, (list, tuple)):
            auction_class = [auction_classes]
        if not set(auction_classes).issubset(
           set([x for x in all_subclasses(Auction)])):
            raise ValueError('Unknown auction class: ' +
                             str(params['auction_class']))
        # Note: we don't check the auction parameters here for now
        # because the different auctions require different parameters

        if not 'scalebyvalue' in params:
            raise ValueError('Expected param: scalebyvalue')

        if not 'maxiter' in params:
            raise ValueError('Expected param: maxiter')

        if not 'maxtime' in params:
            raise ValueError('Expected param: maxtime')

        # Check that the run_only_auctiongroupstr is valid:
        if self.run_only_auctiongroupstr:
            #found = False
            found = True
            for k in self._get_group_params():
                if self._get_group_string(k) == self.run_only_auctiongroupstr:
                    found = True
            if not found:
                raise ValueError('Auction Group not found: ' +
                                 self.run_only_auctiongroupstr + " in " +
                                 str([self._get_group_string(k) for k in 
                                      self._get_group_params()]))

    def _get_group_string(self, params):
        """ Get a string that captures the group name. """
        keys = self._get_list_param_keys()

        def shorten(str):
            if str == "auction_class":
                return ''
            elif str == 'generator_param_name':
                return 'gen_'
            return str + "_"

        def to_str(obj):
            if isinstance(obj, (types.TypeType, types.ClassType)):
                return obj.__name__
            return str(obj)
        # Because some keys get removed if they are not part of the
        # auction, remove them here too:
        keys = [k for k in keys if k in params]
        return "#".join([shorten(k) + to_str(params[k]) for k in keys])

    def _get_group_params_with_restriction(self):
        """ Get the group params, but if we are supposed to restrict
            to a single param, only return that instead.
        """
        if self.run_only_auctiongroupstr:
            for k in self._get_group_params():
                if self._get_group_string(k) == self.run_only_auctiongroupstr:
                    return [k]
            raise ValueError('Auction Group not found: ' +
                             self.run_only_auctiongroupstr + " in " +
                             str([self._get_group_string(k) for k in 
                                  self._get_group_params()]))
        else:
            return self._get_group_params()

    def _get_group_params(self):
        """ Generator function: the sequence of parameters for each group.
            Override so it pays attention to the auction class.
        """
        def create_generator(params, list_keys, cls):
            list_values = [params[k] for k in list_keys]
            for values in itertools.product(*list_values):
                #handle the case where bidding_strategy='default': for
                #that case drop all the heuristic_pool_num except the first
                if 'bidding_strategy' in list_keys and 'heuristic_pool_num' in list_keys:
                   d = dict(zip(list_keys, values))
                   if d['bidding_strategy'] == 'default' and d['heuristic_pool_num']!=params['heuristic_pool_num'][0]:
                      continue
                p = copy.copy(params)
                p['auction_class'] = cls
                for k, v in zip(list_keys, values):
                    p[k] = v
                yield p
        list_keys = self._get_list_param_keys()
        if len(list_keys) == 0:
            # No lists, so just use the params as is:
            return [self._params]
        elif not 'auction_class' in list_keys:
            # Auction class is not list, so just iterate over others:
            return create_generator(self._params, list_keys,
                                    self._params['auction_class'])
        else:
            # Auction class is in list, so handle it separately:
            list_keys.remove('auction_class')
            iterables = []
            for cls in self._params['auction_class']:
                # Get rid of any keys that aren't an argument:
                reduced_keys = copy.copy(list_keys)
                params = copy.copy(self._params)
                for k in self._get_all_auction_paramkeys():
                    if k in list_keys and not self._is_paramkey_for_auction_cls(cls, k):
                        reduced_keys.remove(k)
                        del params[k]
                iterables.append(create_generator(params, reduced_keys, cls))
            # Now flatten the iterables and return a single one:
            return itertools.chain.from_iterable(iterables)

    def _get_all_auction_paramkeys(self):
        ''' Get all the parameters experiment parameters that are passed 
            directly to the auction constructor.  We handle these special -- 
            if we are running with a list of these parameters, any auction 
            which doesn't take it as an argument will only be run once.
        '''
        return ['epsilon', 'stepc', 'epoch']

    def _is_paramkey_for_auction_cls(self, auction_cls, key):
        """ Can this auction be configured by this parameter? """
        args = inspect.getargspec(auction_cls.__init__).args
        return key in args

    def _is_instance_run(self, params, idx):
        """ We'll only run it if the instance file isn't there """
        inst_filename = self._filename_for_instance(params,
                                                    idx,
                                                    'instance')
        return not os.path.exists(inst_filename)

    def _go_instance(self, params, idx):
        instance = self._get_generator_instance(params, idx)
        auction = self._get_auction(params, idx, instance)
        auction.run()

    def _get_generator_param_set(self, params):
        gen_param_name = params['generator_param_name']
        # First look in the generator factory module:
        gen_param_set = getattr(adaptiveCA.generatorfactory,
                                gen_param_name, None)
        if gen_param_set == None:
            # Otherwise look in the current module:
            module = sys.modules[self.__module__]
            gen_param_set = getattr(module,
                                    gen_param_name, None)
        if gen_param_set == None:
            raise ValueError('Unknown generator params: ' + gen_param_name)
        return gen_param_set

    def _get_generator_instance(self, params, idx):
        if not hasattr(self, '__generator'):
            factory = adaptiveCA.generatorfactory.GeneratorFactory()
            gen_param_set = self._get_generator_param_set(params)
            self.__generator = factory.get(gen_param_set)
        return self.__generator.get_instance(idx)

    def _scalevalue(self, instance):
        """ Obtain the scaling value for the given instance.
            For QuedraticValue, just use the max
            For MultiMinded (cats), use the median
            Otherwise complain.
        """
        cls = instance.agents.values()[0].__class__  # Just use the first.
        if issubclass(cls, QuadraticValuation):
            # Do max for the QV
            grand = Bundle(instance.goods)
            return max(a.valueq(grand) for a in instance.agents.values())
        elif issubclass(cls, MultiMinded):
            # Do median for multiminded
            vals = []
            for a in instance.agents.values():
                vals.extend([a.valueq(b) for b in a.xor.bundles()])
            return np.median(vals)
        else:
            raise Exception("Unknown agent class:", cls)

    def _get_auction(self, params, idx, instance):
        def maxval(instance):
            grand = Bundle(instance.goods)
            return max(a.valueq(grand) for a in instance.agents.values())

        V = self._scalevalue(instance) if params['scalebyvalue'] else 1
        args = {'items': instance.goods,
                'agents': instance.agents}
        if 'epsilon' in params:
            args['epsilon'] = V * params['epsilon']
        if 'stepc' in params:
            args['stepc'] = V * params['stepc']
            #Set Gamma to an unscaled version of stepc.
            #(For LCA we use gamma instead of stepc because it is by
            # default a relative measure.  Because its relative, never
            # scale by the value.  We base it on stepc, so it can setup
            # in the same way as the other types of auctions).
            args['gamma'] = params['stepc']
        if 'epoch' in params:
            args['epoch'] = params['epoch']
        if 'reserve_type' in params: #For LinearClockAuction
            args['reserve_type'] = params['reserve_type']
        if 'personalized' in params: #For AdaptiveCuttingAuction
            args['personalized'] = params['personalized']
        auction_cls = params['auction_class']
        auction = auction_cls(**args)
        instr = AuctionExperimentInstrumentation(auction, self, params, idx,
                                                 V,
                                                 self.include_round_file,
                                                 self.include_prices_file,
                                                 self.include_xorprices_file)
        auction.set_instrumentation(instr)
        auction.maxiter = params['maxiter']
        auction.maxtime = params['maxtime']

        if isinstance(auction, HeuristicAuction) or \
           isinstance(auction, SubgradientAuction):
            if 'bidding_strategy' in params:
                auction.bidding_strategy = params['bidding_strategy']
            if 'heuristic_pool_num' in params:
                auction.heuristic_pool_num = params['heuristic_pool_num']
        return auction

    def _post_group(self, params):
        # Combine all of the files in the group into one CSV
        self._create_combined_file(params, 'instance')
        if self.include_round_file:
            self._create_combined_file(params, 'round')
        if self.include_prices_file:
            self._create_combined_file(params, 'prices')
        if self.include_xorprices_file:
            self._create_combined_file(params, 'xorprices')


    def _create_combined_file(self, params, type_name, extension=".csv"):

        # first determine the superset of all fieldnames:
        fieldnames = []
        idx = 1
        while True:
            fname = self._filename_for_instance(params, idx,
                                                type_name, extension)
            if not os.path.exists(fname):
                break
            
            # Find the fieldnames:
            with open(fname, 'r') as infile:
                try:
                    reader = csv.DictReader(infile)
                    for field in reader.fieldnames:
                        if not field in fieldnames:
                            fieldnames.append(field)
                except TypeError as e:
                    sys.stderr.write('Error reading file: ' + fname +"\n")
                    raise e
            idx += 1

        # Create the file:
        combined_fname = self._filename_for_group(params, type_name, extension)
        with open(combined_fname, 'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            idx = 1
            while True:
                fname = self._filename_for_instance(params, idx,
                                                    type_name, extension)
                if not os.path.exists(fname):
                    break
                with open(fname, 'r') as infile:
                    reader = csv.DictReader(infile)
                    for row in reader:
                        writer.writerow(row)
                idx += 1

class AuctionExperimentInstrumentation(AuctionInstrumentation):
    """ We will produce two files:
        - round = information in every round of the auction
        - instance = summary information across the full instance
    """

    def __init__(self, auction, experiment, params, idx, 
                 scalevalue,
                 include_round_file=True,
                 include_prices_file=True,
                 include_xorprices_file=True):
        super(AuctionExperimentInstrumentation, self).__init__(auction)
        self.experiment = experiment
        self.params = params
        self.idx = idx
        self.scalevalue = scalevalue
        self.include_round_file = include_round_file
        self.include_prices_file = include_prices_file
        self.include_xorprices_file = include_xorprices_file

    # The Instrumentation Members:
    ##############################

    def pre_run(self, auction):
        if self.include_round_file:
            self._open_round_file()
        if self.include_prices_file:
            self._open_prices_file()
        if self.include_xorprices_file:
            self._open_xorprices_file()
        self.start_time = time.clock()

    def pre_round(self, auction):
        pass

    def post_round(self, auction):
        # Push forward the start time by the time for instrumentation
        if self.include_round_file:
            rem_time = time.clock()
            self._writerow_round_file()
            rem_time = time.clock() - rem_time
            self.start_time += rem_time
        if self.include_prices_file:
            rem_time = time.clock()
            self._writerow_prices_file()
            rem_time = time.clock() - rem_time
            self.start_time += rem_time
        if self.include_xorprices_file:
            rem_time = time.clock()
            self._writerow_xorprices_file()
            rem_time = time.clock() - rem_time
            self.start_time += rem_time


    def post_run(self, auction):
        self.end_time = time.clock()
        self.runtime = self.end_time - self.start_time
        if self.include_round_file:
            self._close_round_file()
        if self.include_prices_file:
            self._close_prices_file()
        if self.include_xorprices_file:
            self._close_xorprices_file()
        self._create_instance_file()

    # Round File Management:
    ########################

    def _open_round_file(self):
        filename = self.experiment._filename_for_instance(self.params,
                                                          self.idx,
                                                          'round')
        self.roundfile = open(filename, 'w')
        fieldnames = self._param_headers()
        fieldnames.extend(['round'])
        fieldnames.extend(self._common_headers('curr'))
        self.roundcsv = csv.DictWriter(self.roundfile, fieldnames)
        self.roundcsv.writeheader()

    def _writerow_round_file(self):
        fields = self._param_fields()
        fields.update(self._common_fields('curr'))
        fields.update({'round': self._rounds()})
        self.roundcsv.writerow(fields)
        self.roundfile.flush()

    def _close_round_file(self):
        self.roundfile.close()

    # Prices File Management:
    #########################

    def _open_prices_file(self):
        filename = self.experiment._filename_for_instance(self.params,
                                                          self.idx,
                                                          'prices')
        self.pricesfile = open(filename, 'w+')
        fieldnames = self._param_headers()
        fieldnames.extend(['round'])
        self.pricescsv = ModifiableDictWriter(self.pricesfile, fieldnames)
        self.pricescsv.writeheader()

    def _writerow_prices_file(self):
        fields = self._param_fields()
        fields.update({'round': self._rounds()})
        fields.update(self._prices().as_ordered_dict())
        self.pricescsv.writerow(fields)
        self.pricesfile.flush()

    def _close_prices_file(self):
        self.pricesfile.close()


    # XorPrices File Management:
    ############################

    def _open_xorprices_file(self):
        filename = self.experiment._filename_for_instance(self.params,
                                                          self.idx,
                                                          'xorprices')
        self.xorpricesfile = open(filename, 'w+')
        fieldnames = self._param_headers()
        fieldnames.extend(['round'])
        # Now get all the xor bundles:
        instance = self.experiment._get_generator_instance(self.params,
                                                           self.idx)
        self.xorpricesbundles = set()
        for agent in instance.agents.values():
            # Check that it is multi-minded
            if not isinstance(agent, MultiMinded):
                raise Exception("XorPrices only writable by MultiMind agents")
            #Walk the bundles of interest
            for b in agent.xor.bundles():
                self.xorpricesbundles.add(b)
        self.xorpricesbundles = list(self.xorpricesbundles)
        self.xorpricesbundles.sort()
        fieldnames.extend([b.csvable() for b in self.xorpricesbundles])
        self.xorpricescsv = csv.DictWriter(self.xorpricesfile, fieldnames)
        self.xorpricescsv.writeheader()

    def _writerow_xorprices_file(self):
        fields = self._param_fields()
        fields.update({'round': self._rounds()})
        p = self._prices()
        if p.personalized:
            filename = self.experiment._filename_for_instance(self.params,
                                                              self.idx,
                                                              'xorprices')
            sys.stderr.write(filename+": Personalized Prices\n")
        # Add prices for all bundles:
        for b in self.xorpricesbundles:
            if p.personalized:
                fields[b.csvable()] = p.all_agents_str(b)                
            else:
                fields[b.csvable()] = p.price(b)
        self.xorpricescsv.writerow(fields)
        self.xorpricesfile.flush()

    def _close_xorprices_file(self):
        self.xorpricesfile.close()

    # Instance File Management:
    ###########################

    def _create_instance_file(self):
        inst_filename = \
            self.experiment._filename_for_instance(self.params,
                                                   self.idx,
                                                   'instance')
        fieldnames = self._param_headers()
        fieldnames.extend(['rounds',
                           'status',
                           'runtime',
                           'efficient_value'])
        fieldnames.extend(self._common_headers('final'))
        with open(inst_filename, 'w') as instfile:
            summarycsv = csv.DictWriter(instfile, fieldnames)
            summarycsv.writeheader()
            fields = self._param_fields()
            fields.update(self._common_fields('final'))
            fields.update({'rounds': self._rounds(),
                           'status': self.auction.status,
                           'runtime': self.runtime,
                           'efficient_value': self._efficient_value()})
            summarycsv.writerow(fields)

    # Param Fields:
    ###############

    def _param_headers(self):
        headers = ['idx',
                   'items',
                   'agents',
                   'auction_class',
                   'epsilon',
                   'stepc',
                   'epoch',
                   'scalebyvalue',
                   'reserve_type',
                   'maxiter',
                   'maxtime',
                   'generator_param_name',
                   'personalized']

        if 'expstrat' in self.params:
            headers.append('expstrat')
        if 'bidding_strategy' in self.params:
            headers.append('bidding_strategy')
        if 'heuristic_pool_num' in self.params:
            headers.append('heuristic_pool_num')

        gen_param_set = self.experiment._get_generator_param_set(self.params)
        # remove columns we don't want:
        gen_param_set = copy.copy(gen_param_set)
        del gen_param_set['subdir']
        del gen_param_set['prefix']
        if 'goods' in gen_param_set:
            del gen_param_set['goods']
        if 'agents' in gen_param_set:
            del gen_param_set['agents']
        headers.extend(gen_param_set.keys())
        return headers

    def _param_fields(self):
        fields = {'idx': self.idx,
                  'items': len(self.auction.items),
                  'agents': len(self.auction.agents)}
        fields.update(self.params)
        # Add the generator fields:
        gen_param_set = self.experiment._get_generator_param_set(self.params)
        # remove columns we don't want:
        gen_param_set = copy.copy(gen_param_set)
        del gen_param_set['subdir']
        del gen_param_set['prefix']
        if 'goods' in gen_param_set:
            del gen_param_set['goods']
        if 'agents' in gen_param_set:
            del gen_param_set['agents']
        fields.update(gen_param_set)
        # Don't include the following, if they aren't part of the auction:
        self._remove_key_if_not_in_auction(self.auction, fields, 'epsilon')
        self._remove_key_if_not_in_auction(self.auction, fields, 'stepc')
        self._remove_key_if_not_in_auction(self.auction, fields, 'epoch')
        self._remove_key_if_not_in_auction(self.auction, fields,'reserve_type')
        self._remove_key_if_not_in_auction(self.auction, fields,'personalized')

        # Don't include the strategy fields if it isn't a HeuristicAuction
        if not (isinstance(self.auction, HeuristicAuction) or
                isinstance(self.auction, SubgradientAuction)):
            if 'bidding_strategy' in fields:
                del fields['bidding_strategy']
            if 'heuristic_pool_num' in fields:
                del fields['heuristic_pool_num']

        # Don't include number of instances:
        del fields['num_instances']
        # Record the class as a string, not a class:
        fields['auction_class'] = fields['auction_class'].__name__
        return fields

    def _remove_key_if_not_in_auction(self, auction, fields, key):
        if not self._is_key_in_auction(auction, key) and key in fields:
            del fields[key]

    def _is_key_in_auction(self, auction, key):
        args = inspect.getargspec(auction.__class__.__init__).args
        return key in args

    # Common Fields:
    ###############

    def _common_headers(self, prefix):
        return [prefix + '_num_winners',
                prefix + '_max_agent_value',
                prefix + '_scalevalue',
                prefix + '_value',
                prefix + '_total_price',
                prefix + '_revenue',
                prefix + '_indirect_util',
                prefix + '_price_degree',
                prefix + '_price_sparsity',
                prefix + '_imbalance',
                prefix + '_wd_nvars',
                prefix + '_wd_ncons']

    def _common_fields(self, prefix):
        fields = {prefix + '_num_winners': self._winners(),
                  prefix + '_max_agent_value': self._max_agent_value(),
                  prefix + '_scalevalue': self.scalevalue,
                  prefix + '_value': self._current_value(),
                  prefix + '_total_price': self._current_total_price(),
                  prefix + '_revenue': self._current_revenue(),
                  prefix + '_indirect_util': self._current_ind_util(),
                  prefix + '_price_degree': self._price_degree(),
                  prefix + '_price_sparsity': self._price_sparsity(),
                  prefix + '_imbalance': self._imbalance(),
                  prefix + '_wd_nvars': self._wd_size()[0],
                  prefix + '_wd_ncons': self._wd_size()[1]}
        return fields
