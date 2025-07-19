"""
Workflow Audit Trail and Performance Monitoring Service
Provides comprehensive tracking, auditing, and performance analysis for course generation workflows
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os
import uuid

logger = logging.getLogger(__name__)

class AuditEventType(str, Enum):
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_FAILED = "stage_failed"
    AGENT_CALLED = "agent_called"
    AGENT_RESPONDED = "agent_responded"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    PERFORMANCE_METRIC = "performance_metric"

class WorkflowStage(str, Enum):
    PLANNING = "planning"
    CONTENT_CREATION = "content_creation"
    QUALITY_REVIEW = "quality_review"
    FINALIZATION = "finalization"

@dataclass
class AuditEvent:
    """Individual audit event record."""
    id: str
    event_type: AuditEventType
    timestamp: datetime
    workflow_id: Optional[str]
    course_request_id: Optional[int]
    user_id: Optional[int]
    component: str
    operation: str
    details: Dict[str, Any]
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class WorkflowAuditTrail:
    """Complete audit trail for a workflow."""
    workflow_id: str
    course_request_id: int
    user_id: int
    company_name: str
    started_at: datetime
    completed_at: Optional[datetime]
    total_duration_ms: Optional[float]
    status: str
    events: List[AuditEvent]
    stage_durations: Dict[str, float]
    agent_calls: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    errors: List[Dict[str, Any]]

@dataclass
class PerformanceMetrics:
    """Performance metrics for analysis."""
    metric_id: str
    timestamp: datetime
    workflow_id: Optional[str]
    metric_type: str
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]

class AuditService:
    """Comprehensive audit and performance monitoring service."""
    
    def __init__(self):
        # Audit storage
        self.audit_events: List[AuditEvent] = []
        self.workflow_trails: Dict[str, WorkflowAuditTrail] = {}
        self.performance_metrics: List[PerformanceMetrics] = []
        
        # Performance tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.stage_timers: Dict[str, Dict[str, datetime]] = {}
        
        # Configuration
        self.config = {
            "max_audit_events": int(os.getenv("MAX_AUDIT_EVENTS", "10000")),
            "audit_retention_days": int(os.getenv("AUDIT_RETENTION_DAYS", "30")),
            "performance_retention_days": int(os.getenv("PERFORMANCE_RETENTION_DAYS", "7")),
            "enable_detailed_logging": os.getenv("ENABLE_DETAILED_AUDIT_LOGGING", "true").lower() == "true",
            "performance_sampling_rate": float(os.getenv("PERFORMANCE_SAMPLING_RATE", "1.0")),
            "auto_cleanup_interval_hours": int(os.getenv("AUDIT_CLEANUP_INTERVAL", "24"))
        }
        
        # Analytics cache
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
        # Background cleanup task
        self._cleanup_task = None
        self._cleanup_active = False
    
    async def start_audit_service(self):
        """Start the audit service and background tasks."""
        if not self._cleanup_active:
            self._cleanup_active = True
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Audit service started with background cleanup")
    
    async def stop_audit_service(self):
        """Stop the audit service."""
        self._cleanup_active = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Audit service stopped")
    
    async def log_event(
        self,
        event_type: AuditEventType,
        component: str,
        operation: str,
        details: Dict[str, Any],
        workflow_id: Optional[str] = None,
        course_request_id: Optional[int] = None,
        user_id: Optional[int] = None,
        duration_ms: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> str:
        """Log an audit event."""
        
        event_id = str(uuid.uuid4())
        
        event = AuditEvent(
            id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            workflow_id=workflow_id,
            course_request_id=course_request_id,
            user_id=user_id,
            component=component,
            operation=operation,
            details=details,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        # Store event
        self.audit_events.append(event)
        
        # Update workflow trail if applicable
        if workflow_id and workflow_id in self.workflow_trails:
            self.workflow_trails[workflow_id].events.append(event)
        
        # Log for external systems if enabled
        if self.config["enable_detailed_logging"]:
            logger.info(
                f"AUDIT: [{event_type.value}] {component}.{operation} - "
                f"Workflow: {workflow_id}, Duration: {duration_ms}ms, Success: {success}"
            )
        
        return event_id
    
    async def start_workflow_audit(
        self,
        workflow_id: str,
        course_request_id: int,
        user_id: int,
        company_name: str,
        details: Dict[str, Any] = None
    ):
        """Start auditing a new workflow."""
        
        # Create workflow audit trail
        trail = WorkflowAuditTrail(
            workflow_id=workflow_id,
            course_request_id=course_request_id,
            user_id=user_id,
            company_name=company_name,
            started_at=datetime.utcnow(),
            completed_at=None,
            total_duration_ms=None,
            status="started",
            events=[],
            stage_durations={},
            agent_calls=[],
            performance_metrics={},
            errors=[]
        )
        
        self.workflow_trails[workflow_id] = trail
        self.active_workflows[workflow_id] = {
            "started_at": datetime.utcnow(),
            "current_stage": None,
            "stage_start_times": {}
        }
        
        # Log start event
        await self.log_event(
            event_type=AuditEventType.WORKFLOW_STARTED,
            component="workflow_orchestrator",
            operation="start_workflow",
            details=details or {},
            workflow_id=workflow_id,
            course_request_id=course_request_id,
            user_id=user_id
        )
        
        logger.info(f"Started audit trail for workflow {workflow_id}")
    
    async def complete_workflow_audit(
        self,
        workflow_id: str,
        status: str,
        final_details: Dict[str, Any] = None,
        quality_score: Optional[float] = None
    ):
        """Complete workflow auditing."""
        
        if workflow_id not in self.workflow_trails:
            logger.warning(f"Attempted to complete audit for unknown workflow: {workflow_id}")
            return
        
        trail = self.workflow_trails[workflow_id]
        completion_time = datetime.utcnow()
        
        # Update trail
        trail.completed_at = completion_time
        trail.status = status
        trail.total_duration_ms = (completion_time - trail.started_at).total_seconds() * 1000
        
        # Calculate performance metrics
        await self._calculate_workflow_performance(workflow_id, quality_score)
        
        # Log completion event
        event_type = AuditEventType.WORKFLOW_COMPLETED if status == "completed" else AuditEventType.WORKFLOW_FAILED
        
        await self.log_event(
            event_type=event_type,
            component="workflow_orchestrator",
            operation="complete_workflow",
            details=final_details or {},
            workflow_id=workflow_id,
            duration_ms=trail.total_duration_ms,
            success=status == "completed"
        )
        
        # Clean up active tracking
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
        
        if workflow_id in self.stage_timers:
            del self.stage_timers[workflow_id]
        
        logger.info(
            f"Completed audit trail for workflow {workflow_id}: "
            f"Status={status}, Duration={trail.total_duration_ms:.1f}ms"
        )
    
    async def start_stage_audit(
        self,
        workflow_id: str,
        stage: WorkflowStage,
        details: Dict[str, Any] = None
    ):
        """Start auditing a workflow stage."""
        
        stage_start = datetime.utcnow()
        
        # Track stage timing
        if workflow_id not in self.stage_timers:
            self.stage_timers[workflow_id] = {}
        
        self.stage_timers[workflow_id][stage.value] = stage_start
        
        # Update active workflow tracking
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["current_stage"] = stage.value
            self.active_workflows[workflow_id]["stage_start_times"][stage.value] = stage_start
        
        # Log stage start
        await self.log_event(
            event_type=AuditEventType.STAGE_STARTED,
            component="workflow_orchestrator",
            operation=f"start_{stage.value}",
            details=details or {},
            workflow_id=workflow_id
        )
    
    async def complete_stage_audit(
        self,
        workflow_id: str,
        stage: WorkflowStage,
        success: bool = True,
        details: Dict[str, Any] = None,
        error_message: Optional[str] = None
    ):
        """Complete stage auditing."""
        
        stage_end = datetime.utcnow()
        duration_ms = None
        
        # Calculate stage duration
        if (workflow_id in self.stage_timers and 
            stage.value in self.stage_timers[workflow_id]):
            
            stage_start = self.stage_timers[workflow_id][stage.value]
            duration_ms = (stage_end - stage_start).total_seconds() * 1000
            
            # Update workflow trail
            if workflow_id in self.workflow_trails:
                self.workflow_trails[workflow_id].stage_durations[stage.value] = duration_ms
        
        # Log stage completion
        event_type = AuditEventType.STAGE_COMPLETED if success else AuditEventType.STAGE_FAILED
        
        await self.log_event(
            event_type=event_type,
            component="workflow_orchestrator",
            operation=f"complete_{stage.value}",
            details=details or {},
            workflow_id=workflow_id,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        # Record performance metric
        if duration_ms is not None:
            await self.record_performance_metric(
                metric_type="stage_duration",
                metric_name=f"{stage.value}_duration_ms",
                value=duration_ms,
                unit="milliseconds",
                workflow_id=workflow_id,
                context={"stage": stage.value, "success": success}
            )
    
    async def log_agent_call(
        self,
        workflow_id: str,
        agent_name: str,
        operation: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        duration_ms: float,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log an agent API call."""
        
        # Create agent call record
        agent_call = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_name": agent_name,
            "operation": operation,
            "request_size_bytes": len(json.dumps(request_data)),
            "response_size_bytes": len(json.dumps(response_data)),
            "duration_ms": duration_ms,
            "success": success,
            "error_message": error_message
        }
        
        # Add to workflow trail
        if workflow_id in self.workflow_trails:
            self.workflow_trails[workflow_id].agent_calls.append(agent_call)
        
        # Log audit events
        await self.log_event(
            event_type=AuditEventType.AGENT_CALLED,
            component="agent_client",
            operation=f"call_{agent_name}",
            details={
                "agent_name": agent_name,
                "operation": operation,
                "request_size": len(json.dumps(request_data))
            },
            workflow_id=workflow_id
        )
        
        await self.log_event(
            event_type=AuditEventType.AGENT_RESPONDED,
            component="agent_client",
            operation=f"response_{agent_name}",
            details={
                "agent_name": agent_name,
                "operation": operation,
                "response_size": len(json.dumps(response_data))
            },
            workflow_id=workflow_id,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        # Record performance metrics
        await self.record_performance_metric(
            metric_type="agent_response_time",
            metric_name=f"{agent_name}_response_time_ms",
            value=duration_ms,
            unit="milliseconds",
            workflow_id=workflow_id,
            context={"agent_name": agent_name, "operation": operation, "success": success}
        )
    
    async def record_performance_metric(
        self,
        metric_type: str,
        metric_name: str,
        value: float,
        unit: str,
        workflow_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ):
        """Record a performance metric."""
        
        # Apply sampling rate
        import random
        if random.random() > self.config["performance_sampling_rate"]:
            return
        
        metric = PerformanceMetrics(
            metric_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            workflow_id=workflow_id,
            metric_type=metric_type,
            metric_name=metric_name,
            value=value,
            unit=unit,
            context=context or {}
        )
        
        self.performance_metrics.append(metric)
        
        # Log performance event
        await self.log_event(
            event_type=AuditEventType.PERFORMANCE_METRIC,
            component="performance_monitor",
            operation="record_metric",
            details={
                "metric_type": metric_type,
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "context": context
            },
            workflow_id=workflow_id
        )
    
    async def _calculate_workflow_performance(self, workflow_id: str, quality_score: Optional[float] = None):
        """Calculate comprehensive performance metrics for a completed workflow."""
        
        if workflow_id not in self.workflow_trails:
            return
        
        trail = self.workflow_trails[workflow_id]
        
        # Calculate metrics
        metrics = {
            "total_duration_ms": trail.total_duration_ms,
            "stage_count": len(trail.stage_durations),
            "agent_calls_count": len(trail.agent_calls),
            "error_count": len([e for e in trail.events if not e.success]),
            "quality_score": quality_score
        }
        
        # Agent performance metrics
        if trail.agent_calls:
            agent_durations = [call["duration_ms"] for call in trail.agent_calls]
            metrics.update({
                "avg_agent_response_time_ms": sum(agent_durations) / len(agent_durations),
                "max_agent_response_time_ms": max(agent_durations),
                "min_agent_response_time_ms": min(agent_durations)
            })
        
        # Stage performance metrics
        if trail.stage_durations:
            stage_times = list(trail.stage_durations.values())
            metrics.update({
                "avg_stage_duration_ms": sum(stage_times) / len(stage_times),
                "longest_stage_ms": max(stage_times),
                "shortest_stage_ms": min(stage_times)
            })
        
        # Efficiency metrics
        if trail.total_duration_ms and trail.agent_calls:
            total_agent_time = sum(call["duration_ms"] for call in trail.agent_calls)
            metrics["agent_time_percentage"] = (total_agent_time / trail.total_duration_ms) * 100
            metrics["processing_efficiency"] = (total_agent_time / trail.total_duration_ms) * 100
        
        trail.performance_metrics = metrics
        
        # Record individual performance metrics
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                await self.record_performance_metric(
                    metric_type="workflow_performance",
                    metric_name=metric_name,
                    value=float(value),
                    unit="milliseconds" if "ms" in metric_name else "count",
                    workflow_id=workflow_id,
                    context={"workflow_completed": True}
                )
    
    async def _cleanup_loop(self):
        """Background cleanup task."""
        while self._cleanup_active:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(self.config["auto_cleanup_interval_hours"] * 3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in audit cleanup loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _cleanup_old_data(self):
        """Clean up old audit and performance data."""
        
        audit_cutoff = datetime.utcnow() - timedelta(days=self.config["audit_retention_days"])
        performance_cutoff = datetime.utcnow() - timedelta(days=self.config["performance_retention_days"])
        
        # Clean up audit events
        old_count = len(self.audit_events)
        self.audit_events = [
            event for event in self.audit_events
            if event.timestamp > audit_cutoff
        ]
        
        # Limit total events
        if len(self.audit_events) > self.config["max_audit_events"]:
            self.audit_events = self.audit_events[-self.config["max_audit_events"]:]
        
        # Clean up performance metrics
        old_metrics_count = len(self.performance_metrics)
        self.performance_metrics = [
            metric for metric in self.performance_metrics
            if metric.timestamp > performance_cutoff
        ]
        
        # Clean up completed workflow trails
        old_trails = [
            workflow_id for workflow_id, trail in self.workflow_trails.items()
            if (trail.completed_at and trail.completed_at < audit_cutoff)
        ]
        
        for workflow_id in old_trails:
            del self.workflow_trails[workflow_id]
        
        # Clean up analytics cache
        expired_cache_keys = [
            key for key, expiry in self.cache_expiry.items()
            if expiry < datetime.utcnow()
        ]
        
        for key in expired_cache_keys:
            if key in self.analytics_cache:
                del self.analytics_cache[key]
            del self.cache_expiry[key]
        
        if old_count > len(self.audit_events) or old_metrics_count > len(self.performance_metrics) or old_trails:
            logger.info(
                f"Audit cleanup completed: Removed {old_count - len(self.audit_events)} events, "
                f"{old_metrics_count - len(self.performance_metrics)} metrics, {len(old_trails)} trails"
            )
    
    # Public API methods
    
    def get_workflow_audit_trail(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get complete audit trail for a workflow."""
        
        if workflow_id in self.workflow_trails:
            trail = self.workflow_trails[workflow_id]
            return asdict(trail)
        
        return None
    
    def get_audit_events(
        self,
        workflow_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit events with filtering."""
        
        events = self.audit_events
        
        # Apply filters
        if workflow_id:
            events = [e for e in events if e.workflow_id == workflow_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if component:
            events = [e for e in events if e.component == component]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        events = events[:limit]
        
        return [asdict(event) for event in events]
    
    def get_performance_analytics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get performance analytics for a time window."""
        
        cache_key = f"performance_analytics_{time_window_hours}h"
        cache_expiry = datetime.utcnow() + timedelta(minutes=5)  # Cache for 5 minutes
        
        # Check cache
        if (cache_key in self.analytics_cache and 
            cache_key in self.cache_expiry and 
            self.cache_expiry[cache_key] > datetime.utcnow()):
            return self.analytics_cache[cache_key]
        
        # Calculate analytics
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Filter metrics by time window
        recent_metrics = [
            metric for metric in self.performance_metrics
            if metric.timestamp > cutoff_time
        ]
        
        # Calculate workflow analytics
        workflow_analytics = self._calculate_workflow_analytics(cutoff_time)
        
        # Calculate agent analytics
        agent_analytics = self._calculate_agent_analytics(recent_metrics)
        
        # Calculate system analytics
        system_analytics = self._calculate_system_analytics(cutoff_time)
        
        analytics = {
            "time_window_hours": time_window_hours,
            "generated_at": datetime.utcnow().isoformat(),
            "workflow_analytics": workflow_analytics,
            "agent_analytics": agent_analytics,
            "system_analytics": system_analytics,
            "total_metrics": len(recent_metrics)
        }
        
        # Cache result
        self.analytics_cache[cache_key] = analytics
        self.cache_expiry[cache_key] = cache_expiry
        
        return analytics
    
    def _calculate_workflow_analytics(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Calculate workflow-specific analytics."""
        
        # Get recent workflows
        recent_workflows = [
            trail for trail in self.workflow_trails.values()
            if trail.started_at > cutoff_time
        ]
        
        if not recent_workflows:
            return {"total_workflows": 0}
        
        # Calculate metrics
        total_workflows = len(recent_workflows)
        completed_workflows = [w for w in recent_workflows if w.status == "completed"]
        failed_workflows = [w for w in recent_workflows if w.status == "failed"]
        
        success_rate = (len(completed_workflows) / total_workflows) * 100 if total_workflows > 0 else 0
        
        # Duration analytics
        completed_durations = [w.total_duration_ms for w in completed_workflows if w.total_duration_ms]
        
        duration_analytics = {}
        if completed_durations:
            duration_analytics = {
                "avg_duration_ms": sum(completed_durations) / len(completed_durations),
                "min_duration_ms": min(completed_durations),
                "max_duration_ms": max(completed_durations),
                "median_duration_ms": sorted(completed_durations)[len(completed_durations) // 2]
            }
        
        return {
            "total_workflows": total_workflows,
            "completed_workflows": len(completed_workflows),
            "failed_workflows": len(failed_workflows),
            "success_rate_percentage": round(success_rate, 2),
            "duration_analytics": duration_analytics
        }
    
    def _calculate_agent_analytics(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Calculate agent-specific analytics."""
        
        agent_metrics = [m for m in metrics if m.metric_type == "agent_response_time"]
        
        if not agent_metrics:
            return {}
        
        # Group by agent
        agent_data = {}
        for metric in agent_metrics:
            agent_name = metric.context.get("agent_name")
            if agent_name:
                if agent_name not in agent_data:
                    agent_data[agent_name] = []
                agent_data[agent_name].append(metric.value)
        
        # Calculate analytics per agent
        agent_analytics = {}
        for agent_name, response_times in agent_data.items():
            agent_analytics[agent_name] = {
                "call_count": len(response_times),
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "median_response_time_ms": sorted(response_times)[len(response_times) // 2]
            }
        
        return agent_analytics
    
    def _calculate_system_analytics(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Calculate system-wide analytics."""
        
        # Get recent events
        recent_events = [
            event for event in self.audit_events
            if event.timestamp > cutoff_time
        ]
        
        if not recent_events:
            return {}
        
        # Calculate error rate
        error_events = [e for e in recent_events if not e.success]
        error_rate = (len(error_events) / len(recent_events)) * 100 if recent_events else 0
        
        # Component activity
        component_activity = {}
        for event in recent_events:
            component = event.component
            if component not in component_activity:
                component_activity[component] = 0
            component_activity[component] += 1
        
        return {
            "total_events": len(recent_events),
            "error_events": len(error_events),
            "error_rate_percentage": round(error_rate, 2),
            "component_activity": component_activity,
            "active_workflows": len(self.active_workflows)
        }
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get comprehensive audit summary."""
        
        return {
            "total_audit_events": len(self.audit_events),
            "total_workflow_trails": len(self.workflow_trails),
            "active_workflows": len(self.active_workflows),
            "total_performance_metrics": len(self.performance_metrics),
            "audit_service_config": self.config,
            "cleanup_active": self._cleanup_active,
            "cache_entries": len(self.analytics_cache),
            "generated_at": datetime.utcnow().isoformat()
        }

# Global audit service instance
audit_service = AuditService()