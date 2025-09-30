#!/usr/bin/env python3
"""
Sample Operation Gladio Data Entry
Demonstrates the fact library system with sample data from Operation Gladio
"""

from evidence_schema_gladio import (
    GladioEvidenceDatabase, PersonDossier, Organization, ResourceFlow,
    Relationship, Evidence, Claim, TimeReference, LocationReference,
    EvidenceType, ConfidenceLevel
)


def create_sample_gladio_data():
    """Create sample Operation Gladio data to demonstrate the system"""

    db = GladioEvidenceDatabase("gladio_sample.db")
    print("🔍 Creating sample Operation Gladio fact library...")

    # Sample Evidence Sources
    gladio_book = Evidence(
        evidence_id="EV_GLADIO_BOOK_001",
        evidence_type=EvidenceType.BOOK,
        description="Operation Gladio by Paul L. Williams - comprehensive historical analysis",
        source="Operation Gladio by Paul L. Williams",
        confidence=ConfidenceLevel.PROBABLE
    )

    # Sample Person 1: Stefano Delle Chiaie (Italian neofascist)
    stefano_birth = TimeReference(
        year=1936,
        month=9,
        day=13,
        confidence=ConfidenceLevel.CONFIRMED,
        time_description="September 13, 1936",
        source_description="Official records"
    )

    stefano_ordine_nuovo = Claim(
        claim_id="CL_STEFANO_ORDINE_NUOVO",
        statement="Founded and led Ordine Nuovo (New Order) neofascist organization",
        category="organizational_leadership",
        supporting_evidence=[gladio_book],
        overall_confidence=ConfidenceLevel.CONFIRMED,
        time_reference=TimeReference(
            year=1969,
            earliest_possible="1968-01-01",
            latest_possible="1970-12-31",
            time_description="late 1960s",
            confidence=ConfidenceLevel.PROBABLE
        )
    )

    stefano_strategy_tension = Claim(
        claim_id="CL_STEFANO_STRATEGY_TENSION",
        statement="Participated in 'Strategy of Tension' bombing campaigns in Italy",
        category="operation_participation",
        supporting_evidence=[gladio_book],
        overall_confidence=ConfidenceLevel.PROBABLE,
        time_reference=TimeReference(
            year=1970,
            earliest_possible="1969-01-01",
            latest_possible="1974-12-31",
            time_description="early 1970s",
            confidence=ConfidenceLevel.POSSIBLE
        )
    )

    stefano_delle_chiaie = PersonDossier(
        person_id="PERS_DELLE_CHIAIE_STEFANO",
        first_name="Stefano",
        last_name="Delle Chiaie",
        aliases=["Il Caccola", "The Black Prince"],
        birth_date=stefano_birth,
        birth_location=LocationReference(
            country="Italy",
            city="Caserta",
            confidence=ConfidenceLevel.CONFIRMED
        ),
        organization_memberships=[stefano_ordine_nuovo],
        operation_participation=[stefano_strategy_tension],
        political_affiliations=[
            Claim(
                claim_id="CL_STEFANO_NEOFASCIST",
                statement="Committed neofascist ideology",
                category="political_affiliation",
                supporting_evidence=[gladio_book],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ],
        political_impact=[
            Claim(
                claim_id="CL_STEFANO_TERROR_IMPACT",
                statement="Instrumental in Italian domestic terrorism campaigns of 1970s",
                category="political_impact",
                supporting_evidence=[gladio_book],
                overall_confidence=ConfidenceLevel.PROBABLE
            )
        ]
    )

    # Sample Organization: Ordine Nuovo
    ordine_nuovo = Organization(
        organization_id="ORG_ORDINE_NUOVO",
        name="Ordine Nuovo",
        aliases=["New Order", "ON"],
        founding_date=TimeReference(
            year=1969,
            confidence=ConfidenceLevel.PROBABLE,
            time_description="1969"
        ),
        declared_purpose=[
            Claim(
                claim_id="CL_ON_DECLARED_PURPOSE",
                statement="Political organization defending traditional Italian values",
                category="declared_purpose",
                supporting_evidence=[gladio_book],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ],
        actual_activities=[
            Claim(
                claim_id="CL_ON_TERRORIST_ACTIVITIES",
                statement="Conducted terrorist bombing campaigns as part of Strategy of Tension",
                category="actual_activities",
                supporting_evidence=[gladio_book],
                overall_confidence=ConfidenceLevel.PROBABLE,
                time_reference=TimeReference(
                    year=1970,
                    earliest_possible="1969-01-01",
                    latest_possible="1975-12-31",
                    time_description="early 1970s",
                    confidence=ConfidenceLevel.POSSIBLE
                )
            )
        ],
        headquarters=LocationReference(
            country="Italy",
            city="Rome",
            confidence=ConfidenceLevel.PROBABLE
        )
    )

    # Sample Organization: NATO/Gladio
    nato_gladio = Organization(
        organization_id="ORG_NATO_GLADIO",
        name="Gladio",
        aliases=["Stay-behind network", "NATO stay-behind", "Gladio network"],
        founding_date=TimeReference(
            year=1952,
            confidence=ConfidenceLevel.PROBABLE,
            time_description="early 1950s"
        ),
        declared_purpose=[
            Claim(
                claim_id="CL_GLADIO_DECLARED",
                statement="Anti-communist resistance network in case of Soviet invasion",
                category="declared_purpose",
                supporting_evidence=[gladio_book],
                overall_confidence=ConfidenceLevel.CONFIRMED
            )
        ],
        actual_activities=[
            Claim(
                claim_id="CL_GLADIO_DOMESTIC_OPS",
                statement="Conducted domestic political operations against left-wing parties",
                category="actual_activities",
                supporting_evidence=[gladio_book],
                overall_confidence=ConfidenceLevel.PROBABLE,
                time_reference=TimeReference(
                    year=1960,
                    earliest_possible="1955-01-01",
                    latest_possible="1990-12-31",
                    time_description="1960s-1980s",
                    confidence=ConfidenceLevel.POSSIBLE
                )
            )
        ],
        parent_organizations=["ORG_NATO", "ORG_CIA"]
    )

    # Sample Relationship: Stefano Delle Chiaie <-> Ordine Nuovo
    stefano_ordine_relationship = Relationship(
        relationship_id="REL_STEFANO_ORDINE_NUOVO",
        entity_1="PERS_DELLE_CHIAIE_STEFANO",
        entity_2="ORG_ORDINE_NUOVO",
        entity_1_type="person",
        entity_2_type="organization",
        relationship_type="leader",
        relationship_description="Founded and led Ordine Nuovo organization",
        relationship_start=TimeReference(
            year=1969,
            confidence=ConfidenceLevel.PROBABLE
        ),
        supporting_evidence=[gladio_book],
        confidence=ConfidenceLevel.CONFIRMED,
        publicly_acknowledged=True,
        deliberately_hidden=False,
        significance="high",
        implications=["Central figure in Italian neofascist movement", "Key actor in Strategy of Tension"]
    )

    # Sample Resource Flow: CIA funding to Gladio network
    cia_gladio_funding = ResourceFlow(
        flow_id="FLOW_CIA_GLADIO_FUNDING",
        source_entity="ORG_CIA",
        recipient_entity="ORG_NATO_GLADIO",
        resource_type="money",
        amount="millions of dollars (exact amount classified)",
        description="Regular funding for Gladio stay-behind operations",
        flow_date=TimeReference(
            year=1960,
            earliest_possible="1952-01-01",
            latest_possible="1990-12-31",
            time_description="1950s-1980s ongoing",
            confidence=ConfidenceLevel.PROBABLE
        ),
        stated_purpose="Anti-communist resistance preparation",
        actual_purpose="Domestic political operations and influence",
        evidence=[gladio_book],
        confidence=ConfidenceLevel.PROBABLE
    )

    # Add all data to database
    print("📊 Adding sample data to database...")

    success_count = 0

    if db.add_person(stefano_delle_chiaie):
        print("✅ Added person: Stefano Delle Chiaie")
        success_count += 1

    if db.add_organization(ordine_nuovo):
        print("✅ Added organization: Ordine Nuovo")
        success_count += 1

    if db.add_organization(nato_gladio):
        print("✅ Added organization: Gladio")
        success_count += 1

    if db.add_relationship(stefano_ordine_relationship):
        print("✅ Added relationship: Stefano Delle Chiaie <-> Ordine Nuovo")
        success_count += 1

    print(f"\n📈 Sample data creation complete: {success_count}/4 items added successfully")

    # Demonstrate search capabilities
    print("\n🔍 Testing search capabilities...")

    search_results = db.search_people("Stefano")
    print(f"Search for 'Stefano': {len(search_results)} results found")

    if search_results:
        person = search_results[0]
        print(f"  - {person.get('first_name', 'Unknown')} {person.get('last_name', 'Unknown')}")
        print(f"  - Aliases: {person.get('aliases', [])}")
        birth_date = person.get('birth_date', {})
        print(f"  - Birth: {birth_date.get('year', 'Unknown') if birth_date else 'Unknown'}")
        print(f"  - Organization memberships: {len(person.get('organization_memberships', [])) if person.get('organization_memberships') else 0}")

    # Demonstrate network analysis
    print("\n🕸️  Testing network analysis...")
    analysis = db.analyze_relationships("PERS_DELLE_CHIAIE_STEFANO")
    print(f"Network analysis for Stefano Delle Chiaie:")
    print(f"  - Total connections: {analysis['network_analysis']['total_connections']}")
    print(f"  - Direct relationships: {len(analysis['direct_relationships'])}")

    print("\n✅ Sample Operation Gladio fact library demonstration complete!")
    print("\nThe database now contains:")
    print("  - Comprehensive person dossiers with temporal granularity")
    print("  - Organization profiles with declared vs. actual purposes")
    print("  - Relationship mapping with evidence validation")
    print("  - Resource flow tracking with confidence assessments")
    print("  - Multi-dimensional evidence validation")

    return db


def demonstrate_fact_extraction():
    """Demonstrate how to extract facts from Operation Gladio text"""

    print("\n📚 FACT EXTRACTION DEMONSTRATION")
    print("="*50)

    # Sample text extraction (demonstrating methodology)
    sample_text = """
    Example text analysis for Operation Gladio:

    'Stefano Delle Chiaie, born September 13, 1936, in Caserta, Italy,
    founded the neofascist organization Ordine Nuovo in 1969. Known by
    the alias "Il Caccola" (The Booger), Delle Chiaie became a central
    figure in the Strategy of Tension bombing campaigns that rocked Italy
    in the early 1970s.'
    """

    print("Sample text extraction methodology:")
    print("1. ENTITY IDENTIFICATION:")
    print("   - Person: Stefano Delle Chiaie")
    print("   - Organization: Ordine Nuovo")
    print("   - Alias: Il Caccola")
    print("   - Location: Caserta, Italy")

    print("\n2. TEMPORAL EXTRACTION:")
    print("   - Birth date: September 13, 1936 (CONFIRMED)")
    print("   - Organization founding: 1969 (PROBABLE)")
    print("   - Operation timeframe: early 1970s (POSSIBLE)")

    print("\n3. RELATIONSHIP MAPPING:")
    print("   - Stefano Delle Chiaie -> FOUNDED -> Ordine Nuovo")
    print("   - Stefano Delle Chiaie -> PARTICIPATED -> Strategy of Tension")

    print("\n4. EVIDENCE ASSESSMENT:")
    print("   - Source: Book text with page reference")
    print("   - Confidence: PROBABLE (single source, needs corroboration)")
    print("   - Supporting evidence needed: Official records, multiple sources")


if __name__ == "__main__":
    print("🔍 OPERATION GLADIO FACT LIBRARY SYSTEM")
    print("=====================================")

    # Create sample database
    db = create_sample_gladio_data()

    # Demonstrate extraction methodology
    demonstrate_fact_extraction()

    print("\n🎯 NEXT STEPS:")
    print("1. Use interactive data entry: python3 gladio_data_entry.py")
    print("2. Run analysis tools: python3 gladio_analysis.py")
    print("3. Begin systematic extraction from Operation Gladio text")
    print("4. Cross-reference with additional historical sources")
    print("\nSystem ready for comprehensive Operation Gladio analysis!")