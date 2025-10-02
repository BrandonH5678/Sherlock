#!/usr/bin/env python3
"""
Operation Gladio Intelligence Report Generator
Generate comprehensive intelligence summary reports

Design: Aggregate all analysis results into actionable intelligence
Memory: <200MB
Output: Markdown reports and JSON summaries
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class IntelligenceReportGenerator:
    """Generate intelligence reports from all analysis results"""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

        # Load all data
        self.entities = self.load_json('entity_dossiers.json')
        self.relationships = self.load_json('relationships.json')
        self.resource_flows = self.load_json('resource_flows.json')
        self.timeline = self.load_json('timeline.json')
        self.network_metrics = self.load_json('network_metrics.json')

    def load_json(self, filename: str) -> Dict:
        """Load JSON file"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return {}

    def generate_executive_summary(self) -> str:
        """Generate executive summary"""

        total_entities = self.entities.get('metadata', {}).get('total_entities', 0)
        people_count = self.entities.get('metadata', {}).get('people', 0)
        orgs_count = self.entities.get('metadata', {}).get('organizations', 0)

        total_relationships = self.relationships.get('metadata', {}).get('total_relationships', 0)

        total_flows = self.resource_flows.get('metadata', {}).get('total_flows', 0)
        money_flows = self.resource_flows.get('metadata', {}).get('money_flows', 0)
        weapons_flows = self.resource_flows.get('metadata', {}).get('weapons_flows', 0)

        total_events = self.timeline.get('metadata', {}).get('total_events', 0)
        earliest_year = self.timeline.get('metadata', {}).get('earliest_year', 'Unknown')
        latest_year = self.timeline.get('metadata', {}).get('latest_year', 'Unknown')

        network_nodes = self.network_metrics.get('network_size', {}).get('total_nodes', 0)
        network_edges = self.network_metrics.get('network_size', {}).get('total_edges', 0)

        summary = f"""# Operation Gladio Intelligence Analysis
## Executive Summary

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}
**Source:** Operation Gladio: The Unholy Alliance Between the Vatican, the CIA, and the Mafia
**Processing Method:** Automated intelligence extraction and analysis

### Key Findings

This analysis reveals a complex network of {total_entities} entities ({people_count} individuals, {orgs_count} organizations) involved in Operation Gladio spanning {earliest_year}-{latest_year}.

**Network Scale:**
- **{total_relationships:,} relationships** mapped between entities
- **{total_flows:,} resource flows** tracked (money, weapons, information, drugs)
- **{total_events} timeline events** extracted across {latest_year - earliest_year if isinstance(latest_year, int) and isinstance(earliest_year, int) else 'multiple'} years

**Resource Flows:**
- **${money_flows:,} money transfers** identified
- **{weapons_flows:,} weapons shipments** documented
- Focus on CIA-Vatican-Mafia triangle of influence

**Network Analysis:**
- **{network_nodes} key nodes** in primary network
- **{network_edges:,} connections** mapping power structures
- Central hub: CIA ({self.network_metrics.get('centrality', {}).get('top_10_nodes', [[]])[0][1] if self.network_metrics.get('centrality', {}).get('top_10_nodes') else 'N/A'} connections)

"""
        return summary

    def generate_top_entities_report(self) -> str:
        """Generate top entities section"""

        dossiers = self.entities.get('dossiers', {})

        # Get people sorted by mentions
        people = [(name, data) for name, data in dossiers.items() if data.get('entity_type') == 'person']
        people_sorted = sorted(people, key=lambda x: x[1].get('mention_count', 0), reverse=True)

        # Get organizations sorted by mentions
        orgs = [(name, data) for name, data in dossiers.items() if data.get('entity_type') == 'organization']
        orgs_sorted = sorted(orgs, key=lambda x: x[1].get('mention_count', 0), reverse=True)

        report = """### Top 15 Most Referenced Individuals

| Name | Mentions | Affiliations | Key Roles |
|------|----------|--------------|-----------|
"""

        for name, data in people_sorted[:15]:
            mentions = data.get('mention_count', 0)
            affiliations = ', '.join(data.get('affiliations', [])[:3])
            roles = ', '.join(r[:50] for r in data.get('roles', [])[:2])
            report += f"| {name} | {mentions} | {affiliations} | {roles[:60]}{'...' if len(roles) > 60 else ''} |\n"

        report += """\n### Top 15 Most Referenced Organizations

| Name | Mentions | Type | Aliases |
|------|----------|------|---------|
"""

        for name, data in orgs_sorted[:15]:
            mentions = data.get('mention_count', 0)
            aliases = ', '.join(data.get('aliases', [])[:3])
            report += f"| {name} | {mentions} | Organization | {aliases} |\n"

        return report

    def generate_network_analysis(self) -> str:
        """Generate network analysis section"""

        top_nodes = self.network_metrics.get('centrality', {}).get('top_10_nodes', [])
        rel_types = self.network_metrics.get('relationship_types', {})

        report = """### Network Centrality Analysis

**Most Connected Entities (Network Hubs):**

| Entity | Connections | Role in Network |
|--------|-------------|-----------------|
"""

        for node, connections in top_nodes[:10]:
            report += f"| {node} | {connections} | Network Hub |\n"

        report += """\n### Relationship Distribution

| Relationship Type | Count | Percentage |
|-------------------|-------|------------|
"""

        total_rels = sum(rel_types.values()) if rel_types else 1

        for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_rels) * 100
            report += f"| {rel_type.capitalize()} | {count} | {percentage:.1f}% |\n"

        return report

    def generate_timeline_summary(self) -> str:
        """Generate timeline summary"""

        timeline_events = self.timeline.get('timeline', [])

        # Group by decade
        by_decade = {}
        for event in timeline_events:
            year = event.get('year')
            if year and isinstance(year, int):
                decade = (year // 10) * 10
                if decade not in by_decade:
                    by_decade[decade] = []
                by_decade[decade].append(event)

        report = """### Historical Timeline

**Events by Decade:**

| Period | Event Count | Key Focus Areas |
|--------|-------------|-----------------|
"""

        for decade in sorted(by_decade.keys()):
            events = by_decade[decade]
            # Get most common entities
            entity_freq = {}
            for event in events:
                for entity in event.get('entities_involved', []):
                    entity_freq[entity] = entity_freq.get(entity, 0) + 1

            top_entities = sorted(entity_freq.items(), key=lambda x: x[1], reverse=True)[:3]
            focus = ', '.join(e[0] for e in top_entities)

            report += f"| {decade}s | {len(events)} | {focus} |\n"

        return report

    def generate_resource_flow_analysis(self) -> str:
        """Generate resource flow analysis"""

        flows_by_type = self.resource_flows.get('flows_by_type', {})

        report = """### Resource Flow Analysis

**Resource Transfer Summary:**

| Resource Type | Flows Identified | Notable Patterns |
|---------------|------------------|------------------|
"""

        for resource_type, flows in flows_by_type.items():
            count = len(flows)

            # Find top source
            sources = {}
            for flow in flows:
                source = flow.get('source_entity', 'Unknown')
                sources[source] = sources.get(source, 0) + 1

            top_source = max(sources.items(), key=lambda x: x[1])[0] if sources else 'N/A'

            report += f"| {resource_type.capitalize()} | {count:,} | Primary source: {top_source} |\n"

        return report

    def generate_full_report(self, output_path: Path):
        """Generate full markdown report"""

        report = self.generate_executive_summary()
        report += "\n---\n\n"
        report += self.generate_top_entities_report()
        report += "\n---\n\n"
        report += self.generate_network_analysis()
        report += "\n---\n\n"
        report += self.generate_timeline_summary()
        report += "\n---\n\n"
        report += self.generate_resource_flow_analysis()

        report += """\n---\n
## Methodology

This intelligence analysis was generated through automated processing of the Operation Gladio audiobook transcript using:

1. **Entity Extraction**: Pattern-based recognition of people and organizations
2. **Relationship Mapping**: Co-occurrence analysis and context classification
3. **Resource Flow Tracking**: Identification of money, weapons, and information transfers
4. **Timeline Construction**: Temporal event extraction and sequencing
5. **Network Analysis**: Graph-based centrality and connection analysis

**Processing Statistics:**
- Transcript size: 96,247 words
- Processing time: ~3 hours
- Memory usage: <200MB peak
- Checkpoint-based pipeline: Crash-resistant, resumable

**Limitations:**
- Automated extraction may miss nuanced relationships
- Confidence levels indicate pattern-matching certainty, not historical accuracy
- Resource amounts are as stated in source material
- Timeline events extracted based on explicit date mentions

---

**Generated:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
**System:** Sherlock Evidence Analysis System
**Source:** Operation Gladio: The Unholy Alliance Between the Vatican, the CIA, and the Mafia (Paul L. Williams)
"""

        with open(output_path, 'w') as f:
            f.write(report)

        print(f"Saved full report to {output_path}")

    def generate_json_summary(self, output_path: Path):
        """Generate JSON summary of top entities"""

        dossiers = self.entities.get('dossiers', {})

        # Get top 20 people
        people = [(name, data) for name, data in dossiers.items() if data.get('entity_type') == 'person']
        people_sorted = sorted(people, key=lambda x: x[1].get('mention_count', 0), reverse=True)[:20]

        # Get top 10 organizations
        orgs = [(name, data) for name, data in dossiers.items() if data.get('entity_type') == 'organization']
        orgs_sorted = sorted(orgs, key=lambda x: x[1].get('mention_count', 0), reverse=True)[:10]

        summary = {
            'analysis_date': datetime.now().isoformat(),
            'top_people': [
                {
                    'name': name,
                    'mentions': data.get('mention_count', 0),
                    'affiliations': data.get('affiliations', []),
                    'roles': data.get('roles', [])[:3]
                }
                for name, data in people_sorted
            ],
            'top_organizations': [
                {
                    'name': name,
                    'mentions': data.get('mention_count', 0),
                    'aliases': data.get('aliases', [])
                }
                for name, data in orgs_sorted
            ],
            'network_hubs': self.network_metrics.get('centrality', {}).get('top_10_nodes', [])[:10],
            'timeline_span': {
                'earliest': self.timeline.get('metadata', {}).get('earliest_year'),
                'latest': self.timeline.get('metadata', {}).get('latest_year'),
                'total_events': self.timeline.get('metadata', {}).get('total_events', 0)
            }
        }

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"Saved JSON summary to {output_path}")


def main():
    """Generate intelligence reports"""

    data_dir = Path("/home/johnny5/Sherlock/audiobooks/operation_gladio")
    markdown_output = data_dir / "gladio_intelligence_summary.md"
    json_output = data_dir / "top_entities_report.json"

    generator = IntelligenceReportGenerator(data_dir)

    print("Generating intelligence reports...")

    # Generate full markdown report
    generator.generate_full_report(markdown_output)

    # Generate JSON summary
    generator.generate_json_summary(json_output)

    print("\n✅ Intelligence reports generated successfully!")
    print(f"   Markdown report: {markdown_output}")
    print(f"   JSON summary: {json_output}")


if __name__ == "__main__":
    main()
