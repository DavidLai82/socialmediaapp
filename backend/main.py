"""
Main FastAPI application with CrewAI multi-agent integration
for social media optimization platform.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis

# Real crew import deferred to try/except below
from models.schemas import (
    AgentTaskRequest, 
    AgentTaskResponse, 
    ContentGenerationRequest,
    TrendAnalysisRequest,
    VideoCreationRequest,
    AgentStatus,
    ErrorResponse
)
from utils.websocket_manager import websocket_manager
from utils.task_manager import TaskManager
from config.settings import settings, validate_required_settings, setup_logging, print_startup_info

# Lightweight in-memory TaskManager fallback for development without Redis
class InMemoryTaskManager:
	def __init__(self):
		self.tasks = {}
		self.user_tasks = {}
		self.initialized = True

	async def initialize(self, _redis_client=None):
		self.initialized = True

	async def create_task(self, task_type: str, user_id: str, parameters: Dict[str, object], priority=None, max_retries: int = 3, timeout_seconds: int = 300) -> str:
		import uuid, datetime
		task_id = str(uuid.uuid4())
		task = {
			"task_id": task_id,
			"task_type": task_type,
			"user_id": user_id,
			"parameters": parameters,
			"status": "pending",
			"priority": (priority.value if hasattr(priority, "value") else priority) or 2,
			"max_retries": max_retries,
			"retry_count": 0,
			"timeout_seconds": timeout_seconds,
			"created_at": datetime.datetime.now().isoformat(),
			"updated_at": datetime.datetime.now().isoformat(),
			"started_at": None,
			"completed_at": None,
			"result": None,
			"error": None,
			"progress": 0,
		}
		self.tasks[task_id] = task
		self.user_tasks.setdefault(user_id, set()).add(task_id)
		return task_id

	async def get_task_status(self, task_id: str):
		return self.tasks.get(task_id)

	async def update_task_status(self, task_id: str, status: str, progress: Optional[int] = None, error: Optional[str] = None, result: Optional[object] = None):
		import datetime
		t = self.tasks.get(task_id)
		if not t:
			return
		t["status"] = status
		t["updated_at"] = datetime.datetime.now().isoformat()
		if progress is not None:
			t["progress"] = progress
		if error is not None:
			t["error"] = error
		if result is not None:
			t["result"] = result
		if status == "running" and not t.get("started_at"):
			t["started_at"] = datetime.datetime.now().isoformat()
		if status in ("completed", "failed", "cancelled"):
			t["completed_at"] = datetime.datetime.now().isoformat()

	async def complete_task(self, task_id: str, result: object):
		return await self.update_task_status(task_id, "completed", progress=100, result=result)

	async def fail_task(self, task_id: str, error: str):
		return await self.update_task_status(task_id, "failed", error=error)

	async def cancel_task(self, task_id: str, reason: str = "Cancelled by user"):
		return await self.update_task_status(task_id, "cancelled", error=reason)

	async def get_active_tasks_count(self) -> int:
		return sum(1 for t in self.tasks.values() if t.get("status") in ("pending", "running"))

	async def get_user_tasks(self, user_id: str, limit: int = 10, offset: int = 0):
		ids = list(self.user_tasks.get(user_id, []))
		return [self.tasks[i] for i in ids[offset:offset+limit]]

# Attempt to import real SocialOptimizerCrew, else provide a lightweight stub for development
try:
	from agents.social_optimizer import SocialOptimizerCrew as RealSocialOptimizerCrew
except Exception as import_error:  # pragma: no cover
	logger = logging.getLogger(__name__)
	logger.warning(f"Falling back to stub SocialOptimizerCrew due to import error: {import_error}")

	class RealSocialOptimizerCrew:  # type: ignore
		def __init__(self):
			self.initialized = False

		async def initialize(self):
			self.initialized = True

		async def get_agents_status(self):
			return {
				"social_optimizer": {"name": "social_optimizer", "status": "active"},
				"traffic_analyst": {"name": "traffic_analyst", "status": "active"},
				"content_writer": {"name": "content_writer", "status": "active"},
				"video_creator": {"name": "video_creator", "status": "active"},
				"script_writer": {"name": "script_writer", "status": "active"},
			}

		async def generate_content(self, **kwargs):
			return {"mock": True, "action": "generate_content", **kwargs}

		async def analyze_trends(self, **kwargs):
			return {"mock": True, "action": "analyze_trends", **kwargs}

		async def create_video_content(self, **kwargs):
			return {"mock": True, "action": "create_video_content", **kwargs}

# Import API routes
from api.websocket_routes import websocket_router
from api.monitoring_routes import monitoring_router

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Global instances
redis_client: Optional[redis.Redis] = None
# Use global singleton instance from utils
# websocket_manager imported above
task_manager: TaskManager | InMemoryTaskManager = TaskManager()
social_crew: Optional[RealSocialOptimizerCrew] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global redis_client, social_crew, task_manager
    
    # Startup
    logger.info("Starting Social Media Optimization Platform...")
    
    try:
        # Validate configuration
        validate_required_settings()
        
        # Print startup information
        print_startup_info()
        
        # Initialize Redis connection
        try:
            redis_client = redis.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db,
                password=settings.redis.password,
                max_connections=settings.redis.max_connections,
                decode_responses=True
            )
            await redis_client.ping()
            logger.info("Redis connection established")
            await task_manager.initialize(redis_client)
            logger.info("Task manager initialized")
        except Exception as redis_error:
            logger.warning(f"Redis unavailable, using in-memory task manager: {redis_error}")
            # Switch to in-memory fallback
            task_manager = InMemoryTaskManager()  # type: ignore
        
        # Initialize CrewAI social optimization crew
        if settings.ai_services.openai_api_key or settings.ai_services.anthropic_api_key:
            social_crew = RealSocialOptimizerCrew()
            await social_crew.initialize()
            logger.info("Social optimization crew initialized")
        else:
            # Initialize stub crew for development
            social_crew = RealSocialOptimizerCrew()
            await social_crew.initialize()
            logger.warning("AI keys not configured - initialized stub social crew for development")
        
        logger.info("Application startup complete!")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    try:
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
        
        logger.info("Application shutdown complete!")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.server.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors_origins,
    allow_credentials=settings.server.cors_credentials,
    allow_methods=settings.server.cors_methods,
    allow_headers=settings.server.cors_headers,
)

# Include API routers
app.include_router(websocket_router, prefix="/api")
app.include_router(monitoring_router, prefix="/api")


# Dependency to get Redis client
async def get_redis() -> redis.Redis:
    """Get Redis client dependency."""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis not initialized")
    return redis_client


# Dependency to get social crew
async def get_social_crew() -> RealSocialOptimizerCrew:
    """Get social optimization crew dependency."""
    if not social_crew:
        raise HTTPException(status_code=500, detail="Social crew not initialized")
    return social_crew


# Root endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "active",
        "agents": ["social_optimizer", "traffic_analyst", "content_writer", "video_creator", "script_writer"],
        "api_docs": "/docs",
        "health_check": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint that tolerates missing dependencies in development."""
    try:
        # Check Redis connection if available
        redis_status = "unavailable"
        if redis_client:
            try:
                await redis_client.ping()
                redis_status = "healthy"
            except Exception as e:
                redis_status = f"unhealthy: {str(e)}"

        # Check agents status
        agents_status = {}
        if social_crew and getattr(social_crew, "initialized", False):
            try:
                agents_status = await social_crew.get_agents_status()
            except Exception as e:
                agents_status = {"error": f"Failed to get agent status: {str(e)}"}

        # Get active tasks count
        active_tasks = 0
        try:
            active_tasks = await task_manager.get_active_tasks_count()
        except Exception as e:
            logger.warning(f"Failed to get active tasks count: {str(e)}")

        overall_status = "healthy"
        if redis_status not in ("healthy", "unavailable"):
            overall_status = "degraded"
        if not social_crew or not getattr(social_crew, "initialized", False):
            overall_status = "degraded" if overall_status == "healthy" else "critical"

        return {
            "status": overall_status,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "components": {
                "redis": redis_status,
                "agents": "healthy" if agents_status and not agents_status.get("error") else "degraded",
                "task_manager": "healthy" if task_manager.initialized else "degraded"
            },
            "agents": agents_status,
            "active_tasks": active_tasks,
            "environment": settings.environment,
            "version": settings.app_version
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/agents/status", response_model=Dict[str, AgentStatus])
async def get_agents_status() -> Dict[str, AgentStatus]:
    """Get status of all agents."""
    if not social_crew or not getattr(social_crew, "initialized", False):
        raise HTTPException(
            status_code=503, 
            detail="Social media optimization crew not initialized"
        )
    
    try:
        return await social_crew.get_agents_status()
    except Exception as e:
        logger.error(f"Failed to get agent status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


# Content Generation Endpoint
@app.post("/agents/content/generate", response_model=AgentTaskResponse)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    crew: RealSocialOptimizerCrew = Depends(get_social_crew)
):
    """Generate social media content using the content writing agent."""
    try:
        # Create task ID
        task_id = await task_manager.create_task(
            task_type="content_generation",
            user_id=request.user_id,
            parameters=request.dict()
        )
        
        # Start background task
        background_tasks.add_task(
            execute_content_generation,
            task_id,
            request,
            crew
        )
        
        return AgentTaskResponse(
            task_id=task_id,
            status="started",
            message="Content generation task started",
            agent="content_writer"
        )
        
    except Exception as e:
        logger.error(f"Error starting content generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Trend Analysis Endpoint
@app.post("/agents/trends/analyze", response_model=AgentTaskResponse)
async def analyze_trends(
    request: TrendAnalysisRequest,
    background_tasks: BackgroundTasks,
    crew: RealSocialOptimizerCrew = Depends(get_social_crew)
):
    """Analyze social media trends using the traffic analysis agent."""
    try:
        task_id = await task_manager.create_task(
            task_type="trend_analysis",
            user_id=request.user_id,
            parameters=request.dict()
        )
        
        background_tasks.add_task(
            execute_trend_analysis,
            task_id,
            request,
            crew
        )
        
        return AgentTaskResponse(
            task_id=task_id,
            status="started",
            message="Trend analysis task started",
            agent="traffic_analyst"
        )
        
    except Exception as e:
        logger.error(f"Error starting trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Video Creation Endpoint
@app.post("/agents/video/create", response_model=AgentTaskResponse)
async def create_video_content(
    request: VideoCreationRequest,
    background_tasks: BackgroundTasks,
    crew: RealSocialOptimizerCrew = Depends(get_social_crew)
):
    """Create video content plan using video creation and script writing agents."""
    try:
        task_id = await task_manager.create_task(
            task_type="video_creation",
            user_id=request.user_id,
            parameters=request.dict()
        )
        
        background_tasks.add_task(
            execute_video_creation,
            task_id,
            request,
            crew
        )
        
        return AgentTaskResponse(
            task_id=task_id,
            status="started",
            message="Video creation task started",
            agent="video_creator"
        )
        
    except Exception as e:
        logger.error(f"Error starting video creation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Task Status Endpoints
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task."""
    try:
        task_status = await task_manager.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/user/{user_id}")
async def get_user_tasks(user_id: str, limit: int = 10, offset: int = 0):
    """Get tasks for a specific user."""
    try:
        tasks = await task_manager.get_user_tasks(user_id, limit, offset=offset)
        return {"tasks": tasks}
        
    except Exception as e:
        logger.error(f"Error getting user tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Task cancellation endpoint
@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str, user_id: str):
    """Cancel a specific task."""
    try:
        # Verify task exists and belongs to user
        task_status = await task_manager.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task_status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this task")
        
        if task_status.get("status") in ["completed", "failed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Task cannot be cancelled")
        
        await task_manager.cancel_task(task_id, "Cancelled by user")
        
        return {"message": "Task cancelled successfully", "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task functions
async def execute_content_generation(
    task_id: str, 
    request: ContentGenerationRequest, 
    crew: RealSocialOptimizerCrew
):
    """Execute content generation task in background."""
    try:
        await task_manager.update_task_status(task_id, "running")
        
        # Execute content generation through CrewAI
        result = await crew.generate_content(
            platform=request.platform,
            topic=request.topic,
            brand_voice=request.brand_voice,
            target_audience=request.target_audience,
            content_type=request.content_type
        )
        
        await task_manager.complete_task(task_id, result)
        
        # Notify via WebSocket
        await websocket_manager.send_task_update(
            user_id=request.user_id,
            task_id=task_id,
            status="completed",
            result=result
        )
        
    except Exception as e:
        logger.error(f"Content generation task {task_id} failed: {str(e)}")
        await task_manager.fail_task(task_id, str(e))
        
        await websocket_manager.send_task_update(
            user_id=request.user_id,
            task_id=task_id,
            status="failed",
            error=str(e)
        )


async def execute_trend_analysis(
    task_id: str, 
    request: TrendAnalysisRequest, 
    crew: RealSocialOptimizerCrew
):
    """Execute trend analysis task in background."""
    try:
        await task_manager.update_task_status(task_id, "running")
        
        result = await crew.analyze_trends(
            platforms=request.platforms,
            keywords=request.keywords,
            timeframe=request.timeframe,
            competitor_accounts=request.competitor_accounts
        )
        
        await task_manager.complete_task(task_id, result)
        
        await websocket_manager.send_task_update(
            user_id=request.user_id,
            task_id=task_id,
            status="completed",
            result=result
        )
        
    except Exception as e:
        logger.error(f"Trend analysis task {task_id} failed: {str(e)}")
        await task_manager.fail_task(task_id, str(e))
        
        await websocket_manager.send_task_update(
            user_id=request.user_id,
            task_id=task_id,
            status="failed",
            error=str(e)
        )


async def execute_video_creation(
    task_id: str, 
    request: VideoCreationRequest, 
    crew: RealSocialOptimizerCrew
):
    """Execute video creation task in background."""
    try:
        await task_manager.update_task_status(task_id, "running")
        
        result = await crew.create_video_content(
            topic=request.topic,
            platform=request.platform,
            duration=request.duration,
            style=request.style,
            target_audience=request.target_audience
        )
        
        await task_manager.complete_task(task_id, result)
        
        await websocket_manager.send_task_update(
            user_id=request.user_id,
            task_id=task_id,
            status="completed",
            result=result
        )
        
    except Exception as e:
        logger.error(f"Video creation task {task_id} failed: {str(e)}")
        await task_manager.fail_task(task_id, str(e))
        
        await websocket_manager.send_task_update(
            user_id=request.user_id,
            task_id=task_id,
            status="failed",
            error=str(e)
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "internal_server_error",
            "message": "An internal server error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload and settings.is_development,
        log_level=settings.server.log_level,
        workers=settings.server.workers if not settings.server.reload else 1
    )