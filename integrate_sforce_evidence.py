#!/usr/bin/env python3
"""
S-Force Evidence Integration
Integrates S-Force Cuban paramilitary intelligence into Sherlock evidence database

Architecture: Similar to JFK/Thread 3 integration
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


class SForceEvidenceIntegrator:
    """Integrate S-Force intelligence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("sforce_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in S-Force research
        self.entities = {
            'people': [
                'Felix Rodriguez', 'Luis Posada', 'Rafael "Chi Chi" Quintero',
                'Eugenio Martinez', 'Howard Hunt', 'Ed Wilson',
                'Guillermo Hernandez Cartaya', 'Duney Perez Alamo',
                'Gaspar Jimenez', 'Nestor "Tony" Izquierdo',
                'Juan Perez-Franco', 'Angel Ferrer', 'Felipe de Diego',
                'James McCord', 'Richard Nixon', 'Ronald Reagan',
                'Fidel Castro', 'Richard Bissell', 'Allen Dulles'
            ],
            'organizations': [
                'S-Force', 'Brigade 2506', 'Operation 40', 'CIA',
                'CORU', 'Ex-Combatientes de Fort Jackson',
                'World Finance Corporation', 'DIA', 'Christic Institute',
                'Miami Organized Crime Bureau'
            ],
            'operations': [
                'Bay of Pigs', 'Watergate', 'Operation Eagle',
                'Iran-Contra', 'Operation 40'
            ],
            'locations': [
                'Miami', 'Fort Jackson', 'Fort Benning', 'Ilopango Air Base',
                'Cuba', 'El Salvador', 'Mexico', 'Argentina', 'Chile'
            ]
        }

    def add_speakers(self):
        """Add key S-Force speakers to database"""
        print("\n📋 Adding S-Force speakers...")

        speakers = [
            Speaker(
                speaker_id="peter_dale_scott",
                name="Peter Dale Scott",
                title="Researcher - US Covert Politics",
                organization="Pacific News Service",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1987-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="felix_rodriguez",
                name="Felix Rodriguez",
                title="CIA Operative - Bay of Pigs Veteran",
                organization="CIA / Brigade 2506",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1961-01-01T00:00:00",
                last_seen="1990-01-01T00:00:00"
            ),
            Speaker(
                speaker_id="howard_hunt",
                name="Howard Hunt",
                title="CIA Officer - Watergate Organizer",
                organization="Central Intelligence Agency",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1950-01-01T00:00:00",
                last_seen="2007-01-23T00:00:00"
            )
        ]

        for speaker in speakers:
            self.db.add_speaker(speaker)
            print(f"  ✅ {speaker.name}")

    def create_evidence_sources(self):
        """Create S-Force evidence sources"""
        print("\n📄 Creating evidence sources...")

        sources = [
            EvidenceSource(
                source_id="sforce_contragate_article_1987",
                title="Contragate's Second Secret Team - The Cuban S-Force",
                url="https://digitalrepository.unm.edu/noticen/480",
                file_path="/home/johnny5/Sherlock/evidence/sforce_contragate_article.txt",
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=2,
                created_at="1987-03-04T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'S-Force Cuban Paramilitary Operations',
                    'topic': 'CIA Cuban exile covert operations',
                    'author': 'Peter Dale Scott',
                    'publication': 'Pacific News Service',
                    'date_published': '1987-03-04',
                    'significance': 'First public documentation of S-Force elite Cuban CIA unit'
                }
            ),
            EvidenceSource(
                source_id="frus_1958_60_cuba_operations",
                title="FRUS 1958-60 Vol VI Doc 481 - Proposed Operations Against Cuba",
                url="https://history.state.gov/historicaldocuments/frus1958-60v06/d481",
                file_path=None,
                evidence_type=EvidenceType.WEB_ARCHIVE,
                duration=None,
                page_count=None,
                created_at="1960-01-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'S-Force Cuban Paramilitary Operations',
                    'topic': 'CIA covert action planning Cuba',
                    'classification': 'Declassified',
                    'source': 'Foreign Relations of the United States'
                }
            ),
            EvidenceSource(
                source_id="frus_1961_63_cuba_covert_ops",
                title="FRUS 1961-63 Vol X Doc 46 - Covert Operations Cuba",
                url="https://history.state.gov/historicaldocuments/frus1961-63v10/d46",
                file_path=None,
                evidence_type=EvidenceType.WEB_ARCHIVE,
                duration=None,
                page_count=None,
                created_at="1962-01-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'S-Force Cuban Paramilitary Operations',
                    'topic': 'Bay of Pigs and post-invasion operations',
                    'classification': 'Declassified',
                    'source': 'Foreign Relations of the United States'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✅ {source.source_id}")

    def extract_key_claims(self):
        """Extract key claims from S-Force research"""
        print("\n🔍 Extracting key claims...")

        key_claims = [
            {
                'text': 'American "secret team" behind illegal contra supply operation had shadow arm - second "secret team" of Cuban exiles and Bay of Pigs veterans who played key roles in Watergate and financed activities through drug operations.',
                'context': 'Editor\'s note describing S-Force structure',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['S-Force', 'CIA', 'Brigade 2506', 'Watergate'],
                'tags': ['sforce', 'cuban-exiles', 'secret-team', 'drug-financing']
            },
            {
                'text': 'Cuban secret team work included assassination efforts, major terrorist operations, and famous Watergate burglaries under President Nixon. Some members arrested in 1970 in Operation Eagle - largest federal narcotics enforcement operation ever up to that time.',
                'context': 'S-Force operational activities and criminal connections',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['S-Force', 'Watergate', 'Operation Eagle', 'Richard Nixon'],
                'tags': ['assassination', 'terrorism', 'watergate', 'narcotics']
            },
            {
                'text': 'Felix Rodriguez and Luis Posada were Cubans in charge of loading ill-fated Hasenfus supply plane at Ilopango air base in El Salvador. Working in contra supply operation with other ex-CIA Cubans recruited through Brigade 2506.',
                'context': 'Iran-Contra operations S-Force involvement',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['Felix Rodriguez', 'Luis Posada', 'Brigade 2506', 'Ilopango Air Base'],
                'tags': ['iran-contra', 'el-salvador', 'brigade-2506']
            },
            {
                'text': 'Brigade 2506 President Juan Perez-Franco made Brigade support for contras official in 1985. A decade earlier paved way for Brigade entrance into CORU - Cuban exile terrorist alliance supported by military governments of Chile and Argentina.',
                'context': 'Brigade 2506 connection to CORU terrorist network',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['Juan Perez-Franco', 'Brigade 2506', 'CORU', 'Chile', 'Argentina'],
                'tags': ['coru', 'terrorism', 'chile', 'argentina']
            },
            {
                'text': 'CORU funded by Miami-based World Finance Corporation, set up in 1971 by Brigade 2506 veteran Guillermo Hernandez Cartaya. House Committee found WFC activities included political corruption, gunrunning, and narcotics trafficking on international level.',
                'context': 'World Finance Corporation criminal financing network',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['World Finance Corporation', 'Guillermo Hernandez Cartaya', 'CORU'],
                'tags': ['money-laundering', 'narcotics', 'gunrunning', 'corruption']
            },
            {
                'text': 'S-Force members were elite specialists trained in sabotage and black arts, much smaller than Brigade 2506. At least three S-Force members in touch with renegade ex-CIA agent Ed Wilson.',
                'context': 'S-Force elite unit structure and Ed Wilson connection',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['S-Force', 'Ed Wilson', 'Brigade 2506'],
                'tags': ['sabotage', 'ed-wilson', 'elite-unit']
            },
            {
                'text': 'Howard Hunt attended Brigade 2506 tenth anniversary meeting in 1971 to recruit future Watergate burglars for Nixon White House "plumbers" counterintelligence break-in teams. Hunt went to elite counterintelligence operation of CIA Miami station.',
                'context': 'Watergate recruitment from S-Force operatives',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['Howard Hunt', 'Brigade 2506', 'Watergate', 'CIA', 'Miami'],
                'tags': ['watergate', '1971', 'recruitment', 'plumbers']
            },
            {
                'text': 'Most of elite 150 men were Bay of Pigs veterans who underwent further army training at Fort Jackson. Others like Rodriguez and Posada sent for officer training at Fort Benning. Some recruited to work for CIA.',
                'context': 'S-Force training and military integration',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['Fort Jackson', 'Fort Benning', 'Felix Rodriguez', 'Luis Posada', 'CIA'],
                'tags': ['training', 'military', 'fort-jackson', 'fort-benning']
            },
            {
                'text': 'Counterintelligence operation known as Operation 40 had to be closed down in early 1970s after one of its planes crashed in Southern California with several kilos of cocaine and heroin aboard. Rodriguez and Posada identified as Operation 40 members.',
                'context': 'Operation 40 drug smuggling exposure',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['Operation 40', 'Felix Rodriguez', 'Luis Posada', 'CIA'],
                'tags': ['operation-40', 'drug-smuggling', 'cocaine', 'heroin']
            },
            {
                'text': 'Among those in Hunt first Watergate break-in never arrested: Angel Ferrer (president of Ex-Combatientes), Felipe de Diego (Operation 40 member). Eugenio Martinez (Operation 40, on CIA payroll) arrested June 17, 1972 with Hunt and McCord.',
                'context': 'Watergate break-in participants from S-Force',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['Angel Ferrer', 'Felipe de Diego', 'Eugenio Martinez', 'Howard Hunt', 'James McCord', 'Operation 40'],
                'tags': ['watergate', '1972', 'break-in', 'operation-40']
            },
            {
                'text': 'Most important S-Force task was assassination of Fidel Castro. Rafael "Chi Chi" Quintero identified by Business Week as man "who played key role in Bay of Pigs invasion and in subsequent efforts to assassinate Fidel Castro."',
                'context': 'S-Force assassination mission',
                'source': 'sforce_contragate_article_1987',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['Rafael "Chi Chi" Quintero', 'Fidel Castro', 'S-Force', 'Bay of Pigs'],
                'tags': ['assassination', 'castro', 'bay-of-pigs']
            },
            {
                'text': 'CIA directed to organize opposition to Castro regime. Planned to develop propaganda channels, clandestine agent networks within Cuba, and trained paramilitary ground and air forces in Central America.',
                'context': 'FRUS 1961-63 covert operations planning',
                'source': 'frus_1961_63_cuba_covert_ops',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['CIA', 'Fidel Castro', 'Cuba'],
                'tags': ['covert-ops', 'paramilitary', 'propaganda']
            },
            {
                'text': 'CIA recruiting and training paramilitary cadres in locations outside U.S. Objective: organize and lead resistance forces in Cuba. Estimated development time: 6-8 months. Limited air capability for resupply and infiltration already exists under CIA control.',
                'context': 'FRUS 1958-60 paramilitary force development',
                'source': 'frus_1958_60_cuba_operations',
                'speaker': 'peter_dale_scott',
                'confidence': 1.0,
                'entities': ['CIA', 'Cuba'],
                'tags': ['paramilitary', 'training', 'infiltration', '1958-1960']
            }
        ]

        claim_ids = []
        for i, claim_data in enumerate(key_claims):
            claim_id = f"sforce_claim_{i:04d}"

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
                tags=['sforce', 'cuban-exiles', 'cia-operations'] + claim_data['tags'],
                created_at=datetime.now().isoformat()
            )

            self.db.add_evidence_claim(claim)
            claim_ids.append(claim_id)

        print(f"  ✅ Extracted {len(claim_ids)} key claims")
        return claim_ids

    def save_checkpoint(self, stats: Dict):
        """Save integration checkpoint"""
        checkpoint_path = self.checkpoint_dir / "sforce_integration_checkpoint.json"
        stats['timestamp'] = datetime.now().isoformat()

        with open(checkpoint_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n  ✅ Checkpoint saved: {checkpoint_path}")


def main():
    """Integrate S-Force evidence into Sherlock"""
    print("=" * 70)
    print("S-Force Evidence Integration")
    print("=" * 70)

    integrator = SForceEvidenceIntegrator("/home/johnny5/Sherlock/evidence.db")

    # Add speakers
    integrator.add_speakers()

    # Create evidence sources
    integrator.create_evidence_sources()

    # Extract claims
    claim_ids = integrator.extract_key_claims()

    # Save checkpoint
    stats = {
        'speakers_added': 3,
        'sources_created': 3,
        'claims_extracted': len(claim_ids)
    }
    integrator.save_checkpoint(stats)

    print("\n" + "=" * 70)
    print("✅ S-Force Evidence Integration Complete")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Speakers: {stats['speakers_added']}")
    print(f"  - Sources: {stats['sources_created']}")
    print(f"  - Claims: {stats['claims_extracted']}")


if __name__ == "__main__":
    main()
