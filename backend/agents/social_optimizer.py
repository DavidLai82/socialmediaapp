"""
Social Media Optimization Agent - Main Coordinator
Multi-agent system for social media content optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from crewai import Agent, Crew, Task, Process
from crewai.tools import BaseTool
import os
from dotenv import load_dotenv

from ..utils.task_manager import TaskManager
from .content_tools import ContentGenerationTool
from .social_media_tools import SocialMediaAnalysisTool
from .video_tools import VideoCreationTool

load_dotenv()
logger = logging.getLogger(__name__)


class SocialOptimizerCrew:
    """Main coordinator for the social media optimization multi-agent system."""
    
    def __init__(self):
        self.crew = None
        self.agents = {}
        self.tools = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the crew and all agents."""
        try:
            # Initialize tools
            self.tools = {
                'content_generation': ContentGenerationTool(),
                'social_media_analysis': SocialMediaAnalysisTool(),
                'video_creation': VideoCreationTool()
            }
            
            # Create agents
            await self._create_agents()
            
            # Create crew
            self.crew = Crew(
                agents=list(self.agents.values()),
                process=Process.hierarchical,
                verbose=True,
                manager_llm="gpt-4"
            )
            
            self.initialized = True
            logger.info("Social Media Optimization Crew initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize crew: {str(e)}")
            raise
    
    async def _create_agents(self):
        """Create and configure all agents."""
        
        # Main Social Optimization Agent
        self.agents['social_optimizer'] = Agent(
            role='Social Media Strategy Coordinator',
            goal='Coordinate all social media optimization activities and ensure cohesive strategy execution',
            backstory="""You are the lead social media strategist responsible for coordinating 
            all social media optimization efforts. You understand brand voice, audience targeting, 
            and platform-specific best practices. You delegate tasks to specialized agents and 
            ensure all activities align with the overall social media strategy.""",
            tools=list(self.tools.values()),
            verbose=True,
            allow_delegation=True,
            max_iter=3
        )
        
        # Traffic Analysis Agent
        self.agents['traffic_analyst'] = Agent(
            role='Social Media Traffic Analyst',
            goal='Analyze social media trends, competitor activities, and predict viral content opportunities',
            backstory="""You are an expert in social media analytics and trend prediction. 
            You continuously monitor social media platforms for emerging trends, analyze 
            competitor strategies, and identify opportunities for viral content. Your insights 
            drive content strategy and timing decisions.""",
            tools=[self.tools['social_media_analysis']],
            verbose=True,
            max_iter=3
        )
        
        # Content Writing Agent
        self.agents['content_writer'] = Agent(
            role='Social Media Content Writer',
            goal='Create engaging, platform-optimized content that aligns with trends and brand voice',
            backstory="""You are a skilled social media content creator who understands 
            the nuances of different platforms. You create compelling posts, captions, and 
            copy that resonate with target audiences while maintaining brand consistency. 
            You optimize content for engagement and shareability.""",
            tools=[self.tools['content_generation']],
            verbose=True,
            max_iter=3
        )
        
        # Video Creation Agent
        self.agents['video_creator'] = Agent(
            role='Video Content Planner',
            goal='Plan and structure video content for maximum engagement across platforms',
            backstory="""You are a video content strategist who understands visual storytelling 
            and platform-specific video requirements. You create detailed video concepts, 
            shot lists, and production guidelines. You work closely with the script writer 
            to ensure cohesive video narratives.""",
            tools=[self.tools['video_creation']],
            verbose=True,
            allow_delegation=True,
            max_iter=3
        )
        
        # Script Writing Agent
        self.agents['script_writer'] = Agent(
            role='Video Script Writer',
            goal='Write compelling video scripts with strong hooks and clear narratives',
            backstory="""You are a specialized script writer focused on creating engaging 
            video scripts for social media. You understand the importance of strong opening 
            hooks, clear messaging, and platform-specific script requirements. You work 
            under the video creation agent to bring video concepts to life.""",
            tools=[self.tools['content_generation']],
            verbose=True,
            max_iter=3
        )
    
    async def generate_content(
        self, 
        platform: str, 
        topic: str, 
        brand_voice: str,
        target_audience: str,
        content_type: str = "post"
    ) -> Dict[str, Any]:
        """Generate social media content using the multi-agent system."""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create task for content generation
            task = Task(
                description=f"""
                Create engaging {content_type} content for {platform} about {topic}.
                
                Requirements:
                - Platform: {platform}
                - Topic: {topic}
                - Brand Voice: {brand_voice}
                - Target Audience: {target_audience}
                - Content Type: {content_type}
                
                Steps:
                1. Analyze current trends related to the topic
                2. Create platform-optimized content
                3. Include relevant hashtags and engagement elements
                4. Ensure brand voice consistency
                5. Optimize for the target audience
                
                Deliver the final content with engagement recommendations.
                """,
                agent=self.agents['social_optimizer'],
                expected_output="Complete social media content with captions, hashtags, and engagement strategy"
            )
            
            # Execute task
            result = await asyncio.to_thread(self.crew.kickoff, {"tasks": [task]})
            
            return {
                "content": result,
                "platform": platform,
                "topic": topic,
                "brand_voice": brand_voice,
                "target_audience": target_audience,
                "content_type": content_type,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def analyze_trends(
        self,
        platforms: List[str],
        keywords: List[str],
        timeframe: str = "24h",
        competitor_accounts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze social media trends and opportunities."""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            task = Task(
                description=f"""
                Analyze social media trends and opportunities.
                
                Requirements:
                - Platforms: {', '.join(platforms)}
                - Keywords: {', '.join(keywords)}
                - Timeframe: {timeframe}
                - Competitor Accounts: {competitor_accounts or 'None specified'}
                
                Steps:
                1. Monitor trending topics on specified platforms
                2. Analyze keyword performance and engagement
                3. Identify viral content patterns
                4. Analyze competitor performance (if provided)
                5. Predict upcoming trend opportunities
                6. Provide actionable recommendations
                
                Deliver comprehensive trend analysis with recommendations.
                """,
                agent=self.agents['traffic_analyst'],
                expected_output="Detailed trend analysis with actionable insights and recommendations"
            )
            
            result = await asyncio.to_thread(self.crew.kickoff, {"tasks": [task]})
            
            return {
                "trends": result,
                "platforms": platforms,
                "keywords": keywords,
                "timeframe": timeframe,
                "competitor_accounts": competitor_accounts,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def create_video_content(
        self,
        topic: str,
        platform: str,
        duration: str,
        style: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """Create video content plan with script."""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            task = Task(
                description=f"""
                Create comprehensive video content plan and script.
                
                Requirements:
                - Topic: {topic}
                - Platform: {platform}
                - Duration: {duration}
                - Style: {style}
                - Target Audience: {target_audience}
                
                Steps:
                1. Develop video concept and structure
                2. Create detailed shot list and visual plan
                3. Write engaging script with strong hook
                4. Plan platform-specific optimizations
                5. Include engagement and CTA recommendations
                
                Coordinate with script writer for compelling narrative.
                """,
                agent=self.agents['video_creator'],
                expected_output="Complete video content plan with script, shot list, and production guidelines"
            )
            
            result = await asyncio.to_thread(self.crew.kickoff, {"tasks": [task]})
            
            return {
                "video_plan": result,
                "topic": topic,
                "platform": platform,
                "duration": duration,
                "style": style,
                "target_audience": target_audience,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Video creation failed: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def get_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents."""
        
        status = {}
        
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                "name": agent_name,
                "role": getattr(agent, 'role', 'Unknown'),
                "status": "active" if self.initialized else "initializing",
                "tools": len(getattr(agent, 'tools', [])),
                "max_iterations": getattr(agent, 'max_iter', 0)
            }
        
        return status