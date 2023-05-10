import numpy as np
import math
def greedy(flow_dic):
    abs_err = 1000
    num_of_ods = len(flow_dic)    
    counter = 0
    for od_path, od_size in flow_dic.items():
        epsilon = abs_err/od_size
        width = math.ceil(math.e/epsilon)
        delta = 0.05
        num_of_regs = math.ceil(math.log(1/delta))
        sketch_size = num_of_regs * width * 4 #each register 32 bits
        #print("sketch size:", sketch_size)
        best_d = None
        for d in od_path:
            if d.mem_available() >= sketch_size:
                if best_d is None or d.M - d.mem_available() < best_d.M - best_d.mem_available():
                    best_d = d
        if best_d is not None:
            d.place_sketch(od_path, sketch_size)
            #print("best device:", best_d.name)
        else:
            counter += 1
            #print("cannot place sketch")
    print("counter:", counter)