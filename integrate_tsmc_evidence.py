#!/usr/bin/env python3
"""
TSMC Evidence Integration
Integrates Taiwan Semiconductor Manufacturing Company intelligence into Sherlock

This represents potential MODERN continuation of corporate-state fusion pattern
documented in Sullivan & Cromwell cases (Iran 1953, Guatemala 1954, Chile 1973)

Architecture: Similar to S&C/S-Force/JFK integration
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


class TSMCIntegrator:
    """Integrate TSMC semiconductor intelligence into Sherlock"""

    def __init__(self, db_path: str = "evidence.db"):
        self.db = EvidenceDatabase(db_path)
        self.checkpoint_dir = Path("tsmc_checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

        # Key entities identified in TSMC research
        self.entities = {
            'people': [
                'Morris Chang', 'K. T. Li', 'Sun Yun-suan',
                'Mark Liu', 'C. C. Wei'
            ],
            'organizations': [
                'TSMC', 'ITRI', 'ERSO', 'UMC', 'Philips',
                'ASML', 'Apple', 'NVIDIA', 'AMD', 'Qualcomm',
                'Broadcom', 'MediaTek', 'Intel', 'Samsung',
                'National Development Fund', 'KMT',
                'Synopsys', 'Cadence', 'Applied Materials',
                'Lam Research', 'Tokyo Electron'
            ],
            'locations': [
                'Taiwan', 'Hsinchu Science Park', 'Arizona',
                'Japan', 'Germany', 'Singapore', 'Netherlands'
            ],
            'technologies': [
                'EUV lithography', 'CoWoS', 'InFO', 'SoIC',
                '3nm', '5nm', '7nm', 'Advanced Packaging'
            ]
        }

    def add_speakers(self):
        """Add key TSMC speakers to database"""
        print("\n📋 Adding TSMC speakers...")

        speakers = [
            Speaker(
                speaker_id="morris_chang",
                name="Morris Chang",
                title="TSMC Founder & Former Chairman",
                organization="Taiwan Semiconductor Manufacturing Company",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1987-01-01T00:00:00",
                last_seen=datetime.now().isoformat()
            ),
            Speaker(
                speaker_id="kt_li",
                name="K. T. Li",
                title="Economic Planner & Technocrat",
                organization="Taiwan Government / KMT",
                voice_embedding=None,
                confidence=1.0,
                first_seen="1960-01-01T00:00:00",
                last_seen="2001-05-31T00:00:00"
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
        """Create TSMC evidence sources"""
        print("\n📄 Creating evidence sources...")

        sources = [
            EvidenceSource(
                source_id="tsmc_structural_analysis_2025",
                title="TSMC: How a Pure-Play Foundry Became the World's Keystone Semiconductor Producer",
                url=None,
                file_path=None,
                evidence_type=EvidenceType.DOCUMENT,
                duration=None,
                page_count=None,
                created_at="2025-10-01T00:00:00",
                ingested_at=datetime.now().isoformat(),
                metadata={
                    'case': 'TSMC State-Corporate Fusion',
                    'topic': 'Taiwan semiconductor dominance and geopolitical leverage',
                    'analysis_type': 'Structural brief on state-led industrial strategy',
                    'significance': 'Modern example of corporate-state alignment, potential continuation of S&C pattern',
                    'geopolitical_context': 'Silicon shield, national security infrastructure'
                }
            )
        ]

        for source in sources:
            self.db.add_evidence_source(source)
            print(f"  ✅ {source.source_id}")

    def extract_key_claims(self):
        """Extract key claims from TSMC research"""
        print("\n🔍 Extracting key claims...")

        key_claims = [
            {
                'text': 'TSMC founded 1987 spun out of Taiwan government R&D complex with new model: manufacture only, no in-house chip design. First pure-play foundry in the world.',
                'context': 'TSMC origins and business model innovation',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['TSMC', 'Morris Chang', 'Taiwan', 'ITRI'],
                'tags': ['tsmc', 'pure-play-foundry', '1987', 'business-model', 'state-spinout']
            },
            {
                'text': 'Seed equity from Taiwan National Development Fund and Philips, with government science-park land, tax, and talent policies lowering risk. Government provided nearly half of initial equity.',
                'context': 'State-led capital formation and risk reduction',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'kt_li',
                'confidence': 1.0,
                'entities': ['TSMC', 'National Development Fund', 'Philips', 'Taiwan'],
                'tags': ['state-capital', 'government-equity', 'risk-sharing', 'industrial-policy']
            },
            {
                'text': 'K. T. Li (economic planner) seeded Taiwan high-tech pivot, fostered ITRI/ERSO and Hsinchu Science Park, recruited diaspora talent, introduced venture finance norms. Sun Yun-suan (premier) backed science-park development and export-led upgrading.',
                'context': 'Technocratic architects of Taiwan semiconductor strategy',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'kt_li',
                'confidence': 1.0,
                'entities': ['K. T. Li', 'Sun Yun-suan', 'ITRI', 'ERSO', 'Hsinchu Science Park', 'KMT'],
                'tags': ['technocrats', 'industrial-policy', 'kmt-state', 'diaspora-recruitment']
            },
            {
                'text': 'Morris Chang (ex-TI) rejected IDM model: TSMC would fabricate for everyone and design nothing. That neutrality solved conflict Intel/Samsung faced (selling chips while being foundry), unlocking trust from fabless firms.',
                'context': 'Pure-play business model breaks competitive conflict',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['Morris Chang', 'TSMC', 'Intel', 'Samsung'],
                'tags': ['neutrality', 'trust-economics', 'fabless-ecosystem', 'competitive-advantage']
            },
            {
                'text': 'Customers Apple, NVIDIA, AMD, Qualcomm, Broadcom optimized toolchains for TSMC, raising switching costs. Ecosystem lock-in through PDKs, IP blocks, physical design rules tuned to TSMC.',
                'context': 'Customer lock-in through technical ecosystem alignment',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['TSMC', 'Apple', 'NVIDIA', 'AMD', 'Qualcomm', 'Broadcom'],
                'tags': ['lock-in', 'switching-costs', 'ecosystem', 'pdk', 'customer-dependence']
            },
            {
                'text': 'Export controls, lithography chokepoints, and "silicon shield/porcupine" dynamic bind TSMC to U.S., EU (Netherlands), Japan strategies while deterring CCP aggression against Taiwan.',
                'context': 'Geopolitical leverage through semiconductor dependence',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['TSMC', 'Taiwan', 'ASML', 'Netherlands'],
                'tags': ['silicon-shield', 'geopolitics', 'export-controls', 'deterrence', 'national-security']
            },
            {
                'text': 'EUV lithography (ASML, Netherlands) and advanced EDA/IP (largely U.S.) bind supply chain to Western export regimes. U.S. rules (Entity List, foreign direct product rule) constrain PRC access to leading-edge logic.',
                'context': 'Technological chokepoints enable geopolitical control',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['ASML', 'Netherlands', 'TSMC'],
                'tags': ['euv', 'chokepoints', 'export-controls', 'technology-control', 'western-alliance']
            },
            {
                'text': 'Taiwan advanced fabs described as "silicon shield" (or "porcupine sting") - economic-security interdependence that raises cost of CCP aggression. Allied industrial policy (U.S. CHIPS, Japan/EU subsidies) support TSMC diversification.',
                'context': 'National security framing of semiconductor manufacturing',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['TSMC', 'Taiwan'],
                'tags': ['silicon-shield', 'national-defense', 'deterrence', 'chips-act', 'allied-policy']
            },
            {
                'text': 'Scale flywheel: Volume → yield → margins → CapEx/R&D. Aggressive reinvestment (tens of billions annually) sustains node cadence (7→5→3→2 nm) and advanced packaging capacity.',
                'context': 'Compounding advantage through capital-intensive scale',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['TSMC'],
                'tags': ['scale', 'yield', 'capex', 'reinvestment', 'competitive-moat']
            },
            {
                'text': 'Majority of world 3/5/7 nm logic wafers run at TSMC. Leading AI and mobile parts depend on its capacity and packaging. Advanced packaging (CoWoS, InFO, SoIC) is strategic bottleneck.',
                'context': 'TSMC concentration of cutting-edge manufacturing',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['TSMC'],
                'tags': ['market-dominance', '3nm', '5nm', '7nm', 'advanced-packaging', 'ai-dependency']
            },
            {
                'text': 'Export controls and subsidy regimes now directly shape TSMC capacity location and customer mix. Allies treat TSMC as critical infrastructure and underwrite resilience.',
                'context': 'State policy directly shaping corporate operations',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['TSMC'],
                'tags': ['state-policy', 'critical-infrastructure', 'allied-coordination', 'industrial-policy']
            },
            {
                'text': 'TSMC structural keystone of modern compute because policy, capital, and business model aligned—then compounded via yield, trust, and scale. Power is fragile-resilient: fragile to single-island shocks yet resilient due to global dependence and allied underwriting.',
                'context': 'Structural analysis of TSMC dominance',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'morris_chang',
                'confidence': 1.0,
                'entities': ['TSMC', 'Taiwan'],
                'tags': ['structural-analysis', 'keystone-position', 'fragile-resilient', 'systemic-importance']
            },
            {
                'text': 'KMT state ambitions: Move up value chain, diaspora repatriation, cluster strategy (Hsinchu + universities + ITRI), public risk-sharing (government equity, tax, land, utilities), global integration (listings, JVs, IP alliances).',
                'context': 'Deliberate state industrial strategy for semiconductor leadership',
                'source': 'tsmc_structural_analysis_2025',
                'speaker': 'kt_li',
                'confidence': 1.0,
                'entities': ['Taiwan', 'KMT', 'Hsinchu Science Park', 'ITRI'],
                'tags': ['industrial-strategy', 'state-planning', 'cluster-strategy', 'public-private-partnership']
            }
        ]

        claim_ids = []
        for i, claim_data in enumerate(key_claims):
            claim_id = f"tsmc_claim_{i:04d}"

            claim = EvidenceClaim(
                claim_id=claim_id,
                source_id=claim_data['source'],
                speaker_id=claim_data['speaker'],
                claim_type=ClaimType.FACTUAL,
                text=claim_data['text'],
                confidence=claim_data['confidence'],
                start_time=None,
                end_time=None,
                page_number=None,
                context=claim_data['context'],
                entities=claim_data['entities'],
                tags=['tsmc', 'semiconductors', 'industrial-policy', 'geopolitics'] + claim_data['tags'],
                created_at=datetime.now().isoformat()
            )

            self.db.add_evidence_claim(claim)
            claim_ids.append(claim_id)

        print(f"  ✅ Extracted {len(claim_ids)} key claims")
        return claim_ids

    def save_checkpoint(self, stats: Dict):
        """Save integration checkpoint"""
        checkpoint_path = self.checkpoint_dir / "tsmc_integration_checkpoint.json"
        stats['timestamp'] = datetime.now().isoformat()

        with open(checkpoint_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n  ✅ Checkpoint saved: {checkpoint_path}")


def main():
    """Integrate TSMC evidence into Sherlock"""
    print("=" * 70)
    print("TSMC Semiconductor Intelligence Integration")
    print("=" * 70)

    integrator = TSMCIntegrator("/home/johnny5/Sherlock/evidence.db")

    # Add speakers
    integrator.add_speakers()

    # Create evidence sources
    integrator.create_evidence_sources()

    # Extract claims
    claim_ids = integrator.extract_key_claims()

    # Save checkpoint
    stats = {
        'speakers_added': 2,
        'sources_created': 1,
        'claims_extracted': len(claim_ids)
    }
    integrator.save_checkpoint(stats)

    print("\n" + "=" * 70)
    print("✅ TSMC Evidence Integration Complete")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Speakers: {stats['speakers_added']}")
    print(f"  - Sources: {stats['sources_created']}")
    print(f"  - Claims: {stats['claims_extracted']}")
    print(f"\nPattern Analysis:")
    print(f"  - State-led industrial policy (echoes S&C corporate-state fusion)")
    print(f"  - Government equity & risk-sharing (parallel to CIA corporate protection)")
    print(f"  - Geopolitical leverage ('silicon shield' = modern strategic asset)")
    print(f"  - Allied policy coordination (export controls, subsidies)")


if __name__ == "__main__":
    main()
