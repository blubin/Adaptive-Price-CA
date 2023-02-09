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

"""
Module providing functionality to solve Math Programs
defined in pulp, according to a default solver

"""

import pulp
import sys

# The number of CPLEX Threads we should use:
NUM_CPLEX_THREADS = 2

# Figure out the active solver:
# Here we set it as a global variable, which should have a good default

active_solver = pulp.solvers.CPLEX_PY if pulp.solvers.CPLEX_PY().available() \
    else pulp.solvers.PULP_CBC_CMD if pulp.solvers.PULP_CBC_CMD().available()\
    else None


# If we haven't found one, its probably a problem...
if active_solver is None:
    raise Exception("No Solver Available.") #pragma: no cover

def set_active_solver(solverfactory):
    """ Set the solverfactory to something else... """
    global active_solver          #pragma: no cover
    active_solver = solverfactory #pragma: no cover

def is_cplex():
    """ Ask if the active solver is CPLEX """
    return active_solver == pulp.solvers.CPLEX_PY

if is_cplex():
    import cplex

def solve(pulp_problem, ex_if_nonopt = True, mip = True):
    """ Solve the pulp problem according to the default solver
        pulp_problem : a Pulp problem to solve
        ex_if_nonopt : Throw an exception if the result isn't optimal
        Returns : A string indicating the WD Status
    """  
    #print "Solving using ", active_solver
    if is_cplex(): 
        mysolver = active_solver(mip, msg=False) #pragma: no cover
    else:
        mysolver = active_solver() #pragma: no cover
    pulp_problem.solve(solver=mysolver)
    
    if is_cplex():
        # This is a hack to work around a bug in Pulp where it doesn't seem
        # to be properly recording dual variables when running under cplex
        # note: the bug appears to be a missing () in get_problem_type() below
        con_names = [con for con in pulp_problem.constraints]
        if pulp_problem.solverModel.get_problem_type() == cplex.Cplex.problem_type.LP:
            constraintpivalues = \
                dict(zip(con_names, \
                pulp_problem.solverModel.solution.get_dual_values(con_names)))
            #print 'mpsolve.solve pyvalues:', constraintpivalues
            pulp_problem.assignConsPi(constraintpivalues)

    status = pulp.LpStatus[pulp_problem.status]
    #print "Status", pulp_problem.status, "=", status
    if ex_if_nonopt and status != 'Optimal': #pragma: no cover
        raise Exception("MP Solve was non-optimal", pulp_problem) 
    return status

#Apply a monkey patch that will set the threads parameter.  See
#see https://filippo.io/instance-monkey-patching-in-python/
#
# Note that the cpu_mask parameter is not available prior to 12.6,
# so we elect to set to use taskset separately at the PID level
# (see cpurestrict.py)
num_threads_printed=False
def monkey_buildSolverModel(cplex_py, lp):
    #first call the original model:
    old_buildSolverModel(cplex_py, lp)
    #Set the thread count:
    global num_threads_printed
    if not num_threads_printed:
        sys.stderr.write("CPLEX Threads set to "+str(NUM_CPLEX_THREADS)+".\n")
        num_threads_printed=True
    cplex_py.solverModel.parameters.threads.set(NUM_CPLEX_THREADS)
    # Patch so we fix the problem described here:
    # Only want to do this for Cplex 12.5.  But here we do it regardless:
    #https://www.ibm.com/developerworks/community/forums/html/topic?id=e5f5855a-47c4-47e0-96bc-dea8b847a2b4
    cplex_py.solverModel.parameters.preprocessing.repeatpresolve.set(0)


if hasattr(pulp.solvers.CPLEX_PY, 'buildSolverModel'):
    old_buildSolverModel = pulp.solvers.CPLEX_PY.buildSolverModel
    pulp.solvers.CPLEX_PY.buildSolverModel = monkey_buildSolverModel
#else:
#    sys.stderr.write("Warning: Couldn't find CPLEX_PY.buildSolverModel\n")

