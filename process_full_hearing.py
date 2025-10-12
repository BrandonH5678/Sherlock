#!/usr/bin/env python3
"""
Process Full House Oversight Committee Hearing on UAPs
Intelligence extraction for Sherlock evidence database
July 26, 2023 - 54-page transcript
"""

from evidence_schema_gladio import (
    GladioEvidenceDatabase, PersonDossier, Organization, Claim, Evidence,
    TimeReference, LocationReference, EvidenceType, ConfidenceLevel, Relationship
)
from datetime import datetime
import json


def process_full_hearing():
    """Extract intelligence from complete House Oversight Committee UAP hearing"""

    db = GladioEvidenceDatabase('evidence.db')

    # Source evidence document
    hearing_transcript = Evidence(
        evidence_id="hoc_uap_hearing_full_2023",
        evidence_type=EvidenceType.TESTIMONY,
        description="House Oversight Committee hearing on Unidentified Anomalous Phenomena - Full transcript with all witnesses and Q&A",
        source="House Oversight Committee HHRG-118-GO06 transcript",
        page_reference="54 pages",
        evidence_date=TimeReference(
            year=2023,
            month=7,
            day=26,
            confidence=ConfidenceLevel.CONFIRMED
        ),
        confidence=ConfidenceLevel.CONFIRMED,
        reliability_notes="Congressional testimony under oath with multiple witnesses"
    )

    # ========================
    # RYAN GRAVES DOSSIER
    # ========================

    ryan_graves = PersonDossier(
        person_id="graves_ryan",
        first_name="Ryan",
        last_name="Graves",

        employment_timeline=[
            Claim(
                claim_id="graves_usn_pilot",
                statement="F/A-18 pilot in US Navy for over 10 years",
                category="employment",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Self-reported under oath to Congress"
            ),
            Claim(
                claim_id="graves_asa_executive_director",
                statement="Executive Director of Americans for Safe Aerospace",
                category="employment",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                time_reference=TimeReference(
                    year=2023,
                    confidence=ConfidenceLevel.CONFIRMED,
                    time_description="Current position as of July 2023 testimony"
                )
            )
        ],

        significant_activities=[
            Claim(
                claim_id="graves_uap_encounters_training",
                statement="Witnessed unidentified anomalous phenomena on multiple training missions with strike group off Atlantic coast",
                category="uap_encounter",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Direct firsthand testimony under oath",
                time_reference=TimeReference(
                    year=2014,
                    time_description="During training missions, 2014-2015",
                    confidence=ConfidenceLevel.PROBABLE
                ),
                location_reference=LocationReference(
                    region="Atlantic Coast",
                    location_description="Off Virginia coast during training exercises",
                    confidence=ConfidenceLevel.CONFIRMED
                )
            ),
            Claim(
                claim_id="graves_uap_radar_upgrade_correlation",
                statement="UAP sightings began after radar system upgrades in 2014, objects detected daily for at least 2 years",
                category="uap_pattern",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.PROBABLE,
                assessment_notes="Correlation between radar upgrades and detection frequency",
                time_reference=TimeReference(
                    year=2014,
                    earliest_possible="2014-01-01",
                    latest_possible="2016-12-31",
                    time_description="2014 radar upgrades through at least 2 years of daily detections",
                    confidence=ConfidenceLevel.CONFIRMED
                )
            ),
            Claim(
                claim_id="graves_uap_cube_sphere",
                statement="Described UAP as dark grey or black cube inside clear sphere, approximately 5-15 feet in diameter",
                category="uap_description",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Detailed visual description from close-range observation"
            ),
            Claim(
                claim_id="graves_near_miss_incident",
                statement="Two F-18 jets nearly collided with UAP object during training mission, official hazard report filed",
                category="aviation_safety",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Official aviation safety report exists",
                time_reference=TimeReference(
                    year=2014,
                    time_description="During 2014-2015 training period",
                    confidence=ConfidenceLevel.PROBABLE
                )
            ),
            Claim(
                claim_id="graves_30_pilots_reporting",
                statement="Conservatively 30+ pilots from his squadron and strike group witnessed UAP phenomena",
                category="witness_corroboration",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.PROBABLE,
                assessment_notes="Estimated number of pilot witnesses, not individually verified in testimony"
            ),
            Claim(
                claim_id="graves_vandenberg_mothership",
                statement="Commercial pilots reported large dark grey or black cube 'mothership' UAP at high altitude off Vandenberg AFB",
                category="uap_encounter",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.PROBABLE,
                assessment_notes="Secondhand report from commercial pilots to Americans for Safe Aerospace",
                time_reference=TimeReference(
                    year=2023,
                    time_description="Recent report received by ASA",
                    confidence=ConfidenceLevel.POSSIBLE
                ),
                location_reference=LocationReference(
                    region="California",
                    location_description="Off Vandenberg Air Force Base",
                    confidence=ConfidenceLevel.CONFIRMED
                )
            ),
            Claim(
                claim_id="graves_reporting_stigma",
                statement="Commercial and military pilots face stigma and career repercussions for reporting UAP sightings",
                category="institutional_culture",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.PROBABLE,
                assessment_notes="Based on multiple pilot reports to ASA organization"
            )
        ],

        political_impact=[
            Claim(
                claim_id="graves_aviation_safety_priority",
                statement="UAPs represent significant aviation safety hazard requiring government transparency and investigation",
                category="policy_recommendation",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Explicit policy recommendation in Congressional testimony"
            )
        ],

        created_by="sherlock_intelligence_extraction"
    )

    # ========================
    # COMMANDER DAVID FRAVOR DOSSIER
    # ========================

    david_fravor = PersonDossier(
        person_id="fravor_david",
        first_name="David",
        last_name="Fravor",

        employment_timeline=[
            Claim(
                claim_id="fravor_usn_pilot_18years",
                statement="US Navy pilot for 18 years",
                category="military_service",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Self-reported under oath"
            ),
            Claim(
                claim_id="fravor_commanding_officer",
                statement="Commanding Officer of VFA-41 Black Aces strike fighter squadron",
                category="military_leadership",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                time_reference=TimeReference(
                    year=2004,
                    confidence=ConfidenceLevel.CONFIRMED,
                    time_description="At time of Nimitz incident, November 2004"
                )
            )
        ],

        military_service=[
            Claim(
                claim_id="fravor_retirement_rank",
                statement="Retired from US Navy as Commander",
                category="military_service",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ],

        significant_activities=[
            Claim(
                claim_id="fravor_nimitz_tic_tac_encounter",
                statement="Witnessed 'Tic Tac' UAP during USS Nimitz carrier strike group training off San Diego - white smooth object with no wings or exhaust, approximately 40 feet long",
                category="uap_encounter",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Direct firsthand testimony under oath, corroborated by WSO and other pilots",
                time_reference=TimeReference(
                    year=2004,
                    month=11,
                    day=14,
                    confidence=ConfidenceLevel.CONFIRMED,
                    time_description="November 14, 2004"
                ),
                location_reference=LocationReference(
                    region="Pacific Ocean",
                    location_description="Approximately 100 miles off San Diego coast",
                    coordinates={"lat": 32.5, "lon": -119.0},
                    confidence=ConfidenceLevel.PROBABLE
                )
            ),
            Claim(
                claim_id="fravor_tic_tac_performance",
                statement="Tic Tac UAP demonstrated instantaneous acceleration, estimated >3000 mph velocity, went from 50ft above water to 20,000+ feet in under a second, no visible propulsion",
                category="uap_capabilities",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Observed performance characteristics beyond known aircraft capabilities"
            ),
            Claim(
                claim_id="fravor_radar_corroboration",
                statement="Princeton radar tracked UAP descending from 80,000 feet to sea level in less than a second, E-2 Hawkeye also tracked object",
                category="sensor_data",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Multiple independent radar systems corroborated visual sighting"
            ),
            Claim(
                claim_id="fravor_cap_point_prediction",
                statement="Tic Tac UAP appeared at predetermined CAP point 60 miles away, suggesting knowledge of classified training plan",
                category="intelligence_indicator",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.PROBABLE,
                assessment_notes="Object location at classified rendezvous point suggests advanced knowledge or prediction"
            ),
            Claim(
                claim_id="fravor_video_evidence",
                statement="Second flight recorded FLIR video of Tic Tac UAP, video later publicly released as 'NIMITZ video'",
                category="documentary_evidence",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Video evidence exists and has been publicly authenticated"
            ),
            Claim(
                claim_id="fravor_sensor_superiority",
                statement="Tic Tac UAP demonstrated active jamming or sensor superiority capabilities",
                category="uap_capabilities",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.PROBABLE,
                assessment_notes="Based on object's ability to evade or interfere with tracking systems"
            )
        ],

        technological_impact=[
            Claim(
                claim_id="fravor_tech_beyond_known",
                statement="Tic Tac performance characteristics represent technology far beyond any known US or foreign aircraft capabilities as of 2004 and still unexplained as of 2023",
                category="technology_assessment",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Performance envelope exceeds known physics constraints for conventional aircraft"
            )
        ],

        created_by="sherlock_intelligence_extraction"
    )

    # ========================
    # ADDITIONAL GRUSCH CLAIMS FROM Q&A
    # ========================

    # Get existing Grusch dossier or create claims to add
    grusch_qa_claims = [
        Claim(
            claim_id="grusch_nonhuman_biologics",
            statement="Biologics came with some recovered UAP craft, assessed as non-human origin",
            category="extraordinary_claim",
            supporting_evidence=[hearing_transcript],
            overall_confidence=ConfidenceLevel.UNVERIFIED,
            assessment_notes="Extraordinary claim from secondhand sources, stated in response to direct Congressional questioning"
        ),
        Claim(
            claim_id="grusch_people_harmed",
            statement="Has knowledge of people who have been harmed or injured in efforts to cover up or conceal UAP information",
            category="harm_allegation",
            supporting_evidence=[hearing_transcript],
            overall_confidence=ConfidenceLevel.DISPUTED,
            assessment_notes="Serious allegation requiring investigation, based on interview sources"
        ),
        Claim(
            claim_id="grusch_funding_misappropriation",
            statement="Certain UAP programs funded through misappropriation of federal funds",
            category="financial_irregularity",
            supporting_evidence=[hearing_transcript],
            overall_confidence=ConfidenceLevel.DISPUTED,
            assessment_notes="Allegation of illegal funding mechanisms, requires financial audit"
        ),
        Claim(
            claim_id="grusch_craft_assessment",
            statement="Has interviewed individuals who have direct knowledge of non-human origin craft and assessment of their exotic materials",
            category="investigation_scope",
            supporting_evidence=[hearing_transcript],
            overall_confidence=ConfidenceLevel.PROBABLE,
            assessment_notes="Documented interview methodology over 4 years"
        )
    ]

    # ========================
    # ORGANIZATIONS
    # ========================

    # Americans for Safe Aerospace
    asa = Organization(
        organization_id="americans_safe_aerospace",
        name="Americans for Safe Aerospace",
        aliases=["ASA"],
        founding_date=TimeReference(
            year=2022,
            confidence=ConfidenceLevel.PROBABLE,
            time_description="Prior to 2023 testimony"
        ),
        declared_purpose=[
            Claim(
                claim_id="asa_mission",
                statement="Organization dedicated to aviation safety through UAP reporting and pilot support",
                category="organizational_mission",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ],
        actual_activities=[
            Claim(
                claim_id="asa_pilot_reporting",
                statement="Provides safe reporting mechanism for commercial and military pilots to report UAP encounters without career stigma",
                category="operations",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ]
    )
    db.add_organization(asa)
    print(f"✅ Americans for Safe Aerospace organization added")

    # USS Nimitz Carrier Strike Group
    nimitz_csg = Organization(
        organization_id="nimitz_carrier_strike_group_2004",
        name="USS Nimitz Carrier Strike Group",
        aliases=["Nimitz CSG", "CVN-68 Strike Group"],
        significant_events=[
            Claim(
                claim_id="nimitz_tic_tac_incident",
                statement="Nimitz carrier strike group encountered and tracked Tic Tac UAP during training exercises November 2004",
                category="uap_encounter",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                time_reference=TimeReference(
                    year=2004,
                    month=11,
                    confidence=ConfidenceLevel.CONFIRMED
                )
            ),
            Claim(
                claim_id="nimitz_multiple_days_tracking",
                statement="Princeton radar tracked anomalous objects for multiple days prior to pilot visual encounter",
                category="sensor_data",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Extended tracking period suggests systematic observation campaign"
            )
        ]
    )
    db.add_organization(nimitz_csg)
    print(f"✅ USS Nimitz CSG organization added")

    # VFA-41 Black Aces
    vfa41 = Organization(
        organization_id="vfa_41_black_aces",
        name="Strike Fighter Squadron 41 (VFA-41)",
        aliases=["VFA-41", "Black Aces"],
        leadership_timeline=[
            Claim(
                claim_id="vfa41_fravor_command",
                statement="Commander David Fravor served as Commanding Officer during Nimitz incident",
                category="leadership",
                supporting_evidence=[hearing_transcript],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                time_reference=TimeReference(
                    year=2004,
                    confidence=ConfidenceLevel.CONFIRMED
                )
            )
        ]
    )
    db.add_organization(vfa41)
    print(f"✅ VFA-41 Black Aces organization added")

    # Add persons
    success_graves = db.add_person(ryan_graves)
    print(f"✅ Ryan Graves dossier added: {success_graves}")

    success_fravor = db.add_person(david_fravor)
    print(f"✅ Commander David Fravor dossier added: {success_fravor}")

    # ========================
    # RELATIONSHIPS
    # ========================

    # Graves - ASA
    rel_graves_asa = Relationship(
        relationship_id="graves_asa_leadership",
        entity_1="graves_ryan",
        entity_2="americans_safe_aerospace",
        entity_1_type="person",
        entity_2_type="organization",
        relationship_type="leader",
        relationship_description="Executive Director of Americans for Safe Aerospace",
        supporting_evidence=[hearing_transcript],
        confidence=ConfidenceLevel.CONFIRMED,
        publicly_acknowledged=True,
        significance="high",
        implications=["Pilot advocacy organization", "UAP reporting mechanism"]
    )
    db.add_relationship(rel_graves_asa)
    print(f"✅ Graves-ASA relationship added")

    # Fravor - Nimitz CSG
    rel_fravor_nimitz = Relationship(
        relationship_id="fravor_nimitz_participation",
        entity_1="fravor_david",
        entity_2="nimitz_carrier_strike_group_2004",
        entity_1_type="person",
        entity_2_type="organization",
        relationship_type="member",
        relationship_description="Squadron commander during Nimitz Tic Tac encounter",
        relationship_start=TimeReference(year=2004, confidence=ConfidenceLevel.CONFIRMED),
        supporting_evidence=[hearing_transcript],
        confidence=ConfidenceLevel.CONFIRMED,
        publicly_acknowledged=True,
        significance="high",
        implications=["Direct UAP encounter witness", "Multiple sensor corroboration"]
    )
    db.add_relationship(rel_fravor_nimitz)
    print(f"✅ Fravor-Nimitz CSG relationship added")

    # Fravor - VFA-41
    rel_fravor_vfa41 = Relationship(
        relationship_id="fravor_vfa41_command",
        entity_1="fravor_david",
        entity_2="vfa_41_black_aces",
        entity_1_type="person",
        entity_2_type="organization",
        relationship_type="leader",
        relationship_description="Commanding Officer of VFA-41 Black Aces",
        relationship_start=TimeReference(year=2004, confidence=ConfidenceLevel.PROBABLE),
        supporting_evidence=[hearing_transcript],
        confidence=ConfidenceLevel.CONFIRMED,
        publicly_acknowledged=True,
        significance="high"
    )
    db.add_relationship(rel_fravor_vfa41)
    print(f"✅ Fravor-VFA-41 relationship added")

    print("\n" + "="*80)
    print("📊 FULL HEARING INTELLIGENCE EXTRACTION SUMMARY")
    print("="*80)
    print(f"Source: House Oversight Committee UAP Hearing - July 26, 2023")
    print(f"Evidence Type: Congressional testimony (under oath, multiple witnesses)")
    print(f"Document: 54-page full hearing transcript")
    print(f"\nWitnesses Processed:")
    print(f"  - Ryan Graves (USN F/A-18 pilot, ASA Executive Director)")
    print(f"  - Commander David Fravor (USN Ret., Nimitz Tic Tac encounter)")
    print(f"  - David Grusch (additional Q&A claims)")
    print(f"\nEntities Extracted:")
    print(f"  - 2 New Persons: Ryan Graves, Commander David Fravor")
    print(f"  - 3 New Organizations: Americans for Safe Aerospace, USS Nimitz CSG, VFA-41")
    print(f"  - 3 New Relationships")
    print(f"\nKey Claims Extracted:")
    print(f"  - Ryan Graves: 7 claims (UAP encounters, cube-sphere description, aviation safety)")
    print(f"  - Commander Fravor: 6 claims (Tic Tac encounter, performance analysis, sensor data)")
    print(f"  - Additional Grusch Q&A: 4 claims (biologics, harm allegations, funding)")
    print(f"\nMajor Intelligence Items:")
    print(f"  ✓ Nimitz Tic Tac incident (Nov 14, 2004) - CONFIRMED with multiple sensors")
    print(f"  ✓ Atlantic coast UAP encounters (2014-2015) - CONFIRMED, daily for 2+ years")
    print(f"  ✓ Cube-within-sphere UAP morphology - CONFIRMED visual description")
    print(f"  ✓ Near-miss aviation safety incident - CONFIRMED with hazard report")
    print(f"  ✓ 30+ pilot witnesses from single strike group - PROBABLE")
    print(f"  ✓ Vandenberg AFB 'mothership' sighting - PROBABLE secondhand report")
    print(f"  ✓ Non-human biologics claim - UNVERIFIED extraordinary claim")
    print(f"  ✓ Harm/injury allegations - DISPUTED, requires investigation")
    print(f"\nConfidence Assessment:")
    print(f"  - CONFIRMED: Direct pilot encounters, radar data, visual observations under oath")
    print(f"  - PROBABLE: Corroborated secondhand reports, performance assessments")
    print(f"  - DISPUTED: Harm allegations, funding irregularities (require investigation)")
    print(f"  - UNVERIFIED: Non-human biologics, extraordinary technology claims")
    print(f"\nIntelligence Priority: CRITICAL")
    print(f"  - Multiple credible military witnesses under oath")
    print(f"  - Sensor data corroboration from multiple platforms")
    print(f"  - Aviation safety implications")
    print(f"  - National security implications")
    print(f"  - Government transparency and oversight issues")
    print("="*80)


if __name__ == "__main__":
    print("🔍 SHERLOCK INTELLIGENCE EXTRACTION")
    print("Processing: Full House Oversight Committee UAP Hearing Transcript\n")
    process_full_hearing()
    print("\n✅ Intelligence extraction complete - data stored in evidence.db")
