"""
Comprehensive test script for CrewAI + FastAPI integration.
Tests all major components and functionality.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any

import httpx
import websockets
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
TEST_USER_ID = "test_user_123"


class TestResult(BaseModel):
    """Test result model."""
    test_name: str
    success: bool
    duration: float
    message: str
    data: Dict[str, Any] = {}


class IntegrationTester:
    """Comprehensive integration tester for the social media optimization platform."""
    
    def __init__(self):
        self.results = []
        self.client = None
        self.websocket = None
    
    async def run_all_tests(self):
        """Run all integration tests."""
        logger.info("Starting comprehensive integration tests...")
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
        
        try:
            # Test basic API endpoints
            await self.test_health_check()
            await self.test_agent_status()
            
            # Test task management
            await self.test_content_generation()
            await self.test_trend_analysis()
            await self.test_video_creation()
            
            # Test WebSocket functionality
            await self.test_websocket_connection()
            await self.test_websocket_subscriptions()
            
            # Test monitoring endpoints
            await self.test_monitoring_endpoints()
            
            # Test real-time notifications
            await self.test_real_time_notifications()
            
        finally:
            await self.client.aclose()
            if self.websocket:
                await self.websocket.close()
        
        # Print test results
        self.print_test_results()
    
    async def test_health_check(self):
        """Test health check endpoint."""
        start_time = time.time()
        
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.results.append(TestResult(
                    test_name="Health Check",
                    success=True,
                    duration=duration,
                    message="Health check passed",
                    data=data
                ))
            else:
                self.results.append(TestResult(
                    test_name="Health Check",
                    success=False,
                    duration=duration,
                    message=f"Health check failed with status {response.status_code}"
                ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="Health Check",
                success=False,
                duration=duration,
                message=f"Health check error: {str(e)}"
            ))
    
    async def test_agent_status(self):
        """Test agent status endpoint."""
        start_time = time.time()
        
        try:
            response = await self.client.get(f"{BASE_URL}/agents/status")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.results.append(TestResult(
                    test_name="Agent Status",
                    success=True,
                    duration=duration,
                    message=f"Retrieved status for {len(data)} agents",
                    data={"agent_count": len(data)}
                ))
            else:
                self.results.append(TestResult(
                    test_name="Agent Status",
                    success=False,
                    duration=duration,
                    message=f"Agent status failed with status {response.status_code}"
                ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="Agent Status",
                success=False,
                duration=duration,
                message=f"Agent status error: {str(e)}"
            ))
    
    async def test_content_generation(self):
        """Test content generation endpoint."""
        start_time = time.time()
        
        try:
            payload = {
                "user_id": TEST_USER_ID,
                "platform": "twitter",
                "topic": "AI and social media optimization",
                "brand_voice": "professional",
                "target_audience": "marketing professionals",
                "content_type": "post"
            }
            
            response = await self.client.post(
                f"{BASE_URL}/agents/content/generate",
                json=payload
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                
                # Wait a bit and check task status
                await asyncio.sleep(2)
                status_response = await self.client.get(f"{BASE_URL}/tasks/{task_id}")
                
                self.results.append(TestResult(
                    test_name="Content Generation",
                    success=True,
                    duration=duration,
                    message=f"Content generation task created: {task_id}",
                    data={"task_id": task_id, "status": status_response.json() if status_response.status_code == 200 else None}
                ))
            else:
                self.results.append(TestResult(
                    test_name="Content Generation",
                    success=False,
                    duration=duration,
                    message=f"Content generation failed with status {response.status_code}"
                ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="Content Generation",
                success=False,
                duration=duration,
                message=f"Content generation error: {str(e)}"
            ))
    
    async def test_trend_analysis(self):
        """Test trend analysis endpoint."""
        start_time = time.time()
        
        try:
            payload = {
                "user_id": TEST_USER_ID,
                "platforms": ["twitter", "linkedin"],
                "keywords": ["AI", "social media", "marketing"],
                "timeframe": "7d"
            }
            
            response = await self.client.post(
                f"{BASE_URL}/agents/trends/analyze",
                json=payload
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                
                self.results.append(TestResult(
                    test_name="Trend Analysis",
                    success=True,
                    duration=duration,
                    message=f"Trend analysis task created: {task_id}",
                    data={"task_id": task_id}
                ))
            else:
                self.results.append(TestResult(
                    test_name="Trend Analysis",
                    success=False,
                    duration=duration,
                    message=f"Trend analysis failed with status {response.status_code}"
                ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="Trend Analysis",
                success=False,
                duration=duration,
                message=f"Trend analysis error: {str(e)}"
            ))
    
    async def test_video_creation(self):
        """Test video creation endpoint."""
        start_time = time.time()
        
        try:
            payload = {
                "user_id": TEST_USER_ID,
                "topic": "Social media marketing tips",
                "platform": "tiktok",
                "duration": 30,
                "style": "educational",
                "target_audience": "small business owners"
            }
            
            response = await self.client.post(
                f"{BASE_URL}/agents/video/create",
                json=payload
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                
                self.results.append(TestResult(
                    test_name="Video Creation",
                    success=True,
                    duration=duration,
                    message=f"Video creation task created: {task_id}",
                    data={"task_id": task_id}
                ))
            else:
                self.results.append(TestResult(
                    test_name="Video Creation",
                    success=False,
                    duration=duration,
                    message=f"Video creation failed with status {response.status_code}"
                ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="Video Creation",
                success=False,
                duration=duration,
                message=f"Video creation error: {str(e)}"
            ))
    
    async def test_websocket_connection(self):
        """Test WebSocket connection."""
        start_time = time.time()
        
        try:
            uri = f"{WS_URL}/ws/connect?user_id={TEST_USER_ID}"
            
            async with websockets.connect(uri) as websocket:
                # Send a ping message
                ping_message = {"type": "ping"}
                await websocket.send(json.dumps(ping_message))
                
                # Wait for pong response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                duration = time.time() - start_time
                
                if response_data.get("type") == "pong":
                    self.results.append(TestResult(
                        test_name="WebSocket Connection",
                        success=True,
                        duration=duration,
                        message="WebSocket connection and ping/pong successful",
                        data=response_data
                    ))
                else:
                    self.results.append(TestResult(
                        test_name="WebSocket Connection",
                        success=False,
                        duration=duration,
                        message=f"Unexpected WebSocket response: {response_data}"
                    ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="WebSocket Connection",
                success=False,
                duration=duration,
                message=f"WebSocket connection error: {str(e)}"
            ))
    
    async def test_websocket_subscriptions(self):
        """Test WebSocket subscriptions."""
        start_time = time.time()
        
        try:
            uri = f"{WS_URL}/ws/connect?user_id={TEST_USER_ID}"
            
            async with websockets.connect(uri) as websocket:
                # Subscribe to agent updates
                subscribe_message = {
                    "type": "subscribe",
                    "subscription": "agent_content_writer"
                }
                await websocket.send(json.dumps(subscribe_message))
                
                # Wait for subscription confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                duration = time.time() - start_time
                
                if response_data.get("type") == "subscription_confirmed":
                    self.results.append(TestResult(
                        test_name="WebSocket Subscriptions",
                        success=True,
                        duration=duration,
                        message="WebSocket subscription successful",
                        data=response_data
                    ))
                else:
                    self.results.append(TestResult(
                        test_name="WebSocket Subscriptions",
                        success=False,
                        duration=duration,
                        message=f"Subscription failed: {response_data}"
                    ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="WebSocket Subscriptions",
                success=False,
                duration=duration,
                message=f"WebSocket subscription error: {str(e)}"
            ))
    
    async def test_monitoring_endpoints(self):
        """Test monitoring endpoints."""
        start_time = time.time()
        
        try:
            # Test monitoring health
            response = await self.client.get(f"{BASE_URL}/monitoring/health")
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Test metrics endpoint
                metrics_response = await self.client.get(f"{BASE_URL}/monitoring/metrics")
                
                # Test dashboard endpoint
                dashboard_response = await self.client.get(f"{BASE_URL}/monitoring/dashboard")
                
                duration = time.time() - start_time
                
                success = all([
                    response.status_code == 200,
                    metrics_response.status_code == 200,
                    dashboard_response.status_code == 200
                ])
                
                self.results.append(TestResult(
                    test_name="Monitoring Endpoints",
                    success=success,
                    duration=duration,
                    message="Monitoring endpoints tested successfully",
                    data={
                        "health_status": health_data.get("status"),
                        "endpoints_tested": 3
                    }
                ))
            else:
                duration = time.time() - start_time
                self.results.append(TestResult(
                    test_name="Monitoring Endpoints",
                    success=False,
                    duration=duration,
                    message=f"Monitoring health check failed with status {response.status_code}"
                ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="Monitoring Endpoints",
                success=False,
                duration=duration,
                message=f"Monitoring endpoints error: {str(e)}"
            ))
    
    async def test_real_time_notifications(self):
        """Test real-time notifications via WebSocket."""
        start_time = time.time()
        
        try:
            # Send a test notification via HTTP API
            notification_payload = {
                "notification_type": "test",
                "title": "Test Notification",
                "message": "This is a test notification",
                "user_id": TEST_USER_ID
            }
            
            # First, establish WebSocket connection
            uri = f"{WS_URL}/ws/connect?user_id={TEST_USER_ID}"
            
            async with websockets.connect(uri) as websocket:
                # Send the notification via HTTP
                response = await self.client.post(
                    f"{BASE_URL}/ws/notify/system",
                    json=notification_payload
                )
                
                if response.status_code == 200:
                    # Wait for the notification to arrive via WebSocket
                    try:
                        notification = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        notification_data = json.loads(notification)
                        
                        duration = time.time() - start_time
                        
                        if notification_data.get("type") == "system_notification":
                            self.results.append(TestResult(
                                test_name="Real-time Notifications",
                                success=True,
                                duration=duration,
                                message="Real-time notification received successfully",
                                data=notification_data
                            ))
                        else:
                            self.results.append(TestResult(
                                test_name="Real-time Notifications",
                                success=False,
                                duration=duration,
                                message=f"Unexpected notification type: {notification_data.get('type')}"
                            ))
                    
                    except asyncio.TimeoutError:
                        duration = time.time() - start_time
                        self.results.append(TestResult(
                            test_name="Real-time Notifications",
                            success=False,
                            duration=duration,
                            message="Notification not received within timeout"
                        ))
                else:
                    duration = time.time() - start_time
                    self.results.append(TestResult(
                        test_name="Real-time Notifications",
                        success=False,
                        duration=duration,
                        message=f"Failed to send notification: {response.status_code}"
                    ))
        
        except Exception as e:
            duration = time.time() - start_time
            self.results.append(TestResult(
                test_name="Real-time Notifications",
                success=False,
                duration=duration,
                message=f"Real-time notification error: {str(e)}"
            ))
    
    def print_test_results(self):
        """Print comprehensive test results."""
        print("\n" + "="*80)
        print("CREWAI + FASTAPI INTEGRATION TEST RESULTS")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - passed_tests
        
        print(f"\nSUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\nDETAILED RESULTS:")
        print("-"*80)
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{status} | {result.test_name:<25} | {result.duration:.3f}s | {result.message}")
            
            if result.data and result.success:
                print(f"     Data: {json.dumps(result.data, indent=6)}")
        
        print("\n" + "="*80)
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! The CrewAI + FastAPI integration is working correctly.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Please check the implementation.")
        
        print("="*80)


async def main():
    """Main test function."""
    print("Starting CrewAI + FastAPI Integration Tests...")
    print("Make sure the server is running on http://localhost:8000")
    print("Waiting 3 seconds before starting tests...\n")
    
    await asyncio.sleep(3)
    
    tester = IntegrationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

