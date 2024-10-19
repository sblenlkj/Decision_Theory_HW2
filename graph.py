import json
import pandas as pd
import numpy as np

import networkx as nx

from collections import defaultdict, Counter
from itertools import combinations, accumulate

import hashlib

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

    def __init__(self, file_name: str, not_lst: list=None):
        self.dct, self.nodes_lst, self.nodes_weight_dct, self.connections_lst, self.only_connections_lst, self.connection_relation_dct \
            = self.set_dct_from_json(file_name, not_lst=not_lst)
        self.nodes_df, self.connections_df = self.set_dfs()
        
        self.graph = None
        
    def set_dct_from_json(self, file_name: str, not_lst: list=None):
        dct = self.process_json(file_name, not_lst=not_lst)
        
        nodes_lst = []
        nodes_weight_dct = {}
        for nodes_type, types_data in dct["nodes"].items():
            for (node_name, times) in types_data:
                nodes_lst.append([node_name, times, nodes_type])
                nodes_weight_dct[node_name] = times
        
        connections_lst = []
        only_connections_lst = []
        connection_relation_dct = defaultdict(set)
        
        for connection_dct in dct["connections"]:
            a, b = connection_dct["nodes"]

            connection_relation_dct[a].add(b)
            connection_relation_dct[b].add(a)

            connections_lst.append([a, b, connection_dct["times"]])
            only_connections_lst.append([a, b])
        
        return dct, nodes_lst, nodes_weight_dct, connections_lst, only_connections_lst, connection_relation_dct

    def process_json(self, file_name: str, not_lst: list=None) -> None:
        def func(not_lst):
            if not_lst is None:
                return lambda lst: lst
            return lambda lst: [e for e in lst if e not in not_lst]

        f = func(not_lst)
        infile = open(f"{self.folder_path}{file_name}")
        dct = json.load(infile)
        
        nodes_dct = defaultdict(list)
        connections_lst = []
        
        for v in dct["data"].values():
            nodes = []

            d = f([v["tutor"]])
            nodes_dct["tutors"].extend(d)
            nodes.extend(d)

            d = f(v["countries"])
            nodes_dct["countries"].extend(d)
            nodes.extend(d)

            d = f(v["topics"])
            nodes_dct["topics"].extend(d)
            nodes.extend(d)

            connections_lst.extend([Connection(t[0], t[1]) for t in combinations(nodes, 2)])
        
        for k, v in nodes_dct.items():
            nodes_dct[k] = list(map(lambda x: [x[0], x[1]], sorted(Counter(v).items())))
        
        dct["nodes"] = nodes_dct
        dct["connections"] = [{"times": v, "nodes": c.to_list()} for c, v in Counter(connections_lst).items()]

        return dct
    
    def set_dfs(self):
        columns_for_nodes_df = ["node", "times", "type"]
        columns_for_connections_df = ["node1", "node2", "times"]

        nodes_df = pd.DataFrame(self.nodes_lst, columns=columns_for_nodes_df)
        connections_df = pd.DataFrame(self.connections_lst, columns=columns_for_connections_df)

        return nodes_df, connections_df
    
    def save_dfs(self):
        node_df_to_save, connections_df = self.nodes_df.copy(), self.connections_df.copy()

        node_df_to_save["id"] = node_df_to_save["node"]
        node_df_to_save.rename(columns={"node": "label", "type": "category", "times": "weight"}, inplace=True)
        node_df_to_save.to_csv(f"{self.folder_path}/nodes_df.csv", index=False)

        t = ["Undirected"] * connections_df.shape[0]
        connections_df["type"] = np.array(t)
        connections_df.rename(columns={"node1": "source", "node2": "target", "times": "weight"}, inplace=True)
        connections_df.to_csv(f"{self.folder_path}/connections_df.csv", index=False)
    
    def example_df_to_desktop(self):
        nodes = pd.DataFrame([[1, "a"], [2, "b"], [3, "c"], [4, "d"]], columns=["id", "label"])
        nodes.to_csv(f"~/Desktop/nodes_df.csv", index=False)

        t = "Undirected"
        edges = pd.DataFrame([[1, 3, t], [2, 4, t], [1, 2, t]], columns=["source", "target", "type"])
        edges.to_csv(f"~/Desktop/edges_df.csv", index=False)
    
    def DFS(self, node, not_visited_set):
        not_visited_set.remove(node)

        for neighbor in self.connection_relation_dct[node]:
            if neighbor in not_visited_set:
                self.DFS(neighbor, not_visited_set)

    def is_connected(self):
        keys = list(self.connection_relation_dct.keys())
        not_visited_set = set(keys)
        start_node = keys[0]

        self.DFS(start_node, not_visited_set)

        return len(not_visited_set) == 0
    
    def set_graph(self, use_weight_edges: bool=False):
        g = nx.Graph()

        nodes = [
            (
                node, 
                {'group': node_type, 'label': node}
            )
            for (node, _, node_type) in self.nodes_lst
        ]
        
        g.add_nodes_from(nodes)

        if use_weight_edges:
            g.add_weighted_edges_from(self.connections_lst)
        else:
            g.add_edges_from(self.only_connections_lst)

        self.graph = g
    

    def calculate_all_4_metrics(self):
        lst = [
            (nx.degree_centrality, "degr"),
            (nx.eigenvector_centrality, "eigenr"),
            (nx.betweenness_centrality, "betw"),
            (nx.load_centrality, "load")
        ]

        final_df = self.nodes_df
        lst1, lst2 = [], []
        for (f, name) in lst:
            result_column_name, place_column_name = f"{name}_result", f"{name}_p"
            lst1.append(result_column_name)
            lst2.append(place_column_name)

            results = f(self.graph)
            df = pd.DataFrame(results.items(), columns=["node", result_column_name])
            df[result_column_name] = df[result_column_name].apply(lambda x: round(x*100, 1))

            sorted_df = df[result_column_name].value_counts().reset_index().sort_values(by=result_column_name, ascending=False)
            lst = list(accumulate(sorted_df["count"]))
            lst.insert(0, 0)

            sorted_df[place_column_name] = (np.array(lst) + 1)[:-1]
            sorted_df.drop(columns="count", inplace=True)

            df = pd.merge(df, sorted_df, on=result_column_name)
            final_df = pd.merge(final_df, df, on="node")

        lst = ["node", "type"]
        lst.extend(lst1)
        lst.extend(lst2)

        return final_df.loc[:, lst]