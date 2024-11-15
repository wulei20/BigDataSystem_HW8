import random
from collections import defaultdict

from utils import load_graph, save_vertex_cut_partitions

def vertex_cut_partition(edges, num_partitions):
    partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "edges": []})
    vertex_to_master = {}
    partition_id = 0

    for src, dst in edges:
        # Round-robin assignment to partitions
        partitions[partition_id]["edges"].append((src, dst))

        # Assign master vertices if not already assigned
        if src not in vertex_to_master:
            vertex_to_master[src] = partition_id
            partitions[partition_id]["master_vertices"].add(src)

        if dst not in vertex_to_master:
            vertex_to_master[dst] = partition_id
            partitions[partition_id]["master_vertices"].add(dst)

        # Update master and vertices info
        partitions[partition_id]["vertices"].update([src, dst])

        partition_id = (partition_id + 1) % num_partitions
        
    return partitions


# Example usage
edges = load_graph("test.graph")
partitions = vertex_cut_partition(edges, 3)
save_vertex_cut_partitions(partitions, "random_vertex_cut_output.txt")
