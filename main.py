import networkx as nx
from itertools import combinations
import os
from CP import *
from graph_visualization import *
from itertools import combinations_with_replacement
output_dir = os.path.dirname(os.path.abspath(__file__))  # PATH string this file is contained in


# how to merge two graphs:
'''
# Create two graphs
G1 = nx.Graph()
G1.add_edges_from([('a', 'b'), ('b', 'c')])

G2 = nx.Graph()
G2.add_edges_from([('c', 'd'), ('d', 'e')])

# Merge the graphs
G_merged = nx.compose(G1, G2)
'''
# how to merge multiple graphs
'''
# Create multiple graphs
G1 = nx.Graph()
G1.add_edges_from([('a', 'b'), ('b', 'c')])

G2 = nx.Graph()
G2.add_edges_from([('c', 'd'), ('d', 'e')])

G3 = nx.Graph()
G3.add_edges_from([('e', 'f'), ('f', 'g')])

# Merge the graphs
G_merged = nx.compose_all([G1, G2, G3])
'''


def inspect(graph):
    nodes = list(graph.nodes)
    edges = list(graph.edges)

    graph_info = {
        "Nodes": nodes,
        "Edges": edges
    }
    return graph_info


def build(vertices, edges):
    """
    Create a graph using NetworkX from a list of vertices and edges.
    build([u,v,w,...], [(u, v), (w, v), ...])
    """
    graph = nx.Graph()
    graph.add_nodes_from(vertices)
    graph.add_edges_from(edges)
    return graph


def merge(*graphs):
    new_graph = nx.Graph()

    for graph in graphs:
        new_graph.add_nodes_from(graph.nodes())
        new_graph.add_edges_from(graph.edges())
    return new_graph


def path(path_graph):
    graph_nodes = list(path_graph)
    graph = nx.Graph()
    graph.add_nodes_from(graph_nodes)
    for i in range(len(graph_nodes) - 1):
        graph.add_edge(graph_nodes[i], graph_nodes[i + 1])
    return graph


def cycle(cycle_graph):
    graph_nodes = list(cycle_graph)
    graph = nx.Graph()
    graph.add_nodes_from(graph_nodes)
    for i in range(len(graph_nodes)):
        graph.add_edge(graph_nodes[i], graph_nodes[(i + 1) % len(graph_nodes)])
    return graph


def star(hub, neighbors):
    leaves = list(neighbors)
    graph = nx.Graph()
    graph.add_node(hub)
    for node in leaves:
        graph.add_node(node)
        graph.add_edge(hub, node)
    return graph


def complete_k(n):
    graph = nx.Graph()
    graph.add_nodes_from(range(0, n))
    for node in range(0, n):
        for neighbor in range(0, n):
            if node != neighbor:
                graph.add_edge(node, neighbor)
    return graph


def is_isomorphic_to_any(graph, graph_list):
    for g in graph_list:
        if nx.is_isomorphic(graph, g):
            return True
    return False


def trees(n):
    all_trees = []
    nodes = list(range(n + 1))  # A tree with n edges has n+1 nodes

    for edges in combinations(combinations(nodes, 2), n):
        new_graph = nx.Graph()
        new_graph.add_edges_from(edges)
        if nx.is_tree(new_graph) and not is_isomorphic_to_any(new_graph, all_trees):
            all_trees.append(new_graph)
    return all_trees


'''-----------------------------------------------------------------------------------'''

current_graph = nx.Graph()
current_graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (4, 5), (5, 6)])

labeled_current_graph = labeling_1_rotational_lambda(current_graph, 3)
