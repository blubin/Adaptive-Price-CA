import adaptiveCA.mpsolve as mpsolve

from pulp import *

def setup_module(module):
    # Use the example from https://projects.coin-or.org/PuLP/browser/trunk/examples/WhiskasModel2.py?format=txt
    # Creates a list of the Ingredients
    Ingredients = ['CHICKEN', 'BEEF', 'MUTTON', 'RICE', 'WHEAT', 'GEL']
    # A dictionary of the costs of each of the Ingredients is created
    costs = {'CHICKEN': 0.013, 
             'BEEF': 0.008, 
             'MUTTON': 0.010, 
             'RICE': 0.002, 
             'WHEAT': 0.005, 
             'GEL': 0.001}
    # A dictionary of the protein percent in each of the Ingredients is created
    proteinPercent = {'CHICKEN': 0.100, 
                      'BEEF': 0.200, 
                      'MUTTON': 0.150, 
                      'RICE': 0.000, 
                      'WHEAT': 0.040, 
                      'GEL': 0.000}
    # A dictionary of the fat percent in each of the Ingredients is created
    fatPercent = {'CHICKEN': 0.080, 
                  'BEEF': 0.100, 
                  'MUTTON': 0.110, 
                  'RICE': 0.010, 
                  'WHEAT': 0.010, 
                  'GEL': 0.000}
    # A dictionary of the fibre percent in each of the Ingredients is created
    fibrePercent = {'CHICKEN': 0.001, 
                    'BEEF': 0.005, 
                    'MUTTON': 0.003, 
                    'RICE': 0.100, 
                    'WHEAT': 0.150, 
                    'GEL': 0.000}
    # A dictionary of the salt percent in each of the Ingredients is created
    saltPercent = {'CHICKEN': 0.002, 
                   'BEEF': 0.005, 
                   'MUTTON': 0.007, 
                   'RICE': 0.002, 
                   'WHEAT': 0.008, 
                   'GEL': 0.000}
    # Create the 'prob' variable to contain the problem data
    prob = LpProblem("The Whiskas Problem", LpMinimize)
    # A dictionary called 'ingredient_vars' is created to contain the referenced Variables
    ingredient_vars = LpVariable.dicts("Ingr",Ingredients,0)
    # The objective function is added to 'prob' first
    prob += lpSum([costs[i]*ingredient_vars[i] for i in Ingredients]), "Total Cost of Ingredients per can"
    # The five constraints are added to 'prob'
    prob += lpSum([ingredient_vars[i] for i in Ingredients]) == 100, "PercentagesSum"
    prob += lpSum([proteinPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 8.0, "ProteinRequirement"
    prob += lpSum([fatPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 6.0, "FatRequirement"
    prob += lpSum([fibrePercent[i] * ingredient_vars[i] for i in Ingredients]) <= 2.0, "FibreRequirement"
    prob += lpSum([saltPercent[i] * ingredient_vars[i] for i in Ingredients]) <= 0.4, "SaltRequirement"
    module.prob = prob
    module.ingredient_vars = ingredient_vars

class TestMPSolve:

    def test_solve(self):
        mpsolve.solve(prob)
        #print LpStatus[prob.status]
        #for v in prob.variables():
        #    print v.name, "=", v.varValue
        #print "Total Cost of Ingredients per can = ", value(prob.objective)
        assert LpStatus[prob.status] == "Optimal"
        assert value(prob.objective) == 0.52

    def test_integer(self):
        ingredient_vars['CHICKEN'].cat = LpInteger
        mpsolve.solve(prob)
        #print LpStatus[prob.status]
        #for v in prob.variables():
        #    print v.name, "=", v.varValue
        #print "Total Cost of Ingredients per can = ", value(prob.objective)
        assert LpStatus[prob.status] == "Optimal"
        assert value(prob.objective) == 0.52

    def test_dual(self):
        mpsolve.solve(prob, False, False)
        #print LpStatus[prob.status]
        #for v in prob.variables():
        #    print v.name, "=", v.varValue
        #print "Total Cost of Ingredients per can = ", value(prob.objective)

        #import cplex
        #n = [con for con in prob.constraints]
        #print 'Cplex: ' + str(prob.solverModel.solution.get_dual_values(n))

        assert LpStatus[prob.status] == "Optimal"
        assert value(prob.objective) == 0.52
        assert prob.constraints['FatRequirement'].pi == 0.07

    # Don't include this one for now, as it fails on CPLEX.  
    # At some point we might want to code support for this into mpsolve...

    # def test_integer_dual(self):
    #     ingredient_vars['CHICKEN'].cat = LpInteger
    #     mpsolve.solve(prob)
    #     #print LpStatus[prob.status]
    #     #for v in prob.variables():
    #     #    print v.name, "=", v.varValue
    #     #print "Total Cost of Ingredients per can = ", value(prob.objective)
    #     assert LpStatus[prob.status] == "Optimal"
    #     assert value(prob.objective) == 0.52

    #     # Note: this will likely fail for cplex unless we add code to explicitly
    #     # (1) solve the MIP (2) fix all integer values (3) resolve for the lp duals.
    #     assert prob.constraints['FatRequirement'].pi == 0.07

    def test_row_duals(self):
        prob = LpProblem("Simple Alloc Problem", LpMaximize)
        xA10 = LpVariable('xA10',0,None,pulp.LpContinuous)
        xA01 = LpVariable('xA01',0,None,pulp.LpContinuous)
        xA11 = LpVariable('xA11',0,None,pulp.LpContinuous)
        xB10 = LpVariable('xB10',0,None,pulp.LpContinuous)
        xB01 = LpVariable('xB01',0,None,pulp.LpContinuous)
        xB11 = LpVariable('xB11',0,None,pulp.LpContinuous)
        y_00_11 = LpVariable('y_00_11',0,None,pulp.LpContinuous)

        prob += 1*xA10 + 2*xA01 + 3*xA11 + 10*xB10 + 20*xB01 + 30*xB11, "Objective"
        prob += xA10+xA11 + xB10 + xB11 - y_00_11 <= 0, 'Item 1'
        prob += xA01+xA11 + xB01 + xB11 - y_00_11 <= 0, 'Item 2'
        prob += xA10 + xA01 + xA11 <= 1, 'Agent 1'
        prob += xB10 + xB01 + xB11 <= 1, 'Agent 2'
        prob += y_00_11 <= 1, 'Supply'

        mpsolve.solve(prob, False, False)
        #print LpStatus[prob.status]
        #for v in prob.variables():
        #    print v.name, "=", v.varValue
        #print "Objective Value = ", value(prob.objective)
        #for c in prob.constraints:
        #    print c, '=', prob.constraints[c].pi

        assert LpStatus[prob.status] == "Optimal"
        assert value(prob.objective) == 30.0
        assert prob.constraints['Supply'].pi == 30.0

    def test_cols_duals(self):
        prob = LpProblem("Simple Alloc Problem", LpMaximize)
        obj = pulp.LpConstraintVar("Objective")
        prob.setObjective(obj)
        item1 = pulp.LpConstraintVar("Item 1", pulp.LpConstraintLE, 0)
        item2 = pulp.LpConstraintVar("Item 2", pulp.LpConstraintLE, 0)
        agent1 = pulp.LpConstraintVar("Agent 1", pulp.LpConstraintLE, 1)
        agent2 = pulp.LpConstraintVar("Agent 2", pulp.LpConstraintLE, 1)
        supply = pulp.LpConstraintVar("Supply", pulp.LpConstraintLE, 1)
        prob += item1
        prob += item2
        prob += agent1
        prob += agent2
        prob += supply

        xA10 = pulp.LpVariable('xA10', 0, None, pulp.LpContinuous, \
               1*obj+1*item1+0*item2+1*agent1+0*agent2+0*supply)
        xA01 = pulp.LpVariable('xA01', 0, None, pulp.LpContinuous, \
               2*obj+0*item1+1*item2+1*agent1+0*agent2+0*supply)
        xA11 = pulp.LpVariable('xA11', 0, None, pulp.LpContinuous, \
               3*obj+1*item1+1*item2+1*agent1+0*agent2+0*supply)
        xB10 = pulp.LpVariable('xB10', 0, None, pulp.LpContinuous, \
               10*obj+1*item1+0*item2+0*agent1+1*agent2+0*supply)
        xB01 = pulp.LpVariable('xB01', 0, None, pulp.LpContinuous, \
               20*obj+0*item1+1*item2+0*agent1+1*agent2+0*supply)
        xB11 = pulp.LpVariable('xB11', 0, None, pulp.LpContinuous, \
               30*obj+1*item1+1*item2+0*agent1+1*agent2+0*supply)
        y_00_11 = pulp.LpVariable('y_00_11', 0, None, pulp.LpContinuous, \
               0*obj-1*item1-1*item2+0*agent1+0*agent2+1*supply)

        mpsolve.solve(prob, False, False)
        #print LpStatus[prob.status]
        #for v in prob.variables():
        #    print v.name, "=", v.varValue
        #print "Objective Value = ", value(prob.objective)
        #for c in prob.constraints:
        #    print c, '=', prob.constraints[c].pi

        assert LpStatus[prob.status] == "Optimal"
        assert value(prob.objective) == 30.0
        assert prob.constraints['Supply'].pi == 30.0
