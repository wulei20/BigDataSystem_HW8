from collections import defaultdict

from utils import load_graph, save_vertex_cut_partitions

def heuristic_vertex_cut_partition(edges, num_partitions):
    partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "edges": []})
    vertex_to_machines = defaultdict(set)  # Track which machines each vertex is assigned to
    vertex_to_master = {}
    partition_load = [0] * num_partitions  # Track edge load per partition

    mean_edge_load = len(edges) / num_partitions

    for src, dst in edges:
        machines_u = vertex_to_machines[src]
        machines_v = vertex_to_machines[dst]

        if machines_u and machines_v:
            # Case 1: If A(u) and A(v) intersect, assign to a machine in the intersection
            intersection = machines_u & machines_v
            if intersection:
                chosen_partition = min(intersection, key=lambda x: partition_load[x])
            else:
                # Case 2: No intersection; assign to machine of vertex with more unassigned edges
                chosen_partition = min(machines_u | machines_v,
                                       key=lambda x: partition_load[x])
        elif machines_u or machines_v:
            # Case 3: One vertex is assigned; choose a machine from the assigned vertex
            assigned_machines = machines_u or machines_v
            chosen_partition = min(assigned_machines, key=lambda x: partition_load[x])
        else:
            # Case 4: Neither vertex is assigned; assign to the least loaded machine
            chosen_partition = partition_load.index(min(partition_load))

        # Assign edge to the chosen partition
        partitions[chosen_partition]["edges"].append((src, dst))
        partitions[chosen_partition]["vertices"].update([src, dst])
        partition_load[chosen_partition] += 1  # Update load for chosen partition

        # Update master and machine assignment
        if src not in vertex_to_master:
            partitions[chosen_partition]["master_vertices"].add(src)
            vertex_to_master[src] = chosen_partition
        vertex_to_machines[src].add(chosen_partition)
        
        if dst not in vertex_to_master:
            partitions[chosen_partition]["master_vertices"].add(dst)
            vertex_to_master[dst] = chosen_partition
        vertex_to_machines[dst].add(chosen_partition)
        
        if len(partitions[chosen_partition]["edges"]) >= mean_edge_load:
            # If the partition is full, remove it from the candidate list
            for vertex in partitions[chosen_partition]["vertices"]:
                vertex_to_machines[vertex].remove(chosen_partition)
                
    return partitions

# Example usage
edges = load_graph("test.graph")
partitions = heuristic_vertex_cut_partition(edges, 3)
save_vertex_cut_partitions(partitions, "heuristic_vertex_cut_output.txt")
