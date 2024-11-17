from collections import defaultdict
import mmap
import struct
import time
import os

from utils import load_graph, save_vertex_cut_partitions, save_huge_vertex_cut_partitions, parse_args, get_output_file_name, get_mermaid_file_name, save_detailed_vertex_cut_partitions, draw_mermaid_graph

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

def hybrid_cut_partition_huge(path, num_partitions, degree_threshold):
    start_time = time.time()
    with open(path, "r") as f:
        # Read the file using mmap
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        
        partitions = defaultdict(lambda: {"master_vertices": set(), "vertices": set(), "edges": 0})
        vertex_degrees = defaultdict(int)
        vertex_to_master = {}
    
        # Count in-degrees of vertices to determine low/high degree status
        while True:
            data = mmapped_file.read(8)
            if not data:
                break
            src, dst = struct.unpack("ii", data)
            vertex_degrees[src] += 1
            vertex_degrees[dst] += 1

        print(f"Loaded {len(vertex_degrees)} vertices in {time.time() - start_time} seconds")
        start_time = time.time()
        mmapped_file.seek(0)

        edge_num = 0
        while True:
            edge_num += 1
            if edge_num % 100000000 == 0:
                print(f"Processed {edge_num} edges in {time.time() - start_time} seconds")
            data = mmapped_file.read(8)
            if not data:
                break
            src, dst = struct.unpack("ii", data)

            # Determine if destination vertex is high-degree
            is_high_degree = vertex_degrees[dst] > degree_threshold

            if is_high_degree:
                # High-degree vertex: assign edge based on the source vertex
                chosen_partition = (src - 1) % num_partitions
            else:
                # Low-degree vertex: assign edge based on the destination vertex
                chosen_partition = (dst - 1) % num_partitions

            # Assign the edge and track vertices in the chosen partition
            partitions[chosen_partition]["edges"] += 1
            partitions[chosen_partition]["vertices"].update([src, dst])
            
            # Assign master vertices if not already assigned
            if src not in vertex_to_master:
                vertex_to_master[src] = chosen_partition
                partitions[chosen_partition]["master_vertices"].add(src)

            if dst not in vertex_to_master:
                vertex_to_master[dst] = chosen_partition
                partitions[chosen_partition]["master_vertices"].add(dst)

    return partitions

def main():
    args = parse_args()
    start = time.time()
    input_file = args.input_file
    method = "hybrid_vertex_cut"
    output_file = os.path.join(args.output_dir, get_output_file_name(method, args.input_file, args.num_partitions, detailed=False, threshold=args.degree_threshold))
    print("Output file:", output_file)
    output_file_detailed = os.path.join(args.output_dir, get_output_file_name(method, args.input_file, args.num_partitions, detailed=True, threshold=args.degree_threshold))
    mermaid_file = os.path.join(args.output_dir, get_mermaid_file_name(method, args.input_file, args.num_partitions))
    if args.huge_graph:
        partitions = hybrid_cut_partition_huge(input_file, args.num_partitions, args.degree_threshold)
        print(f"Partitioned in {time.time() - start} seconds")
        save_huge_vertex_cut_partitions(partitions, output_file)
    else:
        edges = load_graph(input_file)
        partitions = hybrid_cut_partition(edges, args.num_partitions, args.degree_threshold)
        print(f"Partitioned in {time.time() - start} seconds")
        if args.print_detail:
            save_detailed_vertex_cut_partitions(partitions, output_file_detailed)
        elif args.print_both:
            save_vertex_cut_partitions(partitions, output_file)
            save_detailed_vertex_cut_partitions(partitions, output_file_detailed)
        else:
            save_vertex_cut_partitions(partitions, output_file)
        if args.draw_mermaid:
            draw_mermaid_graph(partitions, mermaid_file)

if __name__ == "__main__":
    main()