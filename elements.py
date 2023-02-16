from constants import Const
import math

class Switch:
    def __init__(self, name, dpid):
        self.name = name
        self.dpid = dpid
        self.M = Const.SW_MEM
        self.sketches = dict()

    def mem_available(self):
        a = self.M
        for s in self.sketches:
            a = a - s.sketch_size
        return a        
    
    def place_sketch(self, od):
        self.sketches[od] = od.sketch_size


class Host:
    def __init__(self, name):
        self.name = name
        self.M = Const.H_MEM
        self.sketches = dict()
    def mem_available(self):
        a = self.M
        for s in self.sketches:
            a = a - s.sketch_size
        return a        
    
    def place_sketch(self, od):
        self.sketches[od] = od.sketch_size

class Sketch:
    def __init__(self, epsilon, delta):
        C = math.log(1/delta)
        R = math.log(math.e/epsilon)
        self.Q = C * R

class OD:
    def __init__(self, od_path, flowsize, sketch_size):
        self.od_path = od_path
        self.flowsize = flowsize
        self.sketch_size = sketch_size
        #self.Q = self.sketch.Q

        