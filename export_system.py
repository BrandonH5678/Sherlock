#!/usr/bin/env python3
"""
Export System for Sherlock
Multi-format export capabilities: Markdown, JSON, Mermaid diagrams, CSV
"""

import csv
import json
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from enum import Enum

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from query_system import HybridQuerySystem, QueryResult, SearchQuery, QueryType
from answer_synthesis import AnswerSynthesizer, AnswerSynthesis
from evidence_database import EvidenceDatabase


class ExportFormat(Enum):
    """Supported export formats"""
    MARKDOWN = "markdown"
    JSON = "json"
    MERMAID = "mermaid"
    CSV = "csv"
    HTML = "html"


class ExportSystem:
    """Multi-format export system for Sherlock analysis results"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.query_system = HybridQuerySystem(db_path)
        self.synthesizer = AnswerSynthesizer(db_path)

    def export_synthesis(self, synthesis: AnswerSynthesis, format_type: ExportFormat, output_path: str) -> bool:
        """Export synthesis results in specified format"""

        print(f"📄 Exporting synthesis to {format_type.value}: {output_path}")
        start_time = time.time()

        try:
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            if format_type == ExportFormat.MARKDOWN:
                content = self._export_synthesis_markdown(synthesis)
            elif format_type == ExportFormat.JSON:
                content = self._export_synthesis_json(synthesis)
            elif format_type == ExportFormat.MERMAID:
                content = self._export_synthesis_mermaid(synthesis)
            elif format_type == ExportFormat.CSV:
                content = self._export_synthesis_csv(synthesis)
            elif format_type == ExportFormat.HTML:
                content = self._export_synthesis_html(synthesis)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")

            # Write to file
            if format_type == ExportFormat.CSV:
                # CSV content is already structured for writing
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    content(f)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            processing_time = time.time() - start_time
            print(f"✅ Export completed in {processing_time:.2f}s")
            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def export_query_results(self, results: List[QueryResult], query: SearchQuery,
                           format_type: ExportFormat, output_path: str) -> bool:
        """Export raw query results in specified format"""

        print(f"📄 Exporting {len(results)} query results to {format_type.value}: {output_path}")
        start_time = time.time()

        try:
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            if format_type == ExportFormat.MARKDOWN:
                content = self._export_results_markdown(results, query)
            elif format_type == ExportFormat.JSON:
                content = self._export_results_json(results, query)
            elif format_type == ExportFormat.CSV:
                content = self._export_results_csv(results, query)
            elif format_type == ExportFormat.HTML:
                content = self._export_results_html(results, query)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")

            # Write to file
            if format_type == ExportFormat.CSV:
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    content(f)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            processing_time = time.time() - start_time
            print(f"✅ Export completed in {processing_time:.2f}s")
            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def _export_synthesis_markdown(self, synthesis: AnswerSynthesis) -> str:
        """Export synthesis as Markdown"""

        md_lines = []

        # Header
        md_lines.append(f"# Sherlock Analysis: {synthesis.query}")
        md_lines.append("")
        md_lines.append(f"**Query Type:** {synthesis.query_type}")
        md_lines.append(f"**Generated:** {synthesis.generated_at}")
        md_lines.append(f"**Processing Time:** {synthesis.processing_time:.2f}s")
        md_lines.append(f"**Overall Confidence:** {synthesis.overall_confidence:.1%}")
        md_lines.append(f"**Sources Analyzed:** {synthesis.total_sources}")
        md_lines.append(f"**Claims Extracted:** {synthesis.total_claims}")
        md_lines.append("")

        # Executive Summary
        md_lines.append("## Executive Summary")
        md_lines.append(synthesis.synthesis_notes)
        md_lines.append("")

        # The 5 blocks
        blocks = [
            ("## 1. ESTABLISHED FACTS", synthesis.established),
            ("## 2. CONTESTED/DISPUTED", synthesis.contested),
            ("## 3. ANALYTICAL REASONING", synthesis.why),
            ("## 4. ANALYTICAL FLAGS", synthesis.flags),
            ("## 5. RECOMMENDED NEXT STEPS", synthesis.next_steps)
        ]

        for title, block in blocks:
            md_lines.append(title)
            md_lines.append(f"**Confidence:** {block.confidence:.1%}")
            md_lines.append("")
            md_lines.append(block.content)
            md_lines.append("")

            # Add sources if available
            if block.sources:
                md_lines.append("### Sources")
                for i, source in enumerate(block.sources, 1):
                    source_line = f"{i}. {source.get('title', 'Unknown Source')}"
                    if source.get('confidence'):
                        source_line += f" (Confidence: {source['confidence']:.1%})"
                    if source.get('timecode'):
                        source_line += f" [Timecode: {source['timecode']:.1f}s]"
                    md_lines.append(source_line)
                md_lines.append("")

        # Metadata
        md_lines.append("## Metadata")
        md_lines.append(f"- **Total Processing Time:** {synthesis.processing_time:.2f} seconds")
        md_lines.append(f"- **Evidence Sources:** {synthesis.total_sources}")
        md_lines.append(f"- **Total Claims:** {synthesis.total_claims}")
        md_lines.append(f"- **Synthesis Method:** 5-Block Structured Analysis")
        md_lines.append("")

        # Footer
        md_lines.append("---")
        md_lines.append("*Generated by Sherlock Evidence Analysis System*")

        return "\n".join(md_lines)

    def _export_synthesis_json(self, synthesis: AnswerSynthesis) -> str:
        """Export synthesis as JSON"""

        # Convert synthesis to dictionary
        synthesis_dict = asdict(synthesis)

        # Add export metadata
        synthesis_dict['export_metadata'] = {
            'exported_at': datetime.now().isoformat(),
            'export_format': 'json',
            'schema_version': '1.0'
        }

        return json.dumps(synthesis_dict, indent=2, default=str)

    def _export_synthesis_mermaid(self, synthesis: AnswerSynthesis) -> str:
        """Export synthesis as Mermaid diagram"""

        mermaid_lines = []

        # Start diagram
        mermaid_lines.append("graph TD")
        mermaid_lines.append("    %% Sherlock Analysis Flow Diagram")
        mermaid_lines.append(f"    %% Query: {synthesis.query}")
        mermaid_lines.append("")

        # Query node
        query_id = "Q[\"🔍 Query<br/>" + synthesis.query[:30] + "...\"]"
        mermaid_lines.append(f"    {query_id}")
        mermaid_lines.append("")

        # Block nodes with confidence colors
        def confidence_color(conf):
            if conf >= 0.8:
                return "fill:#90EE90"  # Light green
            elif conf >= 0.6:
                return "fill:#FFE4B5"  # Light orange
            elif conf >= 0.4:
                return "fill:#FFA07A"  # Light coral
            else:
                return "fill:#F08080"  # Light salmon

        # Established block
        est_conf = synthesis.established.confidence
        mermaid_lines.append(f"    E[\"✅ ESTABLISHED<br/>Confidence: {est_conf:.1%}\"]")
        mermaid_lines.append(f"    style E {confidence_color(est_conf)}")

        # Contested block
        con_conf = synthesis.contested.confidence
        mermaid_lines.append(f"    C[\"⚠️ CONTESTED<br/>Confidence: {con_conf:.1%}\"]")
        mermaid_lines.append(f"    style C {confidence_color(con_conf)}")

        # Why block
        why_conf = synthesis.why.confidence
        mermaid_lines.append(f"    W[\"🧠 REASONING<br/>Confidence: {why_conf:.1%}\"]")
        mermaid_lines.append(f"    style W {confidence_color(why_conf)}")

        # Flags block
        flag_conf = synthesis.flags.confidence
        mermaid_lines.append(f"    F[\"🚩 FLAGS<br/>Confidence: {flag_conf:.1%}\"]")
        mermaid_lines.append(f"    style F {confidence_color(flag_conf)}")

        # Next steps block
        next_conf = synthesis.next_steps.confidence
        mermaid_lines.append(f"    N[\"➡️ NEXT STEPS<br/>Confidence: {next_conf:.1%}\"]")
        mermaid_lines.append(f"    style N {confidence_color(next_conf)}")

        # Overall synthesis
        overall_conf = synthesis.overall_confidence
        mermaid_lines.append(f"    S[\"📊 SYNTHESIS<br/>Overall: {overall_conf:.1%}<br/>Sources: {synthesis.total_sources}\"]")
        mermaid_lines.append(f"    style S {confidence_color(overall_conf)}")

        # Connections
        mermaid_lines.append("")
        mermaid_lines.append("    %% Flow connections")
        mermaid_lines.append("    Q --> E")
        mermaid_lines.append("    Q --> C")
        mermaid_lines.append("    Q --> W")
        mermaid_lines.append("    E --> S")
        mermaid_lines.append("    C --> S")
        mermaid_lines.append("    W --> S")
        mermaid_lines.append("    W --> F")
        mermaid_lines.append("    S --> N")

        return "\n".join(mermaid_lines)

    def _export_synthesis_csv(self, synthesis: AnswerSynthesis) -> callable:
        """Export synthesis as CSV (returns writer function)"""

        def write_csv(file_handle):
            writer = csv.writer(file_handle)

            # Header
            writer.writerow([
                'Block Type', 'Title', 'Content', 'Confidence', 'Source Count', 'Metadata'
            ])

            # Data rows
            blocks = [
                synthesis.established,
                synthesis.contested,
                synthesis.why,
                synthesis.flags,
                synthesis.next_steps
            ]

            for block in blocks:
                writer.writerow([
                    block.block_type,
                    block.title,
                    block.content[:500] + "..." if len(block.content) > 500 else block.content,
                    f"{block.confidence:.1%}",
                    len(block.sources),
                    json.dumps(block.metadata)
                ])

            # Summary row
            writer.writerow([])
            writer.writerow(['SUMMARY', 'Query', synthesis.query, f"{synthesis.overall_confidence:.1%}",
                           synthesis.total_sources, f"Claims: {synthesis.total_claims}"])

        return write_csv

    def _export_synthesis_html(self, synthesis: AnswerSynthesis) -> str:
        """Export synthesis as HTML"""

        html_lines = []

        # HTML header
        html_lines.append("<!DOCTYPE html>")
        html_lines.append("<html lang='en'>")
        html_lines.append("<head>")
        html_lines.append("    <meta charset='UTF-8'>")
        html_lines.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_lines.append(f"    <title>Sherlock Analysis: {synthesis.query}</title>")
        html_lines.append("    <style>")
        html_lines.append("""
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        .block { margin-bottom: 30px; padding: 20px; border-left: 4px solid #007cba; background: #f9f9f9; }
        .confidence { display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
        .conf-high { background: #28a745; }
        .conf-medium { background: #ffc107; color: black; }
        .conf-low { background: #dc3545; }
        .sources { margin-top: 15px; font-size: 0.9em; }
        .metadata { background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 30px; }
        """)
        html_lines.append("    </style>")
        html_lines.append("</head>")
        html_lines.append("<body>")

        # Header section
        html_lines.append("<div class='header'>")
        html_lines.append(f"<h1>Sherlock Analysis: {synthesis.query}</h1>")
        html_lines.append(f"<p><strong>Query Type:</strong> {synthesis.query_type}</p>")
        html_lines.append(f"<p><strong>Generated:</strong> {synthesis.generated_at}</p>")
        html_lines.append(f"<p><strong>Processing Time:</strong> {synthesis.processing_time:.2f}s</p>")

        # Overall confidence badge
        conf_class = "conf-high" if synthesis.overall_confidence >= 0.7 else "conf-medium" if synthesis.overall_confidence >= 0.4 else "conf-low"
        html_lines.append(f"<span class='confidence {conf_class}'>Overall Confidence: {synthesis.overall_confidence:.1%}</span>")
        html_lines.append("</div>")

        # The 5 blocks
        blocks = [
            ("ESTABLISHED FACTS", synthesis.established, "🏛️"),
            ("CONTESTED/DISPUTED", synthesis.contested, "⚖️"),
            ("ANALYTICAL REASONING", synthesis.why, "🧠"),
            ("ANALYTICAL FLAGS", synthesis.flags, "🚩"),
            ("RECOMMENDED NEXT STEPS", synthesis.next_steps, "➡️")
        ]

        for title, block, emoji in blocks:
            conf_class = "conf-high" if block.confidence >= 0.7 else "conf-medium" if block.confidence >= 0.4 else "conf-low"

            html_lines.append("<div class='block'>")
            html_lines.append(f"<h2>{emoji} {title}</h2>")
            html_lines.append(f"<span class='confidence {conf_class}'>Confidence: {block.confidence:.1%}</span>")

            # Content (preserve line breaks)
            content_html = block.content.replace('\n', '<br>')
            html_lines.append(f"<p>{content_html}</p>")

            # Sources
            if block.sources:
                html_lines.append("<div class='sources'>")
                html_lines.append("<strong>Sources:</strong>")
                html_lines.append("<ul>")
                for source in block.sources:
                    source_text = source.get('title', 'Unknown Source')
                    if source.get('confidence'):
                        source_text += f" (Confidence: {source['confidence']:.1%})"
                    if source.get('timecode'):
                        source_text += f" [Timecode: {source['timecode']:.1f}s]"
                    html_lines.append(f"<li>{source_text}</li>")
                html_lines.append("</ul>")
                html_lines.append("</div>")

            html_lines.append("</div>")

        # Metadata section
        html_lines.append("<div class='metadata'>")
        html_lines.append("<h3>Analysis Metadata</h3>")
        html_lines.append(f"<p><strong>Sources Analyzed:</strong> {synthesis.total_sources}</p>")
        html_lines.append(f"<p><strong>Claims Extracted:</strong> {synthesis.total_claims}</p>")
        html_lines.append(f"<p><strong>Synthesis Notes:</strong> {synthesis.synthesis_notes}</p>")
        html_lines.append("</div>")

        # Footer
        html_lines.append("<footer style='margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; text-align: center; color: #666;'>")
        html_lines.append("<p><em>Generated by Sherlock Evidence Analysis System</em></p>")
        html_lines.append("</footer>")

        html_lines.append("</body>")
        html_lines.append("</html>")

        return "\n".join(html_lines)

    def _export_results_markdown(self, results: List[QueryResult], query: SearchQuery) -> str:
        """Export query results as Markdown"""

        md_lines = []

        # Header
        md_lines.append(f"# Query Results: {query.query_text}")
        md_lines.append("")
        md_lines.append(f"**Query Type:** {query.query_type.value}")
        md_lines.append(f"**Results Found:** {len(results)}")
        md_lines.append(f"**Generated:** {datetime.now().isoformat()}")
        md_lines.append("")

        # Results
        for i, result in enumerate(results, 1):
            md_lines.append(f"## Result {i}: {result.title}")
            md_lines.append(f"**Type:** {result.result_type}")
            md_lines.append(f"**Confidence:** {result.confidence:.1%}")
            md_lines.append(f"**Relevance:** {result.relevance_score:.1%}")
            md_lines.append("")
            md_lines.append(f"**Content:** {result.content}")
            md_lines.append("")

            if result.timecode:
                md_lines.append(f"**Timecode:** {result.timecode:.1f}s")
                md_lines.append("")

            if result.context:
                md_lines.append(f"**Context:** {result.context}")
                md_lines.append("")

            # Source info
            md_lines.append("**Source Information:**")
            for key, value in result.source_info.items():
                if value:
                    md_lines.append(f"- {key.replace('_', ' ').title()}: {value}")
            md_lines.append("")

        return "\n".join(md_lines)

    def _export_results_json(self, results: List[QueryResult], query: SearchQuery) -> str:
        """Export query results as JSON"""

        export_data = {
            'query': {
                'text': query.query_text,
                'type': query.query_type.value,
                'limit': query.limit,
                'sort_by': query.sort_by
            },
            'results': [asdict(result) for result in results],
            'metadata': {
                'result_count': len(results),
                'exported_at': datetime.now().isoformat(),
                'export_format': 'json'
            }
        }

        return json.dumps(export_data, indent=2, default=str)

    def _export_results_csv(self, results: List[QueryResult], query: SearchQuery) -> callable:
        """Export query results as CSV (returns writer function)"""

        def write_csv(file_handle):
            writer = csv.writer(file_handle)

            # Header
            writer.writerow([
                'Result ID', 'Type', 'Title', 'Content', 'Confidence', 'Relevance',
                'Source Title', 'Speaker', 'Timecode', 'Context'
            ])

            # Data rows
            for result in results:
                writer.writerow([
                    result.result_id,
                    result.result_type,
                    result.title,
                    result.content[:500] + "..." if len(result.content) > 500 else result.content,
                    f"{result.confidence:.1%}",
                    f"{result.relevance_score:.1%}",
                    result.source_info.get('source_title', ''),
                    result.source_info.get('speaker_name', ''),
                    result.timecode if result.timecode else '',
                    result.context[:200] + "..." if result.context and len(result.context) > 200 else result.context or ''
                ])

        return write_csv

    def _export_results_html(self, results: List[QueryResult], query: SearchQuery) -> str:
        """Export query results as HTML"""

        html_lines = []

        # HTML header
        html_lines.append("<!DOCTYPE html>")
        html_lines.append("<html lang='en'>")
        html_lines.append("<head>")
        html_lines.append("    <meta charset='UTF-8'>")
        html_lines.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_lines.append(f"    <title>Query Results: {query.query_text}</title>")
        html_lines.append("    <style>")
        html_lines.append("""
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        .result { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .confidence { display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-size: 0.9em; }
        .conf-high { background: #28a745; }
        .conf-medium { background: #ffc107; color: black; }
        .conf-low { background: #dc3545; }
        .metadata { font-size: 0.9em; color: #666; margin-top: 10px; }
        """)
        html_lines.append("    </style>")
        html_lines.append("</head>")
        html_lines.append("<body>")

        # Header
        html_lines.append("<div class='header'>")
        html_lines.append(f"<h1>Query Results: {query.query_text}</h1>")
        html_lines.append(f"<p><strong>Query Type:</strong> {query.query_type.value}</p>")
        html_lines.append(f"<p><strong>Results Found:</strong> {len(results)}</p>")
        html_lines.append("</div>")

        # Results
        for i, result in enumerate(results, 1):
            conf_class = "conf-high" if result.confidence >= 0.7 else "conf-medium" if result.confidence >= 0.4 else "conf-low"
            rel_class = "conf-high" if result.relevance_score >= 0.7 else "conf-medium" if result.relevance_score >= 0.4 else "conf-low"

            html_lines.append("<div class='result'>")
            html_lines.append(f"<h3>Result {i}: {result.title}</h3>")
            html_lines.append(f"<span class='confidence {conf_class}'>Confidence: {result.confidence:.1%}</span> ")
            html_lines.append(f"<span class='confidence {rel_class}'>Relevance: {result.relevance_score:.1%}</span>")

            html_lines.append(f"<p><strong>Content:</strong> {result.content}</p>")

            if result.timecode:
                html_lines.append(f"<p><strong>Timecode:</strong> {result.timecode:.1f}s</p>")

            if result.context:
                html_lines.append(f"<p><strong>Context:</strong> {result.context}</p>")

            # Metadata
            html_lines.append("<div class='metadata'>")
            html_lines.append(f"<p><strong>Type:</strong> {result.result_type} | <strong>Source:</strong> {result.source_info.get('source_title', 'Unknown')}")
            if result.source_info.get('speaker_name'):
                html_lines.append(f" | <strong>Speaker:</strong> {result.source_info['speaker_name']}")
            html_lines.append("</p>")
            html_lines.append("</div>")

            html_lines.append("</div>")

        html_lines.append("</body>")
        html_lines.append("</html>")

        return "\n".join(html_lines)

    def close(self):
        """Close database connections"""
        self.db.close()
        self.query_system.close()
        self.synthesizer.close()


def main():
    """CLI interface for export system"""
    if len(sys.argv) < 4:
        print("Export System for Sherlock")
        print("Usage:")
        print("  python export_system.py synthesis '<query_text>' <format> <output_path> [query_type]")
        print("  python export_system.py query '<query_text>' <format> <output_path> [query_type] [limit]")
        print("")
        print("Formats: markdown, json, mermaid, csv, html")
        sys.exit(1)

    command = sys.argv[1].lower()
    query_text = sys.argv[2]
    format_str = sys.argv[3].lower()
    output_path = sys.argv[4]

    try:
        export_format = ExportFormat(format_str)
    except ValueError:
        print(f"❌ Invalid format: {format_str}")
        print("Supported formats: markdown, json, mermaid, csv, html")
        sys.exit(1)

    export_system = ExportSystem()

    try:
        if command == "synthesis":
            query_type = QueryType(sys.argv[5]) if len(sys.argv) > 5 else QueryType.FULL_TEXT

            query = SearchQuery(
                query_text=query_text,
                query_type=query_type,
                filters={},
                date_range=None,
                speaker_filter=None,
                source_filter=None,
                entity_filter=None,
                limit=20,
                sort_by="relevance",
                include_context=True
            )

            # Generate synthesis
            synthesis = export_system.synthesizer.synthesize_answer(query)

            # Export synthesis
            success = export_system.export_synthesis(synthesis, export_format, output_path)
            if success:
                print(f"✅ Synthesis exported to: {output_path}")
            else:
                print(f"❌ Failed to export synthesis")

        elif command == "query":
            query_type = QueryType(sys.argv[5]) if len(sys.argv) > 5 else QueryType.FULL_TEXT
            limit = int(sys.argv[6]) if len(sys.argv) > 6 else 10

            query = SearchQuery(
                query_text=query_text,
                query_type=query_type,
                filters={},
                date_range=None,
                speaker_filter=None,
                source_filter=None,
                entity_filter=None,
                limit=limit,
                sort_by="relevance",
                include_context=True
            )

            # Execute query
            results = export_system.query_system.execute_query(query)

            # Export results
            success = export_system.export_query_results(results, query, export_format, output_path)
            if success:
                print(f"✅ Query results exported to: {output_path}")
            else:
                print(f"❌ Failed to export query results")

        else:
            print(f"❌ Unknown command: {command}")

    finally:
        export_system.close()


if __name__ == "__main__":
    main()