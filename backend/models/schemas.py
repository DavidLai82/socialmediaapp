"""
Pydantic schemas for API request/response validation
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


# Enums
class PlatformType(str, Enum):
    """Social media platform types."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


class ContentType(str, Enum):
    """Content types for generation."""
    POST = "post"
    THREAD = "thread"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"
    CAROUSEL = "carousel"
    ARTICLE = "article"


class TaskStatusType(str, Enum):
    """Task status types."""
    PENDING = "pending"
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatusType(str, Enum):
    """Agent status types."""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    INITIALIZING = "initializing"
    OFFLINE = "offline"


# Base schemas
class BaseRequest(BaseModel):
    """Base request schema with common fields."""
    user_id: str = Field(..., description="Unique user identifier")
    
    class Config:
        use_enum_values = True


class BaseResponse(BaseModel):
    """Base response schema with common fields."""
    success: bool = Field(default=True, description="Indicates if request was successful")
    message: Optional[str] = Field(None, description="Optional message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        use_enum_values = True


# Agent Task Schemas
class AgentTaskRequest(BaseRequest):
    """Base schema for agent task requests."""
    priority: Optional[int] = Field(2, ge=1, le=4, description="Task priority (1=low, 4=critical)")
    timeout: Optional[int] = Field(300, ge=30, le=3600, description="Task timeout in seconds")


class AgentTaskResponse(BaseResponse):
    """Response schema for agent task creation."""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatusType = Field(..., description="Current task status")
    agent: str = Field(..., description="Agent handling the task")
    estimated_completion: Optional[int] = Field(None, description="Estimated completion time in seconds")


# Content Generation Schemas
class ContentGenerationRequest(AgentTaskRequest):
    """Request schema for content generation."""
    platform: PlatformType = Field(..., description="Target social media platform")
    topic: str = Field(..., min_length=3, max_length=200, description="Content topic or theme")
    brand_voice: str = Field(..., min_length=3, max_length=100, description="Brand voice and tone")
    target_audience: str = Field(..., min_length=3, max_length=200, description="Target audience description")
    content_type: ContentType = Field(ContentType.POST, description="Type of content to generate")
    additional_context: Optional[str] = Field(None, max_length=500, description="Additional context or requirements")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    hashtags: Optional[List[str]] = Field(None, description="Specific hashtags to use")
    call_to_action: Optional[str] = Field(None, max_length=100, description="Specific call-to-action")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v and len(v) > 20:
            raise ValueError('Maximum 20 keywords allowed')
        return v
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        if v and len(v) > 30:
            raise ValueError('Maximum 30 hashtags allowed')
        return v


class ContentGenerationResponse(BaseResponse):
    """Response schema for content generation results."""
    content: Dict[str, Any] = Field(..., description="Generated content data")
    platform: PlatformType = Field(..., description="Target platform")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# Trend Analysis Schemas
class TrendAnalysisRequest(AgentTaskRequest):
    """Request schema for trend analysis."""
    platforms: List[PlatformType] = Field(..., min_items=1, description="Platforms to analyze")
    keywords: List[str] = Field(..., min_items=1, max_items=50, description="Keywords to track")
    timeframe: str = Field("24h", description="Analysis timeframe (1h, 24h, 7d, 30d)")
    competitor_accounts: Optional[List[str]] = Field(None, description="Competitor accounts to analyze")
    include_sentiment: bool = Field(False, description="Include sentiment analysis")
    geographic_region: Optional[str] = Field(None, description="Geographic region filter")
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = ['1h', '24h', '7d', '30d']
        if v not in valid_timeframes:
            raise ValueError(f'Timeframe must be one of {valid_timeframes}')
        return v
    
    @validator('competitor_accounts')
    def validate_competitor_accounts(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 competitor accounts allowed')
        return v


class TrendAnalysisResponse(BaseResponse):
    """Response schema for trend analysis results."""
    trends: Dict[str, Any] = Field(..., description="Trend analysis data")
    platforms: List[PlatformType] = Field(..., description="Analyzed platforms")
    timeframe: str = Field(..., description="Analysis timeframe")
    insights: Optional[List[str]] = Field(None, description="Key insights from analysis")


# Video Creation Schemas
class VideoCreationRequest(AgentTaskRequest):
    """Request schema for video content creation."""
    topic: str = Field(..., min_length=3, max_length=200, description="Video topic or theme")
    platform: PlatformType = Field(..., description="Target platform for video")
    duration: str = Field(..., description="Target video duration (e.g., '30s', '2min')")
    style: str = Field(..., description="Video style (e.g., 'professional', 'casual', 'energetic')")
    target_audience: str = Field(..., min_length=3, max_length=200, description="Target audience")
    video_type: str = Field("educational", description="Type of video content")
    include_script: bool = Field(True, description="Include script generation")
    include_shot_list: bool = Field(True, description="Include shot list")
    brand_colors: Optional[List[str]] = Field(None, description="Brand colors to use")
    music_style: Optional[str] = Field(None, description="Preferred music style")
    
    @validator('brand_colors')
    def validate_brand_colors(cls, v):
        if v and len(v) > 5:
            raise ValueError('Maximum 5 brand colors allowed')
        return v


class VideoCreationResponse(BaseResponse):
    """Response schema for video creation results."""
    video_plan: Dict[str, Any] = Field(..., description="Complete video production plan")
    script: Optional[Dict[str, Any]] = Field(None, description="Generated script")
    shot_list: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed shot list")
    production_notes: Optional[Dict[str, Any]] = Field(None, description="Production guidelines")


# Agent Status Schemas
class AgentStatus(BaseModel):
    """Schema for individual agent status."""
    name: str = Field(..., description="Agent name")
    status: AgentStatusType = Field(..., description="Current agent status")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    active_tasks: int = Field(0, ge=0, description="Number of active tasks")
    completed_tasks: int = Field(0, ge=0, description="Number of completed tasks")
    error_count: int = Field(0, ge=0, description="Number of recent errors")
    uptime_seconds: Optional[int] = Field(None, description="Agent uptime in seconds")
    
    class Config:
        use_enum_values = True


class AgentSystemStatus(BaseResponse):
    """Schema for overall agent system status."""
    agents: Dict[str, AgentStatus] = Field(..., description="Status of all agents")
    total_agents: int = Field(..., ge=0, description="Total number of agents")
    active_agents: int = Field(..., ge=0, description="Number of active agents")
    system_health: str = Field(..., description="Overall system health")


# Task Management Schemas
class TaskInfo(BaseModel):
    """Schema for task information."""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task")
    user_id: str = Field(..., description="User who created the task")
    status: TaskStatusType = Field(..., description="Current task status")
    progress: int = Field(0, ge=0, le=100, description="Task completion percentage")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error: Optional[str] = Field(None, description="Error message if task failed")
    retry_count: int = Field(0, ge=0, description="Number of retry attempts")
    
    class Config:
        use_enum_values = True


class TaskListResponse(BaseResponse):
    """Response schema for task list requests."""
    tasks: List[TaskInfo] = Field(..., description="List of tasks")
    total_count: int = Field(..., ge=0, description="Total number of tasks")
    page: int = Field(1, ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")


# Analytics and Monitoring Schemas
class SystemMetrics(BaseModel):
    """Schema for system performance metrics."""
    timestamp: datetime = Field(..., description="Metrics timestamp")
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    active_connections: int = Field(..., ge=0, description="Number of active connections")
    active_tasks: int = Field(..., ge=0, description="Number of active tasks")
    request_rate: float = Field(..., ge=0, description="Requests per second")
    error_rate: float = Field(..., ge=0, description="Error rate percentage")


class PerformanceMetrics(BaseModel):
    """Schema for performance analytics."""
    time_period: str = Field(..., description="Time period for metrics")
    avg_response_time: float = Field(..., ge=0, description="Average response time in milliseconds")
    max_response_time: float = Field(..., ge=0, description="Maximum response time in milliseconds")
    min_response_time: float = Field(..., ge=0, description="Minimum response time in milliseconds")
    total_requests: int = Field(..., ge=0, description="Total number of requests")
    successful_requests: int = Field(..., ge=0, description="Number of successful requests")
    failed_requests: int = Field(..., ge=0, description="Number of failed requests")
    throughput: float = Field(..., ge=0, description="Requests per second")


# WebSocket Message Schemas
class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    data: Optional[Dict[str, Any]] = Field(None, description="Message data")
    
    class Config:
        use_enum_values = True


class TaskUpdateMessage(WebSocketMessage):
    """Schema for task update WebSocket messages."""
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatusType = Field(..., description="Task status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Task progress percentage")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")


class AgentStatusMessage(WebSocketMessage):
    """Schema for agent status WebSocket messages."""
    agent_name: str = Field(..., description="Agent name")
    status: AgentStatusType = Field(..., description="Agent status")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional status details")


# Configuration Schemas
class APIConfig(BaseModel):
    """Schema for API configuration."""
    title: str = Field(default="Social Media AI Platform", description="API title")
    version: str = Field(default="1.0.0", description="API version")
    debug: bool = Field(default=False, description="Debug mode")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    max_request_size: int = Field(default=10485760, description="Maximum request size in bytes")
    rate_limit: int = Field(default=100, description="Rate limit per minute")


class DatabaseConfig(BaseModel):
    """Schema for database configuration."""
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    pool_size: int = Field(default=10, ge=1, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, description="Maximum connection overflow")


class RedisConfig(BaseModel):
    """Schema for Redis configuration."""
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    database: int = Field(default=0, ge=0, le=15, description="Redis database number")
    password: Optional[str] = Field(None, description="Redis password")
    max_connections: int = Field(default=10, ge=1, description="Maximum connections")


# Error Response Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")


class ValidationError(BaseModel):
    """Schema for validation error details."""
    field: str = Field(..., description="Field name with validation error")
    message: str = Field(..., description="Validation error message")
    value: Any = Field(None, description="Invalid value that caused the error")


class ValidationErrorResponse(ErrorResponse):
    """Schema for validation error responses."""
    error: str = Field(default="validation_error", description="Error type")
    validation_errors: List[ValidationError] = Field(..., description="List of validation errors")


# Pagination Schemas
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("desc", regex="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseResponse):
    """Base schema for paginated responses."""
    total_count: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")