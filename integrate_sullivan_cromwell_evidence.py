#!/usr/bin/env python3
"""
Sullivan & Cromwell / CIA Evidence Integration
Integrates Sullivan & Cromwell law firm / CIA connection intelligence into Sherlock

Architecture: Similar to S-Force/JFK integration
Output: Evidence sources, claims, speakers, relationships
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class SullivanCromwellIntegrator:
    """Integrate Sullivan & Cromwell / CIA intelligence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("sullivan_cromwell_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in Sullivan & Cromwell research
        self.entities = {
            'people': [
                'Allen Dulles', 'John Foster Dulles',
                'Jacobo Árbenz'
            ],
            'organizations': [
                'Sullivan & Cromwell', 'CIA', 'United Fruit Company',
                'I.G. Farben', 'State Department'
            ],
            'operations': [
                'Operation PBSuccess', 'Guatemala Coup 1954'
            ],
            'locations': [
                'Guatemala', 'Latin America', 'Germany'
            ]
        }

    def add_speakers(self):
        """Add key Sullivan & Cromwell speakers to database"""
        print("\n📋 Adding Sullivan & Cromwell speakers...")

        speakers = [
            Speaker(
                speaker_id="john_foster_dulles",
                name="John Foster Dulles",
                title="Secretary of State / Former Sullivan & Cromwell Partner",
                organization="U.S. State Department / Sullivan & Cromwell",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1920-01-01T00:00:00",
                last_seen="1959-05-24T00:00:00"
            ),
            Speaker(
                speaker_id="allen_dulles",
                name="Allen Dulles",
                title="CIA Director / Former Sullivan & Cromwell Partner",
                organization="Central Intelligence Agency / Sullivan & Cromwell",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1920-01-01T00:00:00",
                last_seen="1969-01-29T00:00:00"
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
        """Create Sullivan & Cromwell evidence sources"""
        print("\n📄 Creating evidence sources...")

        sources = [
            EvidenceSource(
                source_id="sullivan_cromwell_cia_analysis_2025",
                title="Sullivan & Cromwell / CIA Client-Intervention Overlaps",
                url=None,
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="2025-10-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'Sullivan & Cromwell CIA Connections',
                    'topic': 'Law firm client overlap with CIA covert operations',
                    'analysis_type': 'Corporate-intelligence nexus research',
                    'significance': 'Documents Dulles brothers revolving door between law firm and intelligence'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✅ {source.source_id}")

    def extract_key_claims(self):
        """Extract key claims from Sullivan & Cromwell research"""
        print("\n🔍 Extracting key claims...")

        key_claims = [
            {
                'text': 'Sullivan & Cromwell was longtime client counsel for United Fruit Company. Dulles brothers (John Foster, Allen) associated with UFCO via S&C partnership.',
                'context': 'United Fruit Company representation by Sullivan & Cromwell',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'United Fruit Company', 'John Foster Dulles', 'Allen Dulles'],
                'tags': ['sullivan-cromwell', 'united-fruit', 'dulles-brothers', 'law-firm-client']
            },
            {
                'text': 'John Foster Dulles was former Sullivan & Cromwell partner, then became Secretary of State while firm represented United Fruit Company. Professional link to UFCO maintained.',
                'context': 'Revolving door between Sullivan & Cromwell and State Department',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['John Foster Dulles', 'Sullivan & Cromwell', 'United Fruit Company', 'State Department'],
                'tags': ['revolving-door', 'conflict-of-interest', 'secretary-of-state']
            },
            {
                'text': 'Allen Dulles as CIA Director was on United Fruit Company Board of Trustees and owned shares in UFCO while directing CIA operations.',
                'context': 'CIA Director financial interest in corporation benefiting from covert operations',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'allen_dulles',
                'confidence': 1.0,
                'entities': ['Allen Dulles', 'CIA', 'United Fruit Company'],
                'tags': ['conflict-of-interest', 'ufco-board', 'financial-interest', 'cia-director']
            },
            {
                'text': '1954 Guatemala coup (Operation PBSuccess) overthrew Árbenz regime. Coup motivated in part by land reforms targeting United Fruit Company holdings.',
                'context': 'CIA covert operation benefiting Sullivan & Cromwell client',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'allen_dulles',
                'confidence': 1.0,
                'entities': ['Operation PBSuccess', 'Guatemala', 'Jacobo Árbenz', 'United Fruit Company', 'CIA'],
                'tags': ['guatemala-coup', '1954', 'operation-pbsuccess', 'land-reform']
            },
            {
                'text': 'State Department memos reference that "Sullivan & Cromwell, the Secretary of State\'s former firm, represented the United Fruit" during Guatemala intervention.',
                'context': 'State Department acknowledgment of law firm conflict of interest',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['State Department', 'Sullivan & Cromwell', 'United Fruit Company', 'John Foster Dulles'],
                'tags': ['state-dept-memo', 'documented-conflict', 'guatemala']
            },
            {
                'text': 'Sullivan & Cromwell had been involved with negotiating financial/corporate arrangements with German firms including I.G. Farben.',
                'context': 'Pre-WWII Sullivan & Cromwell German corporate connections',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 0.9,
                'entities': ['Sullivan & Cromwell', 'I.G. Farben', 'Germany'],
                'tags': ['ig-farben', 'germany', 'pre-wwii', 'corporate-finance']
            },
            {
                'text': 'Sullivan & Cromwell has long served sovereign finance and Latin American corporate clients, handling large-scale sovereign debt, bond underwriting, arbitration, and structuring.',
                'context': 'S&C Latin America practice created financial interest in regime stability',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'Latin America'],
                'tags': ['sovereign-finance', 'latin-america', 'bond-underwriting', 'debt-structuring']
            },
            {
                'text': 'S&C position to benefit from U.S. influence maintaining favorable regimes in Latin America. Financial infrastructure requires regime stability.',
                'context': 'Corporate-intelligence alignment analysis',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 0.9,
                'entities': ['Sullivan & Cromwell', 'CIA', 'Latin America'],
                'tags': ['regime-stability', 'financial-interest', 'covert-support']
            },
            {
                'text': 'Personnel linkages between Sullivan & Cromwell and U.S. foreign/intelligence service magnify alignment. Dulles brothers moved between S&C and state service, private-law worldview and client priorities tracked into state action.',
                'context': 'Revolving door analysis of law firm to government service',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'allen_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'CIA', 'State Department', 'John Foster Dulles', 'Allen Dulles'],
                'tags': ['revolving-door', 'client-priorities', 'state-action', 'alignment']
            },
            {
                'text': 'S&C role in structuring sovereign and corporate debt, underwriting bonds, and advising on infrastructure provides legal-financial infrastructure requiring regime stability. U.S. intelligence and foreign policy historically intervened to preserve regimes or suppress nationalizations.',
                'context': 'Structural analysis of corporate law firm / intelligence alignment',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'john_foster_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'CIA', 'State Department'],
                'tags': ['regime-preservation', 'anti-nationalization', 'structural-alignment']
            },
            {
                'text': 'United Fruit / Guatemala 1954 is strongest documented overlap: S&C was counsel to corporation whose interests directly threatened by political reform, and U.S. intelligence apparatus intervened to protect those interests.',
                'context': 'Assessment of clearest corporate-intelligence alignment case',
                'source': 'sullivan_cromwell_cia_analysis_2025',
                'speaker': 'allen_dulles',
                'confidence': 1.0,
                'entities': ['Sullivan & Cromwell', 'United Fruit Company', 'CIA', 'Guatemala', 'Operation PBSuccess'],
                'tags': ['guatemala-1954', 'corporate-protection', 'covert-intervention', 'clearest-case']
            }
        ]

        claim_ids = []
        for i, claim_data in enumerate(key_claims):
            claim_id = f"sullivan_cromwell_claim_{i:04d}"

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

        print(f"  ✅ Extracted {len(claim_ids)} key claims")
        return claim_ids

    def save_checkpoint(self, stats: Dict):
        """Save integration checkpoint"""
        checkpoint_path = self.checkpoint_dir / "sullivan_cromwell_checkpoint.json"
        stats['timestamp'] = datetime.now().isoformat()

        with open(checkpoint_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n  ✅ Checkpoint saved: {checkpoint_path}")


def main():
    """Integrate Sullivan & Cromwell evidence into Sherlock"""
    print("=" * 70)
    print("Sullivan & Cromwell / CIA Evidence Integration")
    print("=" * 70)

    integrator = SullivanCromwellIntegrator("/home/johnny5/Sherlock/evidence.db")

    # Add speakers
    integrator.add_speakers()

    # Create evidence sources
    integrator.create_evidence_sources()

    # Extract claims
    claim_ids = integrator.extract_key_claims()

    # Save checkpoint
    stats = {
        'speakers_added': 2,
        'sources_created': 1,
        'claims_extracted': len(claim_ids)
    }
    integrator.save_checkpoint(stats)

    print("\n" + "=" * 70)
    print("✅ Sullivan & Cromwell Evidence Integration Complete")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Speakers: {stats['speakers_added']}")
    print(f"  - Sources: {stats['sources_created']}")
    print(f"  - Claims: {stats['claims_extracted']}")


if __name__ == "__main__":
    main()
