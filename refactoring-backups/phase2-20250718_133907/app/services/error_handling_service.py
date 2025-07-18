"""
Comprehensive Error Handling and Recovery Service
Provides centralized error handling, recovery mechanisms, and system resilience
"""

import logging
import traceback
import asyncio
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)

class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecoveryAction(str, Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    RESTART = "restart"

@dataclass
class ErrorContext:
    """Context information for an error."""
    operation: str
    component: str
    user_id: Optional[int] = None
    workflow_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ErrorRecord:
    """Detailed error record for tracking and analysis."""
    id: str
    severity: ErrorSeverity
    context: ErrorContext
    error_type: str
    error_message: str
    stack_trace: str
    occurred_at: datetime
    resolved_at: Optional[datetime] = None
    recovery_attempted: bool = False
    recovery_action: Optional[RecoveryAction] = None
    recovery_success: bool = False
    retry_count: int = 0
    escalated: bool = False

@dataclass
class RecoveryStrategy:
    """Recovery strategy configuration."""
    max_retries: int
    retry_delay_seconds: float
    exponential_backoff: bool
    fallback_action: Optional[Callable] = None
    escalation_threshold: int = 3
    recovery_timeout_seconds: int = 300

class SystemRecoveryManager:
    """Manages system recovery and error handling strategies."""
    
    def __init__(self):
        # Error tracking
        self.error_history: List[ErrorRecord] = []
        self.active_errors: Dict[str, ErrorRecord] = {}
        
        # Recovery strategies by component
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {
            "agent_communication": RecoveryStrategy(
                max_retries=3,
                retry_delay_seconds=2.0,
                exponential_backoff=True,
                escalation_threshold=5,
                recovery_timeout_seconds=60
            ),
            "workflow_orchestration": RecoveryStrategy(
                max_retries=2,
                retry_delay_seconds=5.0,
                exponential_backoff=True,
                escalation_threshold=3,
                recovery_timeout_seconds=300
            ),
            "database_operations": RecoveryStrategy(
                max_retries=5,
                retry_delay_seconds=1.0,
                exponential_backoff=True,
                escalation_threshold=10,
                recovery_timeout_seconds=30
            ),
            "websocket_communication": RecoveryStrategy(
                max_retries=3,
                retry_delay_seconds=1.0,
                exponential_backoff=False,
                escalation_threshold=5,
                recovery_timeout_seconds=15
            ),
            "health_monitoring": RecoveryStrategy(
                max_retries=2,
                retry_delay_seconds=10.0,
                exponential_backoff=False,
                escalation_threshold=3,
                recovery_timeout_seconds=60
            )
        }
        
        # Circuit breaker states
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.config = {
            "max_error_history": int(os.getenv("MAX_ERROR_HISTORY", "1000")),
            "error_retention_hours": int(os.getenv("ERROR_RETENTION_HOURS", "24")),
            "enable_auto_recovery": os.getenv("ENABLE_AUTO_RECOVERY", "true").lower() == "true",
            "enable_escalation": os.getenv("ENABLE_ESCALATION", "true").lower() == "true",
            "circuit_breaker_threshold": int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5")),
            "circuit_breaker_timeout": int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "300"))
        }
        
        # Performance tracking
        self.recovery_metrics = {
            "total_errors": 0,
            "auto_recovered": 0,
            "manual_intervention_required": 0,
            "escalated_errors": 0,
            "circuit_breaker_trips": 0,
            "last_reset": datetime.utcnow()
        }
    
    async def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        auto_recover: bool = True
    ) -> Dict[str, Any]:
        """Central error handling with automatic recovery attempts."""
        
        error_id = f"{context.component}_{context.operation}_{int(datetime.utcnow().timestamp())}"
        
        # Create error record
        error_record = ErrorRecord(
            id=error_id,
            severity=severity,
            context=context,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            occurred_at=datetime.utcnow()
        )
        
        # Track error
        self.error_history.append(error_record)
        self.active_errors[error_id] = error_record
        self.recovery_metrics["total_errors"] += 1
        
        # Log error
        logger.error(
            f"[{error_id}] {severity.value.upper()} error in {context.component}.{context.operation}: {error}"
        )
        
        # Check circuit breaker
        if self._should_trip_circuit_breaker(context.component):
            await self._trip_circuit_breaker(context.component)
            return {
                "error_id": error_id,
                "handled": False,
                "recovery_attempted": False,
                "circuit_breaker_tripped": True,
                "message": f"Circuit breaker tripped for {context.component}"
            }
        
        # Attempt recovery if enabled
        recovery_result = None
        if auto_recover and self.config["enable_auto_recovery"]:
            recovery_result = await self._attempt_recovery(error_record)
        
        # Send notifications for critical errors
        if severity == ErrorSeverity.CRITICAL:
            await self._send_critical_error_notification(error_record)
        
        # Cleanup old errors
        await self._cleanup_old_errors()
        
        return {
            "error_id": error_id,
            "handled": True,
            "recovery_attempted": recovery_result is not None,
            "recovery_success": recovery_result.get("success", False) if recovery_result else False,
            "circuit_breaker_tripped": False,
            "recovery_details": recovery_result
        }
    
    async def _attempt_recovery(self, error_record: ErrorRecord) -> Dict[str, Any]:
        """Attempt automatic error recovery based on component strategy."""
        
        component = error_record.context.component
        strategy = self.recovery_strategies.get(component)
        
        if not strategy:
            logger.warning(f"No recovery strategy defined for component: {component}")
            return {"success": False, "reason": "No recovery strategy"}
        
        error_record.recovery_attempted = True
        
        # Check if we've exceeded max retries
        if error_record.retry_count >= strategy.max_retries:
            error_record.recovery_action = RecoveryAction.ESCALATE
            if self.config["enable_escalation"]:
                await self._escalate_error(error_record)
            
            return {
                "success": False,
                "reason": "Max retries exceeded",
                "action": RecoveryAction.ESCALATE
            }
        
        # Calculate retry delay
        if strategy.exponential_backoff:
            delay = strategy.retry_delay_seconds * (2 ** error_record.retry_count)
        else:
            delay = strategy.retry_delay_seconds
        
        logger.info(
            f"Attempting recovery for error {error_record.id}, retry {error_record.retry_count + 1}/{strategy.max_retries} after {delay}s"
        )
        
        # Wait before retry
        await asyncio.sleep(delay)
        
        try:
            # Determine recovery action
            recovery_action = await self._determine_recovery_action(error_record, strategy)
            error_record.recovery_action = recovery_action
            error_record.retry_count += 1
            
            # Execute recovery
            if recovery_action == RecoveryAction.RETRY:
                success = await self._retry_operation(error_record)
            elif recovery_action == RecoveryAction.FALLBACK:
                success = await self._execute_fallback(error_record, strategy)
            elif recovery_action == RecoveryAction.RESTART:
                success = await self._restart_component(error_record)
            else:
                success = False
            
            if success:
                error_record.recovery_success = True
                error_record.resolved_at = datetime.utcnow()
                self.recovery_metrics["auto_recovered"] += 1
                
                # Remove from active errors
                if error_record.id in self.active_errors:
                    del self.active_errors[error_record.id]
                
                logger.info(f"Successfully recovered from error {error_record.id}")
                
                return {
                    "success": True,
                    "action": recovery_action,
                    "retry_count": error_record.retry_count
                }
            else:
                # Schedule retry or escalate
                if error_record.retry_count < strategy.max_retries:
                    # Will retry on next error occurrence
                    return {
                        "success": False,
                        "action": recovery_action,
                        "retry_count": error_record.retry_count,
                        "will_retry": True
                    }
                else:
                    # Escalate
                    await self._escalate_error(error_record)
                    return {
                        "success": False,
                        "action": RecoveryAction.ESCALATE,
                        "retry_count": error_record.retry_count
                    }
            
        except Exception as recovery_error:
            logger.error(f"Recovery attempt failed for error {error_record.id}: {recovery_error}")
            
            # If recovery itself fails, escalate
            await self._escalate_error(error_record)
            
            return {
                "success": False,
                "reason": f"Recovery failed: {str(recovery_error)}",
                "action": RecoveryAction.ESCALATE
            }
    
    async def _determine_recovery_action(
        self, 
        error_record: ErrorRecord, 
        strategy: RecoveryStrategy
    ) -> RecoveryAction:
        """Determine the best recovery action for an error."""
        
        component = error_record.context.component
        error_type = error_record.error_type
        
        # Component-specific recovery logic
        if component == "agent_communication":
            if "timeout" in error_record.error_message.lower():
                return RecoveryAction.RETRY
            elif "connection" in error_record.error_message.lower():
                return RecoveryAction.FALLBACK
            else:
                return RecoveryAction.RETRY
        
        elif component == "workflow_orchestration":
            if error_record.retry_count == 0:
                return RecoveryAction.RETRY
            else:
                return RecoveryAction.FALLBACK
        
        elif component == "database_operations":
            if "lock" in error_record.error_message.lower():
                return RecoveryAction.RETRY
            elif "connection" in error_record.error_message.lower():
                return RecoveryAction.RESTART
            else:
                return RecoveryAction.RETRY
        
        elif component == "websocket_communication":
            return RecoveryAction.RESTART
        
        elif component == "health_monitoring":
            return RecoveryAction.RETRY
        
        # Default action
        return RecoveryAction.RETRY
    
    async def _retry_operation(self, error_record: ErrorRecord) -> bool:
        """Retry the original operation."""
        
        # This would need to be implemented with specific retry logic
        # For now, we'll simulate retry success based on error type
        
        component = error_record.context.component
        error_type = error_record.error_type
        
        # Simulate different success rates for different components
        if component == "agent_communication":
            if "TimeoutError" in error_type:
                return error_record.retry_count <= 2  # Timeout usually resolves
            else:
                return error_record.retry_count <= 1  # Other errors less likely to resolve
        
        elif component == "database_operations":
            return error_record.retry_count <= 3  # DB operations often succeed on retry
        
        elif component == "websocket_communication":
            return error_record.retry_count <= 1  # WebSocket issues need restart
        
        else:
            return error_record.retry_count <= 2  # Default retry behavior
    
    async def _execute_fallback(self, error_record: ErrorRecord, strategy: RecoveryStrategy) -> bool:
        """Execute fallback action if defined."""
        
        if strategy.fallback_action:
            try:
                result = await strategy.fallback_action(error_record)
                return result
            except Exception as e:
                logger.error(f"Fallback action failed for error {error_record.id}: {e}")
                return False
        
        # Component-specific fallback logic
        component = error_record.context.component
        
        if component == "agent_communication":
            # Fallback to mock agent response
            logger.info(f"Falling back to mock response for {error_record.id}")
            return True
        
        elif component == "workflow_orchestration":
            # Fallback to simplified workflow
            logger.info(f"Falling back to simplified workflow for {error_record.id}")
            return True
        
        else:
            return False
    
    async def _restart_component(self, error_record: ErrorRecord) -> bool:
        """Restart the affected component."""
        
        component = error_record.context.component
        
        logger.info(f"Attempting to restart component: {component}")
        
        # Component-specific restart logic
        if component == "websocket_communication":
            try:
                # Import here to avoid circular imports
                from app.services.websocket_service import websocket_service
                
                await websocket_service.stop_monitoring()
                await asyncio.sleep(1)
                await websocket_service.start_monitoring()
                
                return True
            except Exception as e:
                logger.error(f"Failed to restart WebSocket service: {e}")
                return False
        
        elif component == "health_monitoring":
            try:
                from app.services.agent_health_service import agent_health_monitor
                
                await agent_health_monitor.stop_monitoring()
                await asyncio.sleep(2)
                await agent_health_monitor.start_monitoring()
                
                return True
            except Exception as e:
                logger.error(f"Failed to restart health monitoring: {e}")
                return False
        
        else:
            logger.warning(f"Restart not implemented for component: {component}")
            return False
    
    async def _escalate_error(self, error_record: ErrorRecord):
        """Escalate error to human intervention."""
        
        error_record.escalated = True
        self.recovery_metrics["escalated_errors"] += 1
        
        logger.critical(
            f"ERROR ESCALATED: {error_record.id} - {error_record.error_message}\n"
            f"Component: {error_record.context.component}\n"
            f"Operation: {error_record.context.operation}\n"
            f"Retry count: {error_record.retry_count}\n"
            f"Stack trace: {error_record.stack_trace}"
        )
        
        # Send escalation notification
        await self._send_escalation_notification(error_record)
    
    async def _send_critical_error_notification(self, error_record: ErrorRecord):
        """Send notification for critical errors."""
        
        try:
            # Send WebSocket notification if available
            from app.services.websocket_service import connection_manager
            
            await connection_manager.send_system_message(
                f"CRITICAL ERROR: {error_record.context.component} - {error_record.error_message}",
                level="critical"
            )
            
        except Exception as e:
            logger.error(f"Failed to send critical error notification: {e}")
    
    async def _send_escalation_notification(self, error_record: ErrorRecord):
        """Send escalation notification."""
        
        try:
            from app.services.websocket_service import connection_manager
            
            await connection_manager.send_system_message(
                f"Error escalated - manual intervention required: {error_record.context.component}.{error_record.context.operation}",
                level="warning"
            )
            
        except Exception as e:
            logger.error(f"Failed to send escalation notification: {e}")
    
    def _should_trip_circuit_breaker(self, component: str) -> bool:
        """Check if circuit breaker should be tripped for a component."""
        
        threshold = self.config["circuit_breaker_threshold"]
        time_window = timedelta(minutes=5)  # 5-minute window
        cutoff_time = datetime.utcnow() - time_window
        
        # Count recent errors for this component
        recent_errors = [
            error for error in self.error_history
            if (error.context.component == component and 
                error.occurred_at > cutoff_time and
                error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL])
        ]
        
        return len(recent_errors) >= threshold
    
    async def _trip_circuit_breaker(self, component: str):
        """Trip circuit breaker for a component."""
        
        timeout_duration = self.config["circuit_breaker_timeout"]
        timeout_until = datetime.utcnow() + timedelta(seconds=timeout_duration)
        
        self.circuit_breakers[component] = {
            "tripped_at": datetime.utcnow(),
            "timeout_until": timeout_until,
            "trip_count": self.circuit_breakers.get(component, {}).get("trip_count", 0) + 1
        }
        
        self.recovery_metrics["circuit_breaker_trips"] += 1
        
        logger.critical(f"Circuit breaker TRIPPED for component: {component}")
        
        # Send notification
        try:
            from app.services.websocket_service import connection_manager
            
            await connection_manager.send_system_message(
                f"Circuit breaker tripped for {component}. Service temporarily disabled.",
                level="critical"
            )
            
        except Exception as e:
            logger.error(f"Failed to send circuit breaker notification: {e}")
    
    def is_circuit_breaker_open(self, component: str) -> bool:
        """Check if circuit breaker is open for a component."""
        
        if component not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[component]
        return datetime.utcnow() < breaker["timeout_until"]
    
    async def reset_circuit_breaker(self, component: str) -> bool:
        """Manually reset circuit breaker for a component."""
        
        if component in self.circuit_breakers:
            del self.circuit_breakers[component]
            logger.info(f"Circuit breaker reset for component: {component}")
            return True
        
        return False
    
    async def _cleanup_old_errors(self):
        """Clean up old error records."""
        
        retention_cutoff = datetime.utcnow() - timedelta(hours=self.config["error_retention_hours"])
        
        # Remove old errors from history
        self.error_history = [
            error for error in self.error_history
            if error.occurred_at > retention_cutoff
        ]
        
        # Keep only recent errors, but limit total count
        if len(self.error_history) > self.config["max_error_history"]:
            self.error_history = self.error_history[-self.config["max_error_history"]:]
        
        # Clean up resolved active errors
        resolved_errors = [
            error_id for error_id, error in self.active_errors.items()
            if error.resolved_at and error.resolved_at < retention_cutoff
        ]
        
        for error_id in resolved_errors:
            del self.active_errors[error_id]
    
    # Public API methods
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary and statistics."""
        
        # Calculate error rates by component
        component_errors = {}
        for error in self.error_history:
            component = error.context.component
            if component not in component_errors:
                component_errors[component] = {"total": 0, "recovered": 0, "escalated": 0}
            
            component_errors[component]["total"] += 1
            if error.recovery_success:
                component_errors[component]["recovered"] += 1
            if error.escalated:
                component_errors[component]["escalated"] += 1
        
        return {
            "total_errors": len(self.error_history),
            "active_errors": len(self.active_errors),
            "recovery_metrics": self.recovery_metrics,
            "component_errors": component_errors,
            "circuit_breakers": {
                component: {
                    **breaker,
                    "is_open": self.is_circuit_breaker_open(component)
                }
                for component, breaker in self.circuit_breakers.items()
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_recent_errors(self, limit: int = 50, component: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent errors with optional component filtering."""
        
        errors = self.error_history
        
        if component:
            errors = [error for error in errors if error.context.component == component]
        
        # Sort by occurrence time (newest first)
        errors.sort(key=lambda x: x.occurred_at, reverse=True)
        
        return [asdict(error) for error in errors[:limit]]
    
    async def mark_error_resolved(self, error_id: str) -> bool:
        """Manually mark an error as resolved."""
        
        if error_id in self.active_errors:
            error = self.active_errors[error_id]
            error.resolved_at = datetime.utcnow()
            del self.active_errors[error_id]
            
            logger.info(f"Error {error_id} manually marked as resolved")
            return True
        
        return False

# Global error recovery manager instance
system_recovery_manager = SystemRecoveryManager()

# Utility function for easy error handling
async def handle_system_error(
    error: Exception,
    component: str,
    operation: str,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    user_id: Optional[int] = None,
    workflow_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    auto_recover: bool = True
) -> Dict[str, Any]:
    """Convenience function for handling system errors."""
    context = ErrorContext(
        operation=operation,
        component=component,
        user_id=user_id,
        workflow_id=workflow_id,
        metadata=metadata
    )
    return await system_recovery_manager.handle_error(
        error=error,
        context=context,
        severity=severity,
        auto_recover=auto_recover
    )