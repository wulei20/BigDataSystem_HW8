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
            if "replicated_edges" in data:
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

def get_output_file_name(method, input_file, num_partitions, detailed=False, threshold=None):
    input_file = input_file.split("/")[-1]
    if not os.path.exists(f"output/{method}_output"):
        os.makedirs(f"output/{method}_output")
    if threshold:
        return f"{method}_output/{input_file.split('.')[0]}_{num_partitions}part_threshold_{threshold}{'_detailed' if detailed else ''}.txt"
    else:
        return f"{method}_output/{input_file.split('.')[0]}_{num_partitions}part{'_detailed' if detailed else ''}.txt"

def get_mermaid_file_name(method, input_file, num_partitions, threshold=None):
    input_file = input_file.split("/")[-1]
    if not os.path.exists(f"output/{method}_output"):
        os.makedirs(f"output/{method}_output")
    if threshold:
        return f"{method}_output/{input_file.split('.')[0]}_{num_partitions}part_threshold_{threshold}_mermaid.md"
    else:
        return f"{method}_output/{input_file.split('.')[0]}_{num_partitions}part_mermaid.md"

if __name__ == "__main__":
    # graph = [(1, 4), (1, 6), 
    #          (2, 1), (2, 5), (2, 6),
    #          (3, 1), (3, 4),
    #          (4, 1),
    #          (5, 1)]
    # save_graph(graph, "test.graph")

    start = time.time()
    stop = time.time()
    print(f"Time elapsed: {stop - start}")