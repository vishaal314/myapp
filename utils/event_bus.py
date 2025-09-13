"""
Event Bus System for Enterprise Integration

Provides in-process event handling with optional Redis pub/sub for production scaling.
Enables enterprise features to integrate without modifying core functionality.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading

# Try importing Redis for production pub/sub - graceful fallback if not available
try:
    import redis
    from utils.redis_cache import get_cache
    REDIS_AVAILABLE = True
except ImportError:
    get_cache = None  # type: ignore
    REDIS_AVAILABLE = False

logger = logging.getLogger("utils.event_bus")

class EventType(Enum):
    """Enterprise event types for integration"""
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed" 
    SCAN_FAILED = "scan_failed"
    FINDING_DETECTED = "finding_detected"
    CRITICAL_ISSUE_FOUND = "critical_issue_found"
    DSAR_REQUEST_SUBMITTED = "dsar_request_submitted"
    DSAR_REQUEST_PROCESSED = "dsar_request_processed"
    CONSENT_UPDATED = "consent_updated"
    VENDOR_RISK_ALERT = "vendor_risk_alert"
    COMPLIANCE_EVIDENCE_ADDED = "compliance_evidence_added"
    SOC2_AUDIT_EVENT = "soc2_audit_event"
    TICKET_CREATED = "ticket_created"
    CONNECTOR_EVENT = "connector_event"
    
@dataclass
class Event:
    """Enterprise event data structure"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    source: str
    user_id: str
    session_id: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'data': self.data,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        return cls(
            event_id=data['event_id'],
            event_type=EventType(data['event_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=data['source'],
            user_id=data['user_id'],
            session_id=data['session_id'],
            data=data['data'],
            metadata=data.get('metadata', {})
        )

class EventBus:
    """
    Enterprise Event Bus for loosely-coupled integration
    
    Supports both in-process listeners and optional Redis pub/sub for scaling.
    Maintains existing functionality while enabling enterprise features.
    """
    
    def __init__(self, use_redis: bool = False):
        self.use_redis = use_redis and REDIS_AVAILABLE
        self._listeners: Dict[EventType, List[Tuple[str, Callable[[Event], None]]]] = {}
        self._lock = threading.Lock()
        self._redis_client = None
        
        if self.use_redis and get_cache is not None:
            try:
                cache = get_cache()
                # Check if Redis client has publish method (fallback for compatibility)
                if cache is not None and hasattr(cache, 'publish'):
                    self._redis_client = cache
                    logger.info("EventBus: Redis pub/sub enabled for scaling")
                else:
                    logger.warning("EventBus: Redis cache doesn't support pub/sub, using in-process mode")
                    self.use_redis = False
            except Exception as e:
                logger.warning(f"EventBus: Redis unavailable, using in-process mode: {e}")
                self.use_redis = False
    
    def subscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> str:
        """
        Subscribe to events of a specific type
        
        Args:
            event_type: The event type to listen for
            listener: Callback function that receives Event objects
            
        Returns:
            Listener ID for unsubscribing
        """
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            
            listener_id = str(uuid.uuid4())
            # Store listener with ID for removal
            listener_wrapper = (listener_id, listener)
            self._listeners[event_type].append(listener_wrapper)
            
            logger.debug(f"EventBus: Subscribed to {event_type.value}, {len(self._listeners[event_type])} listeners")
            return listener_id
    
    def unsubscribe(self, event_type: EventType, listener_id: str) -> bool:
        """
        Unsubscribe from events
        
        Args:
            event_type: The event type to unsubscribe from
            listener_id: The listener ID returned by subscribe
            
        Returns:
            True if listener was found and removed
        """
        with self._lock:
            if event_type not in self._listeners:
                return False
            
            original_count = len(self._listeners[event_type])
            self._listeners[event_type] = [
                (lid, listener) for lid, listener in self._listeners[event_type]
                if lid != listener_id
            ]
            
            removed = len(self._listeners[event_type]) < original_count
            if removed:
                logger.debug(f"EventBus: Unsubscribed from {event_type.value}")
            
            return removed
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers
        
        Args:
            event: The event to publish
        """
        try:
            # In-process delivery to local listeners
            self._deliver_local(event)
            
            # Redis pub/sub for distributed listeners (if enabled)
            if self.use_redis and self._redis_client:
                self._deliver_redis(event)
                
        except Exception as e:
            logger.error(f"EventBus: Failed to publish {event.event_type.value}: {e}")
    
    def _deliver_local(self, event: Event) -> None:
        """Deliver event to in-process listeners"""
        event_type = event.event_type
        
        if event_type not in self._listeners:
            logger.debug(f"EventBus: No listeners for {event_type.value}")
            return
        
        listeners = self._listeners[event_type].copy()  # Thread-safe copy
        
        for listener_id, listener in listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"EventBus: Listener {listener_id} failed for {event_type.value}: {e}")
    
    def _deliver_redis(self, event: Event) -> None:
        """Deliver event via Redis pub/sub"""
        try:
            channel = f"enterprise_events:{event.event_type.value}"
            message = json.dumps(event.to_dict())
            self._redis_client.publish(channel, message)
            logger.debug(f"EventBus: Published {event.event_type.value} to Redis")
        except Exception as e:
            logger.error(f"EventBus: Redis publish failed for {event.event_type.value}: {e}")
    
    def create_event(self, event_type: EventType, source: str, user_id: str, 
                    session_id: str, data: Dict[str, Any], 
                    metadata: Optional[Dict[str, Any]] = None) -> Event:
        """
        Create a new event with generated ID and timestamp
        
        Args:
            event_type: Type of event
            source: Source component/service generating the event
            user_id: User ID associated with the event
            session_id: Session ID for tracking
            data: Event-specific data
            metadata: Optional metadata
            
        Returns:
            Configured Event object
        """
        return Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(),
            source=source,
            user_id=user_id,
            session_id=session_id,
            data=data,
            metadata=metadata
        )
    
    def get_listener_count(self, event_type: EventType) -> int:
        """Get number of listeners for an event type"""
        return len(self._listeners.get(event_type, []))
    
    def get_all_listener_counts(self) -> Dict[str, int]:
        """Get listener counts for all event types"""
        return {
            event_type.value: len(listeners) 
            for event_type, listeners in self._listeners.items()
        }

# Global event bus instance
_event_bus: Optional[EventBus] = None

def get_event_bus(use_redis: bool = False) -> EventBus:
    """
    Get or create the global event bus instance
    
    Args:
        use_redis: Enable Redis pub/sub for distributed events
        
    Returns:
        EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus(use_redis=use_redis)
        logger.info("EventBus: Initialized global event bus")
    return _event_bus

def publish_event(event_type: EventType, source: str, user_id: str, 
                 session_id: str, data: Dict[str, Any], 
                 metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Convenience function to publish an event
    
    Args:
        event_type: Type of event to publish
        source: Source component/service
        user_id: User ID
        session_id: Session ID
        data: Event data
        metadata: Optional metadata
    """
    bus = get_event_bus()
    event = bus.create_event(event_type, source, user_id, session_id, data, metadata)
    bus.publish(event)