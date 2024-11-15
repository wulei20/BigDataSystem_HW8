from collections import defaultdict

from utils import load_graph, save_vertex_cut_partitions

def hybrid_cut_partition(edges, num_partitions, degree_threshold):
    partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "edges": []})
    vertex_degrees = defaultdict(int)
    vertex_to_master = {}
    
    # Count in-degrees of vertices to determine low/high degree status
    for src, dst in edges:
        vertex_degrees[src] += 1
        vertex_degrees[dst] += 1

    for src, dst in edges:
        # Determine if destination vertex is high-degree
        is_high_degree = vertex_degrees[dst] > degree_threshold

        if is_high_degree:
            # High-degree vertex: assign edge based on the source vertex
            chosen_partition = (src - 1) % num_partitions
        else:
            # Low-degree vertex: assign edge based on the destination vertex
            chosen_partition = (dst - 1) % num_partitions

        # Assign the edge and track vertices in the chosen partition
        partitions[chosen_partition]["edges"].append((src, dst))
        partitions[chosen_partition]["vertices"].update([src, dst])
        
        # Assign master vertices if not already assigned
        if src not in vertex_to_master:
            vertex_to_master[src] = chosen_partition
            partitions[chosen_partition]["master_vertices"].add(src)

        if dst not in vertex_to_master:
            vertex_to_master[dst] = chosen_partition
            partitions[chosen_partition]["master_vertices"].add(dst)

    return partitions

# Example usage
edges = load_graph("test.graph")
degree_threshold = 3  # User-defined threshold for high-degree vertices
num_partitions = 3
partitions = hybrid_cut_partition(edges, num_partitions, degree_threshold)
save_vertex_cut_partitions(partitions, "hybrid_vertex_cut_output.txt")
