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
            a = a - s.Q
        return a        
    
    def place_sketch(self, od):
        self.sketches[od] = od.Q


class Host:
    def __init__(self, name):
        self.name = name
        self.M = Const.H_MEM
        self.sketches = dict()


class Sketch:
    def __init__(self, epsilon, delta):
        C = math.log(1/delta)
        R = math.log(math.e/epsilon)
        self.Q = C * R

class OdSketch:
    def __init__(self, od_path, sketch):
        self.od_path = od_path
        self.sketch = sketch
        self.Q = self.sketch.Q

        