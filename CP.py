from z3 import Solver, Int, sat, Distinct, Or
import networkx as nx


def rename_nodes_by_labels(graph):
    """Rename nodes based on their assigned labels."""
    mapping = {node: graph.nodes[node].get("label", node) for node in graph.nodes()}  # Handles missing labels
    return nx.relabel_nodes(graph, mapping)


def construct_k_graph(graph, k):
    """Returns a list of k identical copies of G."""
    return [graph.copy() for _ in range(k)]


def labeling_1_to_k(graph, r):
    """
    Builds a (1-2-...-k)-labeling for k copies of G, with node labels assigned correctly.
    - Each vertex label is unique within its copy.
    - Vertex labels can repeat across different copies.
    - ℓ(u, v) = |label_i[u] - label_i[v]| is in [1, k] for each copy.
    - ℓ^*(u, v) = (label_i[u] + label_i[v]) mod m for each edge.
    - (ℓ, ℓ^*) pairs must be disjoint across copies.
    """
    m = graph.number_of_edges()
    k = r // 2 if r % 2 == 0 else (r - 1) // 2
    if k <= 0:
        print("k <= 0, no labeling possible.")
    elif (r ** 2) % (2 * m) != r % (2 * m):
        return None

    # Create k identical copies of G
    k_copies = construct_k_graph(graph, k)

    s = Solver()

    # Variables: From each copy of G in kG, each node gets a unique label in {0, ..., 2m-3}
    label = {i: {v: Int(f'label_{i}_{v}') for v in graph.nodes()} for i in range(k)}
    # Track all (ell, ell_star) pairs to ensure they are unique across all copies
    all_pairs = []

    for i in range(k):
        # 1. Unique labels within a copy
        s.add(Distinct([label[i][v] for v in graph.nodes()]))

        for v in graph.nodes():
            s.add(label[i][v] >= 0, label[i][v] <= 2 * m + r - 1)

        for (u, v) in graph.edges():
            # ℓ(u, v) = |label_u - label_v|
            diff = Int(f'diff_{i}_{u}_{v}')
            s.add(Or(diff == label[i][u] - label[i][v], diff == label[i][v] - label[i][u]))
            s.add(diff >= 1, diff <= k)

            # ℓ^*(u, v) = (label_u + label_v) mod m
            l_star = (label[i][u] + label[i][v]) % m

            # For disjointness across copies (diff, l_star) is unique
            pair_hash = Int(f'pair_{i}_{u}_{v}')
            s.add(pair_hash == diff * m + l_star)
            all_pairs.append(pair_hash)

    # 4. Enforce (ℓ, ℓ^*)-disjointness: All edge pairs across copies must be different
    s.add(Distinct(all_pairs))

    # 5. Requirement: All possible pairs (ell, ell_star) must exist
    for ell in range(1, k + 1):
        for ell_star in range(m):
            target = ell * m + ell_star
            s.add(Or([p == target for p in all_pairs]))
    '''
    for i in range(k):
        for v in graph.nodes():
            s.add(label[i][v] >= 0, label[i][v] <= 2 * m + r - 1)

        # Ensure unique labels within each copy
        unique_labels = [label[i][v] for v in graph.nodes()]
        s.add(Distinct(*unique_labels))  # Enforces no duplicate labels within the same copy

    edge_list = list(graph.edges())
    length = [{} for _ in range(k)]
    length_star = [{} for _ in range(k)]

    for i in range(k):
        for (u, v) in edge_list:
            len_var = Int(f'len_{i}_{u}_{v}')
            s.add(len_var == Abs(label[i][u] - label[i][v]))
            s.add(And(len_var >= 1, len_var <= k))
            length[i][(u, v)] = len_var

            len_star_var = Int(f'len_star_{i}_{u}_{v}')
            q = Int(f'q_{i}_{u}_{v}')
            s.add(len_star_var >= 0, len_star_var < m)
            s.add(len_star_var == (label[i][u] + label[i][v]) - m * q)
            s.add(q >= 0)
            length_star[i][(u, v)] = len_star_var

    # Enforce (ℓ, ℓ^*)-disjointness across copies
    for i in range(k):
        for j in range(i + 1, k):
            for e1 in edge_list:
                for e2 in edge_list:
                    same_ell = (length[i][e1] == length[j][e2])
                    same_ell_s = (length_star[i][e1] == length_star[j][e2])
                    s.add(Not(And(same_ell, same_ell_s)))

    # checking all pairs exist...
    for ell in range(1, k + 1):
        for ell_star in range(m):
            pair_exists = []
            for i in range(k):
                for (u, v) in edge_list:
                    pair_exists.append(And(length[i][(u, v)] == ell, length_star[i][(u, v)] == ell_star))
            s.add(Or(*pair_exists))
    '''

    # Solve
    print("Solving...")
    if s.check() == sat:
        print("Solver found a solution.")
        model = s.model()
        labeled_copies = []
        for i in range(k):
            graph_i = k_copies[i]
            labels = {v: model[label[i][v]].as_long() for v in graph_i.nodes()}
            nx.set_node_attributes(graph_i, labels, "label")
            labeled_copies.append(graph_i)

            # Print labels for debugging
            print(f"\nGraph {i}:")
            for v in graph_i.nodes(data=True):
                print(f"  Node {v[0]}: Label {v[1]['label']}")

            labeled_copies = [rename_nodes_by_labels(g) for g in labeled_copies]
        return labeled_copies
    print("No solution found.")
    return None
