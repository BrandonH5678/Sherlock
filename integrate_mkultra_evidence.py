#!/usr/bin/env python3
"""
MK-Ultra Evidence Integration
Integrates CIA mind control program intelligence into Sherlock

MK-Ultra represents DOMESTIC CIA operations (illegal) with connections to:
- JFK assassination (Dr. Jolly West evaluated Jack Ruby)
- Counterculture manipulation (Haight-Ashbury operations)
- Illegal domestic surveillance (CHAOS, COINTELPRO overlap)

Pattern: Illegal CIA domestic operations with systematic cover-up
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class MKUltraIntegrator:
    """Integrate MK-Ultra CIA mind control intelligence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("mkultra_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in MK-Ultra research
        self.entities = {
            'people': [
                'Dr. Louis Jolyon West', 'Sidney Gottlieb', 'Allen Dulles',
                'Charles Manson', 'Roger Smith', 'Jack Ruby',
                'Sharon Tate', 'Shahrokh Hatami'
            ],
            'organizations': [
                'CIA', 'MK-Ultra', 'FBI', 'LAPD',
                'Haight-Ashbury Free Medical Clinic',
                'UCLA', 'Operation CHAOS', 'COINTELPRO'
            ],
            'locations': [
                'Haight-Ashbury', 'San Francisco', 'Los Angeles',
                'Dallas', 'Washington DC'
            ],
            'operations': [
                'MK-Ultra', 'Operation CHAOS', 'COINTELPRO',
                'San Francisco Project', 'Amphetamine Research Project'
            ]
        }

    def add_speakers(self):
        """Add key MK-Ultra speakers to database"""
        print("\n📋 Adding MK-Ultra speakers...")

        speakers = [
            Speaker(
                speaker_id="dr_jolly_west",
                name="Dr. Louis Jolyon 'Jolly' West",
                title="UCLA Psychiatry Chair & MK-Ultra Researcher",
                organization="UCLA / CIA MK-Ultra Program",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1953-01-01T00:00:00",
                last_seen="1999-01-02T00:00:00"
            ),
            Speaker(
                speaker_id="sidney_gottlieb",
                name="Sidney Gottlieb",
                title="CIA MK-Ultra Program Director",
                organization="CIA Technical Services Division",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1951-01-01T00:00:00",
                last_seen="1973-01-01T00:00:00"
            ),
            Speaker(
                speaker_id="roger_smith_parole",
                name="Roger Smith",
                title="Parole Officer & Amphetamine Researcher",
                organization="California Department of Corrections / Haight-Ashbury Free Medical Clinic",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1967-03-21T00:00:00",
                last_seen="1969-08-01T00:00:00"
            ),
            Speaker(
                speaker_id="charles_manson",
                name="Charles Manson",
                title="Career Criminal & Cult Leader",
                organization="Manson Family",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1967-03-21T00:00:00",
                last_seen="1969-08-09T00:00:00"
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
        """Create MK-Ultra evidence sources"""
        print("\n📄 Creating evidence sources...")

        sources = [
            EvidenceSource(
                source_id="mkultra_manson_analysis_2025",
                title="MK-Ultra, Charles Manson, and CIA Counterculture Operations",
                url="https://lareviewofbooks.org/article/down-the-manson-rabbit-hole/",
                file_path=None,
                evidence_type=EvidenceType.WEB_ARCHIVE,
                duration=None,
                page_count=None,
                created_at="2019-06-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'MK-Ultra CIA Mind Control',
                    'topic': 'Illegal domestic CIA operations, mind control research, counterculture manipulation',
                    'source_type': 'Los Angeles Review of Books - Tom O\'Neill "Chaos" book review',
                    'significance': 'Documents CIA domestic operations, connects to JFK via Jack Ruby',
                    'pattern': 'Illegal CIA domestic ops, systematic cover-up, destroyed records'
                }
            ),
            EvidenceSource(
                source_id="mkultra_manson_bookforum_2019",
                title="Chaos: Charles Manson, the CIA, and the Secret History of the Sixties",
                url="https://www.bookforum.com/print/2602/chaos-charles-manson-the-cia-and-the-secret-history-of-the-sixties-by-tom-o-neill-21984",
                file_path=None,
                evidence_type=EvidenceType.WEB_ARCHIVE,
                duration=None,
                page_count=None,
                created_at="2019-06-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'MK-Ultra CIA Mind Control',
                    'topic': 'Manson case anomalies, parole officer CIA connections, prosecutorial misconduct',
                    'source_type': 'Bookforum - Tom O\'Neill book review',
                    'significance': 'Documents specific investigative findings, law enforcement failures',
                    'pattern': 'Cover-up, withheld evidence, intelligence agent involvement'
                }
            ),
            EvidenceSource(
                source_id="mkultra_manson_smith_west_2025",
                title="MK-Ultra Connections: Roger Smith and Dr. Jolly West at Haight-Ashbury",
                url=None,
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="2025-10-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'MK-Ultra CIA Mind Control',
                    'topic': 'Geographic/temporal overlap between Manson parole officer and CIA MK-Ultra researcher',
                    'analysis_type': 'Intelligence analysis of Haight-Ashbury operations',
                    'significance': 'Documents CIA presence in same location/time as Manson operations'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✅ {source.source_id}")

    def extract_key_claims(self):
        """Extract key claims from MK-Ultra research"""
        print("\n🔍 Extracting key claims...")

        key_claims = [
            {
                'text': 'Dr. Louis Jolyon "Jolly" West was UCLA psychiatry chair and suspected MK-Ultra researcher who worked with Sidney Gottlieb to devise the blueprint for MK-Ultra in early 1950s.',
                'context': 'MK-Ultra origins and key personnel',
                'source': 'mkultra_manson_analysis_2025',
                'speaker': 'dr_jolly_west',
                'confidence': 1.0,
                'entities': ['Dr. Louis Jolyon West', 'Sidney Gottlieb', 'MK-Ultra', 'CIA', 'UCLA'],
                'tags': ['mkultra', 'mind-control', 'cia-researcher', 'psychiatry', '1950s']
            },
            {
                'text': 'Dr. Jolly West reported to CIA about replacing "true memories with false ones" using hypnosis and LSD as part of MK-Ultra research.',
                'context': 'MK-Ultra mind control techniques',
                'source': 'mkultra_manson_analysis_2025',
                'speaker': 'dr_jolly_west',
                'confidence': 1.0,
                'entities': ['Dr. Louis Jolyon West', 'CIA', 'MK-Ultra'],
                'tags': ['hypnosis', 'lsd', 'false-memories', 'mind-control-techniques']
            },
            {
                'text': 'Dr. Jolly West was present when Jack Ruby suffered psychotic break in Dallas jail cell after JFK assassination.',
                'context': 'MK-Ultra connection to JFK assassination',
                'source': 'mkultra_manson_bookforum_2019',
                'speaker': 'dr_jolly_west',
                'confidence': 1.0,
                'entities': ['Dr. Louis Jolyon West', 'Jack Ruby', 'JFK', 'Dallas'],
                'tags': ['jack-ruby', 'jfk-assassination', 'psychotic-break', 'dallas-jail', 'cross-reference-jfk']
            },
            {
                'text': 'Dr. Jolly West kept office at Haight-Ashbury Free Medical Clinic in 1967, same location and time Manson and followers frequently visited.',
                'context': 'Geographic/temporal overlap West and Manson',
                'source': 'mkultra_manson_analysis_2025',
                'speaker': 'dr_jolly_west',
                'confidence': 1.0,
                'entities': ['Dr. Louis Jolyon West', 'Charles Manson', 'Haight-Ashbury Free Medical Clinic', 'San Francisco'],
                'tags': ['haight-ashbury', '1967', 'geographic-overlap', 'temporal-overlap']
            },
            {
                'text': 'Dr. Jolly West ran a "laboratory" disguised as a "hippie crash pad" funded by CIA.',
                'context': 'CIA covert domestic operations infrastructure',
                'source': 'mkultra_manson_bookforum_2019',
                'speaker': 'dr_jolly_west',
                'confidence': 0.9,
                'entities': ['Dr. Louis Jolyon West', 'CIA', 'Haight-Ashbury'],
                'tags': ['covert-facility', 'hippie-crash-pad', 'cia-funding', 'domestic-operations']
            },
            {
                'text': 'Charles Manson released on parole March 21, 1967. Parole officer Roger Smith was criminology Ph.D. who reduced client load to just Manson.',
                'context': 'Unusual parole arrangement for Manson',
                'source': 'mkultra_manson_bookforum_2019',
                'speaker': 'roger_smith_parole',
                'confidence': 1.0,
                'entities': ['Charles Manson', 'Roger Smith'],
                'tags': ['parole', '1967', 'unusual-treatment', 'exclusive-caseload']
            },
            {
                'text': 'Roger Smith directed Manson to report to Haight-Ashbury Free Medical Clinic where Smith was running Amphetamine Research Project studying links between drug use and collective violence.',
                'context': 'Parole officer research involving Manson',
                'source': 'mkultra_manson_smith_west_2025',
                'speaker': 'roger_smith_parole',
                'confidence': 1.0,
                'entities': ['Roger Smith', 'Charles Manson', 'Haight-Ashbury Free Medical Clinic'],
                'tags': ['amphetamine-research', 'collective-violence', 'drug-research', 'san-francisco-project']
            },
            {
                'text': 'Manson arrested at least 10 times between 1967-1969. Roger Smith never revoked parole despite repeated arrests.',
                'context': 'Inexplicable law enforcement leniency',
                'source': 'mkultra_manson_analysis_2025',
                'speaker': 'charles_manson',
                'confidence': 1.0,
                'entities': ['Charles Manson', 'Roger Smith'],
                'tags': ['arrests', 'parole-violations', 'law-enforcement-leniency', 'unexplained-protection']
            },
            {
                'text': 'Mid-1968 Roger Smith supervisor tried to intervene in Manson case but was overruled by Washington DC headquarters.',
                'context': 'Federal intervention in local parole case',
                'source': 'mkultra_manson_bookforum_2019',
                'speaker': 'roger_smith_parole',
                'confidence': 1.0,
                'entities': ['Roger Smith', 'Charles Manson', 'Washington DC'],
                'tags': ['federal-intervention', 'washington-override', '1968', 'headquarters-directive']
            },
            {
                'text': 'Operation CHAOS (CIA domestic spying) and COINTELPRO (FBI counterintelligence) both began in 1967, same year as Manson parole and Haight-Ashbury operations.',
                'context': 'Temporal overlap of domestic intelligence operations',
                'source': 'mkultra_manson_analysis_2025',
                'speaker': 'allen_dulles',
                'confidence': 1.0,
                'entities': ['Operation CHAOS', 'COINTELPRO', 'CIA', 'FBI'],
                'tags': ['operation-chaos', 'cointelpro', '1967', 'domestic-spying', 'counterculture-targeting']
            },
            {
                'text': 'CIA allegedly attempted to create "Manchurian Candidate" style programmed assassins through MK-Ultra mind control research.',
                'context': 'MK-Ultra assassination programming objective',
                'source': 'mkultra_manson_analysis_2025',
                'speaker': 'sidney_gottlieb',
                'confidence': 0.8,
                'entities': ['CIA', 'MK-Ultra'],
                'tags': ['manchurian-candidate', 'assassination-programming', 'mind-control', 'covert-objective']
            },
            {
                'text': 'Shahrokh Hatami (Sharon Tate photographer) claimed he learned of Tate murders from intelligence agent before police were notified.',
                'context': 'Intelligence foreknowledge of Manson murders',
                'source': 'mkultra_manson_bookforum_2019',
                'speaker': 'charles_manson',
                'confidence': 0.9,
                'entities': ['Shahrokh Hatami', 'Sharon Tate', 'Charles Manson'],
                'tags': ['foreknowledge', 'intelligence-agent', 'tate-murders', 'suspicious-timing']
            },
            {
                'text': 'Deputy DA disclosed orders to keep Manson name out of Beausoleil trial before Manson was charged. Sheriff interviews with witnesses withheld from defense team.',
                'context': 'Prosecutorial misconduct and evidence suppression',
                'source': 'mkultra_manson_bookforum_2019',
                'speaker': 'charles_manson',
                'confidence': 1.0,
                'entities': ['Charles Manson', 'LAPD'],
                'tags': ['prosecutorial-misconduct', 'withheld-evidence', 'cover-up', 'due-process-violation']
            },
            {
                'text': 'Taped confession about undiscovered Manson murders seized by LA district attorney office and never disclosed.',
                'context': 'Evidence suppression by prosecutors',
                'source': 'mkultra_manson_bookforum_2019',
                'speaker': 'charles_manson',
                'confidence': 1.0,
                'entities': ['Charles Manson', 'LAPD'],
                'tags': ['seized-evidence', 'undisclosed-confession', 'cover-up', 'prosecutor-suppression']
            },
            {
                'text': 'Roger Smith "San Francisco Project" revealed as CIA front operation.',
                'context': 'CIA cover for domestic operations',
                'source': 'mkultra_manson_smith_west_2025',
                'speaker': 'roger_smith_parole',
                'confidence': 0.9,
                'entities': ['Roger Smith', 'CIA', 'San Francisco'],
                'tags': ['cia-front', 'san-francisco-project', 'cover-operation', 'domestic-ops']
            },
            {
                'text': 'Geographic hub: Haight-Ashbury Free Medical Clinic served as convergence point for Dr. Jolly West (MK-Ultra), Roger Smith (Amphetamine Research), and Charles Manson (frequent visitor) in 1967-1968.',
                'context': 'Structural analysis of geographic convergence',
                'source': 'mkultra_manson_smith_west_2025',
                'speaker': 'dr_jolly_west',
                'confidence': 1.0,
                'entities': ['Dr. Louis Jolyon West', 'Roger Smith', 'Charles Manson', 'Haight-Ashbury Free Medical Clinic'],
                'tags': ['geographic-hub', 'convergence-point', 'operational-overlap', 'structural-analysis']
            },
            {
                'text': 'Pattern: Illegal CIA domestic operations (MK-Ultra, Operation CHAOS) with systematic destruction of records. CIA destroyed most MK-Ultra files in 1973 when program exposure imminent.',
                'context': 'Cover-up pattern analysis',
                'source': 'mkultra_manson_analysis_2025',
                'speaker': 'sidney_gottlieb',
                'confidence': 1.0,
                'entities': ['CIA', 'MK-Ultra', 'Operation CHAOS'],
                'tags': ['destroyed-records', 'systematic-cover-up', '1973', 'evidence-destruction', 'pattern-analysis']
            }
        ]

        claim_ids = []
        for i, claim_data in enumerate(key_claims):
            claim_id = f"mkultra_claim_{i:04d}"

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
                tags=['mkultra', 'cia-domestic-ops', 'mind-control', 'illegal-operations'] + claim_data['tags'],
                created_at=datetime.now().isoformat()
            )

            self.db.add_evidence_claim(claim)
            claim_ids.append(claim_id)

        print(f"  ✅ Extracted {len(claim_ids)} key claims")
        return claim_ids

    def save_checkpoint(self, stats: Dict):
        """Save integration checkpoint"""
        checkpoint_path = self.checkpoint_dir / "mkultra_integration_checkpoint.json"
        stats['timestamp'] = datetime.now().isoformat()

        with open(checkpoint_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n  ✅ Checkpoint saved: {checkpoint_path}")


def main():
    """Integrate MK-Ultra evidence into Sherlock"""
    print("=" * 70)
    print("MK-Ultra CIA Mind Control Intelligence Integration")
    print("=" * 70)

    integrator = MKUltraIntegrator("/home/johnny5/Sherlock/evidence.db")

    # Add speakers
    integrator.add_speakers()

    # Create evidence sources
    integrator.create_evidence_sources()

    # Extract claims
    claim_ids = integrator.extract_key_claims()

    # Save checkpoint
    stats = {
        'speakers_added': 4,
        'sources_created': 3,
        'claims_extracted': len(claim_ids)
    }
    integrator.save_checkpoint(stats)

    print("\n" + "=" * 70)
    print("✅ MK-Ultra Evidence Integration Complete")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Speakers: {stats['speakers_added']}")
    print(f"  - Sources: {stats['sources_created']}")
    print(f"  - Claims: {stats['claims_extracted']}")
    print(f"\nKey Connections:")
    print(f"  - JFK assassination (Dr. West evaluated Jack Ruby)")
    print(f"  - Geographic hub (Haight-Ashbury convergence point)")
    print(f"  - Illegal domestic operations (CHAOS, COINTELPRO overlap)")
    print(f"  - Systematic cover-up (destroyed MK-Ultra records)")
    print(f"  - Allen Dulles approved MK-Ultra as CIA Director (cross-reference S&C)")


if __name__ == "__main__":
    main()
