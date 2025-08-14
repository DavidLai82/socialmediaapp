"""
Content Generation Tools for Social Media AI Agents
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from crewai.tools import BaseTool
import openai
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ContentGenerationTool(BaseTool):
    """Tool for generating social media content using AI models."""
    
    name: str = "content_generation_tool"
    description: str = "Generate engaging social media content optimized for specific platforms and audiences"
    
    def __init__(self):
        super().__init__()
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI service clients."""
        try:
            if os.getenv('OPENAI_API_KEY'):
                self.openai_client = openai.OpenAI(
                    api_key=os.getenv('OPENAI_API_KEY')
                )
            
            if os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = anthropic.Anthropic(
                    api_key=os.getenv('ANTHROPIC_API_KEY')
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {str(e)}")
    
    def _run(
        self, 
        platform: str,
        content_type: str,
        topic: str,
        brand_voice: str,
        target_audience: str,
        additional_context: str = ""
    ) -> str:
        """Generate content for social media platforms."""
        
        try:
            prompt = self._build_content_prompt(
                platform, content_type, topic, brand_voice, target_audience, additional_context
            )
            
            # Try OpenAI first, then Anthropic as fallback
            if self.openai_client:
                return self._generate_with_openai(prompt)
            elif self.anthropic_client:
                return self._generate_with_anthropic(prompt)
            else:
                return self._generate_fallback_content(platform, topic, brand_voice)
                
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return self._generate_fallback_content(platform, topic, brand_voice)
    
    def _build_content_prompt(
        self,
        platform: str,
        content_type: str,
        topic: str,
        brand_voice: str,
        target_audience: str,
        additional_context: str
    ) -> str:
        """Build optimized prompt for content generation."""
        
        platform_specs = self._get_platform_specifications(platform)
        
        prompt = f"""
Create engaging {content_type} content for {platform} about {topic}.

PLATFORM: {platform}
CONTENT TYPE: {content_type}
TOPIC: {topic}
BRAND VOICE: {brand_voice}
TARGET AUDIENCE: {target_audience}

PLATFORM SPECIFICATIONS:
{platform_specs}

REQUIREMENTS:
1. Follow platform-specific best practices and character limits
2. Maintain consistent brand voice: {brand_voice}
3. Optimize for target audience: {target_audience}
4. Include relevant hashtags (appropriate number for platform)
5. Add engaging call-to-action
6. Use trending keywords naturally
7. Create compelling hook in the first sentence

ADDITIONAL CONTEXT:
{additional_context}

DELIVERABLES:
- Main content/caption
- Relevant hashtags
- Engagement strategy suggestions
- Best posting time recommendations

Generate high-quality, engaging content that will resonate with the target audience and perform well on {platform}.
        """
        
        return prompt.strip()
    
    def _get_platform_specifications(self, platform: str) -> str:
        """Get platform-specific content guidelines."""
        
        specs = {
            'twitter': """
            - Character limit: 280 characters
            - Use 1-2 relevant hashtags maximum
            - Include engaging visuals when possible
            - Encourage retweets and replies
            - Use threads for longer content
            - Optimal posting times: 9 AM, 1 PM, 3 PM weekdays
            """,
            'linkedin': """
            - Professional tone and industry insights
            - Longer posts (1300 characters) perform well
            - Use 3-5 professional hashtags
            - Share expertise and thought leadership
            - Encourage professional discussions
            - Optimal posting times: Tuesday-Thursday, 7-9 AM
            """,
            'instagram': """
            - Visual-first platform - content should complement images
            - Use 5-10 hashtags in first comment or end of caption
            - Include call-to-action for engagement
            - Stories and Reels perform well
            - Authentic, lifestyle-focused content
            - Optimal posting times: 6-9 AM, 12-2 PM, 5-7 PM
            """,
            'facebook': """
            - Conversational and community-focused
            - Longer posts can perform well (up to 500 characters)
            - Use 1-2 hashtags maximum
            - Encourage comments and shares
            - Include questions to drive engagement
            - Optimal posting times: 9 AM, 1-3 PM weekdays
            """,
            'tiktok': """
            - Short, catchy, trend-focused content
            - Hook viewers in first 3 seconds
            - Use trending hashtags and sounds
            - Authentic, entertaining content
            - Include clear call-to-action
            - Optimal posting times: 6-10 AM, 7-9 PM
            """,
            'youtube': """
            - Compelling titles and descriptions
            - Use relevant keywords for SEO
            - Include timestamps for longer videos
            - Encourage subscriptions and comments
            - End screens and cards for engagement
            - Consistent posting schedule important
            """
        }
        
        return specs.get(platform.lower(), "General social media best practices apply.")
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate content using OpenAI."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator who creates engaging, platform-optimized content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', 2000)),
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise
    
    def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate content using Anthropic."""
        
        try:
            response = self.anthropic_client.messages.create(
                model=os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}")
            raise
    
    def _generate_fallback_content(self, platform: str, topic: str, brand_voice: str) -> str:
        """Generate basic fallback content when AI services are unavailable."""
        
        templates = {
            'twitter': f"🔥 Excited to share insights about {topic}! What's your experience with this? Share your thoughts below! #{topic.replace(' ', '')}",
            'linkedin': f"Sharing some thoughts on {topic} and its impact on our industry. Would love to hear your perspectives in the comments. #{topic.replace(' ', '')} #Industry #Insights",
            'instagram': f"✨ Diving deep into {topic} today! Swipe to see more insights. What questions do you have? Drop them below! ⬇️ #{topic.replace(' ', '')} #Content",
            'facebook': f"Let's talk about {topic}! I've been exploring this topic and wanted to share some insights with our community. What are your thoughts?",
            'tiktok': f"POV: You're learning about {topic} 🎯 Follow for more insights! #{topic.replace(' ', '')} #Learn #Tips",
            'youtube': f"In today's video, we're exploring {topic} and what it means for you. Don't forget to subscribe for more content like this!"
        }
        
        fallback = templates.get(platform.lower(), f"Exploring {topic} - what are your thoughts on this? Let's discuss!")
        
        return f"""
FALLBACK CONTENT (AI services unavailable):

Content: {fallback}

Hashtags: #{topic.replace(' ', '')} #SocialMedia #Engagement

Note: This is basic template content. For optimal results, please configure your AI API keys.
        """.strip()


class HashtagResearchTool(BaseTool):
    """Tool for researching and suggesting optimal hashtags."""
    
    name: str = "hashtag_research_tool"
    description: str = "Research and suggest optimal hashtags for social media content"
    
    def _run(self, topic: str, platform: str, target_audience: str) -> str:
        """Research hashtags for given topic and platform."""
        
        try:
            # Platform-specific hashtag strategies
            hashtag_strategies = {
                'instagram': {
                    'count': '5-10 hashtags',
                    'mix': 'Mix of popular and niche hashtags',
                    'placement': 'First comment or end of caption'
                },
                'twitter': {
                    'count': '1-2 hashtags maximum',
                    'mix': 'Trending and topic-specific',
                    'placement': 'Integrated naturally in tweet'
                },
                'linkedin': {
                    'count': '3-5 professional hashtags',
                    'mix': 'Industry-specific and broad professional tags',
                    'placement': 'End of post'
                },
                'tiktok': {
                    'count': '3-5 hashtags',
                    'mix': 'Trending tags and niche descriptive tags',
                    'placement': 'In caption'
                }
            }
            
            # Generate hashtag suggestions
            suggested_hashtags = self._generate_hashtag_suggestions(topic, platform, target_audience)
            
            strategy = hashtag_strategies.get(platform.lower(), hashtag_strategies['instagram'])
            
            return f"""
HASHTAG RESEARCH RESULTS:

Platform: {platform}
Topic: {topic}
Target Audience: {target_audience}

STRATEGY:
- Count: {strategy['count']}
- Mix: {strategy['mix']}
- Placement: {strategy['placement']}

SUGGESTED HASHTAGS:
{suggested_hashtags}

TIPS:
- Monitor hashtag performance regularly
- Mix popular and niche hashtags
- Avoid banned or spam hashtags
- Keep hashtags relevant to content
- Use hashtag analytics tools for optimization
            """.strip()
            
        except Exception as e:
            logger.error(f"Hashtag research failed: {str(e)}")
            return f"Error researching hashtags: {str(e)}"
    
    def _generate_hashtag_suggestions(self, topic: str, platform: str, target_audience: str) -> str:
        """Generate hashtag suggestions based on topic and platform."""
        
        # Basic hashtag generation logic
        topic_words = topic.lower().split()
        base_tags = []
        
        # Create base hashtags from topic
        for word in topic_words:
            if len(word) > 2:  # Avoid very short words
                base_tags.append(f"#{word}")
        
        # Add topic as combined hashtag
        topic_combined = topic.replace(' ', '').replace('-', '')
        if len(topic_combined) <= 20:  # Instagram hashtag limit
            base_tags.append(f"#{topic_combined}")
        
        # Platform-specific additions
        platform_tags = {
            'instagram': ['#content', '#socialmedia', '#engagement', '#community'],
            'twitter': ['#trending', '#discussion'],
            'linkedin': ['#professional', '#industry', '#insights', '#networking'],
            'tiktok': ['#fyp', '#trending', '#viral', '#tips'],
            'facebook': ['#community', '#discussion'],
            'youtube': ['#video', '#subscribe', '#content']
        }
        
        suggested = base_tags + platform_tags.get(platform.lower(), [])
        
        return '\n'.join(suggested[:10])  # Limit to 10 suggestions


class ContentOptimizationTool(BaseTool):
    """Tool for optimizing content for better engagement."""
    
    name: str = "content_optimization_tool"
    description: str = "Optimize content for maximum engagement and platform performance"
    
    def _run(self, content: str, platform: str, optimization_goals: str) -> str:
        """Optimize existing content for better performance."""
        
        try:
            optimization_suggestions = []
            
            # Platform-specific optimizations
            if platform.lower() == 'twitter':
                optimization_suggestions.extend(self._optimize_for_twitter(content))
            elif platform.lower() == 'instagram':
                optimization_suggestions.extend(self._optimize_for_instagram(content))
            elif platform.lower() == 'linkedin':
                optimization_suggestions.extend(self._optimize_for_linkedin(content))
            elif platform.lower() == 'tiktok':
                optimization_suggestions.extend(self._optimize_for_tiktok(content))
            
            # General optimizations
            optimization_suggestions.extend(self._general_optimizations(content))
            
            return f"""
CONTENT OPTIMIZATION ANALYSIS:

Original Content: {content[:100]}...
Platform: {platform}
Goals: {optimization_goals}

OPTIMIZATION SUGGESTIONS:
{chr(10).join(f"• {suggestion}" for suggestion in optimization_suggestions)}

PERFORMANCE PREDICTIONS:
- Engagement potential: Medium to High
- Shareability: Depends on implementation of suggestions
- Algorithm compatibility: Good with optimizations applied
            """.strip()
            
        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            return f"Error optimizing content: {str(e)}"
    
    def _optimize_for_twitter(self, content: str) -> List[str]:
        """Twitter-specific optimization suggestions."""
        suggestions = []
        
        if len(content) > 280:
            suggestions.append("Content exceeds Twitter's 280-character limit - consider shortening or creating a thread")
        
        if '#' not in content:
            suggestions.append("Consider adding 1-2 relevant hashtags")
        
        if '?' not in content and '!' not in content:
            suggestions.append("Add engaging punctuation or call-to-action")
        
        return suggestions
    
    def _optimize_for_instagram(self, content: str) -> List[str]:
        """Instagram-specific optimization suggestions."""
        suggestions = []
        
        if len(content) < 100:
            suggestions.append("Consider expanding content - longer captions often perform better on Instagram")
        
        if 'story' not in content.lower():
            suggestions.append("Consider mentioning if this relates to Instagram Stories")
        
        return suggestions
    
    def _optimize_for_linkedin(self, content: str) -> List[str]:
        """LinkedIn-specific optimization suggestions."""
        suggestions = []
        
        if len(content) < 150:
            suggestions.append("Consider expanding with professional insights - LinkedIn favors longer, value-driven content")
        
        if '?' not in content:
            suggestions.append("Add a thought-provoking question to encourage professional discussion")
        
        return suggestions
    
    def _optimize_for_tiktok(self, content: str) -> List[str]:
        """TikTok-specific optimization suggestions."""
        suggestions = []
        
        if 'pov:' not in content.lower() and 'how to' not in content.lower():
            suggestions.append("Consider using trending formats like 'POV:' or 'How to'")
        
        suggestions.append("Ensure content complements video format")
        
        return suggestions
    
    def _general_optimizations(self, content: str) -> List[str]:
        """General optimization suggestions for all platforms."""
        suggestions = []
        
        # Check for call-to-action
        cta_keywords = ['comment', 'share', 'like', 'follow', 'subscribe', 'click', 'visit']
        if not any(keyword in content.lower() for keyword in cta_keywords):
            suggestions.append("Add a clear call-to-action to encourage engagement")
        
        # Check for emotional words
        emotional_words = ['amazing', 'incredible', 'exciting', 'love', 'awesome', 'fantastic']
        if not any(word in content.lower() for word in emotional_words):
            suggestions.append("Consider adding emotional language to increase engagement")
        
        return suggestions