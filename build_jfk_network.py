#!/usr/bin/env python3
"""
JFK Entity Relationship Network Builder
Builds network graph from JFK evidence claims

Architecture: Similar to Thread 3 network builder
Output: GraphViz visualization + statistics
"""

import json
import sqlite3
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List
from collections import defaultdict, Counter
from datetime import datetime


class JFKNetworkBuilder:
    """Build JFK relationship network from evidence"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        self.nodes = {}
        self.edges = defaultdict(int)

    def extract_jfk_entities(self) -> Dict[str, List[str]]:
        """Extract entities from JFK claims"""
        cursor = self.conn.execute("""
            SELECT entities FROM evidence_claims
            WHERE source_id LIKE 'jfk%'
        """)

        all_entities = []
        for row in cursor:
            try:
                entities = json.loads(row['entities']) if row['entities'] else []
                all_entities.extend(entities)
            except:
                pass

        return Counter(all_entities)

    def build_network(self):
        """Build co-occurrence network"""
        print("\n🔍 Building JFK entity network...")

        # Get entities from claims
        cursor = self.conn.execute("""
            SELECT entities FROM evidence_claims
            WHERE source_id LIKE 'jfk%'
        """)

        entity_mentions = Counter()
        claim_entities = []

        for row in cursor:
            try:
                entities = json.loads(row['entities']) if row['entities'] else []
                entity_list = list(set(entities))  # Unique per claim
                claim_entities.append(entity_list)

                for entity in entity_list:
                    entity_mentions[entity] += 1
            except:
                pass

        # Build nodes
        for entity, count in entity_mentions.items():
            entity_type = self._classify_entity(entity)
            self.nodes[entity] = {
                'type': entity_type,
                'mentions': count,
                'connections': 0
            }

        # Build edges
        for entities in claim_entities:
            for i, e1 in enumerate(entities):
                for e2 in entities[i+1:]:
                    edge = tuple(sorted([e1, e2]))
                    self.edges[edge] += 1

        # Update connection counts
        for (e1, e2), count in self.edges.items():
            if e1 in self.nodes:
                self.nodes[e1]['connections'] += count
            if e2 in self.nodes:
                self.nodes[e2]['connections'] += count

        print(f"  ✅ Nodes: {len(self.nodes)}")
        print(f"  ✅ Edges: {len(self.edges)}")

    def _classify_entity(self, entity: str) -> str:
        """Classify entity type"""
        entity_lower = entity.lower()

        # Organizations
        if any(o in entity_lower for o in ['cia', 'hsca', 'dre', 'fbi', 'committee', 'commission', 'arrb', 'jmwave', 'station']):
            return 'organization'

        # Locations
        if any(l in entity_lower for l in ['orleans', 'mexico', 'miami', 'dallas', 'consulate', 'embassy']):
            return 'location'

        # Programs (special CIA operations)
        if any(p in entity_lower for p in ['jmwave', 'dre']):
            return 'program'

        # People (has spaces, capitalized, not caught above)
        if ' ' in entity and entity[0].isupper():
            return 'person'

        # Default to organization if all caps
        if entity.isupper():
            return 'organization'

        return 'person'

    def generate_dot_file(self, output_path: Path, top_n: int = 30):
        """Generate GraphViz DOT file"""
        print(f"\n📊 Generating GraphViz network (top {top_n} entities)...")

        # Sort by connections
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda x: x[1]['connections'],
            reverse=True
        )[:top_n]

        top_entity_names = {name for name, _ in sorted_nodes}

        # Colors
        colors = {
            'organization': '#FF6B6B',  # Red
            'person': '#4ECDC4',        # Cyan
            'location': '#FFE66D',      # Yellow
            'program': '#95E1D3'        # Light cyan
        }

        # Generate DOT
        dot_lines = [
            'graph JFKNetwork {',
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
            color = colors.get(entity_type, '#CCCCCC')
            size = 0.4 + (data['connections'] / 20.0)

            label = entity.replace('"', '\\"')
            dot_lines.append(
                f'  "{entity}" [fillcolor="{color}", '
                f'label="{label}", '
                f'width={size:.2f}, height={size:.2f}];'
            )

        dot_lines.append('')

        # Add edges
        for (e1, e2), weight in self.edges.items():
            if e1 in top_entity_names and e2 in top_entity_names:
                penwidth = min(1.0 + (weight / 2.0), 5.0)
                dot_lines.append(f'  "{e1}" -- "{e2}" [penwidth={penwidth:.1f}];')

        dot_lines.append('}')

        with open(output_path, 'w') as f:
            f.write('\n'.join(dot_lines))

        print(f"  ✅ DOT file: {output_path}")

    def generate_images(self, dot_path: Path, output_dir: Path):
        """Generate PNG/SVG/PDF from DOT"""
        if not shutil.which('dot'):
            print("\n⚠️  GraphViz not installed - skipping")
            return

        formats = {
            'png': 'Raster image',
            'svg': 'Scalable vector',
            'pdf': 'PDF format'
        }

        print(f"\nGenerating visualizations...")

        for fmt, desc in formats.items():
            output_path = output_dir / f"jfk_network.{fmt}"

            try:
                subprocess.run([
                    'dot', f'-T{fmt}', str(dot_path), '-o', str(output_path)
                ], check=True, capture_output=True, timeout=60)

                size = output_path.stat().st_size / 1024  # KB
                print(f"  ✅ {fmt.upper()}: {output_path.name} ({size:.1f}KB)")
            except Exception as e:
                print(f"  ❌ {fmt.upper()}: Failed")

    def generate_statistics(self, output_path: Path):
        """Generate network statistics"""
        stats = {
            'network_size': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'nodes_by_type': dict(Counter(n['type'] for n in self.nodes.values()))
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
            'generated': datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"  ✅ Statistics: {output_path}")

        return stats


def main():
    """Build JFK network"""
    print("=" * 70)
    print("JFK Entity Relationship Network Builder")
    print("=" * 70)

    builder = JFKNetworkBuilder("/home/johnny5/Sherlock/evidence.db")

    # Build network
    builder.build_network()

    # Generate outputs
    output_dir = Path("/home/johnny5/Sherlock/jfk_network")
    output_dir.mkdir(exist_ok=True)

    dot_path = output_dir / "jfk_network.dot"
    builder.generate_dot_file(dot_path, top_n=25)

    # Generate images
    builder.generate_images(dot_path, output_dir)

    # Generate statistics
    stats_path = output_dir / "jfk_network_stats.json"
    stats = builder.generate_statistics(stats_path)

    print("\n" + "=" * 70)
    print("✅ JFK Network Generation Complete")
    print("=" * 70)
    print(f"\nNetwork Statistics:")
    print(f"  - Total nodes: {stats['network_size']['total_nodes']}")
    print(f"  - Total edges: {stats['network_size']['total_edges']}")
    print(f"  - Most connected: {stats['centrality']['top_10_nodes'][0][0]} ({stats['centrality']['top_10_nodes'][0][1]} connections)")


if __name__ == "__main__":
    main()
