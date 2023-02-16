import numpy as np
import networkx as nx
from elements import *
import matplotlib.pyplot as plt
from opt import *
from traffic_gen import *

class FatTreeTopo():
    def __init__(self, k, G):
        if (k % 2) != 0:
            print('Number of ports in a fattree must be even!')
            return
        num_pods = k
        num_core = k * k // 4
        num_agg = k * k // 2
        num_agg_per_pod = k // 2
        num_edge = k * k // 2
        num_edge_per_pod = k // 2
        hosts_per_sw = k // 2
        num_sws = num_core + num_agg + num_edge
        
        print('Create a fattree topology with {} switches'.format(num_sws)) 

        dpid_counter = 1
        cores = []
        pods = []
        
        for x in range(num_core):
            sw = Switch('core%02d' % x, dpid='%d' %dpid_counter)
            G.add_node(sw)
            cores.append(sw)
            dpid_counter += 1
        for podnum in range(num_pods):
            aggs = []
            edges = []
            for aggnum in range(num_agg_per_pod):
                sw = Switch('p%02da%02d' % (podnum, aggnum), dpid='%d' %dpid_counter)
                G.add_node(sw)
                aggs.append(sw)
                dpid_counter += 1
            for edgenum in range(num_edge_per_pod):
                sw = Switch('p%02de%02d' % (podnum, edgenum), dpid='%d' %dpid_counter)
                G.add_node(sw)
                edges.append(sw)
                dpid_counter += 1
            a_pod = (aggs, edges)
            pods.append(a_pod)
        
        # Add hosts to switches
        pods_cpy = pods[:]
        host_i = 0
        while len(pods_cpy) > 0:
            agg, edge = pods_cpy.pop(0)
            edge_cpy = edge[:]
            while len(edge_cpy) > 0:
                e = edge_cpy.pop(0)
                for i in range(hosts_per_sw):
                    host = Host('h{}'.format(host_i))
                    G.add_node(host)
                    host_i += 1
                    G.add_edge(e, host)

        # Connect pods
        for pod in pods:
            agg, edge = pod
            for e in edge:
                for a in agg:
                    G.add_edge(a, e)

        # Connect core and agg
        for pod in pods:
            agg, edge = pod
            for agg_i in range(num_agg_per_pod):
                a = agg[agg_i]
                for core_i in range(k // 2): # k/2 == num_core/num_agg_per_pod
                    c = cores[core_i + (agg_i * k // 2)]
                    G.add_edge(a, c)

def mytest():
    OD_NUM = 10
    hosts = []
    G = nx.Graph()
    FatTreeTopo(4,G)
    for node in G.nodes():
        if "h" in node.name:
            hosts.append(node)
            
    ods = []
    abs_err = 1000
    nhost = 16
    load = 0.3
    time = 0.1
    f_list = traffic_gen(nhost, load, time)
    t = 2
    end_time = time + t
    while(t <= end_time):
        for i in range(OD_NUM):
            od_path = []
            ns = np.random.choice(hosts, size=2, replace=False)
            pt = nx.shortest_path(G, ns[0], ns[1])
            for pp in pt:
                od_path.append(pp)

            od = OD(od_path, 0, 0)
            for f in f_list:
                if f.t > t and f.t < t + 0.1:
                    if ns[0].name == "h"+str(f.src) and ns[1].name == "h"+str(f.dst):
                        #print("flow size", f.size)
                        od.flowsize = f.size + od.flowsize

            if od.flowsize != 0:
                epsilon = abs_err/od.flowsize
                width = math.ceil(math.e/epsilon)
                delta = 0.05
                num_of_regs = math.ceil(math.log(1/delta))
                #print("num of regs", num_of_regs)
                sketch_size = num_of_regs * width * 4 #each register 32 bits
                #print("sketch size", sketch_size)
                od.sketch_size = sketch_size            
            ods.append(od)
            #for f in f_list:
            #    print(f.t)
            place_sketch(od)     
        t = t + 0.1


    

    for d in ods:
        print("od sketch size", d.sketch_size)
      
        

if __name__ == "__main__":
    mytest()
