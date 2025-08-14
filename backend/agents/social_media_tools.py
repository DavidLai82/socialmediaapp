"""
Social Media Analysis and Integration Tools
"""

import asyncio
import logging
import os
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from crewai.tools import BaseTool
import requests
import tweepy
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SocialMediaAnalysisTool(BaseTool):
    """Tool for analyzing social media trends and competitor activities."""
    
    name: str = "social_media_analysis_tool"
    description: str = "Analyze social media trends, competitor activities, and viral content patterns"
    
    def __init__(self):
        super().__init__()
        self.twitter_client = None
        self.linkedin_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize social media API clients."""
        try:
            # Twitter API v2 client
            if all([
                os.getenv('TWITTER_BEARER_TOKEN'),
                os.getenv('TWITTER_API_KEY'),
                os.getenv('TWITTER_API_SECRET')
            ]):
                self.twitter_client = tweepy.Client(
                    bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                    consumer_key=os.getenv('TWITTER_API_KEY'),
                    consumer_secret=os.getenv('TWITTER_API_SECRET'),
                    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                    access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
                    wait_on_rate_limit=True
                )
                logger.info("Twitter client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize social media clients: {str(e)}")
    
    def _run(
        self,
        analysis_type: str,
        platforms: Union[str, List[str]],
        keywords: Union[str, List[str]],
        timeframe: str = "24h",
        competitor_accounts: Optional[List[str]] = None
    ) -> str:
        """Analyze social media trends and activities."""
        
        try:
            if isinstance(platforms, str):
                platforms = [platforms]
            if isinstance(keywords, str):
                keywords = [keywords.strip() for keywords in keywords.split(',')]
            
            results = {
                "analysis_type": analysis_type,
                "platforms": platforms,
                "keywords": keywords,
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
            
            # Perform platform-specific analysis
            for platform in platforms:
                if platform.lower() == 'twitter':
                    results["data"][platform] = self._analyze_twitter(keywords, timeframe, competitor_accounts)
                elif platform.lower() == 'linkedin':
                    results["data"][platform] = self._analyze_linkedin(keywords, timeframe, competitor_accounts)
                elif platform.lower() == 'instagram':
                    results["data"][platform] = self._analyze_instagram(keywords, timeframe, competitor_accounts)
                else:
                    results["data"][platform] = self._fallback_analysis(platform, keywords, timeframe)
            
            # Generate insights and recommendations
            insights = self._generate_insights(results)
            results["insights"] = insights
            
            return json.dumps(results, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Social media analysis failed: {str(e)}")
            return self._generate_error_response(str(e))
    
    def _analyze_twitter(self, keywords: List[str], timeframe: str, competitor_accounts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze Twitter trends and activities."""
        
        if not self.twitter_client:
            return {"error": "Twitter API not configured", "fallback": self._twitter_fallback_analysis(keywords)}
        
        try:
            analysis_data = {
                "trending_topics": [],
                "keyword_performance": {},
                "competitor_analysis": {},
                "viral_patterns": [],
                "engagement_insights": {}
            }
            
            # Get trending topics
            try:
                trends = self.twitter_client.get_place_trends(1)  # Worldwide trends
                if trends:
                    analysis_data["trending_topics"] = [trend["name"] for trend in trends[0]["trends"][:10]]
            except Exception as e:
                logger.warning(f"Could not fetch Twitter trends: {str(e)}")
            
            # Analyze keywords
            for keyword in keywords:
                try:
                    # Search recent tweets
                    tweets = self.twitter_client.search_recent_tweets(
                        query=keyword,
                        max_results=100,
                        tweet_fields=['created_at', 'public_metrics', 'author_id']
                    )
                    
                    if tweets.data:
                        keyword_data = self._analyze_tweet_performance(tweets.data)
                        analysis_data["keyword_performance"][keyword] = keyword_data
                        
                except Exception as e:
                    logger.warning(f"Could not analyze keyword '{keyword}': {str(e)}")
                    analysis_data["keyword_performance"][keyword] = {"error": str(e)}
            
            # Analyze competitor accounts
            if competitor_accounts:
                for account in competitor_accounts:
                    try:
                        user = self.twitter_client.get_user(username=account.replace('@', ''))
                        if user.data:
                            user_tweets = self.twitter_client.get_users_tweets(
                                user.data.id,
                                max_results=50,
                                tweet_fields=['created_at', 'public_metrics']
                            )
                            
                            if user_tweets.data:
                                competitor_data = self._analyze_competitor_performance(user_tweets.data)
                                analysis_data["competitor_analysis"][account] = competitor_data
                                
                    except Exception as e:
                        logger.warning(f"Could not analyze competitor '{account}': {str(e)}")
                        analysis_data["competitor_analysis"][account] = {"error": str(e)}
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Twitter analysis failed: {str(e)}")
            return {"error": str(e), "fallback": self._twitter_fallback_analysis(keywords)}
    
    def _analyze_linkedin(self, keywords: List[str], timeframe: str, competitor_accounts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze LinkedIn trends and activities."""
        
        # LinkedIn API has limited public access, so we provide structured fallback analysis
        return {
            "platform": "LinkedIn",
            "note": "LinkedIn API access is limited. Providing trend analysis based on industry patterns.",
            "trending_topics": self._get_linkedin_industry_trends(),
            "keyword_insights": self._analyze_linkedin_keywords(keywords),
            "best_practices": {
                "posting_times": ["Tuesday-Thursday", "7-9 AM", "12-1 PM"],
                "content_types": ["Industry insights", "Professional tips", "Company updates"],
                "hashtag_strategy": "3-5 professional hashtags",
                "engagement_tips": [
                    "Ask thought-provoking questions",
                    "Share industry insights",
                    "Comment on industry leader posts",
                    "Use professional storytelling"
                ]
            },
            "competitor_analysis": self._linkedin_competitor_guidance(competitor_accounts) if competitor_accounts else None
        }
    
    def _analyze_instagram(self, keywords: List[str], timeframe: str, competitor_accounts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze Instagram trends and activities."""
        
        # Instagram Basic Display API has limited capabilities for public data
        return {
            "platform": "Instagram",
            "note": "Instagram API access is limited. Providing trend analysis based on platform patterns.",
            "trending_hashtags": self._get_instagram_trending_hashtags(keywords),
            "content_insights": {
                "popular_formats": ["Reels", "Stories", "Carousel posts"],
                "optimal_posting_times": ["6-9 AM", "12-2 PM", "5-7 PM"],
                "hashtag_strategy": "5-10 hashtags, mix of popular and niche",
                "engagement_drivers": [
                    "High-quality visuals",
                    "Authentic storytelling",
                    "User-generated content",
                    "Behind-the-scenes content"
                ]
            },
            "keyword_analysis": self._analyze_instagram_keywords(keywords),
            "competitor_insights": self._instagram_competitor_guidance(competitor_accounts) if competitor_accounts else None
        }
    
    def _fallback_analysis(self, platform: str, keywords: List[str], timeframe: str) -> Dict[str, Any]:
        """Provide fallback analysis when API access is not available."""
        
        return {
            "platform": platform,
            "analysis_type": "Fallback Analysis",
            "note": f"API access not configured for {platform}. Providing general insights.",
            "keywords": keywords,
            "general_insights": {
                "trending_topics": f"General trends for {', '.join(keywords)}",
                "best_practices": self._get_platform_best_practices(platform),
                "content_suggestions": self._generate_content_suggestions(platform, keywords),
                "timing_recommendations": self._get_optimal_posting_times(platform)
            }
        }
    
    def _analyze_tweet_performance(self, tweets: List) -> Dict[str, Any]:
        """Analyze performance metrics of tweets."""
        
        total_tweets = len(tweets)
        total_likes = sum(tweet.public_metrics.get('like_count', 0) for tweet in tweets)
        total_retweets = sum(tweet.public_metrics.get('retweet_count', 0) for tweet in tweets)
        total_replies = sum(tweet.public_metrics.get('reply_count', 0) for tweet in tweets)
        
        return {
            "total_tweets": total_tweets,
            "average_likes": total_likes / total_tweets if total_tweets > 0 else 0,
            "average_retweets": total_retweets / total_tweets if total_tweets > 0 else 0,
            "average_replies": total_replies / total_tweets if total_tweets > 0 else 0,
            "engagement_rate": (total_likes + total_retweets + total_replies) / total_tweets if total_tweets > 0 else 0,
            "top_performing_tweets": sorted(tweets, key=lambda t: t.public_metrics.get('like_count', 0), reverse=True)[:3]
        }
    
    def _analyze_competitor_performance(self, tweets: List) -> Dict[str, Any]:
        """Analyze competitor tweet performance."""
        
        performance_data = self._analyze_tweet_performance(tweets)
        
        # Add competitor-specific insights
        performance_data.update({
            "posting_frequency": len(tweets),
            "content_themes": self._extract_content_themes([tweet.text for tweet in tweets]),
            "engagement_patterns": self._analyze_engagement_patterns(tweets)
        })
        
        return performance_data
    
    def _extract_content_themes(self, tweet_texts: List[str]) -> List[str]:
        """Extract common themes from tweet content."""
        
        # Simple keyword extraction (in production, you'd use more sophisticated NLP)
        all_words = []
        for text in tweet_texts:
            words = text.lower().split()
            all_words.extend([word.strip('.,!?#@') for word in words if len(word) > 3])
        
        # Count word frequency
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Return top themes
        themes = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return [theme[0] for theme in themes]
    
    def _analyze_engagement_patterns(self, tweets: List) -> Dict[str, Any]:
        """Analyze engagement patterns in tweets."""
        
        hourly_engagement = {}
        for tweet in tweets:
            hour = tweet.created_at.hour
            engagement = (
                tweet.public_metrics.get('like_count', 0) +
                tweet.public_metrics.get('retweet_count', 0) +
                tweet.public_metrics.get('reply_count', 0)
            )
            
            if hour not in hourly_engagement:
                hourly_engagement[hour] = []
            hourly_engagement[hour].append(engagement)
        
        # Calculate average engagement by hour
        avg_hourly_engagement = {}
        for hour, engagements in hourly_engagement.items():
            avg_hourly_engagement[hour] = sum(engagements) / len(engagements)
        
        best_hours = sorted(avg_hourly_engagement.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "best_posting_hours": [f"{hour}:00" for hour, _ in best_hours],
            "hourly_averages": avg_hourly_engagement
        }
    
    def _generate_insights(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights from analysis results."""
        
        insights = {
            "key_findings": [],
            "recommendations": [],
            "trending_opportunities": [],
            "content_strategy": [],
            "timing_optimization": []
        }
        
        # Analyze data across platforms
        for platform, data in results["data"].items():
            if "error" not in data:
                # Key findings
                if "trending_topics" in data and data["trending_topics"]:
                    insights["key_findings"].append(f"{platform}: Top trending topics include {', '.join(data['trending_topics'][:3])}")
                
                # Recommendations
                if "keyword_performance" in data:
                    for keyword, perf in data["keyword_performance"].items():
                        if "engagement_rate" in perf and perf["engagement_rate"] > 0:
                            insights["recommendations"].append(f"Keyword '{keyword}' shows strong engagement on {platform}")
                
                # Trending opportunities
                if "viral_patterns" in data and data["viral_patterns"]:
                    insights["trending_opportunities"].extend(data["viral_patterns"])
        
        # Generate content strategy recommendations
        insights["content_strategy"] = [
            "Focus on trending topics identified in analysis",
            "Create content around high-performing keywords",
            "Study competitor strategies and adapt successful approaches",
            "Optimize posting times based on engagement patterns"
        ]
        
        return insights
    
    def _twitter_fallback_analysis(self, keywords: List[str]) -> Dict[str, Any]:
        """Provide fallback Twitter analysis."""
        
        return {
            "trending_topics": ["AI", "Technology", "Social Media", "Digital Marketing", "Innovation"],
            "keyword_suggestions": keywords + ["trending", "viral", "engagement"],
            "best_practices": {
                "character_limit": 280,
                "optimal_hashtags": "1-2 per tweet",
                "posting_frequency": "3-5 times per day",
                "best_times": ["9 AM", "1 PM", "3 PM"]
            }
        }
    
    def _get_linkedin_industry_trends(self) -> List[str]:
        """Get current LinkedIn industry trends."""
        
        return [
            "AI and Automation",
            "Remote Work Strategies",
            "Professional Development",
            "Industry Insights",
            "Leadership Tips",
            "Career Growth",
            "Digital Transformation",
            "Networking",
            "Thought Leadership",
            "Business Strategy"
        ]
    
    def _analyze_linkedin_keywords(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze LinkedIn keyword potential."""
        
        analysis = {}
        for keyword in keywords:
            analysis[keyword] = {
                "professional_relevance": "High" if any(word in keyword.lower() for word in ["business", "professional", "career", "industry"]) else "Medium",
                "hashtag_potential": f"#{keyword.replace(' ', '')}",
                "content_angle": f"Professional insights on {keyword}",
                "target_audience": "Industry professionals and decision makers"
            }
        
        return analysis
    
    def _linkedin_competitor_guidance(self, competitor_accounts: List[str]) -> Dict[str, Any]:
        """Provide LinkedIn competitor analysis guidance."""
        
        return {
            "analysis_approach": "Manual monitoring recommended",
            "key_metrics": ["Post engagement", "Follower growth", "Content themes", "Posting frequency"],
            "competitors": {account: {"monitoring_status": "Manual review required"} for account in competitor_accounts},
            "tools_recommended": ["LinkedIn Analytics", "Third-party social listening tools"]
        }
    
    def _get_instagram_trending_hashtags(self, keywords: List[str]) -> List[str]:
        """Generate trending Instagram hashtags."""
        
        base_hashtags = []
        for keyword in keywords:
            # Create hashtags from keywords
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            base_hashtags.append(hashtag)
        
        # Add general trending hashtags
        trending = ["#trending", "#viral", "#content", "#socialmedia", "#engagement", "#community", "#brand", "#marketing"]
        
        return base_hashtags + trending
    
    def _analyze_instagram_keywords(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze Instagram keyword potential."""
        
        analysis = {}
        for keyword in keywords:
            analysis[keyword] = {
                "hashtag_potential": f"#{keyword.replace(' ', '')}",
                "visual_content_ideas": [f"{keyword} behind-the-scenes", f"{keyword} tutorial", f"{keyword} inspiration"],
                "story_opportunities": [f"{keyword} polls", f"{keyword} Q&A", f"{keyword} tips"],
                "reel_concepts": [f"Quick {keyword} tips", f"{keyword} before/after", f"{keyword} trends"]
            }
        
        return analysis
    
    def _instagram_competitor_guidance(self, competitor_accounts: List[str]) -> Dict[str, Any]:
        """Provide Instagram competitor analysis guidance."""
        
        return {
            "analysis_approach": "Manual monitoring and third-party tools",
            "key_metrics": ["Engagement rate", "Story views", "Reel performance", "Hashtag usage"],
            "competitors": {account: {"monitoring_status": "Manual review required"} for account in competitor_accounts},
            "tools_recommended": ["Instagram Insights", "Third-party analytics tools"]
        }
    
    def _get_platform_best_practices(self, platform: str) -> Dict[str, Any]:
        """Get best practices for specific platform."""
        
        practices = {
            'twitter': {
                "character_limit": 280,
                "hashtags": "1-2 per tweet",
                "posting_frequency": "3-5 times per day",
                "best_content": ["News updates", "Quick tips", "Engaging questions"]
            },
            'linkedin': {
                "post_length": "1300 characters optimal",
                "hashtags": "3-5 professional hashtags",
                "posting_frequency": "1-2 times per day",
                "best_content": ["Industry insights", "Professional tips", "Thought leadership"]
            },
            'instagram': {
                "caption_length": "125-150 characters for feed posts",
                "hashtags": "5-10 hashtags",
                "posting_frequency": "1-2 times per day",
                "best_content": ["Visual storytelling", "Behind-the-scenes", "User-generated content"]
            },
            'facebook': {
                "post_length": "40-80 characters for high engagement",
                "hashtags": "1-2 hashtags maximum",
                "posting_frequency": "1-2 times per day",
                "best_content": ["Community-focused", "Shareable content", "Videos"]
            }
        }
        
        return practices.get(platform.lower(), practices['twitter'])
    
    def _generate_content_suggestions(self, platform: str, keywords: List[str]) -> List[str]:
        """Generate content suggestions for platform and keywords."""
        
        suggestions = []
        for keyword in keywords:
            suggestions.extend([
                f"Share insights about {keyword}",
                f"Ask audience questions about {keyword}",
                f"Create tutorial content for {keyword}",
                f"Share news/updates related to {keyword}"
            ])
        
        return suggestions[:8]  # Limit to 8 suggestions
    
    def _get_optimal_posting_times(self, platform: str) -> List[str]:
        """Get optimal posting times for platform."""
        
        times = {
            'twitter': ["9:00 AM", "1:00 PM", "3:00 PM"],
            'linkedin': ["7:00 AM", "8:00 AM", "12:00 PM", "5:00 PM"],
            'instagram': ["6:00 AM", "12:00 PM", "7:00 PM"],
            'facebook': ["9:00 AM", "1:00 PM", "3:00 PM"],
            'tiktok': ["6:00 AM", "10:00 AM", "7:00 PM"],
            'youtube': ["2:00 PM", "4:00 PM", "6:00 PM"]
        }
        
        return times.get(platform.lower(), times['twitter'])
    
    def _generate_error_response(self, error_message: str) -> str:
        """Generate structured error response."""
        
        return json.dumps({
            "error": True,
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "fallback_data": {
                "general_trends": ["AI", "Social Media", "Digital Marketing", "Technology"],
                "recommendation": "Please check API configurations and try again",
                "manual_analysis": "Consider using social media management tools for detailed analysis"
            }
        }, indent=2)


class SocialMediaPostingTool(BaseTool):
    """Tool for posting content to social media platforms."""
    
    name: str = "social_media_posting_tool"
    description: str = "Post content to various social media platforms"
    
    def __init__(self):
        super().__init__()
        self.twitter_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize social media API clients for posting."""
        try:
            if all([
                os.getenv('TWITTER_API_KEY'),
                os.getenv('TWITTER_API_SECRET'),
                os.getenv('TWITTER_ACCESS_TOKEN'),
                os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            ]):
                auth = tweepy.OAuthHandler(
                    os.getenv('TWITTER_API_KEY'),
                    os.getenv('TWITTER_API_SECRET')
                )
                auth.set_access_token(
                    os.getenv('TWITTER_ACCESS_TOKEN'),
                    os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
                )
                self.twitter_client = tweepy.API(auth, wait_on_rate_limit=True)
                logger.info("Twitter posting client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize posting clients: {str(e)}")
    
    def _run(
        self,
        platform: str,
        content: str,
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None
    ) -> str:
        """Post content to social media platform."""
        
        try:
            result = {
                "platform": platform,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            if platform.lower() == 'twitter':
                result.update(self._post_to_twitter(content, media_urls))
            elif platform.lower() == 'linkedin':
                result.update(self._post_to_linkedin(content, media_urls))
            elif platform.lower() == 'instagram':
                result.update(self._post_to_instagram(content, media_urls))
            else:
                result.update({
                    "status": "simulated",
                    "message": f"Posting simulation for {platform} - API not configured"
                })
            
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Posting failed: {str(e)}")
            return json.dumps({
                "error": True,
                "message": str(e),
                "platform": platform,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
    
    def _post_to_twitter(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post content to Twitter."""
        
        if not self.twitter_client:
            return {
                "status": "error",
                "message": "Twitter API not configured",
                "simulation": True
            }
        
        try:
            # For demo purposes, we'll simulate posting
            return {
                "status": "simulated",
                "message": "Twitter posting simulated - would post in production",
                "content_length": len(content),
                "within_limits": len(content) <= 280,
                "media_count": len(media_urls) if media_urls else 0
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _post_to_linkedin(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post content to LinkedIn."""
        
        return {
            "status": "simulated",
            "message": "LinkedIn posting simulated - requires LinkedIn API setup",
            "content_length": len(content),
            "professional_tone": "business" in content.lower() or "professional" in content.lower()
        }
    
    def _post_to_instagram(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post content to Instagram."""
        
        return {
            "status": "simulated",
            "message": "Instagram posting simulated - requires Instagram API setup",
            "content_length": len(content),
            "requires_media": True,
            "media_provided": bool(media_urls)
        }