#!/usr/bin/env python3
"""
Italian UFO Case (1933) Evidence Integration
Integrates evidence from alleged June 13, 1933 UFO crash in Northern Italy into Sherlock

This represents FIRST alleged UFO crash retrieval case (14 years before Roswell)
and potential connection to post-WWII US intelligence UFO retrieval programs.

Key Intelligence:
- June 13, 1933 crash in Magenta, Northern Italy
- Mussolini's "Gabinetto RS/33" (allegedly headed by Guglielmo Marconi)
- David Grusch claims US forces retrieved craft after WWII (1945)
- Forensically authenticated 1936 documents
- Significant historical skepticism and authentication concerns

Architecture: Similar to MK-Ultra/Thread 3/JFK integration
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


class ItalyUFOIntegrator:
    """Integrate Italian UFO crash (1933) evidence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("italy_ufo_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in Italian UFO research
        self.entities = {
            'people': [
                'Roberto Pinotti', 'Guglielmo Marconi', 'David Grusch',
                'Benito Mussolini', 'Marco Negri', 'Pietro Negri',
                'Antonio Garavaglia', 'Giuseppe Stilo', 'Graeme Rendall'
            ],
            'organizations': [
                'Gabinetto RS/33', 'SIAI Marchetti', 'OSS',
                'National Ufological Center', 'Supreme Court of State Security',
                'National Reconnaissance Office', 'Vatican'
            ],
            'locations': [
                'Magenta', 'Northern Italy', 'Vergiate', 'Arona',
                'Milan', 'Italy'
            ],
            'technologies': [
                'UFO craft', 'Bell-shaped object', 'Telegraph communications'
            ],
            'operations': [
                'Gabinetto RS/33', 'OSS retrieval operation 1945'
            ]
        }

    def add_speakers(self):
        """Add key Italian UFO case speakers to database"""
        print("\n📋 Adding Italian UFO case speakers...")

        speakers = [
            Speaker(
                speaker_id="roberto_pinotti",
                name="Roberto Pinotti",
                title="President, National Ufological Center",
                organization="Centro Ufologico Nazionale (Italy)",
                voice_embedding=None,
                confidence=1.0,
                first_seen="2000-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="david_grusch",
                name="David Grusch",
                title="Former Intelligence Officer & UFO Whistleblower",
                organization="National Reconnaissance Office / National Geospatial-Intelligence Agency",
                voice_embedding=None,
                confidence=1.0,
                first_seen="2023-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="marco_negri",
                name="Marco Negri",
                title="Local Witness / Descendant",
                organization="Family of Pietro Negri (Mayor of Arona)",
                voice_embedding=None,
                confidence=0.7,
                first_seen="2000-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="giuseppe_stilo",
                name="Giuseppe Stilo",
                title="Italian UFO Researcher & Skeptic",
                organization="Independent Researcher",
                voice_embedding=None,
                confidence=0.8,
                first_seen="2000-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="antonio_garavaglia",
                name="Antonio Garavaglia",
                title="Forensic Document Examiner",
                organization="Independent Expert",
                voice_embedding=None,
                confidence=0.9,
                first_seen="2000-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
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
        """Create Italian UFO evidence sources"""
        print("\n📄 Creating evidence sources...")

        sources = [
            EvidenceSource(
                source_id="italy_ufo_1933_dailymail_report",
                title="Italian researcher shares evidence files of secret 'first' UFO crash in Italy (1933)",
                url="https://www.dailymail.co.uk/",
                file_path="/home/johnny5/Downloads/Italian researcher shares evidence files of secret 'first' UFO crash in Italy | .pdf",
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=60,
                created_at="2023-01-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'Italian UFO Crash 1933',
                    'topic': 'Alleged pre-Roswell UFO crash and Mussolini government response',
                    'analysis_type': 'Investigative journalism on historical UFO documents',
                    'significance': 'First alleged UFO crash retrieval case (14 years before Roswell)',
                    'authentication_status': 'Partially authenticated (1936 document), significant skepticism',
                    'connection': 'David Grusch claims US forces retrieved craft post-WWII'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✅ {source.source_id}")

    def extract_key_claims(self):
        """Extract key claims from Italian UFO case research"""
        print("\n🔍 Extracting key claims...")

        key_claims = [
            {
                'text': 'Roberto Pinotti received documents anonymously in 1996 alleging a June 13, 1933 UFO crash in Magenta, Northern Italy, 14 years before the Roswell incident.',
                'context': 'Origin of Italian UFO crash evidence',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'roberto_pinotti',
                'confidence': 0.8,
                'entities': ['Roberto Pinotti', 'Magenta', 'Northern Italy'],
                'tags': ['italy-ufo', '1933', 'pre-roswell', 'anonymous-documents'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Pentagon whistleblower David Grusch claims the Italian UFO craft was captured by US forces after World War II and that Mussolini\'s government had retrieved and studied the object.',
                'context': 'Modern whistleblower testimony connecting to alleged 1933 case',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'david_grusch',
                'confidence': 0.6,
                'entities': ['David Grusch', 'Benito Mussolini', 'OSS'],
                'tags': ['grusch-testimony', 'us-retrieval', '1945', 'post-wwii'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Mussolini allegedly established "Gabinetto RS/33" (Special Research Cabinet 33) to study the crashed UFO, headed by Guglielmo Marconi, the Nobel Prize-winning radio inventor.',
                'context': 'Alleged Italian government UFO research program',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'roberto_pinotti',
                'confidence': 0.5,
                'entities': ['Benito Mussolini', 'Gabinetto RS/33', 'Guglielmo Marconi'],
                'tags': ['rs33', 'marconi', 'government-program', 'fascist-italy'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Telegram dated June 1933 allegedly from Mussolini ordered "immediate arrest" for "diffusion of news related to aircraft of unknown nature and origin" with "maximum penalties for transgressors up to refer to the Supreme Court of State Security".',
                'context': 'Alleged government suppression telegram',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'roberto_pinotti',
                'confidence': 0.4,
                'entities': ['Benito Mussolini', 'Supreme Court of State Security'],
                'tags': ['telegram', 'secrecy-order', 'suppression', 'june-1933'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Antonio Garavaglia forensically tested the documents in 2000 and authenticated at least one 1936 memo as genuine period material, stating the paper, ink, and typewriter characteristics were consistent with 1930s Italian government documents.',
                'context': 'Forensic authentication of documents',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'antonio_garavaglia',
                'confidence': 0.7,
                'entities': ['Antonio Garavaglia'],
                'tags': ['forensic-testing', 'authentication', '1936-document', 'typewriter-analysis'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The alleged UFO was stored at SIAI Marchetti facilities in Vergiate, an aircraft manufacturing plant near the crash site.',
                'context': 'Alleged storage location of retrieved craft',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'roberto_pinotti',
                'confidence': 0.4,
                'entities': ['SIAI Marchetti', 'Vergiate'],
                'tags': ['storage-location', 'aircraft-facility', 'northern-italy'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Marco Negri testified that his great-great grandfather Pietro Negri, Mayor of Arona from 1920s-1950s, told family stories about the UFO crash and government response in the 1930s.',
                'context': 'Local family testimony from descendant of 1930s mayor',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'marco_negri',
                'confidence': 0.5,
                'entities': ['Marco Negri', 'Pietro Negri', 'Arona'],
                'tags': ['family-testimony', 'local-knowledge', 'mayor', 'oral-history'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Giuseppe Stilo, Italian UFO researcher, called the Pinotti documents "embarrassing stories" and expressed skepticism about their authenticity.',
                'context': 'Researcher skepticism about Italian UFO case',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'giuseppe_stilo',
                'confidence': 0.9,
                'entities': ['Giuseppe Stilo'],
                'tags': ['skepticism', 'researcher-criticism', 'authentication-concerns'],
                'claim_type': ClaimType.OPINION
            },
            {
                'text': 'British historian Graeme Rendall stated "the evidence is inconclusive" and noted that vintage paper could have been used to create forgeries, and documents lacked protocol numbers or official stamps typical of Italian government communications.',
                'context': 'Historical analysis raising authentication concerns',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'giuseppe_stilo',
                'confidence': 0.8,
                'entities': ['Graeme Rendall'],
                'tags': ['authentication-concerns', 'forgery-possibility', 'missing-protocols'],
                'claim_type': ClaimType.OPINION
            },
            {
                'text': 'The telegram described the UFO traveling at 130 km/h, which skeptics note is too slow for an advanced craft and within the speed range of 1930s Italian fighter aircraft.',
                'context': 'Speed anomaly raising authenticity questions',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'giuseppe_stilo',
                'confidence': 0.7,
                'entities': [],
                'tags': ['speed-anomaly', 'authentication-concerns', 'technical-inconsistency'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'David Grusch testified to Congress that the US has recovered "non-human" spacecraft and that he was informed of a "multi-decade UAP crash retrieval and reverse engineering program" during his intelligence work.',
                'context': 'Broader context of Grusch whistleblower claims',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'david_grusch',
                'confidence': 0.6,
                'entities': ['David Grusch', 'National Reconnaissance Office'],
                'tags': ['grusch-testimony', 'crash-retrieval-program', 'reverse-engineering', 'congressional-testimony'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Grusch specifically claimed the Italian UFO was part of a broader pattern of crash retrievals, stating "I was told about the Italian UFO" and that US intelligence was aware of Mussolini\'s recovery operation.',
                'context': 'Grusch linking Italian case to broader retrieval program',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'david_grusch',
                'confidence': 0.5,
                'entities': ['David Grusch'],
                'tags': ['italy-connection', 'crash-retrieval-pattern', 'us-intelligence-knowledge'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The documents allegedly mention Vatican involvement or knowledge of the UFO incident, though specific details are not provided in available materials.',
                'context': 'Vatican connection alleged in documents',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'roberto_pinotti',
                'confidence': 0.3,
                'entities': ['Vatican'],
                'tags': ['vatican', 'religious-institution', 'alleged-knowledge'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The alleged 1945 US retrieval would have been conducted by OSS (Office of Strategic Services, predecessor to CIA) agents operating in Italy at the end of World War II.',
                'context': 'US intelligence operation to retrieve Italian UFO',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'david_grusch',
                'confidence': 0.4,
                'entities': ['OSS'],
                'tags': ['oss', 'cia-predecessor', '1945', 'us-retrieval', 'post-wwii-operations'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Pinotti states the documents were mailed to him anonymously with no return address, making source verification impossible and raising questions about their provenance.',
                'context': 'Document chain of custody concerns',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'roberto_pinotti',
                'confidence': 0.8,
                'entities': ['Roberto Pinotti'],
                'tags': ['anonymous-source', 'provenance-concerns', 'chain-of-custody'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The alleged crash occurred on June 13, 1933 in Magenta, a town in Northern Italy near Milan, in an area that would later become significant for Italian aviation and aerospace industry.',
                'context': 'Geographic and temporal context of alleged crash',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'roberto_pinotti',
                'confidence': 0.5,
                'entities': ['Magenta', 'Milan', 'Northern Italy'],
                'tags': ['crash-location', 'june-1933', 'northern-italy', 'geographic-context'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'If authentic, this case would represent the earliest documented government UFO crash retrieval operation, predating the 1947 Roswell incident by 14 years and potentially reshaping UFO crash retrieval chronology.',
                'context': 'Historical significance of the claim',
                'source': 'italy_ufo_1933_dailymail_report',
                'speaker': 'roberto_pinotti',
                'confidence': 0.4,
                'entities': [],
                'tags': ['pre-roswell', 'historical-significance', 'chronology', 'first-case'],
                'claim_type': ClaimType.OPINION
            }
        ]

        claim_ids = []
        for i, claim_data in enumerate(key_claims):
            claim_id = f"italy_ufo_claim_{i:04d}"

            claim = EvidenceClaim(
                claim_id=claim_id,
                source_id=claim_data['source'],
                speaker_id=claim_data['speaker'],
                claim_type=claim_data['claim_type'],
                text=claim_data['text'],
                confidence=claim_data['confidence'],
                start_time=None,
                end_time=None,
                page_number=None,
                context=claim_data['context'],
                entities=claim_data['entities'],
                tags=['italy-ufo', '1933-crash', 'pre-roswell', 'mussolini'] + claim_data['tags'],
                created_at=datetime.now().isoformat()
            )

            self.db.add_evidence_claim(claim)
            claim_ids.append(claim_id)

        print(f"  ✅ Extracted {len(claim_ids)} key claims")
        return claim_ids

    def save_checkpoint(self, stats: Dict):
        """Save integration checkpoint"""
        checkpoint_path = self.checkpoint_dir / "italy_ufo_integration_checkpoint.json"
        stats['timestamp'] = datetime.now().isoformat()

        with open(checkpoint_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n  ✅ Checkpoint saved: {checkpoint_path}")


def main():
    """Integrate Italian UFO (1933) evidence into Sherlock"""
    print("=" * 70)
    print("Italian UFO Crash (1933) Evidence Integration")
    print("=" * 70)

    integrator = ItalyUFOIntegrator("/home/johnny5/Sherlock/evidence.db")

    # Add speakers
    integrator.add_speakers()

    # Create evidence sources
    integrator.create_evidence_sources()

    # Extract claims
    claim_ids = integrator.extract_key_claims()

    # Save checkpoint
    stats = {
        'speakers_added': 5,
        'sources_created': 1,
        'claims_extracted': len(claim_ids)
    }
    integrator.save_checkpoint(stats)

    print("\n" + "=" * 70)
    print("✅ Italian UFO (1933) Evidence Integration Complete")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Speakers: {stats['speakers_added']}")
    print(f"  - Sources: {stats['sources_created']}")
    print(f"  - Claims: {stats['claims_extracted']}")
    print(f"\nPattern Analysis:")
    print(f"  - Pre-Roswell crash retrieval allegation (14 years earlier)")
    print(f"  - Fascist government suppression and study program")
    print(f"  - Post-WWII US intelligence retrieval (OSS → CIA connection)")
    print(f"  - Modern whistleblower testimony (David Grusch)")
    print(f"  - Forensic authentication mixed with significant skepticism")
    print(f"  - Potential connection to Thread 3 Soviet UFO research")


if __name__ == "__main__":
    main()
