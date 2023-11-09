import numpy as np
import networkx as nx
from elements import *
from optimization2 import *
import matplotlib.pyplot as plt
from solver import *
from traffic_gen import *
from matplotlib import pyplot as plt
from itertools import chain
import time
from greedy import *

class FinishTime:
    def __init__(self, G, bandwidth):
        self.G = G
    #     #  1---- 3-----4-----5
    #     #        |     |
    #     #  2-----      ------6
    #     self.G = nx.DiGraph()
    #     self.G.add_nodes_from([1, 2, 3, 4, 5, 6])
    #     self.G.add_edges_from([(1, 3), (3, 1), (1, 2), (2, 1), (2, 4), (4, 2), (2, 3), (3, 2), (3, 4), (4, 3), (4, 5), (5, 4), (4, 6), (6, 4)])
        for e in self.G.edges():
            self.G.edges[e]["bw"] = bandwidth
            self.G.edges[e]["cur_flows"] = set()
            self.G.edges[e]["bottleneck"] = None

    def get_link_inc(self, e):
        used_bw = 0
        unfixed_flows = 0
        for flow in self.G.edges[e]["cur_flows"]:
            if flow.modified:
                used_bw = used_bw + flow.prev_bw
            else:
                unfixed_flows = unfixed_flows + 1
        if unfixed_flows > 0:
            return (self.G.edges[e]["bw"] - used_bw) / unfixed_flows
        else:
            return 0

    def compute_finish_times(self, flows):
        events = list()
        ARRIVAL = "ARRIVAL"
        DEPARTURE = "DEPARTURE"
        # keep all arrival events in a heap and add them gradually
        arrival_events = list()
        for flow in flows:
            arrival_event = Event(ARRIVAL, flow.arrival_time, flow)
            arrival_events.append(arrival_event)
        heapq.heapify(arrival_events)
        arrival_event = heapq.heappop(arrival_events)
        heapq.heappush(events, arrival_event)
        departeds = [set(), set()]
        cur_departed = 0
        while len(events) > 0 or len(arrival_events) > 0:
            # ignore wrong departure events
            if len(events) > 0 and events[0].type == DEPARTURE and events[0].object.finish_time != events[0].value:
                heapq.heappop(events)
                continue

            # ignore the case if two events have the same time
            if len(events) > 0 and events[0].type == DEPARTURE and events[0].object in departeds[0]:
                heapq.heappop(events)
                continue

            # ignore the case if two events have the same time
            if len(events) > 0 and events[0].type == DEPARTURE and events[0].object in departeds[1]:
                heapq.heappop(events)
                continue

            # check if a new arrival can be added
            if len(arrival_events) > 0 and (len(events) == 0 or events[0].value > arrival_events[0].value):
                arrival_event = heapq.heappop(arrival_events)
                heapq.heappush(events, arrival_event)

            event = heapq.heappop(events)

            if event.type == DEPARTURE:
                departeds[cur_departed].add(event.object)
                if len(departeds[cur_departed]) >= 10000:
                    cur_departed = (cur_departed + 1) % 2
                    departeds[cur_departed] = set()
            # print("[{}] {} at {}.".format(event.type, event.object, event.value))

            # remove/add the flow from/to links along its path
            path = event.object.path
            in_bottleneck = set()
            modified_flows = set()
            for idx in range(len(path) - 1):
                cur_e = (path[idx], path[idx + 1])
                in_bottleneck.add(cur_e)
                if event.type == ARRIVAL:
                    self.G.edges[cur_e]["cur_flows"].add(event.object)
                elif event.type == DEPARTURE:
                    self.G.edges[cur_e]["cur_flows"].remove(event.object)


            # sort all affected links based on the possible increase per flow
            bottlenecks = list()
            for e in in_bottleneck:
                if len(self.G.edges[e]["cur_flows"]) > 0:
                    bottleneck = Bottleneck(self.G.edges[e]["bw"] / len(self.G.edges[e]["cur_flows"]), e)
                    self.G.edges[e]["bottleneck"] = bottleneck
                    heapq.heappush(bottlenecks, bottleneck)

            while len(bottlenecks) > 0:
                bottleneck = heapq.heappop(bottlenecks)
                # determine the least flow rates and fix them
                link_inc = self.get_link_inc(bottleneck.object)
                if link_inc > 0:
                    for flow in self.G.edges[bottleneck.object]["cur_flows"]:
                        if not flow.modified:
                            flow.modified = True
                            modified_flows.add(flow)
                            new_finish = flow.calc_finish_time(event.value, link_inc)
                            flow.finish_event = Event(DEPARTURE, new_finish, flow)
                            heapq.heappush(events, flow.finish_event)
                        # add all other links in the  path of flows in the current link
                        path = flow.path
                        for idx in range(len(path) - 1):
                            cur_e = (path[idx], path[idx + 1])
                            link_inc_update = self.get_link_inc(cur_e)
                            if link_inc_update > 0:
                                in_bottleneck.add(cur_e)
                                if cur_e not in in_bottleneck:
                                    bottleneck2 = Bottleneck(link_inc_update, cur_e)
                                    self.G.edges[cur_e]["bottleneck"] = bottleneck2
                                    heapq.heappush(bottlenecks, bottleneck2)
                                else:
                                    self.G.edges[cur_e]["bottleneck"].value = link_inc_update
                heapq.heapify(bottlenecks)
            #heapq.heapify(events)

            for flow in modified_flows:
                flow.modified = False


class FatTreeTopo():
    def __init__(self, G):
        #if (k % 2) != 0:
        #    print('Number of ports in a fattree must be even!')
        #    return
        num_pods = 5
        num_core = 16
        num_agg = 20
        num_agg_per_pod = 4
        num_edge = 20
        num_edge_per_pod = 4
        hosts_per_sw = 16
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
                
                for core_i in range(4):
                    c = cores[core_i + (agg_i * 4)]
                    G.add_edge(a, c)
def translate_bandwidth(b):
	if b == None:
		return None
	if type(b)!=str:
		return None
	if b[-1] == 'G':
		return float(b[:-1])*1e9
	if b[-1] == 'M':
		return float(b[:-1])*1e6
	if b[-1] == 'K':
		return float(b[:-1])*1e3
	return float(b)
    
def mytest():
    #st = time.time()
    load = 0.8
    sim_time = 10
    #epoch_length = avg_inter_arrival
    bandwidth = "1G"
    G = nx.Graph()
    FatTreeTopo(G)
    bw = translate_bandwidth(bandwidth)
    ft = FinishTime(G, bw)
    flows = list()
    avg_inter_arrival, flows = traffic_gen(G, load, sim_time, bandwidth)
    
    epoch_length = 0.1
    print("flows length", len(flows))
    # for key, value in flow_dic.items():
    #     print("key:", key, "value:", value)
    print("Start computing finish times at {}".format(time.time()))
    ft.compute_finish_times(flows)
    print("End computing finish times at {}".format(time.time()))
    #print(len(flows))
    f_sizes = []
    f_durations = []
    #for f in flows:
    #    print("src:", f.src.name, "dst:", f.dst.name, "Arrival:", f.arrival_time, "Finish:", f.finish_time, "Size:", f.size, "Duration:", f.finish_time - f.arrival_time)
    for f in flows:
        f_sizes.append(f.size)
        #print("flow size", f.size)
        f_durations.append((f.finish_time - f.arrival_time))
        #print(f.finish_time - f.arrival_time)
        #print("src:", f.src.name, "dst:", f.dst.name, "Arrival:", f.arrival_time, "Finish:", f.finish_time, "Size:", f.size, "Duration:", f.finish_time - f.arrival_time)

    # x = np.sort(f_sizes)
    # y = 1. * np.arange(len(f_sizes)) / (len(f_sizes) - 1)
    # plt.plot(x, y)
    # plt.xlabel("Flow Size (bytes)")
    # plt.ylabel("Probability")
    # plt.show()

    # d = np.sort(f_durations)
    # dd = 1. * np.arange(len(f_durations)) / (len(f_durations) - 1)
    # plt.plot(d, dd)
    # plt.xlabel("Flow Duration")
    # plt.ylabel("Probability")
    # plt.show()
    failures = []
    t = 0
    end_time = sim_time + t
    count = 0
    lens = []
    all_epochs_flucs = []
    tmp_dic = {}
    counter = 1
    aggflows = {tuple([]): []}

    while(t <= end_time):
        flow_dic = {}
        diff = {}
        print("epoooooooch")
        count = count + 1  
        for f in flows:
            
            #for p in f.path:
            #    print(p.name)
            fp = tuple(f.path[1:-1])
            if fp in flow_dic:
                tmp = flow_dic.get(fp)
            else:
                tmp = 0
            if f.arrival_time >= t and f.arrival_time <= t + epoch_length and f.finish_time <= t + epoch_length:
                flow_dic[fp] = tmp + f.size
                #print("1", "arrival:", f.arrival_time, "finish:", f.finish_time, "size:", f.size)
                #print("flow dic", flow_dic[fp])
            if f.arrival_time >= t and f.arrival_time <= t + epoch_length and f.finish_time >= t + epoch_length:
                #print("2", "arrival:", f.arrival_time, "finish:", f.finish_time, "size:", f.size, f.size*(((t + epoch_length) - f.arrival_time)/(f.finish_time - f.arrival_time)))
                flow_dic[fp] = tmp + f.size*(((t + epoch_length) - f.arrival_time)/(f.finish_time - f.arrival_time))
            if f.arrival_time <= t and f.finish_time >= t and f.finish_time <= t + epoch_length:
                #print("3", "arrival:", f.arrival_time, "finish:", f.finish_time, "size:", f.size, f.size * ((f.finish_time - t)/(f.finish_time - f.arrival_time)))
                flow_dic[fp] = tmp + f.size * ((f.finish_time - t)/(f.finish_time - f.arrival_time))
            if f.arrival_time <= t and f.finish_time >= t + epoch_length:
                #print("4", "arrival:", f.arrival_time, "finish:", f.finish_time, "size:", f.size)
                flow_dic[fp] = tmp + epoch_length / (f.finish_time - f.arrival_time)
                
        print(count)
        for key, value in flow_dic.items():
            #print("flow_dic", key, value)
            if key in aggflows.keys():
                aggflows[key].append(value)
            else:
                aggflows[key] = []
                aggflows[key].append(value)
        
        
        
        
        
        #aggsize.append() 
        #for key in flow_dic.keys():
        #    print("flow dic:", flow_dic.get(key, 0), "tmp dic:", tmp_dic.get(key, 0))

        # fluctuation_dict = {}
        # for key in flow_dic:
        #     if key in tmp_dic:
        #         fluctuation_dict[key] = flow_dic[key] - tmp_dic[key]

    
        #if counter == 1:
        #decision_vars, failure = place_sketch(flow_dic)
            #print("number of flows in first epoch", len(flow_dic))
        #else:
            #print("number of flows in next epochs", len(flow_dic))
            #check_feasibility(decision_vars, flow_dic)
            
        #greedy(flow_dic)
        #counter += 1
        #failures.append(failure)
        #
        #break
        #diffs = {key: flow_dic.get(key, 0) - tmp_dic.get(key, 0) for key in set(flow_dic) | set(tmp_dic)}
        #for k, v in diffs.items():
        #    print("diff", v)
        #flucs = list(diffs.values())
        #flucs = [abs(ele) for ele in list(fluctuation_dict.values())]
        #all_epochs_flucs.append(flucs)
        #for key, value in flow_dic.items():
        #    tmp_dic[key] = value

        lens.append(len(flow_dic))


        t = t + epoch_length
    #for l in lens:
    #    print("flow dic length", l)
    #print(aggflows)
    #decision_vars, failure = place_sketch(aggflows)
    average_calc(aggflows, epoch_length)
    #print("flucccccccccc size", len(all_epochs_flucs))
    
    #sample_epoch = [element for sublist in all_epochs_flucs[1:-1] for element in sublist]
    #print("sample epoch len", len(sample_epoch))
    #print("failuresssss:", failures)


    # x = np.sort(sample_epoch)
    # y = 1. * np.arange(len(sample_epoch)) / (len(sample_epoch) - 1)
    # plt.plot(x, y)
    # plt.xlabel("Fluctuations (OD diffs in 4 consequent epochs)")
    # plt.ylabel("Probability")
    # plt.show()






    #print("number of epochs:", count) 
    #plt.bar(range(len(aggflows)), aggflows.values())
    #plt.xlabel("epoch #")
    #plt.ylabel("aggregate flow size of an OD path (bytes)")
    #plt.show()
    #for v in aggflows:
    #    print(v)
    #print(len(aggflows))
    # ods = []
    # abs_err = 1000
    # nhost = 16
    # load = 0.3
    # time = 0.1
    # f_list = traffic_gen(nhost, load, time)
    # t = 2
    # end_time = time + t
    # while(t <= end_time):
    #     for i in range(OD_NUM):
    #         od_path = []
    #         ns = np.random.choice(hosts, size=2, replace=False)
    #         pt = nx.shortest_path(G, ns[0], ns[1])
    #         #print("---------------------------------")
    #         #print("source:", ns[0].name)
    #         #print("destination:", ns[1].name)
    #         for pp in pt:
    #             od_path.append(pp)

        #     od = OD(od_path, 0, 0)
        #     for f in f_list:
        #         if f.t > t and f.t < t + 0.1:
        #             if ns[0].name == "h"+str(f.src) and ns[1].name == "h"+str(f.dst):
        #                 print("a flow with size", f.size, "goes from", ns[0].name, "to", ns[1].name, "in time:", f.t)
        #                 od.flowsize = f.size + od.flowsize
        #     print("Total size of flows between this OD within an epoch:", od.flowsize)
        #     if od.flowsize != 0:
        #         epsilon = abs_err/od.flowsize
        #         width = math.ceil(math.e/epsilon)
        #         delta = 0.05
        #         num_of_regs = math.ceil(math.log(1/delta))
        #         print(num_of_regs)
        #         print("num of regs", num_of_regs)
        #         sketch_size = num_of_regs * width * 4 #each register 32 bits
        #         print("sketch size", sketch_size)
        #         od.sketch_size = sketch_size            
        #    ods.append(od)
        #     for f in f_list:
        #        print(f.t)
        #    place_sketch(od)     
        # t = t + 0.1


    
      
        

if __name__ == "__main__":
    mytest()
