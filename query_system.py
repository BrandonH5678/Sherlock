#!/usr/bin/env python3
"""
Hybrid Search and Query System for Sherlock
Advanced query interface with semantic search, filtering, and ranking
"""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import EvidenceDatabase
from analysis_engine import AnalysisEngine
from graph_analysis import GraphAnalysisSystem


class QueryType(Enum):
    """Types of queries supported"""
    FULL_TEXT = "full_text"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    ENTITY = "entity"
    SPEAKER = "speaker"
    SOURCE = "source"
    CONTRADICTION = "contradiction"
    PROPAGANDA = "propaganda"


@dataclass
class QueryResult:
    """Individual query result with ranking and metadata"""
    result_id: str
    result_type: str  # claim, source, speaker, entity
    content: str
    title: str
    confidence: float
    relevance_score: float
    source_info: Dict
    metadata: Dict
    timecode: Optional[float]
    context: str


@dataclass
class SearchQuery:
    """Structured search query with filters and options"""
    query_text: str
    query_type: QueryType
    filters: Dict
    date_range: Optional[Tuple[str, str]]
    speaker_filter: Optional[List[str]]
    source_filter: Optional[List[str]]
    entity_filter: Optional[List[str]]
    limit: int
    sort_by: str  # relevance, date, confidence
    include_context: bool


class HybridQuerySystem:
    """Advanced hybrid search and query system"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.analysis_engine = AnalysisEngine(db_path)
        self.graph_system = GraphAnalysisSystem(db_path)

    def execute_query(self, query: SearchQuery) -> List[QueryResult]:
        """Execute hybrid query with multiple search strategies"""

        print(f"🔍 Executing {query.query_type.value} query: '{query.query_text[:50]}...'")
        start_time = time.time()

        try:
            results = []

            if query.query_type == QueryType.FULL_TEXT:
                results = self._execute_full_text_search(query)
            elif query.query_type == QueryType.SEMANTIC:
                results = self._execute_semantic_search(query)
            elif query.query_type == QueryType.TEMPORAL:
                results = self._execute_temporal_search(query)
            elif query.query_type == QueryType.ENTITY:
                results = self._execute_entity_search(query)
            elif query.query_type == QueryType.SPEAKER:
                results = self._execute_speaker_search(query)
            elif query.query_type == QueryType.SOURCE:
                results = self._execute_source_search(query)
            elif query.query_type == QueryType.CONTRADICTION:
                results = self._execute_contradiction_search(query)
            elif query.query_type == QueryType.PROPAGANDA:
                results = self._execute_propaganda_search(query)

            # Apply filters
            results = self._apply_filters(results, query)

            # Sort results
            results = self._sort_results(results, query.sort_by)

            # Limit results
            results = results[:query.limit]

            processing_time = time.time() - start_time
            print(f"✅ Query completed: {len(results)} results in {processing_time:.2f}s")

            return results

        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return []

    def _execute_full_text_search(self, query: SearchQuery) -> List[QueryResult]:
        """Execute full-text search using FTS5"""

        try:
            # Search claims using FTS5
            claims_results = self.db.search_claims(query.query_text, limit=query.limit * 2)

            results = []
            for claim in claims_results:
                result = QueryResult(
                    result_id=claim['claim_id'],
                    result_type='claim',
                    content=claim['text'],
                    title=f"Claim from {claim.get('source_title', 'Unknown Source')}",
                    confidence=claim.get('confidence', 0.0),
                    relevance_score=self._calculate_text_relevance(query.query_text, claim['text']),
                    source_info={
                        'source_id': claim['source_id'],
                        'source_title': claim.get('source_title', 'Unknown'),
                        'speaker_name': claim.get('speaker_name')
                    },
                    metadata={
                        'claim_type': claim.get('claim_type'),
                        'entities': claim.get('entities', []),
                        'tags': claim.get('tags', [])
                    },
                    timecode=claim.get('start_time'),
                    context=claim.get('context', '')
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Full-text search error: {e}")
            return []

    def _execute_semantic_search(self, query: SearchQuery) -> List[QueryResult]:
        """Execute semantic search (simplified - would use embeddings in production)"""

        try:
            # For now, fall back to enhanced full-text search with entity matching
            results = self._execute_full_text_search(query)

            # Enhance with entity-based semantic matching
            query_entities = self._extract_query_entities(query.query_text)

            for result in results:
                # Boost scores for entity matches
                entity_overlap = len(set(query_entities).intersection(set(result.metadata.get('entities', []))))
                if entity_overlap > 0:
                    result.relevance_score += entity_overlap * 0.2

            return results

        except Exception as e:
            print(f"Semantic search error: {e}")
            return []

    def _execute_temporal_search(self, query: SearchQuery) -> List[QueryResult]:
        """Execute temporal-based search"""

        try:
            results = []

            # Build base query with temporal constraints
            sql_query = """
                SELECT ec.claim_id, ec.text, ec.confidence, ec.start_time, ec.context,
                       es.title as source_title, es.created_at, s.name as speaker_name,
                       ec.entities, ec.tags, ec.claim_type, ec.source_id
                FROM evidence_claims ec
                JOIN evidence_sources es ON ec.source_id = es.source_id
                LEFT JOIN speakers s ON ec.speaker_id = s.speaker_id
                WHERE 1=1
            """

            params = []

            # Add date range filter
            if query.date_range:
                sql_query += " AND es.created_at BETWEEN ? AND ?"
                params.extend(query.date_range)

            # Add text filter if provided
            if query.query_text:
                sql_query += " AND (ec.text LIKE ? OR es.title LIKE ?)"
                search_term = f"%{query.query_text}%"
                params.extend([search_term, search_term])

            sql_query += " ORDER BY es.created_at DESC LIMIT ?"
            params.append(query.limit)

            cursor = self.db.connection.execute(sql_query, params)

            for row in cursor.fetchall():
                claim_id, text, confidence, start_time, context, source_title, created_at, speaker_name, entities_json, tags_json, claim_type, source_id = row

                result = QueryResult(
                    result_id=claim_id,
                    result_type='claim',
                    content=text,
                    title=f"Claim from {source_title} ({created_at[:10]})",
                    confidence=confidence,
                    relevance_score=self._calculate_temporal_relevance(query, created_at),
                    source_info={
                        'source_id': source_id,
                        'source_title': source_title,
                        'speaker_name': speaker_name,
                        'created_at': created_at
                    },
                    metadata={
                        'claim_type': claim_type,
                        'entities': json.loads(entities_json) if entities_json else [],
                        'tags': json.loads(tags_json) if tags_json else []
                    },
                    timecode=start_time,
                    context=context
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Temporal search error: {e}")
            return []

    def _execute_entity_search(self, query: SearchQuery) -> List[QueryResult]:
        """Execute entity-focused search"""

        try:
            # Build entity graph if not already built
            if not self.graph_system.entity_graph:
                self.graph_system.build_entity_graph()

            results = []

            # Search for claims mentioning the query entities
            cursor = self.db.connection.execute("""
                SELECT ec.claim_id, ec.text, ec.confidence, ec.start_time, ec.context,
                       es.title as source_title, s.name as speaker_name,
                       ec.entities, ec.tags, ec.claim_type, ec.source_id
                FROM evidence_claims ec
                JOIN evidence_sources es ON ec.source_id = es.source_id
                LEFT JOIN speakers s ON ec.speaker_id = s.speaker_id
                WHERE ec.entities LIKE ?
                ORDER BY ec.confidence DESC
                LIMIT ?
            """, (f"%{query.query_text}%", query.limit))

            for row in cursor.fetchall():
                claim_id, text, confidence, start_time, context, source_title, speaker_name, entities_json, tags_json, claim_type, source_id = row

                entities = json.loads(entities_json) if entities_json else []
                entity_match_score = self._calculate_entity_relevance(query.query_text, entities)

                result = QueryResult(
                    result_id=claim_id,
                    result_type='claim',
                    content=text,
                    title=f"Entity-related claim from {source_title}",
                    confidence=confidence,
                    relevance_score=entity_match_score,
                    source_info={
                        'source_id': source_id,
                        'source_title': source_title,
                        'speaker_name': speaker_name
                    },
                    metadata={
                        'claim_type': claim_type,
                        'entities': entities,
                        'tags': json.loads(tags_json) if tags_json else [],
                        'entity_matches': [e for e in entities if query.query_text.lower() in e.lower()]
                    },
                    timecode=start_time,
                    context=context
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Entity search error: {e}")
            return []

    def _execute_speaker_search(self, query: SearchQuery) -> List[QueryResult]:
        """Execute speaker-focused search"""

        try:
            # Get claims by speaker
            speaker_claims = []

            if query.speaker_filter:
                for speaker_id in query.speaker_filter:
                    claims = self.db.get_claims_by_speaker(speaker_id)
                    speaker_claims.extend(claims)
            else:
                # Search for speaker by name in query
                cursor = self.db.connection.execute("""
                    SELECT speaker_id FROM speakers
                    WHERE name LIKE ? OR speaker_id LIKE ?
                """, (f"%{query.query_text}%", f"%{query.query_text}%"))

                speaker_ids = [row[0] for row in cursor.fetchall()]
                for speaker_id in speaker_ids:
                    claims = self.db.get_claims_by_speaker(speaker_id)
                    speaker_claims.extend(claims)

            results = []
            for claim in speaker_claims[:query.limit]:
                result = QueryResult(
                    result_id=claim['claim_id'],
                    result_type='claim',
                    content=claim['text'],
                    title=f"Statement by {claim.get('speaker_name', 'Unknown Speaker')}",
                    confidence=claim.get('confidence', 0.0),
                    relevance_score=self._calculate_speaker_relevance(query, claim),
                    source_info={
                        'source_id': claim['source_id'],
                        'source_title': claim.get('source_title', 'Unknown'),
                        'speaker_name': claim.get('speaker_name')
                    },
                    metadata={
                        'claim_type': claim.get('claim_type'),
                        'entities': claim.get('entities', []),
                        'tags': claim.get('tags', [])
                    },
                    timecode=claim.get('start_time'),
                    context=claim.get('context', '')
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Speaker search error: {e}")
            return []

    def _execute_contradiction_search(self, query: SearchQuery) -> List[QueryResult]:
        """Execute contradiction-focused search"""

        try:
            results = []

            # Find contradictions in the database
            cursor = self.db.connection.execute("""
                SELECT er.subject_id, er.object_id, er.confidence, er.evidence,
                       ec1.text as claim1_text, ec2.text as claim2_text,
                       es1.title as source1_title, es2.title as source2_title
                FROM evidence_relationships er
                JOIN evidence_claims ec1 ON er.subject_id = ec1.claim_id
                JOIN evidence_claims ec2 ON er.object_id = ec2.claim_id
                JOIN evidence_sources es1 ON ec1.source_id = es1.source_id
                JOIN evidence_sources es2 ON ec2.source_id = es2.source_id
                WHERE er.relationship_type = 'contradicts'
                ORDER BY er.confidence DESC
                LIMIT ?
            """, (query.limit,))

            for row in cursor.fetchall():
                subject_id, object_id, confidence, evidence, claim1_text, claim2_text, source1_title, source2_title = row

                # Calculate relevance if query text provided
                relevance_score = 1.0
                if query.query_text:
                    relevance_score = max(
                        self._calculate_text_relevance(query.query_text, claim1_text),
                        self._calculate_text_relevance(query.query_text, claim2_text)
                    )

                result = QueryResult(
                    result_id=f"contradiction_{subject_id}_{object_id}",
                    result_type='contradiction',
                    content=f"CONTRADICTION: '{claim1_text[:100]}...' vs '{claim2_text[:100]}...'",
                    title=f"Contradiction between {source1_title} and {source2_title}",
                    confidence=confidence,
                    relevance_score=relevance_score,
                    source_info={
                        'source1_title': source1_title,
                        'source2_title': source2_title
                    },
                    metadata={
                        'claim1_id': subject_id,
                        'claim2_id': object_id,
                        'evidence': evidence,
                        'claim1_text': claim1_text,
                        'claim2_text': claim2_text
                    },
                    timecode=None,
                    context=evidence
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Contradiction search error: {e}")
            return []

    def _execute_propaganda_search(self, query: SearchQuery) -> List[QueryResult]:
        """Execute propaganda-focused search"""

        try:
            results = []

            # Find propaganda flags in the database
            cursor = self.db.connection.execute("""
                SELECT er.subject_id, er.object_id, er.confidence, er.evidence,
                       ec.text, es.title as source_title, s.name as speaker_name
                FROM evidence_relationships er
                JOIN evidence_claims ec ON er.subject_id = ec.claim_id
                JOIN evidence_sources es ON ec.source_id = es.source_id
                LEFT JOIN speakers s ON ec.speaker_id = s.speaker_id
                WHERE er.relationship_type = 'propaganda_flag'
                ORDER BY er.confidence DESC
                LIMIT ?
            """, (query.limit,))

            for row in cursor.fetchall():
                subject_id, object_id, confidence, evidence, claim_text, source_title, speaker_name = row

                # Parse evidence JSON
                try:
                    evidence_data = json.loads(evidence)
                    techniques = evidence_data.get('techniques', [])
                    explanation = evidence_data.get('explanation', '')
                except:
                    techniques = []
                    explanation = evidence

                # Calculate relevance if query text provided
                relevance_score = 1.0
                if query.query_text:
                    relevance_score = self._calculate_text_relevance(query.query_text, claim_text)

                result = QueryResult(
                    result_id=f"propaganda_{subject_id}",
                    result_type='propaganda',
                    content=f"PROPAGANDA ({object_id}): {claim_text}",
                    title=f"Propaganda detected in {source_title}",
                    confidence=confidence,
                    relevance_score=relevance_score,
                    source_info={
                        'source_title': source_title,
                        'speaker_name': speaker_name
                    },
                    metadata={
                        'claim_id': subject_id,
                        'propaganda_type': object_id,
                        'techniques': techniques,
                        'explanation': explanation
                    },
                    timecode=None,
                    context=explanation
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Propaganda search error: {e}")
            return []

    def _apply_filters(self, results: List[QueryResult], query: SearchQuery) -> List[QueryResult]:
        """Apply additional filters to results"""

        filtered_results = results

        # Apply date range filter
        if query.date_range:
            start_date, end_date = query.date_range
            filtered_results = [
                r for r in filtered_results
                if r.source_info.get('created_at', '') >= start_date and
                   r.source_info.get('created_at', '') <= end_date
            ]

        # Apply speaker filter
        if query.speaker_filter:
            filtered_results = [
                r for r in filtered_results
                if r.source_info.get('speaker_name') in query.speaker_filter
            ]

        # Apply source filter
        if query.source_filter:
            filtered_results = [
                r for r in filtered_results
                if r.source_info.get('source_id') in query.source_filter or
                   r.source_info.get('source_title') in query.source_filter
            ]

        # Apply entity filter
        if query.entity_filter:
            filtered_results = [
                r for r in filtered_results
                if any(entity in r.metadata.get('entities', []) for entity in query.entity_filter)
            ]

        return filtered_results

    def _sort_results(self, results: List[QueryResult], sort_by: str) -> List[QueryResult]:
        """Sort results by specified criteria"""

        if sort_by == 'relevance':
            return sorted(results, key=lambda x: x.relevance_score, reverse=True)
        elif sort_by == 'confidence':
            return sorted(results, key=lambda x: x.confidence, reverse=True)
        elif sort_by == 'date':
            return sorted(results, key=lambda x: x.source_info.get('created_at', ''), reverse=True)
        else:
            return results

    def _calculate_text_relevance(self, query_text: str, content: str) -> float:
        """Calculate text relevance score"""

        query_words = set(query_text.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        intersection = query_words.intersection(content_words)
        return len(intersection) / len(query_words)

    def _calculate_temporal_relevance(self, query: SearchQuery, created_at: str) -> float:
        """Calculate temporal relevance score"""

        if not query.date_range:
            return 1.0

        try:
            start_date, end_date = query.date_range
            query_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            content_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

            # Score based on how close to the center of the date range
            range_center = query_start + (query_end - query_start) / 2
            distance = abs((content_date - range_center).days)
            max_distance = (query_end - query_start).days / 2

            if max_distance == 0:
                return 1.0

            return max(0.0, 1.0 - (distance / max_distance))

        except:
            return 0.5  # Default score if date parsing fails

    def _calculate_entity_relevance(self, query_text: str, entities: List[str]) -> float:
        """Calculate entity relevance score"""

        if not entities:
            return 0.0

        query_lower = query_text.lower()
        matches = sum(1 for entity in entities if query_lower in entity.lower() or entity.lower() in query_lower)

        return min(matches / len(entities), 1.0)

    def _calculate_speaker_relevance(self, query: SearchQuery, claim: Dict) -> float:
        """Calculate speaker relevance score"""

        base_score = 1.0

        # Boost score if query text matches claim content
        if query.query_text:
            base_score *= self._calculate_text_relevance(query.query_text, claim.get('text', ''))

        return base_score

    def _extract_query_entities(self, query_text: str) -> List[str]:
        """Extract potential entities from query text"""

        # Simple entity extraction - capitalize words that might be entities
        words = query_text.split()
        entities = []

        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word and len(clean_word) > 2:
                entities.append(clean_word.title())

        return entities

    def close(self):
        """Close database connections"""
        self.db.close()
        self.analysis_engine.close()
        self.graph_system.close()


def main():
    """CLI interface for query system"""
    if len(sys.argv) < 2:
        print("Hybrid Query System for Sherlock")
        print("Usage:")
        print("  python query_system.py search '<query_text>' [type] [limit]")
        print("  python query_system.py temporal '<query_text>' [start_date] [end_date]")
        print("  python query_system.py entity '<entity_name>'")
        print("  python query_system.py contradictions [query_text]")
        print("  python query_system.py propaganda [query_text]")
        sys.exit(1)

    command = sys.argv[1].lower()
    query_system = HybridQuerySystem()

    try:
        if command == "search":
            query_text = sys.argv[2] if len(sys.argv) > 2 else ""
            query_type = QueryType(sys.argv[3]) if len(sys.argv) > 3 else QueryType.FULL_TEXT
            limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10

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

            results = query_system.execute_query(query)

            print(f"\n📊 SEARCH RESULTS ({len(results)} found)")
            print("=" * 60)

            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   Type: {result.result_type.upper()}")
                print(f"   Confidence: {result.confidence:.1%} | Relevance: {result.relevance_score:.1%}")
                print(f"   Content: {result.content[:150]}...")
                if result.timecode:
                    print(f"   Timecode: {result.timecode:.1f}s")

        elif command == "contradictions":
            query_text = sys.argv[2] if len(sys.argv) > 2 else ""

            query = SearchQuery(
                query_text=query_text,
                query_type=QueryType.CONTRADICTION,
                filters={},
                date_range=None,
                speaker_filter=None,
                source_filter=None,
                entity_filter=None,
                limit=10,
                sort_by="confidence",
                include_context=True
            )

            results = query_system.execute_query(query)

            print(f"\n🔍 CONTRADICTIONS FOUND ({len(results)})")
            print("=" * 50)

            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   Confidence: {result.confidence:.1%}")
                print(f"   {result.content}")

        else:
            print(f"❌ Unknown command: {command}")

    finally:
        query_system.close()


if __name__ == "__main__":
    main()