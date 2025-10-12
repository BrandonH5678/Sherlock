#!/usr/bin/env python3
"""
Garry Nolan / Stanford UFO Research Evidence Integration
Integrates evidence from Stanford Magazine "First Contact" article into Sherlock

Key Intelligence:
- Dr. Garry Nolan (Stanford pathology professor) conducting scientific UFO/UAP analysis
- Pentagon/CIA consultation on UAP phenomena
- Material analysis from 1977 Council Bluffs incident
- Brain scan studies of military pilots/intelligence agents exposed to UAP
- Connection to Pentagon's Unidentified Aerial Phenomena Task Force
- Academic credibility brought to UFO research via Stanford affiliation
- Jacques Vallée collaboration (astrophysicist, legendary UFO researcher)

Architecture: Similar to T. Townsend Brown/Italy UFO integration
Output: Evidence sources, claims, speakers, relationships
Source: https://stanfordmag.org/contents/first-contact (July 2023)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class NolanStanfordIntegrator:
    """Integrate Garry Nolan Stanford UFO research evidence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("nolan_stanford_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in Nolan Stanford research
        self.entities = {
            'people': [
                'Garry Nolan', 'Peter Sturrock', 'Jacques Vallée',
                'Jay Stratton', 'Leslie Kean', 'David Baltimore',
                'Michael Angelo', 'Christopher Mellon', 'Lue Elizondo'
            ],
            'organizations': [
                'Stanford University', 'Stanford School of Medicine',
                'Society for Scientific Exploration', 'Pentagon',
                'Unidentified Aerial Phenomena Task Force',
                'All-Domain Anomaly Resolution Office (AARO)',
                'CIA', 'Department of Defense', 'National Cancer Institute'
            ],
            'locations': [
                'Stanford University', 'Council Bluffs Iowa',
                'Atacama Desert Chile', 'Windsor Connecticut'
            ],
            'technologies': [
                'CyTOF cellular analysis', 'brain imaging MRI',
                'UFO artifact materials', 'retroviral DNA delivery',
                'mass cytometry'
            ],
            'operations': [
                'Pentagon UAP Task Force', 'UFO artifact analysis program',
                'Military pilot brain scan study', 'Council Bluffs 1977 investigation'
            ]
        }

    def add_speakers(self):
        """Add key speakers from Stanford UFO research to database"""
        print("\n📋 Adding Stanford UFO research speakers...")

        speakers = [
            Speaker(
                speaker_id="garry_nolan",
                name="Dr. Garry Nolan",
                title="Professor of Pathology, Stanford School of Medicine",
                organization="Stanford University",
                voice_embedding=None,
                confidence=1.0,
                first_seen="2017-12-16T00:00:00",  # NYT UFO article date
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="peter_sturrock",
                name="Dr. Peter Sturrock",
                title="Professor Emeritus of Applied Physics",
                organization="Stanford University",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1982-01-01T00:00:00",  # Scientific Exploration Society founding
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="jacques_vallee",
                name="Dr. Jacques Vallée",
                title="Astrophysicist & UFO Researcher",
                organization="Independent / Venture Capital",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1960-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="jay_stratton",
                name="Jay Stratton",
                title="First Director, Unidentified Aerial Phenomena Task Force",
                organization="US Department of Defense",
                voice_embedding=None,
                confidence=0.95,
                first_seen="2017-01-01T00:00:00",
                last_seen="2023-01-01T00:00:00"
            ),
            Speaker(
                speaker_id="leslie_kean",
                name="Leslie Kean",
                title="Investigative Journalist",
                organization="The New York Times / Independent",
                voice_embedding=None,
                confidence=0.90,
                first_seen="2017-12-16T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="david_baltimore",
                name="Dr. David Baltimore",
                title="Nobel Laureate, Molecular Biologist",
                organization="California Institute of Technology",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1975-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            )
        ]

        for speaker in speakers:
            self.db.add_speaker(speaker)
            print(f"  ✓ Added speaker: {speaker.name}")

    def add_evidence_sources(self):
        """Add Stanford UFO research evidence sources"""
        print("\n📄 Adding Stanford UFO research evidence sources...")

        sources = [
            EvidenceSource(
                source_id="stanford_first_contact_2023",
                title="First Contact - Stanford Magazine Profile of Garry Nolan",
                url="https://stanfordmag.org/contents/first-contact",
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="2023-07-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'source_type': 'journalism',
                    'publication': 'Stanford Magazine',
                    'publication_date': '2023-07',
                    'confidence_level': 0.75,
                    'operation': 'stanford_uap_research',
                    'time_period': '2017-2023',
                    'classification': 'unclassified',
                    'credibility': 'high_academic_institution'
                }
            ),
            EvidenceSource(
                source_id="nyt_ufo_program_2017",
                title="NYT Revelation of Pentagon UFO Program (Referenced)",
                url="https://www.nytimes.com/2017/12/16/us/politics/pentagon-program-ufo-harry-reid.html",
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="2017-12-16T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'source_type': 'journalism',
                    'publication': 'The New York Times',
                    'confidence_level': 0.80,
                    'operation': 'pentagon_ufo_disclosure',
                    'time_period': '2007-2017',
                    'classification': 'declassified',
                    'impact': 'major_disclosure_event'
                }
            ),
            EvidenceSource(
                source_id="council_bluffs_1977_materials",
                title="Council Bluffs 1977 UFO Incident - Material Analysis",
                url=None,
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="1977-01-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'source_type': 'sensor',
                    'incident_location': 'Council Bluffs, Iowa',
                    'confidence_level': 0.70,
                    'operation': 'ufo_material_analysis',
                    'time_period': '1977',
                    'analysis_type': 'elemental_composition',
                    'analyzed_by': 'Garry Nolan'
                }
            ),
            EvidenceSource(
                source_id="nolan_brain_scan_study",
                title="Brain Scan Study of Military Personnel Exposed to UAP",
                url=None,
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="2018-01-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'source_type': 'official',
                    'study_type': 'medical_imaging',
                    'confidence_level': 0.75,
                    'operation': 'uap_health_effects_study',
                    'time_period': '2018-2023',
                    'classification': 'sensitive',
                    'participants': 'military_pilots_intelligence_agents'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✓ Added source: {source.title}")

    def add_claims(self):
        """Add evidence claims from Stanford UFO research"""
        print("\n💡 Adding Stanford UFO research claims...")

        claims = [
            # Nolan's scientific credibility and involvement
            EvidenceClaim(
                claim_id="nolan_claim_001",
                source_id="stanford_first_contact_2023",
                speaker_id="garry_nolan",
                claim_type=ClaimType.FACTUAL,
                text="Dr. Garry Nolan, Stanford pathology professor and immunologist, has been consulting with Pentagon and CIA on UFO/UAP phenomena analysis since 2017.",
                confidence=0.80,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Academic scientist with Nobel laureate mentor brings scientific rigor to UFO investigation. December 2017 NYT article catalyzed involvement.",
                entities=['Garry Nolan', 'Pentagon', 'CIA', 'Stanford University', 'UAP'],
                tags=['stanford', 'pentagon', 'cia', 'uap_research', 'academic_credibility'],
                created_at=datetime.now().isoformat()
            ),

            # Material analysis findings
            EvidenceClaim(
                claim_id="nolan_claim_002",
                source_id="council_bluffs_1977_materials",
                speaker_id="garry_nolan",
                claim_type=ClaimType.FACTUAL,
                text="Garry Nolan analyzed mysterious iron-based materials from 1977 Council Bluffs, Iowa UFO incident using advanced elemental composition techniques.",
                confidence=0.75,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Physical artifact analysis from historical UFO incident. Materials showed unusual composition patterns requiring scientific explanation.",
                entities=['Garry Nolan', 'Council Bluffs', 'UFO materials', 'elemental analysis'],
                tags=['material_analysis', 'council_bluffs', '1977', 'physical_evidence', 'forensics'],
                created_at=datetime.now().isoformat()
            ),

            # Brain scan study
            EvidenceClaim(
                claim_id="nolan_claim_003",
                source_id="nolan_brain_scan_study",
                speaker_id="garry_nolan",
                claim_type=ClaimType.FACTUAL,
                text="Nolan conducted brain imaging studies on military pilots and intelligence agents who experienced close encounters with UAP, finding anomalous brain structures.",
                confidence=0.75,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Medical study of UAP witnesses from military/intelligence community. Findings suggest potential neurological effects from UAP encounters.",
                entities=['Garry Nolan', 'brain imaging', 'military pilots', 'intelligence agents', 'UAP'],
                tags=['brain_scans', 'health_effects', 'military_witnesses', 'medical_study', 'uap_exposure'],
                created_at=datetime.now().isoformat()
            ),

            # Pentagon UAP Task Force connection
            EvidenceClaim(
                claim_id="nolan_claim_004",
                source_id="stanford_first_contact_2023",
                speaker_id="jay_stratton",
                claim_type=ClaimType.FACTUAL,
                text="Jay Stratton, first director of Pentagon's Unidentified Aerial Phenomena Task Force, worked directly with Garry Nolan on UAP scientific analysis.",
                confidence=0.80,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Official Pentagon UAP program collaboration with academic researcher. Demonstrates government scientific investigation of phenomenon.",
                entities=['Jay Stratton', 'Garry Nolan', 'UAP Task Force', 'Pentagon', 'DoD'],
                tags=['pentagon', 'uap_task_force', 'official_program', 'dod', 'collaboration'],
                created_at=datetime.now().isoformat()
            ),

            # NYT disclosure event
            EvidenceClaim(
                claim_id="nolan_claim_005",
                source_id="nyt_ufo_program_2017",
                speaker_id="leslie_kean",
                claim_type=ClaimType.FACTUAL,
                text="December 16, 2017 New York Times article revealed Pentagon's secret UFO investigation program (Advanced Aerospace Threat Identification Program), catalyzing mainstream scientific interest.",
                confidence=0.85,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Major disclosure event bringing UFO research into mainstream. Published by reputable outlet with official confirmation from Pentagon sources.",
                entities=['Leslie Kean', 'New York Times', 'Pentagon', 'AATIP', 'UFO disclosure'],
                tags=['nyt_disclosure', '2017', 'aatip', 'mainstream_media', 'pentagon_confirmation'],
                created_at=datetime.now().isoformat()
            ),

            # Kean's conviction statement
            EvidenceClaim(
                claim_id="nolan_claim_006",
                source_id="stanford_first_contact_2023",
                speaker_id="leslie_kean",
                claim_type=ClaimType.OPINION,
                text="Leslie Kean stated: 'I'm absolutely convinced some of these objects are not made by humans.'",
                confidence=0.60,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Statement from investigative journalist who broke Pentagon UFO story. Opinion based on extensive investigation and official sources.",
                entities=['Leslie Kean', 'UFO', 'non-human intelligence'],
                tags=['opinion', 'non_human_origin', 'investigative_journalism', 'conviction'],
                created_at=datetime.now().isoformat()
            ),

            # Peter Sturrock academic legitimacy
            EvidenceClaim(
                claim_id="nolan_claim_007",
                source_id="stanford_first_contact_2023",
                speaker_id="peter_sturrock",
                claim_type=ClaimType.FACTUAL,
                text="Peter Sturrock, Stanford professor emeritus of applied physics, founded Society for Scientific Exploration (1982) to enable academic study of anomalous phenomena including UFOs.",
                confidence=0.85,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Academic legitimization of UFO research at prestigious institution. Demonstrates long-term Stanford connection to phenomenon investigation.",
                entities=['Peter Sturrock', 'Stanford', 'Society for Scientific Exploration', 'UFO research'],
                tags=['stanford', 'academic_research', 'sse', '1982', 'institutional_support'],
                created_at=datetime.now().isoformat()
            ),

            # Jacques Vallée collaboration
            EvidenceClaim(
                claim_id="nolan_claim_008",
                source_id="stanford_first_contact_2023",
                speaker_id="jacques_vallee",
                claim_type=ClaimType.FACTUAL,
                text="Jacques Vallée, legendary astrophysicist and UFO researcher, collaborates with Garry Nolan on UAP material analysis and phenomenon investigation.",
                confidence=0.80,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Vallée has 60+ years UFO research experience. Collaboration brings historical perspective to modern scientific analysis.",
                entities=['Jacques Vallée', 'Garry Nolan', 'UAP materials', 'astrophysics'],
                tags=['vallee', 'collaboration', 'material_analysis', 'historical_researcher'],
                created_at=datetime.now().isoformat()
            ),

            # Nolan's scientific methodology quote
            EvidenceClaim(
                claim_id="nolan_claim_009",
                source_id="stanford_first_contact_2023",
                speaker_id="garry_nolan",
                claim_type=ClaimType.OPINION,
                text="Nolan stated: 'If you take a potential solution off the table... you could spend the rest of eternity searching' - arguing for considering extraterrestrial hypothesis.",
                confidence=0.65,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Scientific philosophy statement advocating for considering all hypotheses including extraterrestrial origin. Methodological approach to phenomenon.",
                entities=['Garry Nolan', 'extraterrestrial hypothesis', 'scientific method'],
                tags=['methodology', 'et_hypothesis', 'scientific_approach', 'opinion'],
                created_at=datetime.now().isoformat()
            ),

            # CyTOF technology application
            EvidenceClaim(
                claim_id="nolan_claim_010",
                source_id="stanford_first_contact_2023",
                speaker_id="garry_nolan",
                claim_type=ClaimType.FACTUAL,
                text="Nolan developed CyTOF (mass cytometry) cellular analysis technology and applied advanced analytical techniques to UAP material investigation.",
                confidence=0.85,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Application of cutting-edge biotech to UFO research. Demonstrates scientific rigor and advanced methodology in phenomenon investigation.",
                entities=['Garry Nolan', 'CyTOF', 'mass cytometry', 'UAP materials', 'biotech'],
                tags=['cytof', 'technology', 'biotech', 'material_analysis', 'methodology'],
                created_at=datetime.now().isoformat()
            ),

            # All-Domain Anomaly Resolution Office
            EvidenceClaim(
                claim_id="nolan_claim_011",
                source_id="stanford_first_contact_2023",
                speaker_id="jay_stratton",
                claim_type=ClaimType.FACTUAL,
                text="Pentagon established All-Domain Anomaly Resolution Office (AARO) as successor to UAP Task Force, institutionalizing UAP investigation.",
                confidence=0.90,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Official DoD office for UAP investigation. Represents ongoing government commitment to phenomenon study beyond initial task force.",
                entities=['AARO', 'Pentagon', 'UAP Task Force', 'Department of Defense'],
                tags=['aaro', 'pentagon', 'institutional', 'official_program', 'ongoing'],
                created_at=datetime.now().isoformat()
            ),

            # Academic-government bridge
            EvidenceClaim(
                claim_id="nolan_claim_012",
                source_id="stanford_first_contact_2023",
                speaker_id="garry_nolan",
                claim_type=ClaimType.FACTUAL,
                text="Nolan's work represents unprecedented academic-government collaboration on UAP research, bridging scientific credibility with official investigation programs.",
                confidence=0.75,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Historical shift from stigmatized fringe topic to legitimate academic-government scientific investigation. Stanford affiliation provides credibility.",
                entities=['Garry Nolan', 'Stanford', 'Pentagon', 'academic research', 'government collaboration'],
                tags=['academic_government_bridge', 'credibility', 'paradigm_shift', 'collaboration'],
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
        print("GARRY NOLAN / STANFORD UFO RESEARCH EVIDENCE INTEGRATION")
        print("="*80)

        self.add_speakers()
        self.add_evidence_sources()
        self.add_claims()

        print("\n" + "="*80)
        print("✅ INTEGRATION COMPLETE")
        print("="*80)
        print("\nTarget Classification: UAP RESEARCH / ACADEMIC-GOVERNMENT COLLABORATION")
        print("Operational Context: Modern scientific investigation of UAP phenomenon")
        print("Related Operations: Pentagon UAP Task Force, AARO, Council Bluffs 1977")
        print("Confidence: HIGH (0.75-0.85 for most claims, journalism source)")
        print("Cross-Reference: Jacques Vallée, Peter Sturrock, Pentagon programs")
        print("\nKey Intelligence:")
        print("  - Academic legitimization of UAP research via Stanford affiliation")
        print("  - Official Pentagon/CIA scientific consultation relationship")
        print("  - Physical material analysis from historical UFO incidents")
        print("  - Medical evidence (brain scans) of UAP encounter effects")
        print("  - NYT 2017 disclosure as watershed moment for mainstream acceptance")
        print("\nNext Steps:")
        print("  - Cross-reference with David Grusch testimony (UAP crash retrievals)")
        print("  - Investigate Council Bluffs 1977 incident details")
        print("  - Research AARO official reports and findings")
        print("  - Connect to T. Townsend Brown electrokinetic propulsion research")
        print("  - Analyze brain scan findings for pattern identification")


if __name__ == "__main__":
    integrator = NolanStanfordIntegrator()
    integrator.run()
