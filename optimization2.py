import gurobipy as gp
from gurobipy import GRB
import numpy as np
import math
from scipy.stats import norm
import json

HASH_CAPACITY = 107142840000

# def fluc_func(size):
# 	mu = size # mean
# 	sigma = 0.3*mu #0.3 mean / 0.6 mean / 0.9 mean # standard deviation
# 	#actual_size = mean + variance
# 	actual_size = np.random.normal(mu, sigma)
# 	return mu, sigma, actual_size
    
#decision_vars is a dectionary of decision variables from a solved optimization problem
def check_feasibility(decision_vars, flow_dic):
    # print("hiiiiiiiiiiiiiiiiii")
    # for key, value in decision_vars.items():
    #     print(f"{key}: {value}")
    x_var = decision_vars
    N = 0.1
    actual_sizes = []
    means = []
    sigmas = []
    abs_err = 1000
    num_of_ods = len(flow_dic)
    for size in flow_dic.values():
        mu, sigma, actual_size = fluc_func(size)
        actual_sizes.append(actual_size)
        means.append(mu)
        sigmas.append(sigma)

    #with open('data.json', 'r') as f:
    #    decision_vars = json.load(f)
    num_of_ods = len(flow_dic)
    devices_set = set()
    for od in flow_dic.keys():
        for device in od:
            devices_set.add(device)
    devices = list(devices_set)

    m = gp.Model("fixed_variable_model")

    #x_var = dict()
    #for j in range(num_of_ods):
    #    for w in range(len(devices)):
    #        x_var[j, w] = m.addVar(vtype=gp.GRB.BINARY, lb=decision_vars, ub=decision_vars, name=f'x_{j}_{w}')

    #x_var = {}
    # for key in decision_vars:
    #     key = m.addVar(vtype=GRB.BINARY, name=f"{key}", start=decision_vars[key])

    # x_var = dict()
    # for j in range(num_of_ods):
    #    for w in range(len(devices)):
    #        x_var[j, w] = m.addVar(vtype=gp.GRB.BINARY, name=f'x_{j}_{w}')

    #x_fixed = m.addVar(vtype=gp.GRB.BINARY, lb=decision_vars, ub=decision_vars, name="x_fixed")


    # Memory Constraint: For all devices.
    # Sketch_sizes has the memory requirement of each sketch
    sketch_sizes = dict()
    for i in range(num_of_ods):
        epsilon = abs_err/actual_sizes[i]
        width = math.ceil(math.e/epsilon)
        delta = 0.05
        num_of_regs = math.ceil(math.log(1/delta))
        sketch_sizes[i] = num_of_regs * width * 4
        #print("sketch size", sketch_sizes[i])

    w = 0
    for d in devices:
        m.addConstr(
            gp.quicksum(
                x_var[j, w] * sketch_sizes[j] for j in range(num_of_ods)
            ) <= d.mem()
        )
        w+=1

    # Assignment Constraint
    for j in range(num_of_ods):
        m.addConstr(
            gp.quicksum(
                x_var[j, w] for w in range(len(devices))
            ) <= 1
        )
    # Hashing Capacity Constraint
    w = 0
    for d in devices:
        m.addConstr(
            gp.quicksum(
                x_var[j, w] * 3 * (actual_sizes[j]/5) for j in range(num_of_ods)
            ) <= HASH_CAPACITY
        )
        w += 1        
    m.setObjective(
        gp.quicksum(
            x_var[j, w] 
            for j in range(num_of_ods)
            for w in range(len(devices))
        ), GRB.MAXIMIZE)
    

    m.optimize()

    if m.status == GRB.Status.INFEASIBLE:
        print("The model is infeasible")
    else:
        print("The model is feasible")
        #for i in I:
        #    print(f"x_{i} = {x[i].X}")


    #m.optimize()
