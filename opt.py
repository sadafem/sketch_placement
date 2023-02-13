#import gurobipy as gp
#from gurobipy import GRB
import numpy as np

def place_sketch(all_nodes, od):
        #tr = TestResult()
        best_d = None
        for d in od.od_path:
            if d.mem_avail() >= od.Q:
                if best_d is None or d.M - d.mem_avail() < best_d.M - best_d.mem_avail():
                    best_d = d
        if best_d is not None:
            best_d.place_sketch(od, od.Q)
 
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
    

