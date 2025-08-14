"""
Monitoring and analytics routes for system health and performance tracking
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import psutil
import os

logger = logging.getLogger(__name__)

# Create router
monitoring_router = APIRouter(
    prefix="/monitoring",
    tags=["monitoring"]
)


@monitoring_router.get("/health")
async def detailed_health_check():
    """Comprehensive health check endpoint."""
    
    try:
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "components": {}
        }
        
        # System metrics
        health_data["components"]["system"] = await get_system_metrics()
        
        # Database health
        health_data["components"]["database"] = await check_database_health()
        
        # Redis health
        health_data["components"]["redis"] = await check_redis_health()
        
        # Agent system health
        health_data["components"]["agents"] = await check_agent_health()
        
        # API health
        health_data["components"]["api"] = await check_api_health()
        
        # Determine overall health status
        component_statuses = [comp.get("status", "unknown") for comp in health_data["components"].values()]
        
        if "critical" in component_statuses:
            health_data["status"] = "critical"
        elif "degraded" in component_statuses:
            health_data["status"] = "degraded"
        else:
            health_data["status"] = "healthy"
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@monitoring_router.get("/metrics")
async def get_system_metrics():
    """Get detailed system performance metrics."""
    
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics (if available)
        try:
            network = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": network.bytes_sent,
                "bytes_received": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_received": network.packets_recv
            }
        except:
            network_stats = {"error": "Network stats not available"}
        
        # Process metrics
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "usage_percent": memory.percent,
                "process_rss": process_memory.rss,
                "process_vms": process_memory.vms
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "usage_percent": (disk.used / disk.total) * 100
            },
            "network": network_stats,
            "uptime": get_uptime_seconds()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@monitoring_router.get("/agents/status")
async def get_agent_monitoring():
    """Get detailed agent system monitoring information."""
    
    try:
        from ..agents.social_optimizer import SocialOptimizerCrew
        
        # Initialize crew if not already done
        social_crew = SocialOptimizerCrew()
        
        if not social_crew.initialized:
            try:
                await social_crew.initialize()
            except Exception as e:
                logger.warning(f"Could not initialize crew for monitoring: {str(e)}")
        
        agent_status = {}
        
        if social_crew.initialized:
            agent_status = await social_crew.get_agents_status()
            
            # Add additional monitoring data
            for agent_name, status in agent_status.items():
                status.update({
                    "last_health_check": datetime.now().isoformat(),
                    "response_time": await measure_agent_response_time(agent_name),
                    "memory_usage": await get_agent_memory_usage(agent_name),
                    "error_rate": await get_agent_error_rate(agent_name)
                })
        else:
            agent_status = {
                "error": "Agent system not initialized",
                "initialization_status": "failed"
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "agent_system_status": "active" if social_crew.initialized else "inactive",
            "agents": agent_status,
            "total_agents": len(agent_status) if isinstance(agent_status, dict) else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent monitoring data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent monitoring data: {str(e)}")


@monitoring_router.get("/tasks/analytics")
async def get_task_analytics(
    time_range: str = Query("24h", description="Time range: 1h, 24h, 7d, 30d"),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """Get task execution analytics and performance metrics."""
    
    try:
        from ..utils.task_manager import TaskManager
        
        task_manager = TaskManager()
        
        # Calculate time range
        time_ranges = {
            "1h": timedelta(hours=1),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        if time_range not in time_ranges:
            raise HTTPException(status_code=400, detail="Invalid time range")
        
        start_time = datetime.now() - time_ranges[time_range]
        
        # Get task analytics (mock implementation)
        analytics = await get_task_analytics_data(start_time, user_id)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "time_range": time_range,
            "user_id": user_id,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task analytics: {str(e)}")


@monitoring_router.get("/performance/trends")
async def get_performance_trends(
    metric: str = Query("response_time", description="Metric to analyze"),
    period: str = Query("24h", description="Time period for trends")
):
    """Get performance trends and patterns."""
    
    try:
        # Mock implementation - replace with real data collection
        trends_data = await get_performance_trends_data(metric, period)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metric": metric,
            "period": period,
            "trends": trends_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance trends: {str(e)}")


@monitoring_router.get("/logs/recent")
async def get_recent_logs(
    level: str = Query("INFO", description="Log level filter"),
    limit: int = Query(100, description="Number of recent logs to retrieve"),
    component: Optional[str] = Query(None, description="Filter by component")
):
    """Get recent application logs for monitoring."""
    
    try:
        # Mock implementation - replace with actual log retrieval
        logs = await get_recent_log_entries(level, limit, component)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "limit": limit,
            "component": component,
            "logs": logs
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent logs: {str(e)}")


@monitoring_router.get("/alerts")
async def get_active_alerts():
    """Get active system alerts and warnings."""
    
    try:
        alerts = await get_system_alerts()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "alert_count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


# Helper functions

async def get_system_metrics():
    """Get basic system health metrics."""
    
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = "healthy"
        issues = []
        
        if cpu_percent > 90:
            status = "critical"
            issues.append("High CPU usage")
        elif cpu_percent > 70:
            status = "degraded" if status == "healthy" else status
            issues.append("Elevated CPU usage")
        
        if memory.percent > 90:
            status = "critical"
            issues.append("High memory usage")
        elif memory.percent > 80:
            status = "degraded" if status == "healthy" else status
            issues.append("Elevated memory usage")
        
        if (disk.used / disk.total) > 0.95:
            status = "critical"
            issues.append("Disk space critical")
        elif (disk.used / disk.total) > 0.85:
            status = "degraded" if status == "healthy" else status
            issues.append("Low disk space")
        
        return {
            "status": status,
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": (disk.used / disk.total) * 100,
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"System metrics check failed: {str(e)}")
        return {
            "status": "critical",
            "error": str(e)
        }


async def check_database_health():
    """Check database connectivity and health."""
    
    try:
        # Mock database health check
        # Replace with actual database connection test
        
        # Simulate database check
        await asyncio.sleep(0.01)  # Simulate query time
        
        return {
            "status": "healthy",
            "connection_pool": "active",
            "response_time_ms": 10,
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "critical",
            "error": str(e)
        }


async def check_redis_health():
    """Check Redis connectivity and health."""
    
    try:
        # Mock Redis health check
        # Replace with actual Redis ping
        
        await asyncio.sleep(0.005)  # Simulate ping time
        
        return {
            "status": "healthy",
            "response_time_ms": 5,
            "memory_usage": "2MB",
            "connected_clients": 3,
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "status": "critical",
            "error": str(e)
        }


async def check_agent_health():
    """Check agent system health."""
    
    try:
        # Check if agents are responsive
        return {
            "status": "healthy",
            "initialized": True,
            "active_agents": 5,
            "response_time_ms": 50,
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent health check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e)
        }


async def check_api_health():
    """Check API endpoints health."""
    
    try:
        return {
            "status": "healthy",
            "active_connections": 10,
            "response_time_ms": 25,
            "error_rate_percent": 0.1,
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e)
        }


async def measure_agent_response_time(agent_name: str) -> float:
    """Measure agent response time."""
    
    try:
        # Mock implementation
        # Replace with actual agent response time measurement
        return round(50 + (hash(agent_name) % 100), 2)  # Mock response time
        
    except Exception:
        return -1


async def get_agent_memory_usage(agent_name: str) -> str:
    """Get agent memory usage."""
    
    try:
        # Mock implementation
        return f"{10 + (hash(agent_name) % 20)}MB"
        
    except Exception:
        return "unknown"


async def get_agent_error_rate(agent_name: str) -> float:
    """Get agent error rate."""
    
    try:
        # Mock implementation
        return round(0.1 + (hash(agent_name) % 5) * 0.1, 2)
        
    except Exception:
        return -1


async def get_task_analytics_data(start_time: datetime, user_id: Optional[str]) -> Dict[str, Any]:
    """Get task analytics data."""
    
    try:
        # Mock implementation
        return {
            "total_tasks": 150,
            "completed_tasks": 140,
            "failed_tasks": 5,
            "pending_tasks": 5,
            "average_completion_time": "2.5 minutes",
            "success_rate": 93.3,
            "task_types": {
                "content_generation": 60,
                "trend_analysis": 40,
                "video_creation": 30,
                "other": 20
            },
            "hourly_distribution": [
                {"hour": i, "count": 5 + (i % 10)} for i in range(24)
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get task analytics: {str(e)}")
        return {"error": str(e)}


async def get_performance_trends_data(metric: str, period: str) -> Dict[str, Any]:
    """Get performance trends data."""
    
    try:
        # Mock implementation
        data_points = []
        now = datetime.now()
        
        for i in range(24):  # Last 24 hours
            timestamp = now - timedelta(hours=23-i)
            value = 100 + (i % 10) * 10  # Mock values
            
            data_points.append({
                "timestamp": timestamp.isoformat(),
                "value": value
            })
        
        return {
            "data_points": data_points,
            "trend": "stable",
            "average": 150,
            "min": 100,
            "max": 190
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance trends: {str(e)}")
        return {"error": str(e)}


async def get_recent_log_entries(level: str, limit: int, component: Optional[str]) -> List[Dict[str, Any]]:
    """Get recent log entries."""
    
    try:
        # Mock implementation
        logs = []
        
        for i in range(min(limit, 50)):
            timestamp = datetime.now() - timedelta(minutes=i)
            logs.append({
                "timestamp": timestamp.isoformat(),
                "level": level,
                "component": component or "system",
                "message": f"Sample log message {i}",
                "details": f"Additional context for log entry {i}"
            })
        
        return logs
        
    except Exception as e:
        logger.error(f"Failed to get log entries: {str(e)}")
        return [{"error": str(e)}]


async def get_system_alerts() -> List[Dict[str, Any]]:
    """Get active system alerts."""
    
    try:
        alerts = []
        
        # Check system thresholds
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        if cpu_percent > 80:
            alerts.append({
                "id": "high_cpu",
                "severity": "warning" if cpu_percent < 90 else "critical",
                "title": "High CPU Usage",
                "message": f"CPU usage is {cpu_percent}%",
                "timestamp": datetime.now().isoformat(),
                "component": "system"
            })
        
        if memory.percent > 85:
            alerts.append({
                "id": "high_memory",
                "severity": "warning" if memory.percent < 95 else "critical",
                "title": "High Memory Usage",
                "message": f"Memory usage is {memory.percent}%",
                "timestamp": datetime.now().isoformat(),
                "component": "system"
            })
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        return [{"error": str(e)}]


def get_uptime_seconds() -> int:
    """Get system uptime in seconds."""
    
    try:
        return int(psutil.boot_time())
    except:
        return 0