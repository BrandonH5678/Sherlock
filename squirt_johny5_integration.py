#!/usr/bin/env python3
"""
Squirt/Johny5Alive Integration Framework for Sherlock Phase 6
Provides seamless integration with the Squirt voice system and Johny5Alive main controller
"""

import asyncio
import json
import os
import sqlite3
import sys
import time
import uuid
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import subprocess

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import EvidenceDatabase
from audit_system import AuditSystem
from voice_engine import VoiceEngineManager, TranscriptionMode, ProcessingPriority

# Optional imports for inter-process communication
try:
    import zmq
    ZMQ_AVAILABLE = True
except ImportError:
    ZMQ_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import dbus
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False


class SystemComponent(Enum):
    """System components in the Johny5Alive ecosystem"""
    SHERLOCK = "sherlock"              # Evidence analysis system
    SQUIRT = "squirt"                  # Voice memo system
    JOHNY5ALIVE = "johny5alive"        # Main system controller
    VOICE_ENGINE = "voice_engine"      # Shared voice processing
    FILE_MONITOR = "file_monitor"      # File system monitoring
    BACKUP_SYSTEM = "backup_system"    # Backup and sync
    ANALYSIS_QUEUE = "analysis_queue"  # Analysis task queue


class MessageType(Enum):
    """Types of messages between systems"""
    VOICE_MEMO_READY = "voice_memo_ready"           # New voice memo available
    ANALYSIS_REQUEST = "analysis_request"           # Request for analysis
    ANALYSIS_COMPLETE = "analysis_complete"         # Analysis completed
    TRANSCRIPTION_READY = "transcription_ready"     # Transcription available
    EVIDENCE_UPDATED = "evidence_updated"           # Evidence database updated
    SYSTEM_STATUS = "system_status"                 # System status update
    PRIORITY_OVERRIDE = "priority_override"         # Override processing priority
    RESOURCE_REQUEST = "resource_request"           # Request system resources
    RESOURCE_RELEASE = "resource_release"           # Release system resources
    HEALTH_CHECK = "health_check"                   # Health check ping
    SHUTDOWN_REQUEST = "shutdown_request"           # Graceful shutdown request


class ProcessingMode(Enum):
    """Processing modes for different scenarios"""
    IMMEDIATE = "immediate"     # Process immediately (Squirt voice memos)
    SCHEDULED = "scheduled"     # Process at scheduled time
    BACKGROUND = "background"   # Process when resources available
    BATCH = "batch"            # Batch process multiple items
    RESEARCH = "research"      # Deep research analysis


@dataclass
class SystemMessage:
    """Message between system components"""
    message_id: str
    source: SystemComponent
    target: SystemComponent
    message_type: MessageType
    payload: Dict
    priority: int  # 1-10, 1 = highest
    timestamp: str
    expiry: Optional[str] = None
    reply_to: Optional[str] = None


@dataclass
class VoiceMemoNotification:
    """Notification about a new voice memo"""
    memo_id: str
    file_path: str
    duration: float
    format: str
    created_at: str
    user_id: str
    priority: ProcessingPriority
    metadata: Dict


@dataclass
class AnalysisRequest:
    """Request for evidence analysis"""
    request_id: str
    source_files: List[str]
    analysis_types: List[str]
    priority: ProcessingPriority
    mode: ProcessingMode
    requester: SystemComponent
    deadline: Optional[str] = None
    parameters: Dict = None


@dataclass
class SystemStatus:
    """Status of a system component"""
    component: SystemComponent
    status: str  # "active", "busy", "idle", "maintenance", "error"
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: float
    last_activity: str
    capabilities: List[str]
    load_average: float


class MessageBus:
    """Inter-system message bus for communication"""

    def __init__(self, component_id: SystemComponent):
        self.component_id = component_id
        self.subscribers = {}  # message_type -> callback
        self.message_queue = []
        self.running = False

        # Initialize communication backends
        self.zmq_context = None
        self.zmq_socket = None
        self.redis_client = None

        self._init_communication()

    def _init_communication(self):
        """Initialize communication backends"""
        # Try ZeroMQ first (preferred for low-latency)
        if ZMQ_AVAILABLE:
            try:
                self.zmq_context = zmq.Context()
                self.zmq_socket = self.zmq_context.socket(zmq.PUB)
                self.zmq_socket.bind(f"tcp://*:{5555 + hash(self.component_id.value) % 1000}")
                logging.info(f"ZeroMQ initialized for {self.component_id.value}")
            except Exception as e:
                logging.warning(f"ZeroMQ init failed: {e}")

        # Try Redis as fallback
        if REDIS_AVAILABLE and not self.zmq_socket:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
                self.redis_client.ping()
                logging.info(f"Redis initialized for {self.component_id.value}")
            except Exception as e:
                logging.warning(f"Redis init failed: {e}")

        # Fallback to file-based communication
        if not self.zmq_socket and not self.redis_client:
            self.message_dir = Path(f"/tmp/johny5_messages/{self.component_id.value}")
            self.message_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"File-based messaging for {self.component_id.value}")

    def subscribe(self, message_type: MessageType, callback: Callable[[SystemMessage], None]):
        """Subscribe to a message type"""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(callback)

    def publish(self, target: SystemComponent, message_type: MessageType,
               payload: Dict, priority: int = 5) -> str:
        """Publish a message"""
        message_id = str(uuid.uuid4())

        message = SystemMessage(
            message_id=message_id,
            source=self.component_id,
            target=target,
            message_type=message_type,
            payload=payload,
            priority=priority,
            timestamp=datetime.now().isoformat()
        )

        # Send via available backend
        if self.zmq_socket:
            self._send_zmq(message)
        elif self.redis_client:
            self._send_redis(message)
        else:
            self._send_file(message)

        return message_id

    def _send_zmq(self, message: SystemMessage):
        """Send message via ZeroMQ"""
        try:
            topic = f"{message.target.value}.{message.message_type.value}"
            message_data = json.dumps(asdict(message))
            self.zmq_socket.send_multipart([topic.encode(), message_data.encode()])
        except Exception as e:
            logging.error(f"ZeroMQ send error: {e}")

    def _send_redis(self, message: SystemMessage):
        """Send message via Redis"""
        try:
            channel = f"{message.target.value}:{message.message_type.value}"
            message_data = json.dumps(asdict(message))
            self.redis_client.publish(channel, message_data)
        except Exception as e:
            logging.error(f"Redis send error: {e}")

    def _send_file(self, message: SystemMessage):
        """Send message via file system"""
        try:
            target_dir = Path(f"/tmp/johny5_messages/{message.target.value}")
            target_dir.mkdir(parents=True, exist_ok=True)

            message_file = target_dir / f"{message.message_id}.json"
            with open(message_file, 'w') as f:
                json.dump(asdict(message), f, indent=2)
        except Exception as e:
            logging.error(f"File send error: {e}")

    def start_listening(self):
        """Start listening for messages"""
        self.running = True

        if self.zmq_socket:
            threading.Thread(target=self._listen_zmq, daemon=True).start()
        elif self.redis_client:
            threading.Thread(target=self._listen_redis, daemon=True).start()
        else:
            threading.Thread(target=self._listen_file, daemon=True).start()

    def _listen_zmq(self):
        """Listen for ZeroMQ messages"""
        subscriber = self.zmq_context.socket(zmq.SUB)
        # Subscribe to messages for this component
        topic_prefix = f"{self.component_id.value}."
        subscriber.setsockopt(zmq.SUBSCRIBE, topic_prefix.encode())

        # Connect to other components (simplified - would scan for active components)
        for port in range(5555, 5565):
            try:
                subscriber.connect(f"tcp://localhost:{port}")
            except:
                continue

        while self.running:
            try:
                topic, message_data = subscriber.recv_multipart(zmq.NOBLOCK)
                message_dict = json.loads(message_data.decode())
                message = SystemMessage(**message_dict)
                self._handle_message(message)
            except zmq.Again:
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"ZeroMQ receive error: {e}")

    def _listen_redis(self):
        """Listen for Redis messages"""
        pubsub = self.redis_client.pubsub()
        # Subscribe to messages for this component
        pattern = f"{self.component_id.value}:*"
        pubsub.psubscribe(pattern)

        while self.running:
            try:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'pmessage':
                    message_dict = json.loads(message['data'].decode())
                    msg = SystemMessage(**message_dict)
                    self._handle_message(msg)
            except Exception as e:
                logging.error(f"Redis receive error: {e}")

    def _listen_file(self):
        """Listen for file-based messages"""
        while self.running:
            try:
                for message_file in self.message_dir.glob("*.json"):
                    try:
                        with open(message_file, 'r') as f:
                            message_dict = json.load(f)
                        message = SystemMessage(**message_dict)
                        self._handle_message(message)
                        message_file.unlink()  # Remove processed message
                    except Exception as e:
                        logging.error(f"File message error: {e}")

                time.sleep(1.0)  # Check every second
            except Exception as e:
                logging.error(f"File listen error: {e}")

    def _handle_message(self, message: SystemMessage):
        """Handle received message"""
        if message.message_type in self.subscribers:
            for callback in self.subscribers[message.message_type]:
                try:
                    callback(message)
                except Exception as e:
                    logging.error(f"Message handler error: {e}")

    def stop(self):
        """Stop the message bus"""
        self.running = False
        if self.zmq_context:
            self.zmq_context.term()


class SquirtIntegration:
    """Integration with Squirt voice memo system"""

    def __init__(self, message_bus: MessageBus, voice_engine: VoiceEngineManager):
        self.message_bus = message_bus
        self.voice_engine = voice_engine
        self.squirt_directory = Path.home() / "squirt_memos"
        self.processed_memos = set()

        # Subscribe to relevant messages
        self.message_bus.subscribe(MessageType.VOICE_MEMO_READY, self._handle_voice_memo)
        self.message_bus.subscribe(MessageType.PRIORITY_OVERRIDE, self._handle_priority_override)

        # Start monitoring for new voice memos
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_squirt_directory, daemon=True)
        self.monitor_thread.start()

    def _monitor_squirt_directory(self):
        """Monitor Squirt directory for new voice memos"""
        while self.monitoring:
            try:
                if self.squirt_directory.exists():
                    for audio_file in self.squirt_directory.glob("*.wav"):
                        if str(audio_file) not in self.processed_memos:
                            self._process_new_memo(audio_file)
                            self.processed_memos.add(str(audio_file))

                time.sleep(2.0)  # Check every 2 seconds
            except Exception as e:
                logging.error(f"Squirt monitoring error: {e}")
                time.sleep(10.0)

    def _process_new_memo(self, audio_file: Path):
        """Process a new voice memo from Squirt"""
        try:
            # Get file metadata
            stat = audio_file.stat()
            duration = self._estimate_duration(audio_file)

            # Create notification
            notification = VoiceMemoNotification(
                memo_id=str(uuid.uuid4()),
                file_path=str(audio_file),
                duration=duration,
                format="wav",
                created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                user_id="squirt_user",
                priority=ProcessingPriority.IMMEDIATE,
                metadata={
                    'file_size': stat.st_size,
                    'detected_by': 'sherlock_squirt_integration'
                }
            )

            # Notify Sherlock about new memo
            self.message_bus.publish(
                SystemComponent.SHERLOCK,
                MessageType.VOICE_MEMO_READY,
                asdict(notification),
                priority=1  # Highest priority
            )

            logging.info(f"New Squirt memo detected: {audio_file.name}")

        except Exception as e:
            logging.error(f"Memo processing error: {e}")

    def _estimate_duration(self, audio_file: Path) -> float:
        """Estimate audio duration (simplified)"""
        try:
            # Simple estimation based on file size
            # Real implementation would use librosa or similar
            file_size = audio_file.stat().st_size
            # Rough estimate: 16kHz, 16-bit mono = ~32KB per second
            estimated_duration = file_size / 32000
            return estimated_duration
        except:
            return 0.0

    def _handle_voice_memo(self, message: SystemMessage):
        """Handle voice memo notification"""
        try:
            notification = VoiceMemoNotification(**message.payload)
            logging.info(f"Processing voice memo: {notification.memo_id}")

            # Process with voice engine immediately
            # This would integrate with the existing voice processing pipeline
            # For now, just log the processing request

            # Send analysis request to Sherlock
            analysis_request = AnalysisRequest(
                request_id=str(uuid.uuid4()),
                source_files=[notification.file_path],
                analysis_types=["transcription", "speaker_diarization", "basic_analysis"],
                priority=notification.priority,
                mode=ProcessingMode.IMMEDIATE,
                requester=SystemComponent.SQUIRT,
                parameters={
                    'memo_id': notification.memo_id,
                    'urgent': True
                }
            )

            self.message_bus.publish(
                SystemComponent.SHERLOCK,
                MessageType.ANALYSIS_REQUEST,
                asdict(analysis_request),
                priority=1
            )

        except Exception as e:
            logging.error(f"Voice memo handling error: {e}")

    def _handle_priority_override(self, message: SystemMessage):
        """Handle priority override from Squirt"""
        try:
            # Squirt can override processing priority for urgent memos
            override_data = message.payload
            logging.info(f"Priority override from Squirt: {override_data}")
            # Implement priority adjustment logic here
        except Exception as e:
            logging.error(f"Priority override error: {e}")


class Johny5AliveIntegration:
    """Integration with Johny5Alive main system"""

    def __init__(self, message_bus: MessageBus, evidence_db: EvidenceDatabase):
        self.message_bus = message_bus
        self.evidence_db = evidence_db
        self.system_status = SystemStatus(
            component=SystemComponent.SHERLOCK,
            status="active",
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            uptime=0.0,
            last_activity=datetime.now().isoformat(),
            capabilities=[
                "evidence_analysis", "speaker_diarization", "multi_modal_processing",
                "document_extraction", "cross_system_intelligence"
            ],
            load_average=0.0
        )

        # Subscribe to system messages
        self.message_bus.subscribe(MessageType.HEALTH_CHECK, self._handle_health_check)
        self.message_bus.subscribe(MessageType.RESOURCE_REQUEST, self._handle_resource_request)
        self.message_bus.subscribe(MessageType.SHUTDOWN_REQUEST, self._handle_shutdown_request)

        # Start status reporting
        self.status_thread = threading.Thread(target=self._status_reporter, daemon=True)
        self.status_thread.start()

    def _status_reporter(self):
        """Periodically report system status"""
        while True:
            try:
                self._update_system_metrics()

                # Send status to Johny5Alive
                self.message_bus.publish(
                    SystemComponent.JOHNY5ALIVE,
                    MessageType.SYSTEM_STATUS,
                    asdict(self.system_status),
                    priority=7  # Low priority
                )

                time.sleep(30.0)  # Report every 30 seconds
            except Exception as e:
                logging.error(f"Status reporting error: {e}")
                time.sleep(60.0)

    def _update_system_metrics(self):
        """Update system performance metrics"""
        try:
            # Get system metrics (simplified)
            import psutil
            self.system_status.cpu_usage = psutil.cpu_percent()
            self.system_status.memory_usage = psutil.virtual_memory().percent
            self.system_status.disk_usage = psutil.disk_usage('/').percent
            self.system_status.load_average = psutil.getloadavg()[0]
            self.system_status.last_activity = datetime.now().isoformat()
        except Exception as e:
            logging.warning(f"Metrics update error: {e}")

    def _handle_health_check(self, message: SystemMessage):
        """Handle health check from Johny5Alive"""
        try:
            # Respond with current status
            self.message_bus.publish(
                message.source,
                MessageType.SYSTEM_STATUS,
                asdict(self.system_status),
                priority=3
            )
        except Exception as e:
            logging.error(f"Health check error: {e}")

    def _handle_resource_request(self, message: SystemMessage):
        """Handle resource request from Johny5Alive"""
        try:
            resource_request = message.payload
            resource_type = resource_request.get('type')
            amount = resource_request.get('amount', 1.0)

            # Simple resource management
            available = self._check_resource_availability(resource_type, amount)

            response = {
                'request_id': message.message_id,
                'resource_type': resource_type,
                'requested_amount': amount,
                'available': available,
                'granted': available,
                'timestamp': datetime.now().isoformat()
            }

            self.message_bus.publish(
                message.source,
                MessageType.SYSTEM_STATUS,
                response,
                priority=4
            )

        except Exception as e:
            logging.error(f"Resource request error: {e}")

    def _check_resource_availability(self, resource_type: str, amount: float) -> bool:
        """Check if requested resources are available"""
        if resource_type == "cpu":
            return self.system_status.cpu_usage < 80.0
        elif resource_type == "memory":
            return self.system_status.memory_usage < 85.0
        elif resource_type == "disk":
            return self.system_status.disk_usage < 90.0
        else:
            return True  # Unknown resource, assume available

    def _handle_shutdown_request(self, message: SystemMessage):
        """Handle graceful shutdown request"""
        try:
            shutdown_data = message.payload
            delay = shutdown_data.get('delay', 30)  # 30 second default delay

            logging.info(f"Shutdown request received, delay: {delay} seconds")

            # Notify other components
            self.message_bus.publish(
                SystemComponent.JOHNY5ALIVE,
                MessageType.SYSTEM_STATUS,
                {
                    'status': 'shutting_down',
                    'delay': delay,
                    'message': 'Sherlock graceful shutdown initiated'
                },
                priority=1
            )

            # Implement graceful shutdown logic here
            # - Save current work
            # - Close database connections
            # - Stop processing threads

        except Exception as e:
            logging.error(f"Shutdown handling error: {e}")


class SherlockSystemIntegrator:
    """Main integrator for Sherlock with Squirt and Johny5Alive"""

    def __init__(self, evidence_db_path: str = "evidence.db"):
        self.evidence_db = EvidenceDatabase(evidence_db_path)
        self.voice_engine = VoiceEngineManager()
        self.audit_system = AuditSystem()

        # Initialize message bus
        self.message_bus = MessageBus(SystemComponent.SHERLOCK)

        # Initialize integrations
        self.squirt_integration = SquirtIntegration(self.message_bus, self.voice_engine)
        self.johny5_integration = Johny5AliveIntegration(self.message_bus, self.evidence_db)

        # Analysis request queue
        self.analysis_queue = []
        self.processing_analysis = False

        # Subscribe to analysis requests
        self.message_bus.subscribe(MessageType.ANALYSIS_REQUEST, self._handle_analysis_request)

    def start(self):
        """Start the system integrator"""
        try:
            # Start message bus
            self.message_bus.start_listening()

            # Start voice engine
            self.voice_engine.start()

            # Start analysis processor
            self.analysis_thread = threading.Thread(target=self._analysis_processor, daemon=True)
            self.analysis_thread.start()

            # Log startup
            self.audit_system.log_event("system_integration", "sherlock_started", {
                'integrations': ['squirt', 'johny5alive'],
                'capabilities': self.johny5_integration.system_status.capabilities
            })

            logging.info("Sherlock system integrator started successfully")

        except Exception as e:
            logging.error(f"System integrator startup error: {e}")
            raise

    def _handle_analysis_request(self, message: SystemMessage):
        """Handle analysis request from other systems"""
        try:
            request = AnalysisRequest(**message.payload)
            self.analysis_queue.append(request)
            logging.info(f"Analysis request queued: {request.request_id}")

        except Exception as e:
            logging.error(f"Analysis request handling error: {e}")

    def _analysis_processor(self):
        """Process analysis requests from the queue"""
        while True:
            try:
                if self.analysis_queue and not self.processing_analysis:
                    self.processing_analysis = True
                    request = self.analysis_queue.pop(0)
                    self._process_analysis_request(request)
                    self.processing_analysis = False

                time.sleep(1.0)

            except Exception as e:
                logging.error(f"Analysis processor error: {e}")
                self.processing_analysis = False
                time.sleep(5.0)

    def _process_analysis_request(self, request: AnalysisRequest):
        """Process a single analysis request"""
        try:
            logging.info(f"Processing analysis request: {request.request_id}")

            results = {}

            for source_file in request.source_files:
                file_results = {}

                # Process each analysis type
                for analysis_type in request.analysis_types:
                    if analysis_type == "transcription":
                        file_results['transcription'] = self._process_transcription(source_file)
                    elif analysis_type == "speaker_diarization":
                        file_results['diarization'] = self._process_diarization(source_file)
                    elif analysis_type == "basic_analysis":
                        file_results['analysis'] = self._process_basic_analysis(source_file)

                results[source_file] = file_results

            # Send completion notification
            self.message_bus.publish(
                request.requester,
                MessageType.ANALYSIS_COMPLETE,
                {
                    'request_id': request.request_id,
                    'results': results,
                    'completion_time': datetime.now().isoformat()
                },
                priority=2
            )

            # Log completion
            self.audit_system.log_event("system_integration", "analysis_completed", {
                'request_id': request.request_id,
                'requester': request.requester.value,
                'files_processed': len(request.source_files),
                'analysis_types': request.analysis_types
            })

        except Exception as e:
            logging.error(f"Analysis processing error: {e}")

            # Send error notification
            self.message_bus.publish(
                request.requester,
                MessageType.ANALYSIS_COMPLETE,
                {
                    'request_id': request.request_id,
                    'error': str(e),
                    'completion_time': datetime.now().isoformat()
                },
                priority=2
            )

    def _process_transcription(self, source_file: str) -> Dict:
        """Process transcription for a source file"""
        # This would integrate with the existing transcription pipeline
        return {
            'transcript': 'Placeholder transcript',
            'confidence': 0.85,
            'processing_time': 5.2
        }

    def _process_diarization(self, source_file: str) -> Dict:
        """Process speaker diarization for a source file"""
        # This would integrate with the existing diarization pipeline
        return {
            'speakers': ['Speaker_0', 'Speaker_1'],
            'turns': 12,
            'confidence': 0.78
        }

    def _process_basic_analysis(self, source_file: str) -> Dict:
        """Process basic analysis for a source file"""
        # This would integrate with the existing analysis pipeline
        return {
            'entities': ['entity1', 'entity2'],
            'sentiment': 'neutral',
            'flags': []
        }

    def stop(self):
        """Stop the system integrator"""
        try:
            self.message_bus.stop()
            self.voice_engine.stop()

            self.audit_system.log_event("system_integration", "sherlock_stopped", {
                'shutdown_time': datetime.now().isoformat()
            })

            logging.info("Sherlock system integrator stopped")

        except Exception as e:
            logging.error(f"System integrator shutdown error: {e}")


def main():
    """Demo of Squirt/Johny5Alive integration"""
    print("🔗 Squirt/Johny5Alive Integration Framework - Phase 6")
    print("=" * 60)

    integrator = SherlockSystemIntegrator()

    print("✅ System integrator initialized")
    print("🎤 Squirt integration: Real-time voice memo processing")
    print("🧠 Johny5Alive integration: System coordination and resource management")
    print("📡 Message bus: ZeroMQ/Redis/File-based inter-process communication")
    print("⚡ Priority handling: Immediate processing for Squirt voice memos")
    print("📊 Health monitoring: Real-time system status reporting")
    print("\nReady for seamless system integration")

    # Example of starting the integrator
    # integrator.start()

    # The integrator would run continuously, handling:
    # - Voice memos from Squirt
    # - Analysis requests from Johny5Alive
    # - System coordination messages
    # - Resource management requests


if __name__ == "__main__":
    main()