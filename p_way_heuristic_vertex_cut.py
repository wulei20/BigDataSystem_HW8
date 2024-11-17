from collections import defaultdict
import mmap
import struct
import time
import os
from utils import load_graph, save_vertex_cut_partitions, save_huge_vertex_cut_partitions, parse_args, get_output_file_name, get_mermaid_file_name, save_detailed_vertex_cut_partitions, draw_mermaid_graph

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

def heuristic_vertex_cut_partition_huge(path, num_partitions):
    start_time = time.time()
    with open(path, "r") as f:
        # Read the file using mmap
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        
        partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "edges": 0})
        vertex_to_master = {}
        vertex_to_machines = defaultdict(set)  # Track which machines each vertex is assigned to
        partition_load = [0] * num_partitions  # Track edge load per partition

        mean_edge_load = len(mmapped_file) / num_partitions / 8
        print("mean_edge_load: ", mean_edge_load)

        edge_num = 0
        while True:
            edge_num += 1
            if edge_num % 100000000 == 0:
                print(f"Processed {edge_num} edges in {time.time() - start_time} seconds")
            data = mmapped_file.read(8)
            if not data:
                break
            src, dst = struct.unpack("ii", data)
            
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
            
            if partition_load[chosen_partition] >= mean_edge_load:
                # If the partition is full, remove it from the candidate list
                for vertex in partitions[chosen_partition]["vertices"]:
                    vertex_to_machines[vertex].remove(chosen_partition)
                    
        for partition in partitions:
            partitions[partition]["edges"] = partition_load[partition]
    return partitions

def main():
    args = parse_args()
    start = time.time()
    input_file = args.input_file
    method = "heuristic_vertex_cut"
    output_file = os.path.join(args.output_dir, get_output_file_name(method, args.input_file, args.num_partitions))
    print(output_file)
    output_file_detailed = os.path.join(args.output_dir, get_output_file_name(method, args.input_file, args.num_partitions, detailed=True))
    mermaid_file = os.path.join(args.output_dir, get_mermaid_file_name(method, args.input_file, args.num_partitions))
    if args.huge_graph:
        partitions = heuristic_vertex_cut_partition_huge(input_file, args.num_partitions)
        print(f"Partitioned in {time.time() - start} seconds")
        save_huge_vertex_cut_partitions(partitions, output_file)
    else:
        edges = load_graph(input_file)
        partitions = heuristic_vertex_cut_partition(edges, args.num_partitions)
        print(f"Partitioned in {time.time() - start} seconds")
        if args.print_detail:
            save_detailed_vertex_cut_partitions(partitions, output_file_detailed)
        elif args.print_both:
            save_vertex_cut_partitions(partitions, output_file)
            save_detailed_vertex_cut_partitions(partitions, output_file_detailed)
        else:
            save_vertex_cut_partitions(partitions, output_file)
        if args.draw_graph:
            draw_mermaid_graph(partitions, mermaid_file)

if __name__ == "__main__":
    main()