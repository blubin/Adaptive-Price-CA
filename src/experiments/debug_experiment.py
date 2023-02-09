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

""" Module that:
    - provides information about a given experiment
    - enables running a single instance repeatably
    Provision is made to invoke these interactively, or
    from the command line.
"""

import argparse
import sys
import logging
from adaptiveCA.experiments.experiment import Experiment, AuctionExperiment
from adaptiveCA.experiments.basic import BasicExperiment
from adaptiveCA.experiments.subgradient import SubgradientExperiment
from adaptiveCA.experiments.bidscale import BidScaleExperiment
from adaptiveCA.experiments.CASupplement import CASupplementExperiment
from adaptiveCA.experiments.lca import LCAExperiment
from adaptiveCA.experiments.cutting import CuttingExperiment
from adaptiveCA.experiments.strategy import StrategyExperiment

def all_subclasses(cls):
    """ Get all subclasses of a given class"""
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]


class DebugExperiment(object):

    def __init__(self, exp, param_set_name, instance, auctiongroupstr=None):
        """
        Setup the given experiment instance (which will be a subclass
        of Experiment), with the given param_set so it will run
        just the given instance
        exp -- the experiment subclass
        param_set_name -- the name of a parameter set of this experiment
        instance -- what instance number to run
        auctiongroupstr -- string describing what auction group to use
        """
        exp._param_set_name = param_set_name
        if not exp._param_set_name in exp._param_sets():
            raise ValueError("Unexpected parameter set", exp._param_set_name)
        exp._params = exp._param_sets()[exp._param_set_name]
        exp.run_only_instance = instance
        exp.run_only_auctiongroupstr = auctiongroupstr
        self.exp = exp
        exp._check_parameters(exp._params)

    @classmethod
    def parse(cls):
        """ Parse the command line arguments """
        parser = argparse.ArgumentParser(description='Debug an experiment')
        parser.add_argument('--list_experiments',
                            action='store_true',
                            help='list what experiments are available')
        parser.add_argument('--list_param_sets',
                            action='store_true',
                            help='list what param sets are available')
        parser.add_argument('--list_auctiongroups',
                            action='store_true',
                            help='list auction groups for experiment/param_set')
        parser.add_argument('--not_parallel',
                            dest='parallel', action='store_false',
                            help='run instances serial instead of parallel')
        parser.add_argument('--auctiongroupstr',
                            default=None,
                            help='Which auction group to run, default to all')
        parser.add_argument('--instance', type=int,
                            default=1,
                            help='Instance to run')
        parser.add_argument('experiment_name', nargs='?',
                            choices=['LCA', 'Basic', 'Subgradient', 'BidScale', 'CASupplement', 'Cutting', 'Strategy'],
                            default='Basic',
                            help='Experiment to run, default to "Basic"')
        parser.add_argument('param_set_name', nargs='?',
                            default=None,
                            help='Param set to use, default provided')

        args = parser.parse_args()

        # List possible experiments
        if args.list_experiments:
            print 'Available experiments:'
            for k in sorted([cls.__name__ for cls in
                             all_subclasses(AuctionExperiment)]):
                print k
            sys.exit(0)

        # Create the Experiment
        exp_class_name = args.experiment_name + 'Experiment'
        exp_class = globals()[exp_class_name]
        exp = exp_class()
        exp.parallel = args.parallel
        if args.param_set_name is None:
            param_set_name = exp._default_param_set_name()
        else:
            param_set_name = args.param_set_name

        # List possible param sets:
        if args.list_param_sets:
            print('Available parameter sets for experiment \'%s\':' %
                  args.experiment_name)
            for k in sorted(exp._param_sets().keys()):
                print k
            sys.exit(0)

        de = DebugExperiment(exp, param_set_name, args.instance)

        # List possible auctions:
        if args.list_auctiongroups:
            print('Available auction groups for experiment ' +
                  '\'%s\' and param set \'%s\':' %
                  (args.experiment_name, param_set_name))
            for k in sorted(exp._get_group_params()):
                print exp._get_group_string(k)
            sys.exit(0)

        if args.auctiongroupstr:
            de = DebugExperiment(exp, param_set_name, args.instance,
                                 args.auctiongroupstr)

        return de

    def run(self, include_round_file = False,
                  include_prices_file = False,
                  debug_wd = False):
        print('Running %s.' % self)
        self.exp.include_round_file = include_round_file
        self.exp.include_prices_file = include_prices_file
        if debug_wd:
            logging.getLogger("WD").setLevel(logging.DEBUG)
        sys.stdout.flush()
        self.exp.run()

    def __str__(self):
        return "Experiment %s with param set %s for group %s instance %d" % \
            (self.exp.shortname, self.exp._param_set_name,
               self.exp.run_only_auctiongroupstr
               if self.exp.run_only_auctiongroupstr else 'ALL',
               self.exp.run_only_instance)

if __name__ == "__main__":
    DebugExperiment.parse().run()
