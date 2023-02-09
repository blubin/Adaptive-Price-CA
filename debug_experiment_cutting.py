from multiprocessing import freeze_support
from adaptiveCA.experiments.debug_experiment import *
from adaptiveCA.generators import Instance
import sys, os
import logging
from adaptiveCA.agents import MultiMinded

# Make sure logging really goes to a file: 
if __name__ == '__main__' and os.path.isfile("debug.log"):
  os.remove("debug.log")
logging.basicConfig(level=logging.INFO, filename="debug.log", filemode="a",)
sys.stdout = sys.stderr = open("debug.log", "a+", 0)

def runit():
  sys.argv = ["debug_experiment.py",
              "--not_parallel",
              "--instance", "1",
              "--auctiongroupstr",
              "AdaptiveCuttingAuction#epsilon_0.025#gen_qv_g10a5s5c5#stepc_0.0025",
              "Cutting",
              "qv_epsilon_stepc"]
  
  experiment = DebugExperiment.parse().exp
  params = experiment._get_group_params_with_restriction().pop()
  instance = experiment._get_generator_instance(params, 1)
  print instance
  auction = experiment._get_auction(params, 1, instance)
  print auction
  experiment = DebugExperiment.parse()
  print experiment
  experiment.run()
  
if __name__ == '__main__':  
  runit()
