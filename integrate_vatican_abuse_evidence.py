#!/usr/bin/env python3
"""
Vatican Sexual Abuse Cover-Up Evidence Integration
Integrates 1962 Vatican document and institutional cover-up intelligence into Sherlock

Key Intelligence:
- 1962 "Crimen sollicitationis" document - 69-page Latin instruction from Pope John XXIII
- Threatened excommunication for those who spoke out about sexual abuse
- May 2001 Vatican letter (Cardinal Ratzinger) confirmed 1962 instruction still in force
- Document confirmed genuine by Roman Catholic Church in England and Wales
- Specific case: Cardinal Murphy-O'Connor covered up priest Michael Hill (convicted, 9 victims)

Architecture: Similar to Operation Mockingbird/MK-Ultra integration
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


class VaticanAbuseIntegrator:
    """Integrate Vatican sexual abuse cover-up evidence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("vatican_abuse_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in Vatican abuse investigation
        self.entities = {
            'people': [
                'Pope John XXIII', 'Cardinal Ratzinger (Pope Benedict XVI)',
                'Cardinal Cormac Murphy-O\'Connor', 'Michael Hill',
                'Daniel Shea', 'Richard Scorer', 'Rev Thomas Doyle',
                'Antony Barnett', 'Jason Rodrigues'
            ],
            'organizations': [
                'Vatican/Holy See', 'Roman Catholic Church',
                'Congregation for Doctrine of Faith', 'Diocese of Arundel and Brighton',
                'The Observer', 'The Guardian'
            ],
            'locations': [
                'Vatican City', 'England', 'Wales', 'United Kingdom',
                'United States', 'Texas', 'Germany', 'Arundel', 'Brighton'
            ],
            'documents': [
                'Crimen sollicitationis (1962)', 'May 2001 Vatican letter (Ratzinger)',
                '1983 Catholic Church England/Wales abuse code'
            ],
            'concepts': [
                'excommunication', 'secrecy', 'cover-up', 'victim silencing',
                'oath of secrecy', 'perpetual silence', 'Holy Office',
                'internal discipline', 'systematic abuse'
            ]
        }

    def add_speakers(self):
        """Add key Vatican abuse investigation speakers to database"""
        print("\n📋 Adding Vatican abuse investigation speakers...")

        speakers = [
            Speaker(
                speaker_id="pope_john_xxiii",
                name="Pope John XXIII",
                title="Pope (1958-1963)",
                organization="Vatican/Holy See",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1958-10-28T00:00:00",
                last_seen="1963-06-03T00:00:00"  # Died 1963
            ),
            Speaker(
                speaker_id="cardinal_ratzinger",
                name="Cardinal Joseph Ratzinger (later Pope Benedict XVI)",
                title="Prefect of Congregation for Doctrine of Faith",
                organization="Vatican/Holy See",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1981-11-25T00:00:00",
                last_seen="2022-12-31T00:00:00"  # Died 2022
            ),
            Speaker(
                speaker_id="cardinal_murphy_oconnor",
                name="Cardinal Cormac Murphy-O'Connor",
                title="Archbishop of Westminster, Head of Roman Catholic Church in England and Wales",
                organization="Roman Catholic Church",
                voice_embedding=None,
                confidence=1.0,
                first_seen="2000-02-22T00:00:00",
                last_seen="2017-09-01T00:00:00"  # Died 2017
            ),
            Speaker(
                speaker_id="michael_hill_priest",
                name="Michael Hill",
                title="Catholic Priest (convicted child abuser)",
                organization="Diocese of Arundel and Brighton",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1970-01-01T00:00:00",
                last_seen="2003-08-17T00:00:00"
            ),
            Speaker(
                speaker_id="daniel_shea_lawyer",
                name="Daniel Shea",
                title="Texan Lawyer (represents abuse victims)",
                organization="Independent",
                voice_embedding=None,
                confidence=1.0,
                first_seen="2003-08-17T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="richard_scorer_lawyer",
                name="Richard Scorer",
                title="British Lawyer (represents UK abuse victims)",
                organization="Independent",
                voice_embedding=None,
                confidence=1.0,
                first_seen="2003-08-17T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="rev_thomas_doyle",
                name="Rev Thomas Doyle",
                title="US Air Force Chaplain, Church Law Specialist",
                organization="US Air Force",
                voice_embedding=None,
                confidence=1.0,
                first_seen="2003-08-17T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="antony_barnett",
                name="Antony Barnett",
                title="Public Affairs Editor",
                organization="The Observer",
                voice_embedding=None,
                confidence=1.0,
                first_seen="2003-08-17T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="vatican_spokesman_2003",
                name="Catholic Church Spokesman (unnamed)",
                title="Official Spokesperson",
                organization="Roman Catholic Church in England and Wales",
                voice_embedding=None,
                confidence=0.8,
                first_seen="2003-08-17T00:00:00",
                last_seen="2003-08-17T00:00:00"
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
        """Create Vatican abuse investigation evidence sources"""
        print("\n📄 Creating evidence sources...")

        sources = [
            EvidenceSource(
                source_id="guardian_vatican_abuse_2003",
                title="Vatican told bishops to cover up sex abuse",
                url="https://www.theguardian.com/world/2003/aug/17/religion.childprotection",
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="2003-08-17T00:27:26.000Z",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    "author": "Antony Barnett",
                    "publication": "The Guardian/The Observer",
                    "publication_date": "2003-08-17",
                    "article_type": "investigative_journalism",
                    "key_document": "Crimen sollicitationis (1962)",
                    "document_confirmed_genuine": True,
                    "confirmed_by": "Roman Catholic Church in England and Wales"
                }
            )
        ]

        for source in sources:
            try:
                self.db.add_evidence_source(source)
                print(f"  ✅ {source.title}")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"  ⚠️  {source.title} (already exists)")
                else:
                    raise

        return sources

    def create_claims(self):
        """Create Vatican abuse investigation claims"""
        print("\n💬 Creating claims...")

        claims = [
            # Document authenticity and scope
            EvidenceClaim(
                claim_id="vatican_abuse_001",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="antony_barnett",
                claim_type=ClaimType.FACTUAL,
                text="The Observer obtained a 40-year-old confidential document from the secret Vatican archive - a 69-page Latin document bearing the seal of Pope John XXIII sent to every bishop in the world",
                confidence=0.60,  # journalism + document confirmation
                start_time=None,
                end_time=None,
                page_number=None,
                context="Document confirmed as genuine by Roman Catholic Church in England and Wales",
                entities=["Pope John XXIII", "Vatican", "bishops"],
                tags=["document_leaked", "vatican", "crimen_sollicitationis", "confirmation"],
                created_at=datetime.now().isoformat()
            ),
            # Secrecy and excommunication policy
            EvidenceClaim(
                claim_id="vatican_abuse_002",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="antony_barnett",
                claim_type=ClaimType.FACTUAL,
                text="Instructions outline policy of 'strictest' secrecy in dealing with sexual abuse allegations and threatens those who speak out with excommunication",
                confidence=0.65,  # document_leaked + official confirmation
                start_time=None,
                end_time=None,
                page_number=None,
                context="Direct quotes from Vatican document 'Crimen sollicitationis', confirmed genuine",
                entities=["Vatican", "excommunication"],
                tags=["excommunication", "secrecy", "intimidation", "policy"],
                created_at=datetime.now().isoformat()
            ),
            # Victim silencing
            EvidenceClaim(
                claim_id="vatican_abuse_003",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="antony_barnett",
                claim_type=ClaimType.FACTUAL,
                text="Document calls for victim to take oath of secrecy when making complaint to Church officials",
                confidence=0.65,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Direct quotes from Vatican document",
                entities=["victims", "oath", "Church officials"],
                tags=["victim_silencing", "oath", "secrecy"],
                created_at=datetime.now().isoformat()
            ),
            # Classification instructions
            EvidenceClaim(
                claim_id="vatican_abuse_004",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="antony_barnett",
                claim_type=ClaimType.FACTUAL,
                text="Document instructs: 'to be diligently stored in the secret archives of the Curia as strictly confidential. Nor is it to be published nor added to with any commentaries'",
                confidence=0.65,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Direct quote from Crimen sollicitationis",
                entities=["Curia", "Vatican", "secret archives"],
                tags=["classification", "secrecy", "confidential"],
                created_at=datetime.now().isoformat()
            ),
            # Legal analysis - international conspiracy
            EvidenceClaim(
                claim_id="vatican_abuse_005",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="daniel_shea_lawyer",
                claim_type=ClaimType.OPINION,
                text="These instructions went out to every bishop around the globe and would certainly have applied in Britain. It proves there was an international conspiracy by the Church to hush up sexual abuse issues. It is a devious attempt to conceal criminal conduct and is a blueprint for deception and concealment",
                confidence=0.55,  # expert analysis based on document
                start_time=None,
                end_time=None,
                page_number=None,
                context="Legal analysis of Vatican document scope and implications",
                entities=["bishops", "Britain", "Church"],
                tags=["conspiracy", "international", "cover-up", "criminal_conduct", "blueprint"],
                created_at=datetime.now().isoformat()
            ),
            # Legal analysis - systematic cover-up
            EvidenceClaim(
                claim_id="vatican_abuse_006",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="richard_scorer_lawyer",
                claim_type=ClaimType.OPINION,
                text="This document appears to prove Catholic Church systematically covered up abuse and tried to silence victims. Threatening excommunication to anybody who speaks out shows the lengths the most senior figures in the Vatican were prepared to go to prevent information getting out to the public domain",
                confidence=0.55,
                start_time=None,
                end_time=None,
                page_number=None,
                context="British lawyer representing UK abuse victims, called document 'explosive'",
                entities=["Catholic Church", "victims", "Vatican", "excommunication"],
                tags=["systematic", "victim_silencing", "cover-up", "explosive"],
                created_at=datetime.now().isoformat()
            ),
            # Timeline contradiction
            EvidenceClaim(
                claim_id="vatican_abuse_007",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="richard_scorer_lawyer",
                claim_type=ClaimType.FACTUAL,
                text="Document dates back to 1962, contradicting Catholic Church claim that sexual abuse was a modern phenomenon",
                confidence=0.60,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Document date verified, Church had claimed abuse awareness was recent",
                entities=["Catholic Church", "1962"],
                tags=["timeline", "church_defense", "contradiction"],
                created_at=datetime.now().isoformat()
            ),
            # Murphy-O'Connor specific case
            EvidenceClaim(
                claim_id="vatican_abuse_008",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="antony_barnett",
                claim_type=ClaimType.FACTUAL,
                text="Cardinal Murphy-O'Connor accused of covering up allegations against priest Michael Hill when Bishop of Arundel and Brighton. Instead of reporting to police, moved Hill to another position where he was later convicted for abusing 9 children",
                confidence=0.65,  # journalism + criminal conviction
                start_time=None,
                end_time=None,
                page_number=None,
                context="Michael Hill convicted, Murphy-O'Connor publicly apologized for his 'mistake'",
                entities=["Cardinal Murphy-O'Connor", "Michael Hill", "Arundel", "Brighton", "police"],
                tags=["murphy-oconnor", "michael_hill", "conviction", "transfer", "cover-up"],
                created_at=datetime.now().isoformat()
            ),
            # Church defense statement
            EvidenceClaim(
                claim_id="vatican_abuse_009",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="vatican_spokesman_2003",
                claim_type=ClaimType.OPINION,
                text="Document is about Church's internal disciplinary procedures for priest accused of using confession to solicit sex. Does not forbid victims to report civil crimes. Confidentiality aimed to protect accused as in court procedures. Secret Vatican orders were not part of organized cover-up, lawyers are taking document 'out of context' and 'distorting it'",
                confidence=0.50,  # official defense statement
                start_time=None,
                end_time=None,
                page_number=None,
                context="Church spokesman official response to The Observer investigation",
                entities=["Church", "victims", "accused"],
                tags=["church_response", "defense", "denial"],
                created_at=datetime.now().isoformat()
            ),
            # 1983 policy claim
            EvidenceClaim(
                claim_id="vatican_abuse_010",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="vatican_spokesman_2003",
                claim_type=ClaimType.FACTUAL,
                text="In 1983 Catholic Church in England and Wales introduced own code dealing with sexual abuse, which would have superseded 1962 instructions",
                confidence=0.50,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Church spokesman claim about policy update",
                entities=["Catholic Church", "England", "Wales", "1983"],
                tags=["policy_change", "1983", "superseded"],
                created_at=datetime.now().isoformat()
            ),
            # Ratzinger 2001 letter - CRITICAL
            EvidenceClaim(
                claim_id="vatican_abuse_011",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="antony_barnett",
                claim_type=ClaimType.FACTUAL,
                text="Vatican sent letter to bishops in May 2001 clearly stating 1962 instruction was in force until then. Letter signed by Cardinal Ratzinger, head of Congregation for Doctrine of Faith",
                confidence=0.65,  # document evidence
                start_time=None,
                end_time=None,
                page_number=None,
                context="May 2001 Vatican letter contradicts claim that 1983 code superseded 1962 policy",
                entities=["Vatican", "bishops", "Cardinal Ratzinger", "Congregation for Doctrine of Faith"],
                tags=["ratzinger", "2001", "policy_continuation", "contradiction"],
                created_at=datetime.now().isoformat()
            ),
            # Expert analysis - secrecy obsession
            EvidenceClaim(
                claim_id="vatican_abuse_012",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="rev_thomas_doyle",
                claim_type=ClaimType.OPINION,
                text="Document is indication of pathological obsession with secrecy in Catholic Church, but not itself a smoking gun. If document has been foundation of continuous policy to cover clergy crimes, then we have quite another issue. Requires concrete proof of whether document used as justification for victim intimidation",
                confidence=0.55,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Expert analysis from Church law specialist and US Air Force chaplain",
                entities=["Catholic Church", "secrecy", "clergy crimes"],
                tags=["secrecy", "expert_opinion", "pathological", "smoking_gun"],
                created_at=datetime.now().isoformat()
            ),
            # Pattern of intimidation
            EvidenceClaim(
                claim_id="vatican_abuse_013",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="rev_thomas_doyle",
                claim_type=ClaimType.FACTUAL,
                text="Too many authenticated reports of victims having been seriously intimidated into silence by Church authorities to assert intimidation is exception and not the norm",
                confidence=0.60,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Church law specialist observation on pattern of victim intimidation",
                entities=["victims", "Church authorities", "intimidation"],
                tags=["intimidation", "pattern", "systematic", "victim_silencing"],
                created_at=datetime.now().isoformat()
            ),
            # Document scope - bestiality
            EvidenceClaim(
                claim_id="vatican_abuse_014",
                source_id="guardian_vatican_abuse_2003",
                speaker_id="antony_barnett",
                claim_type=ClaimType.FACTUAL,
                text="Document focuses on sexual abuse initiated as part of confessional relationship, but instructions also cover 'worst crime' described as obscene act perpetrated by cleric with 'youths of either sex or with brute animals (bestiality)'",
                confidence=0.65,
                start_time=None,
                end_time=None,
                page_number=None,
                context="Direct quote from Crimen sollicitationis document scope",
                entities=["confession", "cleric", "youths"],
                tags=["document_scope", "bestiality", "confession", "abuse_types"],
                created_at=datetime.now().isoformat()
            )
        ]

        for claim in claims:
            try:
                self.db.add_evidence_claim(claim)
                print(f"  ✅ {claim.claim_id}: {claim.text[:60]}...")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"  ⚠️  {claim.claim_id} (already exists)")
                else:
                    raise

        return claims

    def generate_intelligence_report(self):
        """Generate intelligence report on Vatican abuse cover-up"""
        print("\n📊 Generating intelligence report...")

        report = {
            "operation": "Vatican Sexual Abuse Cover-Up",
            "operation_type": "institutional_conspiracy",
            "timeframe": "1962-2003+ (document period to publication, ongoing)",
            "key_dates": [
                {"date": "1962", "event": "Crimen sollicitationis issued by Pope John XXIII"},
                {"date": "1983", "event": "England/Wales Catholic Church new abuse code (claimed to supersede 1962)"},
                {"date": "2001-05", "event": "Cardinal Ratzinger letter confirms 1962 instruction still in force"},
                {"date": "2003-08-17", "event": "The Observer publishes investigation revealing document"}
            ],
            "key_document": {
                "name": "Crimen sollicitationis",
                "date": "1962",
                "type": "Vatican instruction",
                "pages": 69,
                "language": "Latin",
                "sealed_by": "Pope John XXIII",
                "confirmed_genuine": True,
                "confirmed_by": "Roman Catholic Church in England and Wales"
            },
            "key_findings": [
                "1962 Vatican document instructed global bishops to maintain 'strictest secrecy' on sexual abuse",
                "Document threatened excommunication for those who spoke out about abuse",
                "Victims required to take oath of secrecy when making complaints",
                "May 2001 Vatican letter (Cardinal Ratzinger) confirmed 1962 instruction still in force 39 years later",
                "Document confirmed genuine by Roman Catholic Church in England and Wales",
                "Evidence contradicts Church claim that abuse awareness is 'modern phenomenon'",
                "Specific case: Cardinal Murphy-O'Connor covered up priest Michael Hill (9 victims, convicted)"
            ],
            "evidence_quality": "Medium-High: Reputable journalism (The Guardian/Observer), document confirmed genuine by Church, multiple expert legal/Church law sources, specific criminal conviction",
            "intelligence_value": "High: Reveals systematic institutional policy of concealment spanning 40+ years, implicates senior Vatican officials including future Pope Benedict XVI, provides documentary proof of cover-up instructions",
            "targets_identified": [
                {
                    "name": "Cardinal Joseph Ratzinger (Pope Benedict XVI)",
                    "priority": 4,
                    "rationale": "Signed May 2001 letter continuing 1962 secrecy policy, head of Congregation for Doctrine of Faith",
                    "target_type": "person"
                },
                {
                    "name": "Cardinal Cormac Murphy-O'Connor",
                    "priority": 3,
                    "rationale": "Specific cover-up allegations in Michael Hill case (9 victims), transferred priest instead of reporting to police",
                    "target_type": "person"
                },
                {
                    "name": "Michael Hill",
                    "priority": 2,
                    "rationale": "Convicted priest, 9 child victims, protected by Church hierarchy",
                    "target_type": "person"
                },
                {
                    "name": "Congregation for Doctrine of Faith",
                    "priority": 4,
                    "rationale": "Vatican office managing abuse policy, historical connection to Inquisition",
                    "target_type": "organization"
                }
            ],
            "cross_references": [
                {
                    "operation": "Operation Mockingbird",
                    "connection": "Institutional information control, silencing witnesses, systematic secrecy protocols"
                },
                {
                    "operation": "MK-Ultra",
                    "connection": "Institutional abuse, victim intimidation, secrecy protocols, protection of perpetrators"
                }
            ],
            "analyst_assessment": {
                "pattern": "Institutional cover-up with global coordination, multi-decade continuity, victim intimidation",
                "mechanism": "Excommunication threats, secrecy oaths, document classification, internal 'discipline' vs criminal prosecution",
                "scope": "Global (sent to every bishop worldwide), 40+ year documented timeframe (1962-2003+)",
                "resistance": "Lawyers (Daniel Shea, Richard Scorer), investigative journalism (The Observer), Church law specialists (Rev Doyle)",
                "current_status": "Public exposure 2003, ongoing investigations, pattern confirmed by multiple experts"
            },
            "generated_at": datetime.now().isoformat(),
            "analyst": "Sherlock Evidence Analysis System"
        }

        # Save report
        report_path = self.checkpoint_dir / f"vatican_abuse_intel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"  ✅ Intelligence report saved to {report_path}")
        return report

    def run(self):
        """Execute complete Vatican abuse evidence integration"""
        print("="*80)
        print("VATICAN SEXUAL ABUSE COVER-UP EVIDENCE INTEGRATION")
        print("="*80)

        try:
            # Add speakers
            self.add_speakers()

            # Create evidence sources
            sources = self.create_evidence_sources()

            # Create claims
            claims = self.create_claims()

            # Generate intelligence report
            report = self.generate_intelligence_report()

            print("\n" + "="*80)
            print("✅ VATICAN ABUSE EVIDENCE INTEGRATION COMPLETE")
            print("="*80)
            print(f"📊 Sources integrated: {len(sources)}")
            print(f"💬 Claims extracted: {len(claims)}")
            print(f"🎯 Targets identified: {len(report['targets_identified'])}")
            print(f"🔗 Cross-references: {len(report['cross_references'])}")

            # Print key intelligence summary
            print("\n🔍 KEY INTELLIGENCE SUMMARY:")
            for finding in report['key_findings']:
                print(f"  • {finding}")

            print("\n🎯 HIGH-PRIORITY TARGETS:")
            for target in sorted(report['targets_identified'], key=lambda x: x['priority'], reverse=True):
                print(f"  • [{target['priority']}] {target['name']}: {target['rationale']}")

            return True

        except Exception as e:
            print(f"\n❌ Error during integration: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    integrator = VaticanAbuseIntegrator()
    success = integrator.run()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
