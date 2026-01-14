import networkx as nx
from itertools import combinations
import os
from CP import *
from graph_visualization import *
from itertools import combinations_with_replacement
output_dir = os.path.dirname(os.path.abspath(__file__))  # PATH string this file is contained in

# * graph creation tools *#

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


# custom functions to build graphs more intuitively
def inspect(G):
    nodes = list(G.nodes)
    edges = list(G.edges)

    Ginfo = {
        "Nodes": nodes,
        "Edges": edges
    }

    return Ginfo


def build(vertices, edges):
    """
    Create a graph using NetworkX from a list of vertices and edges.
    build([u,v,w,...], [(u, v), (w, v), ...])
    """
    G = nx.Graph()
    G.add_nodes_from(vertices)
    G.add_edges_from(edges)
    return G


def merge(*graphs):
    """
    Merge multiple NetworkX graphs into a single graph.
    """
    G = nx.Graph()

    for graph in graphs:
        G.add_nodes_from(graph.nodes())
        G.add_edges_from(graph.edges())

    return G


def path(c):
    C = list(c)
    G = nx.Graph()
    G.add_nodes_from(C)
    for i in range(len(C) - 1):
        G.add_edge(C[i], C[i + 1])
    return G


def cycle(c):
    C = list(c)
    G = nx.Graph()
    G.add_nodes_from(C)
    for i in range(len(C)):
        G.add_edge(C[i], C[(i + 1) % len(C)])
    return G


def star(hub, neighbors):
    leaves = list(neighbors)
    G = nx.Graph()
    G.add_node(hub)
    for node in leaves:
        G.add_node(node)
        G.add_edge(hub, node)
    return G


def K(n):
    G = nx.Graph()
    G.add_nodes_from(range(0, n))
    for node in range(0, n):
        for neighbor in range(0, n):
            if node != neighbor:
                G.add_edge(node, neighbor)
    return G


def trees(n):
    def is_isomorphic_to_any(graph, graph_list):
        for g in graph_list:
            if nx.is_isomorphic(graph, g):
                return True
        return False

    all_trees = []
    nodes = list(range(n + 1))  # A tree with n edges has n+1 nodes

    for edges in combinations(combinations(nodes, 2), n):
        G = nx.Graph()
        G.add_edges_from(edges)
        if nx.is_tree(G) and not is_isomorphic_to_any(G, all_trees):
            all_trees.append(G)

    return all_trees


def cycle5():
    return nx.cycle_graph(5)


def generate_tripartite_C5():
    base = nx.cycle_graph(5)
    graphs = []

    for u, v in combinations_with_replacement(base.nodes(), 2):
        G = base.copy()
        a = max(G.nodes()) + 1
        b = a + 1

        G.add_edge(u, a)
        G.add_edge(v, b)

        if not any(nx.is_isomorphic(G, H) for H in graphs):
            graphs.append(G)

    return graphs


'''-----------------------------------------------------------------------------------'''

# Testing
print(f'Here: {generate_tripartite_C5()}')
c5 = generate_tripartite_C5()

# graph1 = merge(star(0, [1, 2, 3, 4, 5]), path([6, 7, 8]))  # five star \sqcup two path

# graceful_G= graceful(G)
# sigmapm_G1 = sigmapm(graph1)
# Glist7 = labeling_1_to_k(G,7)
# Glist8 = labeling_1_to_k(G,8)
firstC5 = labeling_1_to_k(c5[0], 7)

# visualize(21, [graceful_G],  '123list', output_dir)
visualize(21, firstC5, '123list', output_dir)
# visualize(21, Glist7,  '123inflist',  output_dir)
# visualize(21, Glist8,  '123inflist',  output_dir)
