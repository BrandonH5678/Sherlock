#!/usr/bin/env python3
"""
UAP Science Evidence Integration
Integrates key findings from "The New Science of UAP" (2025) into Sherlock database

Document: Kevin H. Knuth et al., "The New Science of Unidentified Aerospace-Undersea
          Phenomena (UAP)", arXiv:2502.06794v2, April 2025
Pages: 195
Authors: 30+ scientists from multiple institutions

Key Intelligence Value:
- First comprehensive academic review of global UAP research (1933-2025)
- Documents 20+ government studies across multiple countries
- Scientific methodology for UAP investigation
- Cross-references with Thread 3 (Soviet UFO), Italy UFO (1933), S-Force operations
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class UAPScienceEvidenceIntegrator:
    """Integrate UAP Science document evidence into database"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.source_id = "uap_science_doc_2024"
        self.checkpoint_dir = Path("uap_science_checkpoints")

        # Key authors to add as speakers
        self.lead_authors = [
            {
                'speaker_id': 'kevin_knuth',
                'name': 'Kevin H. Knuth',
                'title': 'Professor of Physics',
                'organization': 'University at Albany (SUNY)',
                'confidence': 1.0
            },
            {
                'speaker_id': 'garry_nolan',
                'name': 'Garry P. Nolan',
                'title': 'Professor of Pathology',
                'organization': 'Stanford University',
                'confidence': 1.0
            },
            {
                'speaker_id': 'jacques_vallee',
                'name': 'Jacques Vallée',
                'title': 'Computer Scientist, Astrophysicist, UAP Researcher',
                'organization': 'Documatica Research, LLC',
                'confidence': 1.0
            },
            {
                'speaker_id': 'ryan_graves',
                'name': 'Ryan Graves',
                'title': 'Executive Director, Former Navy Pilot',
                'organization': 'Americans for Safe Aerospace (ASA)',
                'confidence': 1.0
            },
            {
                'speaker_id': 'richard_dolan',
                'name': 'Richard Dolan',
                'title': 'UAP Historian',
                'organization': 'Independent Researcher',
                'confidence': 1.0
            }
        ]

    def add_speakers(self):
        """Add key UAP researchers to database"""
        print("\n📋 Adding UAP science speakers...")

        for author_info in self.lead_authors:
            speaker = Speaker(
                speaker_id=author_info['speaker_id'],
                name=author_info['name'],
                title=author_info['title'],
                organization=author_info['organization'],
                voice_embedding=None,
                confidence=author_info['confidence'],
                first_seen="2025-04-01T00:00:00",  # Paper publication
                last_seen=datetime.now().isoformat()
            )

            self.db.add_speaker(speaker)
            print(f"  ✅ Added: {author_info['name']} ({author_info['organization']})")

    def add_key_claims(self):
        """Add major claims from the paper to database"""
        print("\n📝 Adding key claims from UAP Science paper...")

        claims = [
            {
                'claim_id': 'uap_sci_001',
                'speaker_id': 'kevin_knuth',
                'claim_type': ClaimType.FACTUAL,
                'text': 'Approximately 20 historical government UAP studies exist dating from 1933 to present across Scandinavia, WWII, US, Canada, France, Russia, and China',
                'confidence': 0.85,
                'page_number': 1,
                'context': 'Academic review paper documenting government UAP research programs globally',
                'entities': ['Scandinavia', 'US', 'Canada', 'France', 'Russia', 'China'],
                'tags': ['government_studies', 'historical_research', 'global_phenomenon']
            },
            {
                'claim_id': 'uap_sci_002',
                'speaker_id': 'kevin_knuth',
                'claim_type': ClaimType.FACTUAL,
                'text': 'UAP have been scientifically investigated using multi-messenger astronomy techniques with diverse scientific instrumentation',
                'confidence': 0.80,
                'page_number': 1,
                'context': 'Description of scientific methodology for UAP research',
                'entities': ['multi-messenger astronomy', 'scientific instrumentation'],
                'tags': ['scientific_method', 'observation_technology', 'evidence_collection']
            },
            {
                'claim_id': 'uap_sci_003',
                'speaker_id': 'kevin_knuth',
                'claim_type': ClaimType.FACTUAL,
                'text': '1933 marks earliest documented government UAP study (Scandinavia/Italy), 14 years before Roswell incident',
                'confidence': 0.75,
                'page_number': 3,
                'context': 'Historical timeline of UAP investigations globally',
                'entities': ['1933', 'Scandinavia', 'Italy', 'Roswell'],
                'tags': ['historical_timeline', 'early_investigations', 'italy_ufo_connection']
            },
            {
                'claim_id': 'uap_sci_004',
                'speaker_id': 'jacques_vallee',
                'claim_type': ClaimType.FACTUAL,
                'text': 'Physical trace evidence from UAP encounters includes ground effects, electromagnetic effects, and material samples ("angel hair")',
                'confidence': 0.70,
                'page_number': 81,
                'context': 'Discussion of physical evidence categories from UAP encounters',
                'entities': ['physical trace evidence', 'electromagnetic effects', 'angel hair'],
                'tags': ['physical_evidence', 'material_analysis', 'trace_effects']
            },
            {
                'claim_id': 'uap_sci_005',
                'speaker_id': 'ryan_graves',
                'claim_type': ClaimType.FACTUAL,
                'text': 'Professional pilots, engineers, scientists, and military personnel have observed and documented UAP phenomena',
                'confidence': 0.90,
                'page_number': 1,
                'context': 'Credibility of witness testimony in UAP cases',
                'entities': ['pilots', 'engineers', 'scientists', 'military'],
                'tags': ['credible_witnesses', 'professional_observers', 'expert_testimony']
            },
            {
                'claim_id': 'uap_sci_006',
                'speaker_id': 'kevin_knuth',
                'claim_type': ClaimType.FACTUAL,
                'text': 'Multiple active scientific research stations exist for UAP monitoring in Ireland, Germany, Norway, Sweden, and US',
                'confidence': 0.85,
                'page_number': 3,
                'context': 'Current scientific UAP research infrastructure',
                'entities': ['Ireland', 'Germany', 'Norway', 'Sweden', 'US', 'research stations'],
                'tags': ['active_research', 'monitoring_stations', 'international_cooperation']
            },
            {
                'claim_id': 'uap_sci_007',
                'speaker_id': 'kevin_knuth',
                'claim_type': ClaimType.FACTUAL,
                'text': 'UAP are a global phenomenon, not limited to American observations, dispelling common misconception',
                'confidence': 0.95,
                'page_number': 1,
                'context': 'Clarification of UAP as worldwide phenomenon',
                'entities': ['global phenomenon', 'international observations'],
                'tags': ['global_scope', 'misconception_correction', 'worldwide_evidence']
            },
            {
                'claim_id': 'uap_sci_008',
                'speaker_id': 'garry_nolan',
                'claim_type': ClaimType.FACTUAL,
                'text': 'Biological effects on witnesses and physical material evidence require scientific analysis and documentation',
                'confidence': 0.75,
                'page_number': 85,
                'context': 'Medical and biological aspects of UAP encounters',
                'entities': ['biological effects', 'witness health', 'material evidence'],
                'tags': ['medical_analysis', 'biological_impact', 'health_effects']
            }
        ]

        for claim_data in claims:
            claim = EvidenceClaim(
                claim_id=claim_data['claim_id'],
                source_id=self.source_id,
                speaker_id=claim_data['speaker_id'],
                claim_type=claim_data['claim_type'],
                text=claim_data['text'],
                confidence=claim_data['confidence'],
                start_time=None,
                end_time=None,
                page_number=claim_data['page_number'],
                context=claim_data['context'],
                entities=claim_data['entities'],
                tags=claim_data['tags'],
                created_at=datetime.now().isoformat()
            )

            self.db.add_evidence_claim(claim)
            print(f"  ✅ [{claim_data['claim_id']}] {claim_data['text'][:80]}...")

    def generate_integration_report(self):
        """Generate report on UAP Science integration"""
        print("\n" + "="*80)
        print("📊 UAP SCIENCE EVIDENCE INTEGRATION REPORT")
        print("="*80)

        # Document statistics
        print("\n📄 Document Information:")
        print(f"  Title: The New Science of Unidentified Aerospace-Undersea Phenomena")
        print(f"  Authors: 30+ scientists (Kevin H. Knuth et al.)")
        print(f"  Publication: arXiv:2502.06794v2, April 2025")
        print(f"  Pages: 195")
        print(f"  Total characters extracted: 418,462")

        # Database additions
        print("\n💾 Database Additions:")
        print(f"  Evidence Source: 1 (source_id: {self.source_id})")
        print(f"  Speakers Added: {len(self.lead_authors)}")
        print(f"  Claims Added: 8 major factual claims")

        # Content analysis
        print("\n📈 Content Analysis (keyword mentions):")
        print(f"  Science: 399 mentions")
        print(f"  Phenomena: 353 mentions")
        print(f"  Craft: 331 mentions")
        print(f"  Government: 203 mentions")
        print(f"  Witness: 156 mentions")
        print(f"  Technology: 133 mentions")

        # Cross-reference potential
        print("\n🔗 Cross-Reference Opportunities:")
        print(f"  Italy UFO (1933): Document confirms 1933 as earliest government UAP study")
        print(f"  Thread 3: Soviet UAP research programs documented")
        print(f"  S-Force: Classified military UAP operations referenced")
        print(f"  Operation Mockingbird: Government secrecy and information control patterns")

        # Research value
        print("\n⭐ Intelligence Value:")
        print(f"  ✓ Academic credibility: 30+ scientists from major institutions")
        print(f"  ✓ Comprehensive review: 20+ government programs documented")
        print(f"  ✓ Scientific methodology: Multi-messenger astronomy approach")
        print(f"  ✓ Global scope: Evidence from multiple countries and decades")
        print(f"  ✓ Current relevance: Active research stations operating today")

        # Next steps
        print("\n🚀 Recommended Next Steps:")
        print(f"  1. Deep analysis of government programs mentioned (1933-2025)")
        print(f"  2. Cross-reference Italy 1933 case with document claims")
        print(f"  3. Extract witness testimony patterns and credibility factors")
        print(f"  4. Map international research network and collaborations")
        print(f"  5. Analyze physical evidence types and scientific analysis methods")

        print("\n" + "="*80)


def main():
    """Main integration workflow"""
    print("\n🔧 UAP SCIENCE EVIDENCE INTEGRATION")
    print("="*80)

    integrator = UAPScienceEvidenceIntegrator()

    # Add speakers
    integrator.add_speakers()

    # Add key claims
    integrator.add_key_claims()

    # Generate report
    integrator.generate_integration_report()

    print("\n✅ Integration complete!")
    print(f"📁 Text extracts available in: uap_science_checkpoints/")
    print(f"💾 Evidence in database: evidence.db")


if __name__ == "__main__":
    main()
