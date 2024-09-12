""" Runs an experiment based on stepsize """
import copy
from qpkernel.auctions import *
from qpkernel.experiments.experiment import AuctionExperiment

include_round_file = False
include_prices_file = False

class StrategyExperiment(AuctionExperiment):
    """ Experiments on both QuadValue and CATS. 
        Omit AdaptiveSubgradientAuction and QuadraticSubgradientAuction
        because they take a very long time to run.
    """

    def __init__(self):
        super(StrategyExperiment, self).__init__("strategy",
                                  include_round_file = False,
                                  include_prices_file = False)

    def _default_param_set_name(self):
        return 'default'

    def __default_param_set(self, mods = None):
        if mods is None:
            mods = {}
        params = {
                'num_instances' : 100,
                'generator_param_name' : 'qv_g10a5s5c5',
                'auction_class' : [LinearSubgradientAuction,
                                   ###QuadraticSubgradientAuction,
                                   ###AdaptiveSubgradientAuction,
                                   LinearHeuristicAuction,
                                   ##QuadraticHeuristicAuction,
                                   ##AdaptiveHeuristicAuction, # <-- Don't care
                                   #IBundle,
                                   AdaptiveCuttingAuction
                                  ],
                'maxiter' : 1000,#750,
                'maxtime' : 3600, #10800,#3600,
                'scalebyvalue' : True,
                'epsilon' : .05,
                'stepc' : .02,
                'epoch' : 10,
                'personalized' : True,
                'heuristic_pool_num':5}
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
                'stepc_strategy'  :self.__default_param_set(
                          {'stepc':[.01,.02,.04,.08],
                           'bidding_strategy':['default',
                                               'heuristic',
                                               'chain']}),
                'epsilon_stepc_strategy'  :self.__default_param_set(
                          {'epsilon':[.05,.1,.2,.4],
                           'stepc':[.01,.02,.04,.08],
                           'bidding_strategy':['default',
                                               'heuristic']}),
                                               #'chain']}),
                'epsilon_stepc_pool'  :self.__default_param_set(
                          {#'epsilon':[.05,.1,.2,.4,.6,.8,1,1.2,1.4,1.6],
                           #'epsilon':[.05,.1,.4,.8,1.2,1.6],
                           'epsilon':[.05],
                           'stepc':[.01,.02,.04,.08],
                           'heuristic_pool_num':[2,3],
                           'bidding_strategy':['default',
                                               'heuristic']}),
                'epsilon_stepc':self.__default_param_set(
                          {'epsilon':[.025,.05,.1,.2],
                           'stepc':[.01,.02,.04,.08]}),
                'epoch'  :self.__default_param_set(
                          {'epoch':[10,20,30,40,50],
                           'auction_class' : [AdaptiveHeuristicAuction]})}
        # Now add these for each of the generator types
        qv_gens = [#'qv_g10a5s5c5',
                   #'qv_g20a5s10c10',
                   'qv_g30a5s15c15']
        ret.update(self.__select_generator('qv', qv_gens, exps))
        cats_reg_gens = [#'cats_reg_g10b50',
                         #'cats_reg_g20b100',
                         'cats_reg_g30b150']
        ret.update(self.__select_generator('cats_reg', cats_reg_gens, exps))
        cats_path_gens = [#'cats_path_g10b50',
                          #'cats_path_g20b100',
                          'cats_path_g30b150']
        ret.update(self.__select_generator('cats_path', cats_path_gens, exps))
        cats_arbitrary_gens = [#'cats_arbitrary_g10b50',
                               #'cats_arbitrary_g20b100',
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
    StrategyExperiment().parse().run()
