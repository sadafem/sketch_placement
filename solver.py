import gurobipy as gp
from gurobipy import GRB
import numpy as np
import math

#flow_dic contains a dictionary of OD path and flow sizes
def place_sketch(flow_dic):

    #greeeeedy

    abs_err = 1000
    num_of_ods = len(flow_dic)
    # for od_path, od_size in flow_dic.items():
    #     epsilon = abs_err/od_size
    #     width = math.ceil(math.e/epsilon)
    #     delta = 0.05
    #     num_of_regs = math.ceil(math.log(1/delta))
    #     sketch_size = num_of_regs * width * 4 #each register 32 bits
    #     print("sketch size:", sketch_size)
    #     best_d = None
    #     for d in od_path:
    #         if d.mem_available() >= sketch_size:
    #             if best_d is None or d.M - d.mem_available() < best_d.M - best_d.mem_available():
    #                 best_d = d
    #     if best_d is not None:
    #         d.place_sketch(od_path, sketch_size)
    #         print("best device:", best_d.name)
    #     else:
    #         print("cannot place sketch")

    m = gp.Model()

    # Add decision variables
    x_var = {}
    for i in range(num_of_ods):
        for j in range(len(list(flow_dic.keys())[i])):
            x_var[i, j] = m.addVar(vtype=gp.GRB.BINARY, name=f'x_{i}_{j}')

    
    # Set objective function
    m.setObjective(gp.quicksum(x_var[i, j] for i in range(num_of_ods) for j in range(len(list(flow_dic.keys())[i]))), GRB.MAXIMIZE)

    # Add the capacity constraints
    for i in range(num_of_ods):
        epsilon = abs_err/list(flow_dic.values())[i]
        width = math.ceil(math.e/epsilon)
        delta = 0.05
        num_of_regs = math.ceil(math.log(1/delta))
        sketch_size = num_of_regs * width * 4
        m.addConstr(gp.quicksum(x_var[i, j] * sketch_size <= list(flow_dic.keys())[i][j].mem_available()) for j in range(len(list(flow_dic.keys())[i])))
    
    # Add the assignment constraints
    for i in range(num_of_ods):
        m.addConstr(gp.quicksum(x_var[i, j] for j in range(len(list(flow_dic.keys())[i]))) <= 1)


    # Add uncertainty sets


    # Optimize the model
    m.optimize()

    # Print the solution
    print(f"Objective value: {m.objVal}")
    for v in m.getVars():
        print(f"{v.varName} = {v.x}")



    #print(next(iter(flow_dic)))
    #path = next(iter(flow_dic))
    # for sw in path:
    #     print(sw.name)
    # for d in path:
    #     print(d.mem_available()) 
    
    
    #tr = TestResult()
    # best_d = None
    # for d in od.od_path:
    #     if d.mem_available() >= od.sketch_size:
    #         if best_d is None or d.M - d.mem_available() < best_d.M - best_d.mem_available():
    #             best_d = d
    # if best_d is not None:
    #     best_d.place_sketch(od)
        #print("best device:", best_d.name)

            #tr.admit_num = 1
            #tr.mem_usage.append(best_d.M - best_d.mem_avail())
            #tr.max_mem = best_d.M - best_d.mem_avail()

    #return tr



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
    

