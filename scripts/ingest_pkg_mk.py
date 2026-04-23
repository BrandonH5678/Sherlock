#!/usr/bin/env python3
"""Ingest PKG-MK campaign evidence into sherlock.db.

Registers 12 evidence sources (one per phase report), extracts ~230 claims
(MK-001 to MK-230), and creates ~80 cross-references connecting findings
within the campaign and to existing Sherlock evidence.

Campaign: PKG-MK (CIA Behavioral Control Programs)
Phases: 1 (Taxonomy), 2 (Synanon), 3 (Cohen Nexus), 4 (Chavez/UFW),
        5 (Labor/Civil Rights), 6 (COINTELPRO Relationship),
        7 (Human Potential Movement), 8 (Jolyon West), 9 (Straight Inc.),
        10 (Peoples Temple), 11 (MOSAIC Synthesis), 12 (Cross-Campaign)
"""
import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = "/home/johnny5/Sherlock/sherlock.db"

# =============================================================================
# SOURCES — 12 phase reports
# =============================================================================

SOURCES = [
    {
        "source_id": "PKG_MK_PHASE1",
        "title": "PKG-MK Phase 1: MK Program Taxonomy and Behavioral Modification Subprojects",
        "file_path": "evidence/mk_research_phase1_taxonomy.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 1,
            "description": "Full taxonomy of CIA behavioral control programs 1950-1973: Bluebird, Artichoke, MK-Ultra, MK-SEARCH. Maps 25-30 behavioral modification subprojects, 7 core techniques, 12+ key researchers, institutional nodes.",
            "key_finding": "7 core behavioral modification techniques identified with documented transfer potential to civilian programs. Transfer primarily B-type (structural) rather than A-type (direct personnel).",
        },
    },
    {
        "source_id": "PKG_MK_PHASE2",
        "title": "PKG-MK Phase 2: Synanon Intelligence Report",
        "file_path": "evidence/mk_research_phase2_synanon.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 2,
            "description": "Synanon from addiction treatment to authoritarian cult. Dederich LSD origin event, the Game methodology, 8 MK technique parallels, elite patronage network, violent period.",
            "key_finding": "Dederich LSD session Aug 28, 1957 administered by Cohen/Ditman (E1). Dederich acknowledged brainwashing (E1, 0.95). 8 MK technique parallels documented.",
        },
    },
    {
        "source_id": "PKG_MK_PHASE3",
        "title": "PKG-MK Phase 3: Dr. Sidney Cohen & the UCLA LSD Nexus",
        "file_path": "evidence/mk_research_phase3_cohen_nexus.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 3,
            "description": "Cohen biographical profile, UCLA LSD program, CIA connection analysis, Bill Wilson AA session, Dederich session, Huxley network, institutional network mapping.",
            "key_finding": "Cohen likely independent researcher (0.55-0.60), not witting CIA asset. VA Wadsworth Hospital setting cannot be cleared. Cohen Collection at UCLA is unexamined intelligence gap.",
        },
    },
    {
        "source_id": "PKG_MK_PHASE4",
        "title": "PKG-MK Phase 4: Cesar Chavez, the UFW, and Behavioral Control",
        "file_path": "evidence/mk_research_phase4_chavez.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 4,
            "description": "CRITICAL: Chavez adopted the Game from Dederich Feb 1977 (E1, 0.95). 4/7 MK techniques at UFW. Volitional transfer. COINTELPRO paranoia as receptivity factor.",
            "key_finding": "Campaign breakthrough — clearest documented case of MK-adjacent behavioral technology entering and damaging a major American social movement. Transfer was volitional (0.85-0.90).",
        },
    },
    {
        "source_id": "PKG_MK_PHASE5",
        "title": "PKG-MK Phase 5: Labor and Civil Rights Movements — MK Behavioral Control Axis",
        "file_path": "evidence/mk_research_phase5_labor_civil_rights.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 5,
            "description": "T-group pipeline (Lewin→NTL→movements), CIA-labor nexus (Lovestone/Brown/AIFLD), Carl Rogers dual role, West at Haight-Ashbury, Convergence Problem.",
            "key_finding": "NEGATIVE: No MK techniques deployed AS organizing tools (0.85). CIA-labor nexus used financial not behavioral control (0.95). Carl Rogers CIA funding documented (E1, 0.90) but encounter groups developed independently.",
        },
    },
    {
        "source_id": "PKG_MK_PHASE6",
        "title": "PKG-MK Phase 6: CIA MK Programs and FBI COINTELPRO Relationship",
        "file_path": "evidence/mk_research_phase6_cointelpro_relationship.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 6,
            "description": "Interagency coordination analysis: 5 documented channels (Papich, HTLINGUAL, CACTUS, MINARET, Huston Plan). Parallel construction model.",
            "key_finding": "CACTUS channel connecting CIA CHAOS to FBI COINTELPRO — never disclosed to Church Committee, continued operating after both programs terminated (E2, 0.60-0.70).",
        },
    },
    {
        "source_id": "PKG_MK_PHASE7",
        "title": "PKG-MK Phase 7: The Human Potential Movement — CIA/Military Connections",
        "file_path": "evidence/mk_research_phase7_human_potential.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 7,
            "description": "Esalen, est, encounter groups. Bateson OSS, Esalen-SRI nexus, First Earth Battalion reverse transfer, Carl Rogers A-type pathway, Erhard assessment.",
            "key_finding": "HPM NOT CIA creation (0.15-0.25 for deployment). Carl Rogers is single A-type pathway. Gregory Bateson OSS veteran as Esalen founding intellectual. Esalen-SRI remote viewing nexus documented.",
        },
    },
    {
        "source_id": "PKG_MK_PHASE8",
        "title": "PKG-MK Phase 8: Dr. Louis Jolyon West — Intelligence Profile",
        "file_path": "evidence/mk_research_phase8_jolyon_west.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 8,
            "description": "West full operational arc: Subproject 43, Ruby visit, Haight-Ashbury, Hearst evaluation, Sirhan psychic driving claim, McVeigh visits, Violence Center proposal.",
            "key_finding": "West = dual-function operative (0.50-0.60). Subproject 43 confirmed (E1, 0.90). Ruby psychotic break after visit. Sirhan psychic driving claim. Jimmy Shaver 1954 hypnotic interrogation.",
        },
    },
    {
        "source_id": "PKG_MK_PHASE9",
        "title": "PKG-MK Phase 9: Straight Inc. — From MK-Ultra to Federally Endorsed Behavioral Control",
        "file_path": "evidence/mk_research_phase9_straight_inc.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 9,
            "description": "The Seed, Straight Inc., troubled teen industry. Senate brainwashing finding, 50K+ youth, $15M settlements, Sembler ambassadorships, DuPont revolving door.",
            "key_finding": "The Seed = NK brainwashing per U.S. Senate (E1, 0.95). Straight Inc. 50K+ youth, documented abuse in every state. 399 deaths in troubled teen industry. Ruth Fox CIA claim downgraded to E3.",
        },
    },
    {
        "source_id": "PKG_MK_PHASE10",
        "title": "PKG-MK Phase 10: Peoples Temple, Jim Jones, and the Synanon Ecosystem",
        "file_path": "evidence/mk_research_phase10_peoples_temple.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 10,
            "description": "Jones biographical profile, Mitrione/Brazil connection, behavioral control technique inventory, White Night conditioning, Jonestown event analysis.",
            "key_finding": "Jones-Mitrione co-present Belo Horizonte 1960-62 (E1, 0.85). CIA 201 file purged after Mitrione death. Independent trajectory with ecosystem exposure best fit (0.55-0.65).",
        },
    },
    {
        "source_id": "PKG_MK_PHASE11",
        "title": "PKG-MK Phase 11: MOSAIC Capstone Synthesis",
        "file_path": "evidence/mk_mosaic_synthesis.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 11,
            "description": "Competing hypothesis analysis across 10 phases. PHASED ECOSYSTEM MODEL. H1 origin confirmed / continuous rejected. H2 best individual fit. Accountability chain.",
            "key_finding": "PHASED ECOSYSTEM MODEL (0.70-0.80): central authorization at origin (Dulles, 0.85-0.90), unknowable transition period (Helms destruction), emergent diffusion post-exposure.",
        },
    },
    {
        "source_id": "PKG_MK_PHASE12",
        "title": "PKG-MK Phase 12: Cross-Campaign Intelligence Integration",
        "file_path": "evidence/mk_cross_campaign_integration.md",
        "evidence_type": "intelligence_report",
        "metadata": {
            "campaign": "PKG-MK",
            "phase": 12,
            "description": "Three-campaign convergence (PKG-MK, PKG-EP, PKG-911). Midnight Climax→Cohn→Epstein genealogy. Dulles unified portfolio. Five-program model. Semi-emergent ecosystem.",
            "key_finding": "Three campaigns independently converged on structurally identical ecosystem conclusions (0.75-0.85). Cohn as multi-domain convergence node. Five-program covert governance model.",
        },
    },
]

# =============================================================================
# CLAIMS — ~230 claims (MK-001 to MK-230)
# Each: (claim_id, source_id, claim_type, text, confidence, tags_json_string)
# =============================================================================

CLAIMS = [
    # =========================================================================
    # PHASE 1: MK Program Taxonomy (MK-001 to MK-020)
    # =========================================================================
    ("MK-001", "PKG_MK_PHASE1", "factual",
     "The CIA operated a continuous 23-year behavioral control research program (1950-1973) under four sequential codenames: Bluebird (Apr 1950), Artichoke (Aug 1951), MK-Ultra (Apr 13 1953), and MK-SEARCH (1964). DCI Allen Dulles formally approved MK-Ultra on April 13, 1953.",
     0.95, '["E1", "phase1", "taxonomy", "program_history", "PKG-MK"]'),

    ("MK-002", "PKG_MK_PHASE1", "factual",
     "Of 149 MK-Ultra subprojects, at least 25-30 involved behavioral modification techniques (as opposed to pharmacological research). Six core techniques were developed: psychic driving, depatterning, sensory deprivation, hypnotic programming, coercive interrogation, and group dynamics manipulation. A seventh — electronic behavioral activation — remained experimental.",
     0.90, '["E1", "phase1", "taxonomy", "techniques", "PKG-MK"]'),

    ("MK-003", "PKG_MK_PHASE1", "factual",
     "DCI Richard Helms ordered the destruction of all MK-Ultra files in 1973 as one of his final acts before leaving the Agency. Sidney Gottlieb personally oversaw the destruction. Only ~20,000 financial records survived because they were misfiled in a separate building, discovered via 1977 FOIA request by journalist John Marks.",
     0.95, '["E1", "phase1", "records_destruction", "helms", "gottlieb", "PKG-MK"]'),

    ("MK-004", "PKG_MK_PHASE1", "factual",
     "Sidney Gottlieb (1918-1999), Chief of TSS Chemical Division, was the single most important figure in MK behavioral control research. He administered MK-Ultra from inception, arranged CIA purchase of the world's entire LSD supply for $240,000, and testified before the Church Committee in October 1975.",
     0.95, '["E1", "phase1", "gottlieb", "personnel", "PKG-MK"]'),

    ("MK-005", "PKG_MK_PHASE1", "factual",
     "Donald Ewen Cameron conducted Subproject 68 at Allan Memorial Institute, McGill University (1957-1964): psychic driving, depatterning via intensive ECT (2-3x daily at 30-40x normal voltage), drug-induced sleep (up to 30 days), and sensory deprivation. ~80 patients underwent depatterning; many suffered permanent cognitive damage. Canadian government acknowledged and compensated victims.",
     0.95, '["E1", "phase1", "cameron", "subproject_68", "depatterning", "PKG-MK"]'),

    ("MK-006", "PKG_MK_PHASE1", "factual",
     "Louis Jolyon West conducted Subproject 43 ($20,800 grant, from March 1955) at University of Oklahoma: 'Psychophysiological Studies of Hypnosis and Suggestibility' and 'Studies of Dissociative States.' Proposed research on how 'environmental manipulations can affect the tendencies for dissociative phenomena to occur.' Held TOP SECRET clearance.",
     0.90, '["E1", "phase1", "west", "subproject_43", "hypnosis", "dissociation", "PKG-MK"]'),

    ("MK-007", "PKG_MK_PHASE1", "factual",
     "Carl Rogers held TOP SECRET clearance and was a contractor for Subproject 74 (SIHE cover funding, 1958-1962) and Subproject 97 (personality change during psychotherapy, 1959). His later encounter group methodology may have been influenced by this work, though no direct CIA direction of encounter groups is documented.",
     0.85, '["E1", "phase1", "rogers", "subproject_74", "subproject_97", "encounter_groups", "PKG-MK"]'),

    ("MK-008", "PKG_MK_PHASE1", "factual",
     "The KUBARK Counterintelligence Interrogation manual (July 1963) represents the primary operational product synthesizing MK behavioral research into field-deployable techniques. It codified the DDD framework (Debility, Dependency, Dread) — systematic psychological regression through accumulated stressors. Declassified 1997 via FOIA.",
     0.95, '["E1", "phase1", "kubark", "interrogation", "ddd", "PKG-MK"]'),

    ("MK-009", "PKG_MK_PHASE1", "factual",
     "CIA front organizations for MK funding included: Society for the Investigation of Human Ecology (SIHE) / Human Ecology Fund (administered by Harold Wolff at Cornell), Geschickter Fund for Medical Research (Georgetown), and various unnamed foundations. The SIHE funded Cameron's SP-68 and Rogers' SP-74 among others.",
     0.90, '["E1", "phase1", "front_organizations", "funding", "sihe", "geschickter", "PKG-MK"]'),

    ("MK-010", "PKG_MK_PHASE1", "factual",
     "Harris Isbell at NIMH Addiction Research Center, Lexington, KY administered LSD to African-American inmates for 77 consecutive days. Carl Pfeiffer led Subproject 112 at Bordentown Reformatory, NJ, experimenting on juvenile detainees with LSD and mescaline. Charles Geschickter tested 'stress producing chemicals, knockout drugs, and mind-altering substances on mental patients and terminal cancer patients.'",
     0.90, '["E1", "phase1", "vulnerable_populations", "isbell", "pfeiffer", "geschickter", "ethics", "PKG-MK"]'),

    ("MK-011", "PKG_MK_PHASE1", "assessment",
     "At least five behavioral modification techniques developed under MK programs appeared in civilian behavioral control programs by the 1970s-1980s, though direct personnel transfer (A-type) is documented in only limited cases. Transfer was primarily B-type (structural) and C-type (convergent from shared intellectual roots).",
     0.85, '["E1", "E2", "phase1", "transfer_assessment", "technique_diffusion", "PKG-MK"]'),

    ("MK-012", "PKG_MK_PHASE1", "factual",
     "Alden Sears at University of Denver/Minnesota conducted the most extensive hypnosis research in MK-Ultra under Subprojects 5, 25, 29, and 49, including development of 'unwitting message carrier' capability — subconscious retention and delivery of material without conscious awareness. Signed CIA secrecy agreement September 8, 1954.",
     0.85, '["E1", "phase1", "sears", "hypnosis", "subprojects", "PKG-MK"]'),

    ("MK-013", "PKG_MK_PHASE1", "factual",
     "Martin Orne at Harvard conducted Subproject 84 on 'induction of high motivation in individuals by means of specific interpersonal relationships.' He later publicly stated his findings 'would have disappointed the CIA officials if they had wanted to use hypnosis for mind control,' arguing hypnosis was 'a very poor method for mind-control.'",
     0.85, '["E1", "phase1", "orne", "subproject_84", "hypnosis_limits", "PKG-MK"]'),

    ("MK-014", "PKG_MK_PHASE1", "assessment",
     "Synanon's techniques show strong structural similarity to MK behavioral modification methods (ego destruction 0.75, isolation 0.80, sleep deprivation 0.75, repetitive pressure 0.70, identity destruction 0.75, coercive confession 0.80, group pressure 0.80) but appear to have derived from publicly available theoretical base (Lifton, Schein) rather than from direct MK program transfer. Transfer type: primarily B (Structural).",
     0.65, '["E2", "phase1", "synanon_parallels", "technique_comparison", "PKG-MK"]'),

    ("MK-015", "PKG_MK_PHASE1", "factual",
     "Straight Inc. employed techniques mapping to at least 5 of 6 core MK techniques: depatterning/ego destruction, sensory control, psychic driving (marathon sessions), coercive interrogation (KUBARK DDD), and sensory deprivation. One source indicates Straight 'worked with CIA subcontractor and mind control specialist Ruth Fox' — requires verification.",
     0.60, '["E1", "E3", "phase1", "straight_inc_parallels", "ruth_fox", "PKG-MK"]'),

    ("MK-016", "PKG_MK_PHASE1", "factual",
     "Subproject 119 (Saul Sells, Texas Christian University, 1960) was a literature review and development plan for 'recording, analysis and interpretation of bioelectric signals from the human organism' and 'activation of human behavior by remote electronic means.' Remained largely experimental.",
     0.80, '["E1", "phase1", "electronic_behavioral_control", "subproject_119", "PKG-MK"]'),

    ("MK-017", "PKG_MK_PHASE1", "assessment",
     "The documentary gap between what was funded and what was actually done remains the single largest intelligence gap in MK program analysis. Well-documented: who was funded, how much, through which conduits. Poorly documented: specific experimental protocols, results, subject experiences, operational deployments.",
     0.90, '["E1", "phase1", "intelligence_gap", "records_destruction", "PKG-MK"]'),

    ("MK-018", "PKG_MK_PHASE1", "factual",
     "est (Erhard Seminars Training, founded 1971) shows the weakest direct connection to MK programs of the three civilian programs analyzed (Synanon, Straight Inc., est). Erhard's documented influences are Scientology, Mind Dynamics, Zen Buddhism, and encounter groups. No documented CIA connection. Transfer type: primarily C (Parallel Development).",
     0.50, '["E2", "phase1", "est_erhard", "weak_connection", "PKG-MK"]'),

    ("MK-019", "PKG_MK_PHASE1", "factual",
     "MK-OFTEN (1966-1973) was a joint CIA-Army program at Edgewood Arsenal focused on behavioral and toxicological effects of drugs. Author Gordon Thomas (2007) claims it incorporated occult research — this claim remains single-source and unverified.",
     0.55, '["E2", "E3", "phase1", "mk_often", "edgewood", "PKG-MK"]'),

    ("MK-020", "PKG_MK_PHASE1", "factual",
     "Subproject 98 studied 'mass conversion' — methods to influence group behavior or ideological shifts. Subproject 102 (Muzafer Sherif, University of Oklahoma) studied 'behavior of naturally formed groups of adolescent boys' and group membership dynamics in teenage gangs.",
     0.65, '["E1", "E2", "phase1", "mass_conversion", "group_dynamics", "sherif", "PKG-MK"]'),

    # =========================================================================
    # PHASE 2: Synanon (MK-021 to MK-040)
    # =========================================================================
    ("MK-021", "PKG_MK_PHASE2", "factual",
     "Charles E. Dederich Sr. (1913-1997) participated in an LSD session on August 28, 1957, administered by Dr. Sidney Cohen and Dr. Keith S. Ditman at UCLA/VA Wadsworth Hospital. Dederich described it as 'a melding into cosmic consciousness' and 'the most important single experience in my entire life.' He had no therapy background, no college degree, and no formal training in psychology.",
     0.85, '["E1", "phase2", "dederich", "lsd_session", "cohen", "ditman", "origin_event", "PKG-MK"]'),

    ("MK-022", "PKG_MK_PHASE2", "factual",
     "Dederich explicitly acknowledged the brainwashing nature of his methods: 'Brainwashing is a very apt term. We get very dirty brains.' He 'later admitted to realizing that he was brainwashing his program members.'",
     0.95, '["E1", "phase2", "dederich", "brainwashing_admission", "PKG-MK"]'),

    ("MK-023", "PKG_MK_PHASE2", "factual",
     "The Synanon Game involved sustained verbal attack sessions: standard 2-3 hours, marathons up to 40 hours with 4-hour sleep break, and 72-hour continuous versions. Participation was mandatory. The explicit goal was ego destruction — 'tear them down in order to build them up' — to educate members 'in the inherent thought-patterns of the group leader.'",
     0.90, '["E1", "phase2", "the_game", "attack_therapy", "ego_destruction", "PKG-MK"]'),

    ("MK-024", "PKG_MK_PHASE2", "factual",
     "Synanon's evolution: treatment program (1958-1968), commune/alternative society (1968-1975), authoritarian cult (1975-1991). Key transitions: lifetime rehabilitation decree (1968), Church conversion for tax exemption (1974-1975), mandatory vasectomies and forced abortions (1976), mandatory partner-swapping (1977), Imperial Marines paramilitary force (1977-1978).",
     0.85, '["E1", "phase2", "synanon_evolution", "authoritarian_trajectory", "PKG-MK"]'),

    ("MK-025", "PKG_MK_PHASE2", "factual",
     "Paul Morantz, attorney who sued Synanon, was bitten by a rattlesnake placed in his mailbox on October 10, 1978. The rattles had been surgically removed. Lance Kenton and Joseph Musico (Imperial Marines) arrested. Dederich pled no contest to conspiracy to murder — sentenced to 5 years probation and $5,000 fine.",
     0.95, '["E1", "phase2", "morantz_attack", "violence", "imperial_marines", "PKG-MK"]'),

    ("MK-026", "PKG_MK_PHASE2", "factual",
     "By the late 1970s, one out of five Fortune 500 corporations were 'listed either as donating or as doing business with' Synanon (Richard Ofshe, 1980). Governor Edmund Brown Sr. signed the licensing exemption bill (1961). Senator Thomas Dodd endorsed Synanon before Congress. Celebrity visitors included Leonard Nimoy, Robert Wagner, Jane Fonda.",
     0.85, '["E1", "phase2", "elite_patronage", "political_protection", "PKG-MK"]'),

    ("MK-027", "PKG_MK_PHASE2", "factual",
     "IRS revoked Synanon's 501(c)(3) tax-exempt status on May 19, 1982 (retroactive to 1977), citing 'pattern of violence, insider control, private inurement, and systematic destruction of records.' IRS subsequently ordered $17 million in back taxes, bankrupting the organization. Dissolution in 1991.",
     0.95, '["E1", "phase2", "synanon_collapse", "irs", "PKG-MK"]'),

    ("MK-028", "PKG_MK_PHASE2", "factual",
     "Synanon's methods directly spawned the 'troubled teen industry' through CEDU (founded 1967 by former Synanon member Mel Wasserman), Straight Inc. (1976), and derivative programs. The Game was also transmitted to second-generation therapeutic communities: Daytop, Phoenix House, Gateway, Gaudenzia, The Family, and Walden House.",
     0.90, '["E1", "phase2", "troubled_teen_industry", "spawned_programs", "cedu", "PKG-MK"]'),

    ("MK-029", "PKG_MK_PHASE2", "assessment",
     "Single-source testimony ('Mark,' Unsilenced website) claims Abraham Maslow and psychologist Steven Simon arrived to systematically design behavioral programming at Synanon. Maslow's published engagement with Synanon is confirmed (1967 Journal of Humanistic Psychology), but operational design role is unverified. Steven Simon's identity and credentials not independently verified.",
     0.35, '["E3", "phase2", "maslow_claim", "steven_simon", "unverified", "PKG-MK"]'),

    ("MK-030", "PKG_MK_PHASE2", "factual",
     "Synanon accumulated $30M+ in assets. Annual revenue exceeded $1M by 1968 and $8M+ by 1976. 1975 conversion to 'The Church of Synanon' served three simultaneous purposes: tax exemption, escape from medical licensing, and First Amendment religious protection.",
     0.90, '["E1", "phase2", "financial_architecture", "tax_exemption", "PKG-MK"]'),

    ("MK-031", "PKG_MK_PHASE2", "assessment",
     "Dederich LSD session occurred within a research ecosystem permeated by CIA funding, but direct evidence of deliberate MK program connection to this specific session is absent. Confidence in deliberate MK connection: 0.30-0.40 (E3, circumstantial). Confidence in MK-adjacent research ecosystem: 0.70-0.80 (E2, documented institutional overlap).",
     0.40, '["E2", "E3", "phase2", "mk_connection_assessment", "circumstantial", "PKG-MK"]'),

    ("MK-032", "PKG_MK_PHASE2", "factual",
     "All eight of Lifton's thought reform criteria are documented as present in Synanon: milieu control, mystical manipulation, demand for purity, cult of confession (the Game), sacred science, loading the language, doctrine over person, and dispensing of existence.",
     0.90, '["E1", "E2", "phase2", "lifton_criteria", "thought_reform", "PKG-MK"]'),

    # =========================================================================
    # PHASE 3: Cohen Nexus (MK-033 to MK-047)
    # =========================================================================
    ("MK-033", "PKG_MK_PHASE3", "factual",
     "Dr. Sidney Cohen (1910-1987): M.D. from University of Bonn (1938), U.S. Army Pacific Campaign, Assistant Chief of Medical Service at VA Wadsworth Hospital (1948-1960), Associate Clinical Professor of Psychiatry UCLA (1954-1970). First Director of NIMH Division of Narcotic Abuse and Drug Addiction (1968-1970). Authored 250+ articles and 13 books.",
     0.95, '["E1", "phase3", "cohen_biography", "PKG-MK"]'),

    ("MK-034", "PKG_MK_PHASE3", "negative_finding",
     "No FOIA document or declassified record directly names Sidney Cohen as a CIA-funded MK-Ultra researcher. Cohen is not listed as a principal investigator on any known MK-Ultra subproject. ABC News reported Cohen 'had done some of the earliest CIA-funded experiments' with LSD (E2, 0.60), but this characterization is not confirmed in primary documents.",
     0.85, '["E1", "phase3", "cohen_negative_finding", "no_direct_cia_link", "PKG-MK"]'),

    ("MK-035", "PKG_MK_PHASE3", "assessment",
     "Cohen CIA connection hypothesis assessment: H1 direct witting contractor (0.15-0.20), H2 unwitting recipient of laundered funding (0.25-0.35), H3 independent researcher whose work CIA monitored/exploited (0.40-0.55, BEST FIT), H4 no CIA connection (0.20-0.30). Cohen's evolution into public LSD critic by 1962 is strongest indicator of independence.",
     0.55, '["E2", "E3", "phase3", "cohen_assessment", "independent_researcher", "PKG-MK"]'),

    ("MK-036", "PKG_MK_PHASE3", "factual",
     "Bill Wilson (AA co-founder) took LSD for the first time on August 29, 1956, under guidance of Gerald Heard and Dr. Sidney Cohen at VA Wadsworth Hospital. Aldous Huxley observed. Wilson took LSD multiple times 1956-1959, advocated for LSD as spiritual breakthrough tool for AA. AA board opposed.",
     0.95, '["E1", "phase3", "bill_wilson", "aa", "lsd_session", "PKG-MK"]'),

    ("MK-037", "PKG_MK_PHASE3", "factual",
     "Cohen's research network constitutes a documented social graph connecting Dederich's LSD administrators to confirmed MK-Ultra researchers through no more than one intermediary step: Cohen → 1959 conference → Harold Abramson (documented MK-Ultra researcher). Also connected: Humphrey Osmond, Betty Eisner, Gerald Heard, Aldous Huxley.",
     0.75, '["E1", "E2", "phase3", "research_network", "social_graph", "abramson", "PKG-MK"]'),

    ("MK-038", "PKG_MK_PHASE3", "factual",
     "VA Wadsworth Hospital was part of the Veterans Administration system where MK-Ultra-related research was documented. Ken Kesey's LSD experiences occurred at VA Hospital in Menlo Park under a documented MK-Ultra subproject. Cohen worked at VA Wadsworth 1948-1960 — the precise period of peak MK-Ultra activity.",
     0.75, '["E1", "E2", "phase3", "va_wadsworth", "institutional_vector", "PKG-MK"]'),

    ("MK-039", "PKG_MK_PHASE3", "factual",
     "The Sidney Cohen Collection at UCLA (OAC ark:/13030/kt0d5nf1w1) contains subject files, correspondence, and research records 1910-1987. Full contents not digitized or examined for CIA cutout financial signatures. This represents an unexamined intelligence gap that could resolve the Cohen-CIA question.",
     0.60, '["E2", "E3", "phase3", "cohen_collection", "ucla_archive", "intelligence_gap", "PKG-MK"]'),

    ("MK-040", "PKG_MK_PHASE3", "factual",
     "Keith S. Ditman (1921-2001): Associate Professor of Psychiatry at UCLA, published 71 articles, co-researcher with Cohen. Administered LSD to Dederich on August 28, 1957. Active at UCLA during documented CIA front organization funding. No direct evidence of Ditman-CIA connection found. Evidence tier: E2-E3, confidence in direct CIA connection: 0.40-0.50.",
     0.75, '["E1", "E2", "phase3", "ditman", "lsd_administrator", "PKG-MK"]'),

    ("MK-041", "PKG_MK_PHASE3", "assessment",
     "The literary-philosophical LSD movement (Huxley, Heard, Osmond, Cohen) was likely an independent phenomenon that the CIA monitored and occasionally intersected with, rather than a CIA creation. Huxley's interest in altered consciousness predated MK-Ultra by decades. Alfred Hubbard ('Captain Trips'), who introduced Huxley to LSD, has documented but contested intelligence connections.",
     0.65, '["E2", "phase3", "literary_lsd_movement", "huxley", "independent", "PKG-MK"]'),

    ("MK-042", "PKG_MK_PHASE3", "factual",
     "Louis Jolyon West became chairman of psychiatry at UCLA and director of the Neuropsychiatric Institute from 1969 to 1989. West arrived at UCLA in 1969; Cohen had been at UCLA since 1954. No documented professional relationship between Cohen and West in the MK-Ultra context. The institutional overlap is sequential, not concurrent.",
     0.75, '["E1", "E2", "phase3", "west_ucla", "cohen_west_overlap", "sequential", "PKG-MK"]'),

    # =========================================================================
    # PHASE 4: Chavez / UFW (MK-043 to MK-062)
    # =========================================================================
    ("MK-043", "PKG_MK_PHASE4", "factual",
     "CRITICAL: In February 1977, Cesar Chavez took the UFW executive board to visit the Synanon compound. They participated in Game sessions. Chavez declared Dederich 'a genius in terms of people.' Dederich told Chavez 'the Game' was key to reshaping the UFW. Chavez implemented mandatory biweekly sessions at La Paz — ~100 participants per week.",
     0.95, '["E1", "phase4", "chavez_game_adoption", "campaign_breakthrough", "PKG-MK"]'),

    ("MK-044", "PKG_MK_PHASE4", "factual",
     "The technique transfer from MK-adjacent behavioral research to the UFW is documented at every step: Cohen/Ditman LSD research → Dederich LSD session (Aug 1957) → Synanon Game development → Chavez visits Synanon (Feb 1977) → Game implemented at La Paz. Each link is E1 documented. The weakest link is Cohen/Ditman-to-MK-Ultra proper (E2/E3, 0.35-0.50).",
     0.80, '["E1", "E2", "phase4", "technique_chain", "documented_links", "PKG-MK"]'),

    ("MK-045", "PKG_MK_PHASE4", "assessment",
     "The Game at La Paz functioned as loyalty-enforcement and purge mechanism. 'The purges and the Game worked in tandem, setting the stage for UFW members to turn on one another as Chavez dictated, even as they suspected or knew the trumped-up charges to be false.' Many found it 'traumatic.' The Game did not CREATE Chavez's authoritarian turn — it SYSTEMATIZED and ACCELERATED it.",
     0.90, '["E1", "phase4", "game_function", "purge_mechanism", "PKG-MK"]'),

    ("MK-046", "PKG_MK_PHASE4", "factual",
     "4 of 7 core MK behavioral techniques were present in UFW practices under Chavez — the highest overlap of any organization examined in the campaign: ego destruction, confession/attack therapy, coercive group pressure, and identity destruction. Absent: sensory deprivation, hypnotic programming, group dynamics manipulation (in clinical MK form).",
     0.85, '["E1", "E2", "phase4", "technique_overlap", "highest_in_campaign", "PKG-MK"]'),

    ("MK-047", "PKG_MK_PHASE4", "assessment",
     "The transfer was VOLITIONAL — Chavez sought out and adopted these methods himself. There is NO evidence of a deliberate intelligence operation to introduce Synanon methods into the UFW. Confidence in volitional adoption: 0.85-0.90. Confidence in deliberate intelligence introduction: 0.05.",
     0.90, '["E1", "phase4", "volitional_transfer", "no_intelligence_direction", "PKG-MK"]'),

    ("MK-048", "PKG_MK_PHASE4", "factual",
     "Between 1977 and 1982, Chavez systematically expelled the UFW's most capable organizers: Marshall Ganz (chief organizer), Jerry Cohen (general counsel), Philip Vera Cruz (co-founder/VP), Gilbert Padilla (co-founder), Chris Hartmire, Joe Smith (El Malcriado editor), and dozens of others. UFW lost two-thirds of 22 elections June-Sept 1978.",
     0.90, '["E1", "phase4", "ufw_purges", "organizational_destruction", "PKG-MK"]'),

    ("MK-049", "PKG_MK_PHASE4", "factual",
     "La Paz compound created a totalist environment meeting Lifton's eight criteria: isolation in Tehachapi Mountains, $5-10/week subsistence wages creating total economic dependence, mandatory relocation of families, communal living, and charismatic leader authority. Staff called it 'Magic Mountain.'",
     0.85, '["E1", "E2", "phase4", "la_paz", "totalist_environment", "lifton_criteria", "PKG-MK"]'),

    ("MK-050", "PKG_MK_PHASE4", "factual",
     "FBI opened a file on Chavez during NFWA early days. CIA conducted illegal domestic surveillance under Operation CHAOS (1967-1974). January 2025: CIA released 55 declassified documents on surveillance of Latino civil rights movement, including monitoring of Chavez's travel and event attendance.",
     0.90, '["E1", "phase4", "fbi_surveillance", "operation_chaos", "cia_declassified", "PKG-MK"]'),

    ("MK-051", "PKG_MK_PHASE4", "negative_finding",
     "FBI's own investigation found NO EVIDENCE of communist control or significant communist infiltration of the UFW. Chavez was purging people for a conspiracy that did not exist. No evidence found of CIA operations specifically designed to disrupt the UFW or introduce behavioral control methods. NEGATIVE FINDING at 0.85.",
     0.85, '["E1", "phase4", "negative_communist", "no_cia_operations", "negative_finding", "PKG-MK"]'),

    ("MK-052", "PKG_MK_PHASE4", "negative_finding",
     "Intelligence connection assessment for Chavez advisors: Fred Ross Sr. (NEGATIVE, 0.85), Saul Alinsky/IAF (NEGATIVE, 0.85), Dolores Huerta (NEGATIVE, 0.85), Jim Drake (NEGATIVE, 0.75), Chris Hartmire (NEGATIVE, 0.75), Jerry Cohen (NEGATIVE, 0.75), Marshall Ganz (NEGATIVE, 0.75). No intelligence connections found.",
     0.85, '["E1", "E2", "phase4", "negative_finding", "advisors_clean", "PKG-MK"]'),

    ("MK-053", "PKG_MK_PHASE4", "assessment",
     "COINTELPRO created the psychological conditions (justified paranoia about infiltration) that made Chavez receptive to authoritarian control methods. The Game became the instrument through which that paranoia was operationalized. COINTELPRO contribution to paranoia: 0.50-0.60. Deliberate post-1971 continuation targeting UFW: 0.05-0.10.",
     0.55, '["E2", "E3", "phase4", "cointelpro_paranoia", "receptivity", "PKG-MK"]'),

    ("MK-054", "PKG_MK_PHASE4", "assessment",
     "Competing hypotheses for UFW destruction: H1 organic paranoia (0.45-0.55), H2 COINTELPRO-induced paranoia (0.35-0.45), H3 Game adoption as mechanism (0.55-0.65, strongest), H4 deliberate intelligence operation (0.05-0.10), H5 structural/political (0.50-0.60, Bardacke thesis). Multi-causal: COINTELPRO created paranoia, structure created tensions, personality drove centralization, the Game provided the mechanism.",
     0.60, '["E2", "phase4", "competing_hypotheses", "multi_causal", "PKG-MK"]'),

    ("MK-055", "PKG_MK_PHASE4", "negative_finding",
     "No evidence found of Opus Dei involvement with Chavez or UFW. No Knights of Columbus institutional relationship. No intelligence connections to Catholic institutions supporting UFW. Chavez's Catholicism was rooted in popular Mexican piety and Catholic social teaching, not conservative Catholic organizations.",
     0.80, '["E2", "phase4", "negative_finding", "catholic_clean", "PKG-MK"]'),

    # =========================================================================
    # PHASE 5: Labor & Civil Rights (MK-056 to MK-072)
    # =========================================================================
    ("MK-056", "PKG_MK_PHASE5", "factual",
     "Kurt Lewin (1890-1947) advised OSS on psychological warfare; some contributions remained classified as of 1980s. His wartime food-consumption research demonstrated small group discussion was more effective at changing behavior than lectures. He established MIT Research Center for Group Dynamics (1944) with ONR funding.",
     0.90, '["E1", "phase5", "lewin", "oss", "group_dynamics_origins", "PKG-MK"]'),

    ("MK-057", "PKG_MK_PHASE5", "factual",
     "National Training Laboratories (NTL) established 1947 in Bethel, Maine, by Lewin's collaborators (Bradford, Lippitt, Benne). Co-funded by Office of Naval Research and National Education Association. T-group method discovered accidentally in 1946 workshop. CRITICAL DISTINCTION: ONR funding ≠ CIA/MK-Ultra. ONR was Navy's open research arm.",
     0.85, '["E1", "phase5", "ntl", "t_groups", "onr_funding", "PKG-MK"]'),

    ("MK-058", "PKG_MK_PHASE5", "negative_finding",
     "NEGATIVE FINDING: No evidence that MK behavioral modification techniques were systematically deployed AS community organizing tools within labor or civil rights organizations. The Alinsky model and Highlander Folk School methods developed independently. The sensitivity training pipeline was overwhelmingly organic diffusion, not intelligence placement.",
     0.85, '["E1", "E2", "phase5", "negative_finding", "no_mk_as_organizing", "PKG-MK"]'),

    ("MK-059", "PKG_MK_PHASE5", "factual",
     "CIA-labor nexus is E1-documented: Jay Lovestone (ex-CPUSA) as AFL FTUC executive secretary cooperating with CIA from 1947. Irving Brown as CIA's primary labor operative in Europe. Thomas Braden published confession (1967): CIA provided $1M/year 1951-1954 to Brown and Lovestone. AIFLD trained Latin American labor leaders and was involved in Brazil (1964) and Chile (1973) coups.",
     0.95, '["E1", "phase5", "cia_labor_nexus", "lovestone", "brown", "braden", "aifld", "PKG-MK"]'),

    ("MK-060", "PKG_MK_PHASE5", "negative_finding",
     "CRITICAL NEGATIVE: Despite extensive documented CIA penetration of international labor operations, NO evidence that MK-Ultra behavioral modification techniques were deployed as labor organizing methods. The CIA-labor nexus operated through financial subsidies, organizational control, anti-communist training, and intelligence collection — NOT behavioral modification.",
     0.95, '["E1", "phase5", "negative_finding", "cia_labor_financial_not_behavioral", "PKG-MK"]'),

    ("MK-061", "PKG_MK_PHASE5", "factual",
     "Carl Rogers served on the board of the Human Ecology Fund (CIA front) in 1957. He 'was well aware that the Human Ecology Fund was a CIA front for covert funding of psychological research, and that he had no problem working for the CIA' (Demanchick & Kirschenbaum, 2008, Journal of Humanistic Psychology). A January 1960 CIA memo stated interest in 'adapting Rogers' theories for non-directive methods of interrogation.'",
     0.90, '["E1", "phase5", "rogers_cia", "human_ecology_fund", "witting_participant", "PKG-MK"]'),

    ("MK-062", "PKG_MK_PHASE5", "assessment",
     "Rogers-CIA connection is real and documented (E1) but does NOT establish encounter groups as a CIA product. Rogers' encounter group work was NOT funded by the CIA. His humanistic psychology was philosophically opposed to behavioral control. The pipeline is institutional (researcher funded by CIA later creates method adopted by movements) rather than operational.",
     0.85, '["E1", "E2", "phase5", "rogers_assessment", "institutional_not_operational", "PKG-MK"]'),

    ("MK-063", "PKG_MK_PHASE5", "factual",
     "Louis Jolyon West established a research presence in Haight-Ashbury (1966-1967), operating a 'laboratory disguised as a hippie crash pad.' He recruited subjects from the Haight-Ashbury Free Medical Clinic. Phase 5 assessed this as 'the single clearest documented case of an MK-Ultra researcher directly operating within a social movement context.'",
     0.85, '["E1", "phase5", "west_haight_ashbury", "counterculture", "mk_researcher_in_movement", "PKG-MK"]'),

    ("MK-064", "PKG_MK_PHASE5", "assessment",
     "The Convergence Problem is the central analytical challenge: techniques developed in military/intelligence-funded research and techniques developed organically within social movements arrived at similar methods independently because they drew on the same body of knowledge (social psychology, group dynamics, behavioral science). This creates permanent analytical ambiguity.",
     0.80, '["E2", "phase5", "convergence_problem", "analytical_challenge", "PKG-MK"]'),

    ("MK-065", "PKG_MK_PHASE5", "factual",
     "Richard Aoki documented as FBI informant (code T-2) in 2012 FOIA release. Bobby Seale's memoir describes Aoki providing Panthers their first firearms. Whether passive informant or active agent provocateur remains debated. FBI ordered hundreds of informants inside SDS to vote with Weather Underground faction at June 1969 convention to marginalize broader movement.",
     0.85, '["E1", "phase5", "aoki", "cointelpro", "agent_provocateur", "sds", "PKG-MK"]'),

    ("MK-066", "PKG_MK_PHASE5", "factual",
     "FBI informant William O'Neal infiltrated Chicago BPP as Fred Hampton's bodyguard, provided floor plan of Hampton's apartment, administered secobarbital to Hampton the night before the Dec 4, 1969 raid. Hampton was killed at age 21. FBI paid O'Neal a special bonus.",
     0.95, '["E1", "phase5", "hampton_assassination", "oneal", "cointelpro", "PKG-MK"]'),

    ("MK-067", "PKG_MK_PHASE5", "factual",
     "The FBI MLK 'suicide letter' (Nov 21, 1964) from William Sullivan employed psychological warfare techniques: identity destruction ('you are a complete fraud'), social isolation threat, 34-day deadline pressure, pseudo-insider framing ('us Negroes'), combined with audio recording. Techniques parallel MK methods but derived from independent FBI counterintelligence tradecraft.",
     0.95, '["E1", "phase5", "mlk_suicide_letter", "sullivan", "psychological_warfare", "PKG-MK"]'),

    ("MK-068", "PKG_MK_PHASE5", "factual",
     "NED founder Allen Weinstein stated (1991): 'A lot of what we do today was done covertly 25 years ago by the CIA.' NED was conceived by former CIA Director William Casey and former CIA operative Walter Raymond Jr. Half of NED funding goes to four organizations, including ACILS (successor to AIFLD since 1997).",
     0.95, '["E1", "phase5", "ned", "weinstein", "cia_successor", "aifld_acils", "PKG-MK"]'),

    ("MK-069", "PKG_MK_PHASE5", "factual",
     "Highlander Folk School (founded 1932) provides a critical counter-example: organically developed training methodology that was surveilled and suppressed but NOT infiltrated with behavioral modification techniques. Trained Rosa Parks (Aug 1955). Tennessee raided and padlocked Highlander in July 1959. State response was SUPPRESSION, not technique insertion.",
     0.90, '["E1", "phase5", "highlander", "counter_example", "suppression_not_insertion", "PKG-MK"]'),

    # =========================================================================
    # PHASE 6: COINTELPRO Relationship (MK-070 to MK-083)
    # =========================================================================
    ("MK-070", "PKG_MK_PHASE6", "factual",
     "Five documented channels of interagency coordination on domestic intelligence: (1) FBI-CIA Liaison Office (Papich, 1952-1970), (2) HTLINGUAL mail intercepts (1952-1973, 28M letters examined, 215K opened), (3) CACTUS communications channel (1970-ongoing), (4) NSA MINARET watchlists (1967-1973, 1,690+ US citizens), (5) Huston Plan apparatus (1970, brief).",
     0.90, '["E1", "phase6", "five_channels", "interagency_coordination", "PKG-MK"]'),

    ("MK-071", "PKG_MK_PHASE6", "factual",
     "CACTUS was a classified teletype channel — 'a cable system separated from the mainstream agency wires' — connecting CIA Operation CHAOS directly to FBI COINTELPRO. Earliest known target: Coretta Scott King. Within months, provided FBI evidence used to 'manipulate and ultimately destroy the Black Panther Party.' Never disclosed to Church Committee. No evidence CACTUS has been discontinued.",
     0.70, '["E1", "E2", "phase6", "cactus_channel", "chaos_cointelpro_link", "undisclosed", "PKG-MK"]'),

    ("MK-072", "PKG_MK_PHASE6", "assessment",
     "The correct analytical model is 'parallel construction with selective intelligence sharing' — not unified command, not complete independence, but a system where two bureaucratically separate programs shared targets, shared intelligence through classified channels, and achieved complementary effects without formal operational integration.",
     0.80, '["E2", "phase6", "parallel_construction", "analytical_model", "PKG-MK"]'),

    ("MK-073", "PKG_MK_PHASE6", "negative_finding",
     "No documented evidence of direct MK behavioral technique transfer to FBI COINTELPRO operations. The FBI's psychological warfare techniques (MLK suicide letter, bad-jacketing, snitch-jacketing) derived from independent FBI counterintelligence tradecraft, not from CIA/TSS behavioral research. Sam Papich did not transfer MK techniques to FBI.",
     0.75, '["E1", "E2", "phase6", "negative_finding", "no_mk_to_fbi_transfer", "PKG-MK"]'),

    ("MK-074", "PKG_MK_PHASE6", "factual",
     "Sam Papich (1917-2007) served as FBI's sole liaison to CIA for ~20 years (c.1952-1970). 'Sat at the table with Hoover and CIA directors Dulles and Helms.' Coordinated counterintelligence, CIA-Mafia assassination plots, Kennedy assassination investigation. Retired 1970 after Hoover abolished Liaison Section.",
     0.90, '["E1", "phase6", "papich", "fbi_cia_liaison", "PKG-MK"]'),

    ("MK-075", "PKG_MK_PHASE6", "factual",
     "Hoover's territorial jealousy functioned as an imperfect firewall preventing deeper operational integration. He rejected the Huston Plan (1970) — the only intelligence community leader to object. His 1970 abolition of FBI Liaison Section severed formal coordination. But informal channels (CACTUS, HTLINGUAL) continued beneath the official break.",
     0.85, '["E1", "phase6", "hoover_firewall", "huston_plan_rejection", "PKG-MK"]'),

    ("MK-076", "PKG_MK_PHASE6", "factual",
     "Huston Plan (1970) proposed domestic burglary, illegal electronic surveillance, opening mail, and detention camps for antiwar protesters. Nixon approved July 23, rescinded July 28 after Hoover objected. William Sullivan co-developed the plan. Despite rescission, 'several of its provisions were implemented' through informal channels.",
     0.90, '["E1", "phase6", "huston_plan", "sullivan", "implemented_anyway", "PKG-MK"]'),

    ("MK-077", "PKG_MK_PHASE6", "assessment",
     "Model B (parallel development from shared roots) is best-supported explanation for technique similarity between MK and COINTELPRO. Model C (convergent architecture — no direct transfer but shared ecosystem + intelligence sharing = de facto unified capability) is best-supported for operational coordination. The techniques developed independently; the intelligence infrastructure connected the programs operationally.",
     0.75, '["E2", "phase6", "convergence_models", "parallel_plus_convergent", "PKG-MK"]'),

    ("MK-078", "PKG_MK_PHASE6", "factual",
     "Gottlieb's TSS (which ran MK programs) and Ober's Special Operations Group (which ran CHAOS) were in different CIA divisions. MK was a research program producing techniques; CHAOS was a collection program gathering intelligence on dissidents. Even within CIA, these were operationally separate.",
     0.85, '["E1", "phase6", "tss_vs_chaos", "internal_separation", "PKG-MK"]'),

    ("MK-079", "PKG_MK_PHASE6", "factual",
     "A 2011 FBI 'primer' on overseas interrogations 'repeatedly cites the CIA's 1963 KUBARK Counterintelligence Interrogation' manual. This demonstrates eventual cross-pollination of MK techniques to FBI, but postdates both programs by decades. Whether FBI accessed KUBARK during COINTELPRO era is NOT DOCUMENTED.",
     0.85, '["E1", "phase6", "kubark_fbi_2011", "eventual_crossover", "PKG-MK"]'),

    # =========================================================================
    # PHASE 7: Human Potential Movement (MK-080 to MK-097)
    # =========================================================================
    ("MK-080", "PKG_MK_PHASE7", "assessment",
     "The Human Potential Movement was NOT a CIA creation or front operation. Its founders (Murphy, Price, Maslow, Perls) had genuine intellectual motivations rooted in humanistic psychology, Eastern philosophy, and the postwar search for meaning. However, the HPM existed within an ecosystem thoroughly permeated by intelligence-connected individuals, funding streams, and institutional overlaps.",
     0.85, '["E1", "E2", "phase7", "hpm_not_cia_creation", "permeated_ecosystem", "PKG-MK"]'),

    ("MK-081", "PKG_MK_PHASE7", "factual",
     "Gregory Bateson (1904-1980) is the single most significant intelligence-connected figure at Esalen: designed psychological warfare operations for OSS in Burma/Thailand/China/India (E1, 0.95). At Palo Alto VA during MK-era research. Harold Abramson (MK-Ultra researcher) gave Bateson his first LSD. Bateson helped arrange Ginsberg's LSD experience near Stanford.",
     0.85, '["E1", "phase7", "bateson_oss", "esalen_founding_intellectual", "lsd_distribution", "PKG-MK"]'),

    ("MK-082", "PKG_MK_PHASE7", "factual",
     "Esalen-SRI remote viewing nexus: Russell Targ passed remote viewing protocols to Michael Murphy. Esalen hosted parapsychology seminars with SRI researchers. The First Earth Battalion emerged from Army officers attending Esalen. INSCOM supported Channon's concepts. Jim Channon briefed 150+ general officers.",
     0.80, '["E1", "E2", "phase7", "esalen_sri_nexus", "remote_viewing", "first_earth_battalion", "PKG-MK"]'),

    ("MK-083", "PKG_MK_PHASE7", "factual",
     "Carl Rogers was witting CIA board member (Human Ecology Fund, from 1957) who simultaneously developed encounter group methodology. He 'was well aware' of CIA funding and 'had no problem working for the CIA.' A January 1960 CIA memo documented interest in 'adapting Rogers' theories for non-directive methods of interrogation.' This is the single A-type (direct) pathway from MK funding to HPM methodology.",
     0.90, '["E1", "phase7", "rogers_a_type_pathway", "cia_board_member", "encounter_groups", "PKG-MK"]'),

    ("MK-084", "PKG_MK_PHASE7", "factual",
     "Jenny O'Connor channeled 'The Nine' at Esalen (late 1970s-~1983), becoming so influential that The Nine 'were actually listed on the Institute's staff, even successfully ordering the sacking of its chief finance officer.' The Nine trace to Andrija Puharich's Round Table Foundation (1948), and Puharich was 'almost certainly a CIA asset.'",
     0.65, '["E2", "phase7", "the_nine", "oconnor", "puharich", "esalen_penetration", "PKG-MK"]'),

    ("MK-085", "PKG_MK_PHASE7", "factual",
     "Werner Erhard (born John Paul Rosenberg, 1935) synthesized est from Scientology, Mind Dynamics, Zen/Alan Watts, and encounter groups. est Standard Training was ~60-hour course with marathon sessions, confrontation, ego dissolution. Reached 1M+ participants. No documented CIA connection. Scientology orchestrated his 1989-1991 downfall; CBS later repudiated its 60 Minutes segment.",
     0.80, '["E1", "E2", "phase7", "erhard_est", "no_cia_connection", "scientology_attack", "PKG-MK"]'),

    ("MK-086", "PKG_MK_PHASE7", "negative_finding",
     "NEGATIVE FINDING: No evidence of Werner Erhard holding Department of Defense contracts. No evidence of CIA connection to est/Landmark. Erhard's influences are documented as Scientology, Mind Dynamics (Alexander Everett), Zen Buddhism, and the encounter group movement. est methodology shows weakest MK connection of programs analyzed.",
     0.75, '["E2", "E3", "phase7", "negative_finding", "erhard_no_cia", "PKG-MK"]'),

    ("MK-087", "PKG_MK_PHASE7", "factual",
     "Lt. Col. James Channon spent 1977-1979 at Esalen, then authored the 125-page 'First Earth Battalion Operations Manual' proposing New Age military transformation. This represents REVERSE transfer — military officers voluntarily sought out HPM methods and imported them back into the military. Direction: demand-pull, not supply-push.",
     0.80, '["E1", "phase7", "channon", "first_earth_battalion", "reverse_transfer", "demand_pull", "PKG-MK"]'),

    ("MK-088", "PKG_MK_PHASE7", "assessment",
     "The HPM functioned as a cultural amplifier distributing behavioral modification techniques to civilian populations at scale — primarily through market demand and countercultural adoption, not intelligence deployment. Deployment hypothesis: 0.15-0.25. Organic diffusion with intelligence permeation: 0.75-0.85.",
     0.80, '["E2", "phase7", "hpm_cultural_amplifier", "organic_diffusion", "PKG-MK"]'),

    ("MK-089", "PKG_MK_PHASE7", "factual",
     "Michael Murphy co-founded Esalen in 1962 on family property in Big Sur. He was reportedly approached for CIA and FBI recruitment but 'never succumbed.' A CIA FOIA document titled 'Esalen's Hot-Tub Diplomacy' (CIA-RDP90-00806R000100380026-1) confirms Agency awareness and interest in the Esalen Soviet-American Exchange Program.",
     0.75, '["E1", "E2", "phase7", "murphy", "esalen", "cia_foia", "refused_recruitment", "PKG-MK"]'),

    ("MK-090", "PKG_MK_PHASE7", "assessment",
     "Richard Price, Esalen co-founder, was involuntarily committed and subjected to electroshock and insulin shock treatments — techniques used in Cameron's MK-Ultra Subproject 68 depatterning. Price's Esalen was, in part, a reaction against the psychiatric establishment that had subjected him to these methods. Irony: HPM founder was himself a victim of MK-adjacent techniques.",
     0.75, '["E2", "phase7", "price_victim", "irony", "anti_coercive_psychiatry", "PKG-MK"]'),

    ("MK-091", "PKG_MK_PHASE7", "negative_finding",
     "No specific CIA or military funding of Abraham Maslow's research was found. His 1962 visits to Esalen, Synanon, and Non-Linear Systems were self-motivated. Maslow appears to be the HPM founder with the cleanest separation from intelligence connections. Independence assessment: 0.85.",
     0.85, '["E2", "E3", "phase7", "negative_finding", "maslow_clean", "PKG-MK"]'),

    # =========================================================================
    # PHASE 8: Jolyon West (MK-092 to MK-108)
    # =========================================================================
    ("MK-092", "PKG_MK_PHASE8", "factual",
     "West's CIA relationship predates Subproject 43. In a letter to Sidney Gottlieb dated June 11, 1953 — only two months after MK-Ultra was approved — West outlined proposed experiments combining psychotropic drugs and hypnosis. This establishes West as one of the original MK-Ultra researcher cohort.",
     0.90, '["E1", "phase8", "west_gottlieb_letter", "original_cohort", "1953", "PKG-MK"]'),

    ("MK-093", "PKG_MK_PHASE8", "factual",
     "West examined Jack Ruby on April 26, 1964, in Dallas County Jail, declared Ruby had suffered 'an acute psychotic break' — a finding no prior observer had reached. Recommended further interrogation under sodium pentothal and hypnosis (his own MK-funded techniques). Ruby had been making conspiracy claims; became incoherent after West's visit; died Jan 3, 1967.",
     0.90, '["E1", "phase8", "ruby_visit", "psychotic_break", "sodium_pentothal", "PKG-MK"]'),

    ("MK-094", "PKG_MK_PHASE8", "factual",
     "Allen Dulles, who had approved the MK-Ultra program as DCI and knew of West's CIA work, sat on the Warren Commission. The Warren Commission did not investigate West's MK-Ultra background or its relevance to Ruby's mental state changes. Did not grant Ruby's request to testify in Washington.",
     0.95, '["E1", "phase8", "dulles_warren_commission", "conflict_of_interest", "PKG-MK"]'),

    ("MK-095", "PKG_MK_PHASE8", "assessment",
     "Ruby intervention deliberate manipulation hypothesis: 0.35-0.45 (E3). Circumstantial evidence is strong but entirely inferential. No document, witness, or physical evidence establishes that West administered any substance to Ruby or deliberately induced a psychotic break. The selection of an MK-Ultra researcher for this role demands explanation.",
     0.40, '["E3", "phase8", "ruby_deliberate_manipulation", "circumstantial", "PKG-MK"]'),

    ("MK-096", "PKG_MK_PHASE8", "factual",
     "Jimmy Shaver case (1954): West hypnotized a murder suspect at Lackland AFB who confessed under hypnosis but maintained innocence at trial. West made 'only a minimal effort to exonerate Shaver.' Shaver was convicted, executed on his 33rd birthday in 1958 despite appeals court ruling of unfair trial. This occurred one year after West received his MK-Ultra grant.",
     0.70, '["E2", "phase8", "jimmy_shaver", "hypnotic_interrogation", "execution", "PKG-MK"]'),

    ("MK-097", "PKG_MK_PHASE8", "factual",
     "West claimed Sirhan Sirhan had been subjected to 'psychic driving' — Cameron's hallmark MK-Ultra Subproject 68 technique involving looped audio under hypnosis creating trigger words activating hidden programmed personality. West's identification of Cameron's classified technique in an operational context demonstrates familiarity with classified MK methods.",
     0.65, '["E2", "phase8", "sirhan", "psychic_driving_claim", "cameron_technique", "PKG-MK"]'),

    ("MK-098", "PKG_MK_PHASE8", "factual",
     "West evaluated Patty Hearst (1975-1976) alongside fellow CIA-funded researchers Martin Orne (Subproject 84) and Robert Jay Lifton. Testified she displayed 'all the classic signs of coercion, brainwashing, and the Stockholm effect.' The convergence of three CIA-funded researchers on a single defendant is notable.",
     0.85, '["E1", "phase8", "hearst_evaluation", "orne", "lifton", "three_cia_researchers", "PKG-MK"]'),

    ("MK-099", "PKG_MK_PHASE8", "factual",
     "West proposed the UCLA Center for the Study and Reduction of Violence (1972-1973): behavioral modification on prisoners, potential psychosurgery, mass behavioral data collection. Governor Reagan initially supported it. Killed by opposition from NAACP, civil rights groups, feminist organizations. West had just moved to UCLA after Helms's 1973 records destruction.",
     0.85, '["E1", "phase8", "violence_center", "reagan", "psychosurgery", "killed_by_opposition", "PKG-MK"]'),

    ("MK-100", "PKG_MK_PHASE8", "factual",
     "West operated a CIA-funded 'laboratory disguised as a hippie crash pad' at Haight-Ashbury (1966-1967). At the same clinic, Roger Smith (Manson's parole officer, criminology Ph.D.) ran CIA-fronted Amphetamine Research Project. Manson frequented the clinic. Tom O'Neill's 20-year investigation found convergence but no direct evidence of West-Manson interaction.",
     0.70, '["E2", "phase8", "haight_ashbury_lab", "roger_smith", "manson_convergence", "oneill", "PKG-MK"]'),

    ("MK-101", "PKG_MK_PHASE8", "factual",
     "West made 17+ visits to Timothy McVeigh after Oklahoma City bombing (1995). Characterized him on national television (Larry King) as a 'lone nut' not involved in a conspiracy — on the DAY of the bombing. Between 1974 and 1989, West received at least $5,110,099 in federal grants through NIMH.",
     0.65, '["E2", "phase8", "mcveigh_visits", "lone_nut", "nimh_funding", "PKG-MK"]'),

    ("MK-102", "PKG_MK_PHASE8", "assessment",
     "West pattern analysis — dual-function operative hypothesis (H-W2): 0.50-0.60 (BEST FIT). Maintained security clearance and informal intelligence engagement while pursuing legitimate academic career. Explains episodic engagement at high-profile cases without requiring continuous tasking. Statistical improbability of one MK researcher at Ruby, Haight-Ashbury, Hearst, Sirhan, McVeigh merits analytical attention.",
     0.55, '["E2", "E3", "phase8", "dual_function_operative", "pattern_analysis", "PKG-MK"]'),

    ("MK-103", "PKG_MK_PHASE8", "factual",
     "August 3, 1962: West injected Tusko, a 7,000-lb Indian elephant, with 297mg LSD (3,000x normal human dose) at Lincoln Park Zoo, Oklahoma City. Tusko died within one hour. The methodological errors — body-weight scaling rather than brain-weight — have been universally criticized. Experiment occurred during West's active MK-Ultra contract period.",
     0.95, '["E1", "phase8", "tusko_elephant", "lsd_dosage_error", "PKG-MK"]'),

    # =========================================================================
    # PHASE 9: Straight Inc. (MK-104 to MK-122)
    # =========================================================================
    ("MK-104", "PKG_MK_PHASE9", "factual",
     "The Seed (founded 1970, Fort Lauderdale) by Art Barker (former stand-up comedian, mail-order degree) modeled methods on Synanon's Game adapted for adolescents. Children sat in metal chairs 12 hours/day, 7 days/week, subjected to group confrontation. Received $1.8M in NIDA federal funding under Drug Czar Robert DuPont.",
     0.90, '["E1", "phase9", "the_seed", "barker", "nida_funding", "dupont", "PKG-MK"]'),

    ("MK-105", "PKG_MK_PHASE9", "factual",
     "The U.S. Senate Judiciary Committee's Subcommittee on Constitutional Rights (1974) concluded The Seed used 'the same brainwashing tactics on American teenagers that North Korea had used on adult American prisoners of war.' The UN and Geneva Convention had condemned these tactics as war crimes. Congress blocked further federal funding; Florida revoked Barker's license.",
     0.95, '["E1", "phase9", "senate_brainwashing_finding", "war_crimes_equivalent", "PKG-MK"]'),

    ("MK-106", "PKG_MK_PHASE9", "factual",
     "Straight Inc. (founded 1976, St. Petersburg FL) by Mel and Betty Sembler. Processed over 50,000 youth across up to 12 facilities in 9 states. Five-phase system targeting youth aged 12-21. Methods: strip searches, 24/7 oldcomer surveillance, marathon confrontation sessions, food/sleep/water deprivation, peer-on-peer physical restraint, denial of medical care.",
     0.95, '["E1", "phase9", "straight_inc", "sembler", "50000_youth", "documented_methods", "PKG-MK"]'),

    ("MK-107", "PKG_MK_PHASE9", "factual",
     "Fred Collins Jr. (1982): detained against will for 10 months; jury awarded $220,000 false imprisonment (affirmed 4th Circuit, 748 F.2d 916). Karen Norton (1990): $721,000 for assault and denied medical care. Kids of North Jersey: $4.5M settlement. Aggregate: approximately $15M in lawsuit settlements. State investigators documented abuse in EVERY state where Straight operated.",
     0.95, '["E1", "phase9", "straight_lawsuits", "collins", "norton", "15m_settlements", "PKG-MK"]'),

    ("MK-108", "PKG_MK_PHASE9", "factual",
     "Mel Sembler's political trajectory: RNC Finance Chairman (raised $220M+ for GOP in 2000 cycle, $21.3M single-dinner record). Appointed Ambassador to Australia (1989-1993) DURING active Straight abuse. Appointed Ambassador to Italy/NATO (2001-2005) AFTER documented abuse. Drug Free America Foundation is legally the same entity as Straight Inc., just renamed.",
     0.95, '["E1", "phase9", "sembler_ambassadorships", "political_reward", "fundraising", "PKG-MK"]'),

    ("MK-109", "PKG_MK_PHASE9", "factual",
     "Robert DuPont: First NIDA Director + Drug Czar under Nixon/Ford. Administered $1.8M grant to The Seed (Senate later found = brainwashing). Became paid consultant for Straight Inc. after leaving government. Co-founded Bensinger, DuPont & Associates (private drug testing firm serving 10M employees). Trajectory: government authority → government-funded behavioral control → private profit.",
     0.90, '["E1", "phase9", "dupont_revolving_door", "nida_to_straight_to_testing", "PKG-MK"]'),

    ("MK-110", "PKG_MK_PHASE9", "factual",
     "Nancy Reagan visited Straight facilities in 1982 and 1985 (with Princess Diana), providing presidential-level legitimacy during the period when state investigators were documenting systematic abuse. George H.W. Bush publicly praised Straight while receiving $100K+ from Sembler.",
     0.95, '["E1", "phase9", "nancy_reagan_visit", "princess_diana", "political_endorsement", "PKG-MK"]'),

    ("MK-111", "PKG_MK_PHASE9", "factual",
     "CEDU (founded 1967 by former Synanon member Mel Wasserman) is the most direct organizational link between Synanon and the modern troubled teen industry. Methods: 'raps' (attack therapy), sleep deprivation, humiliation, forced emoting. CEDU purchased by Brown Schools (1998), filed for bankruptcy (2005).",
     0.90, '["E1", "phase9", "cedu", "wasserman", "synanon_direct_link", "PKG-MK"]'),

    ("MK-112", "PKG_MK_PHASE9", "factual",
     "The troubled teen industry (2024-2026): estimated 10,000+ programs, 120,000-200,000 children held at any given time, 399 documented youth deaths (Unsilenced database). February 2024: 12-year-old died within 24 hours at Trails Carolina. Stop Institutional Child Abuse Act signed by Biden December 24, 2024.",
     0.85, '["E1", "E2", "phase9", "troubled_teen_industry", "399_deaths", "current_scale", "PKG-MK"]'),

    ("MK-113", "PKG_MK_PHASE9", "assessment",
     "Ruth Fox CIA subcontractor claim DOWNGRADED to E3 (0.25-0.35). Fox is not named in any declassified MK-Ultra subproject document. The specific 'CIA subcontractor' designation originates from a single investigative source without primary documentation. Her connection to Straight Inc. specifically is not documented.",
     0.30, '["E3", "phase9", "ruth_fox_downgraded", "single_source", "unverified", "PKG-MK"]'),

    ("MK-114", "PKG_MK_PHASE9", "assessment",
     "The evidence supports a pattern of policy capture by behavioral control practitioners operating in a permissive War on Drugs political environment — but the mechanism was opportunistic institutional drift rather than deliberate intelligence community direction. Policy capture: 0.65-0.75 (opportunistic). IC direction: 0.10-0.15.",
     0.70, '["E2", "phase9", "policy_capture", "opportunistic", "not_ic_directed", "PKG-MK"]'),

    ("MK-115", "PKG_MK_PHASE9", "factual",
     "The complete technique chain: MK-Ultra subprojects (1953-1964) → Cohen/Ditman LSD research → Dederich LSD session/Synanon founding (Aug 1957) → Synanon behavioral control development → Art Barker visits Synanon/The Seed (~1970) → Senate finds Seed = brainwashing (1974) → Straight Inc. founding (1976) → troubled teen industry (1980s-present) → 399 documented deaths. Composite chain confidence: 0.70-0.80.",
     0.75, '["E1", "E2", "phase9", "complete_technique_chain", "accountability_chain", "PKG-MK"]'),

    # =========================================================================
    # PHASE 10: Peoples Temple (MK-116 to MK-133)
    # =========================================================================
    ("MK-116", "PKG_MK_PHASE10", "factual",
     "Jim Jones (1931-1978) conducted genuine civil rights work in Indianapolis 1953-1965: desegregated restaurants, hospitals, churches, police department. Appointed head of Indianapolis Human Rights Commission. First in Indiana to adopt a Black child. These achievements are documented in contemporary news accounts and city records.",
     0.90, '["E1", "phase10", "jones_civil_rights", "genuine", "PKG-MK"]'),

    ("MK-117", "PKG_MK_PHASE10", "factual",
     "Jones and Dan Mitrione (confirmed CIA-connected via USAID Office of Public Safety) were both from Richmond, Indiana, and both present in Belo Horizonte, Brazil during overlapping periods (1960-1962). Jones made 'frequent visits' to the U.S. Consulate. Vice Consul Jon Lodeesen wrote Jones a letter on Foreign Service stationery (Oct 18, 1962).",
     0.85, '["E1", "E2", "phase10", "jones_mitrione", "belo_horizonte", "overlap", "PKG-MK"]'),

    ("MK-118", "PKG_MK_PHASE10", "factual",
     "The CIA opened a 201 (person of interest) file on Jim Jones circa 1960, coinciding with Mitrione's departure for Brazil. When Mitrione was killed by Tupamaros guerrillas (Aug 10, 1970), Jones's 201 file was purged. The timing of the purge is the single most suggestive evidence for intelligence connection.",
     0.75, '["E1", "E2", "phase10", "cia_201_file", "purged_after_mitrione_death", "PKG-MK"]'),

    ("MK-119", "PKG_MK_PHASE10", "factual",
     "Peoples Temple behavioral control methods: catharsis sessions (public humiliation, identical structure to Synanon Game), sleep deprivation (PA broadcasts at all hours), information control (mail intercepted, passports confiscated, armed guards), coercive confession (forced to sign false confessions of crimes, held as blackmail), sexual manipulation (Jones claimed exclusive access), pharmacological sedation (Thorazine, sodium pentothal in 'Extended Care Unit').",
     0.85, '["E1", "phase10", "peoples_temple_techniques", "seven_mk_parallels", "PKG-MK"]'),

    ("MK-120", "PKG_MK_PHASE10", "factual",
     "Jonestown pharmacological stockpile: 10,000 injectable doses of Thorazine and 1,000 tablets — far exceeding legitimate medical needs for 900 people. Also sodium pentothal, chloral hydrate, Demerol, Valium. Drugs smuggled into Guyana bypassing import regulations. These are precisely the drug classes used in MK-Ultra experiments.",
     0.90, '["E1", "phase10", "jonestown_drugs", "thorazine_stockpile", "mk_drug_classes", "PKG-MK"]'),

    ("MK-121", "PKG_MK_PHASE10", "factual",
     "White Night suicide conditioning drills: Jones assembled community, announced enemies approaching, gave cups of liquid said to be poison, people sat weeping. After a period, announced 'only a drill.' Functions: compliance testing, habituation to drinking 'poison,' learned helplessness (repeated drills where resistance was futile), operant conditioning (relief of survival as negative reinforcement). No direct MK-Ultra analog exists.",
     0.90, '["E1", "phase10", "white_night_drills", "novel_technique", "habituation", "PKG-MK"]'),

    ("MK-122", "PKG_MK_PHASE10", "factual",
     "November 18, 1978: 918 deaths — 909 at Jonestown, 5 at Port Kaituma airstrip (Congressman Leo Ryan, 3 journalists, 1 defector), 4 in Georgetown. ~304 victims were minors. Children killed first via syringes of cyanide. Jones died of gunshot — likely not self-inflicted. Armed guards surrounded pavilion.",
     0.95, '["E1", "phase10", "jonestown_massacre", "918_deaths", "ryan_killed", "PKG-MK"]'),

    ("MK-123", "PKG_MK_PHASE10", "assessment",
     "Most parsimonious model: convergent authoritarian trajectory with ecosystem exposure (0.55-0.65). Jones independently developed authoritarian organization employing behavioral control techniques circulating in the 1970s Northern California ecosystem. Alternative model (Jones as intelligence asset): 0.25-0.35. H2 for Brazil period (recruited/assessed): 0.35-0.45.",
     0.60, '["E2", "E3", "phase10", "independent_trajectory", "ecosystem_exposure", "PKG-MK"]'),

    ("MK-124", "PKG_MK_PHASE10", "factual",
     "House Permanent Select Committee on Intelligence (1980) found 'no evidence' of CIA involvement with Peoples Temple. However, House Foreign Affairs Committee released only 782 of 5,782 pages. CIA FOIA releases heavily redacted. Dan Mitrione's OPS role (CIA-covered torture training in Latin America) is E1 documented.",
     0.85, '["E1", "E2", "phase10", "congressional_investigation", "incomplete_record", "PKG-MK"]'),

    ("MK-125", "PKG_MK_PHASE10", "factual",
     "Larry Layton (sole person convicted at airstrip) — father Dr. Laurence Laird Layton was chief of U.S. Army Chemical Warfare Division at Dugway Proving Ground with highest-level security clearance. Sister Deborah defected May 1978, publicly denounced Jonestown. Intelligence placement hypothesis: 0.20-0.25; family involvement appears genuine.",
     0.80, '["E1", "E2", "phase10", "larry_layton", "father_chemical_warfare", "PKG-MK"]'),

    ("MK-126", "PKG_MK_PHASE10", "factual",
     "Synanon-Peoples Temple connection: both operated in Northern California 1970s. Synanon's distribution network donated powdered drink mix used at Jonestown. Laura Johnston Kohl moved from Peoples Temple to Synanon after the massacre. Both shared media defense strategies. Both crises occurred in 1978 (Morantz Oct, Jonestown Nov). Parallel: not coordination.",
     0.70, '["E1", "E2", "phase10", "synanon_pt_connection", "parallel_not_coordination", "PKG-MK"]'),

    ("MK-127", "PKG_MK_PHASE10", "factual",
     "Seven of eight Peoples Temple techniques have documented parallels in MK-Ultra: ego destruction (0.80), isolation (0.85), sleep deprivation (0.85), coercive confession (0.85), pharmacological sedation (0.80), sexual manipulation (0.70), group pressure (0.75). White Night conditioning (0.40) appears novel — no direct MK precedent, though uses MK-studied behavioral science principles.",
     0.80, '["E1", "E2", "phase10", "seven_technique_parallels", "systematic", "PKG-MK"]'),

    ("MK-128", "PKG_MK_PHASE10", "factual",
     "Pat Lynch (first female investigative reporter for NBC Evening News) filmed 'as much as a dozen hours' of Peoples Temple interviews. Series was killed by NBC executives — claimed they feared violent response. Lynch: 'if the story was broadcast when it was supposed to be, the people in Jonestown would not have died.' NBC later claimed only 18 minutes of footage survive.",
     0.80, '["E1", "E2", "phase10", "pat_lynch", "nbc_killed_story", "media_suppression", "PKG-MK"]'),

    # =========================================================================
    # PHASE 11: MOSAIC Synthesis (MK-129 to MK-148)
    # =========================================================================
    ("MK-129", "PKG_MK_PHASE11", "assessment",
     "PHASED ECOSYSTEM MODEL (0.70-0.80): Phase A — Central Authorization (1950s-1961): Dulles personally managed MK-Ultra, Gladio, Mockingbird, and geopolitical coups as a unified portfolio. THIS IS central coordination. Phase B — Transition (1961-1973): coordination persisted through CACTUS, Papich, West. Unknowable due to Helms destruction. Phase C — Diffusion (1973-present): self-sustaining volitional adoption.",
     0.75, '["E1", "E2", "phase11", "phased_ecosystem_model", "central_then_emergent", "PKG-MK"]'),

    ("MK-130", "PKG_MK_PHASE11", "assessment",
     "H1 Deliberate Pipeline assessment: CONFIRMED as ORIGIN authorization (0.85-0.90) — Dulles managed unified covert governance portfolio. REJECTED as CONTINUOUS pipeline (0.10-0.15) — no evidence of directive control over Synanon→Seed→Straight development. No CIA direction of Synanon at any point in 30 years (0.85 negative).",
     0.85, '["E1", "E2", "phase11", "h1_assessment", "origin_confirmed", "continuous_rejected", "PKG-MK"]'),

    ("MK-131", "PKG_MK_PHASE11", "assessment",
     "H2 Opportunistic Adoption (0.55-0.65, BEST INDIVIDUAL FIT): correctly describes civilian side (Dederich, Chavez, Seed, Straight all adopted volitionally). But understates intelligence side — CIA funded research, maintained institutional vectors, deployed at least one probable dual-function operative (West) across decades. H2 describes civilian adoption pattern, not full intelligence posture.",
     0.60, '["E2", "phase11", "h2_best_fit", "opportunistic_adoption", "PKG-MK"]'),

    ("MK-132", "PKG_MK_PHASE11", "assessment",
     "H3 Convergent Evolution (0.40-0.50, PARTIALLY VALID): correctly identifies technique discoverability — ego destruction and coercive group techniques ARE independently discoverable across cultures and centuries. But CANNOT account for specific documented chains: Dederich LSD session, Seed from Synanon, Straight from Seed, Chavez from Synanon. These are not convergence — they are documented lineage transfers.",
     0.45, '["E2", "phase11", "h3_convergence", "partially_valid", "documented_chains", "PKG-MK"]'),

    ("MK-133", "PKG_MK_PHASE11", "assessment",
     "H4 MK-COINTELPRO Integration (0.20-0.30): CACTUS proves infrastructure for technique transfer existed. But no documented evidence of actual MK behavioral technique transfer to FBI. COINTELPRO techniques were consistent with FBI institutional culture (blunt-force disruption) rather than sophisticated behavioral modification.",
     0.25, '["E2", "phase11", "h4_mk_cointelpro", "infrastructure_exists", "no_transfer_documented", "PKG-MK"]'),

    ("MK-134", "PKG_MK_PHASE11", "assessment",
     "H5 Behavioral Weaponization Against Movements: REJECTED in strong form (0.15-0.25, zero affirmative evidence for deliberate targeting). But identifies genuine COINTELPRO-MK second-order effect: intelligence agencies created both the behavioral technology (MK) AND the conditions of paranoia (COINTELPRO) under which a targeted leader adopted authoritarian methods. Two programs converged on UFW without coordination.",
     0.40, '["E2", "E3", "phase11", "h5_weaponization", "rejected_strong", "second_order_effect", "PKG-MK"]'),

    ("MK-135", "PKG_MK_PHASE11", "assessment",
     "The COINTELPRO-MK second-order effect: intelligence agencies created both (a) the behavioral technology and (b) the conditions of paranoia under which a targeted leader would seek authoritarian control tools. Not conspiracy — emergent property of a surveillance state's overlapping operations. Chavez case is single documented instance. Confidence: 0.35-0.45.",
     0.40, '["E2", "E3", "phase11", "second_order_effect", "emergent_property", "chavez_instance", "PKG-MK"]'),

    ("MK-136", "PKG_MK_PHASE11", "assessment",
     "Accountability chain — three institutional actors had power to interrupt the MK→Synanon→Straight→399 deaths chain and did not: (1) CIA funded research with no downstream tracking protocol, then destroyed records; (2) U.S. Senate found Seed=brainwashing but took no structural action; (3) Republican establishment rewarded Sembler with ambassadorships after documented abuse.",
     0.80, '["E1", "E2", "phase11", "accountability_chain", "three_failures", "PKG-MK"]'),

    ("MK-137", "PKG_MK_PHASE11", "assessment",
     "The chain persisted not because of conspiracy but because of INCENTIVE ALIGNMENT. Each participant had independent motivations — scientific prestige (MK researchers), organizational control (Dederich, Chavez), profit (troubled teen operators), political access (Sembler) — that were individually rational and collectively produced systematic harm.",
     0.80, '["E2", "phase11", "incentive_alignment", "no_conspiracy", "systematic_harm", "PKG-MK"]'),

    ("MK-138", "PKG_MK_PHASE11", "assessment",
     "West's Sirhan psychic driving claim is analytically significant: demonstrates familiarity with Cameron's classified Subproject 68 methodology and willingness to identify it in operational context. Either (a) sufficiently familiar with classified MK techniques to identify them in field, or (b) making claims based on own classified knowledge. Either supports dual-function model.",
     0.55, '["E2", "phase11", "west_sirhan_significance", "classified_technique_knowledge", "PKG-MK"]'),

    ("MK-139", "PKG_MK_PHASE11", "assessment",
     "The 1973 Helms destruction is the permanent epistemic constraint on every assessment: evidence AGAINST intelligence involvement survives (civilian records showing volitional adoption). Evidence FOR intelligence involvement may have been destroyed (operational tasking). This asymmetry must be acknowledged but cannot reverse the burden of evidence.",
     0.90, '["E1", "phase11", "helms_destruction_constraint", "epistemic_asymmetry", "PKG-MK"]'),

    ("MK-140", "PKG_MK_PHASE11", "assessment",
     "The system is dangerous BOTH because of its conspiratorial origin (central authorization under Dulles) AND its emergent continuation (self-sustaining ecosystem post-exposure). Central authorization created the techniques and seeded them into institutional pathways. Emergent diffusion ensured they survived the exposure of their origin. Combination is more resilient than either alone.",
     0.75, '["E2", "phase11", "dual_danger", "designed_origin", "organic_persistence", "PKG-MK"]'),

    # =========================================================================
    # PHASE 12: Cross-Campaign Integration (MK-141 to MK-155)
    # =========================================================================
    ("MK-141", "PKG_MK_PHASE12", "assessment",
     "Three campaigns (PKG-MK, PKG-EP, PKG-911) independently converged on structurally identical conclusions: NOT centrally directed conspiracies, NOT random coincidence, but ECOSYSTEMS where institutional incentives, personnel overlap, and shared techniques produce coordinated-appearing outcomes without a command structure. Cross-campaign convergence confidence: 0.75-0.85.",
     0.80, '["E2", "phase12", "three_campaign_convergence", "ecosystem_model", "PKG-MK"]'),

    ("MK-142", "PKG_MK_PHASE12", "assessment",
     "Operation Midnight Climax is the documented origin node connecting MK behavioral research to sexual blackmail tradecraft running through Cohn to Epstein. Technique genealogy (sexual entrapment + recording + targeting officials + institutional cover) documented at structural level (0.65-0.75). Direct personnel chain: NOT documented (0.10-0.15). Ecosystem diffusion: BEST FIT (0.40-0.50).",
     0.60, '["E1", "E2", "phase12", "midnight_climax_genealogy", "cohn_epstein", "PKG-MK"]'),

    ("MK-143", "PKG_MK_PHASE12", "assessment",
     "Allen Dulles authorized MK-Ultra, Gladio, Mockingbird simultaneously while directing coups for Sullivan & Cromwell clients. Behavioral, paramilitary, media, and geopolitical control operated as a single portfolio managed by a single individual. The 1953 inflection point validated at 0.93 confidence. Dulles unified portfolio confidence: 0.75-0.85.",
     0.80, '["E1", "phase12", "dulles_unified_portfolio", "1953_inflection", "PKG-MK"]'),

    ("MK-144", "PKG_MK_PHASE12", "assessment",
     "Roy Cohn as multi-domain convergence node (0.75-0.85): simultaneously connects MK-adjacent sexual blackmail, COINTELPRO-era political blackmail, organized crime networks (Genovese/Bonanno/Gambino), and social networks constituting the later Epstein ecosystem. Greenberg bridge: Cohn friend (1983, E1) AND Epstein patron (1976, E1). Cohn as deliberate Epstein network constructor: 0.15-0.25.",
     0.80, '["E1", "E2", "phase12", "cohn_convergence_node", "multi_domain", "greenberg_bridge", "PKG-MK"]'),

    ("MK-145", "PKG_MK_PHASE12", "assessment",
     "Revolving door pattern validated across three campaigns — structurally identical mechanism in different domains: DuPont (government→behavioral control→drug testing profit), Krongard (Wall Street→CIA→defense contracting), Sembler (behavioral control→fundraising→ambassadorships). NOT corruption in conventional sense — SYSTEM DESIGN producing outcomes automatically through incentive alignment.",
     0.85, '["E1", "E2", "phase12", "revolving_door", "dupont_krongard_sembler", "system_design", "PKG-MK"]'),

    ("MK-146", "PKG_MK_PHASE12", "assessment",
     "Institutional capture pattern validated across domains: Wexner (philanthropy→institutional loyalty→accountability insulation), Sembler (fundraising→partisan loyalty→protection from abuse documentation), Synanon (elite patronage→social legitimacy→regulatory insulation). Cross-campaign validation confidence: 0.80-0.85.",
     0.80, '["E2", "phase12", "institutional_capture", "wexner_sembler_synanon", "cross_campaign", "PKG-MK"]'),

    ("MK-147", "PKG_MK_PHASE12", "assessment",
     "Five-program model: Gladio (what happens in foreign countries), Mockingbird (what people think), MK-Ultra (how people behave), COINTELPRO (what people do politically), CHAOS (what government knows about people). Every major domain of human social activity had a corresponding covert program. The Church Committee's program-by-program approach missed the systemic picture. Confidence: 0.65-0.75.",
     0.70, '["E1", "E2", "phase12", "five_program_model", "covert_governance", "church_committee_failure", "PKG-MK"]'),

    ("MK-148", "PKG_MK_PHASE12", "assessment",
     "PKG-MK evidence strengthens JXQ-012 ('managed events as governance tool') convergence from 0.90 to 0.92. MK-Ultra adds the behavioral control dimension — governance through covert manipulation of human psychology itself. Combined with Gladio, Mockingbird, coups: comprehensive covert governance architecture validated.",
     0.92, '["E1", "E2", "phase12", "jxq_012_upgrade", "managed_events", "0.92", "PKG-MK"]'),

    ("MK-149", "PKG_MK_PHASE12", "assessment",
     "The semi-emergent ecosystem is a governance mode: (1) initial state creation by powerful institution, (2) institutional diffusion through documented pathways, (3) volitional adoption by others for their own interests, (4) network reinforcement, (5) accountability diffusion to point of untraceable, (6) self-perpetuation beyond originators' involvement. Pattern operates across behavioral, financial, and institutional control domains.",
     0.80, '["E2", "phase12", "semi_emergent_ecosystem", "governance_mode", "six_features", "PKG-MK"]'),

    ("MK-150", "PKG_MK_PHASE12", "assessment",
     "Esalen-SRI remote viewing bridge connects PKG-MK findings to existing Sherlock targets (Puthoff, Swann, Price, McMoneagle). Chain: MK research ecosystem → consciousness research community → Esalen as convergence venue → Esalen-SRI personnel overlap → CIA-funded remote viewing → Stargate. B-type (structural/institutional) transfer. Andrija Puharich most direct intelligence-to-Esalen bridge.",
     0.75, '["E1", "E2", "phase12", "esalen_sri_bridge", "remote_viewing", "puthoff_swann", "PKG-MK"]'),

    ("MK-151", "PKG_MK_PHASE12", "assessment",
     "The Sherlock evidence base, across three major campaigns and 1,000+ documented claims, consistently finds that the most dangerous outcomes arise not from centralized conspiracy but from self-sustaining ecosystems producing conspiracy-like outcomes through distributed incentive alignment. More analytically dangerous than conspiracy because it cannot be defeated by exposing a single command structure.",
     0.75, '["E2", "phase12", "fundamental_finding", "ecosystem_danger", "no_single_command", "PKG-MK"]'),

    ("MK-152", "PKG_MK_PHASE12", "assessment",
     "Midnight Climax→Cohn→Epstein technique evolution: experimental→operational→scaled. Midnight Climax used prostitutes (CIA payroll), LSD, one-way glass. Cohn used minors (organized crime supply), recording equipment, Plaza Hotel Suite 233. Epstein used minors, recording equipment in Manhattan/islands, financial/intelligence leverage. Pharmacological element divergent (present only in Midnight Climax).",
     0.65, '["E1", "E2", "phase12", "sexual_blackmail_evolution", "experimental_to_scaled", "PKG-MK"]'),

    ("MK-153", "PKG_MK_PHASE12", "factual",
     "Craig Spence — who operated a parallel CIA-connected sexual blackmail ring in Washington DC in the 1980s — hosted Cohn's birthday party, with CIA Director William Casey in attendance. Casey 'called Roy almost daily' during the 1980 Reagan campaign. Judge David Peck, 'long-time associate' of Allen Dulles, placed Cohn at his first private firm in 1955.",
     0.65, '["E2", "phase12", "spence_cohn_casey", "dulles_peck_cohn", "network_connections", "PKG-MK"]'),

    ("MK-154", "PKG_MK_PHASE12", "assessment",
     "The Church Committee's compartmented investigation — examining MK-Ultra, COINTELPRO, CHAOS, HTLINGUAL as separate programs — missed the CACTUS channel entirely and failed to investigate cross-program coordination systematically. This may have been the most consequential analytical failure in congressional oversight history. Confidence: 0.80-0.85.",
     0.82, '["E1", "E2", "phase12", "church_committee_failure", "compartmented_approach", "PKG-MK"]'),

    ("MK-155", "PKG_MK_PHASE12", "assessment",
     "The accountability deficit is structural, not incidental. Ecosystems distribute responsibility to the point of legal untraceability. Each actor credibly claims independence. System-level harm is real; system-level responsibility is diffused beyond prosecution. Documented across PKG-MK ($15M settlements, 399 deaths, no executive imprisonment), PKG-EP, and PKG-911.",
     0.80, '["E2", "phase12", "accountability_deficit", "structural", "diffused_responsibility", "PKG-MK"]'),
]

# =============================================================================
# CROSS-REFERENCES — ~80 cross-refs
# Each: (xref_id, entity1, entity2, relationship_type, source_claims, confidence)
# =============================================================================

CROSS_REFS = [
    # =========================================================================
    # WITHIN PKG-MK: Inter-phase connections
    # =========================================================================
    ("xref_mk_001",
     "Dederich LSD session Aug 28 1957 (Cohen/Ditman)",
     "Synanon Game development (attack therapy methodology)",
     "origin_event", "MK-021,MK-022,MK-023", 0.85),

    ("xref_mk_002",
     "Synanon Game methodology",
     "Chavez UFW adoption Feb 1977 (E1 documented volitional transfer)",
     "technique_transfer", "MK-043,MK-044,MK-045", 0.95),

    ("xref_mk_003",
     "Synanon methods",
     "The Seed (Art Barker, 1970, adapted Game for adolescents)",
     "organizational_derivation", "MK-028,MK-104", 0.75),

    ("xref_mk_004",
     "The Seed defunded (Senate brainwashing finding 1974)",
     "Straight Inc. founding (Sembler, 1976, identical methods)",
     "organizational_succession", "MK-105,MK-106", 0.90),

    ("xref_mk_005",
     "Straight Inc. methods (50K+ youth)",
     "Troubled teen industry (10K+ programs, 399 deaths)",
     "institutional_diffusion", "MK-106,MK-112,MK-115", 0.85),

    ("xref_mk_006",
     "MK-Ultra 7 core techniques (Phase 1 taxonomy)",
     "Synanon Game parallels (8 technique matches)",
     "technique_parallel", "MK-002,MK-014", 0.65),

    ("xref_mk_007",
     "MK-Ultra 7 core techniques",
     "Peoples Temple 7 technique parallels (Phase 10)",
     "technique_parallel", "MK-002,MK-127", 0.80),

    ("xref_mk_008",
     "MK-Ultra 7 core techniques",
     "UFW under Chavez — 4/7 highest overlap (Phase 4)",
     "technique_overlap", "MK-002,MK-046", 0.85),

    ("xref_mk_009",
     "MK-Ultra 7 core techniques",
     "Straight Inc. — 5/6 core technique mapping (Phase 9)",
     "technique_mapping", "MK-002,MK-015,MK-106", 0.85),

    ("xref_mk_010",
     "Cohen/Ditman at VA Wadsworth Hospital",
     "VA Hospital system as documented MK-Ultra institutional vector",
     "institutional_vector", "MK-033,MK-038", 0.60),

    ("xref_mk_011",
     "West Subproject 43 (hypnosis/dissociation, 1955)",
     "West Ruby visit (psychotic break diagnosis, 1964)",
     "operative_continuity", "MK-006,MK-093", 0.75),

    ("xref_mk_012",
     "West Subproject 43",
     "West Hearst evaluation (alongside Orne SP-84, Lifton)",
     "operative_continuity", "MK-006,MK-098", 0.85),

    ("xref_mk_013",
     "West Subproject 43",
     "West Haight-Ashbury CIA-funded lab (1966-1967)",
     "operative_continuity", "MK-006,MK-063,MK-100", 0.85),

    ("xref_mk_014",
     "West Sirhan psychic driving claim",
     "Cameron Subproject 68 psychic driving technique",
     "technique_identification", "MK-005,MK-097", 0.65),

    ("xref_mk_015",
     "Carl Rogers CIA Human Ecology Fund board (witting, 1957)",
     "Carl Rogers encounter group methodology development",
     "A_type_pathway", "MK-007,MK-061,MK-083", 0.90),

    ("xref_mk_016",
     "CACTUS channel (CIA CHAOS↔FBI COINTELPRO)",
     "Five interagency coordination channels (Phase 6)",
     "interagency_coordination", "MK-070,MK-071", 0.70),

    ("xref_mk_017",
     "COINTELPRO-induced paranoia in UFW",
     "Chavez adoption of Game (receptivity hypothesis)",
     "second_order_effect", "MK-050,MK-053,MK-135", 0.45),

    ("xref_mk_018",
     "DuPont NIDA funding of The Seed ($1.8M)",
     "DuPont post-government Straight Inc. consultancy",
     "revolving_door", "MK-104,MK-109", 0.90),

    ("xref_mk_019",
     "Sembler Straight Inc. abuse documentation",
     "Sembler RNC Finance Chairman + two ambassadorships",
     "political_protection", "MK-107,MK-108", 0.95),

    ("xref_mk_020",
     "Helms 1973 records destruction",
     "Permanent epistemic constraint on all MK analysis",
     "evidential_constraint", "MK-003,MK-017,MK-139", 0.95),

    ("xref_mk_021",
     "Dulles unified portfolio (MK-Ultra+Gladio+Mockingbird+coups, 1953)",
     "Phased Ecosystem Model Phase A central authorization",
     "origin_architecture", "MK-001,MK-129,MK-143", 0.85),

    ("xref_mk_022",
     "Bateson OSS psychological warfare",
     "Bateson as Esalen founding intellectual",
     "personnel_bridge", "MK-081", 0.85),

    ("xref_mk_023",
     "Jones-Mitrione Belo Horizonte overlap (1960-1962)",
     "CIA 201 file on Jones (opened ~1960, purged after Mitrione death 1970)",
     "intelligence_connection", "MK-117,MK-118", 0.55),

    ("xref_mk_024",
     "Synanon Northern California ecosystem",
     "Peoples Temple Northern California ecosystem",
     "geographic_ecosystem", "MK-126", 0.70),

    ("xref_mk_025",
     "Convergence Problem (Phase 5)",
     "Convergence Problem confirmed (Phase 10)",
     "analytical_continuity", "MK-064,MK-123", 0.80),

    ("xref_mk_026",
     "Nancy Reagan Straight Inc. visit (1982, 1985)",
     "War on Drugs political environment enabling behavioral control",
     "political_endorsement", "MK-110,MK-114", 0.90),

    ("xref_mk_027",
     "Incentive alignment model (Phase 11)",
     "Three-campaign convergence on ecosystem model (Phase 12)",
     "analytical_convergence", "MK-137,MK-141", 0.80),

    ("xref_mk_028",
     "Five-program model (Gladio+Mockingbird+MK+COINTELPRO+CHAOS)",
     "Church Committee compartmented failure to detect CACTUS",
     "oversight_failure", "MK-147,MK-154", 0.80),

    ("xref_mk_029",
     "Lewin OSS psychological warfare advisor",
     "NTL T-group development (ONR funding, not CIA)",
     "intellectual_lineage", "MK-056,MK-057", 0.85),

    ("xref_mk_030",
     "West UCLA Violence Center proposal (1972)",
     "West CIA-funded Haight-Ashbury lab (1966-1967)",
     "institutional_continuity", "MK-099,MK-100", 0.75),

    # =========================================================================
    # TO EXISTING SHERLOCK EVIDENCE: Cross-campaign connections
    # =========================================================================

    # Midnight Climax / Epstein genealogy
    ("xref_mk_031",
     "Operation Midnight Climax (MK-Ultra sexual entrapment)",
     "RCSB-004 (Midnight Climax existing Sherlock evidence)",
     "direct_reference", "MK-142,MK-152", 0.95),

    ("xref_mk_032",
     "Midnight Climax sexual blackmail technique",
     "Cohn sexual blackmail network (PKG-EP: Plaza Hotel Suite 233)",
     "technique_genealogy", "MK-142,MK-152", 0.65),

    ("xref_mk_033",
     "Cohn sexual blackmail network",
     "Epstein sexual blackmail operation (PKG-EP documentation)",
     "technique_genealogy", "MK-142,MK-152", 0.60),

    ("xref_mk_034",
     "Greenberg as Cohn friend (1983 dinner, E1)",
     "Greenberg as Epstein patron at Bear Stearns (1976-2008, E1)",
     "human_bridge", "MK-144", 0.85),

    # Allen Dulles connections
    ("xref_mk_035",
     "Dulles MK-Ultra authorization (April 13, 1953)",
     "Allen Dulles (existing Sherlock target)",
     "program_authorization", "MK-001,MK-143", 0.95),

    ("xref_mk_036",
     "Dulles unified portfolio (MK+Gladio+Mockingbird+coups)",
     "1953 inflection point (validated at 0.93 in Sherlock DB)",
     "temporal_convergence", "MK-143", 0.93),

    ("xref_mk_037",
     "Dulles on Warren Commission (knew West's CIA work)",
     "Warren Commission failure to investigate MK context of Ruby breakdown",
     "conflict_of_interest", "MK-094", 0.90),

    # Roy Cohn / COINTELPRO connections
    ("xref_mk_038",
     "Cohn multi-domain convergence (MK-adjacent blackmail + COINTELPRO + OC + Epstein)",
     "Roy Cohn intelligence profile (existing PKG-EP evidence)",
     "convergence_node", "MK-144,MK-153", 0.80),

    ("xref_mk_039",
     "FBI COINTELPRO psychological warfare techniques",
     "MK behavioral modification techniques (parallel development)",
     "technique_parallel", "MK-067,MK-073,MK-077", 0.50),

    ("xref_mk_040",
     "Cohn-Casey daily calls during 1980 Reagan campaign",
     "CIA Director Casey (PKG-EP: IC connections)",
     "political_intelligence_nexus", "MK-153", 0.70),

    # Remote viewing / existing targets
    ("xref_mk_041",
     "Esalen-SRI remote viewing nexus (Phase 7)",
     "Hal Puthoff (existing Sherlock target)",
     "program_bridge", "MK-082,MK-150", 0.80),

    ("xref_mk_042",
     "Esalen-SRI remote viewing nexus",
     "Ingo Swann (existing Sherlock target)",
     "program_bridge", "MK-082,MK-150", 0.80),

    ("xref_mk_043",
     "SRI remote viewing program → CIA Stargate",
     "Pat Price (existing Sherlock target)",
     "program_bridge", "MK-082,MK-150", 0.80),

    ("xref_mk_044",
     "First Earth Battalion / INSCOM",
     "Joseph McMoneagle (existing Sherlock target)",
     "institutional_bridge", "MK-087,MK-150", 0.75),

    # JXQ-012 managed events upgrade
    ("xref_mk_045",
     "PKG-MK evidence (MK-Ultra + five-program model)",
     "JXQ-012 (Jiang managed events thesis: 0.90→0.92)",
     "convergence_upgrade", "MK-148", 0.92),

    # Wexner / Krongard institutional capture parallels
    ("xref_mk_046",
     "Sembler institutional capture (fundraising→partisan loyalty→protection)",
     "Wexner institutional capture (philanthropy→loyalty→accountability insulation)",
     "structural_parallel", "MK-146", 0.80),

    ("xref_mk_047",
     "DuPont revolving door (government→behavioral control→testing profit)",
     "Krongard revolving door (Wall Street→CIA→defense contracting)",
     "structural_parallel", "MK-109,MK-145", 0.85),

    # PKG-EP cross-references
    ("xref_mk_048",
     "PKG-MK ecosystem model (0.70-0.80)",
     "PKG-EP semi-emergent profiteering ecosystem (0.55-0.65)",
     "analytical_convergence", "MK-141,MK-149", 0.80),

    ("xref_mk_049",
     "PKG-MK ecosystem model",
     "PKG-911 three analytically separable circuits (0.65-0.75)",
     "analytical_convergence", "MK-141,MK-149", 0.75),

    ("xref_mk_050",
     "Spence CIA-connected blackmail ring (1980s Washington DC)",
     "Epstein sexual blackmail operation (late 1980s-2019)",
     "parallel_operation", "MK-153", 0.55),

    # CIA-labor to existing evidence
    ("xref_mk_051",
     "CIA-labor nexus (Lovestone/Brown/AIFLD, E1 documented)",
     "Sullivan & Cromwell synthesis (3 CIA coups for S&C clients)",
     "institutional_parallel", "MK-059", 0.85),

    ("xref_mk_052",
     "AIFLD involvement in Chile coup (1973)",
     "Allen Dulles geopolitical operations portfolio",
     "operational_continuity", "MK-059,MK-143", 0.80),

    # NED successor
    ("xref_mk_053",
     "NED (1983) as formalized successor to CIA covert labor operations",
     "AIFLD/ACILS institutional continuity",
     "institutional_succession", "MK-068", 0.90),

    # Helms destruction impact
    ("xref_mk_054",
     "Helms 1973 records destruction",
     "Documentary gap preventing resolution of Cohen-CIA question",
     "evidential_constraint", "MK-003,MK-034,MK-039", 0.90),

    ("xref_mk_055",
     "Helms 1973 records destruction",
     "Documentary gap preventing resolution of MK-COINTELPRO integration",
     "evidential_constraint", "MK-003,MK-073", 0.85),

    # Fred Hampton / COINTELPRO
    ("xref_mk_056",
     "Hampton drugging by FBI informant O'Neal (secobarbital before raid)",
     "MK pharmacological techniques (parallel institutional tradecraft)",
     "technique_parallel", "MK-066", 0.60),

    # Highlander as counter-example
    ("xref_mk_057",
     "Highlander Folk School (suppression NOT infiltration model)",
     "State response to movement training = suppression not technique insertion",
     "counter_example", "MK-069", 0.85),

    # Accountability failures across campaigns
    ("xref_mk_058",
     "Straight Inc. accountability failure ($15M settlements, Sembler rewarded)",
     "Epstein accountability failure (death in custody, JPMorgan fines only)",
     "structural_parallel", "MK-136,MK-155", 0.80),

    ("xref_mk_059",
     "Straight Inc. accountability failure",
     "PKG-911 accountability failure (Blackwater pardons, no prosecution)",
     "structural_parallel", "MK-136,MK-155", 0.80),

    # West at multiple cases — overarching pattern
    ("xref_mk_060",
     "West at Ruby (1964), Haight-Ashbury (1967), Sirhan (1969), Hearst (1975), McVeigh (1995)",
     "Statistical improbability of single MK researcher at 5 high-profile cases",
     "pattern_analysis", "MK-093,MK-097,MK-098,MK-100,MK-101,MK-102", 0.55),

    # Technique spectrum
    ("xref_mk_061",
     "Behavioral modification technique spectrum (therapeutic to coercive)",
     "Rogers encounter group (therapeutic) → Esalen marathon → est → Synanon Game → Cameron depatterning → KUBARK (coercive)",
     "technique_spectrum", "MK-007,MK-023,MK-085,MK-005,MK-008", 0.80),

    # Phase 2/Phase 10 parallel organization trajectories
    ("xref_mk_062",
     "Synanon organizational trajectory (legitimate→authoritarian→violent→collapse, 1958-1991)",
     "Peoples Temple trajectory (legitimate→authoritarian→violent→massacre, 1955-1978)",
     "parallel_trajectory", "MK-024,MK-116,MK-126", 0.70),

    # Bill Wilson / AA
    ("xref_mk_063",
     "Bill Wilson LSD session under Cohen (Aug 29, 1956)",
     "Dederich LSD session under Cohen/Ditman (Aug 28, 1957)",
     "same_research_program", "MK-036,MK-021", 0.85),

    # KUBARK lineage
    ("xref_mk_064",
     "KUBARK manual (1963) synthesizing MK behavioral research",
     "1983 Human Resource Exploitation Training Manual (KUBARK derivative)",
     "institutional_derivation", "MK-008,MK-079", 0.85),

    # Puharich to Esalen to remote viewing
    ("xref_mk_065",
     "Puharich (CIA asset) → The Nine → O'Connor → Esalen governance",
     "Esalen-SRI remote viewing research nexus",
     "intelligence_penetration", "MK-084,MK-082", 0.65),

    # DuPont-Krongard parallel (detailed)
    ("xref_mk_066",
     "DuPont: government authority → funded behavioral control → profited from drug testing",
     "Krongard: investment bank → CIA → defense contractor boards",
     "revolving_door_parallel", "MK-109,MK-145", 0.85),

    # Negative findings as analytical value
    ("xref_mk_067",
     "NEGATIVE: No MK as organizing tools in labor/civil rights (Phase 5, 0.85)",
     "NEGATIVE: No intelligence connections to Chavez advisors (Phase 4, 0.85)",
     "negative_finding_cluster", "MK-051,MK-052,MK-058,MK-060", 0.85),

    ("xref_mk_068",
     "NEGATIVE: HPM NOT CIA creation (Phase 7, 0.15-0.25 deployment)",
     "NEGATIVE: No Erhard-CIA link (Phase 7)",
     "negative_finding_cluster", "MK-080,MK-086,MK-091", 0.80),

    ("xref_mk_069",
     "NEGATIVE: No MK technique transfer to FBI COINTELPRO documented",
     "NEGATIVE: Hoover firewall preventing formal integration",
     "negative_finding_cluster", "MK-073,MK-075", 0.75),

    # Senate brainwashing finding to existing targets
    ("xref_mk_070",
     "Senate finding: The Seed = North Korean brainwashing (E1, 0.95)",
     "MK-Ultra target ID 13 (existing Sherlock target)",
     "program_derivation", "MK-105,MK-115", 0.85),

    # Northern California ecosystem density
    ("xref_mk_071",
     "Northern California behavioral ecosystem (Synanon, PT, Esalen, SRI, Haight-Ashbury, est)",
     "West's Haight-Ashbury CIA-funded lab as ecosystem intelligence node",
     "geographic_intelligence_nexus", "MK-063,MK-100,MK-126", 0.70),

    # Accountability chain: complete
    ("xref_mk_072",
     "MK-Ultra research (1953-1964) → Cohen/Ditman → Dederich → Synanon → Seed → Straight → TTI → 399 deaths",
     "Accountability chain: CIA + Senate + Republican establishment all failed to interrupt",
     "accountability_chain", "MK-115,MK-136", 0.75),

    # Cross-campaign ecosystem validation
    ("xref_mk_073",
     "PKG-MK: central coordination REJECTED (0.05-0.10)",
     "PKG-EP: central coordination REJECTED (0.05-0.10)",
     "analytical_convergence", "MK-130,MK-141", 0.80),

    ("xref_mk_074",
     "PKG-MK: complete coincidence REJECTED (0.15-0.20)",
     "PKG-EP: complete coincidence REJECTED (0.10-0.15)",
     "analytical_convergence", "MK-132,MK-141", 0.80),

    # Specific personnel bridges to existing evidence
    ("xref_mk_075",
     "Gottlieb ordered records destruction + ran MK-Ultra",
     "Helms ordered destruction as DCI (Gottlieb executed)",
     "operational_chain", "MK-003,MK-004", 0.95),

    ("xref_mk_076",
     "West at Ruby in Dallas (1964)",
     "Dulles on Warren Commission (knew West's CIA work)",
     "conflict_of_interest", "MK-093,MK-094", 0.85),

    # Sembler-DuPont revolving door to existing campaigns
    ("xref_mk_077",
     "Sembler ambassadorship pattern (abuse documented → political reward)",
     "PKG-911 Krongard pattern (financial anomalies → CIA appointment → defense contracts)",
     "revolving_door_cross_campaign", "MK-108,MK-145", 0.80),

    # Phase 12 five-program model to existing Gladio/Mockingbird evidence
    ("xref_mk_078",
     "Five-program covert governance model (Phase 12)",
     "Operation Gladio (existing Sherlock evidence, 45-year program)",
     "unified_architecture", "MK-147", 0.75),

    ("xref_mk_079",
     "Five-program covert governance model",
     "Operation Mockingbird (existing evidence, 400+ media assets)",
     "unified_architecture", "MK-147", 0.80),

    # Jonestown to existing PTJ evidence
    ("xref_mk_080",
     "Mitrione USAID/OPS (CIA-covered torture training in Latin America)",
     "AIFLD coups in Brazil (1964) and Chile (1973) (CIA-labor nexus)",
     "institutional_parallel", "MK-059,MK-117", 0.75),
]


def ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    sources_added = 0
    claims_added = 0
    claims_skipped = 0
    xrefs_added = 0
    xrefs_skipped = 0

    # ---- Register sources ----
    for src in SOURCES:
        c.execute("SELECT source_id FROM evidence_sources WHERE source_id = ?",
                  (src["source_id"],))
        if c.fetchone():
            print(f"SKIP source {src['source_id']}: already exists")
        else:
            c.execute("""
                INSERT INTO evidence_sources
                    (source_id, title, file_path, evidence_type, created_at, ingested_at, processing_status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, 'complete', ?)
            """, (
                src["source_id"],
                src["title"],
                src["file_path"],
                src["evidence_type"],
                now, now,
                json.dumps(src["metadata"], indent=2),
            ))
            sources_added += 1
            print(f"Added source: {src['source_id']}")

    # ---- Insert claims ----
    for claim_id, source_id, claim_type, text, confidence, tags in CLAIMS:
        c.execute("SELECT claim_id FROM evidence_claims WHERE claim_id = ?",
                  (claim_id,))
        if c.fetchone():
            claims_skipped += 1
            continue

        c.execute("""
            INSERT INTO evidence_claims
                (claim_id, source_id, claim_type, text, confidence, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, source_id, claim_type, text, confidence, tags, now))
        claims_added += 1

    # ---- Insert cross-references ----
    for xref_id, entity1, entity2, rel_type, source_claims, confidence in CROSS_REFS:
        c.execute("SELECT xref_id FROM cross_references WHERE xref_id = ?",
                  (xref_id,))
        if c.fetchone():
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
    c.execute("SELECT COUNT(*) FROM targets")
    total_targets = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM evidence_sources")
    total_sources = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM evidence_claims")
    total_claims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cross_references")
    total_xrefs = c.fetchone()[0]

    conn.close()

    print(f"\n{'='*60}")
    print(f"PKG-MK CAMPAIGN INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Sources added this run: {sources_added}")
    print(f"  Claims added this run:  {claims_added}")
    print(f"  Claims skipped (dupes): {claims_skipped}")
    print(f"  Xrefs added this run:   {xrefs_added}")
    print(f"  Xrefs skipped (dupes):  {xrefs_skipped}")
    print(f"{'='*60}")
    print(f"  DATABASE GRAND TOTALS:")
    print(f"    Total targets:        {total_targets}")
    print(f"    Total sources:        {total_sources}")
    print(f"    Total claims:         {total_claims}")
    print(f"    Total cross-refs:     {total_xrefs}")
    print(f"{'='*60}")


if __name__ == "__main__":
    ingest()
