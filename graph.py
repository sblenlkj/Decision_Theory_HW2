import json
import pandas as pd
import networkx as nx
from pyvis.network import Network

class MyGraph:
    folder_path = "data/"

    def __init__(self, file_name):
        self.set_dct_from_json(file_name)

        self.nodes_df = None
        self.connections_df = None
        
    def set_dct_from_json(self, file_name):
        infile = open(f"{self.folder_path}{file_name}")
        self.dct = json.load(infile)
        
        self.nodes_lst = []
        for nodes_type, types_data in self.dct["nodes"].items():
            for (node_name, times) in types_data:
                self.nodes_lst.append([node_name, times, nodes_type])
        
        self.connections_lst = []
        self.only_connections_lst = []
        for connection_dct in self.dct["connections"]:
            a, b = connection_dct["nodes"]
            self.connections_lst.append([a, b, connection_dct["times"]])
            self.only_connections_lst.append([a, b])

    def set_dfs(self):
        columns_for_nodes_df = ["node", "times", "type"]
        columns_for_connections_df = ["node1", "node2", "times"]

        self.nodes_df = pd.DataFrame(self.nodes_lst, columns=columns_for_nodes_df)
        self.connections_df = pd.DataFrame(self.connections_lst, columns=columns_for_connections_df)
    
    def save_dfs(self):
        self.nodes_df.to_csv(f"{self.folder_path}/nodes_df.csv", index=False)
        self.connections_df.to_csv(f"{self.folder_path}/connections_df.csv", index=False)
    
    def set_graph(self, legend_flag=False, file_to_save=False):
        g = nx.Graph(self.only_connections_lst)
        net = Network()

        nodes = [
            (
                node, 
                {'group': node_type, 'label': node, 'size': 20}
            )
            for (node, times, node_type) in self.nodes_lst
        ]
        
        g.add_nodes_from(nodes)
        if legend_flag:
            g.add_nodes_from(self.create_legend())
        
        net.from_nx(g)
        net.toggle_physics(False)

        self.net, self.g = net, g

        if file_to_save:
            self.save_html_graph(file_to_save)

    def save_html_graph(self, file_name):
        self.net.show(f"{self.folder_path}{file_name}", notebook=False)

    def create_legend(self):
        step, x, y = 50, -300, -250
        legend_nodes = [
            (
                level, 
                {
                    'group': level, 
                    'label': f"{level} level",
                    'size': 30, 
                    'physics': False, 
                    'x': x, 
                    'y': f'{y + (level-1)*step}px',
                    'shape': 'box', 
                    'widthConstraint': 50, 
                    'font': {'size': 20}
                }
            )
            for level in range(1, 3)
        ]
        return legend_nodes

# MyGraph("2024_final.json").set_graph(file_to_save="graph1.html")