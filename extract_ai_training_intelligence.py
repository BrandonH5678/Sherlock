#!/usr/bin/env python3
"""Extract AI training intelligence from transcript"""
import sys
import json
import logging
from pathlib import Path

sys.path.append("/home/johnny5/Sherlock")
sys.path.append("/home/johnny5/Johny5Alive/j5a-nightshift")

from evidence_database import EvidenceDatabase
from llm_gateway import LLMGateway, LLMMode
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_ai_training_intelligence(transcript_file: str):
    """Extract structured intelligence about AI training"""

    logger.info("="*70)
    logger.info("AI TRAINING INTELLIGENCE EXTRACTION")
    logger.info("="*70)

    with open(transcript_file, 'r') as f:
        transcript = f.read()

    logger.info(f"Transcript loaded: {len(transcript)} characters")

    config_path = Path("/home/johnny5/Johny5Alive/j5a-nightshift/rules.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)

    llm = LLMGateway(mode=LLMMode.API, config=config)

    extraction_prompt = f"""You are an intelligence analyst specializing in AI development and training.

Analyze this podcast transcript and extract ALL relevant information about AI training.

**Focus Areas:**
1. Training Datasets (sources, size, composition, copyright issues)
2. Training Methods (architectures, techniques, hardware)
3. Ethical Considerations (bias, consent, transparency)
4. Corporate Practices (secrecy, competition, regulation)
5. Research Directions (alignment, safety, interpretability)

**Transcript:**
{transcript}

**Output Format (JSON):**
{{
  "claims": [
    {{
      "claim_text": "<specific claim>",
      "claim_type": "<dataset|method|ethics|corporate|research>",
      "speaker": "<speaker name or 'unknown'>",
      "confidence": "<high|medium|low>",
      "supporting_quote": "<exact quote>"
    }}
  ],
  "key_entities": {{
    "organizations": ["<org1>", "<org2>"],
    "people": ["<person1>", "<person2>"],
    "technologies": ["<tech1>", "<tech2>"]
  }},
  "intelligence_summary": "<2-3 paragraph summary>",
  "research_priorities": ["<question 1>", "<question 2>"]
}}"""

    logger.info("Extracting intelligence with Claude...")

    try:
        response = llm.chat(
            messages=[{"role": "user", "content": extraction_prompt}],
            system="You are a specialized intelligence analyst focused on AI training."
        )

        response_text = response.get('content', '')

        import re
        json_match = re.search(r'```json\s*(\{.*\})\s*```', response_text, re.DOTALL)
        if json_match:
            intelligence_data = json.loads(json_match.group(1))
        else:
            intelligence_data = json.loads(response_text)

        logger.info(f"✅ Extracted {len(intelligence_data['claims'])} claims")

        output_file = Path(transcript_file).parent / f"{Path(transcript_file).stem}_ai_training_intelligence.json"
        with open(output_file, 'w') as f:
            json.dump(intelligence_data, f, indent=2)

        logger.info(f"✅ Intelligence saved: {output_file}")

        return {
            'intelligence_file': str(output_file),
            'intelligence_data': intelligence_data
        }

    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_ai_training_intelligence.py <transcript_file>")
        sys.exit(1)

    transcript_file = sys.argv[1]
    extract_ai_training_intelligence(transcript_file)
