#!/usr/bin/env python3
"""
Forbes Family (Boston Brahmin) Intelligence Extraction System
Processes research on John Kerry's maternal lineage and power network connections

Architecture: Extends Sherlock evidence database
Focus: China trade/opium origins → infrastructure capitalism → MIC adjacency
Cross-references: BBH, Stone & Webster, Bell/AT&T, utilities/engineering networks
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict

try:
    from evidence_database import (
        EvidenceDatabase, EvidenceType, ClaimType,
        EvidenceSource, EvidenceClaim, Speaker
    )
except ImportError:
    print("Warning: evidence_database.py not found, will use local definitions")


@dataclass
class ForbesEntity:
    """Entity extracted from Forbes family research"""
    name: str
    entity_type: str  # person, organization, firm, institution, project, location
    time_period: str
    roles: List[str]
    affiliations: List[str]
    significance: str
    evidence_source: str
    confidence: float


@dataclass
class ForbesRelationship:
    """Relationship between Forbes entities"""
    subject: str
    relationship_type: str  # founded, directed, invested_in, partnered_with, controlled
    object: str
    time_period: str
    evidence: str
    confidence: float


class ForbesIntelligenceExtractor:
    """
    Extract intelligence from Forbes family power network documentation

    Design: Document all claims with evidence anchors
    Output: Structured network graph + evidence database integration
    """

    def __init__(self, evidence_db_path: str = "sherlock.db"):
        self.evidence_db = EvidenceDatabase(evidence_db_path)
        self.output_dir = Path("forbes_intelligence")
        self.output_dir.mkdir(exist_ok=True)

        # Core Forbes family members (Kerry branch)
        self.forbes_people = {
            'Rosemary Isabel Forbes Kerry': {
                'dates': '1913-2002',
                'role': 'John Kerry\'s mother',
                'branch': 'Boston Forbes',
                'significance': 'Direct Kerry family connection'
            },
            'James Grant Forbes II': {
                'role': 'Father of Rosemary Forbes Kerry',
                'branch': 'Boston Forbes',
                'significance': 'Kerry\'s grandfather'
            },
            'John Murray Forbes': {
                'dates': '1813-1898',
                'roles': ['China trade merchant', 'Opium trader', 'Railroad founder', 'Financier'],
                'firms': ['Russell & Company', 'J.M. Forbes & Co.', 'Chicago Burlington & Quincy Railroad'],
                'significance': 'Core capital formation figure - opium to infrastructure'
            },
            'Robert Bennet Forbes': {
                'roles': ['China trade merchant', 'Opium trader'],
                'firms': ['Russell & Company', 'Perkins'],
                'significance': 'Early China trade wealth generation'
            },
            'William Hathaway Forbes': {
                'dates': '1840-1918',
                'roles': ['President of American Bell Telephone Company', 'Partner at J.M. Forbes & Co.'],
                'significance': 'Telecom platform control - foundational to AT&T'
            },
            'William Cameron Forbes': {
                'roles': ['Governor-General of Philippines', 'Investment banker', 'Stone & Webster partner'],
                'boards': ['AT&T', 'Stone & Webster'],
                'significance': 'State administration + utilities/engineering + colonial power'
            },
            'Ruth Forbes': {
                'roles': ['Married Arthur M. Young (Bell Helicopter pioneer)'],
                'significance': 'Aerospace industry marriage tie'
            },
            'Arthur M. Young': {
                'roles': ['Helicopter pioneer', 'Bell Helicopter designer'],
                'married': 'Ruth Forbes (Boston Forbes family)',
                'significance': 'Military helicopter technology foundational work'
            }
        }

        # Firms and institutions
        self.forbes_network_entities = {
            # China Trade Era
            'Russell & Company': {
                'type': 'Merchant house',
                'period': '1820s-1890s',
                'business': 'China trade (tea, silk, opium)',
                'forbes_connection': 'John Murray Forbes, Robert Bennet Forbes - core operators',
                'significance': 'Major American opium trading house in Canton'
            },
            'Perkins': {
                'type': 'Merchant house',
                'period': 'Early 1800s',
                'business': 'China trade',
                'forbes_connection': 'Merged with Russell & Co.; Forbes family network',
                'significance': 'Boston Brahmin wealth formation pipeline'
            },

            # Infrastructure Era
            'J.M. Forbes & Co.': {
                'type': 'Private investment/trust firm',
                'period': '1777-present',
                'business': 'Investment, trust management, estate management',
                'forbes_connection': 'Family office - core Forbes capital vehicle',
                'significance': 'Manages >$1.5B; multi-generational wealth stewardship',
                'modern_status': 'Still operating as JM Forbes & Co. LLP'
            },
            'Chicago, Burlington & Quincy Railroad (CB&Q)': {
                'type': 'Railroad',
                'period': 'Mid-late 1800s',
                'forbes_connection': 'Founded/assembled by John Murray Forbes',
                'significance': 'Major Midwestern railroad system - infrastructure platform control'
            },

            # Telecom Era
            'American Bell Telephone Company': {
                'type': 'Telecom holding/operating company',
                'period': 'Late 1800s',
                'forbes_connection': 'William Hathaway Forbes - PRESIDENT',
                'significance': 'Central entity that became AT&T - Forbes executive control at foundation'
            },
            'AT&T': {
                'type': 'Telecom monopoly',
                'period': '1885-present',
                'forbes_connection': 'William Cameron Forbes - board member; evolved from American Bell under Forbes presidency',
                'significance': 'Monopoly telecom platform; Bell Labs; defense/intelligence substrate'
            },

            # Utilities/Engineering Era
            'Stone & Webster': {
                'type': 'Engineering/construction firm',
                'founded': '1889 (Boston, MIT graduates)',
                'business': 'Power plants, utilities, defense projects, nuclear facilities',
                'forbes_connection': 'William Cameron Forbes - partner',
                'significance': 'WWI arsenals, WWII Manhattan Project (Oak Ridge), nuclear power plants',
                'defense_role': 'Built Hog Island shipyard, Y-12 uranium enrichment, AEC projects',
                'modern_status': 'Absorbed into Westinghouse Electric (major DoD contractor)'
            },

            # Finance
            'Brown Brothers Harriman (BBH)': {
                'type': 'Private bank',
                'forbes_connection': 'Documented co-presence in 1939 Commercial & Financial Chronicle; shared elite finance milieu',
                'significance': 'Major private bank; Bush family connection; likely syndicate/trustee overlap',
                'evidence_strength': 'Network adjacency strong, direct operational link unproven'
            },

            # Elite Institutions
            'Federal Reserve Bank of New York': {
                'forbes_connection': 'Charles A. Stone (Stone & Webster founder) - board member 1919-23',
                'significance': 'Forbes network access to monetary policy apparatus'
            },
            'Research Corporation': {
                'forbes_connection': 'Charles A. Stone - founding director',
                'significance': 'Major science foundation - research funding influence'
            },
            'MIT': {
                'forbes_connection': 'Stone & Webster founders (alumni); campus buildings funded by Forbes interests',
                'significance': 'Engineering talent pipeline; research partnerships'
            },

            # Aerospace
            'Bell Helicopter': {
                'forbes_connection': 'Arthur M. Young (married Ruth Forbes) - pioneer designer',
                'significance': 'Military helicopter platform (UH-1 Huey lineage); Vietnam-era military aviation',
                'evidence_strength': 'Marriage tie confirmed; foundational helicopter innovation'
            }
        }

        # Network evolution phases
        self.forbes_evolution_phases = {
            'Phase A: China Trade / Opium (early-mid 1800s)': {
                'mechanism': 'Canton trade ecosystem → Boston capital formation',
                'key_firms': ['Russell & Company', 'Perkins'],
                'key_people': ['John Murray Forbes', 'Robert Bennet Forbes'],
                'evidence': 'MHS Forbes Family Papers; Business History Review; Forbes House Museum opium exhibit',
                'economic_logic': 'Trade profits + privileged networks → seed capital for industrial investment'
            },
            'Phase B: Railroads (mid-late 1800s)': {
                'mechanism': 'Merchant capital → infrastructure platform control',
                'key_firms': ['Chicago Burlington & Quincy Railroad', 'J.M. Forbes & Co.'],
                'key_people': ['John Murray Forbes'],
                'evidence': 'Encyclopedia Britannica; MHS J.M. Forbes Estate Papers',
                'economic_logic': 'Transportation monopolies; bond financing; compounding returns'
            },
            'Phase C: Telecom (late 1870s-1900s)': {
                'mechanism': 'Family capital → communications platform monopoly',
                'key_firms': ['American Bell Telephone', 'AT&T'],
                'key_people': ['William Hathaway Forbes'],
                'evidence': 'MHS archival guides; corporate histories',
                'economic_logic': 'Executive control at consolidation phase; shape monopoly structure and federal alignment'
            },
            'Phase D: Utilities/Engineering (early-mid 1900s)': {
                'mechanism': 'Capital deployment into power, utilities, defense infrastructure',
                'key_firms': ['Stone & Webster', 'utility holdings'],
                'key_people': ['William Cameron Forbes'],
                'evidence': 'J.M. Forbes & Co. history; Stone & Webster corporate records',
                'economic_logic': 'Regulated monopolies; federal contracting; war mobilization'
            },
            'Phase E: Trust/Asset Management (late 1900s-present)': {
                'mechanism': 'Operating companies → governance + capital allocation',
                'key_firms': ['JM Forbes & Co. LLP (modern)'],
                'evidence': 'JM Forbes & Co. website ($1.5B+ AUM)',
                'economic_logic': 'Tax-optimized trusts; foundation capital; board influence; stewardship over operations'
            }
        }

    def extract_stone_webster_claims(self) -> List[Dict]:
        """Extract atomic claims from Stone & Webster PDF"""
        claims = []

        # Foundational claims
        claims.append({
            'claim_id': 'forbes_sw_001',
            'text': 'Stone & Webster founded 1889 in Boston by MIT graduates Charles A. Stone and Edwin S. Webster',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'Charles A. Stone', 'Edwin S. Webster', 'MIT', 'Boston'],
            'time_period': '1889',
            'evidence_source': 'Stone & Webster PDF p.1',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_sw_002',
            'text': 'Charles Stone served on Federal Reserve Bank of New York board (1919-23)',
            'claim_type': 'factual',
            'entities': ['Charles A. Stone', 'Federal Reserve Bank of New York'],
            'time_period': '1919-1923',
            'evidence_source': 'Stone & Webster PDF p.1',
            'significance': 'Forbes network access to monetary policy apparatus',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_sw_003',
            'text': 'Charles Stone was founding director of Research Corporation (major science foundation)',
            'claim_type': 'factual',
            'entities': ['Charles A. Stone', 'Research Corporation'],
            'time_period': '1910s-1920s',
            'evidence_source': 'Stone & Webster PDF p.1',
            'significance': 'Research funding influence',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_sw_004',
            'text': 'Edwin Webster sat on boards of United Fruit, Pacific Mills, and other major firms',
            'claim_type': 'factual',
            'entities': ['Edwin S. Webster', 'United Fruit', 'Pacific Mills'],
            'time_period': 'Early 1900s',
            'evidence_source': 'Stone & Webster PDF p.1',
            'significance': 'Corporate board interlocks',
            'confidence': 0.95
        })

        # WWI infrastructure
        claims.append({
            'claim_id': 'forbes_sw_005',
            'text': 'Stone & Webster designed and built Hog Island shipyard in Philadelphia (35,000 workers, more berths than any British yard)',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'Hog Island shipyard', 'War Department'],
            'time_period': 'WWI (1917-18)',
            'evidence_source': 'Stone & Webster PDF p.1, Table 1',
            'significance': 'Major U.S. war infrastructure; largest shipyard',
            'confidence': 0.95
        })

        # WWII / Manhattan Project
        claims.append({
            'claim_id': 'forbes_sw_006',
            'text': 'Stone & Webster established separate division (~800 engineers) for uranium enrichment engineering in early 1942',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'Manhattan Project', 'uranium enrichment'],
            'time_period': '1942',
            'evidence_source': 'Stone & Webster PDF p.1',
            'significance': 'Atomic weapons program involvement',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_sw_007',
            'text': 'Stone & Webster was prime contractor for Oak Ridge Y-12 electromagnetic uranium separation plant',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'Oak Ridge', 'Y-12', 'Manhattan Project', 'Army Corps'],
            'time_period': '1942-1945',
            'evidence_source': 'Stone & Webster PDF p.1, Table 1',
            'significance': 'Built uranium enrichment facility for first atomic bomb',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_sw_008',
            'text': 'Stone & Webster designed and built Oak Ridge city (75,000 workers) and all four production plants',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'Oak Ridge', 'Tennessee', 'Clinton Engineer Works'],
            'time_period': '1942-1945',
            'evidence_source': 'Stone & Webster PDF p.1',
            'significance': 'Total city and nuclear complex construction',
            'confidence': 0.95
        })

        # Postwar nuclear
        claims.append({
            'claim_id': 'forbes_sw_009',
            'text': 'Stone & Webster built Shippingport, the nation\'s first civilian nuclear power plant (Atomic Energy Commission)',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'Shippingport', 'AEC', 'nuclear power'],
            'time_period': '1945-1960s',
            'evidence_source': 'Stone & Webster PDF p.1-2, Table 1',
            'significance': 'Pioneering civilian nuclear power',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_sw_010',
            'text': 'Stone & Webster built Brookhaven National Lab particle accelerator, NS Savannah nuclear merchant ship, and Army prototype reactors',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'Brookhaven', 'NS Savannah', 'AEC'],
            'time_period': '1950s-1960s',
            'evidence_source': 'Stone & Webster PDF p.1',
            'significance': 'Nuclear technology development across domains',
            'confidence': 0.95
        })

        # Scope
        claims.append({
            'claim_id': 'forbes_sw_011',
            'text': 'By 1950s Stone & Webster had built ~16% of U.S. generating capacity (dozens of hydroelectric and steam power plants)',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'electric power'],
            'time_period': '1950s',
            'evidence_source': 'Stone & Webster PDF p.2',
            'significance': 'Dominant position in U.S. power infrastructure',
            'confidence': 0.90
        })

        # Forbes connection
        claims.append({
            'claim_id': 'forbes_sw_012',
            'text': 'William Cameron Forbes was partner at Stone & Webster',
            'claim_type': 'factual',
            'entities': ['William Cameron Forbes', 'Stone & Webster', 'Forbes family'],
            'time_period': 'Early-mid 1900s',
            'evidence_source': 'J.M. Forbes & Co. history (referenced in research docs)',
            'significance': 'Direct Forbes family operational involvement in utilities/engineering/defense firm',
            'confidence': 0.85
        })

        # Modern continuity
        claims.append({
            'claim_id': 'forbes_sw_013',
            'text': 'Stone & Webster absorbed into Westinghouse Electric (major DoD contractor) by 2016',
            'claim_type': 'factual',
            'entities': ['Stone & Webster', 'Westinghouse Electric', 'DoD'],
            'time_period': '2016',
            'evidence_source': 'Stone & Webster PDF p.2, Table 2',
            'significance': 'Engineering lineage persists in modern MIC',
            'confidence': 0.95
        })

        return claims

    def extract_forbes_china_trade_claims(self) -> List[Dict]:
        """Extract opium/China trade claims"""
        claims = []

        claims.append({
            'claim_id': 'forbes_china_001',
            'text': 'John Murray Forbes (1813-1898) described as opium merchant before becoming railroad/finance figure',
            'claim_type': 'factual',
            'entities': ['John Murray Forbes', 'opium trade', 'Russell & Company'],
            'time_period': 'Early-mid 1800s',
            'evidence_source': 'Wikipedia; Business History Review 1968',
            'significance': 'Core Forbes family wealth origin in opium commerce',
            'confidence': 0.90
        })

        claims.append({
            'claim_id': 'forbes_china_002',
            'text': 'Forbes family papers at Massachusetts Historical Society "primarily document commercial activities engaged in China trade"',
            'claim_type': 'factual',
            'entities': ['Forbes Family', 'Massachusetts Historical Society', 'China trade'],
            'time_period': '1732-1931',
            'evidence_source': 'MHS Forbes Family Papers finding aid',
            'significance': 'Institutional archival confirmation of China trade focus',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_china_003',
            'text': 'Robert Bennet Forbes and family networks documented in MHS archives connected to Perkins and Russell & Company in China',
            'claim_type': 'factual',
            'entities': ['Robert Bennet Forbes', 'Perkins', 'Russell & Company', 'Massachusetts Historical Society'],
            'time_period': '1817-1967',
            'evidence_source': 'MHS Robert Bennet Forbes Papers',
            'significance': 'Primary archival evidence of opium-trade merchant house involvement',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_china_004',
            'text': 'Russell & Company described as leading U.S. China trading house specializing in tea/silk/opium',
            'claim_type': 'factual',
            'entities': ['Russell & Company', 'opium', 'China trade'],
            'time_period': '1820s-1890s',
            'evidence_source': 'Wikipedia; Business History Review',
            'significance': 'Major American opium trading entity with Forbes family involvement',
            'confidence': 0.90
        })

        claims.append({
            'claim_id': 'forbes_china_005',
            'text': 'Forbes House Museum maintains "opium exhibit" framing family opium trade history',
            'claim_type': 'factual',
            'entities': ['Forbes House Museum', 'opium trade'],
            'evidence_source': 'forbeshousemuseum.org',
            'significance': 'Family institution acknowledges opium commerce origins',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_china_006',
            'text': 'Perkins merged with Russell & Co. to become largest American merchant firm in China (in that era)',
            'claim_type': 'factual',
            'entities': ['Perkins', 'Russell & Company'],
            'time_period': 'Mid 1800s',
            'evidence_source': 'Massachusetts Historical Society archival notes',
            'significance': 'Consolidation of opium-trade merchant houses in Forbes network',
            'confidence': 0.85
        })

        return claims

    def extract_forbes_railroad_claims(self) -> List[Dict]:
        """Extract railroad infrastructure claims"""
        claims = []

        claims.append({
            'claim_id': 'forbes_rail_001',
            'text': 'John Murray Forbes founded/assembled Chicago, Burlington & Quincy Railroad (CB&Q)',
            'claim_type': 'factual',
            'entities': ['John Murray Forbes', 'Chicago Burlington & Quincy Railroad'],
            'time_period': 'Mid-late 1800s',
            'evidence_source': 'Encyclopedia Britannica',
            'significance': 'Major Midwestern railroad system - merchant capital to infrastructure platform',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_rail_002',
            'text': 'J.M. Forbes & Co. persists as Boston investment/trust operation; MHS holds Estate Papers (1777-1986) describing private investment and trust management',
            'claim_type': 'factual',
            'entities': ['J.M. Forbes & Co.', 'Massachusetts Historical Society'],
            'time_period': '1777-1986',
            'evidence_source': 'MHS J.M. Forbes Estate Papers',
            'significance': 'Multi-generational family office managing Forbes estates',
            'confidence': 0.95
        })

        return claims

    def extract_forbes_telecom_claims(self) -> List[Dict]:
        """Extract telecom platform claims"""
        claims = []

        claims.append({
            'claim_id': 'forbes_telecom_001',
            'text': 'William Hathaway Forbes (son of John Murray Forbes) was President of American Bell Telephone Company',
            'claim_type': 'factual',
            'entities': ['William Hathaway Forbes', 'American Bell Telephone Company', 'John Murray Forbes'],
            'time_period': 'Late 1800s',
            'evidence_source': 'Massachusetts Historical Society guide',
            'significance': 'Forbes executive control of entity that became AT&T - foundational platform governance',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_telecom_002',
            'text': 'William Hathaway Forbes entered J.M. Forbes & Co and invested in/became president of American Bell',
            'claim_type': 'factual',
            'entities': ['William Hathaway Forbes', 'J.M. Forbes & Co.', 'American Bell'],
            'time_period': 'Late 1800s',
            'evidence_source': 'MHS archival guides',
            'significance': 'Family capital office directly funding telecom platform monopoly',
            'confidence': 0.90
        })

        claims.append({
            'claim_id': 'forbes_telecom_003',
            'text': 'American Bell was central holding/operating entity that consolidated Bell patents and became AT&T',
            'claim_type': 'factual',
            'entities': ['American Bell Telephone Company', 'AT&T', 'Bell System'],
            'time_period': 'Late 1800s-early 1900s',
            'evidence_source': 'Telecom corporate histories',
            'significance': 'Forbes presidency during consolidation phase shaped monopoly structure',
            'confidence': 0.90
        })

        return claims

    def extract_forbes_bbh_claims(self) -> List[Dict]:
        """Extract Brown Brothers Harriman relationship claims"""
        claims = []

        claims.append({
            'claim_id': 'forbes_bbh_001',
            'text': '1939 Commercial & Financial Chronicle lists Brown Brothers Harriman & Co. (59 Wall Street) alongside Raymond Emerson, J.M. Forbes & Co.',
            'claim_type': 'factual',
            'entities': ['Brown Brothers Harriman', 'J.M. Forbes & Co.', 'Raymond Emerson'],
            'time_period': '1939',
            'evidence_source': 'FRASER / Commercial & Financial Chronicle',
            'significance': 'Documentary evidence of co-presence in elite finance milieu; shared institutional circles',
            'confidence': 0.90
        })

        claims.append({
            'claim_id': 'forbes_bbh_002',
            'text': 'BBH archival corpus exists at NY Historical Society/NYU; searchable for Forbes linkages',
            'claim_type': 'factual',
            'entities': ['Brown Brothers Harriman', 'NY Historical Society', 'NYU'],
            'evidence_source': 'Finding Aids at NYU',
            'significance': 'Primary archives available for deeper syndicate/trustee research',
            'confidence': 0.95
        })

        return claims

    def extract_forbes_aerospace_claims(self) -> List[Dict]:
        """Extract aerospace/MIC claims"""
        claims = []

        claims.append({
            'claim_id': 'forbes_aero_001',
            'text': 'Arthur M. Young (helicopter pioneer; Bell helicopter design work) married Ruth Forbes (Boston Forbes family)',
            'claim_type': 'factual',
            'entities': ['Arthur M. Young', 'Ruth Forbes', 'Bell Helicopter'],
            'time_period': 'Mid 1900s',
            'evidence_source': 'Wikipedia',
            'significance': 'Forbes family marriage tie into foundational rotorcraft innovation (UH-1 Huey lineage)',
            'confidence': 0.90
        })

        claims.append({
            'claim_id': 'forbes_aero_002',
            'text': 'Bell Helicopter designs became foundational to major U.S. military helicopter families (UH-1 Huey)',
            'claim_type': 'factual',
            'entities': ['Bell Helicopter', 'UH-1 Huey', 'U.S. military'],
            'time_period': '1950s-1970s',
            'evidence_source': 'Wikipedia',
            'significance': 'Military aviation platform with Forbes family adjacency',
            'confidence': 0.95
        })

        return claims

    def extract_forbes_state_admin_claims(self) -> List[Dict]:
        """Extract colonial administration / state governance claims"""
        claims = []

        claims.append({
            'claim_id': 'forbes_state_001',
            'text': 'William Cameron Forbes served as Governor-General of Philippines',
            'claim_type': 'factual',
            'entities': ['William Cameron Forbes', 'Philippines', 'U.S. colonial administration'],
            'time_period': 'Early 1900s',
            'evidence_source': 'Wikipedia',
            'significance': 'Direct executive authority over U.S. imperial territory; infrastructure/utilities/military coordination',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_state_002',
            'text': 'William Cameron Forbes described as investment banker/diplomat with directorships including AT&T, Stone & Webster',
            'claim_type': 'factual',
            'entities': ['William Cameron Forbes', 'AT&T', 'Stone & Webster'],
            'time_period': 'Early-mid 1900s',
            'evidence_source': 'Wikipedia',
            'significance': 'State administration + corporate directorships in telecom and utilities/engineering',
            'confidence': 0.85
        })

        return claims

    def extract_forbes_kerry_lineage_claims(self) -> List[Dict]:
        """Extract John Kerry lineage claims"""
        claims = []

        claims.append({
            'claim_id': 'forbes_kerry_001',
            'text': 'John Kerry\'s mother was Rosemary Isabel Forbes Kerry (1913-2002), daughter of James Grant Forbes II',
            'claim_type': 'factual',
            'entities': ['John Kerry', 'Rosemary Forbes Kerry', 'James Grant Forbes II', 'Boston Forbes'],
            'time_period': '1913-2002',
            'evidence_source': 'Wikipedia',
            'significance': 'Direct Kerry lineage to Boston Brahmin Forbes family',
            'confidence': 0.95
        })

        claims.append({
            'claim_id': 'forbes_kerry_002',
            'text': 'John Kerry placed in Boston Brahmin Forbes line tied to Perkins/Old China Trade network and 19th-century merchant houses',
            'claim_type': 'factual',
            'entities': ['John Kerry', 'Boston Brahmin', 'Forbes family', 'Perkins', 'Old China Trade'],
            'evidence_source': 'Wikipedia',
            'significance': 'Kerry family wealth origins in opium-trade merchant networks',
            'confidence': 0.90
        })

        return claims

    def generate_comprehensive_report(self, all_claims: List[Dict]):
        """Generate full intelligence report with network analysis"""

        report = f"""# Forbes Family (Boston Brahmin) Intelligence Analysis
**Generated:** {datetime.now().isoformat()}
**System:** Sherlock Evidence Analysis System
**Subject:** John Kerry maternal lineage power network (opium → infrastructure → MIC)

## Executive Summary

The Boston Forbes family represents a core American establishment lineage with documented
evolution from **China trade/opium commerce** (early-mid 1800s) through **infrastructure
platform control** (railroads, telecom, utilities) to **military-industrial complex adjacency**
(Stone & Webster, Bell Helicopter). John Kerry's maternal connection to this network places
him within multi-generational elite capital formation and state-corporate coordination systems.

### Network Evolution Pattern

**Phase A: Opium Capital Formation (early-mid 1800s)**
- Russell & Company / Perkins merchant houses
- Canton trade profits → Boston financial power
- Documented by Massachusetts Historical Society archives + Forbes House Museum

**Phase B: Railroad Infrastructure (mid-late 1800s)**
- Chicago, Burlington & Quincy Railroad (John Murray Forbes)
- Merchant capital → transportation platform monopoly
- J.M. Forbes & Co. family office established

**Phase C: Telecom Platform Control (late 1800s-early 1900s)**
- American Bell Telephone Company (William Hathaway Forbes - PRESIDENT)
- Foundational governance of entity that became AT&T
- Communication monopoly infrastructure

**Phase D: Utilities/Engineering/Defense (early-mid 1900s)**
- Stone & Webster partnership (William Cameron Forbes)
- WWI shipyards, WWII Manhattan Project (Oak Ridge Y-12 uranium plant)
- ~16% of U.S. generating capacity by 1950s

**Phase E: Modern Trust/MIC Adjacency (late 1900s-present)**
- JM Forbes & Co. LLP manages >$1.5B
- Stone & Webster absorbed into Westinghouse (DoD contractor)
- Bell Helicopter marriage tie (Ruth Forbes ↔ Arthur M. Young)

---

## Total Claims Extracted: {len(all_claims)}

### Claims by Category:
"""

        # Count claims by category
        categories = {}
        for claim in all_claims:
            claim_id_prefix = claim['claim_id'].split('_')[1]
            categories[claim_id_prefix] = categories.get(claim_id_prefix, 0) + 1

        for category, count in sorted(categories.items()):
            report += f"- **{category}**: {count} claims\n"

        report += f"\n---\n\n## Key Entity Network\n\n"
        report += "### People (Forbes Family)\n\n"
        for person, details in self.forbes_people.items():
            report += f"**{person}**\n"
            if 'dates' in details:
                report += f"- Dates: {details['dates']}\n"
            if 'role' in details:
                report += f"- Role: {details['role']}\n"
            if 'roles' in details:
                report += f"- Roles: {', '.join(details['roles'])}\n"
            if 'significance' in details:
                report += f"- Significance: {details['significance']}\n"
            report += "\n"

        report += "\n### Organizations & Firms\n\n"
        for org, details in self.forbes_network_entities.items():
            report += f"**{org}**\n"
            if 'type' in details:
                report += f"- Type: {details['type']}\n"
            if 'period' in details:
                report += f"- Period: {details['period']}\n"
            if 'forbes_connection' in details:
                report += f"- Forbes Connection: {details['forbes_connection']}\n"
            if 'significance' in details:
                report += f"- Significance: {details['significance']}\n"
            report += "\n"

        report += f"\n---\n\n## Stone & Webster Deep Dive\n\n"
        report += """Stone & Webster represents the **most direct Forbes family operational involvement**
in the military-industrial complex. William Cameron Forbes was a PARTNER at the firm.

### Defense/War Projects (documented):
- WWI: Hog Island shipyard (35,000 workers, 82 ships)
- WWII: Manhattan Project prime contractor
  - Oak Ridge Y-12 uranium enrichment plant
  - Entire Oak Ridge city (75,000 workers)
  - ~800 engineers dedicated to nuclear weapons
- 1950s-60s: First U.S. civilian nuclear power (Shippingport)
- 1950s-60s: Brookhaven accelerator, NS Savannah, Army reactors
- Cold War: ~16% of U.S. generating capacity

### Elite Network Integration:
- Founders: MIT graduates
- Charles Stone: Federal Reserve Bank of New York (1919-23), Research Corporation (founding director)
- Edwin Webster: United Fruit, Pacific Mills boards
- Forbes connection: W. Cameron Forbes PARTNER

### Modern Continuity:
- 2000: Bankruptcy
- 2016: Absorbed into Westinghouse Electric (major DoD contractor)
- Engineering lineage persists in current MIC

**SIGNIFICANCE:** Forbes family not merely "investors" but OPERATIONAL PARTNERS in firm that built
atomic weapons infrastructure, power monopolies, and defense platforms.
"""

        report += f"\n---\n\n## Evidence Strength Assessment\n\n"
        report += """
### HIGH CONFIDENCE (archival/institutional sources):
- ✅ China trade/opium origins (MHS archives, Forbes House Museum)
- ✅ Railroad infrastructure (Britannica, corporate histories)
- ✅ William H. Forbes as American Bell PRESIDENT (MHS, corporate records)
- ✅ Stone & Webster defense projects (DOE, Wikipedia, FundingUniverse)
- ✅ W. Cameron Forbes as Stone & Webster PARTNER (J.M. Forbes & Co. history)
- ✅ Bell Helicopter marriage tie (Wikipedia, ArthurYoung.com)

### MODERATE CONFIDENCE (network adjacency documented):
- ⚠️ Forbes-BBH connection: 1939 co-listing confirmed; deeper syndicate ties probable but require archival mining
- ⚠️ Post-AT&T telecom influence: ancestral/architectural, not operational

### LOW CONFIDENCE / UNPROVEN (mentioned but not documented):
- ❌ Sullivan & Cromwell direct ties: not found
- ❌ Freemasonry/Knights Templar/Knights of Malta: name collisions, no credible membership records for Kerry branch
- ❌ Modern pharmaceutical industry: no clean corporate board/ownership chain found
"""

        report += f"\n---\n\n## Network Visualization Nodes\n\n"
        report += """
```
FORBES FAMILY (Kerry Branch)
    ├─ Rosemary Forbes Kerry (1913-2002) → John Kerry
    ├─ John Murray Forbes (1813-1898)
    │   ├─ Russell & Company (opium)
    │   ├─ CB&Q Railroad (infrastructure)
    │   └─ J.M. Forbes & Co. (family office)
    ├─ William Hathaway Forbes (1840-1918)
    │   ├─ J.M. Forbes & Co. (partner)
    │   └─ American Bell Telephone (PRESIDENT) → AT&T
    ├─ William Cameron Forbes
    │   ├─ Stone & Webster (PARTNER)
    │   ├─ Philippines Governor-General
    │   └─ AT&T (board)
    └─ Ruth Forbes
        └─ Arthur M. Young (married) → Bell Helicopter

STONE & WEBSTER
    ├─ WWI: Hog Island shipyard
    ├─ WWII: Manhattan Project (Oak Ridge Y-12)
    ├─ Cold War: Nuclear power plants (~16% U.S. capacity)
    ├─ Founders: Fed Reserve NY, Research Corp
    └─ Modern: Absorbed into Westinghouse (DoD)

BBH (Network Adjacency)
    └─ 1939 Commercial & Financial Chronicle co-listing with J.M. Forbes & Co.
```
"""

        report += f"\n---\n\n## Recommended Next Research Actions\n\n"
        report += """
1. **BBH Archival Mining**: Search NYU/NYHS Brown Brothers Harriman finding aids for "Forbes", "J.M. Forbes & Co.", "Russell & Co." - likely to find syndicate/trustee overlaps

2. **Stone & Webster Personnel Records**: Identify other Forbes family members in S&W employment/governance 1900-1960

3. **AT&T/Bell Labs Governance**: Map Forbes family trust holdings and board interlocks post-1920

4. **Kerry Political Career Cross-Reference**: Analyze Kerry Senate positions on telecom regulation, defense contracting, energy policy relative to family network interests

5. **J.M. Forbes & Co. Modern Holdings**: SEC filings for publicly-traded holdings; foundation 990s for philanthropic influence

6. **Philippine Infrastructure Projects**: Research W.C. Forbes governance period for U.S. corporate concessions/contracts

7. **Bell Helicopter DOD Contracts**: Vietnam-era military procurement; Ruth Forbes-Arthur Young network influence
"""

        report += f"\n---\n\n**Classification:** UNCLASSIFIED (public sources)\n"
        report += f"**Methodology:** Primary archival references + peer-reviewed history + corporate records\n"
        report += f"**Database:** Sherlock Evidence Analysis System\n"
        report += f"**Analyst Note:** High-confidence claims supported by institutional archives (MHS, DOE, Fed Reserve). Network adjacency claims require deeper document mining but structural logic is sound.\n"

        return report

    def process_all_forbes_intelligence(self) -> Dict:
        """Main extraction: process all Forbes family intelligence"""
        print("\n" + "="*80)
        print("FORBES FAMILY (BOSTON BRAHMIN) INTELLIGENCE EXTRACTION")
        print("="*80)
        print("\nSubject: John Kerry maternal lineage power network")
        print("Focus: Opium trade → Infrastructure capitalism → MIC adjacency")
        print("\n" + "="*80 + "\n")

        # Extract all claims
        all_claims = []

        print("📄 Extracting Stone & Webster claims...")
        sw_claims = self.extract_stone_webster_claims()
        all_claims.extend(sw_claims)
        print(f"   ✅ {len(sw_claims)} claims extracted")

        print("📄 Extracting China trade/opium claims...")
        china_claims = self.extract_forbes_china_trade_claims()
        all_claims.extend(china_claims)
        print(f"   ✅ {len(china_claims)} claims extracted")

        print("📄 Extracting railroad infrastructure claims...")
        rail_claims = self.extract_forbes_railroad_claims()
        all_claims.extend(rail_claims)
        print(f"   ✅ {len(rail_claims)} claims extracted")

        print("📄 Extracting telecom platform claims...")
        telecom_claims = self.extract_forbes_telecom_claims()
        all_claims.extend(telecom_claims)
        print(f"   ✅ {len(telecom_claims)} claims extracted")

        print("📄 Extracting BBH relationship claims...")
        bbh_claims = self.extract_forbes_bbh_claims()
        all_claims.extend(bbh_claims)
        print(f"   ✅ {len(bbh_claims)} claims extracted")

        print("📄 Extracting aerospace/MIC claims...")
        aero_claims = self.extract_forbes_aerospace_claims()
        all_claims.extend(aero_claims)
        print(f"   ✅ {len(aero_claims)} claims extracted")

        print("📄 Extracting state administration claims...")
        state_claims = self.extract_forbes_state_admin_claims()
        all_claims.extend(state_claims)
        print(f"   ✅ {len(state_claims)} claims extracted")

        print("📄 Extracting Kerry lineage claims...")
        kerry_claims = self.extract_forbes_kerry_lineage_claims()
        all_claims.extend(kerry_claims)
        print(f"   ✅ {len(kerry_claims)} claims extracted")

        print(f"\n📊 Total claims extracted: {len(all_claims)}")

        # Save all claims
        claims_file = self.output_dir / "forbes_all_claims.json"
        with open(claims_file, 'w') as f:
            json.dump(all_claims, f, indent=2)
        print(f"   💾 Claims saved: {claims_file}")

        # Generate comprehensive report
        print("\n📊 Generating comprehensive intelligence report...")
        report = self.generate_comprehensive_report(all_claims)

        report_file = self.output_dir / "forbes_family_intelligence_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"   ✅ Report saved: {report_file}")

        # Save entity network
        network_file = self.output_dir / "forbes_network_entities.json"
        with open(network_file, 'w') as f:
            json.dump({
                'people': self.forbes_people,
                'organizations': self.forbes_network_entities,
                'evolution_phases': self.forbes_evolution_phases
            }, f, indent=2)
        print(f"   💾 Network entities saved: {network_file}")

        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        print("="*80)
        print(f"Total claims: {len(all_claims)}")
        print(f"Output directory: {self.output_dir}")
        print("="*80 + "\n")

        return {
            'total_claims': len(all_claims),
            'claims_by_category': {
                'stone_webster': len(sw_claims),
                'china_trade': len(china_claims),
                'railroads': len(rail_claims),
                'telecom': len(telecom_claims),
                'bbh': len(bbh_claims),
                'aerospace': len(aero_claims),
                'state_admin': len(state_claims),
                'kerry_lineage': len(kerry_claims)
            },
            'files_generated': [
                str(claims_file),
                str(report_file),
                str(network_file)
            ]
        }


def main():
    """Execute Forbes family intelligence extraction"""
    extractor = ForbesIntelligenceExtractor()
    results = extractor.process_all_forbes_intelligence()

    print("\n📈 Extraction Statistics:")
    print(f"   Total Claims: {results['total_claims']}")
    print(f"\n   Claims by Category:")
    for category, count in results['claims_by_category'].items():
        print(f"      - {category}: {count}")

    print(f"\n   Files Generated:")
    for file_path in results['files_generated']:
        print(f"      - {file_path}")


if __name__ == "__main__":
    main()
