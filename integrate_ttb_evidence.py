#!/usr/bin/env python3
"""
Thomas Townsend Brown Evidence Integration
Integrates evidence from T. Townsend Brown electrokinetics/electrogravitic research into Sherlock

Key Intelligence:
- Electrokinetic propulsion research (1920s-1980s)
- Navy Research Laboratory connections
- Project Winterhaven (classified electrokinetic weapons proposal)
- Post-WWII German technology retrieval mission (1945)
- Potential connection to UFO propulsion research
- Patents: Cellular gravitator (1928), Electrokinetics fan (1988)
- Multiple research locations: Caltech, Navy, SRI, Hawaii

Architecture: Similar to Italy UFO/MK-Ultra integration
Output: Evidence sources, claims, speakers, relationships
Source: https://www.thomastownsendbrown.com/misc/timeline.htm
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class ThomasTownsendBrownIntegrator:
    """Integrate T. Townsend Brown electrokinetic propulsion research evidence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("ttb_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in T. Townsend Brown research
        self.entities = {
            'people': [
                'Thomas Townsend Brown', 'Josephine Brown', 'Paul Biefeld',
                'Robert Sarbacher', 'Bradford Shank', 'Floyd Odlum',
                'Agnew Bahnson'
            ],
            'organizations': [
                'US Navy', 'Naval Research Laboratory', 'Caltech',
                'NICAP', 'Vega (Lockheed)', 'SRI', 'Guidance Technologies Inc',
                'Winterhaven Project', 'British Admiralty'
            ],
            'locations': [
                'Zanesville, Ohio', 'Pasadena, California', 'Hawaii',
                'Washington DC', 'Florida', 'North Carolina', 'Germany'
            ],
            'technologies': [
                'Electrokinetic propulsion', 'Electrogravitation',
                'Sidereal radiation detector', 'Cellular gravitator',
                'Biefeld-Brown effect'
            ],
            'operations': [
                'Project Winterhaven', 'German technology retrieval 1945',
                'Navy electrokinetics research'
            ]
        }

    def add_speakers(self):
        """Add key T. Townsend Brown speakers to database"""
        print("\n📋 Adding T. Townsend Brown speakers...")

        speakers = [
            Speaker(
                speaker_id="thomas_townsend_brown",
                name="Thomas Townsend Brown",
                title="Physicist & Electrokinetic Propulsion Researcher",
                organization="Navy Research Laboratory / SRI / Independent",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1905-03-18T00:00:00",
                last_seen="1985-10-27T00:00:00"
            ),
            Speaker(
                speaker_id="paul_biefeld",
                name="Paul Alfons Biefeld",
                title="Physicist & Scientific Mentor",
                organization="California Institute of Technology",
                voice_embedding=None,
                confidence=0.9,
                first_seen="1923-01-01T00:00:00",
                last_seen="1943-01-01T00:00:00"
            ),
            Speaker(
                speaker_id="robert_sarbacher",
                name="Robert Sarbacher",
                title="Physicist & Defense Consultant",
                organization="US Department of Defense / Research & Development Board",
                voice_embedding=None,
                confidence=0.85,
                first_seen="1945-01-01T00:00:00",
                last_seen="1986-01-01T00:00:00"
            ),
            Speaker(
                speaker_id="josephine_brown",
                name="Josephine Beale Brown",
                title="Research Collaborator & Wife",
                organization="T. Townsend Brown Research",
                voice_embedding=None,
                confidence=0.8,
                first_seen="1928-01-01T00:00:00",
                last_seen="1985-10-27T00:00:00"
            )
        ]

        for speaker in speakers:
            self.db.add_speaker(speaker)
            print(f"  ✓ Added speaker: {speaker.name}")

    def add_evidence_sources(self):
        """Add T. Townsend Brown evidence sources"""
        print("\n📄 Adding T. Townsend Brown evidence sources...")

        sources = [
            EvidenceSource(
                source_id="ttb_timeline_web",
                title="Thomas Townsend Brown Timeline - Official Biography",
                url="https://www.thomastownsendbrown.com/misc/timeline.htm",
                file_path=None,
                evidence_type=EvidenceType.WEB_ARCHIVE,
                duration=None,
                page_count=None,
                created_at="2025-10-03T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'source_type': 'official_biography',
                    'domain': 'thomastownsendbrown.com',
                    'archival_status': 'active',
                    'confidence_level': 0.75,
                    'operation': 'electrokinetic_propulsion_research',
                    'time_period': '1905-1985',
                    'classification': 'unclassified_but_sensitive'
                }
            ),
            EvidenceSource(
                source_id="ttb_winterhaven_project",
                title="Project Winterhaven - Electrokinetic Weapons Proposal",
                url=None,
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="1952-01-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'source_type': 'classified_proposal',
                    'classification': 'originally_classified',
                    'submitted_to': 'US Navy',
                    'confidence_level': 0.70,
                    'operation': 'Project Winterhaven',
                    'time_period': '1952-1953',
                    'status': 'rejected_by_navy'
                }
            ),
            EvidenceSource(
                source_id="ttb_german_retrieval_1945",
                title="T. Townsend Brown German Technology Retrieval Mission 1945",
                url=None,
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="1945-06-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'source_type': 'intelligence_operation',
                    'classification': 'classified',
                    'operation': 'Post-WWII technology retrieval',
                    'confidence_level': 0.60,
                    'time_period': '1945',
                    'location': 'Occupied Germany'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✓ Added source: {source.title}")

    def add_claims(self):
        """Add evidence claims from T. Townsend Brown timeline"""
        print("\n💡 Adding T. Townsend Brown claims...")

        claims = [
            # Early research claims
            EvidenceClaim(
                claim_id="ttb_claim_001",
                source_id="ttb_timeline_web",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="Thomas Townsend Brown conducted gravitational radiation research at California Institute of Technology (Caltech) in 1923-1924 under Dr. Paul Biefeld.",
                confidence=0.75,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Early career research establishing foundation for electrokinetic propulsion theories.",
                entities=['Thomas Townsend Brown', 'Paul Biefeld', 'Caltech', 'gravitational radiation'],
                tags=['research', 'caltech', 'early_career', '1920s', 'biefeld_brown_effect'],
                created_at=datetime.now().isoformat()
            ),
            EvidenceClaim(
                claim_id="ttb_claim_002",
                source_id="ttb_timeline_web",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="T. Townsend Brown filed patent for 'cellular gravitator' in 1928, early electrokinetic device.",
                confidence=0.80,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Patent demonstrates early development of electrokinetic propulsion concepts.",
                entities=['Thomas Townsend Brown', 'cellular gravitator', 'patent', 'electrokinetics'],
                tags=['patent', 'technology', '1928', 'electrokinetics'],
                created_at=datetime.now().isoformat()
            ),
            # Navy service and research
            EvidenceClaim(
                claim_id="ttb_claim_003",
                source_id="ttb_timeline_web",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="T. Townsend Brown served on active Navy duty 1930-1933, establishing military research connections.",
                confidence=0.85,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Navy service period establishing official military connections for later classified research.",
                entities=['Thomas Townsend Brown', 'US Navy', 'military research'],
                tags=['navy', 'military', '1930s', 'service_record'],
                created_at=datetime.now().isoformat()
            ),
            # German retrieval mission
            EvidenceClaim(
                claim_id="ttb_claim_004",
                source_id="ttb_german_retrieval_1945",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="T. Townsend Brown participated in post-WWII German technology retrieval mission in occupied Germany (1945).",
                confidence=0.60,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Intelligence operation to retrieve advanced German technologies after WWII surrender. Potential connection to Nazi electrokinetic/propulsion research.",
                entities=['Thomas Townsend Brown', 'Germany', 'technology retrieval', 'WWII', 'intelligence'],
                tags=['germany', 'wwii', '1945', 'intelligence', 'technology_transfer'],
                created_at=datetime.now().isoformat()
            ),
            # Project Winterhaven
            EvidenceClaim(
                claim_id="ttb_claim_005",
                source_id="ttb_winterhaven_project",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="Project Winterhaven proposed electrokinetic weapons system to US Navy, submitted early 1950s. Navy rejected the proposal.",
                confidence=0.70,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Classified proposal for electrokinetic propulsion-based weapons system. Rejection suggests either technical infeasibility or classification concerns.",
                entities=['Project Winterhaven', 'US Navy', 'electrokinetic weapons', 'Thomas Townsend Brown'],
                tags=['project_winterhaven', 'navy', 'classified', '1950s', 'weapons_proposal'],
                created_at=datetime.now().isoformat()
            ),
            # Hawaii research period
            EvidenceClaim(
                claim_id="ttb_claim_006",
                source_id="ttb_timeline_web",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="T. Townsend Brown conducted extended research in Hawaii 1947-1951, period coinciding with early UFO phenomena reporting.",
                confidence=0.75,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Hawaii research period coincides with 1947 Roswell incident and surge in UFO reporting. Location choice may be significant for detection or isolation purposes.",
                entities=['Thomas Townsend Brown', 'Hawaii', 'UFO phenomena', 'research'],
                tags=['hawaii', '1940s', '1950s', 'research', 'ufo_connection'],
                created_at=datetime.now().isoformat()
            ),
            # Institutional connections
            EvidenceClaim(
                claim_id="ttb_claim_007",
                source_id="ttb_timeline_web",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="T. Townsend Brown worked with Navy Research Laboratory, Lockheed (Vega division), and Stanford Research Institute (SRI) on electrokinetic research.",
                confidence=0.80,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Multiple defense contractor and military research institution connections suggest sustained classified research program.",
                entities=['Thomas Townsend Brown', 'Navy Research Laboratory', 'Lockheed', 'SRI', 'electrokinetics'],
                tags=['defense_contractors', 'research_institutions', 'navy', 'classified_research'],
                created_at=datetime.now().isoformat()
            ),
            # Robert Sarbacher connection
            EvidenceClaim(
                claim_id="ttb_claim_008",
                source_id="ttb_timeline_web",
                speaker_id="robert_sarbacher",
                claim_type=ClaimType.FACTUAL,
                text="Robert Sarbacher (DoD Research & Development Board) had documented connection to T. Townsend Brown research activities.",
                confidence=0.70,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Robert Sarbacher is also known for 1983 letter confirming UFO crash retrievals. Connection to Brown suggests electrokinetics-UFO research overlap.",
                entities=['Robert Sarbacher', 'Thomas Townsend Brown', 'DoD', 'UFO research'],
                tags=['sarbacher', 'dod', 'ufo_connection', 'research_overlap'],
                created_at=datetime.now().isoformat()
            ),
            # Late career patent
            EvidenceClaim(
                claim_id="ttb_claim_009",
                source_id="ttb_timeline_web",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="T. Townsend Brown filed electrokinetics fan patent in 1988, three years after his death (1985), suggesting continued research or posthumous patent filing.",
                confidence=0.65,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Patent filed after death raises questions about continuation of research program or delayed declassification of earlier work.",
                entities=['Thomas Townsend Brown', 'electrokinetics fan', 'patent', 'posthumous'],
                tags=['patent', '1988', 'posthumous', 'electrokinetics', 'anomaly'],
                created_at=datetime.now().isoformat()
            ),
            # NICAP involvement
            EvidenceClaim(
                claim_id="ttb_claim_010",
                source_id="ttb_timeline_web",
                speaker_id="thomas_townsend_brown",
                claim_type=ClaimType.FACTUAL,
                text="T. Townsend Brown was involved with NICAP (National Investigations Committee on Aerial Phenomena), suggesting direct UFO research connection.",
                confidence=0.75,
                start_time=None,
                end_time=None,
                page_number=None,
                context="NICAP was major UFO research organization. Brown's involvement suggests electrokinetic propulsion research connected to UFO phenomenon investigation.",
                entities=['Thomas Townsend Brown', 'NICAP', 'UFO research'],
                tags=['nicap', 'ufo_research', 'aerial_phenomena', 'investigation'],
                created_at=datetime.now().isoformat()
            )
        ]

        for claim in claims:
            self.db.add_evidence_claim(claim)
            print(f"  ✓ Added claim: {claim.claim_id}")

        print(f"\n✅ Total claims added: {len(claims)}")

    def run(self):
        """Execute full integration"""
        print("\n" + "="*80)
        print("THOMAS TOWNSEND BROWN EVIDENCE INTEGRATION")
        print("="*80)

        self.add_speakers()
        self.add_evidence_sources()
        self.add_claims()

        print("\n" + "="*80)
        print("✅ INTEGRATION COMPLETE")
        print("="*80)
        print("\nTarget Classification: TECHNOLOGY / PROPULSION RESEARCH")
        print("Operational Context: Potential connection to UFO propulsion research")
        print("Related Operations: Project Winterhaven, German tech retrieval 1945")
        print("Confidence: MEDIUM-HIGH (0.70-0.80 for most claims)")
        print("Cross-Reference: Robert Sarbacher (UFO crash retrieval), NICAP")
        print("\nNext Steps:")
        print("  - Cross-reference with Italy UFO (1933) propulsion theories")
        print("  - Investigate Robert Sarbacher UFO connections")
        print("  - Research Project Winterhaven classified status")
        print("  - Analyze German WWII electrokinetic research programs")


if __name__ == "__main__":
    integrator = ThomasTownsendBrownIntegrator()
    integrator.run()
