#!/usr/bin/env python3
"""
DuPont Dynasty Intelligence Extractor
Sherlock Evidence Analysis System

Extracts intelligence claims from "The DuPont Dynasty: From Gunpowder to the Military-Industrial Complex"
Focus: Industrial dynasty connections to military, political, and financial power structures
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict

@dataclass
class Claim:
    claim_id: str
    text: str
    claim_type: str  # direct_connection, corporate_role, political_position, institutional_link
    entities: List[str]
    category: str  # origins, expansion, wwi, wwii, manhattan_project, political, corporate, modern
    institution: str
    time_period: str
    evidence_source: str
    significance: str
    confidence: float
    cross_references: List[str] = None

class DuPontDynastyExtractor:
    def __init__(self):
        self.output_dir = Path("/home/johnny5/Sherlock/dupont_dynasty_intelligence")
        self.output_dir.mkdir(exist_ok=True)

        self.claims = []

    def extract_all_claims(self):
        """Extract all claims from DuPont Dynasty report"""
        print("\n📋 Extracting DuPont Dynasty claims...")

        # Origins (1800s)
        self._extract_origins_claims()

        # 19th Century Expansion
        self._extract_expansion_claims()

        # WWI Era
        self._extract_wwi_claims()

        # Chemical Diversification
        self._extract_chemical_diversification_claims()

        # General Motors Connection
        self._extract_gm_claims()

        # Manhattan Project
        self._extract_manhattan_project_claims()

        # Cold War MIC
        self._extract_cold_war_claims()

        # Political Influence
        self._extract_political_claims()

        # Strategic Partnerships
        self._extract_partnership_claims()

        # Contemporary Legacy
        self._extract_contemporary_claims()

        print(f"✅ Extracted {len(self.claims)} total claims")

    def _extract_origins_claims(self):
        """Extract claims about DuPont origins (1800-1850s)"""

        self.claims.append(Claim(
            claim_id="dupont_origins_001",
            text="Éleuthère Irénée du Pont (1771-1834), French aristocrat and chemist trained under Antoine Lavoisier, fled French Revolution and emigrated to U.S. in 1800",
            claim_type="direct_connection",
            entities=["Éleuthère Irénée du Pont", "Antoine Lavoisier", "French Revolution"],
            category="origins",
            institution="DuPont Company",
            time_period="1771-1800",
            evidence_source="DuPont Dynasty report - Origins section",
            significance="Dynasty founder with elite scientific training from Lavoisier (father of modern chemistry)",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_origins_002",
            text="Founded E.I. du Pont de Nemours & Company in 1802 on Brandywine River in Delaware to manufacture gunpowder, quickly becoming leading supplier for U.S. military",
            claim_type="direct_connection",
            entities=["E.I. du Pont de Nemours & Company", "U.S. military", "gunpowder", "Delaware"],
            category="origins",
            institution="U.S. Military Supply",
            time_period="1802",
            evidence_source="DuPont Dynasty report - Origins section",
            significance="Establishment as primary military contractor from founding - U.S. defense dependency from inception",
            confidence=0.95,
            cross_references=["Network Intersection: DuPont Manhattan Project contractor"]
        ))

        self.claims.append(Claim(
            claim_id="dupont_origins_003",
            text="DuPont supplied most of the gunpowder used by U.S. forces during Napoleonic Wars and War of 1812; rise paralleled American expansion and need for domestic munitions",
            claim_type="direct_connection",
            entities=["U.S. forces", "War of 1812", "gunpowder", "military supply"],
            category="origins",
            institution="U.S. Military",
            time_period="1800-1815",
            evidence_source="DuPont Dynasty report - Origins section",
            significance="Military contractor monopoly during early American expansion wars",
            confidence=0.9
        ))

    def _extract_expansion_claims(self):
        """Extract 19th century expansion claims"""

        self.claims.append(Claim(
            claim_id="dupont_expansion_001",
            text="DuPont supplied over half of Union Army's gunpowder during Civil War, solidifying role as critical national defense contractor and economic engine in postwar U.S.",
            claim_type="direct_connection",
            entities=["Union Army", "Civil War", "gunpowder", "national defense"],
            category="expansion",
            institution="U.S. Military",
            time_period="1861-1865",
            evidence_source="DuPont Dynasty report - Expansion section",
            significance="Civil War cemented DuPont as indispensable military-industrial partner",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_expansion_002",
            text="DuPont family-run for over a century, forming clan-like corporate aristocracy, marrying into other industrial families like Ball family of glass manufacturing",
            claim_type="institutional_link",
            entities=["DuPont family", "Ball family", "corporate aristocracy", "dynastic marriage"],
            category="expansion",
            institution="Industrial Dynasties",
            time_period="1800s-1900s",
            evidence_source="DuPont Dynasty report - Expansion section",
            significance="Dynastic marriage alliances consolidating industrial power across sectors",
            confidence=0.85,
            cross_references=["Network Intersection: DuPont-Mellon intermarriage"]
        ))

    def _extract_wwi_claims(self):
        """Extract WWI-era claims"""

        self.claims.append(Claim(
            claim_id="dupont_wwi_001",
            text="By 1918, DuPont produced over 50% of the world's explosives",
            claim_type="direct_connection",
            entities=["DuPont", "WWI", "explosives", "global monopoly"],
            category="wwi",
            institution="Military-Industrial Complex",
            time_period="1914-1918",
            evidence_source="DuPont Dynasty report - WWI section",
            significance="Global explosives monopoly during WWI - unprecedented industrial military power",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_wwi_002",
            text="DuPont created subsidiaries Hercules Powder Co. and Atlas Powder Co. to avoid antitrust breakup, though family retained indirect control",
            claim_type="corporate_role",
            entities=["Hercules Powder Co.", "Atlas Powder Co.", "antitrust", "corporate shell"],
            category="wwi",
            institution="Corporate Structure",
            time_period="1912-1918",
            evidence_source="DuPont Dynasty report - WWI section",
            significance="Corporate shell game to evade antitrust regulation while maintaining monopoly control",
            confidence=0.9
        ))

        self.claims.append(Claim(
            claim_id="dupont_wwi_003",
            text="DuPont partnered with British and French firms, setting up international arms and chemical monopolies",
            claim_type="institutional_link",
            entities=["British firms", "French firms", "international monopolies", "arms trade"],
            category="wwi",
            institution="International Arms Cartel",
            time_period="1914-1920s",
            evidence_source="DuPont Dynasty report - WWI section",
            significance="International cartel coordination across Allied powers - transnational military-industrial complex",
            confidence=0.85
        ))

    def _extract_chemical_diversification_claims(self):
        """Extract chemical diversification claims"""

        self.claims.append(Claim(
            claim_id="dupont_chem_001",
            text="In 1920s-30s, DuPont expanded into synthetic chemistry: cellophane, nylon, Teflon, neoprene, and later Kevlar and Freon",
            claim_type="corporate_role",
            entities=["synthetic chemistry", "nylon", "Teflon", "Kevlar", "neoprene", "Freon"],
            category="chemical_diversification",
            institution="Chemical Industry",
            time_period="1920s-1940s",
            evidence_source="DuPont Dynasty report - Diversification section",
            significance="Diversification into materials critical for defense, aerospace, and consumer control",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_chem_002",
            text="DuPont innovations seeded role in textiles, aviation, refrigeration, and eventually defense electronics and coatings",
            claim_type="institutional_link",
            entities=["textiles", "aviation", "defense electronics", "coatings"],
            category="chemical_diversification",
            institution="Defense Supply Chain",
            time_period="1930s-1950s",
            evidence_source="DuPont Dynasty report - Diversification section",
            significance="Material monopoly across critical defense and civilian infrastructure sectors",
            confidence=0.9
        ))

    def _extract_gm_claims(self):
        """Extract General Motors connection claims"""

        self.claims.append(Claim(
            claim_id="dupont_gm_001",
            text="Pierre S. du Pont was president of General Motors (1920-1923) and chairman until 1929; DuPont had substantial ownership of GM stock and directed early mass production strategy",
            claim_type="corporate_role",
            entities=["Pierre S. du Pont", "General Motors", "GM president", "mass production"],
            category="corporate",
            institution="General Motors",
            time_period="1920-1929",
            evidence_source="DuPont Dynasty report - GM section",
            significance="DuPont control of largest American automaker - automotive-chemical-defense integration",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_gm_002",
            text="DuPont ownership of GM linked dynasty deeply to automotive and later aerospace supply chain",
            claim_type="institutional_link",
            entities=["General Motors", "automotive", "aerospace", "supply chain"],
            category="corporate",
            institution="Aerospace-Automotive Complex",
            time_period="1920s-1950s",
            evidence_source="DuPont Dynasty report - GM section",
            significance="Control of automotive sector provided foundation for aerospace/defense manufacturing dominance",
            confidence=0.9
        ))

    def _extract_manhattan_project_claims(self):
        """Extract Manhattan Project claims"""

        self.claims.append(Claim(
            claim_id="dupont_manhattan_001",
            text="DuPont built and operated Hanford Site in Washington, responsible for producing plutonium for Fat Man bomb dropped on Nagasaki",
            claim_type="direct_connection",
            entities=["Hanford Site", "plutonium", "Fat Man bomb", "Nagasaki", "Manhattan Project"],
            category="manhattan_project",
            institution="Manhattan Project",
            time_period="1943-1945",
            evidence_source="DuPont Dynasty report - Manhattan Project section",
            significance="DuPont produced plutonium for atomic bomb - direct role in nuclear weapons program",
            confidence=0.95,
            cross_references=["Network Intersection: DuPont Hanford plutonium production", "Master Dynasty: Harvey Bundy coordinated DuPont contractors"]
        ))

        self.claims.append(Claim(
            claim_id="dupont_manhattan_002",
            text="Though reluctant initially, DuPont was selected for Hanford due to technical expertise and loyalty to U.S. government",
            claim_type="institutional_link",
            entities=["Hanford", "technical expertise", "government loyalty"],
            category="manhattan_project",
            institution="U.S. Government",
            time_period="1943",
            evidence_source="DuPont Dynasty report - Manhattan Project section",
            significance="Government selection based on proven loyalty - trusted partner for most sensitive military program",
            confidence=0.9
        ))

        self.claims.append(Claim(
            claim_id="dupont_manhattan_003",
            text="Hanford initiated DuPont legacy in nuclear infrastructure",
            claim_type="institutional_link",
            entities=["Hanford", "nuclear infrastructure", "atomic energy"],
            category="manhattan_project",
            institution="Nuclear Industry",
            time_period="1945-present",
            evidence_source="DuPont Dynasty report - Manhattan Project section",
            significance="Atomic weapons production established DuPont as nuclear industry cornerstone",
            confidence=0.9
        ))

    def _extract_cold_war_claims(self):
        """Extract Cold War MIC claims"""

        self.claims.append(Claim(
            claim_id="dupont_coldwar_001",
            text="DuPont developed radiation shielding, polymers for military applications, protective coatings, radar components, and advanced fibers during Cold War",
            claim_type="direct_connection",
            entities=["radiation shielding", "military polymers", "radar", "advanced fibers", "Cold War"],
            category="cold_war",
            institution="Military-Industrial Complex",
            time_period="1945-1990",
            evidence_source="DuPont Dynasty report - Cold War section",
            significance="Critical materials for nuclear, aerospace, and electronics warfare systems",
            confidence=0.9
        ))

        self.claims.append(Claim(
            claim_id="dupont_coldwar_002",
            text="DuPont partnered with DARPA-affiliated scientists and military labs to develop next-gen materials",
            claim_type="institutional_link",
            entities=["DARPA", "military labs", "advanced materials", "defense research"],
            category="cold_war",
            institution="DARPA",
            time_period="1958-1990",
            evidence_source="DuPont Dynasty report - Cold War section",
            significance="Direct integration with Pentagon advanced research programs",
            confidence=0.85
        ))

        self.claims.append(Claim(
            claim_id="dupont_coldwar_003",
            text="DuPont maintained relationships with J.P. Morgan, Sullivan & Cromwell, and BBH through financial structuring and legal counsel",
            claim_type="institutional_link",
            entities=["J.P. Morgan", "Sullivan & Cromwell", "BBH", "financial structuring"],
            category="cold_war",
            institution="Wall Street Finance",
            time_period="1940s-1980s",
            evidence_source="DuPont Dynasty report - Deep Interlocks section",
            significance="DuPont integration with same financial-legal nexus as other dynasties (Rockefeller, Dulles, Harriman)",
            confidence=0.9,
            cross_references=["Network Intersection: S&C represented major corporations", "Master Dynasty: BBH banking cartel"]
        ))

        self.claims.append(Claim(
            claim_id="dupont_coldwar_004",
            text="DuPont lawyers often came from Sullivan & Cromwell, managing antitrust and international patent negotiations",
            claim_type="institutional_link",
            entities=["Sullivan & Cromwell", "antitrust", "patent law"],
            category="cold_war",
            institution="Sullivan & Cromwell",
            time_period="1920s-1980s",
            evidence_source="DuPont Dynasty report - Deep Interlocks section",
            significance="Legal counsel from same firm as Dulles brothers - Wall Street-intelligence-industrial nexus",
            confidence=0.85,
            cross_references=["Network Intersection: S&C as Wall Street-intelligence nexus"]
        ))

        self.claims.append(Claim(
            claim_id="dupont_coldwar_005",
            text="DuPont executives sat on boards of Brookings, MIT, National Defense Research Committee, and Committee for Economic Development (Cold War policy-shaping group)",
            claim_type="institutional_link",
            entities=["Brookings Institution", "MIT", "National Defense Research Committee", "Committee for Economic Development"],
            category="cold_war",
            institution="Policy Think Tanks",
            time_period="1940s-1980s",
            evidence_source="DuPont Dynasty report - Deep Interlocks section",
            significance="DuPont governance of institutions shaping Cold War economic and defense policy",
            confidence=0.85
        ))

    def _extract_political_claims(self):
        """Extract political influence claims"""

        self.claims.append(Claim(
            claim_id="dupont_political_001",
            text="T. Coleman du Pont served as U.S. Senator (Delaware) 1925-28",
            claim_type="political_position",
            entities=["T. Coleman du Pont", "U.S. Senate", "Delaware"],
            category="political",
            institution="U.S. Senate",
            time_period="1925-1928",
            evidence_source="DuPont Dynasty report - Political section",
            significance="Direct political representation in U.S. Senate",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_political_002",
            text="Pierre S. du Pont IV served as Governor of Delaware (1977-85) and GOP presidential candidate",
            claim_type="political_position",
            entities=["Pierre S. du Pont IV", "Governor", "Delaware", "GOP presidential candidate"],
            category="political",
            institution="State Government",
            time_period="1977-1985",
            evidence_source="DuPont Dynasty report - Political section",
            significance="Multi-generational political dynasty maintaining state-level control",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_political_003",
            text="Long-term DuPont lobbying apparatus in D.C. via Chemical Manufacturers Association and later American Chemistry Council",
            claim_type="institutional_link",
            entities=["Chemical Manufacturers Association", "American Chemistry Council", "lobbying"],
            category="political",
            institution="Lobbying Infrastructure",
            time_period="1950s-present",
            evidence_source="DuPont Dynasty report - Political section",
            significance="Permanent lobbying infrastructure for chemical industry policy control",
            confidence=0.9
        ))

        self.claims.append(Claim(
            claim_id="dupont_political_004",
            text="DuPont influential in shaping EPA policy, nuclear regulation, patent law, and chemical safety thresholds",
            claim_type="institutional_link",
            entities=["EPA", "nuclear regulation", "patent law", "chemical safety"],
            category="political",
            institution="Federal Regulation",
            time_period="1970-present",
            evidence_source="DuPont Dynasty report - Political section",
            significance="Regulatory capture - shaping rules governing own industry",
            confidence=0.85
        ))

    def _extract_partnership_claims(self):
        """Extract strategic partnership claims"""

        self.claims.append(Claim(
            claim_id="dupont_partner_001",
            text="DuPont held majority shareholder position in General Motors (1910s-1950s) with Pierre du Pont as President",
            claim_type="corporate_role",
            entities=["General Motors", "majority shareholder", "Pierre du Pont"],
            category="corporate",
            institution="General Motors",
            time_period="1910s-1950s",
            evidence_source="DuPont Dynasty report - Strategic Partners table",
            significance="Corporate control of largest American automaker for 40 years",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_partner_002",
            text="DuPont served as primary construction and operator of Hanford nuclear plutonium production facility",
            claim_type="direct_connection",
            entities=["Hanford", "plutonium", "nuclear facility"],
            category="manhattan_project",
            institution="Manhattan Project",
            time_period="1943-1945",
            evidence_source="DuPont Dynasty report - Strategic Partners table",
            significance="Direct operational control of atomic bomb material production",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_partner_003",
            text="Sullivan & Cromwell served as key legal advisers to DuPont in antitrust and international law",
            claim_type="institutional_link",
            entities=["Sullivan & Cromwell", "legal counsel", "antitrust"],
            category="cold_war",
            institution="Sullivan & Cromwell",
            time_period="1920s-1980s",
            evidence_source="DuPont Dynasty report - Strategic Partners table",
            significance="Same legal firm as Dulles brothers - Wall Street-intelligence-corporate nexus",
            confidence=0.9
        ))

        self.claims.append(Claim(
            claim_id="dupont_partner_004",
            text="J.P. Morgan & Co. served as long-term financial partner and bond underwriter for DuPont",
            claim_type="institutional_link",
            entities=["J.P. Morgan", "financial partner", "bond underwriter"],
            category="corporate",
            institution="J.P. Morgan",
            time_period="1900s-1980s",
            evidence_source="DuPont Dynasty report - Strategic Partners table",
            significance="Integration with Morgan financial empire - same nexus as Rockefeller/Harriman networks",
            confidence=0.9
        ))

        self.claims.append(Claim(
            claim_id="dupont_partner_005",
            text="DuPont family had indirect representation on elite policy boards: Brookings, CFR, MITRE",
            claim_type="institutional_link",
            entities=["Brookings Institution", "Council on Foreign Relations", "MITRE"],
            category="political",
            institution="Policy Elite",
            time_period="1940s-present",
            evidence_source="DuPont Dynasty report - Strategic Partners table",
            significance="Governance of institutions shaping defense, intelligence, and economic policy",
            confidence=0.8
        ))

        self.claims.append(Claim(
            claim_id="dupont_partner_006",
            text="DuPont family companies tied to postwar intelligence industrial base via CIA/OSS indirect connections",
            claim_type="institutional_link",
            entities=["CIA", "OSS", "intelligence industrial base"],
            category="cold_war",
            institution="CIA/OSS",
            time_period="1945-1980s",
            evidence_source="DuPont Dynasty report - Strategic Partners table",
            significance="Chemical/materials supply to intelligence apparatus and covert programs",
            confidence=0.75,
            cross_references=["Network Intersection: DuPont MK-Ultra chemical research"]
        ))

    def _extract_contemporary_claims(self):
        """Extract contemporary legacy claims"""

        self.claims.append(Claim(
            claim_id="dupont_contemporary_001",
            text="DuPont merged with Dow Chemical (2017) to form DowDuPont, later split into Corteva (agri), DuPont (materials), and Dow Inc. (chemicals)",
            claim_type="corporate_role",
            entities=["Dow Chemical", "DowDuPont", "Corteva", "merger"],
            category="modern",
            institution="Chemical Industry",
            time_period="2017-2019",
            evidence_source="DuPont Dynasty report - Contemporary section",
            significance="Corporate restructuring maintaining sectoral dominance under new brands",
            confidence=0.95
        ))

        self.claims.append(Claim(
            claim_id="dupont_contemporary_002",
            text="DuPont still produces defense-related products: armor, electronics, sensors, aerospace polymers",
            claim_type="direct_connection",
            entities=["armor", "electronics", "sensors", "aerospace polymers", "defense"],
            category="modern",
            institution="Modern MIC",
            time_period="2000s-present",
            evidence_source="DuPont Dynasty report - Contemporary section",
            significance="Continued military-industrial role in 21st century warfare systems",
            confidence=0.9
        ))

        self.claims.append(Claim(
            claim_id="dupont_contemporary_003",
            text="DuPont tied to surveillance infrastructure and biopharma coatings",
            claim_type="institutional_link",
            entities=["surveillance", "biopharma", "coatings"],
            category="modern",
            institution="Surveillance State",
            time_period="2000s-present",
            evidence_source="DuPont Dynasty report - Contemporary section",
            significance="Materials enabling modern surveillance and biotech control systems",
            confidence=0.8
        ))

        self.claims.append(Claim(
            claim_id="dupont_contemporary_004",
            text="DuPont descendants manage investment vehicles, serve on boards (Nemours Foundation), and influence academic policy via donations",
            claim_type="institutional_link",
            entities=["investment vehicles", "Nemours Foundation", "academic policy", "donations"],
            category="modern",
            institution="Philanthropy/Academia",
            time_period="2000s-present",
            evidence_source="DuPont Dynasty report - Contemporary section",
            significance="Dynastic wealth preservation and continued institutional influence through foundations",
            confidence=0.85
        ))

    def generate_reports(self):
        """Generate all intelligence reports"""
        print("\n📊 Generating intelligence reports...")

        # Save all claims as JSON
        claims_path = self.output_dir / "dupont_dynasty_all_claims.json"
        with open(claims_path, 'w') as f:
            json.dump([asdict(c) for c in self.claims], f, indent=2)
        print(f"✅ All claims: {claims_path}")

        # Generate institutional breakdown
        self._generate_institutional_matrix()

        # Generate markdown report
        self._generate_markdown_report()

    def _generate_institutional_matrix(self):
        """Generate institutional connection matrix"""

        institutions = {}
        for claim in self.claims:
            inst = claim.institution
            if inst not in institutions:
                institutions[inst] = {
                    'total_claims': 0,
                    'direct_connections': 0,
                    'corporate_roles': 0,
                    'political_positions': 0,
                    'institutional_links': 0,
                    'time_span': [],
                    'claims': []
                }

            institutions[inst]['total_claims'] += 1
            institutions[inst]['claims'].append(claim.claim_id)
            institutions[inst]['time_span'].append(claim.time_period)

            if claim.claim_type == 'direct_connection':
                institutions[inst]['direct_connections'] += 1
            elif claim.claim_type == 'corporate_role':
                institutions[inst]['corporate_roles'] += 1
            elif claim.claim_type == 'political_position':
                institutions[inst]['political_positions'] += 1
            elif claim.claim_type == 'institutional_link':
                institutions[inst]['institutional_links'] += 1

        matrix_path = self.output_dir / "dupont_institutional_matrix.json"
        with open(matrix_path, 'w') as f:
            json.dump(institutions, f, indent=2)
        print(f"✅ Institutional matrix: {matrix_path}")

    def _generate_markdown_report(self):
        """Generate comprehensive markdown report"""

        report_path = self.output_dir / "DUPONT_DYNASTY_INTELLIGENCE_REPORT.md"

        with open(report_path, 'w') as f:
            f.write(f"""# DuPont Dynasty Intelligence Report
**Generated:** {datetime.now().isoformat()}
**System:** Sherlock Evidence Analysis System
**Source Document:** The DuPont Dynasty: From Gunpowder to the Military-Industrial Complex

## Executive Summary

This document provides comprehensive intelligence extraction on the **DuPont dynasty**, tracing their evolution from 18th-century French emigré chemists to central pillars of the American military-industrial complex.

**Total Claims Extracted:** {len(self.claims)}

---

## Institutional Connections Summary

""")

            # Count by institution
            inst_counts = {}
            for claim in self.claims:
                inst = claim.institution
                inst_counts[inst] = inst_counts.get(inst, 0) + 1

            for inst, count in sorted(inst_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{inst}**: {count} claims\n")

            f.write(f"""

---

## CRITICAL FINDINGS

### 1. Military-Industrial Foundation (1802)

**Founding as Military Contractor:**
- Éleuthère Irénée du Pont founded company in **1802** specifically to manufacture **gunpowder**
- **IMMEDIATELY became leading supplier to U.S. military**
- Dynasty built on war from inception - not civilian commerce

**Evidence:** Company established during Napoleonic Wars, supplied War of 1812, became Union Army's primary explosives supplier (50%+ of Civil War gunpowder)

**Significance:** Unlike opium dynasties (merchant wealth → political power), DuPont was **purpose-built for military supply** - direct defense contractor monopoly from founding

---

### 2. Global Explosives Monopoly (WWI)

**50% of World's Explosives (1918):**
- By end of WWI, DuPont controlled **over half of global explosives production**
- Created shell subsidiaries (Hercules, Atlas) to evade antitrust breakup
- International cartel partnerships with British/French firms

**Significance:** Unprecedented global military-industrial monopoly - single family controlled majority of world's warfighting explosives capability

---

### 3. Automotive-Industrial Integration

**General Motors Control (1920-1950s):**
- **Pierre S. du Pont** was GM President (1920-1923), Chairman (until 1929)
- DuPont held **majority shareholder position** in GM for 40 years
- Directed mass production strategy

**Significance:** Control of largest American automaker integrated DuPont into transportation, logistics, and later **aerospace/defense vehicle manufacturing**

**Cross-Reference:** GM became major defense contractor (tanks, aircraft, missiles) - DuPont chemical-automotive-defense vertical integration

---

### 4. Manhattan Project - Plutonium Production

**Hanford Site Operator (1943-1945):**
- DuPont **built and operated Hanford Engineer Works**
- Produced **plutonium for Nagasaki bomb (Fat Man)**
- Selected due to "technical expertise and **loyalty to U.S. government**"

**Significance:** DuPont directly enabled atomic bombing of Japan - established nuclear industry role continuing to present

**Cross-References:**
- Network Intersection: "DuPont arguably single biggest industrial task of Manhattan Project"
- Master Dynasty: Harvey Bundy coordinated DuPont contractors

---

### 5. Wall Street-Intelligence Nexus

**Sullivan & Cromwell Legal Counsel:**
- DuPont lawyers came from **Sullivan & Cromwell** (Dulles brothers' firm)
- S&C managed antitrust evasion and international patent law

**J.P. Morgan Financial Partner:**
- Long-term bond underwriting and financial structuring

**Significance:** DuPont integrated into **same Wall Street-intelligence nexus** as Rockefeller, Harriman, Dulles dynasties

**Cross-References:**
- Network Intersection: S&C represented Standard Oil (Rockefeller), advised on IG Farben deals
- Network Intersection: S&C as Wall Street-intelligence bridge under Dulles brothers

---

### 6. Policy Elite Governance

**Board Representation:**
- **Brookings Institution** - defense/economic policy
- **MIT** - defense technology research
- **National Defense Research Committee** - WWII weapons development
- **Committee for Economic Development** - Cold War economic policy
- **CFR** (indirect) - foreign policy elite
- **MITRE** (indirect) - defense systems engineering

**Significance:** DuPont governance of institutions **shaping the policies regulating DuPont** - classic regulatory capture

---

### 7. Cold War MIC Integration

**Critical Materials Monopoly:**
- Radiation shielding (nuclear)
- Military polymers (aerospace)
- Radar components (electronics warfare)
- Advanced fibers (Kevlar for armor)
- Protective coatings (stealth, chemical protection)

**DARPA Partnership:**
- Direct collaboration with Pentagon advanced research programs

**Significance:** DuPont materials are **foundational to modern warfare systems** - no advanced military without DuPont innovations

---

### 8. Political Dynasty

**Direct Political Representation:**
- **T. Coleman du Pont**: U.S. Senator (Delaware) 1925-28
- **Pierre S. du Pont IV**: Governor (Delaware) 1977-85, GOP presidential candidate

**Lobbying Infrastructure:**
- Chemical Manufacturers Association
- American Chemistry Council
- Influence over EPA, nuclear regulation, patent law, chemical safety standards

**Significance:** Multi-generational political dynasty maintaining **state capture** (Delaware) and **federal regulatory influence**

---

### 9. Modern Continuity (2017-Present)

**DowDuPont Merger:**
- Merged with Dow Chemical (2017), split into 3 companies (2019)
- **Still produces defense products**: armor, sensors, aerospace polymers
- Tied to **surveillance infrastructure** and biopharma

**Dynasty Preservation:**
- Investment vehicles
- Nemours Foundation (board positions)
- Academic policy influence via donations

**Significance:** Corporate restructuring **maintains sectoral dominance** while preserving dynastic wealth and institutional influence

---

## THE DUPONT PATTERN

### Unique Characteristics vs Other Dynasties:

**DuPont Dynasty:**
- **Founded AS military contractor** (1802) - not merchant wealth conversion
- **Global monopoly** in core warfighting capability (explosives 50% by 1918)
- **Vertical integration**: chemicals → automotive → aerospace → nuclear
- **Direct government partnership** from inception (trusted for Manhattan Project)

**Comparison to Opium Dynasties:**
- **Opium families**: Merchant wealth (1820s-1890s) → Yale/S&B → BBH → CIA → Globalism
- **DuPont**: Military supplier (1802) → Industrial monopoly → GM control → Manhattan Project → Modern MIC

**Key Difference:** DuPont **WAS the military-industrial complex** from founding, while opium dynasties **BECAME the intelligence-globalist complex** through institutional evolution

---

## CROSS-REFERENCES TO MASTER DYNASTY ANALYSIS

### Confirmed Overlaps:

1. **Manhattan Project:**
   - DuPont: Hanford plutonium production (primary contractor)
   - Stone & Webster (Forbes): Oak Ridge uranium enrichment
   - Harvey Bundy (BBH/S&B): Pentagon liaison coordinating both

2. **Sullivan & Cromwell:**
   - DuPont: Legal counsel for antitrust, international law
   - Dulles brothers: S&C partners, represented Standard Oil (Rockefeller), advised on cartels
   - Significance: **Same law firm** serving DuPont, Rockefeller, and later CIA directors

3. **J.P. Morgan:**
   - DuPont: Financial partner, bond underwriter
   - BBH/Harriman: Morgan interlock with Brown Brothers
   - AT&T: Morgan group controlled telecom monopoly (1920s)
   - Significance: **Morgan nexus** integrating finance-industry-telecom-defense

4. **MK-Ultra Connection:**
   - Network Intersection: DuPont chemist Dr. Ray Treichler consulted on MK-NAOMI
   - Network Intersection: Rockefeller/Carnegie foundations funded MK-Ultra
   - Significance: DuPont chemical research **tapped for CIA mind-control programs**

5. **Policy Elite Boards:**
   - DuPont: Brookings, MIT, NDRC, CED
   - Rockefeller: CFR (David Rockefeller director 1949)
   - Bundy: CFR, Bilderberg (William P. Bundy Secretary-General)
   - Significance: **Overlapping governance** of Cold War policy institutions

---

## TIMELINE INTEGRATION

**1802** - DuPont founded as gunpowder manufacturer (58 years before first DuPont appears in Network Intersection analysis)

**1861-1865** - Civil War: DuPont supplies 50%+ Union gunpowder

**1918** - WWI: DuPont produces 50% of world's explosives

**1920-1923** - Pierre S. du Pont president of General Motors

**1943-1945** - Manhattan Project: DuPont operates Hanford plutonium production

**1950s** - Cold War: DuPont develops military polymers, radiation shielding, radar components

**1950s** - MK-Ultra: DuPont chemists consulted on CIA chemical weapons (MK-NAOMI)

**1977-1985** - Pierre S. du Pont IV serves as Delaware Governor

**2017** - DowDuPont merger, maintaining defense/surveillance role

---

## STATISTICAL SUMMARY

**Total Claims:** {len(self.claims)}

**Claim Types:**
""")

            claim_types = {}
            for claim in self.claims:
                claim_types[claim.claim_type] = claim_types.get(claim.claim_type, 0) + 1

            for ctype, count in sorted(claim_types.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {ctype}: {count}\n")

            f.write(f"""

**Time Span:** 1771-present (254 years)

**Confidence Distribution:**
- High (0.9-0.95): {len([c for c in self.claims if c.confidence >= 0.9])} claims
- Medium-High (0.8-0.89): {len([c for c in self.claims if 0.8 <= c.confidence < 0.9])} claims
- Medium (0.75-0.79): {len([c for c in self.claims if 0.75 <= c.confidence < 0.8])} claims

---

## SIGNIFICANCE

The DuPont dynasty represents the **PUREST FORM** of American military-industrial power:

1. **Founded specifically for military supply** (1802 gunpowder)
2. **Global monopoly in warfighting capability** (50% world explosives by 1918)
3. **Vertical integration**: chemicals → automotive → aerospace → nuclear
4. **Trusted government partner** for most sensitive programs (Manhattan Project)
5. **Wall Street-intelligence nexus integration** (S&C legal, J.P. Morgan financial)
6. **Policy elite governance** (Brookings, MIT, NDRC, CFR)
7. **Multi-generational political dynasty** (Senate, Governor)
8. **Continuous MIC role** (1802-present, 223 years)

Unlike opium dynasties (merchant → institutional), DuPont **WAS institutional power from inception**.

---

**Classification:** UNCLASSIFIED (public sources)
**Methodology:** Structured intelligence extraction from dynasty report
**Total Claims:** {len(self.claims)}
**Cross-References:** Network Intersection (4 claims), Master Dynasty Analysis
**Confidence:** HIGH (documentary and corporate records)

---

**End of Report**
""")

        print(f"✅ Intelligence report: {report_path}")

def main():
    print("="*80)
    print("DUPONT DYNASTY INTELLIGENCE EXTRACTION")
    print("Sherlock Evidence Analysis System")
    print("="*80)
    print("\nProcessing: The DuPont Dynasty - From Gunpowder to Military-Industrial Complex")
    print("Focus: Industrial dynasty evolution, military-industrial integration\n")

    extractor = DuPontDynastyExtractor()

    try:
        # Extract all claims
        extractor.extract_all_claims()

        # Generate reports
        extractor.generate_reports()

        print("\n" + "="*80)
        print("✅ EXTRACTION COMPLETE")
        print("="*80)
        print(f"\nTotal Claims: {len(extractor.claims)}")
        print(f"Output Directory: {extractor.output_dir}")
        print("\nGenerated Files:")
        print("  1. dupont_dynasty_all_claims.json")
        print("  2. dupont_institutional_matrix.json")
        print("  3. DUPONT_DYNASTY_INTELLIGENCE_REPORT.md")

        # Summary statistics
        by_category = {}
        for claim in extractor.claims:
            cat = claim.category
            by_category[cat] = by_category.get(cat, 0) + 1

        print("\n📊 CLAIMS BY CATEGORY:")
        for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat}: {count}")

        print("\n🎯 KEY FINDINGS:")
        print("  - Founded 1802 as military gunpowder contractor")
        print("  - 50% of world's explosives by WWI (1918)")
        print("  - Pierre S. du Pont president of General Motors (1920-1923)")
        print("  - Hanford plutonium production for Nagasaki bomb (1943-1945)")
        print("  - Sullivan & Cromwell legal counsel (Wall Street-intelligence nexus)")
        print("  - J.P. Morgan financial partner (same nexus as Rockefeller/Harriman)")
        print("  - Board governance: Brookings, MIT, CFR, MITRE")
        print("  - Multi-generational political dynasty (Senate, Governor)")
        print("  - Continuous MIC role 1802-present (223 years)")

    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
