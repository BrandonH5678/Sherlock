#!/usr/bin/env python3
"""Ingest Phase 2 intelligence reports into sherlock.db.

Registers 9 evidence sources (EP_007_Q1-Q5, EP_008_Q1-Q4),
extracts key claims, and creates cross-references.
"""
import sqlite3
import json
import re
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

# Phase 2 report definitions
REPORTS = [
    {
        "source_id": "EP_007_Q1",
        "title": "Whitney Webb Top 20 Epstein-Intelligence Claims (PKG-EP Phase 2)",
        "file_path": "evidence/whitney_webb_Q1_top_claims.md",
        "evidence_type": "intelligence_report",
        "claim_prefix": "WW1",
        "claims": [
            ("WW1-001", "factual", "Whitney Webb claims Jeffrey Epstein's operation represents a continuation of sexual blackmail networks traced through Roy Cohn, Craig Spence, and earlier intelligence-linked operations dating to the 1950s.", 0.45, '["E2", "E3", "intelligence_operations", "PKG-EP"]'),
            ("WW1-002", "factual", "Webb documents Robert Maxwell's confirmed role as an Israeli intelligence asset, citing Gordon Thomas sworn affidavit, FBI FOIA files on 'Maxwell PROMIS Sales', and six intelligence chiefs attending his funeral.", 0.75, '["E1", "E2", "intelligence_connections", "PKG-EP"]'),
            ("WW1-003", "factual", "Webb documents the PROMIS software theft by DOJ (confirmed by two federal courts and 1992 House Judiciary Committee) and its distribution through Maxwell/Degem Computers for Israeli intelligence.", 0.80, '["E1", "intelligence_operations", "PKG-EP"]'),
            ("WW1-004", "factual", "Webb documents Alexander Acosta's reported statement that Epstein 'belonged to intelligence' and was told to back off prosecution. Single sourced to Vicky Ward; Acosta denied under oath.", 0.55, '["E2", "intelligence_connections", "PKG-EP"]'),
            ("WW1-005", "factual", "Webb documents Epstein's fake Austrian passport (name 'Marius Fortelni', Saudi residence) found in 2019 raid. E1 evidence from SDNY court filings.", 0.95, '["E1", "intelligence_tradecraft", "PKG-EP"]'),
            ("WW1-006", "factual", "Webb documents Ehud Barak's 30+ visits to Epstein and DOJ emails showing Israeli government secured Manhattan apartment for Barak with Israeli security controlling access.", 0.90, '["E1", "intelligence_connections", "israel", "PKG-EP"]'),
            ("WW1-007", "factual", "Webb documents Leslie Wexner's unprecedented power of attorney to Epstein over his finances, granting control of $46M Manhattan mansion and substantial assets with no clear business justification.", 0.85, '["E1", "financial_architecture", "PKG-EP"]'),
            ("WW1-008", "factual", "Webb documents Mega Group (Wexner/Bronfman) as alleged intelligence-linked fundraising network. Formation documented; intelligence connection relies on inference and contested sources.", 0.35, '["E2", "E3", "intelligence_front", "PKG-EP"]'),
            ("WW1-009", "factual", "Webb documents BCCI as CIA banking infrastructure per Kerry-Brown Senate Report, and argues Epstein's financial architecture followed similar patterns.", 0.60, '["E1", "E3", "intelligence_banking", "PKG-EP"]'),
            ("WW1-010", "factual", "Webb documents Deutsche Bank processed 40+ Epstein accounts post-conviction ($150M fine) and JPMorgan processed $1B+ (Judge Rakoff: 'knew or should have known', $365M settlement).", 0.95, '["E1", "institutional_enablement", "PKG-EP"]'),
            ("WW1-011", "factual", "Webb documents Epstein's science network including Harvard PED ($6.5M), MIT Media Lab ($1.7M via Joi Ito), Edge Foundation (Brockman), with funding continuing post-conviction.", 0.90, '["E1", "science_network", "PKG-EP"]'),
            ("WW1-012", "factual", "Webb documents Ghislaine Maxwell's TerraMar Project as ocean conservation front with UN connections and submarine pilot training, suggesting intelligence cover.", 0.50, '["E1", "E3", "intelligence_cover", "PKG-EP"]'),
            ("WW1-013", "factual", "Webb documents Bill Barr's father Donald Barr hired young Epstein (no college degree) to teach at elite Dalton School. Documented fact; intelligence implications are inference.", 0.70, '["E1", "E3", "personnel_recruitment", "PKG-EP"]'),
            ("WW1-014", "factual", "Webb identifies Ari Ben-Menashe's claim that Epstein and Maxwell were recruited as Israeli intelligence assets in the 1980s. Ben-Menashe is confirmed former Israeli military intelligence but contested source.", 0.25, '["E2", "E3", "intelligence_recruitment", "PKG-EP"]'),
            ("WW1-015", "factual", "Webb documents Epstein's interest in transhumanism, eugenics, and 'seeding the human race' per NYT reporting. Documented statements exist; intelligence connection is inference.", 0.65, '["E1", "E3", "transhumanism", "PKG-EP"]'),
            ("WW1-016", "factual", "Webb documents ABC News spike of Amy Robach's Epstein story (hot mic video confirmed) and systematic media suppression pattern across major outlets.", 0.90, '["E1", "media_suppression", "PKG-EP"]'),
            ("WW1-017", "factual", "Webb documents 2026 Epstein Files release (3M+ pages) revealing FBI informant memo calling Epstein a 'Mossad Agent' and Israeli government installation of security equipment at Epstein apartment.", 0.90, '["E1", "intelligence_connections", "israel", "PKG-EP"]'),
            ("WW1-018", "factual", "Webb argues systematic protection of Epstein by DOJ, FBI, and state law enforcement represents intelligence community shielding rather than ordinary corruption.", 0.50, '["E2", "E3", "institutional_protection", "PKG-EP"]'),
            ("WW1-019", "factual", "Webb documents Towers Financial/Steven Hoffenberg Ponzi scheme ($475M) where Epstein served as consultant. Hoffenberg convicted; claimed Epstein was equal partner.", 0.70, '["E1", "E2", "financial_fraud", "PKG-EP"]'),
            ("WW1-020", "factual", "Webb documents Carbyne911 (Israeli emergency tech startup) board included Epstein, Ehud Barak, and figures connected to Unit 8200 (Israeli signals intelligence).", 0.85, '["E1", "intelligence_technology", "israel", "PKG-EP"]'),
        ]
    },
    {
        "source_id": "EP_007_Q2",
        "title": "Whitney Webb BCCI-Epstein Financial Connections Verification (PKG-EP Phase 2)",
        "file_path": "evidence/whitney_webb_Q2_bcci_verification.md",
        "evidence_type": "intelligence_report",
        "claim_prefix": "WW2",
        "claims": [
            ("WW2-001", "factual", "BCCI operated sex trafficking of minors through its 'protocol department' to compromise politicians and officials, per Kerry-Brown Senate subcommittee report.", 0.90, '["E1", "sexual_blackmail", "BCCI", "PKG-EP"]'),
            ("WW2-002", "factual", "CIA maintained 'several hundred' intelligence reports generated through BCCI relationship, per Kerry-Brown report. BCCI served as CIA financial conduit.", 0.85, '["E1", "intelligence_banking", "BCCI", "PKG-EP"]'),
            ("WW2-003", "factual", "Adnan Khashoggi used BCCI for Iran-Contra arms financing. Documented in Congressional records and Tower Commission.", 0.70, '["E1", "arms_trafficking", "BCCI", "PKG-EP"]'),
            ("WW2-004", "factual", "DOJ deliberately mishandled BCCI prosecution — Manhattan DA Robert Morgenthau forced federal action after DOJ dragged feet for years. Documented in Congressional testimony.", 0.90, '["E1", "institutional_protection", "BCCI", "PKG-EP"]'),
            ("WW2-005", "factual", "BCCI criminal client portfolios were allegedly 'inherited' by successor banks after BCCI collapse (1991). Webb's inference; no direct Congressional documentation of transfer mechanism.", 0.40, '["E2", "E3", "financial_continuity", "BCCI", "PKG-EP"]'),
            ("WW2-006", "factual", "Webb claims Epstein's IAG partnership had BCCI connections. No public court filing, indictment, or Congressional record links Epstein personally to BCCI. Sole source: unsworn statement from convicted fraudster Steven Hoffenberg.", 0.20, '["E3", "financial_connections", "BCCI", "PKG-EP"]'),
            ("WW2-007", "factual", "Rose Law Firm/Systematics (Alltel)/Arkansas BCCI nexus partially documented through Congressional hearings but key claims contested. Mixed evidence.", 0.50, '["E1", "E3", "arkansas_connection", "BCCI", "PKG-EP"]'),
            ("WW2-008", "factual", "BCCI sex trafficking was a deliberate blackmail mechanism, not incidental. Kerry-Brown documents the practice; the characterization as systematic intelligence tool is Webb's inference.", 0.55, '["E1", "E3", "sexual_blackmail", "BCCI", "PKG-EP"]'),
            ("WW2-009", "factual", "Mega Group-BCCI direct connection claimed by Webb lacks primary documentation. E3 confidence.", 0.15, '["E3", "mega_group", "BCCI", "PKG-EP"]'),
            ("WW2-010", "factual", "Overall BCCI-to-Epstein operational continuity thesis has structural plausibility but lacks primary-source documentation for the direct link. Webb's strongest BCCI claims restate Congressional findings; her most original claims lack primary sources.", 0.40, '["E2", "E3", "operational_continuity", "BCCI", "PKG-EP"]'),
        ]
    },
    {
        "source_id": "EP_007_Q3",
        "title": "Whitney Webb Maxwell-PROMIS-Intelligence Nexus (PKG-EP Phase 2)",
        "file_path": "evidence/whitney_webb_Q3_promis_nexus.md",
        "evidence_type": "intelligence_report",
        "claim_prefix": "WW3",
        "claims": [
            ("WW3-001", "factual", "DOJ stole PROMIS software from Inslaw Inc. Two federal courts found theft through 'trickery, fraud and deceit'. House Judiciary Committee (1992) confirmed.", 0.92, '["E1", "PROMIS", "DOJ", "PKG-EP"]'),
            ("WW3-002", "factual", "AG Edwin Meese and Earl Brian authorized to distribute pirated PROMIS for 'intelligence and foreign policy objectives'. Congressional finding in Brooks Report.", 0.80, '["E1", "PROMIS", "intelligence_operations", "PKG-EP"]'),
            ("WW3-003", "factual", "Rafi Eitan (LEKEM chief) visited Inslaw Feb 1983 under alias 'Dr. Ben Or'. MuckRock FOIA (2017) confirmed DOJ provided PROMIS copy to Israeli government representative.", 0.82, '["E1", "E2", "PROMIS", "israel", "PKG-EP"]'),
            ("WW3-004", "factual", "PROMIS backdoor modification claimed by Ari Ben-Menashe and Michael Riconosciuto. Consistent accounts from separate sources but no forensic confirmation of backdoored binary.", 0.50, '["E2", "E3", "PROMIS", "backdoor", "PKG-EP"]'),
            ("WW3-005", "factual", "Robert Maxwell distributed modified PROMIS through Degem Computers for Israeli intelligence. FBI opened counterintelligence investigation into 'Maxwell PROMIS Sales' (FOIA confirmed).", 0.68, '["E1", "E2", "PROMIS", "maxwell", "PKG-EP"]'),
            ("WW3-006", "factual", "Gordon Thomas sworn affidavit: Eitan told him Maxwell sold $500M+ in PROMIS licenses to intelligence agencies worldwide (UK, Australia, KGB, etc.).", 0.40, '["E2", "PROMIS", "distribution", "PKG-EP"]'),
            ("WW3-007", "factual", "Maxwell's death (Nov 5, 1991) — six intelligence chiefs attended funeral. Coincided with end of PROMIS distribution operation.", 0.65, '["E1", "E2", "maxwell", "death", "PKG-EP"]'),
            ("WW3-008", "factual", "Webb's Maxwell-PROMIS-to-Epstein continuity bridge is the weakest link. No primary documentation establishes direct operational succession from Maxwell PROMIS to Epstein blackmail operation.", 0.30, '["E3", "PROMIS", "operational_continuity", "PKG-EP"]'),
        ]
    },
    {
        "source_id": "EP_007_Q4",
        "title": "Whitney Webb Science/Technology Claims Verification (PKG-EP Phase 2)",
        "file_path": "evidence/whitney_webb_Q4_science_verification.md",
        "evidence_type": "intelligence_report",
        "claim_prefix": "WW4",
        "claims": [
            ("WW4-001", "factual", "Harvard PED received $6.5M from Epstein. Martin Nowak resigned as director. Donation documented in Harvard's own review (2020).", 0.95, '["E1", "science_network", "harvard", "PKG-EP"]'),
            ("WW4-002", "factual", "MIT Media Lab received $1.7M+ from Epstein via Joi Ito, including post-conviction donations disguised through intermediaries. Ito resigned. Documented in MIT internal investigation.", 0.95, '["E1", "science_network", "MIT", "PKG-EP"]'),
            ("WW4-003", "factual", "Edge Foundation (John Brockman) facilitated Epstein's access to elite scientific circles. Brockman hosted events where Epstein networked with Nobel laureates. Documented in emails.", 0.90, '["E1", "science_network", "edge_foundation", "PKG-EP"]'),
            ("WW4-004", "factual", "Epstein hosted 'Confronting Gravity' symposium (2006, St. Thomas USVI). Confirmed attendees include Lawrence Krauss, Lisa Randall, Gerard 't Hooft (Nobel), David Gross (Nobel), Frank Wilczek (Nobel).", 0.90, '["E1", "gravity_research", "symposium", "PKG-EP"]'),
            ("WW4-005", "factual", "Lawrence Krauss received $250K from Epstein and organized gravity conference. Resigned from ASU after sexual misconduct allegations. 60+ emails with Epstein documented.", 0.95, '["E1", "science_network", "gravity_research", "PKG-EP"]'),
            ("WW4-006", "factual", "Epstein expressed transhumanist/eugenics interests — wanted to 'seed the human race' with his DNA, fund cryogenics, establish baby ranch in New Mexico. Per NYT reporting (2019).", 0.85, '["E1", "E2", "transhumanism", "eugenics", "PKG-EP"]'),
            ("WW4-007", "factual", "Webb claims Epstein's science funding served intelligence collection purposes (access to researchers with classified connections). Plausible pattern but no primary documentation of intelligence tasking.", 0.35, '["E3", "intelligence_collection", "science_network", "PKG-EP"]'),
            ("WW4-008", "factual", "Leon Black (Apollo Global Management) paid Epstein $158M in fees (2012-2017). Black claimed advisory services; independent review found 'no evidence of wrongdoing' but $158M for tax advice is unprecedented.", 0.85, '["E1", "financial_architecture", "leon_black", "PKG-EP"]'),
        ]
    },
    {
        "source_id": "EP_007_Q5",
        "title": "Whitney Webb Weakest Claims Analysis (PKG-EP Phase 2)",
        "file_path": "evidence/whitney_webb_Q5_weak_claims.md",
        "evidence_type": "intelligence_report",
        "claim_prefix": "WW5",
        "claims": [
            ("WW5-001", "assessment", "55-65% of Webb's claims in 'One Nation Under Blackmail' are well-sourced (E1/E2) from court records, government documents, and multi-source journalism. Confidence 0.75-0.90.", 0.80, '["meta_analysis", "webb_reliability", "PKG-EP"]'),
            ("WW5-002", "assessment", "20-25% of Webb's claims represent reasonable inference from circumstantial evidence (E2/E3). Confidence 0.45-0.60.", 0.75, '["meta_analysis", "webb_reliability", "PKG-EP"]'),
            ("WW5-003", "assessment", "15-20% of Webb's claims are speculative, single-source, or guilt-by-association (E3). Confidence 0.15-0.35.", 0.75, '["meta_analysis", "webb_reliability", "PKG-EP"]'),
            ("WW5-004", "assessment", "Webb's weakest single claim: Ari Ben-Menashe's testimony on Epstein-Maxwell as Israeli assets. Ben-Menashe rejected by Congress, failed polygraph, characterized as 'unreliable' by courts. Reliability 0.15-0.25.", 0.80, '["E3", "weakest_claim", "ben_menashe", "PKG-EP"]'),
            ("WW5-005", "assessment", "Webb's continuous blackmail network thesis (Rosenstiel→Cohn→Epstein) relies on inference across generations with no primary documentation of operational succession. Reliability 0.35-0.45.", 0.70, '["E3", "pattern_matching", "blackmail_continuity", "PKG-EP"]'),
            ("WW5-006", "assessment", "Webb's 'intelligence-organized crime permanent merger' thesis is unfalsifiable by design — treats all government denials as further evidence of conspiracy. Reliability 0.30-0.40.", 0.70, '["E3", "unfalsifiable", "methodology", "PKG-EP"]'),
            ("WW5-007", "assessment", "Webb's network proximity arguments (shared attendance at events, overlapping social circles) are systematically treated as evidence of operational coordination. Standard guilt-by-association problem.", 0.75, '["E3", "guilt_by_association", "methodology", "PKG-EP"]'),
        ]
    },
    {
        "source_id": "EP_008_Q1",
        "title": "Epstein Gravity Symposium / Sherlock Entity Cross-Reference (PKG-EP Phase 2)",
        "file_path": "evidence/epstein_gravity_crossref.md",
        "evidence_type": "cross_reference_report",
        "claim_prefix": "GXR",
        "claims": [
            ("GXR-001", "factual", "No direct personnel overlap between Epstein 'Confronting Gravity' symposium attendees and Thomas Townsend Brown, Hal Puthoff, or Bigelow Aerospace/AAWSAP networks.", 0.90, '["E1", "negative_finding", "gravity_crossref", "PKG-EP"]'),
            ("GXR-002", "factual", "Lisa Randall's extra-dimensional brane models (symposium attendee) cited in DIA DIRD No. 13 by Obousy under AAWSAP/Bigelow contract. One-way intellectual appropriation, no collaboration.", 0.90, '["E1", "citation_bridge", "randall", "AAWSAP", "PKG-EP"]'),
            ("GXR-003", "factual", "Lawrence Krauss ($250K from Epstein, conference organizer) is primary personnel bridge between Epstein gravity interests and elite physics. No defense/classified physics connections.", 0.95, '["E1", "personnel_bridge", "krauss", "PKG-EP"]'),
            ("GXR-004", "factual", "Maria Spiropulu (symposium attendee) selected for DARPA Defense Science Study Group 2020-2021. Only documented defense-adjacent connection for any attendee. No evidence linking this to Epstein.", 0.85, '["E1", "defense_connection", "spiropulu", "PKG-EP"]'),
            ("GXR-005", "assessment", "Epstein recruited mainstream Nobel-tier physicists for prestige; Puthoff/Bigelow network operates in classified/fringe physics mainstream academia rejects. Structurally distinct research ecosystems.", 0.85, '["analytical", "prestige_vs_classified", "gravity_crossref", "PKG-EP"]'),
        ]
    },
    {
        "source_id": "EP_008_Q2",
        "title": "Epstein Financial Entity / Sherlock Dynasty Cross-Reference (PKG-EP Phase 2)",
        "file_path": "evidence/epstein_financial_crossref.md",
        "evidence_type": "cross_reference_report",
        "claim_prefix": "FXR",
        "claims": [
            ("FXR-001", "factual", "JPMorgan Chase is the primary bridge between Epstein financial network and BBH/Rockefeller dynasty axis. Lineage: Percy Rockefeller (S&B 1900, BBH) → Rockefeller control of Chase → JPMorgan Chase (2000) → $1B+ Epstein (2000-2013).", 0.85, '["E1", "institutional_continuity", "jpmorgan", "BBH", "PKG-EP"]'),
            ("FXR-002", "factual", "Deutsche Bank connects to dynasty network through Bankers Trust (acquired 1999), founded 1903 as J.P. Morgan-controlled entity. Epstein relationship migrated from JPMorgan to Deutsche Bank via Paul Morris (2013).", 0.80, '["E1", "institutional_lineage", "deutsche_bank", "PKG-EP"]'),
            ("FXR-003", "factual", "Sullivan & Cromwell is the recurring legal bridge — represented Bear Stearns sale to JPMorgan (2008), served as counsel for Standard Oil and Dulles brothers' intelligence operations historically.", 0.75, '["E1", "legal_bridge", "sullivan_cromwell", "PKG-EP"]'),
            ("FXR-004", "factual", "Bear Stearns was anti-establishment outlier — PSD hiring culture, non-Ivy leadership. Epstein entered Wall Street through institution that rejected dynasty-axis gatekeeping.", 0.90, '["E1", "counter_finding", "bear_stearns", "PKG-EP"]'),
            ("FXR-005", "factual", "Mega Group (Wexner/Bronfman) is a parallel elite network distinct from WASP/S&B/BBH pipeline, with separate intelligence allegations (Mossad vs CIA). Epstein may have bridged these distinct structures.", 0.60, '["E2", "parallel_network", "mega_group", "PKG-EP"]'),
            ("FXR-006", "factual", "Leon Black/Apollo represents a third axis (Drexel Burnham Lambert junk bond network). Epstein's financial network was multi-axial, not embedded in single dynasty pipeline.", 0.85, '["E1", "multi_axial", "leon_black", "apollo", "PKG-EP"]'),
            ("FXR-007", "assessment", "No direct personnel overlap between BBH and any Epstein financial entity. Connections are structural and institutional, spanning decades of corporate evolution.", 0.50, '["E3", "negative_finding", "BBH", "PKG-EP"]'),
        ]
    },
    {
        "source_id": "EP_008_Q3",
        "title": "Danny Sheehan / Iran-Contra / Epstein Network Cross-Reference (PKG-EP Phase 2)",
        "file_path": "evidence/epstein_iran_contra_crossref.md",
        "evidence_type": "cross_reference_report",
        "claim_prefix": "ICX",
        "claims": [
            ("ICX-001", "factual", "William Barr served as AG during both BCCI cover-up (1991-1993) and Epstein's death in custody (2019). Institutional protection pattern across three decades.", 0.85, '["E1", "institutional_bridge", "barr", "PKG-EP"]'),
            ("ICX-002", "factual", "BCCI serves as the primary documented institutional bridge between Iran-Contra and Epstein networks. CIA banking infrastructure documented in Kerry-Brown report.", 0.80, '["E1", "BCCI", "institutional_bridge", "PKG-EP"]'),
            ("ICX-003", "factual", "DOJ used same pattern of non-prosecution/limited prosecution in both Iran-Contra (pardons, dropped charges) and Epstein (2008 NPA, death in custody). Structural parallel in institutional behavior.", 0.75, '["E1", "E2", "DOJ_pattern", "institutional_protection", "PKG-EP"]'),
            ("ICX-004", "factual", "Adnan Khashoggi documented in both networks: Iran-Contra arms broker (Tower Commission) and Epstein social circle/financial connections.", 0.70, '["E1", "E2", "khashoggi", "personnel_overlap", "PKG-EP"]'),
            ("ICX-005", "factual", "No direct personnel overlap between Sheehan's 30 Iran-Contra defendants (Singlaub, Secord, Hakim, Clines, Shackley) and Epstein's documented network.", 0.85, '["E1", "negative_finding", "iran_contra_defendants", "PKG-EP"]'),
            ("ICX-006", "assessment", "Operational pattern matches between networks: front company structures, offshore financial laundering, legal immunity arrangements, and media suppression. Parallel methodology, not proven operational connection.", 0.55, '["E2", "E3", "pattern_analysis", "operational_parallels", "PKG-EP"]'),
        ]
    },
    {
        "source_id": "EP_008_Q4",
        "title": "Howard Lutnick / Cantor Fitzgerald / Sherlock Entity Cross-Reference (PKG-EP Phase 2)",
        "file_path": "evidence/lutnick_entity_crossref.md",
        "evidence_type": "cross_reference_report",
        "claim_prefix": "LXR",
        "claims": [
            ("LXR-001", "factual", "Lutnick testified he cut ties with Epstein in 2005. DOJ files prove island visit 2012 and business relationship through 2014. Documented contradiction.", 0.95, '["E1", "lutnick", "perjury_risk", "PKG-EP"]'),
            ("LXR-002", "factual", "Jes Staley (JPMorgan) emailed Epstein Jan 9, 2014: 'had a dinner with George Tenet and my military guy from Brookings.' Direct IC connection in Epstein-adjacent communications.", 0.90, '["E1", "staley", "tenet", "intelligence_connection", "PKG-EP"]'),
            ("LXR-003", "factual", "George Tenet joined Allen & Company (investment bank) after CIA. Allen & Company has documented Epstein connections. Tenet-Staley-Epstein triangle established.", 0.80, '["E1", "E2", "tenet", "allen_company", "PKG-EP"]'),
            ("LXR-004", "factual", "Cantor Fitzgerald handled ~25% of all US Treasury bond transactions pre-9/11. eSpeed electronic platform was systemically critical financial infrastructure. 658 employees killed.", 0.95, '["E1", "cantor_fitzgerald", "9_11", "financial_infrastructure", "PKG-EP"]'),
            ("LXR-005", "factual", "CIA asked British regulators to investigate Treasury bond trades before 9/11. WTC7 collapse destroyed SEC investigation files and CIA's largest domestic station.", 0.85, '["E1", "E2", "9_11", "records_destruction", "PKG-EP"]'),
            ("LXR-006", "assessment", "No direct documented connection between Cantor Fitzgerald and Carlyle Group/GHW Bush or BCCI. Connections are through shared institutional environment (Wall Street, government bond markets).", 0.50, '["E3", "negative_finding", "cantor_fitzgerald", "bush", "PKG-EP"]'),
            ("LXR-007", "factual", "Lutnick raised $75M+ for Trump 2024 campaign, confirmed as Commerce Secretary Feb 2025. Epstein connection controversy arose during confirmation.", 0.95, '["E1", "lutnick", "political_connections", "PKG-EP"]'),
        ]
    },
]

# Cross-references to create
CROSS_REFS = [
    # Webb Q1 cross-refs
    ("xref_ep_043", "Whitney Webb Analysis", "Sherlock PKG-EP Phase 1", "validation_and_extension", "WW1-002,WW1-003", 0.75),
    ("xref_ep_044", "PROMIS/Inslaw", "Epstein Blackmail Operation", "operational_continuity_alleged", "WW3-008,WW1-003", 0.30),
    # Q2 BCCI cross-refs
    ("xref_ep_045", "BCCI Sex Trafficking", "Epstein Sex Trafficking", "structural_parallel", "WW2-001,WW2-008", 0.65),
    ("xref_ep_046", "BCCI Intelligence Banking", "Epstein Financial Architecture", "operational_pattern_match", "WW2-002,WW2-010", 0.40),
    # Gravity cross-refs
    ("xref_ep_047", "Epstein Gravity Symposium", "AAWSAP/Bigelow Aerospace", "citation_bridge_only", "GXR-001,GXR-002", 0.30),
    ("xref_ep_048", "Lisa Randall (Epstein symposium)", "DIA DIRD No. 13 (AAWSAP)", "theoretical_citation", "GXR-002", 0.90),
    # Financial dynasty cross-refs
    ("xref_ep_049", "JPMorgan Chase", "BBH/Rockefeller Dynasty", "institutional_lineage", "FXR-001", 0.85),
    ("xref_ep_050", "Sullivan & Cromwell", "Epstein Network Legal Infrastructure", "recurring_legal_bridge", "FXR-003", 0.75),
    ("xref_ep_051", "Mega Group (Wexner/Bronfman)", "BBH/WASP Dynasty", "parallel_elite_network", "FXR-005", 0.60),
    # Iran-Contra cross-refs
    ("xref_ep_052", "Iran-Contra Network", "Epstein Network", "institutional_pattern_parallel", "ICX-003,ICX-006", 0.55),
    ("xref_ep_053", "William Barr", "BCCI Cover-Up AND Epstein Death", "institutional_bridge_person", "ICX-001", 0.85),
    ("xref_ep_054", "Adnan Khashoggi", "Both Iran-Contra AND Epstein Networks", "personnel_overlap", "ICX-004", 0.70),
    # Lutnick cross-refs
    ("xref_ep_055", "Jes Staley/JPMorgan", "George Tenet/CIA", "documented_social_connection", "LXR-002,LXR-003", 0.90),
    ("xref_ep_056", "Cantor Fitzgerald 9/11", "SEC Records Destruction (WTC7)", "financial_infrastructure_nexus", "LXR-004,LXR-005", 0.85),
    ("xref_ep_057", "Howard Lutnick", "Jeffrey Epstein", "documented_contradiction_in_testimony", "LXR-001", 0.95),
    # Webb reliability meta-cross-ref
    ("xref_ep_058", "Whitney Webb (source reliability)", "Sherlock Evidence Standards", "meta_assessment", "WW5-001,WW5-002,WW5-003", 0.80),
]


def ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.utcnow().isoformat()

    sources_added = 0
    claims_added = 0
    xrefs_added = 0

    for report in REPORTS:
        # Check if source already exists
        c.execute("SELECT source_id FROM evidence_sources WHERE source_id = ?", (report["source_id"],))
        if c.fetchone():
            print(f"SKIP source {report['source_id']}: already exists")
            continue

        # Insert source
        c.execute("""
            INSERT INTO evidence_sources (source_id, title, file_path, evidence_type, created_at, ingested_at, processing_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, 'complete', ?)
        """, (
            report["source_id"],
            report["title"],
            report["file_path"],
            report["evidence_type"],
            now, now,
            json.dumps({"campaign": "PKG-EP", "phase": 2, "synthesized_from": "phase2_transcripts"})
        ))
        sources_added += 1
        print(f"Added source: {report['source_id']} — {report['title']}")

        # Insert claims
        for claim_id, claim_type, text, confidence, tags in report["claims"]:
            c.execute("SELECT claim_id FROM evidence_claims WHERE claim_id = ?", (claim_id,))
            if c.fetchone():
                print(f"  SKIP claim {claim_id}: already exists")
                continue

            c.execute("""
                INSERT INTO evidence_claims (claim_id, source_id, claim_type, text, confidence, tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (claim_id, report["source_id"], claim_type, text, confidence, tags, now))
            claims_added += 1

        print(f"  Added {len(report['claims'])} claims")

    # Insert cross-references
    for xref_id, entity1, entity2, rel_type, source_claims, confidence in CROSS_REFS:
        c.execute("SELECT xref_id FROM cross_references WHERE xref_id = ?", (xref_id,))
        if c.fetchone():
            print(f"SKIP xref {xref_id}: already exists")
            continue

        c.execute("""
            INSERT INTO cross_references (xref_id, entity1, entity2, relationship_type, source_claims, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (xref_id, entity1, entity2, rel_type, source_claims, confidence, now))
        xrefs_added += 1

    conn.commit()

    # Verify
    c.execute("SELECT COUNT(*) FROM evidence_sources")
    total_sources = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM evidence_claims")
    total_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references")
    total_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"INGESTION COMPLETE")
    print(f"  Sources added: {sources_added} (total: {total_sources})")
    print(f"  Claims added: {claims_added} (total: {total_claims})")
    print(f"  Cross-refs added: {xrefs_added} (total: {total_xrefs})")
    print(f"{'='*60}")


if __name__ == "__main__":
    ingest()
