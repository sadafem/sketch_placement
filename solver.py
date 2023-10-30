import gurobipy as gp
from gurobipy import GRB
import numpy as np
import math
from scipy.stats import norm
import json

HASH_CAPACITY = 17857140000
#we construct rate fluctuation here	
# def fluc_func(size):
# 	mu = size # mean
# 	sigma = 0.9 * mu #0.3 mean / 0.6 mean / 0.9 mean # standard deviation
# 	#actual_size = mean + variance
# 	actual_size = np.random.normal(mu, sigma)
# 	return mu, sigma, actual_size

def average_calc(aggflows):
    averages = []
    variances = []
    count = 0
    for key, value in aggflows.items():
        print(value)
        if len(value) > 0 and not np.isnan(np.sum(value)):
            value_np = np.array(value)
            print("length of bobo", len(value_np))
            averages.append(np.mean(value_np))
            variances.append(np.std(value_np))
            #place_sketch(aggflows, averages[key], variances[key])

        #print("Variance:", variances[key])
    print("aggflow size", len(aggflows))    
    print("length of averages", len(averages))
    print("length of variances", averages)
    #print("Averages:", averages)
    #print("Variances:", variances) 
    print("hiiii")
    #aggflows.popitem()
    #aggflows.popitem()
    #min_length = min(len(lst) for lst in aggflows.values())
    min_length = min(len(lst) for lst in (lst[1:] for lst in aggflows.values() if len(lst) > 1))
    max_length = max(len(lst) for lst in (lst[1:] for lst in aggflows.values() if len(lst) > 1))
    print(min_length)
    print(max_length)

    for i in range(min_length):
        actual_sizes = [lst[i] for lst in aggflows.values() if i < len(lst)]
        print(len(actual_sizes))

        #print("actual sizes", actual_sizes)
    actual_sizess = [lst[0] for lst in aggflows.values() if 0 < len(lst)]
    second_epoch_sizes = [lst[2] for lst in aggflows.values() if 2 < len(lst)]
    place_sketch(aggflows, actual_sizess, second_epoch_sizes, averages, variances)
    #check_feasibility(aggflows, second_epoch_sizes, averages, variances, var)



#flow_dic contains a dictionary( key:OD path  value:flow sizes )
def place_sketch(flow_dic, actual_sizes, actual_sizes2, means, sigmas):
    
    N = 0.7
    #actual_sizes = []
    #means = []
    #sigmas = []
    abs_err = 1000
    num_of_ods = len(flow_dic)
    #mu = mean
    #sigma = variance

    #min_length = min(len(lst) for lst in flow_dic.values())

    # for i in range(min_length):
    #     actual_sizes = [value[i] for value in flow_dic.values()]
    #     print("actual sizes", actual_sizes)


    # for items in flow_dic.values():
    #     for item in items:
    #         actual_size
    #     mu, sigma, actual_size = fluc_func(size)
    #     #actual_sizes.append(actual_size)
    #     means.append(mu)
    #     sigmas.append(sigma)

    devices_set = set()
    for od in flow_dic.keys():
        for device in od:
            devices_set.add(device)
    devices = list(devices_set)
    #for d in devices:
        #print(d.name)

    print("number of devices", len(devices))



    m = gp.Model('Sketch Placement')


    # j -> flow
    # w -> device
    x_var = dict()
    for j in range(num_of_ods):
        for w in range(len(devices)):
            x_var[j, w] = m.addVar(vtype=gp.GRB.BINARY, name=f'x_{j}_{w}')

    # First Constraint: The ones that are not related should be zero
    for j in range(num_of_ods):
        for w in range(len(devices)):
            if devices[w] not in list(flow_dic.keys())[j]:
                m.addConstr(x_var[j, w] == 0)


    # Memory Constraint: For all devices.
    # Sketch_sizes has the memory requirement of each sketch
    sketch_sizes = dict()
    print("num_of_ods", num_of_ods)
    print("actual sizes", len(actual_sizes))
    num_of_ods = num_of_ods - 1
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
    # w = 0
    # for d in devices:
    #     m.addConstr(
    #         gp.quicksum(
    #             x_var[j, w] * 3 * (actual_sizes[j]/5) for j in range(num_of_ods)
    #         ) <= HASH_CAPACITY
    #     )
    #     w += 1

    #Linearized Deterministic Robust Constraint
    cdf_inv = norm.ppf(N)
    w = 0
    for d in devices:
       m.addConstr(
           gp.quicksum(x_var[j, w] * 3 * means[j]/5 for j in range(num_of_ods)) + cdf_inv * gp.quicksum(x_var[j, w] * 3 * sigmas[j]/5 for j in range(num_of_ods)) <= HASH_CAPACITY
       )
       w += 1
    #m.addConstr(sum(rf[i]* alpha * x[i, s] for i in in_path) + cdf_inv * sum(math.sqrt(varf[i])* alpha * x[i, s] for i in in_path)<= B[s])

    # Set objective function
    m.setObjective(
        gp.quicksum(
            x_var[j, w] 
            for j in range(num_of_ods)
            for w in range(len(devices))
        ), GRB.MAXIMIZE)
    
    m.setParam('MIPGap', 0.05)

    # Optimize the model
    m.optimize()
    #print(x_var[1,1])

    #decision_vars = {v.varName: v.X for v in m.getVars()}
    decision_vars = x_var
    #with open('data.json', 'w') as f:
    #    json.dump(decision_vars, f)

    #str_dict = {str(key): value for key, value in flow_dic.items()}
    #with open('flows.json', 'w') as f:
    #    json.dump(str_dict, f)
    #print(xx_var)
    #print("greedy:", counter)
    print("number of ods:", num_of_ods)
    # Print the solution
    print(f"Objective value: {m.objVal}")
    print("Number of palcement failures:", num_of_ods - m.objVal)
    print("Percent of failures:", (num_of_ods - m.objVal)/num_of_ods)
    print("-------------------------------------------------------")
    print(type(x_var))
    m2 = gp.Model("fixed_variable_model")
    xx_var = dict()
    for j in range(num_of_ods):
        for w in range(len(devices)):
            xx_var[j, w] = m2.addVar(vtype=gp.GRB.BINARY, name=f'xx_{j}_{w}', lb=x_var[j,w].X, ub=x_var[j,w].X)

    print("bbbbbbb")         
    #return x_var

#def check_feasibility(flow_dic, actual_sizes, means, sigmas, x_var):
    abs_err = 1000
    num_of_ods = len(flow_dic)
    devices_set = set()
    for od in flow_dic.keys():
        for device in od:
            devices_set.add(device)
    devices = list(devices_set)
    #for d in devices:
        #print(d.name)

    print("number of devices", len(devices))


    m2 = gp.Model("fixed_variable_model")

    xx_var = dict()
    for j in range(num_of_ods):
        for w in range(len(devices)):
            xx_var[j, w] = m2.addVar(vtype=gp.GRB.BINARY, name=f'xx_{j}_{w}', lb=x_var[j,w].x, ub=x_var[j,w].x)

    sketch_sizes = dict()
    print("num_of_ods", num_of_ods)
    print("actual sizes", len(actual_sizes2))
    num_of_ods = num_of_ods - 1
    for i in range(num_of_ods):
        epsilon = abs_err/actual_sizes2[i]
        width = math.ceil(math.e/epsilon)
        delta = 0.05
        num_of_regs = math.ceil(math.log(1/delta))
        sketch_sizes[i] = num_of_regs * width * 4
        print("sketch size", sketch_sizes[i])
    w = 0
    for d in devices:
        m2.addConstr(
            gp.quicksum(
                xx_var[j, w] * sketch_sizes[j] for j in range(num_of_ods)
            ) <= d.mem()
        )
        w+=1

    # Assignment Constraint
    for j in range(num_of_ods):
        m2.addConstr(
            gp.quicksum(
                xx_var[j, w] for w in range(len(devices))
            ) <= 1
        )    

    # Hashing Capacity Constraint
    w = 0
    for d in devices:
        m2.addConstr(
            gp.quicksum(
                xx_var[j, w] * 3 * (actual_sizes2[j]/5) for j in range(num_of_ods)
            ) <= HASH_CAPACITY
        )
        w += 1        
    m2.setObjective(
        gp.quicksum(
            xx_var[j, w] 
            for j in range(num_of_ods)
            for w in range(len(devices))
        ), GRB.MAXIMIZE)
    

    m2.optimize()
    if m2.status == GRB.Status.INFEASIBLE:
        print("The model is infeasible")
    else:
        print("The model is feasible")

    # return decision_vars, (num_of_ods - m.objVal)/num_of_ods
    #for v in m.getVars():
    #    print(f"{v.varName} = {v.x}")    






    # Add decision variables
    # number of sketches = number of ods (because we asign one sketch to monitor each OD)
    # x_var = dict()
    # for i in range(num_of_ods):
    #     #print(list(flow_dic.keys())[i], len(list(flow_dic.keys())[i]))
    #     for j in range(len(list(flow_dic.keys())[i])): #number of devices in each OD
    #         x_var[i, j] = m.addVar(vtype=gp.GRB.BINARY, name=f'x_{i}_{j}')

    

    # # Add the assignment constraints
    # for i in range(num_of_ods):
    #     m.addConstr(
    #         gp.quicksum(
    #             x_var[i, j] 
    #             for j in range(len(list(flow_dic.keys())[i]))
    #         ) <= 1
    #     )            

    

    # flow_dic = {[a,b,c]: 100, [a,c]: 120}
    # x[0,0] -> 0:a
    # x[0,1] -> 1:b
    # x[0,2] -> 2:c
    # x[1,0] -> 0:a
    # x[1,1] -> 1:c
    # 1st constraint
    # NEW:
    
    

    # OLD:
    # m.addConstrs(
    #     (
    #         gp.quicksum(
    #                 x_var[i, j] * sketch_sizes[i]
    #                 for j in range(len(list(flow_dic.keys())[i]))
    #             ) <= list(flow_dic.keys())[i][j].mem()
    #         for i in range(num_of_ods)
    #         for j in range(len(list(flow_dic.keys())[i]))
    #     ), "memory_constraint"
    # )



    # for j in range(len(list(flow_dic.keys())[i])):    
    #     m.addConstrs(
    #         (
    #             gp.quicksum(
    #                     x_var[i, j] * num_of_regs * list(flow_dic.values())[i]/5
    #                     for i in range(num_of_ods)
    #                 ) <= 1785714240    
    #         ), "hash_constraint"
    #     )
    # hash_per_packet = num_of_regs    
    # m.addConstrs(
    #     (
    #         gp.quicksum(
    #                 x_var[i, j] * hash_per_packet * list(flow_dic.values())[i]/1000000000
    #                 for j in range(len(list(flow_dic.keys())[i]))
    #             ) <= 1785714240
    #         for i in range(num_of_ods)
    #         for j in range(len(list(flow_dic.keys())[i]))
    #     ), "hash_constraint"
    # )
    


    # Add the robustness constraints












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
    

