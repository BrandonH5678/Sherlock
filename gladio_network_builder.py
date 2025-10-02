#!/usr/bin/env python3
"""
Operation Gladio Network Graph Builder
Build network visualization from relationships

Design: Graph construction with centrality metrics
Memory: <200MB
Output: DOT format + auto-generated PNG/SVG/PDF (if GraphViz available)
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict, Counter
from datetime import datetime


class NetworkGraphBuilder:
    """Build network graph from relationships"""

    def __init__(self, relationships_path: Path, entities_path: Path):
        self.relationships_path = Path(relationships_path)
        self.entities_path = Path(entities_path)

        # Load data
        self.relationships = self.load_relationships()
        self.entities = self.load_entities()

        # Network structures
        self.nodes = set()
        self.edges = []
        self.node_types = {}
        self.node_connections = defaultdict(int)

    def load_relationships(self) -> List[Dict]:
        """Load relationships from JSON"""
        with open(self.relationships_path) as f:
            data = json.load(f)
        return data['relationships']

    def load_entities(self) -> Dict:
        """Load entities from JSON"""
        with open(self.entities_path) as f:
            data = json.load(f)
        return data['dossiers']

    def build_network(self):
        """Build network from relationships"""

        print("Building network graph...")

        for rel in self.relationships:
            entity1 = rel['entity_1']
            entity2 = rel['entity_2']
            entity1_type = rel['entity_1_type']
            entity2_type = rel['entity_2_type']
            rel_type = rel['relationship_type']
            mention_count = rel['mention_count']

            # Add nodes
            self.nodes.add(entity1)
            self.nodes.add(entity2)

            # Track node types
            self.node_types[entity1] = entity1_type
            self.node_types[entity2] = entity2_type

            # Add edge
            self.edges.append({
                'source': entity1,
                'target': entity2,
                'type': rel_type,
                'weight': mention_count
            })

            # Track connections
            self.node_connections[entity1] += mention_count
            self.node_connections[entity2] += mention_count

        print(f"  Nodes: {len(self.nodes)}")
        print(f"  Edges: {len(self.edges)}")

    def calculate_centrality(self) -> Dict[str, int]:
        """Calculate node centrality (degree centrality)"""
        return dict(self.node_connections)

    def get_top_nodes(self, n: int = 20) -> List[tuple]:
        """Get top N most connected nodes"""
        centrality = self.calculate_centrality()
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:n]

    def generate_dot_file(self, output_path: Path, top_n: int = 50):
        """Generate GraphViz DOT file"""

        # Get top nodes to limit graph size
        top_nodes_list = self.get_top_nodes(top_n)
        top_nodes_set = set(node for node, _ in top_nodes_list)

        # Filter edges to only include top nodes
        filtered_edges = [
            e for e in self.edges
            if e['source'] in top_nodes_set and e['target'] in top_nodes_set
        ]

        print(f"\nGenerating DOT file with top {top_n} nodes...")
        print(f"  Filtered edges: {len(filtered_edges)}")

        with open(output_path, 'w') as f:
            f.write("digraph GladioNetwork {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [fontname=\"Arial\"];\n")
            f.write("  edge [fontname=\"Arial\"];\n\n")

            # Add nodes with styling
            for node in top_nodes_set:
                node_type = self.node_types.get(node, "unknown")
                connections = self.node_connections.get(node, 0)

                # Size based on connections
                size = min(3.0, 0.5 + (connections / 50))

                # Color based on type
                if node_type == "person":
                    color = "lightblue"
                    shape = "ellipse"
                else:
                    color = "lightcoral"
                    shape = "box"

                # Clean node name for DOT format
                clean_name = node.replace('"', '\\"')

                f.write(f'  "{clean_name}" [')
                f.write(f'shape={shape}, ')
                f.write(f'style=filled, ')
                f.write(f'fillcolor={color}, ')
                f.write(f'width={size:.2f}, ')
                f.write(f'height={size:.2f}')
                f.write('];\n')

            f.write("\n")

            # Add edges
            edge_counts = Counter()
            for edge in filtered_edges:
                key = (edge['source'], edge['target'])
                edge_counts[key] += edge['weight']

            for (source, target), weight in edge_counts.items():
                clean_source = source.replace('"', '\\"')
                clean_target = target.replace('"', '\\"')

                # Edge thickness based on weight
                penwidth = min(5.0, 1.0 + (weight / 10))

                f.write(f'  "{clean_source}" -> "{clean_target}" [')
                f.write(f'penwidth={penwidth:.1f}')
                f.write('];\n')

            f.write("}\n")

        print(f"Saved DOT file to {output_path}")

    def calculate_metrics(self) -> Dict:
        """Calculate network metrics"""

        # Degree distribution
        degrees = list(self.node_connections.values())
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0

        # Node type distribution
        type_counts = Counter(self.node_types.values())

        # Relationship type distribution
        rel_types = [e['type'] for e in self.edges]
        rel_type_counts = Counter(rel_types)

        metrics = {
            'network_size': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'people': type_counts.get('person', 0),
                'organizations': type_counts.get('organization', 0)
            },
            'centrality': {
                'average_degree': avg_degree,
                'max_degree': max_degree,
                'top_10_nodes': self.get_top_nodes(10)
            },
            'relationship_types': dict(rel_type_counts),
            'generated': datetime.now().isoformat()
        }

        return metrics

    def save_metrics(self, metrics: Dict, output_path: Path):
        """Save network metrics to JSON"""
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)

        print(f"Saved metrics to {output_path}")

    def generate_images(self, dot_path: Path, output_dir: Path):
        """Generate PNG, SVG, and PDF from DOT file if GraphViz available"""

        # Check if GraphViz is installed
        if not shutil.which('dot'):
            print("\n⚠️  GraphViz not installed - skipping image generation")
            print("   Install with: sudo apt-get install graphviz")
            return

        formats = {
            'png': 'Raster image (for embedding in documents)',
            'svg': 'Scalable vector (for web/interactive)',
            'pdf': 'PDF format (for reports)'
        }

        print(f"\n📊 Generating network visualizations...")

        for fmt, description in formats.items():
            output_path = output_dir / f"gladio_network.{fmt}"

            try:
                subprocess.run([
                    'dot',
                    f'-T{fmt}',
                    str(dot_path),
                    '-o', str(output_path)
                ], check=True, capture_output=True, timeout=60)

                file_size = output_path.stat().st_size / (1024 * 1024)  # MB
                print(f"  ✅ {fmt.upper()}: {output_path.name} ({file_size:.1f}MB - {description})")

            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to generate {fmt}: {e.stderr.decode()}")
            except subprocess.TimeoutExpired:
                print(f"  ❌ Timeout generating {fmt} (>60s)")
            except Exception as e:
                print(f"  ❌ Error generating {fmt}: {e}")


def main():
    """Build network graph for Operation Gladio"""

    relationships_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/relationships.json")
    entities_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/entity_dossiers.json")
    dot_output_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/gladio_network.dot")
    metrics_output_path = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio/network_metrics.json")

    builder = NetworkGraphBuilder(relationships_path, entities_path)

    # Build network
    builder.build_network()

    # Calculate metrics
    metrics = builder.calculate_metrics()

    # Generate DOT file (top 50 nodes for readability)
    builder.generate_dot_file(dot_output_path, top_n=50)

    # Save metrics
    builder.save_metrics(metrics, metrics_output_path)

    # Generate images (PNG/SVG/PDF) if GraphViz available
    builder.generate_images(dot_output_path, dot_output_path.parent)

    # Display summary
    print("\n" + "="*60)
    print("NETWORK SUMMARY:")
    print("="*60)
    print(f"Total nodes: {metrics['network_size']['total_nodes']}")
    print(f"  People: {metrics['network_size']['people']}")
    print(f"  Organizations: {metrics['network_size']['organizations']}")
    print(f"Total edges: {metrics['network_size']['total_edges']}")
    print(f"Average connections: {metrics['centrality']['average_degree']:.1f}")
    print(f"Max connections: {metrics['centrality']['max_degree']}")

    print("\nTop 10 Most Connected Entities:")
    for node, connections in metrics['centrality']['top_10_nodes']:
        print(f"  {node}: {connections} connections")

    print("\nRelationship Type Distribution:")
    for rel_type, count in sorted(metrics['relationship_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {rel_type}: {count}")

    print(f"\n✅ Network analysis complete!")
    print(f"   DOT source: {dot_output_path.name}")
    if shutil.which('dot'):
        print(f"   Images: gladio_network.{{png,svg,pdf}}")
    else:
        print("   To generate images: dot -Tpng gladio_network.dot -o gladio_network.png")


if __name__ == "__main__":
    main()
