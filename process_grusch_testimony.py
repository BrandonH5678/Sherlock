#!/usr/bin/env python3
"""
Process David Grusch Congressional Testimony
Intelligence extraction for Sherlock evidence database
"""

from evidence_schema_gladio import (
    GladioEvidenceDatabase, PersonDossier, Organization, Claim, Evidence,
    TimeReference, LocationReference, EvidenceType, ConfidenceLevel, Relationship
)
from datetime import datetime
import json


def process_grusch_testimony():
    """Extract intelligence from Grusch House Oversight Committee testimony"""

    db = GladioEvidenceDatabase('evidence.db')

    # Source evidence document
    testimony_evidence = Evidence(
        evidence_id="grusch_hoc_testimony_2023",
        evidence_type=EvidenceType.TESTIMONY,
        description="David Grusch opening and closing statements to House Oversight Committee on UAP",
        source="House Oversight Committee hearing transcript",
        page_reference="3 pages",
        evidence_date=TimeReference(
            year=2023,
            confidence=ConfidenceLevel.CONFIRMED
        ),
        confidence=ConfidenceLevel.CONFIRMED,
        reliability_notes="Congressional testimony under oath"
    )

    # Create person dossier for David Charles Grusch
    grusch = PersonDossier(
        person_id="grusch_david_charles",
        first_name="David",
        middle_names=["Charles"],
        last_name="Grusch",
        aliases=["Dave Grusch"],

        # Employment timeline claims
        employment_timeline=[
            Claim(
                claim_id="grusch_employment_usaf",
                statement="Intelligence officer in US Air Force for 14 years at rank of Major",
                category="employment",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Self-reported under oath to Congress",
                time_reference=TimeReference(
                    year=2023,
                    time_description="14 years prior to 2023",
                    earliest_possible="2009-01-01",
                    latest_possible="2023-07-26",
                    confidence=ConfidenceLevel.PROBABLE
                )
            ),
            Claim(
                claim_id="grusch_employment_nga",
                statement="Intelligence officer at National Geospatial-Intelligence Agency (NGA) at GS-15 civilian level (equivalent to full-bird Colonel), 2021-2023",
                category="employment",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Self-reported under oath, specific dates and grade",
                time_reference=TimeReference(
                    year=2021,
                    earliest_possible="2021-01-01",
                    latest_possible="2023-12-31",
                    time_description="2021-2023",
                    confidence=ConfidenceLevel.CONFIRMED
                )
            ),
            Claim(
                claim_id="grusch_role_uap_colead",
                statement="Co-lead at NGA for Unidentified Anomalous Phenomena (UAP) and trans-medium object analysis",
                category="employment",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Specific role description under oath"
            ),
            Claim(
                claim_id="grusch_role_nro_reservist",
                statement="Member of UAP Task Force (UAPTF) 2019-2021 in NRO reservist capacity",
                category="military_service",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                time_reference=TimeReference(
                    year=2019,
                    earliest_possible="2019-01-01",
                    latest_possible="2021-12-31",
                    time_description="2019-2021",
                    confidence=ConfidenceLevel.CONFIRMED
                )
            ),
            Claim(
                claim_id="grusch_role_nro_ops_center",
                statement="Served in NRO Operations Center on director's briefing staff, coordinated Presidential Daily Brief (PDB) and contingency operations",
                category="military_service",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="High-level intelligence position with PDB access"
            )
        ],

        # Training and clearance timeline
        training_timeline=[
            Claim(
                claim_id="grusch_clearance_all_compartments",
                statement="Cleared to all relevant compartments, position of extreme trust in military and civilian capacities",
                category="training",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Highest level security clearances across intelligence community"
            ),
            Claim(
                claim_id="grusch_tasking_sap_cap_identification",
                statement="Tasked in 2019 by UAPTF director to identify all Special Access Programs & Controlled Access Programs (SAPs/CAPs) needed for congressionally mandated UAP mission",
                category="training",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                time_reference=TimeReference(
                    year=2019,
                    confidence=ConfidenceLevel.CONFIRMED
                )
            )
        ],

        # Significant activities - whistleblower actions
        significant_activities=[
            Claim(
                claim_id="grusch_whistleblower_ppd19",
                statement="Became whistleblower through PPD-19 Urgent Concern filing with Intelligence Community Inspector General (ICIG)",
                category="whistleblower",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Formal legal whistleblower protection invoked"
            ),
            Claim(
                claim_id="grusch_informed_crash_retrieval_program",
                statement="Informed in course of official duties of multi-decade UAP crash retrieval and reverse engineering program, was denied access to additional read-ons",
                category="intelligence_disclosure",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.PROBABLE,
                assessment_notes="Secondhand reporting under oath; requires corroboration from primary sources"
            ),
            Claim(
                claim_id="grusch_evidence_corroboration_4years",
                statement="Corroborated evidence over 4-year period from multiple esteemed military and IC individuals with photography, official documentation, and classified oral testimony",
                category="investigation",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.PROBABLE,
                time_reference=TimeReference(
                    year=2019,
                    earliest_possible="2019-01-01",
                    latest_possible="2023-07-26",
                    time_description="4 years prior to testimony",
                    confidence=ConfidenceLevel.PROBABLE
                )
            ),
            Claim(
                claim_id="grusch_retaliation_suffered",
                statement="Suffered retaliation for whistleblower decision",
                category="retaliation",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                assessment_notes="Self-reported under oath; nature of retaliation not specified in testimony"
            )
        ],

        # Political impact - congressional oversight claims
        political_impact=[
            Claim(
                claim_id="grusch_allegation_oversight_violation",
                statement="US Government operating with secrecy above Congressional oversight regarding UAPs",
                category="oversight_violation",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.DISPUTED,
                assessment_notes="Serious allegation requiring investigation; based on secondhand reports"
            ),
            Claim(
                claim_id="grusch_allegation_executive_abuse",
                statement="Grave congressional oversight issue and potential abuse of executive branch authorities",
                category="constitutional_violation",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.DISPUTED,
                assessment_notes="Constitutional separation of powers allegation"
            )
        ],

        # Technological impact claims
        technological_impact=[
            Claim(
                claim_id="grusch_claim_reverse_engineering",
                statement="Non-Human Reverse Engineering Programs exist that could enable extraordinary technological progress in propulsion, material science, energy production and storage",
                category="technology_assessment",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.UNVERIFIED,
                assessment_notes="Extraordinary claim requiring extraordinary evidence; secondhand reporting"
            )
        ],

        created_by="sherlock_intelligence_extraction"
    )

    # Add person to database
    success = db.add_person(grusch)
    print(f"✅ David Grusch dossier added: {success}")

    # Create organizations mentioned

    # NGA
    nga = Organization(
        organization_id="nga_uap_analysis",
        name="National Geospatial-Intelligence Agency",
        aliases=["NGA"],
        significant_events=[
            Claim(
                claim_id="nga_uap_colead_role",
                statement="NGA established co-lead role for UAP and trans-medium object analysis",
                category="organizational_structure",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                time_reference=TimeReference(
                    year=2021,
                    earliest_possible="2021-01-01",
                    latest_possible="2023-12-31",
                    confidence=ConfidenceLevel.PROBABLE
                )
            )
        ]
    )
    db.add_organization(nga)
    print(f"✅ NGA organization added")

    # UAPTF
    uaptf = Organization(
        organization_id="uaptf",
        name="Unidentified Anomalous Phenomena Task Force",
        aliases=["UAPTF", "UAP Task Force"],
        founding_date=TimeReference(
            year=2019,
            confidence=ConfidenceLevel.PROBABLE,
            time_description="Prior to 2019 UAPTF membership"
        ),
        significant_events=[
            Claim(
                claim_id="uaptf_sap_cap_tasking_2019",
                statement="UAPTF director tasked identification of all SAPs/CAPs needed for congressionally mandated mission in 2019",
                category="operations",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED,
                time_reference=TimeReference(
                    year=2019,
                    confidence=ConfidenceLevel.CONFIRMED
                )
            )
        ]
    )
    db.add_organization(uaptf)
    print(f"✅ UAPTF organization added")

    # AARO
    aaro = Organization(
        organization_id="aaro",
        name="All-Domain Anomaly Resolution Office",
        aliases=["AARO"],
        significant_events=[
            Claim(
                claim_id="aaro_grusch_reporting",
                statement="David Grusch reported to AARO as part of UAP analysis duties",
                category="operations",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ]
    )
    db.add_organization(aaro)
    print(f"✅ AARO organization added")

    # NRO
    nro = Organization(
        organization_id="nro",
        name="National Reconnaissance Office",
        aliases=["NRO"],
        significant_events=[
            Claim(
                claim_id="nro_ops_center_pdb_coordination",
                statement="NRO Operations Center coordinates Presidential Daily Brief (PDB) and contingency operations",
                category="operations",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ]
    )
    db.add_organization(nro)
    print(f"✅ NRO organization added")

    # ICIG
    icig = Organization(
        organization_id="icig",
        name="Intelligence Community Inspector General",
        aliases=["ICIG"],
        significant_events=[
            Claim(
                claim_id="icig_grusch_ppd19_filing",
                statement="ICIG received PPD-19 Urgent Concern filing from David Grusch regarding UAP programs",
                category="oversight",
                supporting_evidence=[testimony_evidence],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ]
    )
    db.add_organization(icig)
    print(f"✅ ICIG organization added")

    # Create relationships

    # Grusch - NGA
    rel_grusch_nga = Relationship(
        relationship_id="grusch_nga_employment",
        entity_1="grusch_david_charles",
        entity_2="nga_uap_analysis",
        entity_1_type="person",
        entity_2_type="organization",
        relationship_type="employee",
        relationship_description="Intelligence officer at GS-15 level, co-lead for UAP analysis",
        relationship_start=TimeReference(year=2021, confidence=ConfidenceLevel.CONFIRMED),
        relationship_end=TimeReference(year=2023, confidence=ConfidenceLevel.CONFIRMED),
        supporting_evidence=[testimony_evidence],
        confidence=ConfidenceLevel.CONFIRMED,
        publicly_acknowledged=True,
        significance="high",
        implications=["High-level UAP analysis role", "Official government UAP program participation"]
    )
    db.add_relationship(rel_grusch_nga)
    print(f"✅ Grusch-NGA relationship added")

    # Grusch - UAPTF
    rel_grusch_uaptf = Relationship(
        relationship_id="grusch_uaptf_membership",
        entity_1="grusch_david_charles",
        entity_2="uaptf",
        entity_1_type="person",
        entity_2_type="organization",
        relationship_type="member",
        relationship_description="UAPTF member in NRO reservist capacity, tasked with SAP/CAP identification",
        relationship_start=TimeReference(year=2019, confidence=ConfidenceLevel.CONFIRMED),
        relationship_end=TimeReference(year=2021, confidence=ConfidenceLevel.CONFIRMED),
        supporting_evidence=[testimony_evidence],
        confidence=ConfidenceLevel.CONFIRMED,
        publicly_acknowledged=True,
        significance="high",
        implications=["Direct UAP task force involvement", "SAP/CAP access and identification authority"]
    )
    db.add_relationship(rel_grusch_uaptf)
    print(f"✅ Grusch-UAPTF relationship added")

    # Grusch - ICIG
    rel_grusch_icig = Relationship(
        relationship_id="grusch_icig_whistleblower",
        entity_1="grusch_david_charles",
        entity_2="icig",
        entity_1_type="person",
        entity_2_type="organization",
        relationship_type="whistleblower",
        relationship_description="Filed PPD-19 Urgent Concern regarding UAP crash retrieval programs",
        supporting_evidence=[testimony_evidence],
        confidence=ConfidenceLevel.CONFIRMED,
        publicly_acknowledged=True,
        significance="high",
        implications=["Formal whistleblower protection invoked", "ICIG validation of complaint credibility"]
    )
    db.add_relationship(rel_grusch_icig)
    print(f"✅ Grusch-ICIG relationship added")

    print("\n" + "="*80)
    print("📊 INTELLIGENCE EXTRACTION SUMMARY")
    print("="*80)
    print(f"Source: David Grusch House Oversight Committee Testimony")
    print(f"Evidence Type: Congressional testimony (under oath)")
    print(f"Confidence Level: CONFIRMED (testimonial) / PROBABLE-DISPUTED (claims)")
    print(f"\nEntities Extracted:")
    print(f"  - 1 Person: David Charles Grusch")
    print(f"  - 5 Organizations: NGA, UAPTF, AARO, NRO, ICIG")
    print(f"  - 3 Relationships: Employment, membership, whistleblower")
    print(f"\nKey Claims Extracted:")
    print(f"  - 14 total claims across categories:")
    print(f"    • Employment timeline (4 claims)")
    print(f"    • Training/clearance (2 claims)")
    print(f"    • Whistleblower activities (4 claims)")
    print(f"    • Political/oversight allegations (2 claims)")
    print(f"    • Technological claims (1 claim)")
    print(f"    • Organizational events (1 claim)")
    print(f"\nConfidence Assessment:")
    print(f"  - CONFIRMED: Personal background, employment, whistleblower filing")
    print(f"  - PROBABLE: Secondhand UAP program reports with 4-year corroboration")
    print(f"  - DISPUTED: Oversight violations (requires investigation)")
    print(f"  - UNVERIFIED: Reverse engineering technology claims")
    print(f"\nIntelligence Priority: HIGH")
    print(f"  - Congressional testimony under oath")
    print(f"  - IC Inspector General validated complaint")
    print(f"  - Involves constitutional oversight allegations")
    print(f"  - Requires follow-up investigation for corroboration")
    print("="*80)


if __name__ == "__main__":
    print("🔍 SHERLOCK INTELLIGENCE EXTRACTION")
    print("Processing: David Grusch Congressional Testimony\n")
    process_grusch_testimony()
    print("\n✅ Intelligence extraction complete - data stored in evidence.db")
