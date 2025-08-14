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

from agents.social_optimizer import SocialOptimizerCrew
from models.schemas import (
    AgentTaskRequest, 
    AgentTaskResponse, 
    ContentGenerationRequest,
    TrendAnalysisRequest,
    VideoCreationRequest,
    AgentStatus,
    ErrorResponse
)
from utils.websocket_manager import WebSocketManager
from utils.task_manager import TaskManager
from config.settings import settings, validate_required_settings, setup_logging, print_startup_info

# Import API routes
from api.websocket_routes import websocket_router
from api.monitoring_routes import monitoring_router

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Global instances
redis_client: Optional[redis.Redis] = None
websocket_manager: WebSocketManager = WebSocketManager()
task_manager: TaskManager = TaskManager()
social_crew: Optional[SocialOptimizerCrew] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global redis_client, social_crew
    
    # Startup
    logger.info("Starting Social Media Optimization Platform...")
    
    try:
        # Validate configuration
        validate_required_settings()
        
        # Print startup information
        print_startup_info()
        
        # Initialize Redis connection
        redis_client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            password=settings.redis.password,
            max_connections=settings.redis.max_connections,
            decode_responses=True
        )
        
        # Test Redis connection
        await redis_client.ping()
        logger.info("Redis connection established")
        
        # Initialize task manager with Redis
        await task_manager.initialize(redis_client)
        logger.info("Task manager initialized")
        
        # Initialize CrewAI social optimization crew
        if settings.ai_services.openai_api_key or settings.ai_services.anthropic_api_key:
            social_crew = SocialOptimizerCrew()
            await social_crew.initialize()
            logger.info("Social optimization crew initialized")
        else:
            logger.warning("No AI service API keys configured - crew initialization skipped")
        
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
async def get_social_crew() -> SocialOptimizerCrew:
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
async def health_check(redis: redis.Redis = Depends(get_redis)):
    """Health check endpoint."""
    try:
        # Check Redis connection
        redis_status = "healthy"
        try:
            await redis.ping()
        except Exception as e:
            redis_status = f"unhealthy: {str(e)}"
        
        # Check agents status
        agents_status = {}
        if social_crew and social_crew.initialized:
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
        if redis_status != "healthy":
            overall_status = "degraded"
        if not social_crew or not social_crew.initialized:
            overall_status = "degraded" if overall_status == "healthy" else "critical"
        
        return {
            "status": overall_status,
            "timestamp": "now",  # Will be replaced with actual timestamp in production
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
    if not social_crew or not social_crew.initialized:
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
    crew: SocialOptimizerCrew = Depends(get_social_crew)
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
    crew: SocialOptimizerCrew = Depends(get_social_crew)
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
    crew: SocialOptimizerCrew = Depends(get_social_crew)
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
    crew: SocialOptimizerCrew
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
    crew: SocialOptimizerCrew
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
    crew: SocialOptimizerCrew
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