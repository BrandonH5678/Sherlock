#!/usr/bin/env python3
"""Route AI training intelligence to Prism for analysis"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def route_to_prism_analysis(intelligence_file: str):
    """Create Prism analysis request for AI training intelligence"""

    logger.info("="*70)
    logger.info("ROUTING TO PRISM: AI TRAINING INTELLIGENCE ANALYSIS")
    logger.info("="*70)

    with open(intelligence_file, 'r') as f:
        intelligence_data = json.load(f)

    prism_request = {
        "request_id": f"prism_ai_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "request_type": "strategic_intelligence_analysis",
        "source": "Shared Context Podcast - AI Training Episode",
        "priority": "HIGH",
        "analysis_framework": "RRARR",
        "intelligence_data": intelligence_data,
        "analysis_directives": {
            "primary_focus": "AI training methods, datasets, ethics, and corporate practices",
            "strategic_questions": [
                "What are the most significant revelations about AI training practices?",
                "What patterns of secrecy or transparency emerge?",
                "What ethical concerns are highlighted?",
                "What research directions are most critical?"
            ]
        }
    }

    prism_request_file = Path(intelligence_file).parent / f"{Path(intelligence_file).stem}_prism_request.json"
    with open(prism_request_file, 'w') as f:
        json.dump(prism_request, f, indent=2)

    logger.info(f"✅ Prism request created: {prism_request_file}")

    instruction_file = Path(intelligence_file).parent / f"{Path(intelligence_file).stem}_prism_instructions.md"

    instructions = f"""# Prism Analysis Required: AI Training Intelligence

**Source:** Shared Context Podcast Episode
**Intelligence File:** {intelligence_file}
**Priority:** HIGH

## Analysis Request

Apply RRARR framework:

### 1. RETRIEVE (Context Gathering)
- Load AI training intelligence from: `{intelligence_file}`
- Review extracted claims ({len(intelligence_data['claims'])} total)
- Cross-reference with existing Sherlock targets

### 2. REASON (Strategic Analysis)
- Analyze patterns in AI training practices
- Identify ethical concerns and corporate dynamics
- Connect to other intelligence targets

### 3. ACT (Strategic Recommendations)
- Research priorities for follow-up
- Targets to add to Sherlock database
- Intelligence operations to plan

### 4. REMEMBER (Knowledge Integration)
- Update knowledge graphs with AI training intelligence
- Create connections to related targets

### 5. REFLECT (Quality Assessment)
- Assess intelligence quality and confidence
- Identify gaps and uncertainties

## Expected Deliverables
1. Strategic assessment document (2-3 pages)
2. Key findings and implications (bulleted summary)
3. Research priorities (ranked list)
4. Target recommendations (people, organizations, projects)
5. Operational plan for AI training intelligence gathering
"""

    with open(instruction_file, 'w') as f:
        f.write(instructions)

    logger.info(f"✅ Prism instructions created: {instruction_file}")
    logger.info("\n" + "="*70)
    logger.info("✅ PRISM ROUTING COMPLETE")
    logger.info("="*70)

    return {
        'prism_request_file': str(prism_request_file),
        'instruction_file': str(instruction_file)
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 prism_analyze_ai_training.py <intelligence_file>")
        sys.exit(1)

    intelligence_file = sys.argv[1]
    route_to_prism_analysis(intelligence_file)
