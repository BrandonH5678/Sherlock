#!/usr/bin/env python3
"""
Sullivan & Cromwell Additional Evidence Integration
Adds Iran 1953, Chile 1970-73 cases to existing S&C intelligence
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class SCAdditionalIntegrator:
    """Integrate additional Sullivan & Cromwell cases"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)

    def add_speakers(self):
        """Add new speakers for Iran/Chile cases"""
        print("\n📋 Adding additional speakers...")

        speakers = [
            Speaker(
                speaker_id="mohammad_mossadegh",
                name="Mohammad Mossadegh",
                title="Prime Minister of Iran",
                organization="Government of Iran",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1951-04-28T00:00:00",
                last_seen="1953-08-19T00:00:00"
            ),
            Speaker(
                speaker_id="salvador_allende",
                name="Salvador Allende",
                title="President of Chile",
                organization="Government of Chile",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1970-11-03T00:00:00",
                last_seen="1973-09-11T00:00:00"
            )
        ]

        for speaker in speakers:
            try:
                self.db.add_speaker(speaker)
                print(f"  ✅ {speaker.name}")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"  ⚠️  {speaker.name} (already exists)")
                else:
                    raise

    def create_evidence_sources(self):
        """Create additional S&C evidence sources"""
        print("\n📄 Creating additional evidence sources...")

        sources = [
            EvidenceSource(
                source_id="sullivan_cromwell_iran_chile_analysis_2025",
                title="Sullivan & Cromwell Client-Operation Overlaps: Iran 1953, Chile 1970-73",
                url=None,
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="2025-10-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'Sullivan & Cromwell CIA Connections - Extended',
                    'topic': 'Iran coup 1953, Chile coup 1973 corporate overlaps',
                    'analysis_type': 'Corporate-intelligence nexus research',
                    'significance': 'Expands S&C pattern beyond Guatemala to Iran and Chile'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✅ {source.source_id}")

    def extract_key_claims(self):
        """Extract claims from Iran/Chile research"""
        print("\n🔍 Extracting additional claims...")

        key_claims = [
            {
                'text': 'Sullivan & Cromwell served as counsel to Standard Oil Co. (New Jersey) / Esso in multiple federal cases 1950s-1960s. Longstanding attorney-client relationship documented.',
                'context': 'S&C representation of Standard Oil (Jersey Standard)',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'Standard Oil', 'Esso', 'John Foster Dulles'],
                'tags': ['standard-oil', 'jersey-standard', 'client-relationship', 'oil-industry']
            },
            {
                'text': '1953 CIA coup in Iran overthrew Mossadegh government. 1954 Consortium Agreement restored Western oil control with Jersey Standard (S&C client) among U.S. participants.',
                'context': 'Iran coup directly benefited S&C oil industry client',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'allen_dulles',
                'confidence': 1.0,
                'entities': ['CIA', 'Iran', 'Mohammad Mossadegh', 'Standard Oil', 'Sullivan & Cromwell'],
                'tags': ['iran-coup', '1953', 'oil-consortium', 'operation-ajax', 'strong-link']
            },
            {
                'text': 'Iran 1953 coup reset control over Iranian oil from which consortium including Standard Oil (N.J.) directly benefited. S&C client gained from covert operation.',
                'context': 'Corporate benefit analysis of Iran coup',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['Standard Oil', 'Iran', 'Sullivan & Cromwell', 'CIA'],
                'tags': ['corporate-benefit', 'oil-control', 'consortium-agreement', 'direct-gain']
            },
            {
                'text': 'Sullivan & Cromwell was counsel of record to Kennecott Copper in U.S. litigation (1960s). Documented attorney-client relationship.',
                'context': 'S&C representation of Kennecott Copper',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'Kennecott Copper'],
                'tags': ['kennecott', 'copper-industry', 'client-relationship', 'chile']
            },
            {
                'text': 'CIA extensive covert programs to destabilize Allende government Chile 1970-1973. Coup September 11, 1973. Copper nationalization directly hit Kennecott/Anaconda interests.',
                'context': 'Chile coup and copper industry impact',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'salvador_allende',
                'confidence': 1.0,
                'entities': ['CIA', 'Chile', 'Salvador Allende', 'Kennecott Copper', 'Anaconda Company'],
                'tags': ['chile-coup', '1973', 'september-11-1973', 'copper-nationalization', 'moderate-link']
            },
            {
                'text': 'U.S. covert action in Chile intersected copper sector where S&C-represented companies (Kennecott) had major Chilean assets. FRUS and Senate Church Committee records detail U.S. covert operations.',
                'context': 'Sectoral overlap between S&C client and CIA operation',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 0.9,
                'entities': ['Sullivan & Cromwell', 'Kennecott Copper', 'CIA', 'Chile'],
                'tags': ['sectoral-overlap', 'church-committee', 'frus', 'documented-covert-ops']
            },
            {
                'text': 'Sullivan & Cromwell counsel appeared in DOJ antitrust litigation touching Anaconda Company affiliates (1960s). Anaconda prominent in Chilean copper pre-1973.',
                'context': 'S&C connection to Anaconda Company',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 0.8,
                'entities': ['Sullivan & Cromwell', 'Anaconda Company', 'Chile'],
                'tags': ['anaconda', 'copper', 'antitrust', 'contextual-link']
            },
            {
                'text': 'Anaconda flagship copper concessions nationalized by Allende before coup. Corporate compensation issues arose post-coup. Same Chile covert operations as Kennecott case.',
                'context': 'Anaconda exposure to Chile nationalization and coup',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'salvador_allende',
                'confidence': 0.9,
                'entities': ['Anaconda Company', 'Salvador Allende', 'Chile', 'CIA'],
                'tags': ['nationalization', 'copper-concessions', 'post-coup-compensation']
            },
            {
                'text': 'Pattern across Guatemala (UFCO), Iran (Standard Oil), Chile (Kennecott/Anaconda): Sectoral exposure (bananas, oil, copper) created situations where covert state power secured conditions that legal/financial structuring alone could not.',
                'context': 'Structural pattern analysis across three coups',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'CIA', 'United Fruit Company', 'Standard Oil', 'Kennecott Copper'],
                'tags': ['pattern-analysis', 'structural-alignment', 'three-coups', 'corporate-state-fusion']
            },
            {
                'text': 'Personnel bridges (Dulles brothers) knit elite Wall Street lawyering to Cold War statecraft. Sectoral exposure created situations where covert state power secured what legal structuring alone could not. Functional alignment repeatedly observable.',
                'context': 'Synthesis of S&C corporate-intelligence nexus',
                'source': 'sullivan_cromwell_iran_chile_analysis_2025',
                'speaker': 'allen_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'Allen Dulles', 'John Foster Dulles', 'CIA'],
                'tags': ['personnel-bridges', 'functional-alignment', 'wall-street-statecraft', 'systematic-pattern']
            }
        ]

        claim_ids = []
        for i, claim_data in enumerate(key_claims):
            claim_id = f"sullivan_cromwell_additional_claim_{i:04d}"

            claim = EvidenceClaim(
                claim_id=claim_id,
                source_id=claim_data['source'],
                speaker_id=claim_data['speaker'],
                claim_type=ClaimType.FACTUAL,
                text=claim_data['text'],
                confidence=claim_data['confidence'],
                start_time=None,
                end_time=None,
                page_number=None,
                context=claim_data['context'],
                entities=claim_data['entities'],
                tags=['sullivan-cromwell', 'cia-law-firm', 'corporate-intelligence'] + claim_data['tags'],
                created_at=datetime.now().isoformat()
            )

            self.db.add_evidence_claim(claim)
            claim_ids.append(claim_id)

        print(f"  ✅ Extracted {len(claim_ids)} additional claims")
        return claim_ids


def main():
    """Integrate additional S&C evidence"""
    print("=" * 70)
    print("Sullivan & Cromwell Additional Evidence Integration")
    print("Iran 1953 + Chile 1970-73")
    print("=" * 70)

    integrator = SCAdditionalIntegrator("/home/johnny5/Sherlock/evidence.db")

    # Add speakers
    integrator.add_speakers()

    # Create evidence sources
    integrator.create_evidence_sources()

    # Extract claims
    claim_ids = integrator.extract_key_claims()

    print("\n" + "=" * 70)
    print("✅ Additional S&C Evidence Integration Complete")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - New speakers: 2 (Mossadegh, Allende)")
    print(f"  - New sources: 1")
    print(f"  - New claims: {len(claim_ids)}")
    print(f"  - Total S&C coups documented: 3 (Guatemala, Iran, Chile)")


if __name__ == "__main__":
    main()
