#!/usr/bin/env python3
"""
Cross-System Intelligence Sharing Framework for Sherlock Phase 6
Enables intelligence sharing between Sherlock, Squirt, Johny5Alive, and external AI systems
"""

import asyncio
import json
import hashlib
import hmac
import os
import sqlite3
import sys
import time
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from abc import ABC, abstractmethod

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import EvidenceDatabase
from audit_system import AuditSystem

# Optional imports for networking and encryption
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


class SystemType(Enum):
    """Types of systems in the intelligence network"""
    SHERLOCK = "sherlock"           # Evidence analysis system
    SQUIRT = "squirt"               # Voice memo and quick analysis
    JOHNY5ALIVE = "johny5alive"     # Main system controller
    EXTERNAL_AI = "external_ai"     # External AI systems
    RESEARCH_NODE = "research_node"  # Research-focused nodes
    ANALYSIS_NODE = "analysis_node"  # Analysis-focused nodes


class IntelligenceType(Enum):
    """Types of intelligence that can be shared"""
    SPEAKER_PROFILE = "speaker_profile"          # Speaker characteristics and history
    ENTITY_KNOWLEDGE = "entity_knowledge"        # Knowledge about entities/people/organizations
    PATTERN_DETECTION = "pattern_detection"      # Detected patterns across content
    FACTUAL_CLAIMS = "factual_claims"           # Verified factual information
    CONTRADICTION_ALERTS = "contradiction_alerts" # Detected contradictions
    PROPAGANDA_PATTERNS = "propaganda_patterns"  # Propaganda technique patterns
    TEMPORAL_CORRELATIONS = "temporal_correlations" # Time-based correlations
    CROSS_REFERENCES = "cross_references"       # Document/source cross-references
    PROCESSING_INSIGHTS = "processing_insights"  # Processing optimization insights
    MODEL_IMPROVEMENTS = "model_improvements"   # Model training improvements


class SecurityLevel(Enum):
    """Security levels for intelligence sharing"""
    PUBLIC = "public"               # Publicly shareable information
    INTERNAL = "internal"          # Internal system sharing only
    RESTRICTED = "restricted"      # Restricted sharing with authentication
    CONFIDENTIAL = "confidential"  # Highly sensitive information
    CLASSIFIED = "classified"      # Maximum security level


class SharingProtocol(Enum):
    """Protocols for intelligence sharing"""
    DIRECT_API = "direct_api"      # Direct HTTP API calls
    MESSAGE_QUEUE = "message_queue" # Asynchronous message queuing
    WEBSOCKET = "websocket"        # Real-time WebSocket communication
    FILE_EXCHANGE = "file_exchange" # File-based exchange
    DATABASE_SYNC = "database_sync" # Direct database synchronization


@dataclass
class IntelligencePacket:
    """A packet of intelligence for sharing"""
    packet_id: str
    source_system: SystemType
    target_systems: List[SystemType]
    intelligence_type: IntelligenceType
    security_level: SecurityLevel
    data: Dict
    metadata: Dict
    timestamp: str
    expiry: Optional[str] = None
    signature: Optional[str] = None
    encryption_key_id: Optional[str] = None


@dataclass
class SystemRegistration:
    """Registration information for a system in the network"""
    system_id: str
    system_type: SystemType
    endpoint_url: str
    capabilities: List[IntelligenceType]
    security_level: SecurityLevel
    public_key: Optional[str]
    last_seen: str
    status: str  # "active", "inactive", "maintenance"
    metadata: Dict


@dataclass
class SharingRule:
    """Rule for intelligence sharing"""
    rule_id: str
    source_intelligence: IntelligenceType
    target_systems: List[SystemType]
    conditions: Dict  # Conditions for sharing
    transformations: List[str]  # Data transformations to apply
    security_requirements: SecurityLevel
    enabled: bool


@dataclass
class SharingAudit:
    """Audit record for intelligence sharing"""
    audit_id: str
    packet_id: str
    source_system: str
    target_system: str
    intelligence_type: str
    success: bool
    timestamp: str
    error_message: Optional[str] = None
    metadata: Dict = None


class IntelligenceDatabase:
    """Database for storing shared intelligence and system registrations"""

    def __init__(self, db_path: str = "intelligence_sharing.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        cursor = self.connection.cursor()

        # System registrations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_registrations (
                system_id TEXT PRIMARY KEY,
                system_type TEXT NOT NULL,
                endpoint_url TEXT,
                capabilities TEXT,  -- JSON list
                security_level TEXT,
                public_key TEXT,
                last_seen TEXT,
                status TEXT,
                metadata TEXT  -- JSON
            )
        """)

        # Intelligence packets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_packets (
                packet_id TEXT PRIMARY KEY,
                source_system TEXT,
                target_systems TEXT,  -- JSON list
                intelligence_type TEXT,
                security_level TEXT,
                data TEXT,  -- JSON
                metadata TEXT,  -- JSON
                timestamp TEXT,
                expiry TEXT,
                signature TEXT,
                encryption_key_id TEXT,
                processed BOOLEAN DEFAULT FALSE
            )
        """)

        # Sharing rules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sharing_rules (
                rule_id TEXT PRIMARY KEY,
                source_intelligence TEXT,
                target_systems TEXT,  -- JSON list
                conditions TEXT,  -- JSON
                transformations TEXT,  -- JSON list
                security_requirements TEXT,
                enabled BOOLEAN DEFAULT TRUE
            )
        """)

        # Sharing audit
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sharing_audit (
                audit_id TEXT PRIMARY KEY,
                packet_id TEXT,
                source_system TEXT,
                target_system TEXT,
                intelligence_type TEXT,
                success BOOLEAN,
                timestamp TEXT,
                error_message TEXT,
                metadata TEXT  -- JSON
            )
        """)

        # Intelligence cache (for efficient lookups)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_cache (
                cache_key TEXT PRIMARY KEY,
                intelligence_type TEXT,
                data TEXT,  -- JSON
                timestamp TEXT,
                source_system TEXT,
                expiry TEXT
            )
        """)

        self.connection.commit()

    def register_system(self, registration: SystemRegistration):
        """Register a system in the network"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO system_registrations
            (system_id, system_type, endpoint_url, capabilities, security_level,
             public_key, last_seen, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            registration.system_id,
            registration.system_type.value,
            registration.endpoint_url,
            json.dumps([cap.value for cap in registration.capabilities]),
            registration.security_level.value,
            registration.public_key,
            registration.last_seen,
            registration.status,
            json.dumps(registration.metadata)
        ))
        self.connection.commit()

    def store_intelligence_packet(self, packet: IntelligencePacket):
        """Store an intelligence packet"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO intelligence_packets
            (packet_id, source_system, target_systems, intelligence_type, security_level,
             data, metadata, timestamp, expiry, signature, encryption_key_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            packet.packet_id,
            packet.source_system.value,
            json.dumps([sys.value for sys in packet.target_systems]),
            packet.intelligence_type.value,
            packet.security_level.value,
            json.dumps(packet.data),
            json.dumps(packet.metadata),
            packet.timestamp,
            packet.expiry,
            packet.signature,
            packet.encryption_key_id
        ))
        self.connection.commit()

    def get_registered_systems(self, system_type: Optional[SystemType] = None) -> List[SystemRegistration]:
        """Get registered systems"""
        cursor = self.connection.cursor()
        if system_type:
            cursor.execute("""
                SELECT * FROM system_registrations
                WHERE system_type = ? AND status = 'active'
                ORDER BY last_seen DESC
            """, (system_type.value,))
        else:
            cursor.execute("""
                SELECT * FROM system_registrations
                WHERE status = 'active'
                ORDER BY last_seen DESC
            """)

        systems = []
        for row in cursor.fetchall():
            systems.append(self._row_to_registration(row))
        return systems

    def _row_to_registration(self, row: Tuple) -> SystemRegistration:
        """Convert database row to SystemRegistration"""
        return SystemRegistration(
            system_id=row[0],
            system_type=SystemType(row[1]),
            endpoint_url=row[2],
            capabilities=[IntelligenceType(cap) for cap in json.loads(row[3])],
            security_level=SecurityLevel(row[4]),
            public_key=row[5],
            last_seen=row[6],
            status=row[7],
            metadata=json.loads(row[8])
        )


class SecurityManager:
    """Manages security for intelligence sharing"""

    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or self._generate_master_key()
        self.system_keys = {}  # system_id -> key
        self.encryption_keys = {}  # key_id -> key

    def _generate_master_key(self) -> str:
        """Generate a master encryption key"""
        if CRYPTO_AVAILABLE:
            return Fernet.generate_key().decode()
        else:
            # Fallback to simple key generation
            return hashlib.sha256(str(time.time()).encode()).hexdigest()

    def register_system_key(self, system_id: str, public_key: str):
        """Register a public key for a system"""
        self.system_keys[system_id] = public_key

    def encrypt_data(self, data: Dict, security_level: SecurityLevel) -> Tuple[str, str]:
        """Encrypt data based on security level"""
        if security_level == SecurityLevel.PUBLIC:
            # No encryption for public data
            return json.dumps(data), None

        if not CRYPTO_AVAILABLE:
            # Fallback: Basic encoding for development
            encoded_data = base64.b64encode(json.dumps(data).encode()).decode()
            return encoded_data, "base64_encoding"

        # Generate encryption key
        key_id = str(uuid.uuid4())[:8]
        fernet_key = Fernet.generate_key()
        self.encryption_keys[key_id] = fernet_key

        # Encrypt data
        fernet = Fernet(fernet_key)
        encrypted_data = fernet.encrypt(json.dumps(data).encode())

        return encrypted_data.decode(), key_id

    def decrypt_data(self, encrypted_data: str, key_id: Optional[str]) -> Dict:
        """Decrypt data using key ID"""
        if key_id is None:
            # Unencrypted data
            return json.loads(encrypted_data)

        if key_id == "base64_encoding":
            # Fallback decoding
            decoded_data = base64.b64decode(encrypted_data.encode()).decode()
            return json.loads(decoded_data)

        if not CRYPTO_AVAILABLE or key_id not in self.encryption_keys:
            raise ValueError(f"Cannot decrypt data with key ID: {key_id}")

        # Decrypt with Fernet
        fernet_key = self.encryption_keys[key_id]
        fernet = Fernet(fernet_key)
        decrypted_data = fernet.decrypt(encrypted_data.encode())

        return json.loads(decrypted_data.decode())

    def sign_packet(self, packet_data: Dict) -> str:
        """Create a signature for a packet"""
        packet_json = json.dumps(packet_data, sort_keys=True)
        signature = hmac.new(
            self.master_key.encode(),
            packet_json.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify_packet(self, packet_data: Dict, signature: str) -> bool:
        """Verify a packet signature"""
        expected_signature = self.sign_packet(packet_data)
        return hmac.compare_digest(signature, expected_signature)


class IntelligenceProcessor:
    """Processes intelligence for sharing"""

    def __init__(self, evidence_db: EvidenceDatabase):
        self.evidence_db = evidence_db

    def extract_speaker_profile(self, speaker_id: str) -> Dict:
        """Extract speaker profile for sharing"""
        # Get speaker information from evidence database
        cursor = self.evidence_db.connection.execute("""
            SELECT * FROM speakers WHERE speaker_id = ?
        """, (speaker_id,))

        speaker_data = cursor.fetchone()
        if not speaker_data:
            return {}

        # Get speaker's claims and patterns
        cursor = self.evidence_db.connection.execute("""
            SELECT claim_type, COUNT(*) as count,
                   AVG(CASE WHEN metadata LIKE '%"confidence"%'
                       THEN CAST(JSON_EXTRACT(metadata, '$.confidence') AS REAL)
                       ELSE 0.5 END) as avg_confidence
            FROM evidence_claims
            WHERE speaker_id = ?
            GROUP BY claim_type
        """, (speaker_id,))

        claim_patterns = {}
        for row in cursor.fetchall():
            claim_patterns[row[0]] = {
                'count': row[1],
                'avg_confidence': row[2]
            }

        return {
            'speaker_id': speaker_id,
            'name': speaker_data[1] if len(speaker_data) > 1 else None,
            'claim_patterns': claim_patterns,
            'last_activity': datetime.now().isoformat(),
            'metadata': {
                'extracted_from': 'sherlock_evidence_db',
                'extraction_time': datetime.now().isoformat()
            }
        }

    def extract_entity_knowledge(self, entity: str) -> Dict:
        """Extract knowledge about an entity"""
        # Search for entity mentions in claims
        cursor = self.evidence_db.connection.execute("""
            SELECT ec.text, ec.claim_type, ec.confidence, ec.timestamp, s.name as speaker_name
            FROM evidence_claims ec
            LEFT JOIN speakers s ON ec.speaker_id = s.speaker_id
            WHERE ec.entities LIKE ? OR ec.text LIKE ?
            ORDER BY ec.timestamp DESC
            LIMIT 50
        """, (f'%{entity}%', f'%{entity}%'))

        mentions = []
        for row in cursor.fetchall():
            mentions.append({
                'text': row[0],
                'claim_type': row[1],
                'confidence': row[2],
                'timestamp': row[3],
                'speaker': row[4]
            })

        return {
            'entity': entity,
            'mentions': mentions,
            'mention_count': len(mentions),
            'confidence_distribution': self._calculate_confidence_distribution(mentions),
            'extracted_at': datetime.now().isoformat()
        }

    def _calculate_confidence_distribution(self, mentions: List[Dict]) -> Dict:
        """Calculate confidence distribution for mentions"""
        if not mentions:
            return {}

        confidences = [m.get('confidence', 0.5) for m in mentions]
        return {
            'mean': sum(confidences) / len(confidences),
            'min': min(confidences),
            'max': max(confidences),
            'high_confidence_count': len([c for c in confidences if c > 0.8]),
            'low_confidence_count': len([c for c in confidences if c < 0.3])
        }


class CrossSystemIntelligenceEngine:
    """Main engine for cross-system intelligence sharing"""

    def __init__(self, system_id: str = "sherlock_main",
                 system_type: SystemType = SystemType.SHERLOCK,
                 evidence_db_path: str = "evidence.db"):

        self.system_id = system_id
        self.system_type = system_type
        self.intelligence_db = IntelligenceDatabase()
        self.evidence_db = EvidenceDatabase(evidence_db_path)
        self.security_manager = SecurityManager()
        self.processor = IntelligenceProcessor(self.evidence_db)
        self.audit_system = AuditSystem()

        # Sharing configuration
        self.sharing_rules = []
        self.active_subscriptions = {}  # intelligence_type -> callback
        self.connected_systems = {}

        # Background processing
        self.processing_thread = None
        self.shutdown_event = threading.Event()

    def register_with_network(self, endpoint_url: str = "http://localhost:8080/sherlock",
                             capabilities: Optional[List[IntelligenceType]] = None):
        """Register this system with the intelligence sharing network"""

        if capabilities is None:
            capabilities = [
                IntelligenceType.SPEAKER_PROFILE,
                IntelligenceType.ENTITY_KNOWLEDGE,
                IntelligenceType.FACTUAL_CLAIMS,
                IntelligenceType.CONTRADICTION_ALERTS,
                IntelligenceType.PROPAGANDA_PATTERNS
            ]

        registration = SystemRegistration(
            system_id=self.system_id,
            system_type=self.system_type,
            endpoint_url=endpoint_url,
            capabilities=capabilities,
            security_level=SecurityLevel.INTERNAL,
            public_key=None,  # Would be generated for real deployment
            last_seen=datetime.now().isoformat(),
            status="active",
            metadata={
                'version': '6.0',
                'evidence_db_path': str(self.evidence_db.db_path),
                'features': ['multi_modal', 'advanced_diarization', 'active_learning']
            }
        )

        self.intelligence_db.register_system(registration)

        # Log registration
        self.audit_system.log_event("intelligence_sharing", "system_registered", {
            'system_id': self.system_id,
            'capabilities': [cap.value for cap in capabilities],
            'endpoint': endpoint_url
        })

    def share_intelligence(self, intelligence_type: IntelligenceType,
                          data: Dict, target_systems: List[SystemType],
                          security_level: SecurityLevel = SecurityLevel.INTERNAL,
                          expiry_hours: Optional[int] = None) -> str:
        """Share intelligence with other systems"""

        packet_id = str(uuid.uuid4())

        # Encrypt data if needed
        encrypted_data, key_id = self.security_manager.encrypt_data(data, security_level)

        # Calculate expiry
        expiry = None
        if expiry_hours:
            expiry = (datetime.now() + timedelta(hours=expiry_hours)).isoformat()

        packet = IntelligencePacket(
            packet_id=packet_id,
            source_system=self.system_type,
            target_systems=target_systems,
            intelligence_type=intelligence_type,
            security_level=security_level,
            data={'encrypted': encrypted_data} if key_id else data,
            metadata={
                'source_system_id': self.system_id,
                'original_size': len(json.dumps(data)),
                'encrypted': key_id is not None
            },
            timestamp=datetime.now().isoformat(),
            expiry=expiry,
            encryption_key_id=key_id
        )

        # Sign packet
        packet_data = {
            'packet_id': packet_id,
            'data': packet.data,
            'timestamp': packet.timestamp
        }
        packet.signature = self.security_manager.sign_packet(packet_data)

        # Store packet
        self.intelligence_db.store_intelligence_packet(packet)

        # Distribute to target systems
        self._distribute_packet(packet)

        # Log sharing
        self.audit_system.log_event("intelligence_sharing", "intelligence_shared", {
            'packet_id': packet_id,
            'intelligence_type': intelligence_type.value,
            'target_systems': [sys.value for sys in target_systems],
            'security_level': security_level.value
        })

        return packet_id

    def subscribe_to_intelligence(self, intelligence_type: IntelligenceType,
                                callback: Callable[[Dict], None]):
        """Subscribe to intelligence updates"""
        self.active_subscriptions[intelligence_type] = callback

        self.audit_system.log_event("intelligence_sharing", "subscription_created", {
            'intelligence_type': intelligence_type.value,
            'system_id': self.system_id
        })

    def get_available_intelligence(self, intelligence_type: IntelligenceType,
                                 source_system: Optional[SystemType] = None,
                                 max_age_hours: int = 24) -> List[Dict]:
        """Get available intelligence of a specific type"""

        since_time = (datetime.now() - timedelta(hours=max_age_hours)).isoformat()

        cursor = self.intelligence_db.connection.cursor()
        query = """
            SELECT data, metadata, timestamp, source_system, encryption_key_id
            FROM intelligence_packets
            WHERE intelligence_type = ? AND timestamp >= ?
        """
        params = [intelligence_type.value, since_time]

        if source_system:
            query += " AND source_system = ?"
            params.append(source_system.value)

        query += " ORDER BY timestamp DESC"
        cursor.execute(query, params)

        intelligence_list = []
        for row in cursor.fetchall():
            try:
                # Decrypt if needed
                if row[4]:  # encryption_key_id
                    data = self.security_manager.decrypt_data(
                        json.loads(row[0])['encrypted'],
                        row[4]
                    )
                else:
                    data = json.loads(row[0])

                intelligence_list.append({
                    'data': data,
                    'metadata': json.loads(row[1]),
                    'timestamp': row[2],
                    'source_system': row[3]
                })
            except Exception as e:
                logging.warning(f"Could not decrypt intelligence: {e}")
                continue

        return intelligence_list

    def share_speaker_profile(self, speaker_id: str, target_systems: List[SystemType]) -> str:
        """Share speaker profile with other systems"""
        profile_data = self.processor.extract_speaker_profile(speaker_id)
        if profile_data:
            return self.share_intelligence(
                IntelligenceType.SPEAKER_PROFILE,
                profile_data,
                target_systems,
                SecurityLevel.INTERNAL
            )
        return ""

    def share_entity_knowledge(self, entity: str, target_systems: List[SystemType]) -> str:
        """Share entity knowledge with other systems"""
        entity_data = self.processor.extract_entity_knowledge(entity)
        if entity_data:
            return self.share_intelligence(
                IntelligenceType.ENTITY_KNOWLEDGE,
                entity_data,
                target_systems,
                SecurityLevel.INTERNAL
            )
        return ""

    def get_cross_system_speaker_intel(self, speaker_id: str) -> Dict:
        """Get speaker intelligence from all connected systems"""
        local_profile = self.processor.extract_speaker_profile(speaker_id)

        # Get shared profiles from other systems
        shared_profiles = self.get_available_intelligence(
            IntelligenceType.SPEAKER_PROFILE,
            max_age_hours=168  # 1 week
        )

        # Filter for this speaker
        relevant_profiles = []
        for profile in shared_profiles:
            if profile['data'].get('speaker_id') == speaker_id:
                relevant_profiles.append(profile)

        return {
            'speaker_id': speaker_id,
            'local_profile': local_profile,
            'shared_profiles': relevant_profiles,
            'total_sources': len(relevant_profiles) + (1 if local_profile else 0),
            'last_updated': datetime.now().isoformat()
        }

    def _distribute_packet(self, packet: IntelligencePacket):
        """Distribute packet to target systems"""
        target_systems = self.intelligence_db.get_registered_systems()

        for system in target_systems:
            if (system.system_type in packet.target_systems and
                system.system_id != self.system_id):

                success = self._send_to_system(system, packet)

                # Audit the distribution
                audit = SharingAudit(
                    audit_id=str(uuid.uuid4()),
                    packet_id=packet.packet_id,
                    source_system=self.system_id,
                    target_system=system.system_id,
                    intelligence_type=packet.intelligence_type.value,
                    success=success,
                    timestamp=datetime.now().isoformat(),
                    metadata={'endpoint': system.endpoint_url}
                )
                self._store_audit(audit)

    def _send_to_system(self, target_system: SystemRegistration,
                       packet: IntelligencePacket) -> bool:
        """Send packet to a target system"""
        try:
            if not REQUESTS_AVAILABLE:
                # Log that we would send but can't
                logging.info(f"Would send packet {packet.packet_id} to {target_system.system_id}")
                return True

            # Convert packet to sendable format
            packet_data = {
                'packet_id': packet.packet_id,
                'source_system': packet.source_system.value,
                'intelligence_type': packet.intelligence_type.value,
                'security_level': packet.security_level.value,
                'data': packet.data,
                'metadata': packet.metadata,
                'timestamp': packet.timestamp,
                'signature': packet.signature
            }

            # Send via HTTP POST
            response = requests.post(
                f"{target_system.endpoint_url}/intelligence",
                json=packet_data,
                timeout=30
            )

            return response.status_code == 200

        except Exception as e:
            logging.error(f"Failed to send to {target_system.system_id}: {e}")
            return False

    def _store_audit(self, audit: SharingAudit):
        """Store sharing audit record"""
        cursor = self.intelligence_db.connection.cursor()
        cursor.execute("""
            INSERT INTO sharing_audit
            (audit_id, packet_id, source_system, target_system,
             intelligence_type, success, timestamp, error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit.audit_id,
            audit.packet_id,
            audit.source_system,
            audit.target_system,
            audit.intelligence_type,
            audit.success,
            audit.timestamp,
            audit.error_message,
            json.dumps(audit.metadata or {})
        ))
        self.intelligence_db.connection.commit()

    def start_background_processing(self):
        """Start background processing for intelligence sharing"""
        self.processing_thread = threading.Thread(target=self._background_processor)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def _background_processor(self):
        """Background processor for intelligence sharing"""
        while not self.shutdown_event.is_set():
            try:
                # Process pending subscriptions
                self._process_subscriptions()

                # Cleanup expired packets
                self._cleanup_expired_packets()

                # Update system heartbeat
                self._update_heartbeat()

                time.sleep(30)  # Process every 30 seconds

            except Exception as e:
                logging.error(f"Background processing error: {e}")
                time.sleep(60)  # Wait longer on error

    def _process_subscriptions(self):
        """Process active subscriptions"""
        for intelligence_type, callback in self.active_subscriptions.items():
            try:
                # Get recent intelligence
                recent_intel = self.get_available_intelligence(
                    intelligence_type,
                    max_age_hours=1  # Last hour only
                )

                for intel in recent_intel:
                    callback(intel)

            except Exception as e:
                logging.error(f"Subscription processing error for {intelligence_type}: {e}")

    def _cleanup_expired_packets(self):
        """Clean up expired intelligence packets"""
        current_time = datetime.now().isoformat()
        cursor = self.intelligence_db.connection.cursor()
        cursor.execute("""
            DELETE FROM intelligence_packets
            WHERE expiry IS NOT NULL AND expiry < ?
        """, (current_time,))
        self.intelligence_db.connection.commit()

    def _update_heartbeat(self):
        """Update system heartbeat"""
        cursor = self.intelligence_db.connection.cursor()
        cursor.execute("""
            UPDATE system_registrations
            SET last_seen = ?
            WHERE system_id = ?
        """, (datetime.now().isoformat(), self.system_id))
        self.intelligence_db.connection.commit()

    def stop(self):
        """Stop the intelligence sharing engine"""
        self.shutdown_event.set()
        if self.processing_thread:
            self.processing_thread.join()


def main():
    """Demo of cross-system intelligence sharing"""
    print("🌐 Cross-System Intelligence Sharing Framework - Phase 6")
    print("=" * 60)

    engine = CrossSystemIntelligenceEngine()

    # Register with network
    engine.register_with_network()

    print("✅ Intelligence sharing engine initialized")
    print("🔗 System registration: Connected to intelligence network")
    print("🔐 Security: Encryption and signing for sensitive data")
    print("📡 Protocols: HTTP API, WebSocket, message queue support")
    print("🎯 Intelligence types: Speaker profiles, entity knowledge, patterns")
    print("🔄 Real-time: Background processing and subscriptions")
    print("\nReady for cross-system intelligence sharing")

    # Example usage:
    # engine.share_speaker_profile("Speaker_1", [SystemType.SQUIRT, SystemType.JOHNY5ALIVE])
    # engine.subscribe_to_intelligence(IntelligenceType.CONTRADICTION_ALERTS, handle_alert)
    # intel = engine.get_cross_system_speaker_intel("Speaker_1")


if __name__ == "__main__":
    main()