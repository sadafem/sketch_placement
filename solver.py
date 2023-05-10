import gurobipy as gp
from gurobipy import GRB
import numpy as np
import math

#flow_dic contains a dictionary of OD path and flow sizes
def place_sketch(flow_dic):

    #greeeeedy

    abs_err = 1000
    num_of_ods = len(flow_dic)
    m = gp.Model('Sketch Placement')

    # Add decision variables
    x_var = dict()
    for i in range(num_of_ods):
        #print(list(flow_dic.keys())[i], len(list(flow_dic.keys())[i]))
        for j in range(len(list(flow_dic.keys())[i])):
            x_var[i, j] = m.addVar(vtype=gp.GRB.BINARY, name=f'x_{i}_{j}')

    
    # Set objective function
    m.setObjective(
        gp.quicksum(
            x_var[i, j] 
            for i in range(num_of_ods) 
            for j in range(len(list(flow_dic.keys())[i]))
        ), GRB.MAXIMIZE)

    # Add the assignment constraints
    for i in range(num_of_ods):
        m.addConstr(
            gp.quicksum(
                x_var[i, j] 
                for j in range(len(list(flow_dic.keys())[i]))
            ) <= 1
        )            

    # Add the capacity constraints
    sketch_sizes = dict()
    for i in range(num_of_ods):
        epsilon = abs_err/list(flow_dic.values())[i]
        width = math.ceil(math.e/epsilon)
        delta = 0.05
        num_of_regs = math.ceil(math.log(1/delta))
        sketch_sizes[i] = num_of_regs * width * 4
    m.addConstrs(
        (
            gp.quicksum(
                    x_var[i, j] * sketch_sizes[i] 
                    for j in range(len(list(flow_dic.keys())[i]))
                ) <= list(flow_dic.keys())[i][j].mem_available()
            for i in range(num_of_ods)
            for j in range(len(list(flow_dic.keys())[i]))
        ), "memory_constraint"
    )
    

    # Add the robustness constraints




    # Optimize the model
    m.optimize()

    #print("greedy:", counter)
    print("number of ods:", num_of_ods)
    # Print the solution
    print(f"Objective value: {m.objVal}")
    print("opti", num_of_ods - m.objVal)
    #for v in m.getVars():
    #    print(f"{v.varName} = {v.x}")







'''
    num_of_ods = len(ods)
    num_of_nodes = len(all_nodes)
    w_id = dict(zip(all_nodes, range(len(all_nodes))))
    m = gp.Model("Model")
    k_w = dict()
    z_var = dict()

    for k in range(num_of_ods):
        k_w[k] = list()
        for w in ods[k].od_path:
            k_w[k].append(w_id[w])
            z_var[k] = m.addVars(k_w[k], vtype=GRB.BINARY, name="assign")

    m.addConstrs(
        (
            gp.quicksum(
                z_var[k][w_id[w]]
                for w in ods[k].od_path
            ) >= 1
            for k in range(num_of_ods)
        ), name="place_sketches"
    )

    m.addConstrs(
        (
            gp.quicksum(
                z_var[k][w] * ods[fk].Q
                for fk in range(num_of_ods)
                if w in k_w[k]
            ) <= all_nodes[w].M
            for w in range(num_of_nodes)
        ), name="memory_constraint"
    )
'''
    

