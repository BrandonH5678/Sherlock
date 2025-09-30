#!/usr/bin/env python3
"""
Operation Gladio Analysis Tools
Advanced analysis and visualization for evidence patterns
"""

import json
import sqlite3
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
from datetime import datetime
import re

from evidence_schema_gladio import (
    GladioEvidenceDatabase, PersonDossier, Organization,
    Relationship, ConfidenceLevel
)


class GladioAnalyzer:
    """Advanced analysis tools for Operation Gladio evidence"""

    def __init__(self, db_path: str = "gladio_evidence.db"):
        self.db = GladioEvidenceDatabase(db_path)

    def analyze_network_patterns(self) -> Dict:
        """Analyze network patterns and identify key nodes"""
        print("🕸️  Analyzing network patterns...")

        # Get all relationships
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT relationship_json FROM relationships")
        relationships = []
        for row in cursor.fetchall():
            rel_data = json.loads(row[0])
            relationships.append(rel_data)

        conn.close()

        # Build network graph
        network = defaultdict(list)
        entity_types = {}
        relationship_types = Counter()

        for rel in relationships:
            entity1 = rel['entity_1']
            entity2 = rel['entity_2']
            rel_type = rel['relationship_type']

            network[entity1].append({
                'target': entity2,
                'type': rel_type,
                'confidence': rel.get('confidence', 'possible')
            })

            network[entity2].append({
                'target': entity1,
                'type': rel_type,
                'confidence': rel.get('confidence', 'possible')
            })

            entity_types[entity1] = rel['entity_1_type']
            entity_types[entity2] = rel['entity_2_type']
            relationship_types[rel_type] += 1

        # Calculate network metrics
        centrality_scores = self.calculate_centrality(network)
        clusters = self.identify_clusters(network)
        hidden_patterns = self.identify_hidden_patterns(relationships)

        analysis = {
            'network_size': {
                'total_entities': len(network),
                'total_relationships': len(relationships),
                'entity_types': dict(Counter(entity_types.values())),
                'relationship_types': dict(relationship_types)
            },
            'key_entities': {
                'highest_centrality': sorted(
                    centrality_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                'most_connected': sorted(
                    [(entity, len(connections)) for entity, connections in network.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            },
            'clusters': clusters,
            'hidden_patterns': hidden_patterns,
            'network_graph': dict(network)
        }

        return analysis

    def calculate_centrality(self, network: Dict) -> Dict[str, float]:
        """Calculate centrality scores for network entities"""
        centrality = {}

        for entity in network:
            # Simple degree centrality (number of connections)
            degree = len(network[entity])

            # Weighted by relationship confidence
            weighted_degree = 0
            for connection in network[entity]:
                confidence_weight = {
                    'confirmed': 1.0,
                    'probable': 0.8,
                    'possible': 0.6,
                    'disputed': 0.4,
                    'unverified': 0.2
                }.get(connection['confidence'], 0.6)
                weighted_degree += confidence_weight

            centrality[entity] = weighted_degree

        return centrality

    def identify_clusters(self, network: Dict) -> List[Dict]:
        """Identify clusters of highly connected entities"""
        visited = set()
        clusters = []

        def dfs_cluster(start_node, current_cluster, depth=0, max_depth=3):
            if depth > max_depth or start_node in visited:
                return

            visited.add(start_node)
            current_cluster.add(start_node)

            for connection in network.get(start_node, []):
                target = connection['target']
                if target not in visited:
                    dfs_cluster(target, current_cluster, depth + 1, max_depth)

        for entity in network:
            if entity not in visited:
                cluster = set()
                dfs_cluster(entity, cluster)
                if len(cluster) > 2:  # Only clusters with 3+ entities
                    clusters.append({
                        'cluster_id': f"CLUSTER_{len(clusters)+1}",
                        'entities': list(cluster),
                        'size': len(cluster)
                    })

        return sorted(clusters, key=lambda x: x['size'], reverse=True)

    def identify_hidden_patterns(self, relationships: List[Dict]) -> Dict:
        """Identify patterns that suggest hidden relationships"""
        patterns = {
            'temporal_clustering': self.find_temporal_clustering(relationships),
            'organizational_overlaps': self.find_organizational_overlaps(relationships),
            'indirect_connections': self.find_indirect_connections(relationships),
            'missing_links': self.identify_missing_links(relationships)
        }

        return patterns

    def find_temporal_clustering(self, relationships: List[Dict]) -> List[Dict]:
        """Find relationships that cluster in time periods"""
        time_periods = defaultdict(list)

        for rel in relationships:
            start_time = rel.get('relationship_start', {})
            if start_time and start_time.get('year'):
                decade = (start_time['year'] // 10) * 10
                time_periods[decade].append(rel)

        clusters = []
        for decade, rels in time_periods.items():
            if len(rels) > 3:  # Significant clustering
                clusters.append({
                    'time_period': f"{decade}s",
                    'relationship_count': len(rels),
                    'entities_involved': list(set([r['entity_1'] for r in rels] + [r['entity_2'] for r in rels]))
                })

        return sorted(clusters, key=lambda x: x['relationship_count'], reverse=True)

    def find_organizational_overlaps(self, relationships: List[Dict]) -> List[Dict]:
        """Find entities connected to multiple organizations"""
        entity_orgs = defaultdict(set)

        for rel in relationships:
            if rel['entity_1_type'] == 'person' and rel['entity_2_type'] == 'organization':
                entity_orgs[rel['entity_1']].add(rel['entity_2'])
            elif rel['entity_1_type'] == 'organization' and rel['entity_2_type'] == 'person':
                entity_orgs[rel['entity_2']].add(rel['entity_1'])

        overlaps = []
        for entity, orgs in entity_orgs.items():
            if len(orgs) > 1:  # Connected to multiple organizations
                overlaps.append({
                    'entity': entity,
                    'organizations': list(orgs),
                    'overlap_count': len(orgs)
                })

        return sorted(overlaps, key=lambda x: x['overlap_count'], reverse=True)

    def find_indirect_connections(self, relationships: List[Dict]) -> List[Dict]:
        """Find potential indirect connections through intermediaries"""
        # Build connection map
        connections = defaultdict(set)
        for rel in relationships:
            connections[rel['entity_1']].add(rel['entity_2'])
            connections[rel['entity_2']].add(rel['entity_1'])

        indirect = []
        for entity1 in connections:
            for entity2 in connections:
                if entity1 != entity2 and entity2 not in connections[entity1]:
                    # Check for common connections
                    common = connections[entity1] & connections[entity2]
                    if len(common) > 1:  # Multiple shared connections
                        indirect.append({
                            'entity_1': entity1,
                            'entity_2': entity2,
                            'intermediaries': list(common),
                            'connection_strength': len(common)
                        })

        return sorted(indirect, key=lambda x: x['connection_strength'], reverse=True)[:20]

    def identify_missing_links(self, relationships: List[Dict]) -> List[str]:
        """Identify potential missing relationships based on patterns"""
        suggestions = []

        # This would implement sophisticated pattern matching
        # For now, return placeholder analysis
        suggestions.append("Analysis of organizational hierarchy gaps")
        suggestions.append("Temporal relationship gap analysis")
        suggestions.append("Geographic co-location pattern analysis")

        return suggestions

    def generate_timeline_analysis(self, start_year: int = 1945, end_year: int = 1990) -> Dict:
        """Generate comprehensive timeline analysis"""
        print(f"📅 Generating timeline analysis {start_year}-{end_year}...")

        # Get all temporal data
        timeline_events = []

        # People events
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT dossier_json FROM people")
        for row in cursor.fetchall():
            person_data = json.loads(row[0])
            events = self.extract_person_timeline(person_data)
            timeline_events.extend(events)

        # Organization events
        cursor.execute("SELECT organization_json FROM organizations")
        for row in cursor.fetchall():
            org_data = json.loads(row[0])
            events = self.extract_organization_timeline(org_data)
            timeline_events.extend(events)

        conn.close()

        # Filter by date range
        filtered_events = [
            event for event in timeline_events
            if start_year <= event['year'] <= end_year
        ]

        # Analyze patterns
        analysis = {
            'total_events': len(filtered_events),
            'events_by_year': self.group_by_year(filtered_events),
            'events_by_type': self.group_by_type(filtered_events),
            'significant_periods': self.identify_significant_periods(filtered_events),
            'event_density': self.calculate_event_density(filtered_events),
            'timeline_events': sorted(filtered_events, key=lambda x: x['year'])
        }

        return analysis

    def extract_person_timeline(self, person_data: Dict) -> List[Dict]:
        """Extract timeline events from person data"""
        events = []
        person_id = person_data['person_id']
        name = f"{person_data.get('first_name', '')} {person_data.get('last_name', '')}"

        # Birth
        if person_data.get('birth_date') and person_data['birth_date'].get('year'):
            events.append({
                'year': person_data['birth_date']['year'],
                'event_type': 'birth',
                'entity_id': person_id,
                'entity_type': 'person',
                'description': f"{name} born",
                'confidence': person_data['birth_date'].get('confidence', 'possible')
            })

        # Extract events from various timeline fields
        timeline_fields = [
            'education_timeline', 'military_service', 'organization_memberships',
            'operation_participation', 'significant_activities'
        ]

        for field in timeline_fields:
            if person_data.get(field):
                for claim in person_data[field]:
                    if claim.get('time_reference') and claim['time_reference'].get('year'):
                        events.append({
                            'year': claim['time_reference']['year'],
                            'event_type': field,
                            'entity_id': person_id,
                            'entity_type': 'person',
                            'description': f"{name}: {claim['statement']}",
                            'confidence': claim.get('overall_confidence', 'possible')
                        })

        return events

    def extract_organization_timeline(self, org_data: Dict) -> List[Dict]:
        """Extract timeline events from organization data"""
        events = []
        org_id = org_data['organization_id']
        name = org_data['name']

        # Founding
        if org_data.get('founding_date') and org_data['founding_date'].get('year'):
            events.append({
                'year': org_data['founding_date']['year'],
                'event_type': 'founding',
                'entity_id': org_id,
                'entity_type': 'organization',
                'description': f"{name} founded",
                'confidence': org_data['founding_date'].get('confidence', 'possible')
            })

        return events

    def group_by_year(self, events: List[Dict]) -> Dict[int, int]:
        """Group events by year"""
        return dict(Counter([event['year'] for event in events]))

    def group_by_type(self, events: List[Dict]) -> Dict[str, int]:
        """Group events by type"""
        return dict(Counter([event['event_type'] for event in events]))

    def identify_significant_periods(self, events: List[Dict]) -> List[Dict]:
        """Identify periods with high event density"""
        events_by_year = self.group_by_year(events)

        significant = []
        for year, count in events_by_year.items():
            if count > 5:  # Threshold for significance
                significant.append({
                    'year': year,
                    'event_count': count,
                    'significance': 'high' if count > 10 else 'medium'
                })

        return sorted(significant, key=lambda x: x['event_count'], reverse=True)

    def calculate_event_density(self, events: List[Dict]) -> Dict:
        """Calculate event density over time"""
        if not events:
            return {}

        years = [event['year'] for event in events]
        min_year, max_year = min(years), max(years)
        total_years = max_year - min_year + 1

        return {
            'events_per_year': len(events) / total_years,
            'peak_year': max(Counter(years).items(), key=lambda x: x[1]),
            'time_span': f"{min_year}-{max_year}",
            'total_events': len(events)
        }

    def generate_evidence_validation_report(self) -> Dict:
        """Generate report on evidence quality and validation"""
        print("🔍 Generating evidence validation report...")

        # Get all evidence from database
        all_evidence = []
        confidence_distribution = Counter()
        evidence_types = Counter()

        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        # Check people evidence
        cursor.execute("SELECT dossier_json FROM people")
        for row in cursor.fetchall():
            person_data = json.loads(row[0])
            evidence = self.extract_person_evidence(person_data)
            all_evidence.extend(evidence)

        conn.close()

        # Analyze evidence quality
        for evidence in all_evidence:
            confidence_distribution[evidence.get('confidence', 'unknown')] += 1
            evidence_types[evidence.get('evidence_type', 'unknown')] += 1

        # Calculate validation metrics
        total_evidence = len(all_evidence)
        high_confidence = sum(confidence_distribution[level] for level in ['confirmed', 'probable'])
        validation_rate = (high_confidence / total_evidence * 100) if total_evidence > 0 else 0

        report = {
            'total_evidence_pieces': total_evidence,
            'confidence_distribution': dict(confidence_distribution),
            'evidence_types': dict(evidence_types),
            'validation_rate': validation_rate,
            'quality_assessment': self.assess_evidence_quality(confidence_distribution),
            'recommendations': self.generate_evidence_recommendations(confidence_distribution)
        }

        return report

    def extract_person_evidence(self, person_data: Dict) -> List[Dict]:
        """Extract all evidence from person data"""
        evidence = []

        timeline_fields = [
            'education_timeline', 'military_service', 'organization_memberships',
            'operation_participation', 'significant_activities'
        ]

        for field in timeline_fields:
            if person_data.get(field):
                for claim in person_data[field]:
                    if claim.get('supporting_evidence'):
                        evidence.extend(claim['supporting_evidence'])

        return evidence

    def assess_evidence_quality(self, confidence_dist: Counter) -> str:
        """Assess overall evidence quality"""
        total = sum(confidence_dist.values())
        if total == 0:
            return "No evidence"

        high_conf = confidence_dist['confirmed'] + confidence_dist['probable']
        high_conf_rate = high_conf / total

        if high_conf_rate > 0.7:
            return "High quality"
        elif high_conf_rate > 0.4:
            return "Medium quality"
        else:
            return "Low quality - needs more verification"

    def generate_evidence_recommendations(self, confidence_dist: Counter) -> List[str]:
        """Generate recommendations for improving evidence quality"""
        recommendations = []

        total = sum(confidence_dist.values())
        if total == 0:
            return ["No evidence to analyze"]

        unverified_rate = confidence_dist['unverified'] / total
        if unverified_rate > 0.3:
            recommendations.append("High rate of unverified claims - seek additional sources")

        disputed_rate = confidence_dist['disputed'] / total
        if disputed_rate > 0.1:
            recommendations.append("Significant disputed evidence - investigate contradictions")

        if confidence_dist['confirmed'] < total * 0.2:
            recommendations.append("Low confirmed evidence rate - seek primary sources")

        return recommendations

    def export_analysis_report(self, output_file: str = "gladio_analysis_report.json"):
        """Export comprehensive analysis report"""
        print(f"📤 Exporting analysis report to {output_file}...")

        report = {
            'analysis_date': datetime.now().isoformat(),
            'network_analysis': self.analyze_network_patterns(),
            'timeline_analysis': self.generate_timeline_analysis(),
            'evidence_validation': self.generate_evidence_validation_report()
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Analysis report exported: {output_file}")


def main():
    """Main analysis interface"""
    print("🔍 Operation Gladio Analysis System")
    print("===================================")

    analyzer = GladioAnalyzer()

    while True:
        print("\n" + "="*50)
        print("📊 ANALYSIS OPTIONS")
        print("="*50)
        print("1. Network Analysis")
        print("2. Timeline Analysis")
        print("3. Evidence Validation Report")
        print("4. Export Complete Analysis")
        print("0. Exit")
        print("-"*50)

        choice = input("Select analysis: ").strip()

        if choice == "1":
            network_analysis = analyzer.analyze_network_patterns()
            print(f"\n🕸️  Network Analysis Results:")
            print(f"  Total entities: {network_analysis['network_size']['total_entities']}")
            print(f"  Total relationships: {network_analysis['network_size']['total_relationships']}")
            print(f"  Key entities: {len(network_analysis['key_entities']['highest_centrality'])}")

        elif choice == "2":
            timeline_analysis = analyzer.generate_timeline_analysis()
            print(f"\n📅 Timeline Analysis Results:")
            print(f"  Total events: {timeline_analysis['total_events']}")
            print(f"  Events per year: {timeline_analysis['event_density']['events_per_year']:.2f}")

        elif choice == "3":
            validation_report = analyzer.generate_evidence_validation_report()
            print(f"\n🔍 Evidence Validation Report:")
            print(f"  Total evidence: {validation_report['total_evidence_pieces']}")
            print(f"  Validation rate: {validation_report['validation_rate']:.1f}%")
            print(f"  Quality: {validation_report['quality_assessment']}")

        elif choice == "4":
            analyzer.export_analysis_report()

        elif choice == "0":
            print("📊 Analysis session ended.")
            break

        else:
            print("❌ Invalid option.")


if __name__ == "__main__":
    main()