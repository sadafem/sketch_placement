import sys
import random
import math
from optparse import OptionParser
from custom_rand import CustomRand
import heapq
import numpy as np
import networkx as nx

class Event:
    def __init__(self, e_type, e_value, e_object):
        self.type = e_type
        self.value = e_value
        self.object = e_object

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

class Bottleneck:
    def __init__(self, b_value, b_object):
        self.value = b_value
        self.object = b_object

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value


class Flow:
	def __init__(self, id, src, dst, size, f_arrival):
		self.id, self.src, self.dst, self.size, self.arrival_time = id, src, dst, size, f_arrival
		self.finish_time = 0
		self.remained_size = size
		self.prev_start = f_arrival
		self.prev_bw = 0
		self.finish_event = None
		self.path = None
		self.modified = False
		
	def __str__(self):
		return "({}: {}->{})".format(self.id, self.src, self.dst)

	def __repr__(self):
		return self.__str__()	

	def calc_finish_time(self, cur_t, cur_bw):
		if cur_bw == self.prev_bw:
			return self.finish_time
		latest_tr = (cur_t - self.prev_start) * self.prev_bw
		self.remained_size = self.remained_size - latest_tr
		self.finish_time = cur_t + (self.remained_size / cur_bw)
        #print("\t[CALC] {} been sending from {} to {} with {}. Sent {}. With {} will finish {} at {}."
        #      .format(self, self.prev_start, cur_t, self.prev_bw, latest_tr, cur_bw, self.remained_size, expected_finish))
		self.prev_start = cur_t
		self.prev_bw = cur_bw
		return self.finish_time

		#return("%d %d %d %.9f"%(self.src, self.dst, self.size, self.t))

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

def poisson(lam):
	return -math.log(1-random.random())*lam




def traffic_gen(G, load, time, bw):
	port = 80
	parser = OptionParser()
	parser.add_option("-c", "--cdf", dest = "cdf_file", help = "the file of the traffic size cdf", default = "WebSearch_distribution.txt")
	#parser.add_option("-n", "--nhost", dest = "nhost", help = "number of hosts")
	#parser.add_option("-l", "--load", dest = "load", help = "the percentage of the traffic load to the network capacity, by default 0.3", default = "0.3")
	#parser.add_option("-b", "--bandwidth", dest = "bandwidth", help = "the bandwidth of host link (G/M/K), by default 10Gb", default = "10G")
	#parser.add_option("-t", "--time", dest = "time", help = "the total run time (s), by default 10", default = "10")
	options,args = parser.parse_args()

	base_t = 0000000000

	#if not options.nhost:
	#	print("please use -n to enter number of hosts")
	#	sys.exit(0)
	#nhost = int(options.nhost)
	#load = float(options.load)
	bandwidth = translate_bandwidth(bw)
	print("bw", bandwidth)
	#print(time)
	time = float(time)*1e9 # translates to ns
	if bandwidth == None:
		print("bandwidth format incorrect")
		sys.exit(0)

	fileName = options.cdf_file
	file = open(fileName,"r")
	lines = file.readlines()
	# read the cdf, save in cdf as [[x_i, cdf_i] ...]
	cdf = []
	for line in lines:
		x,y = map(float, line.strip().split(' '))
		cdf.append([x,y])

	# create a custom random generator, which takes a cdf, and generate number according to the cdf
	customRand = CustomRand()
	if not customRand.setCdf(cdf):
		print("Error: Not valid cdf")
		sys.exit(0)

	avg = customRand.getAvg()
	avg_inter_arrival = 1/(bandwidth*load/8./avg)*1000000000 #nanosecond
	#BandwidthLoad/8Avg: This portion of the formula appears to represent the rate at which data is being transmitted. 
	#Bandwidth is the available data transmission rate, Load is the percentage of that bandwidth being used, and Avg represents the average size of data packets.
	print("avg_inter_arrival", avg_inter_arrival)
	flow_id = 1
	flows = []
	hosts = []
	edges = []
	for node in G.nodes():
		#print(node.name)
		if "h" in node.name:
			hosts.append(node)
		if "e" in node.name and "core" not in node.name:
			edges.append(node)
			#print(node.name)
	nhost = 320
	all_sps = dict()
	for i in range(nhost):

		t = base_t
		while True:
			inter_t = int(poisson(avg_inter_arrival))
			t += inter_t
			dst = random.randint(0, nhost-1)
			while (hosts[dst] == hosts[i]):
				dst = random.randint(0, nhost-1)
			if (t > time + base_t):
				break
			size = int(customRand.rand())
			#mu, sigma, actual_size = fluc_func(size)
			if size <= 0:
				size = 1
			#print("size", size)
			#print("arrival", t * 1e-9)
			flow = Flow(flow_id, hosts[i], hosts[dst], size, t * 1e-9)
			# print(hosts[i].name, hosts[dst].name, size)
			if (flow.src, flow.dst) not in all_sps:
				all_sps[(flow.src, flow.dst)] = list(nx.all_shortest_paths(G, source=flow.src, target=flow.dst))
			flow.path = all_sps[(flow.src, flow.dst)][np.random.randint(0, len(all_sps[(flow.src, flow.dst)]))]
			#flow.path = paths[0]
			#print(flow.path)

			flow_id = flow_id + 1
			flows.append(flow)

	#flows.sort(key = lambda x: x.arrival_time)
	all_sps = None
	return avg_inter_arrival, flows
	#for i in range(nhost):
	#	t = base_t
	#	while True:
	#		inter_t = int(poisson(avg_inter_arrival))
	#		t += inter_t
	#		dst = random.randint(0, nhost-1)
	#		while (dst == i):
	#			dst = random.randint(0, nhost-1)
	#		if (t > time + base_t):
	#			break
	#		size = int(customRand.rand())
	#		if size <= 0:
	#			size = 1
	#		flows = []
	#		f_list.append(Flow(i, dst, size, t * 1e-9))
			#abs_err = 1000
			#epsilon = abs_err/size
			#width = math.ceil(math.e/epsilon)
			#num_of_regs = 3
			#print("epsilon", epsilon)
			#print("sketch width", width)
			#print("sketch size", width*num_of_regs)

	#f_list.sort(key = lambda x: x.t)

	#print(len(f_list))
	#for f in f_list:
		#print(f)
	#return f_list
