from collections import defaultdict
import os
import mmap
import time
import struct
from utils import load_graph, save_edge_cut_partitions, parse_args, get_output_file_name, get_mermaid_file_name, save_huge_edge_cut_partitions, save_detailed_edge_cut_partitions, draw_mermaid_graph

def edge_cut_partition(edges, num_partitions):
    partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "replicated_edges": [], "edges": []})
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
            partitions[src_part]["replicated_edges"].append((src, dst))
            partitions[dst_part]["replicated_edges"].append((src, dst))

        # Update vertices info
        partitions[src_part]["vertices"].update([src, dst])
        partitions[dst_part]["vertices"].update([src, dst])

    return partitions

def edge_cut_partition_huge(path, num_partitions):
    time_start = time.time()
    with open(path, "r") as f:
        # Read the file using mmap
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        
        partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "replicated_edges": 0, "edges": 0})
        vertex_to_partition = {}

        unique_vertices = set()
        while True:
            data = mmapped_file.read(8)
            if not data:
                break
            src, dst = struct.unpack("ii", data)
            unique_vertices.add(src)
            unique_vertices.add(dst)

        mmapped_file.seek(0)

        for idx, vertex in enumerate(unique_vertices):
            vertex_to_partition[vertex] = idx % num_partitions
            partitions[vertex_to_partition[vertex]]["master_vertices"].add(vertex)
            
        print(f"Partitioned vertices in {time.time() - time_start} seconds")

        edge_num = 0
        while True:
            edge_num += 1
            if edge_num % 100000000 == 0:
                print(f"Processed {edge_num} edges in {time.time() - time_start} seconds")
            data = mmapped_file.read(8)
            if not data:
                break
            src, dst = struct.unpack("ii", data)
            src_part = vertex_to_partition[src]
            dst_part = vertex_to_partition[dst]

            # Add edges and vertices to appropriate partitions
            if src_part == dst_part:
                partitions[src_part]["edges"] += 1
            else:
                # Replicate edge across partitions
                partitions[src_part]["replicated_edges"] += 1
                partitions[dst_part]["replicated_edges"] += 1

            # Update vertices info
            partitions[src_part]["vertices"].update([src, dst])
            partitions[dst_part]["vertices"].update([src, dst])

    return partitions

def main():
    args = parse_args()
    start = time.time()
    input_file = args.input_file
    method = "edge_cut"
    output_file = os.path.join(args.output_dir, get_output_file_name(method, args.input_file, args.num_partitions))
    output_file_detailed = os.path.join(args.output_dir, get_output_file_name(method, args.input_file, args.num_partitions, detailed=True))
    mermaid_file = os.path.join(args.output_dir, get_mermaid_file_name(method, args.input_file, args.num_partitions))
    if args.huge_graph:
        partitions = edge_cut_partition_huge(input_file, args.num_partitions)
        print(f"Partitioned in {time.time() - start} seconds")
        save_huge_edge_cut_partitions(partitions, output_file)
    else:
        edges = load_graph(input_file)
        partitions = edge_cut_partition(edges, args.num_partitions)
        print(f"Partitioned in {time.time() - start} seconds")
        if args.print_detail:
            save_detailed_edge_cut_partitions(partitions, output_file_detailed)
        elif args.print_both:
            save_edge_cut_partitions(partitions, output_file)
            save_detailed_edge_cut_partitions(partitions, output_file_detailed)
        else:
            save_edge_cut_partitions(partitions, output_file)
        if args.draw_mermaid:
            draw_mermaid_graph(partitions, mermaid_file)

if __name__ == "__main__":
    main()
