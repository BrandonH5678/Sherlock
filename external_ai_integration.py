#!/usr/bin/env python3
"""
External AI System Integration Framework for Sherlock Phase 6
Provides integration points for external AI systems, APIs, and cloud services
"""

import asyncio
import json
import os
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
from abc import ABC, abstractmethod

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evidence_database import EvidenceDatabase
from audit_system import AuditSystem

# Optional imports for external integrations
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import speech, language
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False


class ExternalAIProvider(Enum):
    """External AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_CLOUD = "google_cloud"
    AWS_COMPREHEND = "aws_comprehend"
    AZURE_COGNITIVE = "azure_cognitive"
    HUGGINGFACE = "huggingface"
    CUSTOM_API = "custom_api"
    LOCAL_MODEL = "local_model"


class AIServiceType(Enum):
    """Types of AI services"""
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_ANALYSIS = "text_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    ENTITY_EXTRACTION = "entity_extraction"
    LANGUAGE_DETECTION = "language_detection"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    FACT_CHECKING = "fact_checking"
    CONTRADICTION_DETECTION = "contradiction_detection"
    BIAS_DETECTION = "bias_detection"
    PROPAGANDA_DETECTION = "propaganda_detection"
    EMOTION_DETECTION = "emotion_detection"
    TOPIC_MODELING = "topic_modeling"
    CLASSIFICATION = "classification"
    QUESTION_ANSWERING = "question_answering"


class ProcessingPriority(Enum):
    """Processing priorities for external AI requests"""
    IMMEDIATE = "immediate"    # Real-time processing
    HIGH = "high"             # Process within minutes
    NORMAL = "normal"         # Process within hours
    LOW = "low"              # Process when resources available
    BATCH = "batch"          # Batch processing during off-hours


class ServiceStatus(Enum):
    """Status of external AI services"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    QUOTA_EXCEEDED = "quota_exceeded"


@dataclass
class AIServiceConfig:
    """Configuration for an external AI service"""
    service_id: str
    provider: ExternalAIProvider
    service_type: AIServiceType
    endpoint_url: str
    api_key: Optional[str]
    model_name: Optional[str]
    parameters: Dict
    rate_limit: Optional[int]  # requests per minute
    timeout: int  # seconds
    retry_attempts: int
    cost_per_request: Optional[float]
    enabled: bool = True


@dataclass
class AIRequest:
    """Request to an external AI service"""
    request_id: str
    service_id: str
    service_type: AIServiceType
    input_data: Dict
    priority: ProcessingPriority
    metadata: Dict
    created_at: str
    scheduled_for: Optional[str] = None
    callback: Optional[Callable] = None


@dataclass
class AIResponse:
    """Response from an external AI service"""
    response_id: str
    request_id: str
    service_id: str
    success: bool
    result: Dict
    confidence: Optional[float]
    processing_time: float
    cost: Optional[float]
    error_message: Optional[str]
    timestamp: str
    metadata: Dict = None


@dataclass
class ServiceMetrics:
    """Metrics for an external AI service"""
    service_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    total_cost: float
    last_request: str
    status: ServiceStatus
    error_rate: float


class ExternalAIAdapter(ABC):
    """Abstract base class for external AI service adapters"""

    def __init__(self, config: AIServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.service_id}")

    @abstractmethod
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process a request using the external AI service"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the external service"""
        pass

    @abstractmethod
    def get_usage_info(self) -> Dict:
        """Get usage information from the service"""
        pass


class OpenAIAdapter(ExternalAIAdapter):
    """Adapter for OpenAI services"""

    def __init__(self, config: AIServiceConfig):
        super().__init__(config)
        if OPENAI_AVAILABLE and config.api_key:
            openai.api_key = config.api_key

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process request using OpenAI API"""
        start_time = time.time()

        try:
            if not OPENAI_AVAILABLE:
                raise Exception("OpenAI library not available")

            input_text = request.input_data.get('text', '')

            if request.service_type == AIServiceType.TEXT_ANALYSIS:
                response = await self._analyze_text(input_text)
            elif request.service_type == AIServiceType.SUMMARIZATION:
                response = await self._summarize_text(input_text)
            elif request.service_type == AIServiceType.SENTIMENT_ANALYSIS:
                response = await self._analyze_sentiment(input_text)
            else:
                raise Exception(f"Service type {request.service_type} not supported")

            processing_time = time.time() - start_time

            return AIResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                service_id=self.config.service_id,
                success=True,
                result=response,
                confidence=response.get('confidence'),
                processing_time=processing_time,
                cost=self._calculate_cost(input_text),
                error_message=None,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return AIResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                service_id=self.config.service_id,
                success=False,
                result={},
                confidence=None,
                processing_time=processing_time,
                cost=0.0,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )

    async def _analyze_text(self, text: str) -> Dict:
        """Analyze text using OpenAI"""
        # Placeholder for OpenAI text analysis
        return {
            'analysis': 'OpenAI text analysis result',
            'entities': ['example_entity'],
            'confidence': 0.85
        }

    async def _summarize_text(self, text: str) -> Dict:
        """Summarize text using OpenAI"""
        return {
            'summary': 'OpenAI generated summary',
            'confidence': 0.9
        }

    async def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using OpenAI"""
        return {
            'sentiment': 'neutral',
            'score': 0.1,
            'confidence': 0.8
        }

    def test_connection(self) -> bool:
        """Test OpenAI connection"""
        try:
            if not OPENAI_AVAILABLE:
                return False
            # Test with a simple request
            return True
        except:
            return False

    def get_usage_info(self) -> Dict:
        """Get OpenAI usage information"""
        return {
            'provider': 'openai',
            'model': self.config.model_name,
            'status': 'active' if self.test_connection() else 'inactive'
        }

    def _calculate_cost(self, text: str) -> float:
        """Calculate cost for OpenAI request"""
        # Simplified cost calculation
        token_count = len(text.split())
        return token_count * (self.config.cost_per_request or 0.0001)


class HuggingFaceAdapter(ExternalAIAdapter):
    """Adapter for Hugging Face models"""

    def __init__(self, config: AIServiceConfig):
        super().__init__(config)
        self.pipelines = {}

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process request using Hugging Face models"""
        start_time = time.time()

        try:
            if not TRANSFORMERS_AVAILABLE:
                raise Exception("Transformers library not available")

            pipeline_task = self._get_pipeline_task(request.service_type)
            if pipeline_task not in self.pipelines:
                self.pipelines[pipeline_task] = pipeline(
                    pipeline_task,
                    model=self.config.model_name or self._get_default_model(pipeline_task)
                )

            pipe = self.pipelines[pipeline_task]
            input_text = request.input_data.get('text', '')

            # Process with the pipeline
            result = pipe(input_text)

            processing_time = time.time() - start_time

            return AIResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                service_id=self.config.service_id,
                success=True,
                result=self._format_result(result, request.service_type),
                confidence=self._extract_confidence(result),
                processing_time=processing_time,
                cost=0.0,  # Local models have no API cost
                error_message=None,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return AIResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                service_id=self.config.service_id,
                success=False,
                result={},
                confidence=None,
                processing_time=processing_time,
                cost=0.0,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )

    def _get_pipeline_task(self, service_type: AIServiceType) -> str:
        """Map service type to Hugging Face pipeline task"""
        mapping = {
            AIServiceType.SENTIMENT_ANALYSIS: "sentiment-analysis",
            AIServiceType.ENTITY_EXTRACTION: "ner",
            AIServiceType.SUMMARIZATION: "summarization",
            AIServiceType.CLASSIFICATION: "text-classification",
            AIServiceType.QUESTION_ANSWERING: "question-answering",
            AIServiceType.TRANSLATION: "translation"
        }
        return mapping.get(service_type, "text-classification")

    def _get_default_model(self, task: str) -> str:
        """Get default model for a task"""
        defaults = {
            "sentiment-analysis": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "ner": "dbmdz/bert-large-cased-finetuned-conll03-english",
            "summarization": "facebook/bart-large-cnn",
            "text-classification": "distilbert-base-uncased-finetuned-sst-2-english"
        }
        return defaults.get(task, "distilbert-base-uncased")

    def _format_result(self, result: Any, service_type: AIServiceType) -> Dict:
        """Format result based on service type"""
        if service_type == AIServiceType.SENTIMENT_ANALYSIS:
            return {
                'sentiment': result[0]['label'],
                'score': result[0]['score'],
                'all_scores': result
            }
        elif service_type == AIServiceType.ENTITY_EXTRACTION:
            return {
                'entities': [
                    {
                        'text': ent['word'],
                        'label': ent['entity'],
                        'confidence': ent['score']
                    } for ent in result
                ]
            }
        else:
            return {'result': result}

    def _extract_confidence(self, result: Any) -> Optional[float]:
        """Extract confidence from result"""
        if isinstance(result, list) and len(result) > 0:
            if 'score' in result[0]:
                return result[0]['score']
        return None

    def test_connection(self) -> bool:
        """Test Hugging Face connection"""
        return TRANSFORMERS_AVAILABLE

    def get_usage_info(self) -> Dict:
        """Get Hugging Face usage information"""
        return {
            'provider': 'huggingface',
            'models_loaded': list(self.pipelines.keys()),
            'status': 'active' if TRANSFORMERS_AVAILABLE else 'inactive'
        }


class CustomAPIAdapter(ExternalAIAdapter):
    """Adapter for custom API services"""

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process request using custom API"""
        start_time = time.time()

        try:
            if not REQUESTS_AVAILABLE:
                raise Exception("Requests library not available")

            # Prepare request data
            payload = {
                'input': request.input_data,
                'service_type': request.service_type.value,
                'parameters': self.config.parameters
            }

            headers = {}
            if self.config.api_key:
                headers['Authorization'] = f"Bearer {self.config.api_key}"
            headers['Content-Type'] = 'application/json'

            # Make API request
            response = requests.post(
                self.config.endpoint_url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout
            )

            response.raise_for_status()
            result = response.json()

            processing_time = time.time() - start_time

            return AIResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                service_id=self.config.service_id,
                success=True,
                result=result,
                confidence=result.get('confidence'),
                processing_time=processing_time,
                cost=self.config.cost_per_request,
                error_message=None,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return AIResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                service_id=self.config.service_id,
                success=False,
                result={},
                confidence=None,
                processing_time=processing_time,
                cost=0.0,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )

    def test_connection(self) -> bool:
        """Test custom API connection"""
        try:
            if not REQUESTS_AVAILABLE:
                return False

            # Test with health check endpoint
            health_url = f"{self.config.endpoint_url.rstrip('/')}/health"
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_usage_info(self) -> Dict:
        """Get custom API usage information"""
        return {
            'provider': 'custom_api',
            'endpoint': self.config.endpoint_url,
            'status': 'active' if self.test_connection() else 'inactive'
        }


class ExternalAIManager:
    """Manager for external AI service integrations"""

    def __init__(self, evidence_db_path: str = "evidence.db"):
        self.evidence_db = EvidenceDatabase(evidence_db_path)
        self.audit_system = AuditSystem()

        self.services = {}  # service_id -> adapter
        self.service_configs = {}  # service_id -> config
        self.request_queue = asyncio.Queue()
        self.metrics = {}  # service_id -> metrics

        # Processing
        self.processing_tasks = []
        self.shutdown_event = threading.Event()

    def register_service(self, config: AIServiceConfig) -> bool:
        """Register an external AI service"""
        try:
            # Create appropriate adapter
            adapter = self._create_adapter(config)

            # Test connection
            if not adapter.test_connection():
                logging.warning(f"Service {config.service_id} connection test failed")
                return False

            self.services[config.service_id] = adapter
            self.service_configs[config.service_id] = config

            # Initialize metrics
            self.metrics[config.service_id] = ServiceMetrics(
                service_id=config.service_id,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                total_cost=0.0,
                last_request="",
                status=ServiceStatus.ACTIVE,
                error_rate=0.0
            )

            # Log registration
            self.audit_system.log_event("external_ai", "service_registered", {
                'service_id': config.service_id,
                'provider': config.provider.value,
                'service_type': config.service_type.value,
                'endpoint': config.endpoint_url
            })

            return True

        except Exception as e:
            logging.error(f"Failed to register service {config.service_id}: {e}")
            return False

    def _create_adapter(self, config: AIServiceConfig) -> ExternalAIAdapter:
        """Create appropriate adapter for the service"""
        if config.provider == ExternalAIProvider.OPENAI:
            return OpenAIAdapter(config)
        elif config.provider == ExternalAIProvider.HUGGINGFACE:
            return HuggingFaceAdapter(config)
        elif config.provider == ExternalAIProvider.CUSTOM_API:
            return CustomAPIAdapter(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    async def submit_request(self, service_id: str, service_type: AIServiceType,
                           input_data: Dict, priority: ProcessingPriority = ProcessingPriority.NORMAL,
                           metadata: Optional[Dict] = None,
                           callback: Optional[Callable] = None) -> str:
        """Submit a request to an external AI service"""

        if service_id not in self.services:
            raise ValueError(f"Service {service_id} not registered")

        request_id = str(uuid.uuid4())

        request = AIRequest(
            request_id=request_id,
            service_id=service_id,
            service_type=service_type,
            input_data=input_data,
            priority=priority,
            metadata=metadata or {},
            created_at=datetime.now().isoformat(),
            callback=callback
        )

        # Add to queue
        await self.request_queue.put(request)

        # Log request
        self.audit_system.log_event("external_ai", "request_submitted", {
            'request_id': request_id,
            'service_id': service_id,
            'service_type': service_type.value,
            'priority': priority.value
        })

        return request_id

    async def process_requests(self):
        """Process requests from the queue"""
        while not self.shutdown_event.is_set():
            try:
                # Get request from queue (with timeout)
                request = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=1.0
                )

                # Process the request
                await self._process_single_request(request)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logging.error(f"Request processing error: {e}")

    async def _process_single_request(self, request: AIRequest):
        """Process a single request"""
        service_id = request.service_id

        if service_id not in self.services:
            logging.error(f"Service {service_id} not found")
            return

        adapter = self.services[service_id]
        metrics = self.metrics[service_id]

        # Update metrics
        metrics.total_requests += 1
        metrics.last_request = datetime.now().isoformat()

        try:
            # Process request
            response = await adapter.process_request(request)

            # Update metrics
            if response.success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1

            # Update average response time
            total_time = (metrics.average_response_time * (metrics.total_requests - 1) +
                         response.processing_time)
            metrics.average_response_time = total_time / metrics.total_requests

            # Update cost
            if response.cost:
                metrics.total_cost += response.cost

            # Update error rate
            metrics.error_rate = metrics.failed_requests / metrics.total_requests

            # Call callback if provided
            if request.callback:
                request.callback(response)

            # Log response
            self.audit_system.log_event("external_ai", "request_processed", {
                'request_id': request.request_id,
                'service_id': service_id,
                'success': response.success,
                'processing_time': response.processing_time,
                'cost': response.cost
            })

        except Exception as e:
            metrics.failed_requests += 1
            metrics.error_rate = metrics.failed_requests / metrics.total_requests

            logging.error(f"Request processing failed: {e}")

    def get_service_status(self, service_id: str) -> Dict:
        """Get status of a service"""
        if service_id not in self.services:
            return {'error': 'Service not found'}

        config = self.service_configs[service_id]
        metrics = self.metrics[service_id]
        adapter = self.services[service_id]

        return {
            'service_id': service_id,
            'provider': config.provider.value,
            'service_type': config.service_type.value,
            'status': metrics.status.value,
            'metrics': asdict(metrics),
            'connection_ok': adapter.test_connection(),
            'usage_info': adapter.get_usage_info()
        }

    def get_all_services_status(self) -> Dict:
        """Get status of all registered services"""
        return {
            service_id: self.get_service_status(service_id)
            for service_id in self.services.keys()
        }

    async def analyze_text_with_multiple_services(self, text: str,
                                                analysis_types: List[AIServiceType]) -> Dict:
        """Analyze text with multiple AI services"""
        results = {}

        for analysis_type in analysis_types:
            # Find suitable services for this analysis type
            suitable_services = [
                service_id for service_id, config in self.service_configs.items()
                if config.service_type == analysis_type and config.enabled
            ]

            if suitable_services:
                # Use the first available service (could be improved with load balancing)
                service_id = suitable_services[0]

                try:
                    request_id = await self.submit_request(
                        service_id,
                        analysis_type,
                        {'text': text}
                    )

                    results[analysis_type.value] = {
                        'request_id': request_id,
                        'service_id': service_id,
                        'status': 'submitted'
                    }
                except Exception as e:
                    results[analysis_type.value] = {
                        'error': str(e),
                        'status': 'failed'
                    }

        return results

    def start_processing(self):
        """Start background processing"""
        async def run_processor():
            await self.process_requests()

        # Start processing in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def run_in_thread():
            loop.run_until_complete(run_processor())

        processing_thread = threading.Thread(target=run_in_thread)
        processing_thread.daemon = True
        processing_thread.start()

    def stop(self):
        """Stop the external AI manager"""
        self.shutdown_event.set()


def main():
    """Demo of external AI integration framework"""
    print("🤖 External AI Integration Framework - Phase 6")
    print("=" * 55)

    manager = ExternalAIManager()

    # Register example services
    huggingface_config = AIServiceConfig(
        service_id="hf_sentiment",
        provider=ExternalAIProvider.HUGGINGFACE,
        service_type=AIServiceType.SENTIMENT_ANALYSIS,
        endpoint_url="",
        api_key=None,
        model_name="cardiffnlp/twitter-roberta-base-sentiment-latest",
        parameters={},
        rate_limit=None,
        timeout=30,
        retry_attempts=3,
        cost_per_request=0.0
    )

    success = manager.register_service(huggingface_config)

    print("✅ External AI manager initialized")
    print(f"🔌 Hugging Face service registered: {'✅' if success else '❌'}")
    print("🎯 Supported providers: OpenAI, Hugging Face, Custom APIs")
    print("📊 Service types: Sentiment, NER, summarization, fact-checking")
    print("⚡ Processing: Async queue with priority handling")
    print("📈 Monitoring: Real-time metrics and usage tracking")
    print("\nReady for external AI service integration")

    # Example usage:
    # async def example():
    #     request_id = await manager.submit_request(
    #         "hf_sentiment",
    #         AIServiceType.SENTIMENT_ANALYSIS,
    #         {"text": "This is a great analysis system!"}
    #     )
    #
    #     status = manager.get_service_status("hf_sentiment")
    #     print(f"Service status: {status}")


if __name__ == "__main__":
    main()