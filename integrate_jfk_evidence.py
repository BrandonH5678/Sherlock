#!/usr/bin/env python3
"""
JFK/Joannides Evidence Integration
Integrates JFK assassination intelligence into Sherlock evidence database

Architecture: Similar to Thread 3 integration
Output: Evidence sources, claims, speakers, relationships
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class JFKEvidenceIntegrator:
    """Integrate JFK/Joannides intelligence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("jfk_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities
        self.entities = {
            'people': [
                'George Joannides', 'David Atlee Phillips', 'Lee Harvey Oswald',
                'Dan Hardway', 'G. Robert Blakey', 'Richard Helms',
                'John McCone', 'Eddie Lopez', 'William Gaudet',
                'Johnny Roselli', 'William Harvey', 'David Robarge'
            ],
            'organizations': [
                'CIA', 'DRE', 'HSCA', 'Warren Commission', 'Church Committee',
                'ARRB', 'Fair Play for Cuba Committee', 'JMWAVE',
                'FBI', 'House Select Committee on Assassinations'
            ],
            'programs': [
                'DRE', 'JMWAVE', 'Mexico City Station', 'Miami Station'
            ],
            'locations': [
                'New Orleans', 'Mexico City', 'Miami', 'Dallas',
                'Cuban Consulate', 'Soviet Embassy', 'Langley'
            ]
        }

    def add_speakers(self):
        """Add key JFK case speakers to database"""
        print("\n📋 Adding JFK case speakers...")

        speakers = [
            Speaker(
                speaker_id="dan_hardway",
                name="Dan Hardway",
                title="HSCA Researcher",
                organization="House Select Committee on Assassinations",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1977-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="g_robert_blakey",
                name="G. Robert Blakey",
                title="Chief Counsel",
                organization="House Select Committee on Assassinations",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1977-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="george_joannides",
                name="George Joannides",
                title="CIA Officer - Psychological Warfare",
                organization="Central Intelligence Agency",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1950-01-01T00:00:00",
                last_seen="1990-01-01T00:00:00"
            ),
            Speaker(
                speaker_id="david_atlee_phillips",
                name="David Atlee Phillips",
                title="CIA Officer - Chief of Cuban Operations",
                organization="Central Intelligence Agency",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1950-01-01T00:00:00",
                last_seen="1988-01-01T00:00:00"
            ),
            Speaker(
                speaker_id="richard_helms",
                name="Richard Helms",
                title="CIA Deputy Director of Plans",
                organization="Central Intelligence Agency",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1947-01-01T00:00:00",
                last_seen="2002-10-23T00:00:00"
            )
        ]

        for speaker in speakers:
            self.db.add_speaker(speaker)
            print(f"  ✅ {speaker.name}")

    def create_evidence_sources(self):
        """Create JFK evidence sources"""
        print("\n📄 Creating evidence sources...")

        sources = [
            EvidenceSource(
                source_id="jfk_hardway_testimony_2025",
                title="Dan Hardway Congressional Testimony - JFK Assassination CIA Obstruction",
                url="https://oversight.house.gov/wp-content/uploads/2025/05/Hardway-Written-Testimony.pdf",
                file_path="/home/johnny5/Sherlock/evidence/hardway_jfk_testimony.pdf",
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=17,
                created_at="2025-05-20T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'JFK Assassination',
                    'topic': 'CIA George Joannides Cover-up',
                    'testimony_date': '2025-05-20',
                    'committee': 'House Committee on Oversight and Accountability',
                    'classification': 'Unclassified',
                    'significance': '62-year CIA cover-up revelation'
                }
            ),
            EvidenceSource(
                source_id="jfk_axios_report_2025_07",
                title="Axios Report: CIA admits shadowy officer monitored Oswald",
                url="https://www.axios.com/2025/07/05/cia-agent-oswald-kennedy-assassination",
                file_path=None,
                evidence_type=EvidenceType.WEB_ARCHIVE,
                duration=None,
                page_count=None,
                created_at="2025-07-05T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'JFK Assassination',
                    'topic': 'George Joannides document release',
                    'publication': 'Axios',
                    'date_published': '2025-07-05',
                    'documents_released': '40 Joannides files'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✅ {source.source_id}")

    def extract_key_claims(self):
        """Extract key claims from Hardway testimony"""
        print("\n🔍 Extracting key claims from testimony...")

        # Read Hardway testimony
        testimony_path = Path("/home/johnny5/Sherlock/evidence/hardway_jfk_testimony.txt")
        with open(testimony_path) as f:
            text = f.read()

        # Key factual claims to extract
        key_claims = [
            {
                'text': 'The CIA has actively and continuously obstructed the investigation of the assassination of President John F. Kennedy for 62 years with no consequences.',
                'context': 'Opening statement of Congressional testimony by HSCA researcher',
                'page': 1,
                'confidence': 1.0,
                'entities': ['CIA', 'JFK', 'HSCA'],
                'tags': ['obstruction', 'cover-up', '62-years']
            },
            {
                'text': 'George Joannides was assigned to handle liaison with Lopez and me beginning in May 1978. He began to change the way file access was handled and obstruct our investigation.',
                'context': 'HSCA researcher describing CIA obstruction operation',
                'page': 2,
                'confidence': 1.0,
                'entities': ['George Joannides', 'CIA', 'HSCA'],
                'tags': ['obstruction', 'covert-operation', '1978']
            },
            {
                'text': 'In 1978, I did not do any research into Joannides because I was not informed he had any involvement with the Kennedy case. CIA firmly represented that all ties between DRE and CIA had been terminated prior to 1963.',
                'context': 'CIA lied about Joannides and DRE connection',
                'page': 3,
                'confidence': 1.0,
                'entities': ['George Joannides', 'DRE', 'CIA'],
                'tags': ['deception', 'dre', 'false-statement']
            },
            {
                'text': 'Phillips was not in Mexico City at the time Oswald was there in 1963, contrary to his sworn testimony. He had been on temporary duty at CIA Headquarters and JMWAVE Miami station.',
                'context': 'David Atlee Phillips lied under oath about location',
                'page': 4,
                'confidence': 1.0,
                'entities': ['David Atlee Phillips', 'Oswald', 'Mexico City', 'JMWAVE'],
                'tags': ['perjury', 'mexico-city', 'october-1963']
            },
            {
                'text': 'CIA was providing DRE with $25,000 per month. Richard Helms appointed George Joannides after meeting with DRE leaders, promising case officer personally responsible to him.',
                'context': 'CIA funding and control of DRE Cuban exile group',
                'page': 5,
                'confidence': 1.0,
                'entities': ['CIA', 'DRE', 'George Joannides', 'Richard Helms'],
                'tags': ['funding', 'dre', 'helms']
            },
            {
                'text': 'In August 1963, Oswald had an encounter with DRE representatives in New Orleans resulting in widespread publicity. DRE under Joannides direct control published first conspiracy theory on day of assassination.',
                'context': 'Oswald-DRE encounter and immediate post-assassination propaganda',
                'page': 6,
                'confidence': 1.0,
                'entities': ['Oswald', 'DRE', 'George Joannides', 'New Orleans'],
                'tags': ['august-1963', 'propaganda', 'conspiracy-theory']
            },
            {
                'text': 'CIA never told Warren Commission, Church Committee, or HSCA about their support of DRE in 1963. CIA ran covert operation to keep that secret when HSCA investigated.',
                'context': 'Systematic CIA deception across all investigations',
                'page': 7,
                'confidence': 1.0,
                'entities': ['CIA', 'Warren Commission', 'Church Committee', 'HSCA', 'DRE'],
                'tags': ['cover-up', 'systematic-deception']
            },
            {
                'text': 'On September 17, 1963, Oswald applied for Mexican travel visa. Person in line in front of him was William Gaudet, a known CIA agent. Gaudet claimed coincidence.',
                'context': 'CIA agent present when Oswald got Mexico visa',
                'page': 8,
                'confidence': 0.9,
                'entities': ['Oswald', 'William Gaudet', 'CIA', 'Mexico'],
                'tags': ['september-1963', 'mexico-city', 'suspicious-coincidence']
            },
            {
                'text': 'Mexico City Station tested impulse camera at Cuban Consulate on days Oswald visited (Sept 27-28). Over 10 feet of 16mm film generated has disappeared.',
                'context': 'Missing photographic surveillance of Oswald in Mexico',
                'page': 8,
                'confidence': 1.0,
                'entities': ['Mexico City Station', 'Cuban Consulate', 'Oswald'],
                'tags': ['missing-evidence', 'photography', 'september-1963']
            },
            {
                'text': 'Phillips arrived in Miami JMWAVE on October 9, 1963 for two-day visit where Joannides was running DRE propaganda operation. This was 6 weeks before assassination.',
                'context': 'Phillips-Joannides meeting 6 weeks before JFK assassination',
                'page': 8,
                'confidence': 1.0,
                'entities': ['David Atlee Phillips', 'George Joannides', 'JMWAVE', 'DRE'],
                'tags': ['october-1963', 'miami', 'coordination']
            },
            {
                'text': 'G. Robert Blakey testified under oath: "Joannides lied to me. CIA lied to me. The Agency knowingly and corruptly obstructed our investigation in violation of 18 U.S.C. § 1505, punishable by up to 5 years imprisonment."',
                'context': 'HSCA Chief Counsel sworn testimony about CIA crimes',
                'page': 10,
                'confidence': 1.0,
                'entities': ['G. Robert Blakey', 'George Joannides', 'CIA', 'HSCA'],
                'tags': ['obstruction-of-justice', 'federal-crime', 'sworn-testimony']
            },
            {
                'text': 'CIA told ARRB in January 1998 that DRE operational files from December 1962 through April 1964 "appear to be missing". Joannides fitness reports prove he had excellent control of DRE throughout this period with $2.4M budget.',
                'context': 'CIA destroyed evidence from critical period',
                'page': 11,
                'confidence': 1.0,
                'entities': ['CIA', 'ARRB', 'DRE', 'George Joannides'],
                'tags': ['destroyed-evidence', 'missing-files', '1962-1964']
            },
            {
                'text': 'CIA admitted in Nelson Declaration (2008) that Joannides worked on covert projects only twice: 1962-1964 JMWAVE and 1978-1979 HSCA liaison. This means HSCA liaison was classified covert operation.',
                'context': 'CIA sworn admission HSCA liaison was covert operation',
                'page': 12,
                'confidence': 1.0,
                'entities': ['CIA', 'George Joannides', 'HSCA'],
                'tags': ['covert-operation', 'admitted-crime', 'illegal-domestic-operation']
            },
            {
                'text': 'Joannides fitness report July 1963: "done an excellent job in handling of significant student exile group which hitherto had successfully resisted any important degree of control." This is DRE, one month before Oswald encounter.',
                'context': 'CIA documents show Joannides controlled DRE when Oswald encountered them',
                'page': 5,
                'confidence': 1.0,
                'entities': ['George Joannides', 'DRE', 'CIA'],
                'tags': ['fitness-report', 'dre-control', 'july-1963']
            },
            {
                'text': 'CIA official historian David Robarge (2014) admitted "benign cover-up" and said CIA Director McCone was "complicit in keeping incendiary issues off Warren Commission agenda." CIA determined what was "best truth."',
                'context': 'CIA admission of covering up information from Warren Commission',
                'page': 15,
                'confidence': 1.0,
                'entities': ['David Robarge', 'John McCone', 'CIA', 'Warren Commission'],
                'tags': ['cover-up-admission', 'warren-commission', 'best-truth']
            }
        ]

        claim_ids = []
        for i, claim_data in enumerate(key_claims):
            claim_id = f"jfk_hardway_claim_{i:04d}"

            claim = EvidenceClaim(
                claim_id=claim_id,
                source_id="jfk_hardway_testimony_2025",
                speaker_id="dan_hardway",
                claim_type=ClaimType.FACTUAL,
                text=claim_data['text'],
                confidence=claim_data['confidence'],
                start_time=None,
                end_time=None,
                page_number=claim_data['page'],
                context=claim_data['context'],
                entities=claim_data['entities'],
                tags=['jfk', 'cia-obstruction', 'joannides'] + claim_data['tags'],
                created_at=datetime.now().isoformat()
            )

            self.db.add_evidence_claim(claim)
            claim_ids.append(claim_id)

        print(f"  ✅ Extracted {len(claim_ids)} key claims")
        return claim_ids

    def save_checkpoint(self, stats: Dict):
        """Save integration checkpoint"""
        checkpoint_path = self.checkpoint_dir / "jfk_integration_checkpoint.json"
        stats['timestamp'] = datetime.now().isoformat()

        with open(checkpoint_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n  ✅ Checkpoint saved: {checkpoint_path}")


def main():
    """Integrate JFK evidence into Sherlock"""
    print("=" * 70)
    print("JFK/Joannides Evidence Integration")
    print("=" * 70)

    integrator = JFKEvidenceIntegrator("/home/johnny5/Sherlock/evidence.db")

    # Add speakers
    integrator.add_speakers()

    # Create evidence sources
    integrator.create_evidence_sources()

    # Extract claims
    claim_ids = integrator.extract_key_claims()

    # Save checkpoint
    stats = {
        'speakers_added': 5,
        'sources_created': 2,
        'claims_extracted': len(claim_ids)
    }
    integrator.save_checkpoint(stats)

    print("\n" + "=" * 70)
    print("✅ JFK Evidence Integration Complete")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Speakers: {stats['speakers_added']}")
    print(f"  - Sources: {stats['sources_created']}")
    print(f"  - Claims: {stats['claims_extracted']}")


if __name__ == "__main__":
    main()
