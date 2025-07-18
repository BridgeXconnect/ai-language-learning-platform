"""
Agent Health Monitoring Service
Comprehensive monitoring and alerting for AI agent system health
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class AgentHealthMetrics:
    """Health metrics for a single agent."""
    agent_name: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    error_count: int
    uptime_percentage: float
    version: Optional[str] = None
    capabilities: Optional[List[str]] = None
    error_message: Optional[str] = None
    last_error: Optional[datetime] = None

@dataclass
class SystemHealthSummary:
    """Overall system health summary."""
    overall_status: HealthStatus
    healthy_agents: int
    total_agents: int
    average_response_time: float
    uptime_percentage: float
    last_incident: Optional[datetime]
    active_alerts: int
    
@dataclass
class HealthAlert:
    """Health monitoring alert."""
    id: str
    level: AlertLevel
    agent_name: Optional[str]
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False

class AgentHealthMonitor:
    """Comprehensive agent health monitoring service."""
    
    def __init__(self):
        self.agents = {
            "orchestrator": "http://localhost:8100",
            "course_planner": "http://localhost:8101", 
            "content_creator": "http://localhost:8102",
            "quality_assurance": "http://localhost:8103"
        }
        
        # Health tracking
        self.health_history: Dict[str, List[AgentHealthMetrics]] = {}
        self.current_health: Dict[str, AgentHealthMetrics] = {}
        
        # Alert system
        self.active_alerts: Dict[str, HealthAlert] = {}
        self.alert_history: List[HealthAlert] = []
        
        # Configuration
        self.config = {
            "check_interval_seconds": int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
            "response_time_threshold_ms": int(os.getenv("RESPONSE_TIME_THRESHOLD", "5000")),
            "error_threshold_count": int(os.getenv("ERROR_THRESHOLD_COUNT", "3")),
            "uptime_threshold_percentage": float(os.getenv("UPTIME_THRESHOLD", "95.0")),
            "history_retention_hours": int(os.getenv("HEALTH_HISTORY_RETENTION", "24")),
            "alert_cooldown_minutes": int(os.getenv("ALERT_COOLDOWN_MINUTES", "10"))
        }
        
        # Performance tracking
        self.performance_metrics = {
            "total_checks": 0,
            "failed_checks": 0,
            "average_system_response_time": 0.0,
            "last_full_system_check": None,
            "monitoring_start_time": datetime.utcnow()
        }
        
        # State
        self._monitoring_active = False
        self._monitoring_task = None
        
        # Initialize health history for all agents
        for agent_name in self.agents.keys():
            self.health_history[agent_name] = []
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self._monitoring_active:
            logger.warning("Health monitoring is already active")
            return
        
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info(f"Agent health monitoring started with {self.config['check_interval_seconds']}s interval")
        
        # Send initial system startup alert
        await self._create_alert(
            AlertLevel.INFO,
            None,
            f"Agent health monitoring system started. Monitoring {len(self.agents)} agents."
        )
    
    async def stop_monitoring(self):
        """Stop health monitoring."""
        if not self._monitoring_active:
            return
        
        self._monitoring_active = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Agent health monitoring stopped")
        
        # Send shutdown alert
        await self._create_alert(
            AlertLevel.INFO,
            None,
            "Agent health monitoring system stopped"
        )
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._monitoring_active:
            try:
                await self._perform_health_checks()
                await self._analyze_health_trends()
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.config["check_interval_seconds"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _perform_health_checks(self):
        """Perform health checks on all agents."""
        check_start = datetime.utcnow()
        
        # Import here to avoid circular imports
        from app.routes.agent_routes import call_agent
        
        health_results = {}
        total_response_time = 0
        successful_checks = 0
        
        for agent_name, endpoint in self.agents.items():
            try:
                # Perform health check
                start_time = datetime.utcnow()
                result = await call_agent(agent_name, "/health", method="GET", timeout=10)
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Determine status
                if result.get("success", False) and result.get("status") == "healthy":
                    status = HealthStatus.HEALTHY
                    error_message = None
                elif result.get("success", False):
                    status = HealthStatus.DEGRADED
                    error_message = result.get("message", "Agent responding but not fully healthy")
                else:
                    status = HealthStatus.UNHEALTHY
                    error_message = result.get("error", "Health check failed")
                
                # Calculate error count
                error_count = self._get_recent_error_count(agent_name)
                if status != HealthStatus.HEALTHY:
                    error_count += 1
                
                # Calculate uptime percentage
                uptime_percentage = self._calculate_uptime_percentage(agent_name)
                
                # Create health metrics
                health_metrics = AgentHealthMetrics(
                    agent_name=agent_name,
                    status=status,
                    response_time_ms=response_time,
                    last_check=datetime.utcnow(),
                    error_count=error_count,
                    uptime_percentage=uptime_percentage,
                    version=result.get("version"),
                    capabilities=result.get("capabilities", []),
                    error_message=error_message,
                    last_error=datetime.utcnow() if status != HealthStatus.HEALTHY else self._get_last_error_time(agent_name)
                )
                
                health_results[agent_name] = health_metrics
                
                if status == HealthStatus.HEALTHY:
                    total_response_time += response_time
                    successful_checks += 1
                
                # Store in history
                self.health_history[agent_name].append(health_metrics)
                self.current_health[agent_name] = health_metrics
                
                # Check for alert conditions
                await self._check_alert_conditions(agent_name, health_metrics)
                
            except Exception as e:
                logger.error(f"Health check failed for {agent_name}: {e}")
                
                # Create error health metrics
                error_metrics = AgentHealthMetrics(
                    agent_name=agent_name,
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=float('inf'),
                    last_check=datetime.utcnow(),
                    error_count=self._get_recent_error_count(agent_name) + 1,
                    uptime_percentage=self._calculate_uptime_percentage(agent_name),
                    error_message=str(e),
                    last_error=datetime.utcnow()
                )
                
                health_results[agent_name] = error_metrics
                self.health_history[agent_name].append(error_metrics)
                self.current_health[agent_name] = error_metrics
                
                await self._check_alert_conditions(agent_name, error_metrics)
        
        # Update performance metrics
        self.performance_metrics["total_checks"] += len(self.agents)
        self.performance_metrics["failed_checks"] += len(self.agents) - successful_checks
        
        if successful_checks > 0:
            self.performance_metrics["average_system_response_time"] = total_response_time / successful_checks
        
        self.performance_metrics["last_full_system_check"] = datetime.utcnow().isoformat()
        
        # Log summary
        healthy_count = sum(1 for metrics in health_results.values() if metrics.status == HealthStatus.HEALTHY)
        logger.info(f"Health check completed: {healthy_count}/{len(self.agents)} agents healthy")
    
    async def _check_alert_conditions(self, agent_name: str, metrics: AgentHealthMetrics):
        """Check if alert conditions are met for an agent."""
        
        # Check for agent down
        if metrics.status == HealthStatus.UNKNOWN:
            await self._create_alert(
                AlertLevel.CRITICAL,
                agent_name,
                f"Agent {agent_name} is unreachable: {metrics.error_message}"
            )
        
        # Check for high response time
        elif (metrics.status == HealthStatus.HEALTHY and 
              metrics.response_time_ms > self.config["response_time_threshold_ms"]):
            await self._create_alert(
                AlertLevel.WARNING,
                agent_name,
                f"Agent {agent_name} response time is high: {metrics.response_time_ms:.1f}ms"
            )
        
        # Check for high error count
        elif metrics.error_count >= self.config["error_threshold_count"]:
            await self._create_alert(
                AlertLevel.WARNING,
                agent_name,
                f"Agent {agent_name} has high error count: {metrics.error_count} recent errors"
            )
        
        # Check for low uptime
        elif metrics.uptime_percentage < self.config["uptime_threshold_percentage"]:
            await self._create_alert(
                AlertLevel.WARNING,
                agent_name,
                f"Agent {agent_name} has low uptime: {metrics.uptime_percentage:.1f}%"
            )
        
        # Resolve alerts if agent is now healthy
        elif metrics.status == HealthStatus.HEALTHY:
            await self._resolve_agent_alerts(agent_name)
    
    async def _create_alert(self, level: AlertLevel, agent_name: Optional[str], message: str) -> str:
        """Create a new health alert."""
        
        # Check for cooldown
        if await self._is_alert_in_cooldown(agent_name, message):
            return
        
        alert_id = f"{level.value}_{agent_name or 'system'}_{int(datetime.utcnow().timestamp())}"
        
        alert = HealthAlert(
            id=alert_id,
            level=level,
            agent_name=agent_name,
            message=message,
            created_at=datetime.utcnow()
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        logger.warning(f"Health alert created: [{level.value.upper()}] {message}")
        
        # Send WebSocket notification if available
        try:
            from app.services.websocket_service import connection_manager
            await connection_manager.broadcast_health_update({
                "alert": asdict(alert),
                "type": "health_alert",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to send alert via WebSocket: {e}")
        
        return alert_id
    
    async def _resolve_agent_alerts(self, agent_name: str):
        """Resolve all active alerts for an agent."""
        resolved_count = 0
        
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.agent_name == agent_name and not alert.resolved_at:
                alert.resolved_at = datetime.utcnow()
                del self.active_alerts[alert_id]
                resolved_count += 1
                
                logger.info(f"Resolved alert: {alert.message}")
        if resolved_count > 0:
            logger.info(f"Resolved {resolved_count} alerts for agent {agent_name}")
    
    async def _is_alert_in_cooldown(self, agent_name: Optional[str], message: str) -> bool:
        """Check if similar alert is in cooldown period."""
        cooldown_period = timedelta(minutes=self.config["alert_cooldown_minutes"])
        cutoff_time = datetime.utcnow() - cooldown_period
        
        for alert in self.alert_history:
            if (alert.agent_name == agent_name and 
                alert.message == message and 
                alert.created_at > cutoff_time):
                return True
        
        return False
    
    def _get_recent_error_count(self, agent_name: str) -> int:
        """Get recent error count for an agent."""
        if agent_name not in self.health_history:
            return 0
        
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_checks = [
            check for check in self.health_history[agent_name]
            if check.last_check > recent_cutoff
        ]
        
        return sum(1 for check in recent_checks if check.status != HealthStatus.HEALTHY)
    
    def _calculate_uptime_percentage(self, agent_name: str) -> float:
        """Calculate uptime percentage for an agent."""
        if agent_name not in self.health_history:
            return 100.0
        
        recent_cutoff = datetime.utcnow() - timedelta(hours=self.config["history_retention_hours"])
        recent_checks = [
            check for check in self.health_history[agent_name]
            if check.last_check > recent_cutoff
        ]
        
        if not recent_checks:
            return 100.0
        
        healthy_checks = sum(1 for check in recent_checks if check.status == HealthStatus.HEALTHY)
        return (healthy_checks / len(recent_checks)) * 100
    
    def _get_last_error_time(self, agent_name: str) -> Optional[datetime]:
        """Get the last error time for an agent."""
        if agent_name not in self.health_history:
            return None
        
        for check in reversed(self.health_history[agent_name]):
            if check.status != HealthStatus.HEALTHY:
                return check.last_error
        
        return None
    
    async def _analyze_health_trends(self):
        """Analyze health trends and create predictive alerts."""
        try:
            for agent_name in self.agents.keys():
                if agent_name not in self.health_history:
                    continue
                
                recent_checks = self.health_history[agent_name][-10:]  # Last 10 checks
                
                if len(recent_checks) < 5:
                    continue
                
                # Trend analysis
                response_times = [check.response_time_ms for check in recent_checks if check.response_time_ms != float('inf')]
                
                if len(response_times) >= 3:
                    # Check for increasing response time trend
                    recent_avg = sum(response_times[-3:]) / 3
                    older_avg = sum(response_times[:-3]) / max(len(response_times) - 3, 1)
                    
                    if recent_avg > older_avg * 1.5:  # 50% increase
                        await self._create_alert(
                            AlertLevel.WARNING,
                            agent_name,
                            f"Agent {agent_name} showing increasing response time trend: {recent_avg:.1f}ms avg"
                        )
                
                # Check for frequent status changes
                status_changes = 0
                for i in range(1, len(recent_checks)):
                    if recent_checks[i].status != recent_checks[i-1].status:
                        status_changes += 1
                
                if status_changes >= 4:  # More than 4 status changes in last 10 checks
                    await self._create_alert(
                        AlertLevel.WARNING,
                        agent_name,
                        f"Agent {agent_name} showing instability: {status_changes} status changes in recent checks"
                    )
        except Exception as e:
            logger.error(f"Error in health trend analysis: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old health history and alert data."""
        try:
            retention_cutoff = datetime.utcnow() - timedelta(hours=self.config["history_retention_hours"])
            
            # Clean up health history
            for agent_name in self.health_history.keys():
                self.health_history[agent_name] = [
                    check for check in self.health_history[agent_name]
                    if check.last_check > retention_cutoff
                ]
            
            # Clean up alert history (keep more alerts for longer)
            alert_retention_cutoff = datetime.utcnow() - timedelta(days=7)
            self.alert_history = [
                alert for alert in self.alert_history
                if alert.created_at > alert_retention_cutoff
            ]
            
        except Exception as e:
            logger.error(f"Error in health data cleanup: {e}")
    
    # Public API methods
    
    def get_current_health(self) -> Dict[str, Dict[str, Any]]:
        """Get current health status for all agents."""
        return {
            agent_name: asdict(metrics)
            for agent_name, metrics in self.current_health.items()
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        if not self.current_health:
            return {
                "overall_status": HealthStatus.UNKNOWN,
                "healthy_agents": 0,
                "total_agents": len(self.agents),
                "average_response_time": 0,
                "uptime_percentage": 0,
                "active_alerts": 0
            }
        
        healthy_agents = sum(1 for metrics in self.current_health.values() if metrics.status == HealthStatus.HEALTHY)
        total_agents = len(self.current_health)
        
        # Determine overall status
        if healthy_agents == total_agents:
            overall_status = HealthStatus.HEALTHY
        elif healthy_agents > total_agents // 2:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        # Calculate averages
        response_times = [
            metrics.response_time_ms for metrics in self.current_health.values()
            if metrics.response_time_ms != float('inf')
        ]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        uptime_percentages = [metrics.uptime_percentage for metrics in self.current_health.values()]
        avg_uptime = sum(uptime_percentages) / len(uptime_percentages) if uptime_percentages else 0
        
        # Get last incident
        last_incident = None
        for alert in reversed(self.alert_history):
            if alert.level in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
                last_incident = alert.created_at
                break
        
        return {
            "overall_status": overall_status,
            "healthy_agents": healthy_agents,
            "total_agents": total_agents,
            "average_response_time": round(avg_response_time, 2),
            "uptime_percentage": round(avg_uptime, 2),
            "last_incident": last_incident.isoformat() if last_incident else None,
            "active_alerts": len(self.active_alerts)
        }
    
    def get_alerts(self, include_resolved: bool = False) -> List[Dict[str, Any]]:
        """Get alerts."""
        if include_resolved:
            return [asdict(alert) for alert in self.alert_history]
        else:
            return [asdict(alert) for alert in self.active_alerts.values()]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get monitoring performance metrics."""
        return {
            **self.performance_metrics,
            "success_rate": round(
                ((self.performance_metrics["total_checks"] - self.performance_metrics["failed_checks"]) / 
                 max(self.performance_metrics["total_checks"], 1)) * 100, 2
            ),
            "monitoring_uptime_hours": round(
                (datetime.utcnow() - self.performance_metrics["monitoring_start_time"]).total_seconds() / 3600, 2
            )
        }
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.utcnow()
            del self.active_alerts[alert_id]
            logger.info(f"Alert manually resolved: {alert_id}")
            return True
        return False

# Global health monitor instance
agent_health_monitor = AgentHealthMonitor()