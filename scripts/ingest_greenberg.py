#!/usr/bin/env python3
"""Ingest Alan 'Ace' Greenberg intelligence reports into sherlock.db.

Registers 1 evidence source (GREENBERG_DYNASTY_001), extracts ~45 claims
across all 5 phases of the Greenberg Campaign (PKG-EP Phase 5 — Campaign A),
and creates ~15 cross-references connecting Greenberg findings to existing targets.

Also upgrades Bear Stearns-BCCI claims (BSB-*) from E3 to E1 based on
Sandstorm Report primary source confirmation.
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

# Single source for the entire Greenberg Campaign
SOURCE = {
    "source_id": "GREENBERG_DYNASTY_001",
    "title": "Greenberg Dynasty Intelligence Report (PKG-EP Phase 5, Campaign A)",
    "file_path": "evidence/greenberg_dynasty_intelligence_report.md",
    "evidence_type": "intelligence_report",
}

# =============================================================================
# CLAIMS — 45 claims across 5 phases (GRB-001 to GRB-045)
# Each: (claim_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    # =========================================================================
    # PHASE 1: Career & Background (GRB-001 to GRB-009)
    # =========================================================================
    ("GRB-001", "factual",
     "Alan 'Ace' Greenberg born November 3, 1927, Wichita, Kansas. Father Jacob Greenberg was a clothing store owner. Attended University of Missouri (BA 1949, finance). Joined Bear Stearns & Co. in 1949, the same year he graduated.",
     0.95, '["E1", "E2", "background", "greenberg", "bear_stearns", "PKG-EP"]'),

    ("GRB-002", "anomaly",
     "Greenberg's military service 1927-1949 is unresolved. He was 17-18 at WWII's end (1945) and 22-26 during the Korean War (1950-1953) — prime draft age for Korea. No WWII or Korean War military service has been documented in any available biography. No selective service records have been FOIA'd.",
     0.70, '["UNVERIFIED", "greenberg", "military_gap", "anomaly", "PKG-EP"]'),

    ("GRB-003", "factual",
     "Greenberg's 'PSD' management philosophy: hire people who are 'Poor, Smart, and have a Deep desire to be rich.' Wrote quarterly memos to Bear Stearns employees enforcing this and frugality principles. Required employees to save rubber bands and paper clips. The philosophy explains his willingness to hire Epstein without credentials.",
     0.90, '["E1", "greenberg", "management_philosophy", "PSD", "PKG-EP"]'),

    ("GRB-004", "factual",
     "Greenberg's Bear Stearns career: partner ~1958; joined board of directors 1974; CEO 1978-1993 (15-year tenure); Chairman Executive Committee 1993-2008. Died July 25, 2014, age 86, after the firm's 2008 collapse. Lost most personal wealth in the Bear Stearns collapse.",
     0.95, '["E1", "greenberg", "bear_stearns", "career", "PKG-EP"]'),

    ("GRB-005", "factual",
     "Greenberg served as honorary co-chairman (alongside Donald Trump and Rupert Murdoch) at a 1983 UJA-Federation dinner honoring Roy Cohn. Greenberg's words at the dinner: 'This is for Roy.' Event confirmed via Consortium News PDF archive. Placed Greenberg at documented social intersection of Cohn's intelligence/organized crime network at its operational peak.",
     0.95, '["E1", "greenberg", "cohn", "trump", "murdoch", "UJA_dinner", "PKG-EP"]'),

    ("GRB-006", "factual",
     "Pre-1983 Greenberg-Cohn social relationship probable via UJA-Federation overlap (both were major donors and UJA was the primary social nexus for Jewish New York business and philanthropy in this era) but not documented in specific pre-1983 meeting records. The 1983 dinner is the earliest documented event.",
     0.60, '["E2", "greenberg", "cohn", "UJA_federation", "social_nexus", "PKG-EP"]'),

    ("GRB-007", "factual",
     "Donald Trump is the strongest documented shared node between Greenberg and Roy Cohn: (1) Cohn was Trump's personal attorney for 13 years (1973-1986); (2) Trump was a Bear Stearns client; (3) Trump co-honored Cohn at the 1983 dinner. Trump's position makes him the most analytically important shared node in the Greenberg network assessment.",
     0.85, '["E1", "E2", "greenberg", "trump", "cohn", "network_node", "PKG-EP"]'),

    ("GRB-008", "factual",
     "Post-Cohn death (1986) network continuity: Greenberg maintained documented social relationships with Trump and Murdoch as both continued in prominence. No evidence that Greenberg deliberately inherited or operated any intelligence/blackmail infrastructure from Cohn. Post-Cohn network continuity is most defensible as coincidence of social relationships, not deliberate succession.",
     0.70, '["E2", "greenberg", "cohn_network", "network_continuity", "PKG-EP"]'),

    ("GRB-009", "factual",
     "James 'Jimmy' Cayne succeeded Greenberg as Bear Stearns CEO in 1993. Cayne maintained an independent personal trust relationship with Jeffrey Epstein during his CEO tenure (1993-2008), separate from but parallel to Greenberg's ongoing client relationship with Epstein. Both Greenberg and Cayne thus maintained personal Epstein relationships across the full 1993-2008 period.",
     0.80, '["E1", "E2", "greenberg", "cayne", "epstein", "bear_stearns", "PKG-EP"]'),

    # =========================================================================
    # PHASE 2: The Epstein Connection (GRB-010 to GRB-022)
    # =========================================================================
    ("GRB-010", "factual",
     "Greenberg hired Jeffrey Epstein at Bear Stearns in 1976 despite Epstein having a fraudulent resume (no college degree; resume falsely claimed Ohio State University degree). The 'Dalton parent' referral trail traces to the Greenberg family itself: Epstein simultaneously tutored Greenberg's son Ted AND was in a romantic relationship with Greenberg's daughter Lynne Greenberg.",
     0.80, '["E2", "greenberg", "epstein", "hire", "dalton", "family_nexus", "PKG-EP"]'),

    ("GRB-011", "factual",
     "Epstein's resume fraud was discovered at Bear Stearns within weeks of hiring. Despite the discovery, Epstein was retained. Most probable explanation: he was simultaneously dating CEO Greenberg's daughter Lynne. Lynne Greenberg later advocated on Epstein's behalf after he was subsequently dismissed from Bear Stearns. No alternative explanation (PSD philosophy alone, intelligence referral) has comparable evidential support.",
     0.75, '["E2", "greenberg", "epstein", "resume_fraud", "retention", "PKG-EP"]'),

    ("GRB-012", "factual",
     "Jeffrey Epstein was made a limited partner at Bear Stearns in 1980 — an extraordinary advancement for someone without a college degree. This promotion occurred under Greenberg's direct authority as CEO. The advancement is consistent with strong internal patronage from the Greenberg family connection and Epstein's documented effectiveness as a client generator.",
     0.80, '["E1", "E2", "greenberg", "epstein", "limited_partner", "PKG-EP"]'),

    ("GRB-013", "factual",
     "Epstein departed Bear Stearns on March 12, 1981 — one day after the SEC opened a formal inquiry into trading by Seagram Company insiders who had purchased St. Joe Minerals stock ahead of a takeover announcement. The timing strongly suggests a managed departure rather than a disciplinary firing, coordinated to protect Bear Stearns from SEC insider trading exposure.",
     0.70, '["E1", "E2", "greenberg", "epstein", "departure", "SEC_inquiry", "managed_exit", "PKG-EP"]'),

    ("GRB-014", "factual",
     "27-year post-departure Greenberg-Epstein relationship documented by Bloomberg's 2025 investigation into Epstein's emails: Epstein continued trading Les Wexner's money through Bear Stearns after his 1981 departure; maintained active relationships with both Greenberg and Cayne; served as chairman of Bear Stearns-owned Liquid Funding Ltd. (2001-2007).",
     0.99, '["E1", "greenberg", "epstein", "post_departure", "wexner", "LFL", "PKG-EP"]'),

    ("GRB-015", "factual",
     "Greenberg contributed to Jeffrey Epstein's 2003 birthday book: 'Working with Jeffrey has been a pleasure.' This contribution in 2003 — 22 years after Epstein's departure, and after Epstein's 2002 Vanity Fair profile (which raised serious questions) and during the period of Epstein's 2001 Virginia Giuffre recruitment — directly contradicts any claim the relationship ended in 1981.",
     0.95, '["E1", "greenberg", "epstein", "birthday_book", "ongoing_relationship", "PKG-EP"]'),

    ("GRB-016", "factual",
     "The Greenberg family contributed collectively to Epstein's birthday book (2003). Lynne Greenberg, Greenberg's daughter who had dated Epstein at Bear Stearns, later advocated on Epstein's behalf after his departure from the firm. Both generations of the Greenberg family maintained positive relationships with Epstein through at least 2003.",
     0.75, '["E2", "greenberg", "epstein", "lynne_greenberg", "family_nexus", "PKG-EP"]'),

    ("GRB-017", "factual",
     "Epstein's draft lawsuit documents (June 2008) show he was preparing legal action against Bear Stearns and JPMorgan over losses in the Enhanced Leverage Fund. JPMorgan ultimately paid Epstein $9 million to settle (2011). Whether this settlement involved Liquid Funding Ltd. claims is not separately documented.",
     0.85, '["E1", "greenberg", "epstein", "bear_stearns", "lawsuit", "settlement", "PKG-EP"]'),

    ("GRB-018", "factual",
     "Jeffrey Epstein's Wexner money management operation, run from his Bear Stearns-adjacent network (1981-1994+), provided a major source of fee revenue for Bear Stearns through block trading commissions. This commercial revenue explains why Greenberg maintained the post-departure relationship independent of any personal warmth: Epstein was a profitable client representing Wexner's $1B+ fortune.",
     0.75, '["E1", "E2", "greenberg", "epstein", "wexner", "commercial_nexus", "PKG-EP"]'),

    ("GRB-019", "factual",
     "'Dalton parent' hypothesis assessed: The widely-cited claim that Donald Barr (OSS officer, Dalton headmaster) was the intelligence-connected 'Dalton parent' who introduced Epstein to Bear Stearns is assessed as UNPROVEN and most probably incorrect. Barr announced his Dalton resignation in February 1974; Epstein started at Dalton in September 1974. No documented Barr-Greenberg connection has been found. The actual referral chain ran through the Greenberg family itself.",
     0.80, '["E2", "greenberg", "epstein", "donald_barr", "dalton_parent", "NEGATIVE_FINDING", "PKG-EP"]'),

    ("GRB-020", "factual",
     "Donald Barr (1926-2006): OSS officer in WWII; joined faculty of Teachers College, Columbia; headmaster of Dalton School 1964-1974; hired Jeffrey Epstein as a math teacher in September 1974 before himself departing Dalton in June 1974. Father of William Barr (Attorney General). His OSS service does not establish a CIA operational role in the 1970s; the CIA connection remains E3 at 0.15 confidence.",
     0.80, '["E1", "E2", "donald_barr", "OSS", "dalton", "epstein", "PKG-EP"]'),

    ("GRB-021", "factual",
     "William Barr (son of Donald Barr): CIA 1971-1977; partner at Shaw Pittman 1977-1989; US Attorney General under Bush (1991-1993) and Trump (2019-2020). Did NOT fully recuse himself from the Epstein criminal case despite the Donald Barr-Epstein hire connection. Personally reviewed Epstein jail footage. CBS News (2025) found inconsistencies in his public account of the Epstein jail death.",
     0.85, '["E1", "E2", "william_barr", "CIA", "epstein", "DOJ", "PKG-EP"]'),

    ("GRB-022", "factual",
     "Epstein became a limited partner at Bear Stearns in 1980, giving him access to the firm's client network and institutional relationships. This platform, established under Greenberg's patronage, is what allowed Epstein to attract ultra-high-net-worth clients like Wexner (circa 1985) and later institutional investors. The Bear Stearns credentialing was the foundation of the Epstein financial myth.",
     0.80, '["E1", "E2", "greenberg", "epstein", "bear_stearns", "credentialing", "PKG-EP"]'),

    # =========================================================================
    # PHASE 3: BCCI & Intelligence Connections (GRB-023 to GRB-035)
    # =========================================================================
    ("GRB-023", "factual",
     "PRIMARY SOURCE CONFIRMATION: The June 1991 Price Waterhouse Sandstorm Report (commissioned by Bank of England, submitted June 22 1991, suppressed until 2011) names Bear Stearns as one of four main BCCI Treasury brokers: 'The main brokers used by Treasury division were: Refco / Capital Commodity Dealers Ltd (Capcom) / Rudolf Wolff / Bear Steans [sic].' Available at: /home/johnny5/Sherlock/evidence/sandstorm_part2_ocr.txt (Section 4, pages 99-101). OCR spelling artifact 'Bear Steans' is unambiguous in context.",
     0.95, '["E1", "greenberg", "bear_stearns", "BCCI", "sandstorm_report", "primary_source", "UPGRADE_E3_TO_E1", "PKG-EP"]'),

    ("GRB-024", "factual",
     "The Sandstorm Report's general allegation about BCCI Treasury brokers: 'The investigation team has seen circumstantial evidence that these brokers did not always trade with Treasury at arms length, and may have facilitated [Akbar] in manipulating profits.' This general allegation applies to all four named brokers including Bear Stearns, but specific aggravating narrative in the Sandstorm Report is directed at Rudolf Wolff (overdrawn balance) and Capcom (BCCI front) — NOT specifically at Bear Stearns.",
     0.80, '["E1", "greenberg", "bear_stearns", "BCCI", "sandstorm_report", "arms_length", "PKG-EP"]'),

    ("GRB-025", "factual",
     "Bear Stearns' BCCI Treasury brokerage documented in Section 4.22-4.23 of Sandstorm Report, relating to 1983-1986 — overlapping Greenberg's CEO tenure (1978-1993). Whether Greenberg personally directed or was aware of the BCCI brokerage relationship is analytically probable (CEO awareness of major institutional counterparties) but not specifically documented. Whether he knew of BCCI's criminal character during 1983-1986 (before public exposure) is unknown.",
     0.65, '["E1", "E3", "greenberg", "bear_stearns", "BCCI", "sandstorm_report", "CEO_awareness", "PKG-EP"]'),

    ("GRB-026", "factual",
     "Capital Commodity Dealers Ltd. (Capcom) — listed alongside Bear Stearns in Sandstorm Report as a main BCCI Treasury broker — was separately documented as a BCCI front operation. Capcom was established in 1984 with initial shareholders from BCCI's major customers. It was investigated and charged under RICO. Bear Stearns appears in the same list but NOT with Capcom's level of structural BCCI entanglement.",
     0.90, '["E1", "bear_stearns", "BCCI", "capcom", "sandstorm_report", "PKG-EP"]'),

    ("GRB-027", "factual",
     "Bear Stearns was a Federal Reserve Bank of New York primary dealer — directly authorized to trade US government securities with the Federal Reserve. Primary dealers are required to participate in all Treasury auctions, make markets in government securities, and provide market intelligence to the Fed. This gave Bear Stearns privileged ongoing access to Treasury and Federal Reserve financial and policy intelligence.",
     0.99, '["E1", "bear_stearns", "federal_reserve", "primary_dealer", "government_finance", "PKG-EP"]'),

    ("GRB-028", "factual",
     "2008 Bear Stearns bailout: The Federal Reserve provided $30 billion in emergency backstop financing to facilitate JPMorgan's acquisition of Bear Stearns at $10/share (March 2008). The Fed explicitly intervened for Bear Stearns but allowed Lehman Brothers to fail six months later. The differential treatment reflects Bear Stearns' privileged primary dealer status and its systemic importance to Treasury market function.",
     0.95, '["E1", "bear_stearns", "federal_reserve", "2008_bailout", "JPMorgan", "primary_dealer", "PKG-EP"]'),

    ("GRB-029", "factual",
     "Liquid Funding Ltd. (LFL): Incorporated October 19, 2000, Bermuda (Appleby law firm). Peak assets $6.7 billion. Bear Stearns 40% equity owner (SEC filing). Epstein served as chairman November 9, 2001 through at least March 19, 2007. 60% ownership publicly undisclosed — identity never determined in any available source. 180:1 leverage ratio. Managed out of Bear Stearns Bank Plc Dublin.",
     0.99, '["E1", "greenberg", "bear_stearns", "epstein", "LFL", "liquid_funding", "bermuda", "PKG-EP"]'),

    ("GRB-030", "factual",
     "LFL April 2008 payoff anomaly: Moody's confirmed in April 2008 that all outstanding rated LFL liabilities were paid in full — three weeks after Bear Stearns' March 2008 collapse. Who had the motivation and resources to pay off a 180:1 leveraged $6.7B vehicle in weeks during the worst financial crisis since 1929 is unexplained. This is the single largest unresolved financial intelligence gap in the Epstein case.",
     0.90, '["E1", "E2", "greenberg", "bear_stearns", "epstein", "LFL", "liquid_funding", "anomaly", "payoff_mystery", "PKG-EP"]'),

    ("GRB-031", "factual",
     "JPMorgan Chase involvement in LFL: Moody's (2004) revealed JPMorgan Chase, Bank of America, and Natexis Banque Populaire extended LFL a $250M liquidity facility. JPMorgan also listed as 'Security Trustee.' Liam MacNamara served simultaneously on LFL's board AND JPMorgan's Dublin board — establishing director-level JPMorgan-LFL overlap beyond the liquidity facility role.",
     0.90, '["E1", "bear_stearns", "epstein", "LFL", "JPMorgan", "macnamara", "PKG-EP"]'),

    ("GRB-032", "factual",
     "Paul Novelly (Liquid Funding Ltd. / Bear Stearns Board): CEO and Chairman of Apex Oil Company (wholesale petroleum products). Bear Stearns Director since 2002; Member Audit Committee, Finance and Risk Committee (Chairman), Corporate Governance Committee. Simultaneously on LFL's board. Lost approximately $10 million in Bear Stearns stock at the 2008 collapse.",
     0.85, '["E1", "bear_stearns", "epstein", "LFL", "novelly", "petroleum", "PKG-EP"]'),

    ("GRB-033", "factual",
     "Jeffrey Lipman (Bear Stearns): Senior executive at Bear Stearns documented in business registry filings. Described as Epstein's primary Bear Stearns counterpart for LFL-related structured investment vehicle activities. After Bear Stearns' 2008 collapse, Lipman's career profile appears in JPMorgan entities (JPMorgan Clearing Corp.), consistent with the broader Bear Stearns-JPMorgan personnel transfer.",
     0.70, '["E2", "bear_stearns", "epstein", "LFL", "lipman", "JPMorgan", "PKG-EP"]'),

    ("GRB-034", "factual",
     "Adnan Khashoggi: BCCI client who moved $20M through BCCI accounts for five Iranian arms deals (documented in Kerry-Brown Senate BCCI Report, E1). Khashoggi subsequently became a client of Epstein's IAG financial operation (post-1981, per Vicky Ward reporting, E2). Bear Stearns was a BCCI Treasury broker (Sandstorm E1). The structural proximity is high, but direct Bear Stearns-Khashoggi financial documentation has not been established.",
     0.55, '["E1", "E2", "bear_stearns", "BCCI", "khashoggi", "epstein", "structural_proximity", "PKG-EP"]'),

    ("GRB-035", "factual",
     "Mike Benz claim assessment: Benz claimed Bear Stearns 'cleared $13 billion with BCCI' and that Greenberg 'set up the BCCI Luxembourg account.' The baseline (Bear Stearns as BCCI broker) is confirmed E1 by Sandstorm. The $13B figure, Greenberg personally setting up accounts, and CIA/Saudi/Israeli covert cash concealment are all E3 — no primary source documentation has been published. Benz's specific claims are unsourced amplification of the real E1 finding.",
     0.90, '["E2", "E3", "bear_stearns", "BCCI", "benz_claim", "unsourced", "greenberg", "PKG-EP"]'),

    # =========================================================================
    # PHASE 4-5: Intelligence Hypothesis & Synthesis (GRB-036 to GRB-045)
    # =========================================================================
    ("GRB-036", "assessment",
     "CIA hypothesis for Greenberg: INDETERMINATE. No documentary evidence (FOIA files, sworn testimony, government records) naming Greenberg as a CIA asset or informant has been found. The structural circumstantial case is real (BCCI brokerage E1, primary dealer access E1, Epstein relationship E1, Cohn social nexus E1) but does not constitute evidence of CIA asset status. Confidence in CIA hypothesis: 0.10. Most parsimonious alternatives explain all documented anomalies.",
     0.90, '["assessment", "greenberg", "CIA", "indeterminate", "hypothesis", "PKG-EP"]'),

    ("GRB-037", "assessment",
     "Greenberg bridge node hypothesis: CONFIRMED at E2. Greenberg is the structural hinge between three overlapping intelligence-adjacent networks: (1) Cohn organized crime/blackmail network (1983 dinner, Trump shared node); (2) Epstein trafficking/intelligence network (founding patron 1976-2008, LFL co-owner); (3) BCCI intelligence banking network (Bear Stearns Treasury broker 1983-1986, Sandstorm E1). Connections are documented. Deliberateness of bridge function is unproven.",
     0.80, '["E2", "assessment", "greenberg", "bridge_node", "cohn", "epstein", "BCCI", "PKG-EP"]'),

    ("GRB-038", "assessment",
     "Overall Greenberg intelligence characterization: Greenberg was an institutional enabler whose decisions — hiring Epstein (1976), maintaining Epstein as client (1981-2008), operating as BCCI Treasury broker (1983-1986), co-owning LFL (2000-2008) — consistently placed Bear Stearns at the intersection of government finance, intelligence-adjacent banking, and offshore financial structures. Whether this reflects deliberate CIA coordination or the natural position of a major primary dealer CEO who maintained relationships with intelligence-adjacent individuals cannot be determined from available evidence.",
     0.80, '["E1", "E2", "assessment", "greenberg", "institutional_enabler", "PKG-EP"]'),

    ("GRB-039", "assessment",
     "Bear Stearns institutional profile under Greenberg: simultaneously (1) Federal Reserve primary dealer with direct Treasury/Fed access; (2) named main BCCI Treasury broker during BCCI's peak CIA banking channel period; (3) institutional home and subsequent 27-year financial relationship of Jeffrey Epstein; (4) 40% owner of Liquid Funding Ltd. with Epstein as chairman and 60% unknown ownership. This institutional profile places Bear Stearns at documented intersection of government finance, IC-adjacent banking, and offshore financial structures.",
     0.85, '["E1", "E2", "bear_stearns", "greenberg", "institutional_profile", "intelligence_adjacent", "PKG-EP"]'),

    ("GRB-040", "assessment",
     "Greenberg's personal relationship with Epstein extended well beyond business: the family connection (son Ted tutored; daughter Lynne dated), the ongoing warmth documented in the 2003 birthday book, the 27-year maintained client relationship. Whether Greenberg had any awareness of Epstein's trafficking operations — given that Epstein's activities were known to some Bear Stearns insiders by the late 1990s — cannot be determined from available evidence.",
     0.60, '["assessment", "greenberg", "epstein", "personal_relationship", "trafficking_awareness", "UNKNOWN", "PKG-EP"]'),

    ("GRB-041", "factual",
     "Bear Stearns' roster of BCCI-connected clients creates a structural node map: Adnan Khashoggi (BCCI client → Epstein IAG client); BCCI Treasury division (Bear Stearns Treasury broker, Sandstorm E1); Jeffrey Epstein (Bear Stearns patron, 1976-2008); Les Wexner (money managed through Bear Stearns via Epstein). The structural proximity of these actors through Bear Stearns as a common institutional node is high, but direct documented links between all parties require further research.",
     0.70, '["E1", "E2", "bear_stearns", "greenberg", "BCCI", "epstein", "wexner", "khashoggi", "structural_node", "PKG-EP"]'),

    ("GRB-042", "factual",
     "The 1983-1986 BCCI Treasury brokerage period overlaps precisely with: (1) the period when BCCI was most actively used as a CIA banking channel (documented in Kerry-Brown Senate report); (2) Greenberg's tenure as Bear Stearns CEO; (3) the period when Epstein was building his post-Bear Stearns financial network. These temporal overlaps are analytically significant but do not establish operational coordination.",
     0.75, '["E1", "E2", "bear_stearns", "greenberg", "BCCI", "CIA", "temporal_overlap", "PKG-EP"]'),

    ("GRB-043", "factual",
     "Greenberg co-owned or supervised three major financial vehicles that intersected the Epstein network: (1) Bear Stearns itself (institutional bank, BCCI broker, primary dealer); (2) Liquid Funding Ltd. (40% Bear Stearns, Epstein chairman, $6.7B, unknown 60% owners); (3) Enhanced Leverage Fund (the fund Epstein's $57M investment may have contributed to triggering collapse). Whether Greenberg specifically understood or directed the intelligence dimensions of these structures is unestablished.",
     0.70, '["E2", "greenberg", "epstein", "bear_stearns", "LFL", "ELF", "financial_vehicles", "PKG-EP"]'),

    ("GRB-044", "factual",
     "The April 2008 LFL payoff — all liabilities paid in full three weeks after Bear Stearns collapsed — is the most analytically unexplained event in the Greenberg-Epstein financial nexus. The candidate explanations for who had both motivation and resources to pay off a 180:1 leveraged $6.7B vehicle at the height of the financial crisis include: Epstein's unknown principals; Wexner-connected entities; foreign sovereign wealth vehicles; intelligence community off-balance-sheet funds. None can be confirmed from available evidence.",
     0.85, '["E1", "E2", "E3", "greenberg", "epstein", "LFL", "liquid_funding", "2008_payoff", "anomaly", "PKG-EP"]'),

    ("GRB-045", "assessment",
     "Greenberg significance to PKG-EP: (1) Created Epstein's institutional platform without which Epstein's financial career may not have existed; (2) BCCI brokerage confirmation upgrades the Bear Stearns-BCCI-Epstein nexus from inference to primary-source documented fact; (3) The 27-year relationship and LFL structure represent the most significant documented overlap between intelligence-adjacent financial operations (BCCI) and the Epstein network; (4) LFL's 60% unknown ownership and April 2008 anomalous payoff remain the most significant unresolved financial intelligence mysteries in the entire Epstein case.",
     0.85, '["E1", "E2", "assessment", "greenberg", "PKG-EP", "significance"]'),
]

# =============================================================================
# CROSS-REFERENCES — 15 connections (xref_grb_001 to xref_grb_015)
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    ("xref_grb_001", "GRB_Greenberg", "EP_Epstein",
     "FOUNDING_PATRON_INSTITUTION",
     "GRB-010,GRB-011,GRB-012,GRB-013,GRB-014,GRB-015",
     0.99),

    ("xref_grb_002", "GRB_Greenberg", "BSB_BearStearns",
     "INSTITUTIONAL_LEADER",
     "GRB-001,GRB-004,GRB-023,GRB-027,GRB-039",
     0.99),

    ("xref_grb_003", "BSB_BearStearns", "BCCI_Network",
     "TREASURY_BROKER_PRIMARY_SOURCE",
     "GRB-023,GRB-024,GRB-025,GRB-026",
     0.95),

    ("xref_grb_004", "GRB_Greenberg", "WEX_Wexner",
     "INDIRECT_FINANCIAL_NEXUS_VIA_EPSTEIN",
     "GRB-014,GRB-018,GRB-041",
     0.80),

    ("xref_grb_005", "GRB_Greenberg", "RC_RoyCohn",
     "SOCIAL_NEXUS_1983_UJA_DINNER",
     "GRB-005,GRB-006,GRB-007",
     0.95),

    ("xref_grb_006", "GRB_Greenberg", "Trump_Network",
     "SHARED_NODE_COHN_BEARING",
     "GRB-005,GRB-007,GRB-008",
     0.85),

    ("xref_grb_007", "BSB_BearStearns", "BCCI_Sandstorm",
     "EVIDENCE_UPGRADE_E3_TO_E1",
     "GRB-023,GRB-024",
     0.95),

    ("xref_grb_008", "EP_Epstein", "LFL_LiquidFunding",
     "CHAIRMAN_OF_OFFSHORE_VEHICLE",
     "GRB-029,GRB-030,GRB-031",
     0.99),

    ("xref_grb_009", "BSB_BearStearns", "JPMorgan_Chase",
     "ACQUISITION_AND_LFL_TRUSTEE",
     "GRB-028,GRB-031,GRB-033",
     0.95),

    ("xref_grb_010", "GRB_Greenberg", "DonaldBarr_OSS",
     "NEGATIVE_FINDING_NO_REFERRAL_CHAIN",
     "GRB-019,GRB-020",
     0.80),

    ("xref_grb_011", "EP_Epstein", "BCCI_Network",
     "STRUCTURAL_PROXIMITY_VIA_BEAR_STEARNS",
     "GRB-023,GRB-034,GRB-042",
     0.60),

    ("xref_grb_012", "BSB_BearStearns", "Sandstorm_Report",
     "PRIMARY_SOURCE_NAMING",
     "GRB-023,GRB-024,GRB-026",
     0.95),

    ("xref_grb_013", "EP_Epstein", "Khashoggi_Network",
     "BCCI_BRIDGE_VIA_BEAR_STEARNS",
     "GRB-034",
     0.55),

    ("xref_grb_014", "BSB_BearStearns", "FederalReserve",
     "PRIMARY_DEALER_PRIVILEGED_RELATIONSHIP",
     "GRB-027,GRB-028",
     0.99),

    ("xref_grb_015", "WilliamBarr_AG", "EP_Epstein",
     "DOJ_OVERSIGHT_FAILURE_FAMILY_CONFLICT",
     "GRB-021",
     0.85),
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
                "campaign": "PKG-EP Phase 5 Campaign A",
                "target_id": 57,
                "target_name": "Alan 'Ace' Greenberg",
                "phases": ["G1_career", "G2_epstein", "G3_cohn", "G4_bcci", "G5_synthesis"],
                "total_claims": 45,
                "total_xrefs": 15,
                "key_finding": "Sandstorm primary source confirms Bear Stearns as BCCI Treasury broker (E1 upgrade)",
                "CIA_hypothesis": "INDETERMINATE (0.10)",
                "bridge_node_confirmed": "E2 (0.80)",
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

    c.execute("SELECT COUNT(*) FROM evidence_claims WHERE claim_id LIKE 'GRB-%'")
    grb_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references WHERE xref_id LIKE 'xref_grb_%'")
    grb_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"GREENBERG CAMPAIGN INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Sources added this run:  {sources_added}")
    print(f"  Claims added this run:   {claims_added}")
    print(f"  Claims skipped (dupes):  {claims_skipped}")
    print(f"  Xrefs added this run:    {xrefs_added}")
    print(f"  Xrefs skipped (dupes):   {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  GREENBERG CAMPAIGN TOTALS:")
    print(f"    GRB-* claims in DB:    {grb_claims}")
    print(f"    xref_grb_* in DB:      {grb_xrefs}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total sources:         {total_sources}")
    print(f"    Total claims:          {total_claims}")
    print(f"    Total cross-refs:      {total_xrefs}")
    print(f"{'='*60}")
    print(f"\n  NOTE: Run scripts/upgrade_bsb_evidence_tier.py to upgrade")
    print(f"  BSB-* claims from E3 to E1 (Sandstorm Report primary source).")


if __name__ == "__main__":
    main()
