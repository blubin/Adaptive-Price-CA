""" Runs an experiment based on stepsize """
import copy
from qpkernel.auctions import *
from qpkernel.experiments.experiment import AuctionExperiment

class XorPricesExperiment(AuctionExperiment):
    """ Experiments on CATS. 
        Track the within round prices
        Run only on the specific auctions and settings
        Chosen as optimal in the main 'basic' experiments.
    """

    def __init__(self):
        super(XorPricesExperiment, self).__init__("xorprices",
                                                  include_round_file = True,
                                                  include_prices_file = False,
                                                  include_xorprices_file =True)

    def _default_param_set_name(self):
        return 'default'

    def __default_param_set(self, mods = None):
        if mods is None:
            mods = {}
        params = {
                'num_instances' : 100,
                'generator_param_name' : 'cats_reg_g30b150',
                'auction_class' : [LinearClockAuction,
                                   LinearSubgradientAuction,
                                   LinearHeuristicAuction,
                                   AdaptiveCuttingAuction,
                                   IBundle,
                                  ],
                'maxiter' : 1000,
                'maxtime' : 10800,
                'scalebyvalue' : True,
                'epsilon' : .05,
                'stepc' : .01,
                'epoch' : 10,
                'personalized' : True}
        params.update(mods)
        return params

    def _param_sets(self):
        # First just include the basic default:
        ret = {'default' : self.__default_param_set()}
        # Now build up line experiments:
        exps = {'stepc':self.__default_param_set(
                {'stepc':[.02,.04,.08,.16]})}
        # Now add these for each of the generator types
        cats_reg_gens = ['cats_reg_g30b150']
        ret.update(self.__select_generator('cats_reg', cats_reg_gens, exps))
        cats_path_gens = ['cats_path_g30b150']
        ret.update(self.__select_generator('cats_path', cats_path_gens, exps))
        cats_arbitrary_gens = ['cats_arbitrary_g30b150']
        ret.update(self.__select_generator('cats_arbitrary', cats_arbitrary_gens, exps))
        return ret

    def __select_generator(self, prefix, generator_param_name, params):
        def modify(params):
            params = copy.copy(params)
            params['generator_param_name'] = generator_param_name
            return params
        return {prefix+"_"+k : modify(params[k]) for k in params}

if __name__ == "__main__":
    XorPricesExperiment().parse().run()
