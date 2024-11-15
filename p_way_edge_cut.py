import random
from collections import defaultdict

from utils import load_graph, save_edge_cut_partitions

def edge_cut_partition(edges, num_partitions):
    partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "replicated_edges": set(), "edges": []})
    vertex_to_partition = {}

    unique_vertices = set(v for edge in edges for v in edge)
    for idx, vertex in enumerate(unique_vertices):
        vertex_to_partition[vertex] = idx % num_partitions
        partitions[vertex_to_partition[vertex]]["master_vertices"].add(vertex)
        

    for src, dst in edges:
        src_part = vertex_to_partition[src]
        dst_part = vertex_to_partition[dst]

        # Add edges and vertices to appropriate partitions
        if src_part == dst_part:
            partitions[src_part]["edges"].append((src, dst))
        else:
            # Replicate edge across partitions
            partitions[src_part]["replicated_edges"].add((src, dst))
            partitions[dst_part]["replicated_edges"].add((src, dst))

        # Update vertices info
        partitions[src_part]["vertices"].update([src, dst])
        partitions[dst_part]["vertices"].update([src, dst])

    return partitions

# Example usage
edges = load_graph("test.graph") # hw8_data/small-5.graph
partitions = edge_cut_partition(edges, 3)
save_edge_cut_partitions(partitions, "edge_cut_output.txt")
