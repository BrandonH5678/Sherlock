#!/usr/bin/env python3
"""
Graph and Relationship Analysis System for Sherlock
Entity mapping, timeline analysis, and network visualization
"""

import json
import sys
import time
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import EvidenceDatabase


@dataclass
class EntityNode:
    """Node representing an entity in the knowledge graph"""
    entity_id: str
    entity_type: str  # person, organization, location, concept, event
    name: str
    aliases: List[str]
    claim_count: int
    first_mentioned: str
    last_mentioned: str
    confidence: float
    metadata: Dict


@dataclass
class RelationshipEdge:
    """Edge representing relationship between entities"""
    source_entity: str
    target_entity: str
    relationship_type: str
    weight: float
    evidence_claims: List[str]
    confidence: float
    metadata: Dict


@dataclass
class TimelineEvent:
    """Event in the timeline analysis"""
    event_id: str
    event_type: str
    timestamp: str
    entities: List[str]
    description: str
    source_claims: List[str]
    confidence: float


@dataclass
class NetworkCluster:
    """Cluster of related entities"""
    cluster_id: str
    entities: List[str]
    central_entity: str
    cluster_type: str
    cohesion_score: float
    description: str


class GraphAnalysisSystem:
    """Advanced graph analysis for entity relationships and networks"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.entity_graph = {}
        self.relationship_matrix = defaultdict(lambda: defaultdict(float))
        self.timeline_events = []

    def build_entity_graph(self) -> Dict[str, EntityNode]:
        """Build entity graph from evidence database"""

        print("🕸️  Building entity knowledge graph...")
        start_time = time.time()

        try:
            entity_mentions = defaultdict(lambda: {
                'count': 0,
                'sources': set(),
                'claims': [],
                'first_seen': None,
                'last_seen': None,
                'contexts': []
            })

            # Extract entities from all claims
            cursor = self.db.connection.execute("""
                SELECT claim_id, text, entities, context, created_at, source_id
                FROM evidence_claims
                ORDER BY created_at
            """)

            for row in cursor.fetchall():
                claim_id, text, entities_json, context, created_at, source_id = row
                entities = json.loads(entities_json) if entities_json else []

                for entity in entities:
                    entity_lower = entity.lower()
                    mention_data = entity_mentions[entity_lower]

                    mention_data['count'] += 1
                    mention_data['sources'].add(source_id)
                    mention_data['claims'].append(claim_id)
                    mention_data['contexts'].append(context[:100])

                    if not mention_data['first_seen']:
                        mention_data['first_seen'] = created_at
                    mention_data['last_seen'] = created_at

            # Create entity nodes
            entity_nodes = {}
            for entity_name, data in entity_mentions.items():
                if data['count'] >= 2:  # Filter entities mentioned at least twice
                    entity_type = self._classify_entity_type(entity_name, data['contexts'])

                    entity_id = f"entity_{hash(entity_name) % 100000:05d}"

                    node = EntityNode(
                        entity_id=entity_id,
                        entity_type=entity_type,
                        name=entity_name.title(),
                        aliases=[entity_name],
                        claim_count=data['count'],
                        first_mentioned=data['first_seen'],
                        last_mentioned=data['last_seen'],
                        confidence=min(data['count'] / 10.0, 1.0),  # Confidence based on mention frequency
                        metadata={
                            'source_count': len(data['sources']),
                            'sources': list(data['sources']),
                            'sample_contexts': data['contexts'][:3]
                        }
                    )

                    entity_nodes[entity_name] = node

            self.entity_graph = entity_nodes
            processing_time = time.time() - start_time

            print(f"✅ Entity graph built: {len(entity_nodes)} entities in {processing_time:.1f}s")
            return entity_nodes

        except Exception as e:
            print(f"❌ Entity graph building error: {e}")
            return {}

    def analyze_entity_relationships(self) -> List[RelationshipEdge]:
        """Analyze relationships between entities"""

        print("🔗 Analyzing entity relationships...")
        start_time = time.time()

        try:
            relationships = []

            # Find entities that co-occur in claims
            cursor = self.db.connection.execute("""
                SELECT claim_id, entities, text, confidence
                FROM evidence_claims
                WHERE entities != '[]' AND entities IS NOT NULL
            """)

            co_occurrence = defaultdict(lambda: defaultdict(int))
            claim_contexts = defaultdict(list)

            for row in cursor.fetchall():
                claim_id, entities_json, text, confidence = row
                entities = json.loads(entities_json) if entities_json else []

                # Convert to lowercase for matching
                entities_lower = [e.lower() for e in entities]

                # Record co-occurrences
                for i, entity1 in enumerate(entities_lower):
                    for entity2 in entities_lower[i+1:]:
                        if entity1 != entity2:
                            co_occurrence[entity1][entity2] += 1
                            co_occurrence[entity2][entity1] += 1
                            claim_contexts[(entity1, entity2)].append(claim_id)

            # Create relationship edges
            for entity1, related_entities in co_occurrence.items():
                for entity2, co_count in related_entities.items():
                    if co_count >= 2:  # Filter for meaningful relationships
                        relationship_type = self._classify_relationship_type(entity1, entity2, co_count)

                        edge = RelationshipEdge(
                            source_entity=entity1,
                            target_entity=entity2,
                            relationship_type=relationship_type,
                            weight=float(co_count),
                            evidence_claims=claim_contexts[(entity1, entity2)],
                            confidence=min(co_count / 5.0, 1.0),
                            metadata={
                                'co_occurrence_count': co_count,
                                'relationship_strength': 'strong' if co_count >= 5 else 'moderate'
                            }
                        )

                        relationships.append(edge)

            processing_time = time.time() - start_time
            print(f"✅ Relationship analysis complete: {len(relationships)} relationships in {processing_time:.1f}s")

            return relationships

        except Exception as e:
            print(f"❌ Relationship analysis error: {e}")
            return []

    def create_timeline_analysis(self) -> List[TimelineEvent]:
        """Create timeline of events from evidence"""

        print("📅 Creating timeline analysis...")
        start_time = time.time()

        try:
            timeline_events = []

            # Extract temporal claims and source creation dates
            cursor = self.db.connection.execute("""
                SELECT
                    ec.claim_id,
                    ec.text,
                    ec.entities,
                    ec.created_at,
                    es.created_at as source_created,
                    es.title as source_title,
                    ec.source_id
                FROM evidence_claims ec
                JOIN evidence_sources es ON ec.source_id = es.source_id
                ORDER BY es.created_at, ec.created_at
            """)

            event_clusters = defaultdict(list)

            for row in cursor.fetchall():
                claim_id, text, entities_json, claim_created, source_created, source_title, source_id = row
                entities = json.loads(entities_json) if entities_json else []

                # Use source creation date as primary timestamp
                timestamp = source_created or claim_created

                # Extract potential events from claim text
                event_type = self._classify_event_type(text)

                if event_type != 'general':  # Skip general statements
                    event_key = f"{timestamp[:10]}_{event_type}"  # Group by date and type
                    event_clusters[event_key].append({
                        'claim_id': claim_id,
                        'text': text,
                        'entities': entities,
                        'timestamp': timestamp,
                        'source_title': source_title,
                        'event_type': event_type
                    })

            # Create timeline events from clusters
            for event_key, claims in event_clusters.items():
                if len(claims) >= 1:  # At least one claim
                    all_entities = []
                    all_claim_ids = []
                    descriptions = []

                    for claim in claims:
                        all_entities.extend(claim['entities'])
                        all_claim_ids.append(claim['claim_id'])
                        descriptions.append(claim['text'][:100])

                    # Remove duplicates and create event
                    unique_entities = list(set(all_entities))

                    event = TimelineEvent(
                        event_id=f"event_{hash(event_key) % 100000:05d}",
                        event_type=claims[0]['event_type'],
                        timestamp=claims[0]['timestamp'],
                        entities=unique_entities,
                        description=f"Event involving {', '.join(unique_entities[:3])}{'...' if len(unique_entities) > 3 else ''}",
                        source_claims=all_claim_ids,
                        confidence=min(len(claims) / 3.0, 1.0)
                    )

                    timeline_events.append(event)

            # Sort by timestamp
            timeline_events.sort(key=lambda x: x.timestamp)
            self.timeline_events = timeline_events

            processing_time = time.time() - start_time
            print(f"✅ Timeline analysis complete: {len(timeline_events)} events in {processing_time:.1f}s")

            return timeline_events

        except Exception as e:
            print(f"❌ Timeline analysis error: {e}")
            return []

    def detect_network_clusters(self, relationships: List[RelationshipEdge]) -> List[NetworkCluster]:
        """Detect clusters of closely related entities"""

        print("🕸️  Detecting entity network clusters...")

        try:
            # Build adjacency list
            adjacency = defaultdict(set)
            entity_weights = defaultdict(float)

            for edge in relationships:
                adjacency[edge.source_entity].add(edge.target_entity)
                adjacency[edge.target_entity].add(edge.source_entity)
                entity_weights[edge.source_entity] += edge.weight
                entity_weights[edge.target_entity] += edge.weight

            # Simple clustering using connected components
            visited = set()
            clusters = []

            for entity in adjacency:
                if entity not in visited:
                    cluster_entities = self._find_connected_component(entity, adjacency, visited)

                    if len(cluster_entities) >= 2:  # Minimum cluster size
                        # Find central entity (highest weight)
                        central_entity = max(cluster_entities, key=lambda e: entity_weights[e])

                        # Calculate cohesion score
                        total_edges = sum(1 for e1 in cluster_entities for e2 in adjacency[e1] if e2 in cluster_entities)
                        possible_edges = len(cluster_entities) * (len(cluster_entities) - 1) / 2
                        cohesion_score = total_edges / possible_edges if possible_edges > 0 else 0

                        cluster = NetworkCluster(
                            cluster_id=f"cluster_{len(clusters):03d}",
                            entities=cluster_entities,
                            central_entity=central_entity,
                            cluster_type=self._classify_cluster_type(cluster_entities),
                            cohesion_score=cohesion_score,
                            description=f"Network cluster centered around {central_entity}"
                        )

                        clusters.append(cluster)

            print(f"✅ Network clustering complete: {len(clusters)} clusters detected")
            return clusters

        except Exception as e:
            print(f"❌ Network clustering error: {e}")
            return []

    def _find_connected_component(self, start_entity: str, adjacency: dict, visited: set) -> List[str]:
        """Find connected component using DFS"""
        component = []
        stack = [start_entity]

        while stack:
            entity = stack.pop()
            if entity not in visited:
                visited.add(entity)
                component.append(entity)
                stack.extend(neighbor for neighbor in adjacency[entity] if neighbor not in visited)

        return component

    def _classify_entity_type(self, entity_name: str, contexts: List[str]) -> str:
        """Classify entity type based on name and context"""

        entity_lower = entity_name.lower()

        # Person indicators
        if any(title in entity_lower for title in ['dr.', 'dr ', 'professor', 'mr.', 'ms.', 'mrs.']):
            return 'person'

        # Organization indicators
        if any(org_type in entity_lower for org_type in ['institute', 'university', 'company', 'corporation', 'agency']):
            return 'organization'

        # Location indicators
        if any(loc_type in entity_lower for loc_type in ['city', 'country', 'street', 'avenue', 'state']):
            return 'location'

        # Concept indicators
        if any(concept in entity_lower for concept in ['algorithm', 'system', 'method', 'process', 'technology']):
            return 'concept'

        # Event indicators
        if any(event in entity_lower for event in ['conference', 'meeting', 'trial', 'study', 'analysis']):
            return 'event'

        return 'concept'  # Default

    def _classify_relationship_type(self, entity1: str, entity2: str, co_count: int) -> str:
        """Classify relationship type between entities"""

        # Simple classification based on entity types and co-occurrence
        if co_count >= 5:
            return 'strong_association'
        elif co_count >= 3:
            return 'moderate_association'
        else:
            return 'weak_association'

    def _classify_event_type(self, text: str) -> str:
        """Classify event type from claim text"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['study', 'research', 'analysis', 'trial']):
            return 'research_event'
        elif any(word in text_lower for word in ['meeting', 'conference', 'discussion']):
            return 'meeting_event'
        elif any(word in text_lower for word in ['policy', 'regulation', 'law']):
            return 'policy_event'
        elif any(word in text_lower for word in ['crisis', 'disaster', 'emergency']):
            return 'crisis_event'
        else:
            return 'general'

    def _classify_cluster_type(self, entities: List[str]) -> str:
        """Classify cluster type based on member entities"""

        entity_types = [self._classify_entity_type(entity, []) for entity in entities]
        type_counter = Counter(entity_types)

        dominant_type = type_counter.most_common(1)[0][0]

        if dominant_type == 'person':
            return 'social_network'
        elif dominant_type == 'organization':
            return 'institutional_network'
        elif dominant_type == 'concept':
            return 'conceptual_network'
        else:
            return 'mixed_network'

    def generate_network_summary(self) -> Dict:
        """Generate comprehensive network analysis summary"""

        try:
            # Build components if not already built
            if not self.entity_graph:
                self.build_entity_graph()

            relationships = self.analyze_entity_relationships()
            timeline = self.create_timeline_analysis()
            clusters = self.detect_network_clusters(relationships)

            # Generate summary statistics
            summary = {
                'entity_count': len(self.entity_graph),
                'relationship_count': len(relationships),
                'timeline_events': len(timeline),
                'network_clusters': len(clusters),
                'entity_types': {},
                'relationship_types': {},
                'cluster_types': {},
                'temporal_span': {},
                'key_entities': [],
                'key_relationships': []
            }

            # Entity type distribution
            entity_types = [node.entity_type for node in self.entity_graph.values()]
            summary['entity_types'] = dict(Counter(entity_types))

            # Relationship type distribution
            relationship_types = [rel.relationship_type for rel in relationships]
            summary['relationship_types'] = dict(Counter(relationship_types))

            # Cluster type distribution
            cluster_types = [cluster.cluster_type for cluster in clusters]
            summary['cluster_types'] = dict(Counter(cluster_types))

            # Temporal span
            if timeline:
                earliest = min(event.timestamp for event in timeline)
                latest = max(event.timestamp for event in timeline)
                summary['temporal_span'] = {
                    'earliest': earliest,
                    'latest': latest,
                    'span_days': (datetime.fromisoformat(latest.replace('Z', '+00:00')) -
                                datetime.fromisoformat(earliest.replace('Z', '+00:00'))).days
                }

            # Key entities (highest mention count)
            key_entities = sorted(self.entity_graph.values(), key=lambda x: x.claim_count, reverse=True)[:5]
            summary['key_entities'] = [{'name': e.name, 'mentions': e.claim_count, 'type': e.entity_type} for e in key_entities]

            # Key relationships (highest weight)
            key_relationships = sorted(relationships, key=lambda x: x.weight, reverse=True)[:5]
            summary['key_relationships'] = [
                {'entities': [r.source_entity, r.target_entity], 'weight': r.weight, 'type': r.relationship_type}
                for r in key_relationships
            ]

            return summary

        except Exception as e:
            print(f"❌ Network summary generation error: {e}")
            return {}

    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """CLI interface for graph analysis system"""
    if len(sys.argv) < 2:
        print("Graph Analysis System for Sherlock")
        print("Usage:")
        print("  python graph_analysis.py entities")
        print("  python graph_analysis.py relationships")
        print("  python graph_analysis.py timeline")
        print("  python graph_analysis.py clusters")
        print("  python graph_analysis.py summary")
        sys.exit(1)

    command = sys.argv[1].lower()
    graph_system = GraphAnalysisSystem()

    try:
        if command == "entities":
            entities = graph_system.build_entity_graph()

            print(f"\n🕸️  ENTITY GRAPH ANALYSIS")
            print("=" * 40)

            if not entities:
                print("No entities found")
            else:
                print(f"Total entities: {len(entities)}")

                # Show top entities by mention count
                top_entities = sorted(entities.values(), key=lambda x: x.claim_count, reverse=True)[:10]
                print("\nTop entities by mentions:")
                for i, entity in enumerate(top_entities, 1):
                    print(f"  {i}. {entity.name} ({entity.entity_type}): {entity.claim_count} mentions")

        elif command == "relationships":
            graph_system.build_entity_graph()
            relationships = graph_system.analyze_entity_relationships()

            print(f"\n🔗 RELATIONSHIP ANALYSIS")
            print("=" * 40)

            if not relationships:
                print("No relationships found")
            else:
                print(f"Total relationships: {len(relationships)}")

                # Show strongest relationships
                top_relationships = sorted(relationships, key=lambda x: x.weight, reverse=True)[:10]
                print("\nStrongest relationships:")
                for i, rel in enumerate(top_relationships, 1):
                    print(f"  {i}. {rel.source_entity} ↔ {rel.target_entity} (weight: {rel.weight})")

        elif command == "timeline":
            timeline = graph_system.create_timeline_analysis()

            print(f"\n📅 TIMELINE ANALYSIS")
            print("=" * 40)

            if not timeline:
                print("No timeline events found")
            else:
                print(f"Total events: {len(timeline)}")

                # Show recent events
                recent_events = timeline[-10:] if len(timeline) > 10 else timeline
                print("\nRecent events:")
                for i, event in enumerate(recent_events, 1):
                    print(f"  {i}. {event.timestamp[:10]} - {event.event_type}: {event.description}")

        elif command == "clusters":
            graph_system.build_entity_graph()
            relationships = graph_system.analyze_entity_relationships()
            clusters = graph_system.detect_network_clusters(relationships)

            print(f"\n🕸️  NETWORK CLUSTERS")
            print("=" * 40)

            if not clusters:
                print("No clusters found")
            else:
                print(f"Total clusters: {len(clusters)}")

                for i, cluster in enumerate(clusters[:5], 1):
                    print(f"\n{i}. {cluster.cluster_type.upper()} (cohesion: {cluster.cohesion_score:.2f})")
                    print(f"   Central entity: {cluster.central_entity}")
                    print(f"   Members: {', '.join(cluster.entities[:5])}{'...' if len(cluster.entities) > 5 else ''}")

        elif command == "summary":
            summary = graph_system.generate_network_summary()

            print(f"\n📊 NETWORK ANALYSIS SUMMARY")
            print("=" * 40)
            print(f"Entities: {summary.get('entity_count', 0)}")
            print(f"Relationships: {summary.get('relationship_count', 0)}")
            print(f"Timeline events: {summary.get('timeline_events', 0)}")
            print(f"Network clusters: {summary.get('network_clusters', 0)}")

            if summary.get('entity_types'):
                print("\nEntity types:")
                for etype, count in summary['entity_types'].items():
                    print(f"  {etype}: {count}")

            if summary.get('key_entities'):
                print("\nKey entities:")
                for entity in summary['key_entities'][:3]:
                    print(f"  {entity['name']} ({entity['type']}): {entity['mentions']} mentions")

        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)

    finally:
        graph_system.close()


if __name__ == "__main__":
    main()