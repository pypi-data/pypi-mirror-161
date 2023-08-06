import collections


def get_ordered_edges_by_edge_indices(*, edge_indices):
    # Create a directed graph which contains both directions
    edge_indices_reversed = [
        (edge_end, edge_start) for
        (edge_start, edge_end) in
        edge_indices
    ]
    directed_edges = \
        edge_indices + \
        edge_indices_reversed

    # Map each edge start vertices to all its edges' end vertices
    edge_start_to_ends = collections.defaultdict(list)
    for (edge_start, edge_end) in directed_edges:
        edge_start_to_ends[edge_start].append(edge_end)

    # Start at the first edge and follow that direction around the graph
    ordered_edges = []
    current_edge = directed_edges[0]
    while len(ordered_edges) < len(edge_indices):
        edge_start = current_edge[1]
        edge_end = \
            edge_start_to_ends[edge_start][0] \
            if edge_start_to_ends[edge_start][0] != current_edge[0] \
            else edge_start_to_ends[edge_start][1]

        next_edge = (edge_start, edge_end)
        ordered_edges.append(next_edge)
        current_edge = next_edge

    return ordered_edges
