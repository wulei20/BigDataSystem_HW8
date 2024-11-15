import struct
import argparse

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
    return edges

def save_edge_cut_partitions(partitions, output_file):
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

def save_vertex_cut_partitions(partitions, output_file):
    with open(output_file, "w") as f:
        for part_id, data in partitions.items():
            num_master = len(data["master_vertices"])
            num_total_vertices = len(data["vertices"])
            num_edges = len(data["edges"])

            f.write(f"Partition {part_id}\n")
            f.write(f"{num_master}\n")
            f.write(f"{num_total_vertices}\n")
            f.write(f"{num_edges}\n")

def parse_args():
    parser = argparse.ArgumentParser(description="Graph partitioning utility")
    parser.add_argument("-id", "--input_dir", type=str, help="Input directory", default="hw8_data")
    parser.add_argument("-od", "--output_dir", type=str, help="Output directory", default="output")
    parser.add_argument("-g", "--graph_file", type=str, help="Graph file", default="small-5.graph")
    return parser.parse_args()

if __name__ == "__main__":
    graph = [(1, 4), (1, 6), 
             (2, 1), (2, 5), (2, 6),
             (3, 1), (3, 4),
             (4, 1),
             (5, 1)]
    save_graph(graph, "test.graph")