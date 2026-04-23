#!/usr/bin/env python3
"""Ingest Wexner Dynasty intelligence reports into sherlock.db.

Registers 1 evidence source (WEX_DYNASTY_001), extracts ~100 claims
across all 9 phases of the Wexner Dynasty Campaign (PKG-EP Phase 4),
and creates ~30 cross-references connecting Wexner findings to existing targets.
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

# Single source for the entire Wexner Dynasty Campaign
SOURCE = {
    "source_id": "WEX_DYNASTY_001",
    "title": "Wexner Dynasty Intelligence Report (PKG-EP Phase 4)",
    "file_path": "evidence/wexner_research_phase9_mosaic.md",
    "evidence_type": "intelligence_report",
}

# =============================================================================
# CLAIMS — 100 claims across 9 phases (WEX-001 to WEX-100)
# Each: (claim_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    # =========================================================================
    # PHASE 1: Dynasty Foundation (WEX-001 to WEX-015)
    # =========================================================================
    ("WEX-001", "factual",
     "Leslie Herbert Wexner born September 8, 1937, Dayton, Ohio. Father Harry Louis Wexner (1899-1975) emigrated from Russia age ~13, fleeing Czarist persecution. Mother Bella Cabakoff (1908-2001) born Williamsburg, Brooklyn.",
     0.90, '["E1", "E2", "dynasty_foundation", "family_origins", "PKG-EP"]'),

    ("WEX-002", "factual",
     "The Limited, Inc. founded August 10, 1963 with $10,000 startup capital ($5K aunt loan + $5K bank loan) at Kingsdale Shopping Center, Columbus OH. First year revenue $162,000.",
     0.95, '["E1", "dynasty_foundation", "corporate_founding", "PKG-EP"]'),

    ("WEX-003", "factual",
     "The Limited IPO 1969 (47,600 shares at $7.25, OTC, 5 stores). NYSE listing 1982 (ticker: LTD). Revenue milestones: $1B (1984), $4B (1988), $6.1B (1991), peak ~$12.9B (2018).",
     0.95, '["E1", "dynasty_foundation", "corporate_growth", "PKG-EP"]'),

    ("WEX-004", "factual",
     "Wexner acquired Victoria's Secret in 1982 for $1 million (5 stores, $6M revenue, heading toward bankruptcy). Transformed to ~$1B revenue by 1992 (1,000x return in 10 years). Peak VS worldwide revenue $7.78B (2016). VS spun off August 2, 2021 as Victoria's Secret & Co. (NYSE: VSCO).",
     0.95, '["E1", "dynasty_foundation", "victorias_secret", "PKG-EP"]'),

    ("WEX-005", "factual",
     "Roy Larson Raymond founded Victoria's Secret June 12, 1977 (Stanford Shopping Center, Palo Alto). After selling to Wexner, filed bankruptcy 1986. Committed suicide August 26, 1993 (Golden Gate Bridge, age 46) — 7 months after Wexner's marriage to Abigail Koppel.",
     0.90, '["E1", "dynasty_foundation", "victorias_secret", "raymond_death", "PKG-EP"]'),

    ("WEX-006", "factual",
     "Wexner's subsidiary acquisition portfolio: Lane Bryant ($105M, 1982), Lerner New York ($297M, 1985), Henri Bendel (~$10M, 1985), Abercrombie & Fitch ($47M, 1988). A&F CEO Mike Jeffries (installed during Wexner ownership) arrested and indicted October 2024 on federal sex trafficking charges.",
     0.90, '["E1", "dynasty_foundation", "corporate_portfolio", "trafficking_parallel", "PKG-EP"]'),

    ("WEX-007", "factual",
     "Wexner Foundation established 1983. Heritage Program (1985), Graduate Fellowship (1988, ended 2023), Israel Fellowship (1989, ended 2024). Total Foundation assets $208M (2017 IRS filing). Total personal philanthropy $500M+.",
     0.95, '["E1", "dynasty_foundation", "wexner_foundation", "PKG-EP"]'),

    ("WEX-008", "factual",
     "Wexner Israel Fellowship at Harvard Kennedy School: 280+ alumni over 35 years in senior Israeli positions — Directors General of ministries, IDF generals/commanders, Supreme Court justices, ambassadors. 40 IDF/MoD, 3 Mossad, 3 Shin Bet alumni documented.",
     0.80, '["E1", "E2", "dynasty_foundation", "israel_fellowship", "intelligence_pipeline", "PKG-EP"]'),

    ("WEX-009", "factual",
     "Mega Group ('The Study Group') co-founded 1991 by Wexner and Charles Bronfman. ~20 initial members, nearly 50 by 2001. Annual dues ~$30,000, twice-yearly meetings. Confirmed members include Edgar Bronfman Sr., Michael Steinhardt, Ronald Lauder, Laurence Tisch, Lester Crown (General Dynamics), Max Fisher.",
     0.85, '["E1", "E2", "dynasty_foundation", "mega_group", "PKG-EP"]'),

    ("WEX-010", "factual",
     "January 1997: NSA intercepted Israeli embassy call to Mossad chief Danny Yatom referencing 'Mega' as intelligence source. Triggered CIA/FBI/NSA mole hunt; hunt abruptly terminated within days of going public (May 7, 1997). Former NSA counterspy John Schindler stated Israeli intelligence viewed Mega as 'a vehicle for espionage and influence operations.'",
     0.70, '["E1", "E2", "dynasty_foundation", "mega_group", "intelligence_operations", "PKG-EP"]'),

    ("WEX-011", "factual",
     "Wexner married Abigail S. Koppel January 23, 1993, age 55 (first marriage, lifelong bachelor). Her father Yehuda Koppel was Haganah commander (pre-state Israeli paramilitary). Epstein drafted the prenuptial agreement and worked with Abigail on nonprofit and business deals post-marriage.",
     0.85, '["E1", "E2", "dynasty_foundation", "marriage", "israel_connection", "PKG-EP"]'),

    ("WEX-012", "factual",
     "Wexner net worth trajectory: $4.4B (2012) to $9.1-10.8B (early 2026). CoreWeave investment: ~4% stake acquired 2017 for $1.6M, worth ~$3B at March 2025 IPO (~1,875x return). Consistently richest person in Ohio.",
     0.90, '["E1", "E2", "dynasty_foundation", "net_worth", "coreweave", "PKG-EP"]'),

    ("WEX-013", "factual",
     "Les + Abigail Wexner career political donations: $5.3M+ combined (state + federal). Historically Republican; Wexner publicly left GOP September 2018 ('I am no longer a Republican'). Has never donated to Trump, JD Vance, or Vivek Ramaswamy. Columbus Mayor Ginther is single largest recipient ($150K+).",
     0.90, '["E1", "dynasty_foundation", "political_donations", "PKG-EP"]'),

    ("WEX-014", "factual",
     "New Albany, OH: Co-founded ~1990 by Wexner and Jack Kessler (New Albany Company). Grew from 1,600 residents to 11,000+. Wexner estate: 336 acres, 45,000 sq ft Georgian mansion, 50-car garage. $235M state-funded highway interchange secured for New Albany.",
     0.90, '["E1", "E2", "dynasty_foundation", "new_albany", "institutional_capture", "PKG-EP"]'),

    ("WEX-015", "factual",
     "Leaked Epstein Yahoo inbox emails (2005-2008) show Epstein acting as de facto CFO for Wexner family office AND Foundation, directing grants to Hillel, Birthright Israel, Israel Fellowship scholarships, Jewish Media Fund ('Shalom Sesame'). Jan 2008: Epstein-controlled entities transferred ~$46M to YLK Charitable Fund (named for Yehuda Koppel, Haganah commander).",
     0.85, '["E1", "dynasty_foundation", "financial_control", "epstein_cfo", "PKG-EP"]'),

    # =========================================================================
    # PHASE 2: Organized Crime (WEX-016 to WEX-028)
    # =========================================================================
    ("WEX-016", "factual",
     "Francis 'Frank' Walsh Jr.'s Walsh Trucking handled 90%+ of The Limited's trucking. Walsh's entity 'Frank Walsh Financial Resources' registered at One Limited Parkway, Columbus — Wexner's corporate HQ address.",
     0.85, '["E1", "E2", "organized_crime", "walsh_trucking", "PKG-EP"]'),

    ("WEX-017", "factual",
     "March 31, 1988 federal RICO indictment by U.S. Attorney Samuel A. Alito Jr.: Walsh ran 'labor peace' payoff scheme with Genovese crime family. Co-defendants included Vincent 'Fish' Cafaro (Genovese soldier). Unindicted co-conspirators: Anthony 'Fat Tony' Salerno (Genovese boss) and Matthew 'Matty the Horse' Ianniello.",
     0.90, '["E1", "organized_crime", "walsh_rico", "salerno", "genovese", "PKG-EP"]'),

    ("WEX-018", "factual",
     "Walsh RICO conspiracy tied to Teamsters Local 560 — controlled by Genovese 'Provenzano Group.' Stephen Andretta (co-defendant) was also a suspect in Jimmy Hoffa's 1975 disappearance. Walsh pled guilty, sentenced to 4 years (1990).",
     0.85, '["E1", "E2", "organized_crime", "teamsters", "hoffa", "PKG-EP"]'),

    ("WEX-019", "factual",
     "Edward DeBartolo Sr. appeared on DOJ Organized Crime Principal Subjects List (1970). US Customs Agent Burda characterized DeBartolo as 'Lansky successor' (1981). Wexner and DeBartolo Sr. jointly bid for Carter Hawley Hale Stores ($55/share, 1984; second bid 1986).",
     0.90, '["E1", "E2", "organized_crime", "debartolo", "lansky", "PKG-EP"]'),

    ("WEX-020", "factual",
     "Arthur Shapiro, Wexner's attorney, murdered March 6, 1985 — professional hit, day before scheduled grand jury appearance. Berry Kessler identified as prime suspect; later convicted of separate contract killing (John Deroo murder, 1994).",
     0.80, '["E1", "organized_crime", "shapiro_murder", "PKG-EP"]'),

    ("WEX-021", "factual",
     "Columbus Police completed Shapiro homicide investigation memo (Elizabeth Leupp, June 6, 1991). Police Chief James Jackson ordered the memo destroyed. Bob Fitrakis obtained surviving copy via public records request (1998). Jackson charged with 'improper disposal of a public record' (1996).",
     0.75, '["E1", "E2", "organized_crime", "shapiro_memo", "evidence_destruction", "PKG-EP"]'),

    ("WEX-022", "factual",
     "Robert Morosky, The Limited president, 'abruptly and inexplicably' departed 1987 — same period Epstein was becoming Wexner's financial adviser. No public explanation for departure.",
     0.60, '["E2", "organized_crime", "morosky_departure", "PKG-EP"]'),

    ("WEX-023", "assessment",
     "The Walsh RICO-to-Wexner chain: Walsh trucking monopoly at Limited HQ → Walsh-Salerno Genovese conspiracy → Shapiro murder (Wexner attorney, pre-grand jury) → memo destruction by Columbus Police Chief → evidence suppression. Chain demonstrates organized crime penetration of Wexner's corporate infrastructure with local law enforcement complicity in cover-up.",
     0.70, '["E1", "E2", "organized_crime", "chain_analysis", "PKG-EP"]'),

    ("WEX-024", "factual",
     "Trump granted DeBartolo Jr. full presidential pardon February 18, 2020 — DeBartolo Jr.'s father was Wexner's joint bidding partner and DOJ Organized Crime Subjects List member.",
     0.95, '["E1", "organized_crime", "debartolo", "trump_pardon", "PKG-EP"]'),

    ("WEX-025", "factual",
     "Vincent Cafaro (Genovese soldier, Walsh co-defendant) became key government witness. Testified about 'fish fund' payoffs to Salerno. Entered witness protection. His cooperation accelerated the Mafia Commission Trial that convicted Salerno (100 years, 1986).",
     0.85, '["E1", "organized_crime", "cafaro_witness", "mafia_commission", "PKG-EP"]'),

    ("WEX-026", "assessment",
     "Roy Cohn bridge chain connecting organized crime to Epstein-Wexner axis: Cohn represented Salerno (Genovese) AND was Trump's attorney AND attended 1983 B'nai B'rith dinner with Ace Greenberg (Bear Stearns, Epstein's employer). Cohn died August 2, 1986 — same year Epstein met Wexner.",
     0.65, '["E1", "E2", "organized_crime", "cohn_bridge", "PKG-EP"]'),

    ("WEX-027", "factual",
     "1983 B'nai B'rith dinner honoring Roy Cohn (May 2): Ace Greenberg, Donald Trump, Rupert Murdoch, Ronald Lauder all present. This event places Epstein's Bear Stearns boss in direct documented social contact with Cohn's network.",
     0.90, '["E1", "organized_crime", "cohn_network", "greenberg", "PKG-EP"]'),

    ("WEX-028", "factual",
     "Max Fisher (Mega Group elder, Marathon Oil) has alleged but poorly documented Purple Gang connections (E3). Bronfman family liquor distribution through Purple Gang is better documented (E1 for Bronfman-Purple link). Fisher-Wexner mentorship widely asserted but details sparse.",
     0.40, '["E2", "E3", "organized_crime", "purple_gang", "fisher", "PKG-EP"]'),

    # =========================================================================
    # PHASE 3: Aircraft & CIA (WEX-029 to WEX-040)
    # =========================================================================
    ("WEX-029", "factual",
     "Southern Air Transport (SAT) founded 1947 Miami. CIA acquired August 5, 1960 for ~$300,000 under Pacific Corporation (alongside Air America, Air Asia, Civil Air Transport, Intermountain Aviation). CIA divested December 31, 1973 to Stanley G. Williams.",
     0.95, '["E1", "aircraft_cia", "sat_history", "PKG-EP"]'),

    ("WEX-030", "factual",
     "James H. Bastian — former CIA lawyer, secretary/VP/general counsel of Pacific Corporation (CIA airline holding) 1961-1974 — acquired SAT stakes January 1975 and October 1975 from Williams, gaining controlling interest by 1979. Classic CIA proprietary disposal: divest to insiders who maintained operational relationships.",
     0.85, '["E1", "E2", "aircraft_cia", "bastian", "cia_disposal", "PKG-EP"]'),

    ("WEX-031", "factual",
     "SAT carried 4 loads of US weapons from US to Israel for transshipment to Iran; return flights carried weapons for Contras from Portugal. October 5, 1986: SAT C-123K shot down over Nicaragua; crew member Eugene Hasenfus captured, exposing covert operations.",
     0.95, '["E1", "aircraft_cia", "iran_contra", "hasenfus", "PKG-EP"]'),

    ("WEX-032", "factual",
     "Kerry Committee (1987-88) found 'substantial evidence of drug smuggling on the part of individual Contras, Contra suppliers, Contra pilots.' SAT specifically cited among 'companies used to support the Contra program.'",
     0.90, '["E1", "aircraft_cia", "kerry_committee", "drug_smuggling", "PKG-EP"]'),

    ("WEX-033", "factual",
     "March 16, 1995: SAT announces relocation of world headquarters to Rickenbacker Airport, Columbus OH — 10 miles south of Wexner's Limited HQ. $46.5M state incentive package secured for the relocation.",
     0.90, '["E1", "aircraft_cia", "sat_columbus", "rickenbacker", "PKG-EP"]'),

    ("WEX-034", "factual",
     "Under Wexner's power of attorney (granted 1991), Epstein arranged SAT's Columbus relocation. Franklin County Sheriff and Ohio Inspector General identified Epstein as having 'pivotal role' in the arrangement.",
     0.75, '["E2", "aircraft_cia", "epstein_pivotal", "sat_relocation", "PKG-EP"]'),

    ("WEX-035", "factual",
     "SAT cargo mission from Columbus: flew products from Hong Kong/southern China to Rickenbacker for Limited Brands retail distribution network. Boeing 727 N908JE — ex-Limited Stores aircraft, later became Epstein's 'Lolita Express.'",
     0.85, '["E1", "E2", "aircraft_cia", "aircraft_transfer", "lolita_express", "PKG-EP"]'),

    ("WEX-036", "factual",
     "1996: Cocaine discovered on SAT aircraft at Rickenbacker Airport. SAT claimed shipment was 'fresh flowers' from Colombia. No prosecution resulted.",
     0.70, '["E2", "aircraft_cia", "cocaine_incident", "rickenbacker", "PKG-EP"]'),

    ("WEX-037", "factual",
     "October 1, 1998: SAT files Chapter 7 bankruptcy in Columbus — exactly one week before CIA Inspector General's cocaine report publication. Fleet reportedly sold to Transafrik International (Angola/UAE operations).",
     0.85, '["E1", "aircraft_cia", "sat_bankruptcy", "cia_timing", "PKG-EP"]'),

    ("WEX-038", "factual",
     "Ohio Inspector General David Sturtz dismissed 1994 — claimed dismissal connected to Wexner/SAT inquiry. Two simultaneous Ohio state investigations (Sheriff, Inspector General) into Wexner/Epstein/SAT suppressed before producing findings.",
     0.50, '["E2", "E3", "aircraft_cia", "investigation_suppression", "PKG-EP"]'),

    ("WEX-039", "assessment",
     "NEGATIVE FINDING: No evidence of SAT connection to Operation Gladio. No evidence of SAT connection to Operation Condor. Thorough search of declassified records, Congressional findings, and investigative journalism found no links.",
     0.90, '["E1", "aircraft_cia", "negative_finding", "gladio", "condor", "PKG-EP"]'),

    ("WEX-040", "factual",
     "December 2025: Drop Site News publishes 'Epstein, Israel, and the CIA' investigation detailing SAT-Columbus corridor, Stanley Pottinger's shared penthouse office with Epstein, and Iran arms embargo circumvention documentation.",
     0.80, '["E2", "aircraft_cia", "drop_site_news", "pottinger", "PKG-EP"]'),

    # =========================================================================
    # PHASE 4: Trafficking (WEX-041 to WEX-052)
    # =========================================================================
    ("WEX-041", "factual",
     "Epstein posed as Victoria's Secret model scout/talent recruiter to lure young women. Duration: 1993 through at least 2006 — documented incidents span 13+ years. Three L Brands executives told NYT that Wexner was informed in 1993 but failed to act.",
     0.85, '["E1", "E2", "trafficking", "vs_recruitment", "PKG-EP"]'),

    ("WEX-042", "factual",
     "Alicia Arden incident: May 20, 1997, Shutters on the Beach hotel, Santa Monica. Epstein told Arden he was VS model scout, groped her ('Let me manhandle you'). Santa Monica PD report filed. Earliest documented police report of Epstein using VS connection — 8 years before FL prosecution. No charges filed.",
     0.90, '["E1", "trafficking", "arden_police_report", "PKG-EP"]'),

    ("WEX-043", "factual",
     "1992: Melanie Walker encountered by Epstein at Plaza Hotel using VS recruitment pitch; Trump was present. Walker subsequently traveled to Thailand with Epstein and received career advancement. 2019-2025: Walker worked at Bill & Melinda Gates Foundation as science officer.",
     0.75, '["E1", "E2", "trafficking", "walker_recruitment", "PKG-EP"]'),

    ("WEX-044", "factual",
     "Maria Farmer sexually assaulted 1996 at Wexner's New Albany estate; held approximately 12 hours by armed security. Filed NYPD complaint August 29, 1996 — the first known criminal complaint about Epstein. FBI ignored complaint for over a decade.",
     0.85, '["E1", "trafficking", "maria_farmer", "new_albany", "PKG-EP"]'),

    ("WEX-045", "factual",
     "Annie Farmer (age 16) abused at Zorro Ranch, NM by Epstein and Maxwell (1996). Epstein acquired Zorro Ranch (~7,600 acres, ~$12M) in 1993 from former Governor Bruce King. FBI/SDNY never searched Zorro Ranch despite multiple victim testimonies.",
     0.85, '["E1", "trafficking", "zorro_ranch", "annie_farmer", "PKG-EP"]'),

    ("WEX-046", "factual",
     "Ed Razek (L Brands CMO, created VS Angels) presided over 'entrenched culture of misogyny, bullying, and harassment' per NYT 2020 investigation: tried to kiss 19-year-old model, told Bella Hadid 'Forget the panties,' touched model's crotch. Multiple HR complaints, no consequences.",
     0.85, '["E1", "E2", "trafficking", "razek_misconduct", "PKG-EP"]'),

    ("WEX-047", "factual",
     "2019: 100+ VS models signed open letter demanding sexual misconduct protections. February 2020: NYT investigation documents VS 'entrenched culture of misogyny.' VS brand functioned simultaneously as legitimate $7.78B enterprise and trafficking recruitment mechanism for 13+ documented years.",
     0.85, '["E1", "E2", "trafficking", "brand_as_weapon", "PKG-EP"]'),

    ("WEX-048", "factual",
     "Jean-Luc Brunel (model scout with Epstein connections) found hanged in French prison cell February 19, 2022; had been charged with rape of minors. Brunel operated MC2 Model Management with Epstein funding.",
     0.90, '["E1", "trafficking", "brunel_death", "PKG-EP"]'),

    ("WEX-049", "factual",
     "2026: NM House unanimously passes Epstein Truth Commission (HR 1). NM AG reopens Zorro Ranch criminal investigation. Wexner's New Albany estate — site of documented Maria Farmer assault and captivity — was never searched by FBI or any law enforcement agency.",
     0.90, '["E1", "trafficking", "nm_commission", "investigation_failure", "PKG-EP"]'),

    ("WEX-050", "assessment",
     "NEGATIVE FINDING: No evidence of Mexico-specific trafficking through Wexner entities. No evidence of narcotics transiting through Rickenbacker Airport in law enforcement records. No evidence Wexner personally visited Zorro Ranch.",
     0.85, '["E1", "trafficking", "negative_finding", "PKG-EP"]'),

    ("WEX-051", "factual",
     "Virginia Giuffre testified under oath that Wexner was among men she was trafficked to. 2011 FBI interview report references 'erotic massage to Leslie Wexner in New York.' Wexner denies all allegations.",
     0.70, '["E1", "trafficking", "giuffre_testimony", "PKG-EP"]'),

    ("WEX-052", "factual",
     "August 15, 2019: FBI internally labels Wexner 'co-conspirator' with note 'limited evidence.' January-February 2026: FBI co-conspirator designation becomes public in unredacted documents. Rep. Ro Khanna reads Wexner's name on House floor (February 10, 2026). No criminal charges ever filed.",
     0.90, '["E1", "trafficking", "co_conspirator", "no_charges", "PKG-EP"]'),

    # =========================================================================
    # PHASE 5: Iran-Contra / Bear Stearns Bridge (WEX-053 to WEX-065)
    # =========================================================================
    ("WEX-053", "factual",
     "Epstein's 'gap years' 1981-1986: Left Bear Stearns March 12, 1981 (one day after SEC opens insider-trading inquiry). Founded Intercontinental Assets Group (IAG), NYC. Worked with Douglas Leese (British arms dealer) in London 1982-84. Bermuda shell companies for China-Iran arms deals.",
     0.80, '["E1", "E2", "iran_contra", "gap_years", "arms_dealing", "PKG-EP"]'),

    ("WEX-054", "factual",
     "Austrian passport issued to Epstein May 21, 1982 under name 'Marius Fortelni' with Saudi Arabia address. E1 evidence from SDNY court filings (2019 raid). Indicates intelligence service involvement in credentialing.",
     0.90, '["E1", "iran_contra", "austrian_passport", "intelligence_tradecraft", "PKG-EP"]'),

    ("WEX-055", "factual",
     "Robert Meister (Aon VP, insurance executive) introduced Epstein to Wexner circa 1985-86 via airplane meeting in Palm Beach. No intelligence background found for Meister (negative finding). Harold Levin (Wexner's prior financial adviser) warned: 'I smell a rat' — warning ignored, Levin displaced.",
     0.80, '["E2", "iran_contra", "meister_introduction", "levin_warning", "PKG-EP"]'),

    ("WEX-056", "factual",
     "Ace Greenberg hired Epstein at Bear Stearns 1976. Epstein became limited partner 1980. Greenberg-Roy Cohn friendship documented (1983 B'nai B'rith dinner). Greenberg maintained relationship with Epstein post-Bear Stearns departure.",
     0.85, '["E1", "iran_contra", "bear_stearns", "greenberg", "cohn", "PKG-EP"]'),

    ("WEX-057", "factual",
     "July 1991: Wexner grants Epstein power of attorney — extraordinary control over financial affairs maintained for 16 years with no apparent oversight. Epstein's personal notes: 'never ever, did anything without informing les.'",
     0.90, '["E1", "iran_contra", "power_of_attorney", "financial_control", "PKG-EP"]'),

    ("WEX-058", "factual",
     "Stanley Pottinger shared penthouse office with Epstein in early 1980s. Pottinger identified in 1984 federal indictment against Cyrus Hashemi for Iran arms embargo circumvention. Epstein-Pottinger partnership documented at same time as Iran arms dealing.",
     0.75, '["E1", "E2", "iran_contra", "pottinger", "arms_embargo", "PKG-EP"]'),

    ("WEX-059", "factual",
     "Lynn Forester sold Manhattan townhouse to Epstein-linked entity $8.5M below market value (2000). Forester joined Deutsche Bank advisory board July 2013; Deutsche Bank takes on Epstein as client one month later.",
     0.85, '["E1", "iran_contra", "forester_rothschild", "financial_bridge", "PKG-EP"]'),

    ("WEX-060", "factual",
     "Epstein signed $25M agreement with Edmond de Rothschild Holding S.A. for 'risk analysis' (2015). Epstein emailed Peter Thiel February 2016: 'As you probably know I represent the Rothschilds.' FBI seized Epstein's 'Little Black Book' (2005) which includes Evelyn and Edouard de Rothschild.",
     0.85, '["E1", "iran_contra", "rothschild", "financial_network", "PKG-EP"]'),

    ("WEX-061", "factual",
     "Epstein hired by Steven Hoffenberg as Towers Financial consultant ($25K/month, 1987). $462M Ponzi scheme. Hoffenberg convicted; claimed Epstein was equal partner. Hoffenberg is sole source for BCCI-Epstein direct link — convicted fraudster's uncorroborated claim.",
     0.70, '["E1", "E2", "iran_contra", "hoffenberg", "towers_financial", "PKG-EP"]'),

    ("WEX-062", "assessment",
     "NEGATIVE FINDING: No BCCI branch, office, or subsidiary in Columbus, Ohio. No BCCI-Wexner direct connection found. BCCI-Epstein direct link rests on Hoffenberg's uncorroborated claim (0.20 confidence).",
     0.85, '["E1", "iran_contra", "negative_finding", "bcci", "PKG-EP"]'),

    ("WEX-063", "factual",
     "Epstein recovered Ana Obregon's father's bonds from Cayman Islands (1982) — demonstrating offshore financial operations capability during gap years. Lived part-time in London working with arms dealer Douglas Leese.",
     0.70, '["E2", "iran_contra", "gap_years", "offshore", "PKG-EP"]'),

    ("WEX-064", "factual",
     "Wexner emailed Epstein post-2008 plea deal: 'You violated your own number 1 rule... always be careful.' This implies Wexner understood Epstein's risk-taking behavior and counseled operational security, not cessation of activities.",
     0.85, '["E1", "iran_contra", "always_be_careful", "operational_security", "PKG-EP"]'),

    ("WEX-065", "factual",
     "Wexner's attorneys claim Epstein repaid $100M — 'just a portion of what he stole.' Despite claiming massive theft, Wexner NEVER filed criminal charges against Epstein for embezzlement. Absence of filing is strongest indicator both men had reasons to avoid legal discovery.",
     0.85, '["E1", "iran_contra", "no_criminal_charges", "financial_control", "PKG-EP"]'),

    # =========================================================================
    # PHASE 6: Science/Intel Programs (WEX-066 to WEX-076)
    # =========================================================================
    ("WEX-066", "factual",
     "OSU total giving: ~$200M (personal + family + Limited Brands Foundation). Wexner Medical Center naming: $100M commitment ($65M Wexner + $35M Limited Brands Foundation, 2011). Board of Trustees: 1988-1997, reappointed 2005, Chair 2009, stepped down June 2012 (8 years early).",
     0.95, '["E1", "science_intel", "osu", "institutional_capture", "PKG-EP"]'),

    ("WEX-067", "factual",
     "OSU confirmed February 2026: no contracts tying building names to Wexner donations — naming is 'honorific.' ~295 removal requests received. OSU 'reviewing' but taking no action. Wexner Center for Arts, Medical Center, football facility all bear his name.",
     0.95, '["E1", "science_intel", "osu_naming", "reputational_hostage", "PKG-EP"]'),

    ("WEX-068", "factual",
     "Harvard Kennedy School: $42M+ via Wexner Foundation. Israel Fellowship partnership (1989-2024). Building naming. Wexner Foundation severed Harvard ties October 2023 citing 'dismal failure' on Oct 7 response — convenient timing before congressional scrutiny of Epstein intensified 2024-2026.",
     0.85, '["E1", "science_intel", "harvard", "institutional_access", "PKG-EP"]'),

    ("WEX-069", "factual",
     "Wexner Foundation paid Ehud Barak ~$2.3M (2004-2006) for two research studies (one never completed). Epstein personally authorized the Barak payment per leaked emails. Barak introduced to Epstein by Shimon Peres (2003). Barak and Epstein subsequently invested in Carbyne 911 (Unit 8200-derived surveillance tech, acquired by Axon 2025 for $625M).",
     0.85, '["E1", "science_intel", "barak", "carbyne", "unit_8200", "PKG-EP"]'),

    ("WEX-070", "factual",
     "Israeli government installed surveillance/security equipment at 301 East 66th St (acquired by Mark Epstein from Wexner). Rafi Shlomo (Israel UN mission protective services director, Barak security detail head) controlled apartment access. System included window sensors and remote access.",
     0.85, '["E1", "science_intel", "israel_surveillance", "barak_apartment", "PKG-EP"]'),

    ("WEX-071", "factual",
     "Epstein as Wexner Foundation trustee (1992-2007) controlled funding to Israeli government leadership pipeline. Epstein's $9.1M in Harvard donations (1998-2008). $6.5M to Harvard Program for Evolutionary Dynamics (Martin Nowak, 2003). Epstein had personal office in Nowak's lab for 9 years.",
     0.90, '["E1", "science_intel", "harvard_ped", "nowak", "PKG-EP"]'),

    ("WEX-072", "factual",
     "Epstein paid OSU OB-GYN Dr. Mark Landon $75K/year for 'biotech consulting' (2001-2005) at the Wexner Medical Center during Epstein's documented eugenics-interest period. Nature of consulting work remains unexplained.",
     0.80, '["E1", "science_intel", "landon_payments", "eugenics", "PKG-EP"]'),

    ("WEX-073", "factual",
     "Leon Black (Apollo Global Management) paid Epstein $158-170M in fees (2012-2017). Senate Finance Committee revealed $170M figure (2025). Second financial pillar after Wexner. Both contributed to Epstein's 50th birthday book. Black retired as Apollo CEO July 2021.",
     0.90, '["E1", "science_intel", "leon_black", "apollo", "PKG-EP"]'),

    ("WEX-074", "factual",
     "Epstein funded 74% of Edge Foundation ($638K of $857K total, 2001-2015). Edge/Brockman facilitated Epstein's access to Bezos, Brin, and tech elite. MIT Media Lab received $525K directly from Epstein + $7.5M channeled (Black $5M+, Gates $2M). Joi Ito resigned.",
     0.85, '["E1", "science_intel", "edge_foundation", "mit_media_lab", "PKG-EP"]'),

    ("WEX-075", "factual",
     "Epstein August 2012 emails seeking 'NSA codebreakers' for genome research. Epstein expressed transhumanist/eugenics interests: wanted to 'seed the human race' with his DNA, fund cryogenics, establish baby ranch in New Mexico (NYT 2019 reporting).",
     0.80, '["E1", "E2", "science_intel", "eugenics", "transhumanism", "PKG-EP"]'),

    ("WEX-076", "factual",
     "Jeffrey Epstein VI Foundation established 2000 (Little Saint James, USVI). Epstein hosted 'Confronting Gravity' symposium 2006 (St. Thomas) with Nobel laureates. Science network served prestige-acquisition function; no personnel overlap with classified Puthoff/Bigelow/AAWSAP research ecosystem.",
     0.85, '["E1", "science_intel", "gravity_symposium", "prestige_network", "PKG-EP"]'),

    # =========================================================================
    # PHASE 7: Trump/Political (WEX-077 to WEX-087)
    # =========================================================================
    ("WEX-077", "factual",
     "Wexner purchased 9 East 71st Street (Manhattan townhouse) for $13.2M in 1989 from Birch Wathen School. Epstein occupied the property from 1995. Epstein formally purchased for $20M total ($10M initial) in 1998. 2011: ownership transferred from joint Wexner-Epstein trust to Epstein-only trust (Maple Inc.). Sold 2021 for ~$51M to Goldman Sachs exec.",
     0.95, '["E1", "trump_political", "townhouse_transfer", "9_east_71st", "PKG-EP"]'),

    ("WEX-078", "factual",
     "Howard Lutnick purchased 11 East 71st Street (adjacent to Epstein) in 1998 through SAM Conversion Corp. — Columbus OH address linking to Wexner/Epstein entity chain. Lutnick visited Epstein's island December 2012 with family; signed Adfin business deal December 28, 2012.",
     0.90, '["E1", "trump_political", "lutnick", "11_east_71st", "entity_chain", "PKG-EP"]'),

    ("WEX-079", "factual",
     "Lutnick testified he cut ties with Epstein in 2005. DOJ files prove island visit 2012 and business relationship through 2014. Documented perjury risk. Lutnick raised $75M+ for Trump 2024 campaign, confirmed Commerce Secretary February 2025.",
     0.95, '["E1", "trump_political", "lutnick_contradiction", "commerce_secretary", "PKG-EP"]'),

    ("WEX-080", "factual",
     "Trump-Epstein documented interactions: 7+ flights on Epstein jets (1993-97, Maxwell trial evidence). 1997 VS Angels party together. 1999 VS fashion event filmed laughing. Trump's 2002 NY Magazine quote: Epstein 'likes beautiful women... many of them are on the younger side.'",
     0.90, '["E1", "trump_political", "trump_epstein", "flights", "PKG-EP"]'),

    ("WEX-081", "factual",
     "Wexner's February 18, 2026 congressional deposition (~5 hours at New Albany mansion): claimed 'duped by world-class con man.' House Democrats accused Wexner of lying (February 20). No Republican members attended the deposition.",
     0.90, '["E1", "trump_political", "deposition_2026", "PKG-EP"]'),

    ("WEX-082", "factual",
     "Ronald Lauder: Mega Group member, Roy Cohn friend, Trump's 50-year friendship, WJC president. Served as US Ambassador to Austria 1986-87 — providing Austrian passport issuance context for Epstein's 'Marius Fortelni' passport (May 1982 issuance, but Lauder-Austria connection relevant).",
     0.75, '["E1", "E2", "trump_political", "lauder", "austria", "PKG-EP"]'),

    ("WEX-083", "factual",
     "Mega Group political operations: Sheldon/Miriam Adelson $500M+ to GOP/Trump ($100M to Trump 2024). Frank Luntz consulting contract (2003) for pro-Israel messaging. Multiple members on WINEP board. Birthright Israel co-founded 1999 by Bronfman + Steinhardt.",
     0.85, '["E1", "E2", "trump_political", "mega_group_politics", "adelson", "PKG-EP"]'),

    ("WEX-084", "factual",
     "Alexander Acosta (US Attorney) granted Epstein sweetheart plea deal 2008: 13 months county jail with work release, immunity for co-conspirators. Acosta appointed Trump's Secretary of Labor 2017. Resigned 2019 amid renewed Epstein scrutiny.",
     0.95, '["E1", "trump_political", "acosta_plea_deal", "labor_secretary", "PKG-EP"]'),

    ("WEX-085", "factual",
     "DOJ begins releasing Epstein files per Epstein Files Transparency Act (December 2025). January 2026: 3.5M+ pages released including 180,000+ images, 2,000+ videos. February 2026: Prince Andrew arrested in UK.",
     0.90, '["E1", "trump_political", "epstein_files", "prince_andrew", "PKG-EP"]'),

    ("WEX-086", "factual",
     "February 2026 Ohio political fallout: 8 of 39 Ohio politicians announced donation redirection after Wexner co-conspirator designation. Senator Bernie Moreno, Mayor Ginther, Lt. Gov. Husted refused or stayed silent. Multiple scrambling to distance.",
     0.85, '["E1", "E2", "trump_political", "ohio_fallout", "PKG-EP"]'),

    ("WEX-087", "factual",
     "Rep. Jesus Garcia: 'There is no single person that was more involved in providing Jeffrey Epstein with the financial support to commit his crimes than Les Wexner.' Congressional record, February 2026.",
     0.90, '["E1", "trump_political", "garcia_statement", "financial_support", "PKG-EP"]'),

    # =========================================================================
    # PHASE 8: Occult (WEX-088 to WEX-092)
    # =========================================================================
    ("WEX-088", "factual",
     "Little Saint James temple structure: Permitted 2010 as 3,500 sq ft 'music pavilion.' Actual construction deviated significantly — rectangular, ~30ft tall, no windows, no stone exterior, false wooden door. Golden dome added 2013-14; blue stripes painted after Oct 2012; dome destroyed by Hurricane Irma/Maria (2017).",
     0.90, '["E1", "E2", "occult_claims", "lsj_temple", "PKG-EP"]'),

    ("WEX-089", "factual",
     "Temple interior (FBI August 2019 search): Zodiac-themed ceiling murals, framed photograph of Pope John Paul II, rotting mattresses, empty bookcases, small bathroom with toilet and shower. NO sacrificial altars, NO pentagrams, NO ritual paraphernalia found in 3.5M-page DOJ release.",
     0.90, '["E1", "occult_claims", "temple_interior", "negative_finding", "PKG-EP"]'),

    ("WEX-090", "factual",
     "Maria Farmer account: Described artwork at Wexner estate and Epstein properties including themes of death, sex, violence. Called Wexner 'The Head of the Snake' (single-source interview claim, E3). Testified about sexual assault at Wexner New Albany estate (E1 — criminal complaint filed).",
     0.70, '["E1", "E3", "occult_claims", "maria_farmer", "PKG-EP"]'),

    ("WEX-091", "assessment",
     "REJECT: All claims of satanic rituals, Moloch worship, adrenochrome harvesting, and child sacrifice at LSJ or Wexner properties. These originate from QAnon-adjacent forums and social media. Zero primary-source evidence in court filings, FBI records, or 3.5M-page Epstein files release. 12 specific claims debunked.",
     0.95, '["E1", "occult_claims", "rejected_claims", "qanon_debunked", "PKG-EP"]'),

    ("WEX-092", "assessment",
     "The temple structure's actual purpose remains genuinely unknown. Physical evidence (mattresses, shower, no windows, massive walls, false door) combined with its remote island location is consistent with a private space designed for exploitation with maximum privacy. Intelligence assessment: mundane but sinister, not supernatural.",
     0.75, '["E1", "E2", "occult_claims", "temple_assessment", "PKG-EP"]'),

    # =========================================================================
    # PHASE 9: MOSAIC Synthesis (WEX-093 to WEX-100)
    # =========================================================================
    ("WEX-093", "assessment",
     "MOSAIC H1 (Unwitting dupe): Confidence 0.10-0.15 (VERY LOW). Requires accepting that a billionaire retail genius who built a $12.9B empire failed to notice 20+ years of warnings, executive reports, financial transfers, and media coverage. Documented evidence overwhelmingly contradicts this narrative.",
     0.85, '["analytical", "mosaic", "hypothesis_h1", "PKG-EP"]'),

    ("WEX-094", "assessment",
     "MOSAIC H2 (Witting financial enabler): Confidence 0.55-0.65 (MODERATE-HIGH). Best fits documented evidence. Wexner provided financial fuel, institutional infrastructure, and VS brand that Epstein exploited. Received: financial management, elite network access, Israeli government connections. Relationship was SYMBIOTIC. Never filing criminal charges for alleged $100M+ theft is strongest indicator both had reasons to avoid legal discovery.",
     0.85, '["analytical", "mosaic", "hypothesis_h2", "PKG-EP"]'),

    ("WEX-095", "assessment",
     "MOSAIC H3 (Intelligence participant): Confidence 0.30-0.40 (LOW-MODERATE). Supported by: SAT relocation, Mega Group, Israel Fellowship (280+ government alumni), Barak payments/Carbyne, Austrian passport, Pottinger partnership, suppressed Ohio investigations. Lacks documentary proof of direct intelligence tasking.",
     0.75, '["analytical", "mosaic", "hypothesis_h3", "intelligence", "PKG-EP"]'),

    ("WEX-096", "assessment",
     "MOSAIC H4 (Directing principal): Confidence 0.15-0.25 (LOW). Epstein's note 'never ever, did anything without informing les' is key but could reflect patron deference rather than operational orders. Overweights financial dependency while underweighting Epstein's extensive independent operations post-2007.",
     0.70, '["analytical", "mosaic", "hypothesis_h4", "PKG-EP"]'),

    ("WEX-097", "assessment",
     "MOSAIC composite: Most probable reality is HYBRID of H2 and H3 elements. Wexner was witting financial enabler whose institutional infrastructure served intelligence-adjacent functions both men understood. Relationship was one of MUTUAL BENEFIT with ASYMMETRIC KNOWLEDGE — Wexner knew enough to benefit but maintained plausible deniability about specifics.",
     0.80, '["analytical", "mosaic", "composite_assessment", "PKG-EP"]'),

    ("WEX-098", "assessment",
     "INSTITUTIONAL CAPTURE finding: Wexner achieved FULL capture of OSU (~$200M, Board membership, naming rights), Harvard Kennedy School ($42M+, Israel Fellowship), and Columbus political apparatus ($5.3M+, $235M highway). TOTAL capture of New Albany (co-founded the town). VS brand functioned as recruitment mechanism. No institution had mechanisms to evaluate donor's criminal connections.",
     0.85, '["analytical", "mosaic", "institutional_capture", "PKG-EP"]'),

    ("WEX-099", "assessment",
     "UNIQUE FINDING — Brand-as-weapon: Victoria's Secret is the first documented case of a major consumer brand ($7.78B peak revenue) weaponized as a trafficking recruitment tool for 13+ years. This dual-use architecture — providing both commercial revenue and predatory access — is the defining innovation of the Wexner-Epstein partnership. No parallel exists in Sherlock's dynasty database.",
     0.80, '["analytical", "mosaic", "brand_as_weapon", "unique_finding", "PKG-EP"]'),

    ("WEX-100", "assessment",
     "ARCHITECTURE OF IMPUNITY: The Wexner-Epstein case documents how American institutional governance, financial regulation, law enforcement, and political accountability are structurally incapable of holding a sufficiently wealthy individual accountable for complicity. Every level failed — Columbus PD (memo destruction), Ohio IG (suppressed), FBI (decade-long inaction on Farmer complaint), DOJ (sweetheart plea, no Zorro search), SEC (no inquiry into $1B+ transfers), Congress (partisan non-attendance at deposition).",
     0.85, '["analytical", "mosaic", "architecture_of_impunity", "system_failure", "PKG-EP"]'),
]

# =============================================================================
# CROSS-REFERENCES — ~30 connecting Wexner findings to existing targets/claims
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    # Wexner <-> Epstein core relationship
    ("xref_wex_001", "Wexner Power of Attorney (1991-2007)", "Epstein Financial Control Architecture",
     "principal_agent_relationship", "WEX-057,WEX-015,WEX-065", 0.90),

    ("xref_wex_002", "Wexner 'always be careful' email", "Epstein Operational Security",
     "knowledge_indicator", "WEX-064,WEX-057", 0.85),

    ("xref_wex_003", "Wexner VS Brand", "Epstein Trafficking Recruitment (13+ years)",
     "brand_as_weapon", "WEX-041,WEX-042,WEX-047,WEX-099", 0.85),

    # Wexner <-> Roy Cohn network
    ("xref_wex_004", "Wexner/Walsh/Salerno Chain", "Roy Cohn Genovese Representation",
     "organized_crime_bridge", "WEX-017,WEX-026,WEX-027", 0.70),

    ("xref_wex_005", "1983 B'nai B'rith Dinner (Cohn/Greenberg/Trump)", "Epstein Bear Stearns Hiring (1976)",
     "network_node_connection", "WEX-027,WEX-056", 0.80),

    ("xref_wex_006", "Roy Cohn Death (August 1986)", "Epstein-Wexner Introduction (1985-86)",
     "temporal_succession", "WEX-026,WEX-055", 0.65),

    # Wexner <-> Bear Stearns/BCCI
    ("xref_wex_007", "Wexner-Bear Stearns Client Relationship", "Bear Stearns BCCI Connection (Sandstorm Report)",
     "institutional_bridge", "WEX-056,BSB-001,BSB-002", 0.75),

    ("xref_wex_008", "Epstein Bear Stearns Departure (1981)", "Epstein Gap Years Arms Dealing",
     "career_transition_to_intelligence", "WEX-053,WEX-054,WEX-058", 0.70),

    ("xref_wex_009", "BCCI-Wexner Direct Connection", "NEGATIVE FINDING — No Columbus BCCI Presence",
     "negative_finding", "WEX-062", 0.85),

    # Wexner <-> Israeli Intelligence
    ("xref_wex_010", "Wexner Israel Fellowship (280+ alumni)", "Israeli Intelligence Community Penetration",
     "soft_power_pipeline", "WEX-008,WEX-070", 0.80),

    ("xref_wex_011", "Mega Group NSA Intercept (1997)", "Wexner Foundation Israel Fellowship Pipeline",
     "intelligence_nexus", "WEX-010,WEX-009", 0.65),

    ("xref_wex_012", "Wexner Foundation Barak Payments ($2.3M)", "Carbyne 911 Unit 8200 Investment",
     "financial_to_intelligence_bridge", "WEX-069,WEX-070", 0.85),

    ("xref_wex_013", "Israeli Surveillance Equipment at Barak Apartment", "Wexner Property Chain (301 E. 66th)",
     "physical_infrastructure_intelligence", "WEX-070", 0.85),

    # Wexner <-> Existing Epstein claims in DB
    ("xref_wex_014", "Wexner Financial Enablement (>$1B)", "Epstein Global Trafficking Network",
     "financial_architecture", "WEX-065,WEX-057,WEX-094", 0.85),

    ("xref_wex_015", "Wexner Boeing 727 Transfer", "Epstein 'Lolita Express' (N908JE)",
     "aircraft_provenance", "WEX-035", 0.90),

    ("xref_wex_016", "Wexner SAT Relocation to Rickenbacker", "CIA Proprietary Airline Infrastructure",
     "intelligence_logistics", "WEX-033,WEX-034,WEX-029", 0.80),

    # Wexner <-> Howard Lutnick
    ("xref_wex_017", "Wexner/Epstein Entity Chain (SAM Conversion Corp)", "Lutnick 11 E. 71st Purchase",
     "property_entity_chain", "WEX-078,LXR-001", 0.90),

    ("xref_wex_018", "Wexner 9 E. 71st Transfer Chain", "Lutnick Adjacent Property Purchase (1998)",
     "real_estate_nexus", "WEX-077,WEX-078", 0.85),

    # Wexner <-> Organized Crime / Shapiro Murder
    ("xref_wex_019", "Shapiro Murder (1985) and Memo Destruction", "Walsh RICO / Genovese Connection",
     "evidence_suppression_chain", "WEX-020,WEX-021,WEX-017", 0.70),

    ("xref_wex_020", "DeBartolo Sr. DOJ Organized Crime List", "Trump DeBartolo Jr. Pardon (2020)",
     "political_protection_chain", "WEX-019,WEX-024", 0.80),

    # Wexner <-> Institutional Capture
    ("xref_wex_021", "Wexner OSU Institutional Capture ($200M)", "Harvard Kennedy School Capture ($42M+)",
     "parallel_institutional_capture", "WEX-066,WEX-068,WEX-098", 0.85),

    ("xref_wex_022", "Wexner Columbus Political Machine ($5.3M+)", "Ohio Investigation Suppression Pattern",
     "political_protection_infrastructure", "WEX-013,WEX-038,WEX-021", 0.75),

    # Wexner <-> Existing Phase 2 cross-references
    ("xref_wex_023", "Wexner Phase 4 Findings", "Webb Phase 2 Reliability Assessment",
     "validation_and_extension", "WEX-094,WW5-001,WW1-007", 0.80),

    ("xref_wex_024", "Wexner-Epstein POA Documentation", "Webb Wexner Financial Control Claims",
     "source_corroboration", "WEX-057,WW1-007", 0.85),

    # Wexner <-> Science/Technology network
    ("xref_wex_025", "Leon Black $170M to Epstein", "Wexner as First Financial Pillar",
     "parallel_financial_patronage", "WEX-073,WEX-065", 0.85),

    ("xref_wex_026", "Epstein Harvard PED ($6.5M)", "Wexner Foundation Harvard Pipeline ($42M+)",
     "institutional_access_amplification", "WEX-071,WEX-068", 0.80),

    # Wexner <-> Trafficking victims
    ("xref_wex_027", "Maria Farmer Assault at Wexner Estate (1996)", "FBI Decade-Long Inaction",
     "justice_system_failure", "WEX-044,WEX-052", 0.85),

    ("xref_wex_028", "Zorro Ranch Never Searched by FBI", "NM Epstein Truth Commission (2026)",
     "belated_accountability", "WEX-045,WEX-049", 0.85),

    # Wexner <-> MOSAIC unique findings
    ("xref_wex_029", "VS Brand-as-Weapon (Unique Finding)", "No Dynasty Parallel in Sherlock DB",
     "unprecedented_mechanism", "WEX-099,WEX-047", 0.80),

    ("xref_wex_030", "Architecture of Impunity (System Failure)", "Existing Epstein Institutional Protection Pattern",
     "structural_parallel", "WEX-100,ICX-003,WW1-018", 0.75),
]


def ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.utcnow().isoformat()

    sources_added = 0
    claims_added = 0
    claims_skipped = 0
    xrefs_added = 0
    xrefs_skipped = 0

    # ---- Register source ----
    c.execute("SELECT source_id FROM evidence_sources WHERE source_id = ?",
              (SOURCE["source_id"],))
    if c.fetchone():
        print(f"SKIP source {SOURCE['source_id']}: already exists")
    else:
        c.execute("""
            INSERT INTO evidence_sources
                (source_id, title, file_path, evidence_type, created_at, ingested_at, processing_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, 'complete', ?)
        """, (
            SOURCE["source_id"],
            SOURCE["title"],
            SOURCE["file_path"],
            SOURCE["evidence_type"],
            now, now,
            json.dumps({
                "campaign": "PKG-EP",
                "phase": 4,
                "sub_phases": "1-9",
                "description": "Wexner Dynasty Campaign — 9-phase MOSAIC synthesis covering dynastic foundation, organized crime, aircraft/CIA, trafficking, Iran-Contra, science/intel, Trump/political, occult claims, and capstone assessment",
                "total_data_points": 935,
                "evidence_distribution": {"E1": "42%", "E2": "36%", "E3": "18%", "REJECT": "12 claims"},
                "negative_findings": 47,
            })
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

    # Wexner-specific counts
    c.execute("SELECT COUNT(*) FROM evidence_claims WHERE claim_id LIKE 'WEX-%'")
    wex_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references WHERE xref_id LIKE 'xref_wex_%'")
    wex_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"WEXNER DYNASTY INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Sources added this run:  {sources_added}")
    print(f"  Claims added this run:   {claims_added}")
    print(f"  Claims skipped (dupes):  {claims_skipped}")
    print(f"  Xrefs added this run:    {xrefs_added}")
    print(f"  Xrefs skipped (dupes):   {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  WEXNER CAMPAIGN TOTALS:")
    print(f"    WEX-* claims in DB:    {wex_claims}")
    print(f"    xref_wex_* in DB:      {wex_xrefs}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total sources:         {total_sources}")
    print(f"    Total claims:          {total_claims}")
    print(f"    Total cross-refs:      {total_xrefs}")
    print(f"{'='*60}")


if __name__ == "__main__":
    ingest()
