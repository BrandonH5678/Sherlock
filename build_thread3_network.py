#!/usr/bin/env python3
"""
Thread 3 Relationship Network Builder
Builds entity relationship graph from Thread 3 intelligence

Architecture: Similar to Operation Gladio network builder
Output: GraphViz DOT file + PNG/SVG/PDF visualizations
"""

import json
import sqlite3
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter


class Thread3NetworkBuilder:
    """Build relationship network from Thread 3 evidence"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        # Network structures
        self.nodes = {}  # entity_name -> {type, connections, mentions}
        self.edges = defaultdict(int)  # (entity1, entity2) -> co-occurrence count

    def extract_entities_from_claims(self) -> Dict[str, Set[str]]:
        """
        Extract all entities from Thread 3 claims

        Returns: claim_id -> set of entities
        """
        cursor = self.conn.execute("""
            SELECT claim_id, entities
            FROM evidence_claims
            WHERE source_id LIKE 'thread3%'
        """)

        claim_entities = {}
        for row in cursor:
            claim_id = row['claim_id']
            entities_json = row['entities']

            try:
                entities = json.loads(entities_json) if entities_json else []
                claim_entities[claim_id] = set(entities)
            except:
                claim_entities[claim_id] = set()

        return claim_entities

    def build_co_occurrence_network(self):
        """Build network based on entity co-occurrences in claims"""
        print("\n🔍 Building Thread 3 co-occurrence network...")

        claim_entities = self.extract_entities_from_claims()

        # Count entity mentions
        entity_mentions = Counter()
        for entities in claim_entities.values():
            for entity in entities:
                entity_mentions[entity] += 1

        # Build nodes
        for entity, count in entity_mentions.items():
            # Classify entity type based on name patterns
            entity_type = self._classify_entity(entity)

            self.nodes[entity] = {
                'type': entity_type,
                'mentions': count,
                'connections': 0
            }

        # Build edges (co-occurrences)
        for entities in claim_entities.values():
            entities_list = list(entities)
            for i, entity1 in enumerate(entities_list):
                for entity2 in entities_list[i+1:]:
                    # Normalize edge (always smaller entity first)
                    edge = tuple(sorted([entity1, entity2]))
                    self.edges[edge] += 1

        # Update connection counts
        for (e1, e2), count in self.edges.items():
            self.nodes[e1]['connections'] += count
            self.nodes[e2]['connections'] += count

        print(f"  ✅ Nodes: {len(self.nodes)}")
        print(f"  ✅ Edges: {len(self.edges)}")

    def _classify_entity(self, entity: str) -> str:
        """Classify entity type based on name patterns"""
        entity_lower = entity.lower()

        # Programs
        if any(p in entity_lower for p in ['thread', 'unit', 'aawsap', 'baass', 'program']):
            return 'program'

        # Organizations
        if any(o in entity_lower for o in ['ministry', 'cia', 'dia', 'mod', 'ussr', 'russia']):
            return 'organization'

        # Locations
        if any(l in entity_lower for l in ['area', 'moscow', 'ukraine', 'groom', 'base', 'afb']):
            return 'location'

        # People (capitalized, contains spaces, no special keywords)
        if entity[0].isupper() and ' ' in entity:
            return 'person'

        return 'unknown'

    def generate_dot_file(self, output_path: Path, top_n: int = 50):
        """
        Generate GraphViz DOT file

        Args:
            top_n: Show only top N most connected entities
        """
        print(f"\n📊 Generating GraphViz network (top {top_n} entities)...")

        # Sort nodes by connection count
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda x: x[1]['connections'],
            reverse=True
        )[:top_n]

        top_entity_names = {name for name, _ in sorted_nodes}

        # Color scheme by entity type
        colors = {
            'program': '#FF6B6B',      # Red
            'organization': '#4ECDC4', # Cyan
            'person': '#95E1D3',       # Light cyan
            'location': '#FFE66D',     # Yellow
            'unknown': '#CCCCCC'       # Gray
        }

        # Generate DOT (use graph, not digraph, for undirected edges)
        dot_lines = [
            'graph Thread3Network {',
            '  layout=fdp;',
            '  overlap=false;',
            '  splines=true;',
            '  node [style=filled, fontname="Arial"];',
            '  edge [color="#88888844"];',
            ''
        ]

        # Add nodes
        for entity, data in sorted_nodes:
            entity_type = data['type']
            color = colors.get(entity_type, colors['unknown'])
            size = 0.3 + (data['connections'] / 100.0)  # Scale by connections

            label = entity.replace('"', '\\"')
            dot_lines.append(
                f'  "{entity}" [fillcolor="{color}", '
                f'label="{label}", '
                f'width={size:.2f}, height={size:.2f}];'
            )

        dot_lines.append('')

        # Add edges (only between top entities)
        for (e1, e2), weight in self.edges.items():
            if e1 in top_entity_names and e2 in top_entity_names:
                # Edge width based on co-occurrence count
                penwidth = min(1.0 + (weight / 5.0), 5.0)
                dot_lines.append(f'  "{e1}" -- "{e2}" [penwidth={penwidth:.1f}];')

        dot_lines.append('}')

        # Write DOT file
        with open(output_path, 'w') as f:
            f.write('\n'.join(dot_lines))

        print(f"  ✅ DOT file: {output_path}")

    def generate_images(self, dot_path: Path, output_dir: Path):
        """Generate PNG, SVG, PDF from DOT file if GraphViz available"""
        if not shutil.which('dot'):
            print("\n⚠️  GraphViz not installed - skipping image generation")
            print("   Install with: sudo apt-get install graphviz")
            return

        formats = {
            'png': 'Raster image (for embedding in documents)',
            'svg': 'Scalable vector (for web/interactive)',
            'pdf': 'PDF format (for reports)'
        }

        print(f"\nGenerating network visualizations...")

        for fmt, description in formats.items():
            output_path = output_dir / f"thread3_network.{fmt}"

            try:
                subprocess.run([
                    'dot',
                    f'-T{fmt}',
                    str(dot_path),
                    '-o', str(output_path)
                ], check=True, capture_output=True, timeout=60)

                size = output_path.stat().st_size / (1024 * 1024)  # MB
                print(f"  ✅ {fmt.upper()}: {output_path.name} ({size:.1f}MB) - {description}")

            except subprocess.TimeoutExpired:
                print(f"  ❌ {fmt.upper()}: Timeout (graph too complex)")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ {fmt.upper()}: Failed - {e.stderr.decode()}")

    def generate_statistics(self, output_path: Path):
        """Generate network statistics JSON"""
        stats = {
            'network_size': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'nodes_by_type': Counter(n['type'] for n in self.nodes.values())
            },
            'centrality': {
                'top_10_nodes': [
                    (name, data['connections'])
                    for name, data in sorted(
                        self.nodes.items(),
                        key=lambda x: x[1]['connections'],
                        reverse=True
                    )[:10]
                ]
            },
            'generated': Path(__file__).name
        }

        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"  ✅ Statistics: {output_path}")


def main():
    """Build Thread 3 network and generate visualizations"""
    print("=" * 70)
    print("Thread 3 Relationship Network Builder")
    print("=" * 70)

    builder = Thread3NetworkBuilder("/home/johnny5/Sherlock/evidence.db")

    # Build network
    builder.build_co_occurrence_network()

    # Generate outputs
    output_dir = Path("/home/johnny5/Sherlock/thread3_network")
    output_dir.mkdir(exist_ok=True)

    dot_path = output_dir / "thread3_network.dot"
    builder.generate_dot_file(dot_path, top_n=30)

    # Generate images
    builder.generate_images(dot_path, output_dir)

    # Generate statistics
    stats_path = output_dir / "thread3_network_stats.json"
    builder.generate_statistics(stats_path)

    print("\n" + "=" * 70)
    print("✅ Thread 3 Network Generation Complete")
    print("=" * 70)
    print(f"\nNetwork files: {output_dir}/")
    print(f"  - thread3_network.dot (GraphViz source)")
    print(f"  - thread3_network.png (visualization)")
    print(f"  - thread3_network.svg (scalable)")
    print(f"  - thread3_network.pdf (printable)")
    print(f"  - thread3_network_stats.json (statistics)")


if __name__ == "__main__":
    main()
