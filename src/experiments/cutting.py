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

""" Runs an experiment based on stepsize """
import copy
from adaptiveCA.auctions import *
from adaptiveCA.experiments.experiment import AuctionExperiment

class CuttingExperiment(AuctionExperiment):
    """ Experiments on both QuadValue and CATS. 
        Omit AdaptiveSubgradientAuction and QuadraticSubgradientAuction
        because they take a very long time to run.
    """

    def __init__(self):
        super(CuttingExperiment, self).__init__("cutting")

    def _default_param_set_name(self):
        return 'default'

    def _get_all_auction_paramkeys(self):
        return ['epsilon', 'stepc', 'epoch', 'expstrat']

    def __default_param_set(self, mods = None):
        if mods is None:
            mods = {}
        params = {
                'num_instances' : 100,
                'generator_param_name' : 'qv_g10a5s5c5',
                'auction_class' : [AdaptiveCuttingAuction],
                'maxiter' : 1000,#750,
                'maxtime' : 10800,#3600,
                'scalebyvalue' : True,
                'epsilon' : .05,
                'stepc' : .04,
                'epoch' : 10,
                'expstrat' : 'abs',    #min,max,abs
                'personalized' : True} 
        params.update(mods)
        return params

    def _param_sets(self):
        # First just include the basic default:
        ret = {'default' : self.__default_param_set()}
        # Now build up line experiments:
        exps = {'epsilon':self.__default_param_set(
                          {'epsilon':[.025,.05,.1,.2]}),
                'stepc'  :self.__default_param_set(
                          {'stepc':[.01,.02,.04,.08]}),
                'epsilon_stepc':self.__default_param_set(
                          {'epsilon':[.025,.05,.1,.2],       
                           'stepc':[.01,.02,.04,.08,.16]}),
                'epoch'  :self.__default_param_set(
                          {'epoch':[1, 5, 10, 20, 40, 80]})}
        # Now add these for each of the generator types
        qv_gens = ['qv_g10a5s5c5',
                   'qv_g30a5s15c15']
        ret.update(self.__select_generator('qv', qv_gens, exps))
        cats_reg_gens = ['cats_reg_g10b50',
                         'cats_reg_g30b150']
        ret.update(self.__select_generator('cats_reg', cats_reg_gens, exps))
        cats_path_gens = ['cats_path_g10b50',
                          'cats_path_g30b150']
        ret.update(self.__select_generator('cats_path', cats_path_gens, exps))
        cats_arbitrary_gens = ['cats_arbitrary_g10b50',
                               'cats_arbitrary_g30b150']
        ret.update(self.__select_generator('cats_arbitrary', cats_arbitrary_gens, exps))
        return ret

    def __select_generator(self, prefix, generator_param_name, params):
        def modify(params):
            params = copy.copy(params)
            params['generator_param_name'] = generator_param_name
            return params
        return {prefix+"_"+k : modify(params[k]) for k in params}

if __name__ == "__main__":
    CuttingExperiment().parse().run()
