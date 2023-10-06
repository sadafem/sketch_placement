import gurobipy as gp
from gurobipy import GRB
import numpy as np
import math
from scipy.stats import norm

def check_feasibility(decision_vars):
    for v in decision_vars:
        print(v.key(),v.value())

    m = gp.Model("fixed_variable_model")

    x_fixed = m.addVar(vtype=gp.GRB.BINARY, lb=decision_vars, ub=decision_vars, name="x_fixed")


    m.optimize()
