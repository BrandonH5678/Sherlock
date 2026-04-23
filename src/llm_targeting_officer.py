#!/usr/bin/env python3
"""
LLM-Enhanced Targeting Officer

Extends deterministic TargetingOfficer with Qwen-powered intelligence for:
- Strategic priority assessment
- Specific research question generation (not generic URLs)
- Autonomous continuous operation
- Self-assessment and gap identification

Constitutional Authority: J5A_CONSTITUTION.md - Principle 3 (System Viability)
"""

import sys
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append("/home/johnny5/Johny5Alive/j5a-nightshift")

from src.sherlock_targeting_officer import TargetingOfficer, Package, PackageStatus
from llm_gateway import LLMGateway, LLMMode

logger = logging.getLogger(__name__)


@dataclass
class PriorityAssessment:
    """LLM-based priority assessment result"""
    target_id: int
    target_name: str
    recommended_priority: int  # 1-5, where 1=highest
    reasoning: str
    intelligence_gaps: List[str]
    related_targets: List[int]
    assessed_at: datetime


@dataclass
class ResearchQuestion:
    """LLM-generated research question"""
    question: str
    evidence_requirements: List[str]
    expected_intelligence_value: str  # "high", "medium", "low"
    min_sources: int
    estimated_complexity: str  # "simple", "moderate", "complex"


class LLMTargetingOfficer(TargetingOfficer):
    """
    LLM-powered targeting officer that uses Qwen for intelligent priority assessment
    and research question generation.

    Extends deterministic TargetingOfficer with LLM-based intelligence reasoning.
    """

    def __init__(self, db_path: str, llm_gateway: LLMGateway):
        """
        Initialize LLM-Enhanced Targeting Officer

        Args:
            db_path: Path to sherlock.db
            llm_gateway: Configured LLM Gateway for Qwen access
        """
        super().__init__(db_path)
        self.llm = llm_gateway
        self.base_path = Path("/home/johnny5/Johny5Alive/j5a-nightshift")

        # Initialize autonomous cycle tracking
        self._init_autonomous_tracking()

        logger.info("LLM-Enhanced Targeting Officer initialized")

    def _init_autonomous_tracking(self):
        """Initialize autonomous cycle tracking table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autonomous_cycles (
                cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_number INTEGER,
                start_time DATETIME,
                end_time DATETIME,
                targets_assessed INTEGER,
                priorities_updated INTEGER,
                jobs_created INTEGER,
                jobs_completed INTEGER,
                gaps_identified INTEGER,
                thermal_max REAL,
                status TEXT DEFAULT 'running'
            )
        ''')

        conn.commit()
        conn.close()

    def _detect_mosaic_indicators(self, target: Dict) -> Dict:
        """
        Detect if target qualifies for mosaic intelligence strategy.

        Mosaic Indicators:
        - High strategic importance (connections to classified programs, key historical events)
        - Limited direct evidence BUT evidence of deliberate obscuration
        - Critical to understanding broader patterns

        Returns: {
            'is_mosaic_target': bool,
            'indicators': List[str],
            'reasoning': str
        }
        """
        indicators = []

        # Check target metadata for mosaic signals
        target_name = target.get('name', '').lower()
        target_type = target.get('target_type', '')
        metadata = target.get('metadata', {})

        # Known mosaic targets from strategy document
        mosaic_keywords = [
            'bahnson', 'brown', 'electrogravitics', 'antigravity',
            'pat price', 'price', 'remote viewing', 's-force', 'covert',
            'classified', 'obscured', 'suppressed', 'hidden program',
            'tesla', 'electrokinetic', 'propulsion'
        ]

        for keyword in mosaic_keywords:
            if keyword in target_name:
                indicators.append(f"Target name contains mosaic keyword: '{keyword}'")
                break  # Only count this once

        # Check for obscuration indicators in metadata
        if isinstance(metadata, dict):
            if metadata.get('classified_period'):
                indicators.append("Has classified work period")
            if metadata.get('connections_to_classified_programs'):
                indicators.append("Documented connections to classified programs")

        # Check target type for obscuration patterns
        if target_type in ['program', 'organization', 'operation']:
            if any(k in target_name for k in ['classified', 'covert', 'hidden', 'suppressed']):
                indicators.append("Program/organization with obscuration indicators")

        is_mosaic = len(indicators) > 0

        return {
            'is_mosaic_target': is_mosaic,
            'indicators': indicators,
            'reasoning': '; '.join(indicators) if is_mosaic else 'No mosaic indicators detected'
        }

    def _create_podcast_processing_job(self, target: Dict) -> Dict:
        """Create Night Shift job for podcast processing"""
        metadata = target.get('metadata', {})

        job = {
            "job_id": f"podcast_{target['target_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "podcast_processing",
            "target_id": target['target_id'],
            "target_name": target['name'],
            "priority": target.get('priority', 5),
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "parameters": {
                "youtube_url": metadata.get('priority_episode') or metadata.get('latest_episode_url'),
                "transcription_mode": "BALANCED",
                "intelligence_focus": metadata.get('intelligence_focus_areas', []),
                "extraction_priority": metadata.get('extraction_priority', 'medium')
            }
        }

        return job

    def assess_target_priority(self, target: Dict) -> PriorityAssessment:
        """
        Use Qwen to assess strategic intelligence value.

        Args:
            target: Target dict with id, name, type, priority, metadata

        Returns:
            PriorityAssessment with recommended priority and reasoning
        """
        logger.info(f"Assessing priority for target: {target['name']}")

        # Get existing research for this target
        existing_research = self._get_existing_research_summary(target['target_id'])

        # Detect mosaic intelligence indicators
        mosaic_info = self._detect_mosaic_indicators(target)

        # Build LLM prompt for priority assessment with mosaic strategy
        mosaic_section = ""
        if mosaic_info['is_mosaic_target']:
            mosaic_section = f"""
{'='*70}
MOSAIC STRATEGY GUIDANCE (CRITICAL):
{'='*70}

Mosaic Target Status: YES - MOSAIC STRATEGY APPLIES
Indicators: {mosaic_info['reasoning']}

**CRITICAL RULE FOR MOSAIC TARGETS:**
IF target shows HIGH CONCERN + LOW DIRECT EVIDENCE + OBSCURATION INDICATORS:
  → DO NOT lower priority due to "limited evidence"
  → INSTEAD: ELEVATE priority (recommend 1 or 2)
  → Strategy: Shift to GRANULAR DETAIL COLLECTION (biographical timeline, network mapping, document recovery)
  → Goal: Build intelligence MOSAIC from indirect evidence

Examples of mosaic targets:
- Agnew Bahnson (Bahnson Labs, alleged antigravity, sparse direct sources)
- Thomas Townsend Brown (electrogravitics, classified work periods)
- Pat Price (remote viewing, unexplained death, classified targets)

For mosaic targets, "limited evidence" is a SIGNAL TO INVESTIGATE DEEPER, not lower priority.

{'='*70}
"""

        prompt = f"""You are a strategic intelligence analyst evaluating research targets.

Target: {target['name']}
Type: {target['target_type']}
Current Priority: {target['priority']}
Existing Research: {existing_research}
{mosaic_section}
Analyze this target's intelligence value based on:
1. Potential to reveal hidden historical patterns
2. Connections to other high-value targets
3. Evidence availability (declassified docs, interviews, books)
4. Strategic importance for understanding obscured events
5. **MOSAIC STRATEGY APPLICATION (if indicators present)**

IMPORTANT: Output ONLY a valid JSON object. Do not include any text before or after the JSON.

{{
  "recommended_priority": <int 1-5, where 1=highest>,
  "reasoning": "<detailed explanation considering mosaic strategy>",
  "intelligence_gaps": ["<gap 1>", "<gap 2>"],
  "related_targets": [],
  "mosaic_strategy_applied": <true or false>
}}"""

        # Call LLM
        try:
            response_text = self.llm.complete(
                instructions=prompt,
                excerpts=[{"text": json.dumps(target), "source": "target_metadata"}],
                limits={"max_output": 500}
            )

            # Parse JSON response
            response_data = self._extract_json_from_response(response_text)

            # Apply mosaic strategy override if needed
            recommended_priority = response_data.get('recommended_priority', target['priority'])
            reasoning = response_data.get('reasoning', 'No reasoning provided')

            if mosaic_info['is_mosaic_target']:
                # If LLM lowered priority on mosaic target, override with elevation
                if recommended_priority > target.get('priority', 5):
                    logger.warning(f"MOSAIC OVERRIDE: LLM recommended lowering priority for mosaic target {target['name']}")
                    logger.warning(f"  Original recommendation: {recommended_priority}")
                    logger.warning(f"  Overriding to: {max(1, target.get('priority', 5) - 1)} (elevate for mosaic strategy)")

                    recommended_priority = max(1, target.get('priority', 5) - 1)
                    reasoning += f"\n\n[MOSAIC OVERRIDE]: This target qualifies for mosaic intelligence strategy due to: {mosaic_info['reasoning']}. Priority elevated to enable granular detail collection despite limited direct evidence."
                    response_data['mosaic_strategy_applied'] = True
                elif recommended_priority == target.get('priority', 5):
                    # If kept same, slightly elevate
                    logger.info(f"MOSAIC STRATEGY: Elevating {target['name']} from {recommended_priority} to {max(1, recommended_priority - 1)}")
                    recommended_priority = max(1, recommended_priority - 1)
                    reasoning += f"\n\n[MOSAIC STRATEGY APPLIED]: Priority elevated for granular detail collection. Indicators: {mosaic_info['reasoning']}"
                    response_data['mosaic_strategy_applied'] = True

            assessment = PriorityAssessment(
                target_id=target['target_id'],
                target_name=target['name'],
                recommended_priority=recommended_priority,
                reasoning=reasoning,
                intelligence_gaps=response_data.get('intelligence_gaps', []),
                related_targets=response_data.get('related_targets', []),
                assessed_at=datetime.now()
            )

            logger.info(f"Assessment complete: priority {target['priority']} → {assessment.recommended_priority}")
            return assessment

        except Exception as e:
            logger.error(f"Priority assessment failed for {target['name']}: {e}")
            # Fallback to current priority
            return PriorityAssessment(
                target_id=target['target_id'],
                target_name=target['name'],
                recommended_priority=target['priority'],
                reasoning=f"LLM assessment failed: {str(e)}",
                intelligence_gaps=[],
                related_targets=[],
                assessed_at=datetime.now()
            )

    def generate_research_questions(
        self,
        target: Dict,
        max_questions: int = 5
    ) -> List[ResearchQuestion]:
        """
        Generate specific, intelligence-focused research questions (not generic URLs).

        Analyzes:
        - What intelligence already exists for this target
        - What key questions remain unanswered
        - What connections to other targets need exploration
        - What evidence types are needed (documents, testimony, etc.)

        Args:
            target: Target dict
            max_questions: Maximum questions to generate

        Returns:
            List of ResearchQuestion objects
        """
        logger.info(f"Generating research questions for: {target['name']}")

        # Get existing research
        existing_research = self._get_existing_research_summary(target['target_id'])
        completed_questions = self._get_completed_questions(target['target_id'])

        # Build LLM prompt
        prompt = f"""You are an intelligence research coordinator designing targeted investigations.

Target: {target['name']}
Type: {target['target_type']}
Existing Research: {existing_research}
Completed Questions: {completed_questions}

Generate {max_questions} specific research questions that:
1. Fill the most critical intelligence gaps
2. Are answerable with available evidence sources
3. Produce actionable intelligence (not general knowledge)
4. Connect to broader patterns across targets

IMPORTANT: Output ONLY a valid JSON array. Do not include any text before or after the JSON.

[
  {{
    "question": "<specific, focused, answerable question>",
    "evidence_requirements": ["<type 1>", "<type 2>"],
    "expected_intelligence_value": "<high/medium/low>",
    "min_sources": 3,
    "estimated_complexity": "<simple/moderate/complex>"
  }}
]"""

        try:
            response_text = self.llm.complete(
                instructions=prompt,
                excerpts=[{"text": json.dumps(target), "source": "target_metadata"}],
                limits={"max_output": 800}
            )

            # Parse JSON array
            questions_data = self._extract_json_from_response(response_text)

            # Handle both array and single object responses
            if isinstance(questions_data, dict):
                questions_data = [questions_data]
            elif not isinstance(questions_data, list):
                logger.warning(f"Unexpected response type: {type(questions_data)}")
                questions_data = []

            questions = []
            for q_data in questions_data[:max_questions]:
                # Skip empty or invalid question objects
                if not isinstance(q_data, dict):
                    continue

                question_text = q_data.get('question', '').strip()
                if not question_text or question_text == 'No question provided':
                    logger.warning(f"Skipping invalid question: {q_data}")
                    continue

                questions.append(ResearchQuestion(
                    question=question_text,
                    evidence_requirements=q_data.get('evidence_requirements', ['Web sources']),
                    expected_intelligence_value=q_data.get('expected_intelligence_value', 'medium'),
                    min_sources=q_data.get('min_sources', 3),
                    estimated_complexity=q_data.get('estimated_complexity', 'moderate')
                ))

            if not questions:
                logger.warning(f"No valid questions generated from LLM response")

            logger.info(f"Generated {len(questions)} research questions")
            return questions

        except Exception as e:
            logger.error(f"Question generation failed for {target['name']}: {e}")
            # Fallback to generic question
            return [ResearchQuestion(
                question=f"What is the historical significance of {target['name']}?",
                evidence_requirements=["Web sources", "Historical documents"],
                expected_intelligence_value="medium",
                min_sources=3,
                estimated_complexity="moderate"
            )]

    def create_nightshift_jobs_from_questions(
        self,
        target_id: int,
        target_name: str,
        questions: List[ResearchQuestion]
    ) -> List[Dict]:
        """
        Convert LLM-generated research questions into Night Shift job definitions.

        Maps complexity to job_class:
        - "simple" → "standard" (Qwen local execution)
        - "complex" → "demanding" (route to Claude Code queue)

        Args:
            target_id: Target ID
            target_name: Target name
            questions: List of ResearchQuestion objects

        Returns:
            List of job definition dicts
        """
        jobs = []
        safe_name = target_name.replace(' ', '_').replace('—', '-').lower()

        for i, q in enumerate(questions, 1):
            job_class = "standard" if q.estimated_complexity == "simple" else "standard"  # Use standard for all initially

            job = {
                "job_id": f"TARGET_{target_id}_Q{i}",
                "type": "sherlock_research",
                "class": job_class,
                "status": "ready",
                "inputs": [{
                    "type": "research_question",
                    "question": q.question,
                    "evidence_requirements": q.evidence_requirements,
                    "min_sources": q.min_sources
                }],
                "outputs": [{
                    "path": f"/home/johnny5/Sherlock/evidence/{safe_name}_Q{i}.md",
                    "type": "markdown"
                }],
                "metadata": {
                    "target_id": target_id,
                    "target_name": target_name,
                    "intelligence_value": q.expected_intelligence_value,
                    "complexity": q.estimated_complexity,
                    "generated_by": "llm_targeting_officer",
                    "generated_at": datetime.now().isoformat()
                }
            }
            jobs.append(job)

        logger.info(f"Created {len(jobs)} Night Shift jobs for {target_name}")
        return jobs

    def review_research_outputs(self, target_id: int) -> Dict:
        """
        Qwen reviews its own research outputs to identify what's still missing.

        For each completed research question:
        1. Load the output markdown file
        2. Assess evidence quality (citations, sources, coherence)
        3. Identify what intelligence was NOT found
        4. Generate follow-up questions for gaps

        Args:
            target_id: Target to review

        Returns:
            Dict with quality_assessment, remaining_gaps, follow_up_questions
        """
        logger.info(f"Reviewing research outputs for target {target_id}")

        # Get target info
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM targets WHERE target_id = ?', (target_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return {
                'outputs_reviewed': 0,
                'quality_assessment': {},
                'remaining_gaps': [],
                'follow_up_questions': []
            }

        target_name = result[0]
        safe_name = target_name.replace(' ', '_').replace('—', '-').lower()

        # Find completed research outputs
        evidence_dir = Path("/home/johnny5/Sherlock/evidence")
        output_files = list(evidence_dir.glob(f"{safe_name}_*.md"))

        if not output_files:
            logger.info(f"No outputs found for {target_name}")
            return {
                'outputs_reviewed': 0,
                'quality_assessment': {},
                'remaining_gaps': [],
                'follow_up_questions': []
            }

        # Review each output
        quality_scores = {}
        all_gaps = []

        for output_file in output_files:
            try:
                with open(output_file, 'r') as f:
                    content = f.read()

                # LLM review prompt
                prompt = f"""Review this research output and identify intelligence gaps:

Output File: {output_file.name}
Content:
{content[:2000]}  # First 2000 chars

Assess:
1. What key intelligence was successfully extracted?
2. What important questions remain unanswered?
3. What evidence sources were NOT found but likely exist?
4. What follow-up research would fill the gaps?

Provide JSON response:
{{
  "quality_score": <0-100>,
  "intelligence_extracted": ["<item 1>", "<item 2>", ...],
  "remaining_gaps": ["<gap 1>", "<gap 2>", ...],
  "missing_evidence": ["<source type 1>", "<source type 2>", ...]
}}"""

                response_text = self.llm.complete(
                    instructions=prompt,
                    excerpts=[{"text": content[:2000], "source": str(output_file)}],
                    limits={"max_output": 400}
                )

                review_data = self._extract_json_from_response(response_text)
                quality_scores[output_file.name] = review_data.get('quality_score', 50)
                all_gaps.extend(review_data.get('remaining_gaps', []))

            except Exception as e:
                logger.warning(f"Failed to review {output_file}: {e}")

        return {
            'outputs_reviewed': len(output_files),
            'quality_assessment': quality_scores,
            'remaining_gaps': list(set(all_gaps)),  # Deduplicate
            'follow_up_questions': []  # Could generate based on gaps
        }

    def assess_all_targets(self) -> Dict:
        """
        Assess all targets and update priorities based on LLM intelligence.

        Returns:
            Dict with assessment results
        """
        logger.info("Starting LLM-based assessment of all targets")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT target_id, name, target_type, priority, status, metadata
            FROM targets
            ORDER BY priority ASC
        ''')

        targets = []
        for row in cursor.fetchall():
            targets.append({
                'target_id': row[0],
                'name': row[1],
                'target_type': row[2],
                'priority': row[3],
                'status': row[4],
                'metadata': json.loads(row[5]) if row[5] else {}
            })

        conn.close()

        # Assess each target
        assessments = []
        priorities_updated = 0

        for target in targets:
            assessment = self.assess_target_priority(target)
            assessments.append(assessment)

            # Update priority if recommendation differs (with hysteresis to prevent oscillation)
            # Require at least 2-level change to update (prevents 3↔4 oscillation)
            priority_delta = abs(assessment.recommended_priority - target['priority'])
            if assessment.recommended_priority != target['priority'] and priority_delta >= 2:
                self._update_target_priority(
                    target['target_id'],
                    assessment.recommended_priority,
                    assessment.reasoning
                )
                priorities_updated += 1
            elif assessment.recommended_priority != target['priority'] and priority_delta == 1:
                logger.debug(f"Skipping 1-level priority change for {target['name']} (hysteresis)")

        logger.info(f"Assessed {len(targets)} targets, updated {priorities_updated} priorities")

        return {
            'targets_assessed': len(targets),
            'priorities_updated': priorities_updated,
            'assessments': [a.__dict__ for a in assessments]
        }

    def run_autonomous_cycle(self, cycle_number: int = 1) -> Dict:
        """
        Execute one autonomous targeting cycle.

        Each cycle:
        1. Assess all targets and update priorities
        2. Generate research questions for high-priority targets
        3. Create Night Shift jobs
        4. Return job definitions for execution

        Args:
            cycle_number: Cycle iteration number

        Returns:
            Dict with cycle results
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Autonomous Cycle {cycle_number}")
        logger.info(f"{'='*70}\n")

        cycle_start = datetime.now()

        # 1. Assess all targets
        assessment_results = self.assess_all_targets()

        # 2. Get top priority targets (priority 1-2)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT target_id, name, target_type, priority, metadata
            FROM targets
            WHERE priority <= 2
            ORDER BY priority ASC
            LIMIT 5
        ''')

        top_targets = []
        for row in cursor.fetchall():
            top_targets.append({
                'target_id': row[0],
                'name': row[1],
                'target_type': row[2],
                'priority': row[3],
                'metadata': json.loads(row[4]) if row[4] else {}
            })
        conn.close()

        # 3. Generate research questions for each (or podcast jobs)
        all_jobs = []
        for target in top_targets:
            target_type = target.get('target_type', 'unknown')

            if target_type == 'podcast_series':
                # Create podcast processing job
                podcast_job = self._create_podcast_processing_job(target)
                all_jobs.append(podcast_job)
                logger.info(f"Created podcast processing job for: {target['name']}")
            else:
                # Standard research question workflow
                questions = self.generate_research_questions(target, max_questions=3)
                jobs = self.create_nightshift_jobs_from_questions(
                    target['target_id'],
                    target['name'],
                    questions
                )
                all_jobs.extend(jobs)

        # 4. Save jobs to Night Shift queue
        jobs_saved = self._save_jobs_to_nightshift(all_jobs)

        # 5. Log cycle to database
        cycle_end = datetime.now()
        self._log_autonomous_cycle(
            cycle_number=cycle_number,
            start_time=cycle_start,
            end_time=cycle_end,
            targets_assessed=assessment_results['targets_assessed'],
            priorities_updated=assessment_results['priorities_updated'],
            jobs_created=len(all_jobs)
        )

        logger.info(f"\nCycle {cycle_number} complete:")
        logger.info(f"  Targets assessed: {assessment_results['targets_assessed']}")
        logger.info(f"  Priorities updated: {assessment_results['priorities_updated']}")
        logger.info(f"  Jobs created: {len(all_jobs)}")
        logger.info(f"  Jobs saved: {jobs_saved}")

        return {
            'cycle_number': cycle_number,
            'targets_assessed': assessment_results['targets_assessed'],
            'priorities_updated': assessment_results['priorities_updated'],
            'jobs_created': len(all_jobs),
            'jobs_saved': jobs_saved,
            'top_targets': [t['name'] for t in top_targets]
        }

    def start_continuous_operation(self, max_cycles: Optional[int] = None):
        """
        Run Night Shift in full autonomous mode until user returns.

        Creates "nightshift_autonomous.lock" file to signal operation.
        User removes lock file to halt gracefully.

        Args:
            max_cycles: Maximum cycles to run (None = infinite)
        """
        lock_file = Path("/home/johnny5/Johny5Alive/j5a-nightshift/nightshift_autonomous.lock")
        lock_file.write_text(f"Started: {datetime.now().isoformat()}\n")

        logger.info("="*70)
        logger.info("AUTONOMOUS CONTINUOUS OPERATION STARTED")
        logger.info("="*70)
        logger.info(f"Lock file: {lock_file}")
        logger.info(f"Remove lock file to halt gracefully")
        logger.info("="*70)

        cycle_count = 0
        while lock_file.exists():
            cycle_count += 1

            if max_cycles and cycle_count > max_cycles:
                logger.info(f"Reached max cycles ({max_cycles}), halting")
                break

            try:
                result = self.run_autonomous_cycle(cycle_count)

                # Wait before next cycle (thermal management)
                import time
                wait_seconds = 300  # 5 minutes between cycles
                logger.info(f"\nWaiting {wait_seconds}s before next cycle...")
                time.sleep(wait_seconds)

            except KeyboardInterrupt:
                logger.info("\nKeyboard interrupt - halting autonomous operation")
                break
            except Exception as e:
                logger.error(f"Cycle {cycle_count} failed: {e}")
                # Continue to next cycle after error

        # Clean up lock file
        if lock_file.exists():
            lock_file.unlink()

        logger.info("\n" + "="*70)
        logger.info("AUTONOMOUS OPERATION COMPLETE")
        logger.info(f"Total cycles: {cycle_count}")
        logger.info("="*70)

    # =================================================================
    # Private Helper Methods
    # =================================================================

    def _get_existing_research_summary(self, target_id: int) -> str:
        """Get summary of existing research for a target"""
        evidence_dir = Path("/home/johnny5/Sherlock/evidence")

        # Get target name
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM targets WHERE target_id = ?', (target_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return "No existing research found"

        target_name = result[0]
        safe_name = target_name.replace(' ', '_').replace('—', '-').lower()

        # Find evidence files
        evidence_files = list(evidence_dir.glob(f"{safe_name}*.json"))

        if not evidence_files:
            return "No existing research found"

        return f"Found {len(evidence_files)} evidence files for {target_name}"

    def _get_completed_questions(self, target_id: int) -> str:
        """Get list of completed research questions"""
        # For now, return placeholder
        # In full implementation, would query job database
        return "None"

    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON object from LLM response text with robust brace matching"""
        # Try to find JSON in response using brace matching to handle trailing text
        try:
            # Find first { or [
            start = response_text.find('{')
            if start == -1:
                start = response_text.find('[')
                is_array = True
            else:
                is_array = False

            if start == -1:
                raise ValueError("No JSON found in response")

            # Use brace counting to find matching close
            open_char = '[' if is_array else '{'
            close_char = ']' if is_array else '}'

            depth = 0
            in_string = False
            escape_next = False
            end = -1

            for i, char in enumerate(response_text[start:], start):
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if char == open_char:
                    depth += 1
                elif char == close_char:
                    depth -= 1
                    if depth == 0:
                        end = i
                        break

            if end == -1:
                # Fallback to rfind
                end = response_text.rfind(close_char)

            if end == -1:
                raise ValueError("No JSON closing found in response")

            json_text = response_text[start:end+1]
            return json.loads(json_text)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return {}
        except Exception as e:
            logger.warning(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return {}

    def _update_target_priority(self, target_id: int, new_priority: int, reasoning: str):
        """Update target priority in database with history logging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current priority for history
        cursor.execute('SELECT priority FROM targets WHERE target_id = ?', (target_id,))
        result = cursor.fetchone()
        old_priority = result[0] if result else new_priority

        timestamp = datetime.now().isoformat()

        # Update target priority
        cursor.execute('''
            UPDATE targets
            SET priority = ?, updated_at = ?
            WHERE target_id = ?
        ''', (new_priority, timestamp, target_id))

        # Log to priority history table
        cursor.execute('''
            INSERT INTO target_priority_history
            (target_id, old_priority, new_priority, reasoning, reviewer, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (target_id, old_priority, new_priority, reasoning[:500], 'llm_targeting_officer', timestamp))

        conn.commit()
        conn.close()

        logger.info(f"Updated target {target_id} priority to {new_priority}: {reasoning[:100]}...")

    def _save_jobs_to_nightshift(self, jobs: List[Dict]) -> int:
        """Save jobs to Night Shift queue"""
        queue_file = Path("/home/johnny5/Johny5Alive/j5a-nightshift/ops/queue/nightshift_jobs.json")

        try:
            # Load existing queue - expect FLAT ARRAY format
            if queue_file.exists():
                with open(queue_file, 'r') as f:
                    queue_data = json.load(f)
                    # Verify it's a list (the actual format)
                    if not isinstance(queue_data, list):
                        if isinstance(queue_data, dict) and "jobs" in queue_data:
                            queue_data = queue_data["jobs"]  # Unwrap if wrapped
                        else:
                            queue_data = []
            else:
                queue_data = []  # Start with flat array, not {"jobs": []}

            # Add new jobs
            queue_data.extend(jobs)  # Works with flat array

            # Save updated queue - maintain FLAT ARRAY format
            with open(queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2)

            logger.info(f"Saved {len(jobs)} jobs to Night Shift queue")
            return len(jobs)

        except Exception as e:
            logger.error(f"Failed to save jobs to Night Shift: {e}")
            return 0

    def _log_autonomous_cycle(
        self,
        cycle_number: int,
        start_time: datetime,
        end_time: datetime,
        targets_assessed: int,
        priorities_updated: int,
        jobs_created: int
    ):
        """Log autonomous cycle to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO autonomous_cycles
            (cycle_number, start_time, end_time, targets_assessed,
             priorities_updated, jobs_created, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            cycle_number,
            start_time.isoformat(),
            end_time.isoformat(),
            targets_assessed,
            priorities_updated,
            jobs_created,
            'completed'
        ))

        conn.commit()
        conn.close()


# Example usage and testing
if __name__ == "__main__":
    import yaml

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load config
    config_path = Path("/home/johnny5/Johny5Alive/j5a-nightshift/rules.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Initialize LLM Gateway
    llm = LLMGateway(mode=LLMMode.LOCAL, config=config)

    # Initialize LLM Targeting Officer
    officer = LLMTargetingOfficer(
        db_path="/home/johnny5/Sherlock/sherlock.db",
        llm_gateway=llm
    )

    print("="*70)
    print("LLM-Enhanced Targeting Officer - Test Run")
    print("="*70)
    print()

    # Test: Run single autonomous cycle
    print("Testing single autonomous cycle...")
    result = officer.run_autonomous_cycle(cycle_number=1)

    print("\nCycle Results:")
    print(f"  Targets assessed: {result['targets_assessed']}")
    print(f"  Priorities updated: {result['priorities_updated']}")
    print(f"  Jobs created: {result['jobs_created']}")
    print(f"  Top targets: {', '.join(result['top_targets'])}")

    print("\n" + "="*70)
    print("✅ Test complete")
    print("="*70)
