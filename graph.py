import json
import hashlib
from collections import defaultdict, Counter
from itertools import combinations

class Connection:
    def __init__(self, a, b):
        self.a, self.b = sorted([a, b])
    
    def __repr__(self) -> str:
        return f"Connection({self.a}, {self.b})"
    
    def __eq__(self, value: object) -> bool:
        return self.a == value.a and self.b == value.b
    
    def __hash__(self) -> int:
        return self.hash_function(self.b + self.a)
    
    def to_list(self) -> list:
        return [self.a, self.b]
    
    def hash_function(self, s):
        return int(hashlib.sha1(s.encode("utf-8")).hexdigest(), 16) % (10 ** 8)


class MyGraph:
    folder_path = "data/"

    def __init__(self, file_name):
        self.file_name = file_name

    def process_final_json(self, to_save=False) -> dict:
        infile = open(f"{self.folder_path}{self.file_name}_united.json")
        dct = json.load(infile)
        
        nodes_dct = defaultdict(list)
        connections_lst = []
        
        
        for v in dct["data"].values():
            nodes = []
            nodes_dct["tutors"].append(v["tutor"])
            nodes.append(v["tutor"])

            nodes_dct["countries"].extend(v["countries"])
            nodes.extend(v["countries"])

            nodes_dct["topics"].extend(v["topics"])
            nodes.extend(v["topics"])

            connections_lst.extend([Connection(t[0], t[1]) for t in combinations(nodes, 2)])
        
        for k, v in nodes_dct.items():
            nodes_dct[k] = list(map(lambda x: {x[0]: x[1]}, sorted(Counter(v).items())))
        
        dct["nodes"] = nodes_dct
        dct["connections"] = [{"times": v, "nodes": c.to_list()} for c, v in Counter(connections_lst).items()]

        if to_save:
            outfile = open(f"{self.folder_path}{self.file_name}_final.json", "w")
            json.dump(dct, outfile, indent=4)
        
        return dct
