#!/usr/bin/env python3
"""Ingest Edward J. DeBartolo Sr. intelligence reports into sherlock.db.

Registers 1 evidence source (DEBARTOLO_DYNASTY_001), extracts ~40 claims
across all 6 phases of the DeBartolo Campaign (PKG-EP Phase 5 — Campaign B),
and creates ~12 cross-references connecting DeBartolo findings to existing targets.

Key finding: $1.7B DeBartolo-Wexner joint venture (Carter-Hawley-Hale 1984/1986)
confirmed as documented business partnership. Gladio hypothesis assessed at 0.05
(E3 only) — operator hypothesis NOT supported by available evidence.
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

# Single source for the entire DeBartolo Campaign
SOURCE = {
    "source_id": "DEBARTOLO_DYNASTY_001",
    "title": "DeBartolo Dynasty Intelligence Report (PKG-EP Phase 5, Campaign B)",
    "file_path": "evidence/debartolo_intelligence_report.md",
    "evidence_type": "intelligence_report",
}

# =============================================================================
# CLAIMS — 40 claims across 6 phases (DEB-001 to DEB-040)
# Each: (claim_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    # =========================================================================
    # PHASE 1: Empire & Background (DEB-001 to DEB-006)
    # =========================================================================
    ("DEB-001", "factual",
     "Edward J. DeBartolo Sr. born May 17, 1909, Youngstown, Ohio as Edward John Paonessa. His stepfather Michael DeBartolo (Italian immigrant from Terlizzi, Apulia) gave him the DeBartolo surname. Graduated Notre Dame (engineering). Began strip mall development ~1948 with Belmont Plaza, then Boardman Plaza (1951).",
     0.90, '["E1", "E2", "background", "debartolo", "youngstown", "PKG-EP"]'),

    ("DEB-002", "factual",
     "DeBartolo Corp. became America's largest shopping mall developer: 200+ retail properties (100+ regional malls + 100+ community centers) at peak; ~$700M annual revenue; ~10% of US mall space; ~15,000 employees. Incorporated formally 1962. Built an average of 5 malls/year through the 1960s-1970s. Nation's largest regional mall: Randall Park Mall near Cleveland (1976, 2.2 million sq ft, 'world's largest' at opening).",
     0.95, '["E1", "E2", "debartolo", "mall_empire", "PKG-EP"]'),

    ("DEB-003", "factual",
     "DeBartolo's sports holdings: San Francisco 49ers (NFL) — DeBartolo Jr. became principal owner 1977; five Super Bowl wins under Walsh/Montana era. Pittsburgh Penguins (NHL) — acquired February 1977 by DeBartolo Sr.; sold 1991. DeBartolo Jr. convicted of $400K bribe to Louisiana Governor Edwin Edwards (guilty plea 1999); Trump presidential pardon February 18, 2020.",
     0.95, '["E1", "debartolo", "sports", "NFL", "NHL", "trump_pardon", "PKG-EP"]'),

    ("DEB-004", "factual",
     "DeBartolo Sr. and Les Wexner jointly bid $1.7 billion for Carter Hawley Hale Stores (LA-based retailer owning The Broadway, Neiman-Marcus, Bergdorf Goodman, Emporium, Contempo Casuals) in 1984 and again in 1986. The 1986 Los Angeles Times described the bid: 'The takeover offer for Carter Hawley brings together the two richest men in Ohio.' Both bids failed. The joint venture demonstrates sustained high-level business partnership requiring mutual trust and complementary financial capability.",
     0.85, '["E2", "debartolo", "wexner", "carter_hawley", "joint_venture", "two_richest_ohio", "PKG-EP"]'),

    ("DEB-005", "factual",
     "Commercial nexus: The Limited (Wexner) was one of the most dominant retail tenants in American malls throughout the 1980s-1990s, operating thousands of storefronts under The Limited, Victoria's Secret, Lane Bryant, Lerner, Express, and A&F brands. DeBartolo was the nation's largest mall developer in the same period. The Limited stores were almost certainly tenants in DeBartolo malls, constituting the foundational commercial relationship enabling the Carter-Hawley-Hale partnership.",
     0.80, '["E2", "debartolo", "wexner", "commercial_nexus", "mall_retail", "PKG-EP"]'),

    ("DEB-006", "factual",
     "DeBartolo built significant mall portfolio across Ohio and nationally: Summit Mall (Akron, 1966); Randall Park Mall (N. Randall, Cleveland area, 1976); multiple Youngstown-area properties; eventually 59 regional shopping malls nationwide plus 100+ community/strip centers. By early 1990s, over one-third of portfolio concentrated in Florida — overlapping geographically with Trafficante's Tampa territory.",
     0.85, '["E1", "E2", "debartolo", "mall_empire", "ohio", "florida", "PKG-EP"]'),

    # =========================================================================
    # PHASE 2: Organized Crime Documentation (DEB-007 to DEB-019)
    # =========================================================================
    ("DEB-007", "factual",
     "DOJ Organized Crime Principal Subjects List (1970): DeBartolo placed on federal organized crime index as associate of Santos Trafficante Jr., Meyer Lansky, and Carlos Marcello, per 1970 DOJ memorandum. List distributed to multiple government agencies 1971. Inclusion required only appearance in investigative reports as an associate — not criminal charges. DeBartolo's attorney (Charles Ruff) challenged the listing when seeking Oklahoma racetrack license; listing was not removed; license was granted.",
     0.85, '["E2", "debartolo", "DOJ_OC_list", "trafficante", "lansky", "marcello", "PKG-EP"]'),

    ("DEB-008", "factual",
     "Pennsylvania Crime Commission characterized DeBartolo as 'associate of the Genovese-LaRocca crime family in Pittsburgh.' This characterization appears in the 1991 Columbus Police Department Shapiro Homicide Investigation report, which drew on Pennsylvania Crime Commission findings. The Pittsburgh crime family (LaRocca family) maintained cooperative relationships with the Genovese family of New York and controlled organized crime in the Youngstown area — DeBartolo's home territory.",
     0.80, '["E2", "debartolo", "pennsylvania_crime_commission", "genovese_larocca", "youngstown", "PKG-EP"]'),

    ("DEB-009", "factual",
     "US Customs Special Agent William F. Burda generated intelligence reports on DeBartolo (January 1981 primary report). Key allegations: DeBartolo organization 'through its control of particular state banks in the state of Florida is operating money-laundering schemes, realizing huge profits from narcotics, guns, skimming operations, and other organized-crime-related activities.' Named connections: Trafficante, Lansky, Marcello. An earlier Burda report described Lansky as 'almost senile and getting out of the business' — implying DeBartolo was positioned as a financial successor.",
     0.70, '["E2", "debartolo", "customs_burda", "money_laundering", "lansky_successor", "trafficante", "PKG-EP"]'),

    ("DEB-010", "factual",
     "Metropolitan Bank of Tampa: DeBartolo Sr. acquired majority stake (227,000 shares) in 1975. So dominant his control that he unilaterally forced the bank president's resignation in 1981. Operated through WFC Corporation / Grand Cayman Island subsidiary. Failed February 12, 1982 — largest Florida bank failure at that time. ~40% of loan portfolio delinquent at failure. Florida comptroller investigating 'what appears to be spurious loans' through Grand Cayman chain. FDLE investigation found 'suspicious customers' but 'no evidence of narcotics laundering per se' — FDLE special agent testified: 'what we did find shocked us.'",
     0.85, '["E2", "debartolo", "metropolitan_bank", "tampa", "grand_cayman", "money_laundering", "FDLE", "PKG-EP"]'),

    ("DEB-011", "factual",
     "Ronald 'Crab' Carabbia and DeBartolo Sr.: FBI surveillance documented multiple Las Vegas trips together; Fratianno testimony confirmed DeBartolo was 'very friendly' with Ronald Carabbia — 'They used to go on junkets to the Tropicana' and DeBartolo 'was a pretty heavy gambler.' Origin: Cleveland mob firebombing campaign against DeBartolo shopping center storefronts in early 1950s; DeBartolo sought Carabbia protection. Ronald Carabbia was the Cleveland family's Youngstown representative and was convicted of murdering Danny Greene via car bomb.",
     0.80, '["E2", "debartolo", "carabbia", "cleveland_OC", "youngstown", "FBI_surveillance", "PKG-EP"]'),

    ("DEB-012", "factual",
     "Arthur Shapiro murder (March 6, 1985): Wexner's personal attorney at Schwartz Shapiro Kelm & Warren, shot twice in the head at a Columbus cemetery — one day before his scheduled grand jury testimony. Columbus Police Department Organized Crime Bureau concluded the killing bore 'strong marks of a La Cosa Nostra (L.C.N.) hit.' Berry Kessler, an accountant with criminal history, was ultimately convicted of murder-for-hire. The chain of command from Kessler to the ordering principal has not been publicly established.",
     0.90, '["E1", "E2", "debartolo", "wexner", "shapiro_murder", "LCN_hit", "grand_jury", "PKG-EP"]'),

    ("DEB-013", "factual",
     "Columbus Police Shapiro file suppression: The 1991 Columbus Police Department 'Shapiro Homicide Investigation: Analysis and Hypothesis' placed DeBartolo as a Genovese-LaRocca associate alongside Wexner and described their 'well-known history of business and investment partnerships.' Columbus Police Chief James G. Jackson ordered the document destroyed June 1991. When confronted by Channel 4 News: 'I thought I got rid of it.' Called the report 'scandalous.' Document survived; digitized; hosted at archive.org ('shapiromurderfilecomplete1').",
     0.90, '["E1", "E2", "debartolo", "wexner", "shapiro_file", "suppression", "columbus_PD", "PKG-EP"]'),

    ("DEB-014", "factual",
     "Youngstown organized crime war (1978-1981): Pittsburgh family under Vincent Prato attempted monopoly over Youngstown rackets; 12 murders over four years. Pittsburgh family won: Charlie 'The Crab' Carabbia (Cleveland) was lured to a Youngstown donut shop and murdered December 13, 1980 on orders from Prato. DeBartolo's documented relationship was with the Carabbia brothers (Cleveland side) while simultaneously owning the Pittsburgh Penguins (Pittsburgh side). He navigated both sides of the organized crime war that defined his home territory.",
     0.80, '["E2", "debartolo", "youngstown_war", "pittsburgh_family", "cleveland_family", "carabbia", "PKG-EP"]'),

    ("DEB-015", "factual",
     "FBI 1985 dossier on DeBartolo: compiled organized crime intelligence including Fratianno testimony, Las Vegas surveillance documentation, and Carabbia relationship assessment. Cited in Dan Moldea's 'Interference: How Organized Crime Influences Professional Football' (William Morrow, 1989). Moldea documented 'no fewer than twenty-six past and present NFL team owners with documented ties to either the gambling community or the organized crime syndicate.'",
     0.75, '["E2", "debartolo", "FBI_1985", "moldea", "NFL_organized_crime", "PKG-EP"]'),

    ("DEB-016", "factual",
     "James Traficant (US Representative, D-OH, Youngstown district): convicted 2002 on eight counts of bribery, racketeering, and corruption; expelled from Congress. Operated within the same Youngstown organized crime political ecosystem as DeBartolo. While no direct DeBartolo-Traficant transaction has been documented, Traficant's convictions confirm the systemic political corruption in DeBartolo's home territory.",
     0.75, '["E2", "debartolo", "traficant", "youngstown", "political_corruption", "PKG-EP"]'),

    ("DEB-017", "factual",
     "Five separate law enforcement agencies independently characterized DeBartolo as an organized crime associate: DOJ (1970), US Customs (1981), FBI (1985 dossier), Pennsylvania Crime Commission (undated), Columbus Police Department (1991). This multi-agency convergence across two decades and five institutions that do not share intelligence in real-time is the strongest available indicator of legitimate law enforcement concern rather than error by any single agency.",
     0.85, '["E2", "debartolo", "multi_agency_convergence", "organized_crime", "PKG-EP"]'),

    ("DEB-018", "factual",
     "Genovese crime family as common organizational denominator: DeBartolo characterized as 'Genovese-LaRocca associate' (Pittsburgh family's Genovese lineage). Walsh Trucking RICO case (Wexner's logistics company) implicates Fat Tony Salerno (NYC Genovese boss) as unindicted co-conspirator. The Genovese family is the common national organizational thread connecting DeBartolo's Youngstown/Pittsburgh orbit and Wexner's Columbus logistics ecosystem.",
     0.70, '["E2", "debartolo", "wexner", "genovese_family", "walsh_trucking", "salerno", "PKG-EP"]'),

    ("DEB-019", "factual",
     "DeBartolo's Louisiana operations: owned Louisiana Downs racetrack (Bossier City, LA) — in Carlos Marcello's Louisiana territory. Built New Orleans shopping centers in Marcello's territory. The pattern of DeBartolo building major commercial projects in the territory of organized crime figures listed in the DOJ 1970 memo alongside him (Marcello in Louisiana; Trafficante in Florida) is analytically significant — operating in mob territory without conflict implies either permission or active relationship.",
     0.70, '["E2", "debartolo", "marcello", "louisiana", "territory_pattern", "PKG-EP"]'),

    # =========================================================================
    # PHASE 3: CIA-Mafia Nexus Assessment (DEB-020 to DEB-025)
    # =========================================================================
    ("DEB-020", "factual",
     "Santos Trafficante Jr. confirmed CIA operational asset (E1): Church Committee (1975-1976) documented Trafficante's recruitment by CIA for Operation Mongoose anti-Castro assassination plots; met with Robert Maheu (Howard Hughes/CIA interface) and John Roselli (LA mob/CIA liaison); participated in ZR/RIFLE poison capsule plots against Castro. Trafficante's CIA connection is primary-source-confirmed at E1 — among the best-documented CIA-organized crime relationships in the public record.",
     0.99, '["E1", "trafficante", "CIA", "operation_mongoose", "church_committee", "PKG-EP"]'),

    ("DEB-021", "factual",
     "Trafficante-DeBartolo CIA inference chain: Trafficante was a CIA asset (E1) → DeBartolo was a Trafficante associate (E2) → DeBartolo may have provided financial services to CIA-Trafficante network (E3, 0.20). This inference chain requires two inferential steps with no primary source documentation at either link. Metropolitan Bank of Tampa (DeBartolo-controlled, Grand Cayman routing, Trafficante's city) is the most plausible specific mechanism but remains unsubstantiated as a CIA channel.",
     0.70, '["E3", "debartolo", "trafficante", "CIA", "inference_chain", "metropolitan_bank", "PKG-EP"]'),

    ("DEB-022", "factual",
     "DeBartolo CIA operational relationship assessed at 0.10 confidence (E3 only). No CIA operational document, FOIA file, congressional testimony, or sworn statement names DeBartolo as a CIA asset, informant, or financial resource. The structural proximity (Trafficante, Tampa bank) is real but does not constitute evidence. DeBartolo's Grand Cayman banking structure is consistent with CIA off-balance-sheet finance methodology but equally consistent with routine organized crime money laundering.",
     0.90, '["E3", "debartolo", "CIA", "NO_EVIDENCE", "assessment", "PKG-EP"]'),

    ("DEB-023", "factual",
     "DeBartolo's organized crime financial infrastructure — $700M revenue shopping malls, cash-intensive racetracks, offshore-structured Tampa bank — is architecturally consistent with a sophisticated money movement operation. Whether this infrastructure was used for organized crime financial coordination, CIA-sanctioned operations, or both cannot be determined from available evidence. The FDLE 'shocked' finding (unspecified irregularity) is the only law enforcement conclusion about actual financial conduct beyond structure.",
     0.65, '["E2", "E3", "debartolo", "financial_infrastructure", "money_movement", "PKG-EP"]'),

    ("DEB-024", "factual",
     "Youngstown as potential domestic intelligence node: Youngstown's extraordinary organized crime penetration of local government, law enforcement, and judiciary is documented at E1 (court records, convictions). The industrial corridor from Cleveland through Youngstown to Pittsburgh was simultaneously a mob-controlled territory and an area of significant CIA-organized crime interaction (Trafficante connections, Cleveland family's reported CIA contacts). Whether DeBartolo's real estate empire served any intelligence function in this context is unestablished.",
     0.50, '["E3", "debartolo", "youngstown", "intelligence_node", "PKG-EP"]'),

    ("DEB-025", "factual",
     "Metropolitan Bank of Tampa as intelligence-adjacent structure: A DeBartolo-controlled bank in Santos Trafficante's home city, operating through Grand Cayman offshore channels, during the period when Trafficante was simultaneously a known CIA asset (1960s confirmed; ongoing CIA relationship unclear after 1963) and an active organized crime boss, represents a potential financial intelligence intersection. No evidence supports this as an active CIA channel; the structure is the observation.",
     0.50, '["E3", "debartolo", "metropolitan_bank", "trafficante", "CIA_adjacent", "PKG-EP"]'),

    # =========================================================================
    # PHASE 4: Gladio Assessment (DEB-026 to DEB-030)
    # =========================================================================
    ("DEB-026", "factual",
     "Operation Gladio (Italian) confirmed at E1: NATO stay-behind networks in post-WWII Europe, documented via Italian parliamentary investigation (1990), Belgian parliamentary investigation (1991), CIA/OSS history. Italian Gladio connected to P2 masonic lodge (Gelli), strategy of tension bombings, Banco Ambrosiano (Calvi), Vatican Bank, and US intelligence oversight. Licio Gelli (P2), Roberto Calvi (Banco Ambrosiano), and Michele Sindona are the documented Gladio-organized crime-finance nexus figures.",
     0.99, '["E1", "gladio", "NATO", "P2", "italy", "PKG-EP"]'),

    ("DEB-027", "factual",
     "US domestic Gladio evidence: Belgian Parliamentary Committee found evidence of 'a more radical version' of Gladio in the US capable of 'carrying out political assassinations.' This is a single E1 data point from foreign parliamentary investigation — not a US government confirmation. No declassified US government document has confirmed a domestic Gladio-equivalent program with specified organizational structure, personnel, or operations.",
     0.70, '["E1", "gladio", "US_domestic", "belgian_parliament", "PKG-EP"]'),

    ("DEB-028", "assessment",
     "DeBartolo-Gladio hypothesis: E3 at 0.05 confidence. DeBartolo shares three structural characteristics with Italian Gladio principals: (1) documented organized crime connections; (2) offshore banking operations (Grand Cayman); (3) proximity to CIA-connected mob figures (Trafficante). He is MISSING the four characteristics required to substantiate Gladio hypothesis: (1) P2 lodge documentation; (2) CIA operational records; (3) parliamentary confirmation; (4) any documented connection to NATO stay-behind infrastructure.",
     0.90, '["E3", "debartolo", "gladio", "NEGATIVE_FINDING", "hypothesis_assessment", "PKG-EP"]'),

    ("DEB-029", "factual",
     "Documented negative findings on DeBartolo-Gladio: (1) No DeBartolo connection to P2 lodge; (2) No DeBartolo connection to strategy of tension events; (3) No DeBartolo name in any published Gladio document; (4) No connection to Gladio-linked European banks (Banco Ambrosiano, Vatican Bank); (5) No connection to documented European or American stay-behind networks; (6) No Italian law enforcement or parliamentary documentation of DeBartolo in Gladio context; (7) Gladio B (Edmonds) entirely irrelevant to DeBartolo's Youngstown/Florida operations.",
     0.95, '["E3", "debartolo", "gladio", "NEGATIVE_FINDINGS", "PKG-EP"]'),

    ("DEB-030", "assessment",
     "Operator's original hypothesis note: 'DeBartolo likely involved in US-side Operation Gladio. Plausible via: Trafficante connection (CIA-Mafia anti-Castro ops used same networks as Gladio domestic component) and Youngstown's documented organized crime hub role.' Assessment: The hypothesis was appropriately bounded by the operator's caveat that US domestic Gladio is the least documented aspect of the program. After full investigation, the evidence does not exist in the public domain to substantiate the hypothesis. Confidence: 0.05.",
     0.90, '["assessment", "debartolo", "gladio", "operator_hypothesis", "NEGATIVE_FINDING", "PKG-EP"]'),

    # =========================================================================
    # PHASE 5-6: Wexner Nexus & Synthesis (DEB-031 to DEB-040)
    # =========================================================================
    ("DEB-031", "factual",
     "DeBartolo-Wexner relationship assessment: Dual-layer relationship. Layer 1 (Commercial): $1.7B Carter-Hawley-Hale joint bid; structural commercial nexus (Limited stores in DeBartolo malls); 'two richest men in Ohio' status. Layer 2 (Organized Crime Ecosystem): Both connected to Genovese family network (DeBartolo via LaRocca-Pittsburgh; Wexner via Walsh/Salerno); both appeared in 1991 Columbus PD Shapiro file in organized crime context; Shapiro murder connecting Wexner's attorney to organized crime, with Police Chief suppression.",
     0.80, '["E2", "debartolo", "wexner", "dual_layer_relationship", "organized_crime", "PKG-EP"]'),

    ("DEB-032", "factual",
     "Shapiro murder significance: Arthur Shapiro (Wexner's attorney) was killed March 6, 1985 — one day before scheduled grand jury testimony, shot twice in the head at a Columbus cemetery. The Columbus PD OCB characterized it as an LCN hit. The two most plausible theories: (1) Wexner's organized crime associates ordered it to prevent testimony on Walsh/Salerno RICO-related matters; (2) DeBartolo's organized crime associates ordered it over Carter-Hawley-Hale financing or other joint venture issues. Neither theory is documented; both are analytically consistent with the timing and method.",
     0.65, '["E2", "E3", "debartolo", "wexner", "shapiro_murder", "theories", "PKG-EP"]'),

    ("DEB-033", "assessment",
     "Overall DeBartolo intelligence characterization: DeBartolo was a 'protected businessman' — a legitimate entrepreneur whose empire was embedded within organized crime networks that provided protection, financial services, and political facilitation across multiple decades. He was not running crime directly but was not independent of it. The multi-agency law enforcement documentation is too consistent to dismiss. Specific criminal transactions (narcotics laundering, syndicate financial coordination) remain unproven. He operated in the protected businessman model typical of major Rust Belt businessmen in mob-controlled cities.",
     0.80, '["assessment", "debartolo", "protected_businessman", "organized_crime", "PKG-EP"]'),

    ("DEB-034", "assessment",
     "'Lansky successor' claim final assessment: The characterization of DeBartolo as Lansky's successor in organized crime financial coordination is the most extraordinary claim in his file. If true, DeBartolo's $700M-revenue commercial empire was the primary vehicle for coordinating the national crime syndicate's finances post-Lansky. This claim is single-source (Customs Agent Burda, E2) and has not been independently corroborated. The claim may reflect informant intelligence exaggerating DeBartolo's role, or it may be accurate. Without primary documentation (original Burda source files), this remains E2/E3.",
     0.55, '["E2", "E3", "debartolo", "lansky_successor", "extraordinary_claim", "PKG-EP"]'),

    ("DEB-035", "factual",
     "DeBartolo's Penguins purchase (February 1977) and Carabbia relationship simultaneously: Acquiring a Pittsburgh sports team while maintaining documented relationships with the Cleveland family's Youngstown representatives — who were at war with the Pittsburgh family — places DeBartolo in a dual-organization position during the most violent period of the Youngstown organized crime war (1978-1981). This may reflect deliberate hedging, business convenience, or simply that DeBartolo's relationships predated the war and survived it.",
     0.65, '["E2", "debartolo", "pittsburgh_penguins", "carabbia", "dual_organization", "PKG-EP"]'),

    ("DEB-036", "factual",
     "Ohio political protection ecosystem: The suppression of the Shapiro file by Columbus Police Chief Jackson (1991), combined with DeBartolo's never being indicted despite five-agency law enforcement documentation, is consistent with systemic political protection of Ohio's wealthiest businessmen. Wexner's political influence (backed Celeste, Glenn, Voinovich) and DeBartolo's Youngstown political network (Traficant, Ohio state government ties) represent parallel political protection infrastructure in different Ohio political networks.",
     0.70, '["E2", "debartolo", "wexner", "political_protection", "ohio", "PKG-EP"]'),

    ("DEB-037", "factual",
     "DeBartolo's death (December 19, 1994) without indictment: After 45+ years of documented organized crime associations, multiple law enforcement investigations, and the Metropolitan Bank failure, DeBartolo Sr. died at age 85 having never been criminally charged with any organized crime offense. This outcome — consistent with the pattern of wealthy organized crime associates receiving political and legal protection — is itself analytically informative. His son Edward Jr. was convicted five years later.",
     0.90, '["E1", "debartolo", "no_indictment", "political_protection", "PKG-EP"]'),

    ("DEB-038", "assessment",
     "DeBartolo's significance to PKG-EP investigation: (1) Confirms DeBartolo-Wexner as documented business partners via $1.7B joint venture — enriches the organized crime ecosystem mapping around Wexner; (2) Genovese family as common denominator for both DeBartolo (LaRocca-Genovese) and Wexner's logistics partner (Salerno, Genovese boss); (3) Shapiro murder as organized crime context for the Wexner-DeBartolo relationship; (4) Gladio hypothesis NEGATIVE — documented at E3/0.05 — future investigators can rule out this line; (5) Metropolitan Bank Tampa remains most promising avenue for intelligence community dimension research.",
     0.80, '["assessment", "debartolo", "PKG-EP", "significance", "wexner_nexus"]'),

    ("DEB-039", "factual",
     "Carter-Hawley-Hale context: Carter Hawley Hale Stores operated The Broadway, Neiman-Marcus, Bergdorf Goodman, and Emporium. DeBartolo's interest: anchor tenant acquisition. Wexner's interest: luxury brand portfolio expansion (mirrors VS, Bendel acquisitions). Two failed bids (1984, 1986) means DeBartolo and Wexner worked together for two years in sustained joint venture planning. The $1.7B figure exceeds both men's individual net worth estimates at that time, requiring coordinated external financing arrangements.",
     0.80, '["E2", "debartolo", "wexner", "carter_hawley", "joint_financing", "PKG-EP"]'),

    ("DEB-040", "assessment",
     "Trump pardon note: DeBartolo Jr.'s presidential pardon (February 18, 2020) followed his 2016 Trump campaign support. The same date — February 18 — appears in the Wexner campaign as the date of Wexner's congressional co-conspirator deposition (February 18, 2026, six years later). The date coincidence is analytically noted but most probably coincidental given the six-year separation. DeBartolo Jr. supported Trump's 2016 campaign; the pardon is documented as both political reward and Youngstown-vote strategy.",
     0.70, '["E1", "debartolo_jr", "trump_pardon", "wexner_deposition", "date_coincidence", "PKG-EP"]'),
]

# =============================================================================
# CROSS-REFERENCES — 12 connections (xref_deb_001 to xref_deb_012)
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    ("xref_deb_001", "DEB_DeBartolo", "WEX_Wexner",
     "BUSINESS_PARTNER_OC_NEXUS",
     "DEB-004,DEB-012,DEB-013,DEB-018,DEB-031",
     0.85),

    ("xref_deb_002", "DEB_DeBartolo", "Trafficante_Tampa",
     "DOCUMENTED_ASSOCIATE_DOJ_CUSTOMS",
     "DEB-007,DEB-009,DEB-010,DEB-020,DEB-021",
     0.80),

    ("xref_deb_003", "DEB_DeBartolo", "EP_Epstein",
     "INDIRECT_VIA_WEXNER",
     "DEB-004,DEB-031",
     0.50),

    ("xref_deb_004", "DEB_DeBartolo", "Genovese_Family",
     "ASSOCIATE_LAROCCA_GENOVESE_BRANCH",
     "DEB-008,DEB-018",
     0.80),

    ("xref_deb_005", "DEB_MetroBank_Tampa", "CIA_Trafficante",
     "POTENTIAL_FINANCIAL_NEXUS",
     "DEB-010,DEB-021,DEB-025",
     0.20),

    ("xref_deb_006", "WEX_Walsh_Trucking", "DEB_DeBartolo",
     "GENOVESE_COMMON_DENOMINATOR",
     "DEB-018",
     0.70),

    ("xref_deb_007", "DEB_DeBartolo", "Shapiro_Murder",
     "ORGANIZED_CRIME_CONTEXT_JOINT_DOCUMENT",
     "DEB-012,DEB-013,DEB-032",
     0.85),

    ("xref_deb_008", "DEB_DeBartolo", "Gladio_Network",
     "NEGATIVE_FINDING_E3_ONLY",
     "DEB-028,DEB-029,DEB-030",
     0.05),

    ("xref_deb_009", "DEB_DeBartolo", "Columbus_PD",
     "SUPPRESSED_DOCUMENT_ORGANIZED_CRIME_NEXUS",
     "DEB-013",
     0.90),

    ("xref_deb_010", "DEB_DeBartolo", "Carabbia_Cleveland",
     "FBI_DOCUMENTED_SOCIAL_RELATIONSHIP",
     "DEB-011,DEB-014",
     0.85),

    ("xref_deb_011", "DEB_DeBartolo_Jr", "Trump_Network",
     "PARDON_2020_POLITICAL_RELATIONSHIP",
     "DEB-003,DEB-040",
     0.90),

    ("xref_deb_012", "DEB_DeBartolo", "BCCI_Parallel",
     "STRUCTURAL_PARALLEL_OFFSHORE_OC_FINANCE",
     "DEB-010,DEB-023",
     0.30),
]


# =============================================================================
# EXECUTION
# =============================================================================

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    sources_added = 0
    claims_added = 0
    claims_skipped = 0
    xrefs_added = 0
    xrefs_skipped = 0

    # ---- Insert source ----
    c.execute("SELECT source_id FROM evidence_sources WHERE source_id = ?",
              (SOURCE["source_id"],))
    if not c.fetchone():
        c.execute("""
            INSERT INTO evidence_sources
                (source_id, title, file_path, evidence_type, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            SOURCE["source_id"],
            SOURCE["title"],
            SOURCE["file_path"],
            SOURCE["evidence_type"],
            json.dumps({
                "campaign": "PKG-EP Phase 5 Campaign B",
                "target_id": 58,
                "target_name": "Edward J. DeBartolo Sr.",
                "phases": ["D1_empire", "D2_crime", "D3_CIA_mafia", "D4_gladio", "D5_wexner", "D6_synthesis"],
                "total_claims": 40,
                "total_xrefs": 12,
                "key_finding": "1.7B Carter-Hawley-Hale joint venture confirms DeBartolo-Wexner business partnership (E2)",
                "gladio_hypothesis": "NEGATIVE - 0.05 confidence (E3 only)",
                "CIA_hypothesis": "INDETERMINATE - 0.10 confidence",
                "evidence_distribution": {"E1": "10%", "E2": "60%", "E3": "25%", "UNVERIFIED": "5%"},
            }),
            now
        ))
        sources_added += 1
        print(f"Added source: {SOURCE['source_id']} -- {SOURCE['title']}")

    # ---- Insert claims ----
    for claim_id, claim_type, text, confidence, tags in CLAIMS:
        c.execute("SELECT claim_id FROM evidence_claims WHERE claim_id = ?",
                  (claim_id,))
        if c.fetchone():
            print(f"  SKIP claim {claim_id}: already exists")
            claims_skipped += 1
            continue

        c.execute("""
            INSERT INTO evidence_claims
                (claim_id, source_id, claim_type, text, confidence, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, SOURCE["source_id"], claim_type, text, confidence, tags, now))
        claims_added += 1

    print(f"  Claims added: {claims_added} | skipped: {claims_skipped}")

    # ---- Insert cross-references ----
    for xref_id, entity1, entity2, rel_type, source_claims, confidence in CROSS_REFS:
        c.execute("SELECT xref_id FROM cross_references WHERE xref_id = ?",
                  (xref_id,))
        if c.fetchone():
            print(f"  SKIP xref {xref_id}: already exists")
            xrefs_skipped += 1
            continue

        c.execute("""
            INSERT INTO cross_references
                (xref_id, entity1, entity2, relationship_type, source_claims, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (xref_id, entity1, entity2, rel_type, source_claims, confidence, now))
        xrefs_added += 1

    conn.commit()

    # ---- Verification summary ----
    c.execute("SELECT COUNT(*) FROM evidence_sources")
    total_sources = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM evidence_claims")
    total_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references")
    total_xrefs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM evidence_claims WHERE claim_id LIKE 'DEB-%'")
    deb_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references WHERE xref_id LIKE 'xref_deb_%'")
    deb_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"DEBARTOLO CAMPAIGN INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Sources added this run:  {sources_added}")
    print(f"  Claims added this run:   {claims_added}")
    print(f"  Claims skipped (dupes):  {claims_skipped}")
    print(f"  Xrefs added this run:    {xrefs_added}")
    print(f"  Xrefs skipped (dupes):   {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  DEBARTOLO CAMPAIGN TOTALS:")
    print(f"    DEB-* claims in DB:    {deb_claims}")
    print(f"    xref_deb_* in DB:      {deb_xrefs}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total sources:         {total_sources}")
    print(f"    Total claims:          {total_claims}")
    print(f"    Total cross-refs:      {total_xrefs}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
