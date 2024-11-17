import struct
import argparse
import time
import mmap
import os

def save_graph(edges, file_path):
    with open(file_path, "wb") as f:
        for src, dst in edges:
            f.write(struct.pack("ii", src, dst))

def load_graph(file_path):
    edges = []
    with open(file_path, "rb") as f:
        while True:
            data = f.read(8)
            if not data:
                break
            src, dst = struct.unpack("ii", data)
            edges.append((src, dst))
    print(f"Loaded {len(edges)} edges from {file_path}")
    return edges

def get_graph_mmap(file_path):
    edges = []
    with open(file_path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        print(f"Loaded {len(mm)} bytes from {file_path}")
        start = time.time()
        while True:
            data = mm.read(8)
            if not data:
                break
            src, dst = struct.unpack("ii", data)
            edges.append((src, dst))
            if len(edges) % 100000000 == 0:
                print(f"Loaded {len(edges)} edges in {time.time() - start} seconds")
        mm.close()
    print(f"Loaded {len(edges)} edges from {file_path}")
    return edges

def get_mean_degree(edges):
    degree = {}
    for src, dst in edges:
        degree[src] = degree.get(src, 0) + 1
        degree[dst] = degree.get(dst, 0) + 1
    return sum(degree.values()) / len(degree)

def save_edge_cut_partitions(partitions, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    with open(output_file, "w") as f:
        for part_id, data in partitions.items():
            num_master = len(data["master_vertices"])
            num_total_vertices = len(data["vertices"])
            num_rep_edges = len(data["replicated_edges"])
            num_edges = len(data["edges"]) + num_rep_edges

            f.write(f"Partition {part_id}\n")
            f.write(f"{num_master}\n")
            f.write(f"{num_total_vertices}\n")
            f.write(f"{num_rep_edges}\n")
            f.write(f"{num_edges}\n")

def save_huge_edge_cut_partitions(partitions, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    with open(output_file, "w") as f:
        for part_id, data in partitions.items():
            num_master = len(data["master_vertices"])
            num_total_vertices = len(data["vertices"])
            num_rep_edges = data["replicated_edges"]
            num_edges = data["edges"] + num_rep_edges

            f.write(f"Partition {part_id}\n")
            f.write(f"{num_master}\n")
            f.write(f"{num_total_vertices}\n")
            f.write(f"{num_rep_edges}\n")
            f.write(f"{num_edges}\n")

def save_detailed_edge_cut_partitions(partitions, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    with open(output_file, "w") as f:
        for part_id, data in partitions.items():
            f.write(f"Partition {part_id}\n")
            f.write("Master Vertices:\n")
            f.write(f"{data['master_vertices']}\n")
            f.write("Vertices:\n")
            f.write(f"{data['vertices']}\n")
            f.write("Replicated Edges:\n")
            f.write(f"{data['replicated_edges']}\n")
            f.write("Edges:\n")
            f.write(f"{data['edges']}\n")

def save_vertex_cut_partitions(partitions, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    with open(output_file, "w") as f:
        for part_id, data in partitions.items():
            num_master = len(data["master_vertices"])
            num_total_vertices = len(data["vertices"])
            num_edges = len(data["edges"])

            f.write(f"Partition {part_id}\n")
            f.write(f"{num_master}\n")
            f.write(f"{num_total_vertices}\n")
            f.write(f"{num_edges}\n")

def save_huge_vertex_cut_partitions(partitions, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    with open(output_file, "w") as f:
        for part_id, data in partitions.items():
            num_master = len(data["master_vertices"])
            num_total_vertices = len(data["vertices"])
            num_edges = data["edges"]

            f.write(f"Partition {part_id}\n")
            f.write(f"{num_master}\n")
            f.write(f"{num_total_vertices}\n")
            f.write(f"{num_edges}\n")

def save_detailed_vertex_cut_partitions(partitions, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    with open(output_file, "w") as f:
        for part_id, data in partitions.items():
            f.write(f"Partition {part_id}\n")
            f.write("Master Vertices:\n")
            f.write(f"{data['master_vertices']}\n")
            f.write("Vertices:\n")
            f.write(f"{data['vertices']}\n")
            f.write("Edges:\n")
            f.write(f"{data['edges']}\n")

def draw_mermaid_graph(partitions, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    with open(output_file, "w") as f:
        f.write("```mermaid\n")
        f.write("graph TD\n")
        for part_id, data in partitions.items():
            f.write(f"subgraph Partition {part_id}\n")
            for mv in data["master_vertices"]:
                f.write(f'{part_id}_{mv}(("{mv}")):::master\n')
            for v in data["vertices"]:
                if v not in data["master_vertices"]:
                    f.write(f'{part_id}_{v}(("{v}")):::normal\n')

            for src, dst in data["edges"]:
                f.write(f"{part_id}_{src} --> {part_id}_{dst}\n")
            for src, dst in data["replicated_edges"]:
                f.write(f"{part_id}_{src} -.-> {part_id}_{dst}\n")

            f.write("classDef master fill:#f9a825,stroke:#333,stroke-width:2px;\n")
            f.write("classDef normal fill:#42a5f5,stroke:#333,stroke-width:2px;\n")

            f.write("end\n")
        f.write("```")

def parse_args():
    parser = argparse.ArgumentParser(description="Graph partitioning utility")
    parser.add_argument("-od", "--output_dir", type=str, help="Output directory", default="output")
    parser.add_argument("-i", "--input_file", type=str, help="Input file", default="small-5.graph")
    parser.add_argument("-n", "--num_partitions", type=int, help="Number of partitions", default=4)
    parser.add_argument("-t", "--degree_threshold", type=int, help="Degree threshold for hybrid partitioning", default=100)
    parser.add_argument("-d", "--print_detail", action="store_true", help="Print detailed output")
    parser.add_argument("-b", "--print_both", action="store_true", help="Print both detailed and non-detailed output")
    parser.add_argument("-m", "--draw_mermaid", action="store_true", help="Draw Mermaid graph")
    parser.add_argument("-hu", "--huge_graph", action="store_true", help="Use mmap for huge graph")
    return parser.parse_args()

def get_output_file_name(method, input_file, num_partitions, detailed=False):
    input_file = input_file.split("/")[-1]
    if not os.path.exists(f"output/{method}_output"):
        os.makedirs(f"output/{method}_output")
    return f"{method}_output/{input_file.split('.')[0]}_{num_partitions}part{'_detailed' if detailed else ''}.txt"

def get_mermaid_file_name(method, input_file, num_partitions):
    input_file = input_file.split("/")[-1]
    if not os.path.exists(f"output/{method}_output"):
        os.makedirs(f"output/{method}_output")
    return f"{method}_output/{input_file.split('.')[0]}_{num_partitions}part_mermaid.md"

if __name__ == "__main__":
    # graph = [(1, 4), (1, 6), 
    #          (2, 1), (2, 5), (2, 6),
    #          (3, 1), (3, 4),
    #          (4, 1),
    #          (5, 1)]
    # save_graph(graph, "test.graph")
    
    # start = time.time()
    # graph = load_graph(f"hw8_data/roadNet-PA.graph")
    # print(get_mean_degree(graph))
    # stop1 = time.time()
    # print(f"Time elapsed: {stop1 - start}")
    # graph = load_graph(f"hw8_data/small-5.graph")
    # print(graph)
    # print(get_mean_degree(graph))
    # stop2 = time.time()
    # print(f"Time elapsed: {stop2 - stop1}")
    # graph = load_graph(f"hw8_data/synthesized-1b.graph")
    # print(get_mean_degree(graph))
    # stop3 = time.time()
    # print(f"Time elapsed: {stop3 - stop2}")
    # graph = load_graph(f"hw8_data/twitter-2010.graph")
    # print(get_mean_degree(graph))
    # stop4 = time.time()
    # print(f"Time elapsed: {stop4 - stop3}")
    start = time.time()
    graph = get_graph_mmap(f"hw8_data/twitter-2010.graph")
    print(get_mean_degree(graph))
    stop = time.time()
    print(f"Time elapsed: {stop - start}")