"""
Task Manager for handling background tasks and job processing
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskManager:
    """Manages background tasks and job processing."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.task_prefix = "task:"
        self.user_tasks_prefix = "user_tasks:"
        self.active_tasks_prefix = "active_tasks"
        self.task_queue_prefix = "task_queue:"
        self.initialized = False
    
    async def initialize(self, redis_client: redis.Redis):
        """Initialize the task manager with Redis client."""
        
        try:
            self.redis_client = redis_client
            
            # Test Redis connection
            await self.redis_client.ping()
            
            self.initialized = True
            logger.info("Task Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Task Manager: {str(e)}")
            raise
    
    async def create_task(
        self,
        task_type: str,
        user_id: str,
        parameters: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        max_retries: int = 3,
        timeout_seconds: int = 300
    ) -> str:
        """Create a new task."""
        
        if not self.initialized:
            raise RuntimeError("Task Manager not initialized")
        
        task_id = str(uuid.uuid4())
        
        task_data = {
            "task_id": task_id,
            "task_type": task_type,
            "user_id": user_id,
            "parameters": parameters,
            "status": TaskStatus.PENDING.value,
            "priority": priority.value,
            "max_retries": max_retries,
            "retry_count": 0,
            "timeout_seconds": timeout_seconds,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "progress": 0
        }
        
        try:
            # Store task data
            await self.redis_client.set(
                f"{self.task_prefix}{task_id}",
                json.dumps(task_data),
                ex=86400  # Expire in 24 hours
            )
            
            # Add to user's task list
            await self.redis_client.sadd(f"{self.user_tasks_prefix}{user_id}", task_id)
            
            # Add to active tasks
            await self.redis_client.sadd(self.active_tasks_prefix, task_id)
            
            # Add to priority queue
            queue_name = f"{self.task_queue_prefix}{priority.name.lower()}"
            await self.redis_client.lpush(queue_name, task_id)
            
            logger.info(f"Task created: {task_id} for user {user_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and details."""
        
        if not self.initialized:
            raise RuntimeError("Task Manager not initialized")
        
        try:
            task_data = await self.redis_client.get(f"{self.task_prefix}{task_id}")
            
            if not task_data:
                return None
            
            return json.loads(task_data)
            
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {str(e)}")
            return None
    
    async def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: Optional[int] = None,
        error: Optional[str] = None,
        result: Optional[Any] = None
    ):
        """Update task status and details."""
        
        if not self.initialized:
            raise RuntimeError("Task Manager not initialized")
        
        try:
            # Get current task data
            current_data = await self.get_task_status(task_id)
            if not current_data:
                logger.warning(f"Task {task_id} not found for status update")
                return
            
            # Update task data
            current_data["status"] = status
            current_data["updated_at"] = datetime.now().isoformat()
            
            if progress is not None:
                current_data["progress"] = progress
            
            if error is not None:
                current_data["error"] = error
            
            if result is not None:
                current_data["result"] = result
            
            if status == TaskStatus.RUNNING.value and not current_data.get("started_at"):
                current_data["started_at"] = datetime.now().isoformat()
            
            if status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                current_data["completed_at"] = datetime.now().isoformat()
                
                # Remove from active tasks
                await self.redis_client.srem(self.active_tasks_prefix, task_id)
            
            # Save updated data
            await self.redis_client.set(
                f"{self.task_prefix}{task_id}",
                json.dumps(current_data),
                ex=86400
            )
            
            logger.info(f"Task {task_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update task status for {task_id}: {str(e)}")
            raise
    
    async def complete_task(self, task_id: str, result: Any):
        """Mark task as completed with result."""
        
        await self.update_task_status(
            task_id,
            TaskStatus.COMPLETED.value,
            progress=100,
            result=result
        )
    
    async def fail_task(self, task_id: str, error: str):
        """Mark task as failed with error."""
        
        await self.update_task_status(
            task_id,
            TaskStatus.FAILED.value,
            error=error
        )
    
    async def cancel_task(self, task_id: str, reason: str = "Cancelled by user"):
        """Cancel a task."""
        
        await self.update_task_status(
            task_id,
            TaskStatus.CANCELLED.value,
            error=reason
        )
    
    async def retry_task(self, task_id: str) -> bool:
        """Retry a failed task."""
        
        if not self.initialized:
            raise RuntimeError("Task Manager not initialized")
        
        try:
            task_data = await self.get_task_status(task_id)
            if not task_data:
                logger.warning(f"Task {task_id} not found for retry")
                return False
            
            if task_data["retry_count"] >= task_data["max_retries"]:
                logger.warning(f"Task {task_id} has exceeded max retries")
                return False
            
            # Increment retry count and reset status
            task_data["retry_count"] += 1
            task_data["status"] = TaskStatus.PENDING.value
            task_data["updated_at"] = datetime.now().isoformat()
            task_data["started_at"] = None
            task_data["completed_at"] = None
            task_data["error"] = None
            task_data["progress"] = 0
            
            # Save updated data
            await self.redis_client.set(
                f"{self.task_prefix}{task_id}",
                json.dumps(task_data),
                ex=86400
            )
            
            # Add back to active tasks
            await self.redis_client.sadd(self.active_tasks_prefix, task_id)
            
            # Add back to queue
            priority = TaskPriority(task_data["priority"])
            queue_name = f"{self.task_queue_prefix}{priority.name.lower()}"
            await self.redis_client.lpush(queue_name, task_id)
            
            logger.info(f"Task {task_id} queued for retry (attempt {task_data['retry_count']})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry task {task_id}: {str(e)}")
            return False
    
    async def get_user_tasks(
        self,
        user_id: str,
        limit: int = 10,
        status_filter: Optional[str] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get tasks for a specific user."""
        
        if not self.initialized:
            raise RuntimeError("Task Manager not initialized")
        
        try:
            # Get user's task IDs
            task_ids = await self.redis_client.smembers(f"{self.user_tasks_prefix}{user_id}")
            
            if not task_ids:
                return []
            
            # Get task data for each ID
            tasks = []
            
            for task_id in task_ids:
                task_data = await self.get_task_status(task_id.decode())
                
                if task_data:
                    # Apply status filter if specified
                    if status_filter and task_data["status"] != status_filter:
                        continue
                    
                    tasks.append(task_data)
            
            # Sort by created_at (most recent first)
            tasks.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply pagination
            start = offset
            end = offset + limit
            
            return tasks[start:end]
            
        except Exception as e:
            logger.error(f"Failed to get user tasks for {user_id}: {str(e)}")
            return []
    
    async def get_active_tasks_count(self) -> int:
        """Get count of active tasks."""
        
        if not self.initialized:
            return 0
        
        try:
            return await self.redis_client.scard(self.active_tasks_prefix)
            
        except Exception as e:
            logger.error(f"Failed to get active tasks count: {str(e)}")
            return 0
    
    async def get_task_queue_length(self, priority: TaskPriority) -> int:
        """Get length of task queue for specific priority."""
        
        if not self.initialized:
            return 0
        
        try:
            queue_name = f"{self.task_queue_prefix}{priority.name.lower()}"
            return await self.redis_client.llen(queue_name)
            
        except Exception as e:
            logger.error(f"Failed to get queue length for {priority.name}: {str(e)}")
            return 0
    
    async def get_next_task(self, priority: TaskPriority) -> Optional[str]:
        """Get next task from priority queue."""
        
        if not self.initialized:
            return None
        
        try:
            queue_name = f"{self.task_queue_prefix}{priority.name.lower()}"
            task_id = await self.redis_client.rpop(queue_name)
            
            if task_id:
                return task_id.decode()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get next task from {priority.name} queue: {str(e)}")
            return None
    
    async def get_all_queue_lengths(self) -> Dict[str, int]:
        """Get lengths of all priority queues."""
        
        if not self.initialized:
            return {}
        
        queue_lengths = {}
        
        for priority in TaskPriority:
            try:
                queue_name = f"{self.task_queue_prefix}{priority.name.lower()}"
                length = await self.redis_client.llen(queue_name)
                queue_lengths[priority.name.lower()] = length
                
            except Exception as e:
                logger.error(f"Failed to get queue length for {priority.name}: {str(e)}")
                queue_lengths[priority.name.lower()] = 0
        
        return queue_lengths
    
    async def cleanup_expired_tasks(self, max_age_hours: int = 24):
        """Clean up expired tasks."""
        
        if not self.initialized:
            return 0
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cutoff_timestamp = cutoff_time.isoformat()
            
            # Get all task keys
            pattern = f"{self.task_prefix}*"
            task_keys = []
            
            async for key in self.redis_client.scan_iter(match=pattern):
                task_keys.append(key)
            
            cleaned_count = 0
            
            for key in task_keys:
                try:
                    task_data = await self.redis_client.get(key)
                    if task_data:
                        task_info = json.loads(task_data)
                        
                        # Check if task is old enough to clean up
                        if task_info.get("created_at", "") < cutoff_timestamp:
                            task_id = task_info.get("task_id")
                            user_id = task_info.get("user_id")
                            
                            # Remove task data
                            await self.redis_client.delete(key)
                            
                            # Remove from user's task list
                            if user_id:
                                await self.redis_client.srem(f"{self.user_tasks_prefix}{user_id}", task_id)
                            
                            # Remove from active tasks
                            await self.redis_client.srem(self.active_tasks_prefix, task_id)
                            
                            cleaned_count += 1
                            
                except Exception as e:
                    logger.error(f"Error cleaning up task {key}: {str(e)}")
            
            logger.info(f"Cleaned up {cleaned_count} expired tasks")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired tasks: {str(e)}")
            return 0
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get comprehensive task statistics."""
        
        if not self.initialized:
            return {}
        
        try:
            stats = {
                "active_tasks": await self.get_active_tasks_count(),
                "queue_lengths": await self.get_all_queue_lengths(),
                "status_counts": {status.value: 0 for status in TaskStatus},
                "task_types": {},
                "average_completion_time": None,
                "success_rate": 0.0
            }
            
            # Count tasks by status and type
            pattern = f"{self.task_prefix}*"
            total_tasks = 0
            completed_tasks = 0
            failed_tasks = 0
            completion_times = []
            
            async for key in self.redis_client.scan_iter(match=pattern):
                try:
                    task_data = await self.redis_client.get(key)
                    if task_data:
                        task_info = json.loads(task_data)
                        total_tasks += 1
                        
                        # Count by status
                        status = task_info.get("status", "unknown")
                        if status in stats["status_counts"]:
                            stats["status_counts"][status] += 1
                        
                        # Count by task type
                        task_type = task_info.get("task_type", "unknown")
                        stats["task_types"][task_type] = stats["task_types"].get(task_type, 0) + 1
                        
                        # Calculate completion times
                        if status == TaskStatus.COMPLETED.value:
                            completed_tasks += 1
                            started_at = task_info.get("started_at")
                            completed_at = task_info.get("completed_at")
                            
                            if started_at and completed_at:
                                start_time = datetime.fromisoformat(started_at)
                                end_time = datetime.fromisoformat(completed_at)
                                completion_time = (end_time - start_time).total_seconds()
                                completion_times.append(completion_time)
                        
                        elif status == TaskStatus.FAILED.value:
                            failed_tasks += 1
                
                except Exception as e:
                    logger.error(f"Error processing task statistics for {key}: {str(e)}")
            
            # Calculate averages
            if completion_times:
                stats["average_completion_time"] = sum(completion_times) / len(completion_times)
            
            if total_tasks > 0:
                stats["success_rate"] = (completed_tasks / total_tasks) * 100
            
            stats["total_tasks"] = total_tasks
            stats["completed_tasks"] = completed_tasks
            stats["failed_tasks"] = failed_tasks
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get task statistics: {str(e)}")
            return {}