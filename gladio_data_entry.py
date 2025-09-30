#!/usr/bin/env python3
"""
Operation Gladio Data Entry System
Interactive tools for building fact libraries from source material
"""

import json
import sys
from typing import Dict, List, Optional
from evidence_schema_gladio import (
    GladioEvidenceDatabase, PersonDossier, Organization, ResourceFlow,
    Relationship, Evidence, Claim, TimeReference, LocationReference,
    EvidenceType, ConfidenceLevel
)


class GladioDataEntry:
    """Interactive data entry system for Operation Gladio evidence"""

    def __init__(self, db_path: str = "gladio_evidence.db"):
        self.db = GladioEvidenceDatabase(db_path)
        self.current_source = "Operation Gladio by Paul L. Williams"

    def main_menu(self):
        """Main interactive menu"""
        while True:
            print("\n" + "="*60)
            print("🔍 OPERATION GLADIO EVIDENCE BUILDER")
            print("="*60)
            print("1. Add Person Dossier")
            print("2. Add Organization")
            print("3. Add Resource Flow")
            print("4. Add Relationship")
            print("5. Search Database")
            print("6. Generate Timeline")
            print("7. Analyze Networks")
            print("8. Export Evidence")
            print("9. Quick Entry Mode")
            print("0. Exit")
            print("-"*60)

            choice = input("Select option: ").strip()

            if choice == "1":
                self.add_person_interactive()
            elif choice == "2":
                self.add_organization_interactive()
            elif choice == "3":
                self.add_resource_flow_interactive()
            elif choice == "4":
                self.add_relationship_interactive()
            elif choice == "5":
                self.search_menu()
            elif choice == "6":
                self.generate_timeline()
            elif choice == "7":
                self.analyze_networks()
            elif choice == "8":
                self.export_evidence()
            elif choice == "9":
                self.quick_entry_mode()
            elif choice == "0":
                print("📊 Evidence database session ended.")
                break
            else:
                print("❌ Invalid option. Please try again.")

    def add_person_interactive(self):
        """Interactive person dossier creation"""
        print("\n" + "-"*50)
        print("👤 PERSON DOSSIER CREATION")
        print("-"*50)

        # Basic identification
        first_name = input("First name: ").strip()
        middle_names = input("Middle names (comma-separated): ").strip().split(",") if input("Middle names (comma-separated): ").strip() else []
        last_name = input("Last name: ").strip()
        aliases = input("Aliases (comma-separated): ").strip().split(",") if input("Aliases (comma-separated): ").strip() else []

        person_id = f"PERS_{last_name.upper()}_{first_name.upper()}"

        print(f"\nCreating dossier for: {first_name} {last_name}")
        print(f"Person ID: {person_id}")

        # Birth information
        birth_date = self.input_date("Birth date")
        birth_location = self.input_location("Birth location")

        # Create person object
        person = PersonDossier(
            person_id=person_id,
            first_name=first_name,
            middle_names=middle_names,
            last_name=last_name,
            aliases=aliases,
            birth_date=birth_date,
            birth_location=birth_location
        )

        # Add detailed information
        if self.confirm("Add education timeline? (y/n): "):
            person.education_timeline = self.input_claims("education")

        if self.confirm("Add military service? (y/n): "):
            person.military_service = self.input_claims("military service")

        if self.confirm("Add organization memberships? (y/n): "):
            person.organization_memberships = self.input_claims("organization membership")

        if self.confirm("Add operation participation? (y/n): "):
            person.operation_participation = self.input_claims("operation participation")

        # Save to database
        if self.db.add_person(person):
            print(f"✅ Person dossier created successfully: {person_id}")
        else:
            print(f"❌ Failed to save person dossier: {person_id}")

    def add_organization_interactive(self):
        """Interactive organization creation"""
        print("\n" + "-"*50)
        print("🏢 ORGANIZATION CREATION")
        print("-"*50)

        name = input("Organization name: ").strip()
        aliases = input("Aliases (comma-separated): ").strip().split(",") if input("Aliases (comma-separated): ").strip() else []

        org_id = f"ORG_{name.upper().replace(' ', '_')}"

        print(f"\nCreating organization: {name}")
        print(f"Organization ID: {org_id}")

        # Temporal information
        founding_date = self.input_date("Founding date")
        dissolution_date = self.input_date("Dissolution date (if applicable)")

        # Create organization object
        org = Organization(
            organization_id=org_id,
            name=name,
            aliases=aliases,
            founding_date=founding_date,
            dissolution_date=dissolution_date if dissolution_date.year else None
        )

        # Add detailed information
        if self.confirm("Add declared purpose? (y/n): "):
            org.declared_purpose = self.input_claims("declared purpose")

        if self.confirm("Add actual activities? (y/n): "):
            org.actual_activities = self.input_claims("actual activities")

        if self.confirm("Add funding sources? (y/n): "):
            org.funding_sources = self.input_claims("funding sources")

        # Save to database
        if self.db.add_organization(org):
            print(f"✅ Organization created successfully: {org_id}")
        else:
            print(f"❌ Failed to save organization: {org_id}")

    def input_date(self, prompt: str) -> TimeReference:
        """Input date with uncertainty handling"""
        print(f"\n📅 {prompt}:")

        year = self.input_int("Year (YYYY, or blank if unknown): ")
        month = self.input_int("Month (MM, or blank if unknown): ")
        day = self.input_int("Day (DD, or blank if unknown): ")

        earliest = input("Earliest possible date (YYYY-MM-DD, or blank): ").strip()
        latest = input("Latest possible date (YYYY-MM-DD, or blank): ").strip()
        description = input("Time description (e.g., 'early 1960s'): ").strip()

        confidence = self.input_confidence("Date confidence")

        return TimeReference(
            year=year,
            month=month,
            day=day,
            earliest_possible=earliest if earliest else None,
            latest_possible=latest if latest else None,
            time_description=description if description else None,
            confidence=confidence
        )

    def input_location(self, prompt: str) -> LocationReference:
        """Input location information"""
        print(f"\n📍 {prompt}:")

        country = input("Country: ").strip()
        region = input("Region/State: ").strip()
        city = input("City: ").strip()
        address = input("Address: ").strip()

        confidence = self.input_confidence("Location confidence")

        return LocationReference(
            country=country if country else None,
            region=region if region else None,
            city=city if city else None,
            address=address if address else None,
            confidence=confidence
        )

    def input_claims(self, category: str) -> List[Claim]:
        """Input multiple claims for a category"""
        claims = []
        print(f"\n📝 Enter {category} information:")

        while True:
            statement = input(f"{category.title()} statement (or 'done' to finish): ").strip()
            if statement.lower() == 'done':
                break

            claim_id = f"CL_{category.upper().replace(' ', '_')}_{len(claims)+1:03d}"

            # Get supporting evidence
            evidence = self.input_evidence(f"Evidence for: {statement}")

            # Get temporal context
            time_ref = None
            if self.confirm("Add date/time reference? (y/n): "):
                time_ref = self.input_date("Event date")

            claim = Claim(
                claim_id=claim_id,
                statement=statement,
                category=category,
                supporting_evidence=[evidence] if evidence else [],
                time_reference=time_ref
            )

            claims.append(claim)
            print(f"✅ Added claim: {statement}")

        return claims

    def input_evidence(self, prompt: str) -> Optional[Evidence]:
        """Input evidence for a claim"""
        print(f"\n🔍 {prompt}:")

        if not self.confirm("Add evidence? (y/n): "):
            return None

        description = input("Evidence description: ").strip()
        page_ref = input("Page reference: ").strip()

        # Evidence type selection
        print("\nEvidence types:")
        for i, etype in enumerate(EvidenceType, 1):
            print(f"{i}. {etype.value}")

        type_choice = self.input_int("Select evidence type (number): ")
        evidence_types = list(EvidenceType)
        evidence_type = evidence_types[type_choice - 1] if 1 <= type_choice <= len(evidence_types) else EvidenceType.DOCUMENT

        confidence = self.input_confidence("Evidence confidence")

        evidence_id = f"EV_{len(description.split())}_{''.join(description.split()[:2]).upper()}"

        return Evidence(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            description=description,
            source=self.current_source,
            page_reference=page_ref if page_ref else None,
            confidence=confidence
        )

    def input_confidence(self, prompt: str) -> ConfidenceLevel:
        """Input confidence level"""
        print(f"\n{prompt}:")
        for i, conf in enumerate(ConfidenceLevel, 1):
            print(f"{i}. {conf.value}")

        choice = self.input_int("Select confidence level: ")
        confidence_levels = list(ConfidenceLevel)
        return confidence_levels[choice - 1] if 1 <= choice <= len(confidence_levels) else ConfidenceLevel.POSSIBLE

    def input_int(self, prompt: str) -> Optional[int]:
        """Input integer with None option"""
        value = input(prompt).strip()
        try:
            return int(value) if value else None
        except ValueError:
            return None

    def confirm(self, prompt: str) -> bool:
        """Confirmation prompt"""
        response = input(prompt).strip().lower()
        return response in ['y', 'yes', '1', 'true']

    def quick_entry_mode(self):
        """Quick entry mode for bulk data entry"""
        print("\n" + "-"*50)
        print("⚡ QUICK ENTRY MODE")
        print("-"*50)
        print("Enter data in format: TYPE|NAME|DETAILS|PAGE")
        print("Types: PERSON, ORG, RELATION, FLOW")
        print("Example: PERSON|John Smith|CIA agent 1960-1975|p.45")
        print("Type 'done' to exit quick mode")
        print("-"*50)

        while True:
            entry = input("Quick entry: ").strip()
            if entry.lower() == 'done':
                break

            try:
                parts = entry.split('|')
                if len(parts) >= 3:
                    entry_type, name, details = parts[0], parts[1], parts[2]
                    page = parts[3] if len(parts) > 3 else None

                    if entry_type.upper() == 'PERSON':
                        self.quick_add_person(name, details, page)
                    elif entry_type.upper() == 'ORG':
                        self.quick_add_organization(name, details, page)
                    else:
                        print(f"⚠️  Unknown type: {entry_type}")
                else:
                    print("❌ Invalid format. Use: TYPE|NAME|DETAILS|PAGE")
            except Exception as e:
                print(f"❌ Error processing entry: {e}")

    def quick_add_person(self, name: str, details: str, page: str = None):
        """Quick add person from condensed information"""
        name_parts = name.strip().split()
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = name_parts[-1] if len(name_parts) > 1 else "Unknown"

        person_id = f"PERS_{last_name.upper()}_{first_name.upper()}"

        # Create basic evidence
        evidence = Evidence(
            evidence_id=f"EV_QUICK_{person_id}",
            evidence_type=EvidenceType.BOOK,
            description=details,
            source=self.current_source,
            page_reference=page,
            confidence=ConfidenceLevel.POSSIBLE
        )

        # Create basic claim
        claim = Claim(
            claim_id=f"CL_QUICK_{person_id}",
            statement=details,
            category="biographical",
            supporting_evidence=[evidence],
            overall_confidence=ConfidenceLevel.POSSIBLE
        )

        person = PersonDossier(
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            significant_activities=[claim]
        )

        if self.db.add_person(person):
            print(f"✅ Quick added: {name}")
        else:
            print(f"❌ Failed to add: {name}")

    def search_menu(self):
        """Search and browse database"""
        print("\n" + "-"*50)
        print("🔍 DATABASE SEARCH")
        print("-"*50)

        query = input("Search query: ").strip()

        # Search people
        people = self.db.search_people(query)
        if people:
            print(f"\n👤 People found ({len(people)}):")
            for person in people:
                print(f"  - {person.first_name} {person.last_name} ({person.person_id})")

        # TODO: Add organization search, relationship search, etc.

    def generate_timeline(self):
        """Generate chronological timeline"""
        print("\n" + "-"*50)
        print("📅 TIMELINE GENERATION")
        print("-"*50)

        start_year = self.input_int("Start year (or blank for all): ")
        end_year = self.input_int("End year (or blank for all): ")

        timeline = self.db.get_timeline(start_year, end_year)

        print(f"\n📊 Timeline Events ({len(timeline)}):")
        for event in timeline[:20]:  # Show first 20
            print(f"  {event['event_date']}: {event['description']}")

    def analyze_networks(self):
        """Analyze relationship networks"""
        print("\n" + "-"*50)
        print("🕸️  NETWORK ANALYSIS")
        print("-"*50)

        entity_id = input("Entity ID to analyze: ").strip()

        analysis = self.db.analyze_relationships(entity_id)

        print(f"\n📊 Network Analysis for {entity_id}:")
        print(f"  Direct relationships: {len(analysis['direct_relationships'])}")
        print(f"  Obscured relationships: {len(analysis['obscured_relationships'])}")
        print(f"  High significance: {len(analysis['high_significance'])}")

    def export_evidence(self):
        """Export evidence in various formats"""
        print("\n" + "-"*50)
        print("📤 EVIDENCE EXPORT")
        print("-"*50)
        print("Export functionality would generate:")
        print("  - JSON evidence files")
        print("  - Timeline visualizations")
        print("  - Network maps")
        print("  - Evidence validation reports")


def main():
    """Main entry point"""
    print("🔍 Operation Gladio Evidence Builder")
    print("====================================")

    # Test database connection
    try:
        entry_system = GladioDataEntry()
        print("✅ Database initialized successfully")
        entry_system.main_menu()
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()