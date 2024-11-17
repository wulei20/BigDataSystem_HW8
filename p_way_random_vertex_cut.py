import mmap
import time
import struct
import os
from collections import defaultdict

from utils import load_graph, save_vertex_cut_partitions, parse_args, get_output_file_name, get_mermaid_file_name, save_huge_vertex_cut_partitions, save_detailed_vertex_cut_partitions, draw_mermaid_graph

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

def vertex_cut_partition_huge(path, num_partitions):
    start_time = time.time()
    with open(path, "r") as f:
        # Read the file using mmap
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        
        partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "edges": 0})
        vertex_to_master = {}
        partition_id = 0

        edge_num = 0
        while True:
            edge_num += 1
            if edge_num % 100000000 == 0:
                print(f"Processed {edge_num} edges in {time.time() - start_time} seconds")
            data = mmapped_file.read(8)
            if not data:
                break
            src, dst = struct.unpack("ii", data)

            # Round-robin assignment to partitions
            partitions[partition_id]["edges"] += 1

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

def main():
    args = parse_args()
    start = time.time()
    input_file = args.input_file
    method = "random_vertex_cut"
    output_file = os.path.join(args.output_dir, get_output_file_name(method, args.input_file, args.num_partitions))
    output_file_detailed = os.path.join(args.output_dir, get_output_file_name(method, args.input_file, args.num_partitions, detailed=True))
    mermaid_file = os.path.join(args.output_dir, get_mermaid_file_name(method, args.input_file, args.num_partitions))
    if args.huge_graph:
        partitions = vertex_cut_partition_huge(input_file, args.num_partitions)
        print(f"Partitioned in {time.time() - start} seconds")
        save_huge_vertex_cut_partitions(partitions, output_file)
    else:
        edges = load_graph(input_file)
        partitions = vertex_cut_partition(edges, args.num_partitions)
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