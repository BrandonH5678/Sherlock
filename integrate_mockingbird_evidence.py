#!/usr/bin/env python3
"""
Operation Mockingbird Evidence Integration
Integrates CIA media manipulation and propaganda network intelligence into Sherlock

This represents systematic CIA control of global media apparatus (1950s-1970s+)
connecting to broader pattern of intelligence-media fusion documented in other operations.

Key Intelligence:
- "Wisner's Wurlitzer" - 800+ propaganda assets at peak
- 50+ owned/subsidized media entities worldwide
- 1,000+ books produced/subsidized
- Systematic "blowback" to American public acknowledged
- Integration with documented coups (Guatemala, Chile, Iran)

Architecture: Similar to MK-Ultra/Italy UFO/JFK integration
Output: Evidence sources, claims, speakers, relationships
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from evidence_database import (
    EvidenceDatabase, EvidenceType, ClaimType,
    EvidenceSource, EvidenceClaim, Speaker
)


class MockingbirdIntegrator:
    """Integrate Operation Mockingbird evidence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("mockingbird_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in Operation Mockingbird research
        self.entities = {
            'people': [
                'Frank G. Wisner', 'Tom Braden', 'Cord Meyer Jr.',
                'William E. Colby', 'Allen Dulles', 'John A. McCone',
                'Frederick Praeger', 'John Hay Whitney', 'David A. Phillips',
                'William F. Buckley Jr.', 'Peter Matthiessen', 'George Plimpton',
                'John M. Crewdson', 'Joseph B. Treaster'
            ],
            'organizations': [
                'Radio Free Europe', 'Radio Liberty', 'Radio Free Asia',
                'Congress of Cultural Freedom', 'Free Europe Committee',
                'American Committee for Liberation', 'Asia Foundation',
                'Forum World Features', 'Foreign News Service',
                'DENA', 'Agenda Orbe Latino American',
                'Rome Daily American', 'Paris Match', 'Encounter',
                'Praeger Publishing', 'Doubleday', 'Scribner\'s', 'Putnam\'s'
            ],
            'locations': [
                'Washington DC', 'New York', 'London', 'Paris', 'Rome',
                'Munich', 'Manila', 'Hong Kong', 'Rangoon', 'Athens'
            ],
            'operations': [
                'Operation Mockingbird', 'Wisner\'s Wurlitzer',
                'Propaganda Assets Inventory', 'KM FORGET'
            ],
            'concepts': [
                'blowback', 'replay', 'domestic fallout',
                'black propaganda', 'white propaganda',
                'proprietary media', 'witting assets', 'unwitting assets'
            ]
        }

    def add_speakers(self):
        """Add key Operation Mockingbird speakers to database"""
        print("\n📋 Adding Operation Mockingbird speakers...")

        speakers = [
            Speaker(
                speaker_id="frank_wisner",
                name="Frank G. Wisner",
                title="First Chief of CIA Covert Action Staff",
                organization="Central Intelligence Agency",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1947-01-01T00:00:00",
                last_seen="1965-10-29T00:00:00"  # Died 1965
            ),
            Speaker(
                speaker_id="tom_braden",
                name="Tom Braden",
                title="First Chief of CIA Propaganda Operations (later syndicated columnist)",
                organization="Central Intelligence Agency",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1950-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="cord_meyer_jr",
                name="Cord Meyer Jr.",
                title="Chief of CIA Propaganda Operations (many years)",
                organization="Central Intelligence Agency",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1951-01-01T00:00:00",
                last_seen="2001-03-13T00:00:00"  # Died 2001
            ),
            Speaker(
                speaker_id="john_crewdson",
                name="John M. Crewdson",
                title="New York Times Investigative Reporter",
                organization="The New York Times",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1977-12-25T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="frederick_praeger",
                name="Frederick Praeger",
                title="Publisher (CIA asset)",
                organization="Praeger Publishing",
                voice_embedding=None,
                confidence=0.9,
                first_seen="1957-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            )
        ]

        for speaker in speakers:
            try:
                self.db.add_speaker(speaker)
                print(f"  ✅ {speaker.name}")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"  ⚠️  {speaker.name} (already exists)")
                else:
                    raise

    def create_evidence_sources(self):
        """Create Operation Mockingbird evidence sources"""
        print("\n📄 Creating evidence sources...")

        sources = [
            EvidenceSource(
                source_id="nyt_mockingbird_1977_part1",
                title="The C.I.A.'s 3-Decade Effort To Mold the World's Views",
                url="https://www.nytimes.com/1977/12/25/archives/the-cias-3decade-effort-to-mold-the-worlds-views-agency-network.html",
                file_path="/home/johnny5/Downloads/The C.I.A.'s 3‐Decade Effort To Mold the World's Views - The New York Times.pdf",
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=22,
                created_at="1977-12-25T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'Operation Mockingbird',
                    'topic': 'CIA media manipulation and propaganda network',
                    'authors': 'John M. Crewdson, Joseph B. Treaster',
                    'publication': 'The New York Times',
                    'analysis_type': 'Investigative journalism exposing CIA media operations',
                    'significance': 'First comprehensive documentation of CIA global propaganda network'
                }
            ),
            EvidenceSource(
                source_id="nyt_mockingbird_1977_part2",
                title="Worldwide Propaganda Network Built by the C.I.A.",
                url="https://www.nytimes.com/1977/12/26/archives/worldwide-propaganda-network-built-by-the-cia-a-worldwide-network.html",
                file_path="/home/johnny5/Downloads/Worldwide Propaganda Network Built by the C.I.A. - The New York Times.pdf",
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=21,
                created_at="1977-12-26T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'Operation Mockingbird',
                    'topic': 'Detailed inventory of CIA-controlled media entities worldwide',
                    'authors': 'John M. Crewdson, Joseph B. Treaster',
                    'publication': 'The New York Times',
                    'analysis_type': 'Investigative journalism - part 2 of series',
                    'significance': 'Comprehensive list of CIA proprietary and influenced media'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✅ {source.source_id}")

    def extract_key_claims(self):
        """Extract key claims from Operation Mockingbird investigation"""
        print("\n🔍 Extracting key claims...")

        key_claims = [
            {
                'text': 'The CIA has been engaged for three decades in an "unremitting, though largely unrecognized, effort to shape foreign opinion in support of American policy abroad" through ownership, subsidization, or influence of newspapers, news agencies, and communications entities worldwide.',
                'context': 'Overview of Operation Mockingbird scope and duration',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': ['CIA'],
                'tags': ['mockingbird', 'propaganda', 'media-manipulation', 'three-decades'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The CIA\'s propaganda network was known officially as the "Propaganda Assets Inventory" but internally called "Wisner\'s Wurlitzer" after Frank G. Wisner, first chief of the agency\'s covert action staff. "Like the Mighty Wurlitzer, almost at the push of a button" it could orchestrate propaganda "in almost any language anywhere in the world."',
                'context': 'Official CIA terminology and operational metaphor',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': ['Frank G. Wisner', 'Propaganda Assets Inventory'],
                'tags': ['wisners-wurlitzer', 'propaganda-assets-inventory', 'covert-action', 'global-reach'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'At its peak a decade ago, the CIA\'s communications empire "embraced more than 800 news and public information organizations and individuals. They ranged in importance from Radio Free Europe to a third-string guy in Quito who could get something in the local paper."',
                'context': 'Scale of CIA propaganda network at peak (circa 1967)',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': ['Radio Free Europe'],
                'tags': ['800-assets', 'peak-operations', '1967', 'global-network'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The CIA has at various times owned or subsidized more than 50 newspapers, news services, radio stations, periodicals and other communications entities, sometimes in the US but mostly overseas, used as vehicles for propaganda efforts, as cover for operatives, or both. Another dozen foreign-based news organizations were infiltrated by paid CIA agents.',
                'context': 'CIA media ownership and infiltration',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': [],
                'tags': ['50-media-entities', 'owned-media', 'subsidized-media', 'infiltrated-media'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Nearly a dozen American publishing houses, including some of the most prominent names in the industry, have printed at least a score of the more than 250 English-language books financed or produced by the CIA since the early 1950s, in many cases without being aware of the agency\'s involvement.',
                'context': 'CIA book publishing operations',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': [],
                'tags': ['250-books', 'publishing-houses', 'unwitting-publishers', 'book-propaganda'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The CIA accepts, as an "unavoidable casualty" of its propaganda battles, that some news reaching American readers and viewers is tainted with disinformation. The agency coined terms to describe the phenomenon: "blowback," "replay," or "domestic fallout." A 1967 CIA directive stated simply that "fallout in the United States from a foreign publication which we support is inevitable and consequently permissible."',
                'context': 'CIA acknowledgment of domestic propaganda contamination',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': [],
                'tags': ['blowback', 'domestic-fallout', '1967-directive', 'inevitable-permissible'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Asked in an interview whether the CIA had ever told foreign journalists working as paid agents what to write, William E. Colby, the former CIA Director, replied: "Oh, sure, all the time."',
                'context': 'CIA Director admission of direct control over journalists',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': ['William E. Colby'],
                'tags': ['colby-admission', 'journalist-control', 'direct-orders', 'paid-agents'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The CIA used paid agents in the foreign bureaus of Associated Press and United Press International to slip agency-prepared dispatches onto the news wire. "We would not tell UPI or AP headquarters in the US when something was planted abroad," one CIA official said, and conceded such stories were likely transmitted over domestic news wires "if they were any good."',
                'context': 'CIA infiltration of major wire services',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 0.9,
                'entities': ['Associated Press', 'United Press International'],
                'tags': ['ap-infiltration', 'upi-infiltration', 'wire-service-manipulation', 'domestic-transmission'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'One of the CIA\'s most extensive propaganda campaigns was waged against Chilean President Salvador Allende in the years before his 1970 election and until his overthrow and death in 1973. Millions of dollars were spent to produce a "stream of anti-Allende stories, editorials and broadcasts throughout Latin America." A CIA propaganda assessment reported "continued replay of Chile theme materials" with "items also carried in New York Times, Washington Post."',
                'context': 'Chile coup propaganda campaign with documented US media pickup',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': ['Salvador Allende', 'New York Times', 'Washington Post'],
                'tags': ['chile-1973', 'allende-propaganda', 'millions-spent', 'nyt-wapo-pickup'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The CIA tampered with Khrushchev\'s 1956 "secret speech" denouncing Stalin. While the genuine expurgated version (missing 34 paragraphs on Soviet foreign policy) was released to US newspapers, another text containing 34 paragraphs "written not by Mr. Khrushchev\'s speechwriters, but by counterintelligence experts at CIA headquarters in Virginia" was distributed via Italian news agency ANSA and other channels worldwide.',
                'context': 'CIA fabrication and insertion into historical documents',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 0.9,
                'entities': ['Nikita Khrushchev', 'ANSA'],
                'tags': ['khrushchev-speech', '1956', 'document-fabrication', 'historical-tampering'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': '"The Penkovsky Papers" published by Doubleday in 1965 purported to be a journal kept by Soviet double agent Col. Oleg Penkovsky before his execution. However, "it was not a diary," said one CIA official, "and it was a major deception to that extent." The book was compiled from CIA records by Frank Gibney (Chicago Daily News employee) and Peter Deriahin (KGB defector employed by CIA).',
                'context': 'CIA fabrication of bestselling book as propaganda',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 0.95,
                'entities': ['Doubleday', 'Oleg Penkovsky', 'Frank Gibney'],
                'tags': ['penkovsky-papers', 'fabricated-diary', 'doubleday', 'major-deception'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Radio Free Europe and Radio Liberty were supported by the CIA until 1971, with the agency\'s participation shielded from public view by two front groups: the Free Europe Committee and the American Committee for Liberation, both of which also engaged in lesser-known propaganda operations.',
                'context': 'CIA broadcasting operations and front organizations',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 1.0,
                'entities': ['Radio Free Europe', 'Radio Liberty', 'Free Europe Committee', 'American Committee for Liberation'],
                'tags': ['rfe', 'radio-liberty', 'broadcasting', 'front-groups', 'until-1971'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The CIA subsidized several Cuban exile publications in Miami through a front called Foreign Publications Inc., with recipients including Avance, El Mundo, El Prensa Libre, Bohemia (which received more than $3 million), and El Diario de las Americas. The CIA also financed AIP, a radio news agency producing programs sent free to 100+ small stations in Central and Latin America.',
                'context': 'CIA funding of Cuban exile media network',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.95,
                'entities': ['Foreign Publications Inc', 'Bohemia'],
                'tags': ['cuban-exile-media', 'miami', '3-million-bohemia', 'latin-america-penetration'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The Congress of Cultural Freedom, a Paris-based CIA front, provided financial support to French magazine Preuves, Forum in Austria, Der Monat in West Germany, El Mundo Nuevo in Latin America, and in India the publications Thought and Quest. In the US, it supported Encounter (British journal).',
                'context': 'CIA cultural front organization media network',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.95,
                'entities': ['Congress of Cultural Freedom', 'Encounter'],
                'tags': ['congress-cultural-freedom', 'european-media', 'cultural-warfare'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Frederick Praeger, the book publisher, published "20 to 25 volumes in which the CIA had had an interest, either in the writing, the publication itself or the postpublication distribution." The CIA\'s involvement might be "reimbursing him directly for expenses of publication or guaranteeing, perhaps through a foundation, the purchase of enough copies to make publication worthwhile."',
                'context': 'CIA relationship with major publisher',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'frederick_praeger',
                'confidence': 0.95,
                'entities': ['Frederick Praeger'],
                'tags': ['praeger-publishing', '20-25-books', 'guaranteed-purchases', 'foundation-fronts'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The Rome Daily American was partly owned by the CIA from 1956 to 1964 "to keep it from falling into the hands of Italian Communists." After sale to Samuel W. Meek (J. Walter Thompson executive), it was managed for several years by Robert H. Cunningham, a CIA officer who had resigned and been rehired as contract employee.',
                'context': 'CIA newspaper ownership in Europe',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.9,
                'entities': ['Rome Daily American', 'Samuel W. Meek'],
                'tags': ['rome-daily-american', 'proprietary-newspaper', 'italy', 'communist-threat'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The CIA had "proprietary" English-language newspapers in other capitals including Athens and Rangoon, serving dual role of providing cover for intelligence operatives and publishing agency propaganda. "We \'had\' at least one newspaper in every foreign capital at any given time," one CIA man said.',
                'context': 'Global network of CIA-owned newspapers',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.85,
                'entities': [],
                'tags': ['proprietary-newspapers', 'every-capital', 'athens', 'rangoon', 'dual-purpose'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'In 1954, CIA Director Allen Dulles told a New York Times executive that Sydney Gruson, the newspaper\'s correspondent in Mexico, was not capable of reporting with objectivity on the impending revolution in Guatemala. Dulles said Secretary of State John Foster Dulles shared his concern. Arthur Hays Sulzberger (NYT publisher) complied by keeping Gruson away from Guatemala during the CIA-fostered revolution that overthrew Arbenz.',
                'context': 'CIA censorship of New York Times Guatemala coverage',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 0.95,
                'entities': ['Allen Dulles', 'Sydney Gruson', 'New York Times', 'Arthur Hays Sulzberger'],
                'tags': ['guatemala-1954', 'nyt-censorship', 'arbenz-coup', 'dulles-brothers'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Forum World Features, founded 1958 as Delaware corporation with offices in London, was owned during much of its life by John Hay Whitney (NY Herald Tribune publisher) who was "witting" of the agency\'s true role. At one time Forum had 30 domestic US newspapers as clients, including Washington Post. "The sale of Forum\'s material to Washington Post and other American newspapers put us in a hell of a dilemma," one CIA official said.',
                'context': 'CIA news service selling to American newspapers',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.9,
                'entities': ['Forum World Features', 'John Hay Whitney', 'Washington Post'],
                'tags': ['forum-world-features', '30-us-clients', 'washington-post', 'domestic-dilemma'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Tom Braden, first head of CIA propaganda operations (now syndicated columnist), said in interview he "had never really been sure that there was anybody in charge" of the operation and that "Frank Wisner kind of handled it off the top of his head." Cord Meyer Jr., who ran it for many years, declined to talk about the operation.',
                'context': 'CIA propaganda leadership and organization',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'tom_braden',
                'confidence': 0.9,
                'entities': ['Tom Braden', 'Frank G. Wisner', 'Cord Meyer Jr.'],
                'tags': ['braden', 'wisner', 'meyer', 'ad-hoc-management'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The Asia Foundation (formerly Committee for Free Asia) was headed for years by Robert Blum, who "several sources said, resigned from the CIA to take it over." The foundation provided cover for at least one CIA operative and carried out media ventures including a 1955 program paying expenses for Asian journalists to study in Harvard\'s Neiman Fellowship program.',
                'context': 'CIA Asia operations and journalist recruitment',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.85,
                'entities': ['Asia Foundation', 'Robert Blum', 'Harvard'],
                'tags': ['asia-foundation', 'neiman-fellowship', 'journalist-recruitment', 'cover-organization'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'William F. Buckley Jr. was a CIA agent for several years in the early 1950s. In 1951, Charles Scribner\'s Sons published "The Yenan Way" by Eudocio Ravines from a translation supplied by Buckley. Scribner\'s was unaware of any agency involvement.',
                'context': 'CIA use of future conservative icon as agent and translator',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.9,
                'entities': ['William F. Buckley Jr.', 'Charles Scribner\'s Sons'],
                'tags': ['buckley', 'cia-agent', '1950s', 'book-translation'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'Peter Matthiessen, the writer and naturalist, began work on novel "Partisans" while with the CIA in Paris from 1951-1953, where he also helped George Plimpton found The Paris Review. Matthiessen used his career as author only as cover for intelligence activities. There is no evidence CIA attempted to control what he wrote or influence The Paris Review.',
                'context': 'CIA operative using literary career as cover',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.85,
                'entities': ['Peter Matthiessen', 'George Plimpton', 'The Paris Review'],
                'tags': ['matthiessen', 'paris-review', 'literary-cover', 'no-editorial-control'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'A Princeton research organization called the Research Council, founded by Hadley Cantril (late chairman of Princeton psychology department) and Lloyd Free, "derived nearly all its income from the CIA in the decade in which it was active." Activities consisted of "extensive public opinion surveys conducted in other countries on questions of interest to the CIA. Some were conducted inside Eastern Europe, the Soviet bloc." The governments "didn\'t know anything about the CIA."',
                'context': 'CIA funding of polling operations in Soviet bloc',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.9,
                'entities': ['Research Council', 'Hadley Cantril', 'Lloyd Free', 'Princeton University'],
                'tags': ['research-council', 'polling', 'soviet-bloc', 'princeton', 'unwitting-governments'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'The CIA occasionally "borrowed" British assets inside Reuters for planting news articles. Asked about William Colby\'s assertion that the agency never "manipulated" Reuters, one official replied "it wasn\'t manipulation because Reuters knew" the stories were planted by CIA and some were bogus.',
                'context': 'CIA cooperation with British intelligence to plant stories in Reuters',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.8,
                'entities': ['Reuters', 'William E. Colby'],
                'tags': ['reuters', 'british-cooperation', 'witting-planting', 'bogus-stories'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'At the time of the American "incursion" into Cambodia in spring 1970, the Hong Kong CIA station "got cable from headquarters instructing us to have all our assets present this in as favorable a light as possible." The newspapers in which slanted stories appeared were read by influential American correspondents.',
                'context': 'CIA Vietnam War propaganda directed at American journalists',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 0.85,
                'entities': [],
                'tags': ['cambodia-1970', 'vietnam-war', 'hong-kong-station', 'american-correspondents'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'In the months before the 1961 Bay of Pigs invasion, the CIA successfully halted publication of several stories, including a major article by David Kraslow (Miami Herald) about training of exile forces in Florida. Kraslow\'s editors asked him to take details to CIA Director Allen Dulles, who cautioned publication would not be "in the national interest." Soon afterward, CIA moved training from Florida to Guatemala.',
                'context': 'CIA domestic censorship before Bay of Pigs',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 0.95,
                'entities': ['Allen Dulles', 'David Kraslow', 'Miami Herald'],
                'tags': ['bay-of-pigs', '1961', 'domestic-censorship', 'national-interest'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'When "The Invisible Government" by David Wise and Thomas B. Ross was published (1964), the CIA\'s first reaction was to try to suppress it. The CIA seriously considered buying up the entire first printing to keep it from public view. Cord Meyer Jr. visited Random House and was told the agency could purchase as many printings as it liked but additional copies would be produced for public sale. A propaganda campaign was then initiated to encourage reviewers to denigrate the book as misinformed and dangerous.',
                'context': 'CIA attempted suppression and smear campaign against book',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 0.9,
                'entities': ['Cord Meyer Jr.', 'Random House', 'David Wise', 'Thomas B. Ross'],
                'tags': ['invisible-government', '1964', 'book-suppression', 'buy-up-scheme', 'smear-campaign'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'In 1966, when New York Times Washington bureau set out to produce series on whether CIA was an "invisible government," cables were sent to overseas bureaus asking correspondents to file on CIA operations. "Consternation within the agency was nearly immediate." The agency\'s fear abated when NYT submitted articles in advance to retired CIA Director John A. McCone. According to Tom Wicker (then NYT Washington bureau chief), "Mr. McCone removed some elements of the series before it appeared."',
                'context': 'CIA pre-publication censorship of New York Times',
                'source': 'nyt_mockingbird_1977_part1',
                'speaker': 'john_crewdson',
                'confidence': 0.95,
                'entities': ['John A. McCone', 'Tom Wicker', 'New York Times'],
                'tags': ['nyt-censorship', '1966', 'mccone', 'pre-publication-review'],
                'claim_type': ClaimType.FACTUAL
            },
            {
                'text': 'One former CIA official said agency passed up opportunity to purchase The Brussels Times, saying it was "easier to buy a reporter, which we\'ve done, than to buy a newspaper."',
                'context': 'CIA preference for journalist recruitment over media ownership',
                'source': 'nyt_mockingbird_1977_part2',
                'speaker': 'john_crewdson',
                'confidence': 0.85,
                'entities': [],
                'tags': ['journalist-recruitment', 'cost-benefit', 'easier-buy-reporter'],
                'claim_type': ClaimType.FACTUAL
            }
        ]

        claim_ids = []
        for i, claim_data in enumerate(key_claims):
            claim_id = f"mockingbird_claim_{i:04d}"

            claim = EvidenceClaim(
                claim_id=claim_id,
                source_id=claim_data['source'],
                speaker_id=claim_data['speaker'],
                claim_type=claim_data['claim_type'],
                text=claim_data['text'],
                confidence=claim_data['confidence'],
                start_time=None,
                end_time=None,
                page_number=None,
                context=claim_data['context'],
                entities=claim_data['entities'],
                tags=['mockingbird', 'cia-propaganda', 'media-manipulation'] + claim_data['tags'],
                created_at=datetime.now().isoformat()
            )

            self.db.add_evidence_claim(claim)
            claim_ids.append(claim_id)

        print(f"  ✅ Extracted {len(claim_ids)} key claims")
        return claim_ids

    def save_checkpoint(self, stats: Dict):
        """Save integration checkpoint"""
        checkpoint_path = self.checkpoint_dir / "mockingbird_integration_checkpoint.json"
        stats['timestamp'] = datetime.now().isoformat()

        with open(checkpoint_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n  ✅ Checkpoint saved: {checkpoint_path}")


def main():
    """Integrate Operation Mockingbird evidence into Sherlock"""
    print("=" * 70)
    print("Operation Mockingbird Evidence Integration")
    print("=" * 70)

    integrator = MockingbirdIntegrator("/home/johnny5/Sherlock/evidence.db")

    # Add speakers
    integrator.add_speakers()

    # Create evidence sources
    integrator.create_evidence_sources()

    # Extract claims
    claim_ids = integrator.extract_key_claims()

    # Save checkpoint
    stats = {
        'speakers_added': 5,
        'sources_created': 2,
        'claims_extracted': len(claim_ids)
    }
    integrator.save_checkpoint(stats)

    print("\n" + "=" * 70)
    print("✅ Operation Mockingbird Evidence Integration Complete")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Speakers: {stats['speakers_added']}")
    print(f"  - Sources: {stats['sources_created']}")
    print(f"  - Claims: {stats['claims_extracted']}")
    print(f"\nPattern Analysis:")
    print(f"  - Wisner's Wurlitzer: 800+ propaganda assets at peak")
    print(f"  - 50+ owned/subsidized media entities worldwide")
    print(f"  - 1,000+ books produced/subsidized since 1950s")
    print(f"  - Systematic 'blowback' to American public acknowledged")
    print(f"  - Direct connections to Guatemala (1954), Chile (1973) coups")
    print(f"  - Cross-references: MK-Ultra, JFK, Sullivan & Cromwell coups")


if __name__ == "__main__":
    main()
