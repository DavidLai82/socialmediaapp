"""
Video Creation and Script Writing Tools for Social Media
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
from crewai.tools import BaseTool
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class VideoCreationTool(BaseTool):
    """Tool for planning and creating video content strategies."""
    
    name: str = "video_creation_tool"
    description: str = "Create comprehensive video content plans, shot lists, and production guidelines"
    
    def _run(
        self,
        topic: str,
        platform: str,
        duration: str,
        style: str,
        target_audience: str,
        video_type: str = "educational",
        brand_voice: str = "professional"
    ) -> str:
        """Create comprehensive video content plan."""
        
        try:
            # Generate video concept
            video_plan = {
                "project_info": {
                    "topic": topic,
                    "platform": platform,
                    "duration": duration,
                    "style": style,
                    "target_audience": target_audience,
                    "video_type": video_type,
                    "brand_voice": brand_voice,
                    "created_at": datetime.now().isoformat()
                },
                "concept": self._generate_video_concept(topic, platform, style, video_type),
                "script_outline": self._create_script_outline(topic, duration, platform, style),
                "shot_list": self._create_shot_list(platform, style, duration),
                "production_guidelines": self._get_production_guidelines(platform, duration),
                "post_production": self._get_post_production_guidelines(platform),
                "optimization": self._get_platform_optimization(platform),
                "engagement_strategy": self._create_engagement_strategy(platform, target_audience),
                "metrics_tracking": self._define_success_metrics(platform, video_type)
            }
            
            return json.dumps(video_plan, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Video creation planning failed: {str(e)}")
            return self._generate_error_response(str(e))
    
    def _generate_video_concept(self, topic: str, platform: str, style: str, video_type: str) -> Dict[str, Any]:
        """Generate creative video concept."""
        
        concept_templates = {
            "educational": {
                "structure": "Hook → Problem → Solution → Action",
                "approach": f"Teach viewers about {topic} in an engaging way",
                "key_elements": ["Clear explanation", "Visual aids", "Step-by-step guidance", "Practical examples"]
            },
            "entertainment": {
                "structure": "Hook → Build-up → Climax → Resolution",
                "approach": f"Entertain while incorporating {topic}",
                "key_elements": ["Strong hook", "Storytelling", "Humor/emotion", "Memorable moments"]
            },
            "promotional": {
                "structure": "Hook → Problem → Solution → Call-to-Action",
                "approach": f"Showcase benefits related to {topic}",
                "key_elements": ["Clear value proposition", "Social proof", "Strong CTA", "Brand integration"]
            },
            "behind_the_scenes": {
                "structure": "Introduction → Process → Insights → Conclusion",
                "approach": f"Show the process behind {topic}",
                "key_elements": ["Authenticity", "Process revelation", "Personal insights", "Community building"]
            }
        }
        
        base_concept = concept_templates.get(video_type, concept_templates["educational"])
        
        platform_adaptations = self._get_platform_concept_adaptations(platform)
        style_elements = self._get_style_elements(style)
        
        return {
            "main_concept": base_concept["approach"],
            "narrative_structure": base_concept["structure"],
            "key_elements": base_concept["key_elements"],
            "platform_adaptations": platform_adaptations,
            "style_elements": style_elements,
            "unique_angle": self._generate_unique_angle(topic, platform, style),
            "visual_theme": self._suggest_visual_theme(style, topic),
            "target_emotions": self._identify_target_emotions(video_type, topic)
        }
    
    def _create_script_outline(self, topic: str, duration: str, platform: str, style: str) -> Dict[str, Any]:
        """Create detailed script outline."""
        
        duration_seconds = self._parse_duration(duration)
        timing_breakdown = self._calculate_timing_breakdown(duration_seconds, platform)
        
        return {
            "total_duration": duration,
            "duration_seconds": duration_seconds,
            "timing_breakdown": timing_breakdown,
            "script_sections": {
                "hook": {
                    "duration": timing_breakdown["hook"],
                    "purpose": "Grab attention immediately",
                    "content_guidelines": [
                        "Start with compelling question or statement",
                        "Create curiosity gap",
                        "Promise value delivery",
                        f"Relate directly to {topic}"
                    ],
                    "platform_notes": self._get_hook_platform_notes(platform)
                },
                "introduction": {
                    "duration": timing_breakdown["introduction"],
                    "purpose": "Set context and establish credibility",
                    "content_guidelines": [
                        "Introduce yourself/brand briefly",
                        f"Establish expertise in {topic}",
                        "Preview what viewers will learn",
                        "Build rapport with audience"
                    ]
                },
                "main_content": {
                    "duration": timing_breakdown["main_content"],
                    "purpose": "Deliver core value",
                    "content_guidelines": [
                        f"Break down {topic} into digestible points",
                        "Use examples and demonstrations",
                        "Maintain engagement throughout",
                        "Include visual elements"
                    ],
                    "structure_suggestions": self._get_main_content_structure(topic, duration_seconds)
                },
                "conclusion": {
                    "duration": timing_breakdown["conclusion"],
                    "purpose": "Reinforce key points and drive action",
                    "content_guidelines": [
                        f"Summarize key points about {topic}",
                        "Provide clear call-to-action",
                        "Encourage engagement",
                        "Thank viewers"
                    ]
                }
            },
            "transition_suggestions": self._get_transition_suggestions(platform, style),
            "engagement_moments": self._identify_engagement_moments(duration_seconds)
        }
    
    def _create_shot_list(self, platform: str, style: str, duration: str) -> Dict[str, Any]:
        """Create detailed shot list for video production."""
        
        duration_seconds = self._parse_duration(duration)
        platform_specs = self._get_platform_video_specs(platform)
        
        shot_categories = {
            "establishing_shots": {
                "purpose": "Set the scene and context",
                "shots": [
                    "Wide shot of filming location",
                    "Close-up of key props/materials",
                    "Brand/logo integration shot"
                ],
                "duration": "5-10 seconds each"
            },
            "talking_head_shots": {
                "purpose": "Main presenter/content delivery",
                "shots": [
                    "Medium shot (chest up)",
                    "Close-up for emphasis",
                    "Over-the-shoulder for demonstrations"
                ],
                "duration": "Primary footage",
                "notes": platform_specs["aspect_ratio_notes"]
            },
            "b_roll_shots": {
                "purpose": "Support main content and maintain visual interest",
                "shots": [
                    "Hands-on demonstrations",
                    "Product/topic close-ups",
                    "Process shots",
                    "Environment/context shots"
                ],
                "duration": "2-5 seconds each",
                "quantity": f"{max(3, duration_seconds // 10)} shots recommended"
            },
            "transition_shots": {
                "purpose": "Smooth transitions between segments",
                "shots": [
                    "Graphics/text overlays",
                    "Logo animations",
                    "Movement shots",
                    "Cut-away reactions"
                ],
                "duration": "1-2 seconds each"
            }
        }
        
        return {
            "total_shots_needed": self._calculate_total_shots(duration_seconds),
            "platform_specifications": platform_specs,
            "shot_categories": shot_categories,
            "filming_order": self._suggest_filming_order(),
            "equipment_recommendations": self._get_equipment_recommendations(style, platform),
            "lighting_setup": self._get_lighting_recommendations(style),
            "audio_requirements": self._get_audio_requirements(platform)
        }
    
    def _get_production_guidelines(self, platform: str, duration: str) -> Dict[str, Any]:
        """Get comprehensive production guidelines."""
        
        platform_specs = self._get_platform_video_specs(platform)
        
        return {
            "pre_production": {
                "planning": [
                    "Finalize script and shot list",
                    "Prepare all props and materials",
                    "Test equipment and setup",
                    "Plan filming schedule"
                ],
                "location_prep": [
                    "Ensure good lighting conditions",
                    "Minimize background noise",
                    "Set up backdrop/environment",
                    "Test camera positions"
                ]
            },
            "production": {
                "filming_tips": [
                    "Record in highest quality available",
                    "Shoot multiple takes for key segments",
                    "Capture extra B-roll footage",
                    "Monitor audio levels throughout"
                ],
                "technical_specs": platform_specs,
                "quality_checklist": [
                    "Sharp focus maintained",
                    "Consistent lighting",
                    "Clear audio without echo",
                    "Stable camera movement"
                ]
            },
            "backup_plans": {
                "technical_issues": "Have backup recording device ready",
                "content_problems": "Prepare additional talking points",
                "time_constraints": "Identify non-essential shots that can be skipped"
            }
        }
    
    def _get_post_production_guidelines(self, platform: str) -> Dict[str, Any]:
        """Get post-production and editing guidelines."""
        
        return {
            "editing_workflow": {
                "rough_cut": [
                    "Assemble main footage in sequence",
                    "Remove obvious mistakes and dead air",
                    "Check overall flow and timing",
                    "Identify areas needing B-roll"
                ],
                "fine_cut": [
                    "Add B-roll and transitions",
                    "Insert graphics and text overlays",
                    "Color correction and audio balancing",
                    "Final timing adjustments"
                ]
            },
            "platform_optimization": self._get_platform_editing_specs(platform),
            "audio_post": {
                "requirements": [
                    "Normalize audio levels",
                    "Remove background noise",
                    "Add music if appropriate",
                    "Ensure clear speech throughout"
                ]
            },
            "graphics_and_text": {
                "guidelines": [
                    "Use brand-consistent fonts and colors",
                    "Ensure text is readable on mobile",
                    "Add captions for accessibility",
                    "Include logo/branding elements"
                ]
            },
            "export_settings": self._get_export_settings(platform)
        }
    
    def _get_platform_optimization(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific optimization guidelines."""
        
        optimizations = {
            "youtube": {
                "title": "60-70 characters, keyword-optimized",
                "description": "Detailed description with timestamps and keywords",
                "thumbnail": "1280x720, eye-catching design",
                "tags": "10-15 relevant tags",
                "end_screen": "Subscribe button and related videos",
                "cards": "Promote other content or external links"
            },
            "tiktok": {
                "title": "Trending hashtags and catchy description",
                "timing": "Hook within first 3 seconds",
                "trends": "Incorporate current trending sounds/effects",
                "hashtags": "Mix trending and niche hashtags",
                "effects": "Use platform-native editing features"
            },
            "instagram": {
                "formats": "Feed post, Stories, Reels optimization",
                "caption": "Engaging caption with call-to-action",
                "hashtags": "5-10 relevant hashtags",
                "stories": "Interactive elements (polls, questions)",
                "igtv": "Vertical format optimization"
            },
            "linkedin": {
                "title": "Professional, value-focused headline",
                "description": "Professional context and key takeaways",
                "format": "Square or horizontal format preferred",
                "captions": "Professional tone with industry insights"
            },
            "facebook": {
                "title": "Engaging, shareable headline",
                "description": "Community-focused description",
                "format": "Square format performs well",
                "engagement": "Ask questions to encourage comments"
            }
        }
        
        return optimizations.get(platform.lower(), optimizations["youtube"])
    
    def _create_engagement_strategy(self, platform: str, target_audience: str) -> Dict[str, Any]:
        """Create comprehensive engagement strategy."""
        
        return {
            "pre_launch": {
                "teasers": f"Create anticipation with {target_audience}",
                "community_prep": "Notify existing followers",
                "cross_promotion": "Share on other platforms",
                "timing": "Post at optimal times for audience"
            },
            "launch": {
                "immediate_actions": [
                    "Respond to first comments quickly",
                    "Share in relevant communities",
                    "Ask engaging questions",
                    "Pin important comments"
                ],
                "call_to_actions": [
                    "Ask viewers to comment their thoughts",
                    "Encourage sharing with friends",
                    "Request likes and follows",
                    "Direct to other content"
                ]
            },
            "ongoing": {
                "community_management": [
                    "Respond to all comments within 24 hours",
                    "Ask follow-up questions",
                    "Share user-generated responses",
                    "Create follow-up content from comments"
                ],
                "performance_monitoring": [
                    "Track engagement rates",
                    "Monitor comment sentiment",
                    "Analyze traffic sources",
                    "Measure conversion goals"
                ]
            },
            "platform_specific": self._get_platform_engagement_tactics(platform)
        }
    
    def _define_success_metrics(self, platform: str, video_type: str) -> Dict[str, Any]:
        """Define success metrics and KPIs for video performance."""
        
        base_metrics = {
            "engagement_metrics": {
                "likes": "Target: 5% of views",
                "comments": "Target: 1-2% of views",
                "shares": "Target: 0.5% of views",
                "saves": "Target: 2% of views (where applicable)"
            },
            "reach_metrics": {
                "views": "Primary metric for reach",
                "impressions": "Total times video was shown",
                "unique_viewers": "Distinct people who watched",
                "reach": "Number of unique accounts reached"
            },
            "retention_metrics": {
                "watch_time": "Average percentage watched",
                "completion_rate": "Percentage who watched to end",
                "re_watches": "Viewers who watched multiple times"
            }
        }
        
        platform_specific_metrics = {
            "youtube": {
                "subscribers_gained": "New subscribers from video",
                "click_through_rate": "CTR from thumbnails",
                "session_duration": "Time spent on channel after video"
            },
            "tiktok": {
                "for_you_page": "FYP algorithm pickup",
                "duets_stitches": "User-generated responses",
                "profile_visits": "Views to creator profile"
            },
            "instagram": {
                "story_mentions": "Shares to stories",
                "profile_visits": "Visits to business profile",
                "website_clicks": "Clicks to external links"
            }
        }
        
        video_type_goals = {
            "educational": {
                "primary_goal": "Knowledge transfer and retention",
                "success_indicators": ["High completion rates", "Positive comments", "Saves/bookmarks"]
            },
            "entertainment": {
                "primary_goal": "Engagement and shareability",
                "success_indicators": ["High share rates", "Comments with reactions", "Re-watches"]
            },
            "promotional": {
                "primary_goal": "Conversions and action",
                "success_indicators": ["Click-through rates", "Website visits", "Conversions"]
            }
        }
        
        return {
            "base_metrics": base_metrics,
            "platform_specific": platform_specific_metrics.get(platform.lower(), {}),
            "video_type_goals": video_type_goals.get(video_type, video_type_goals["educational"]),
            "measurement_timeline": {
                "24_hours": "Initial performance indicators",
                "7_days": "Algorithm optimization period",
                "30_days": "Long-term performance assessment"
            },
            "benchmarking": {
                "compare_to": "Previous video performance",
                "industry_standards": f"Research {platform} benchmarks for your niche",
                "improvement_targets": "5-10% improvement over previous content"
            }
        }
    
    # Helper methods for various calculations and specifications
    
    def _parse_duration(self, duration: str) -> int:
        """Parse duration string to seconds."""
        duration = duration.lower().strip()
        
        if "min" in duration:
            minutes = int(duration.split("min")[0].strip())
            return minutes * 60
        elif "sec" in duration:
            return int(duration.split("sec")[0].strip())
        elif ":" in duration:
            parts = duration.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        else:
            # Default to seconds if unclear
            try:
                return int(duration)
            except:
                return 60  # Default to 1 minute
    
    def _calculate_timing_breakdown(self, duration_seconds: int, platform: str) -> Dict[str, str]:
        """Calculate timing breakdown for script sections."""
        
        if platform.lower() == "tiktok":
            # TikTok needs immediate hook
            return {
                "hook": "0-3 seconds",
                "introduction": "3-8 seconds",
                "main_content": f"8-{duration_seconds-5} seconds",
                "conclusion": f"{duration_seconds-5}-{duration_seconds} seconds"
            }
        elif duration_seconds <= 60:
            # Short videos
            return {
                "hook": "0-5 seconds",
                "introduction": "5-10 seconds",
                "main_content": f"10-{duration_seconds-10} seconds",
                "conclusion": f"{duration_seconds-10}-{duration_seconds} seconds"
            }
        else:
            # Longer videos
            hook_time = min(10, duration_seconds * 0.1)
            intro_time = min(20, duration_seconds * 0.15)
            conclusion_time = min(30, duration_seconds * 0.1)
            
            return {
                "hook": f"0-{int(hook_time)} seconds",
                "introduction": f"{int(hook_time)}-{int(hook_time + intro_time)} seconds",
                "main_content": f"{int(hook_time + intro_time)}-{duration_seconds - int(conclusion_time)} seconds",
                "conclusion": f"{duration_seconds - int(conclusion_time)}-{duration_seconds} seconds"
            }
    
    def _get_platform_video_specs(self, platform: str) -> Dict[str, Any]:
        """Get technical specifications for video platform."""
        
        specs = {
            "youtube": {
                "aspect_ratio": "16:9 (horizontal)",
                "resolution": "1920x1080 minimum",
                "frame_rate": "30fps or 60fps",
                "max_file_size": "256GB",
                "max_duration": "12 hours",
                "aspect_ratio_notes": "Horizontal format preferred"
            },
            "tiktok": {
                "aspect_ratio": "9:16 (vertical)",
                "resolution": "1080x1920",
                "frame_rate": "30fps",
                "max_file_size": "4GB",
                "max_duration": "10 minutes",
                "aspect_ratio_notes": "Vertical format required"
            },
            "instagram": {
                "aspect_ratio": "1:1 (square) or 9:16 (vertical)",
                "resolution": "1080x1080 or 1080x1920",
                "frame_rate": "30fps",
                "max_file_size": "4GB",
                "max_duration": "60 minutes",
                "aspect_ratio_notes": "Square for feed, vertical for reels"
            },
            "linkedin": {
                "aspect_ratio": "16:9 or 1:1",
                "resolution": "1920x1080 or 1080x1080",
                "frame_rate": "30fps",
                "max_file_size": "5GB",
                "max_duration": "10 minutes",
                "aspect_ratio_notes": "Professional horizontal or square"
            }
        }
        
        return specs.get(platform.lower(), specs["youtube"])
    
    def _get_platform_concept_adaptations(self, platform: str) -> List[str]:
        """Get platform-specific concept adaptations."""
        
        adaptations = {
            "youtube": [
                "Focus on educational value and depth",
                "Create compelling thumbnails",
                "Optimize for search with keywords",
                "Plan for longer engagement"
            ],
            "tiktok": [
                "Hook viewers within 3 seconds",
                "Use trending sounds and effects",
                "Keep content fast-paced and dynamic",
                "Encourage user participation"
            ],
            "instagram": [
                "Optimize for visual appeal",
                "Create shareable moments",
                "Use platform features (polls, questions)",
                "Plan for multiple formats (feed, stories, reels)"
            ],
            "linkedin": [
                "Focus on professional value",
                "Share industry insights",
                "Position as thought leadership",
                "Encourage professional discussion"
            ]
        }
        
        return adaptations.get(platform.lower(), adaptations["youtube"])
    
    def _generate_error_response(self, error_message: str) -> str:
        """Generate structured error response."""
        
        return json.dumps({
            "error": True,
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "fallback_guidance": {
                "basic_structure": "Hook → Content → Call-to-Action",
                "timing": "Keep introduction under 10% of total duration",
                "engagement": "Include interactive elements throughout",
                "quality": "Prioritize audio quality over video quality"
            }
        }, indent=2)
    
    def _get_style_elements(self, style: str) -> List[str]:
        """Get style-specific elements."""
        style_elements = {
            "professional": ["Clean backgrounds", "Consistent branding", "Clear audio", "Steady shots"],
            "casual": ["Natural lighting", "Authentic feel", "Conversational tone", "Behind-the-scenes"],
            "creative": ["Dynamic shots", "Creative transitions", "Unique angles", "Artistic elements"],
            "minimal": ["Simple backgrounds", "Clean compositions", "Focus on content", "Uncluttered"]
        }
        return style_elements.get(style.lower(), style_elements["professional"])
    
    def _generate_unique_angle(self, topic: str, platform: str, style: str) -> str:
        """Generate unique angle for the video."""
        return f"Unique perspective on {topic} tailored for {platform} audience with {style} approach"
    
    def _suggest_visual_theme(self, style: str, topic: str) -> str:
        """Suggest visual theme for the video."""
        return f"{style.title()} visual approach focusing on {topic} with consistent color scheme and branding"
    
    def _identify_target_emotions(self, video_type: str, topic: str) -> List[str]:
        """Identify target emotions for the video."""
        emotion_map = {
            "educational": ["Curiosity", "Confidence", "Achievement"],
            "entertainment": ["Joy", "Surprise", "Amusement"],
            "promotional": ["Trust", "Excitement", "Desire"],
            "behind_the_scenes": ["Connection", "Authenticity", "Appreciation"]
        }
        return emotion_map.get(video_type, emotion_map["educational"])
    
    def _get_hook_platform_notes(self, platform: str) -> List[str]:
        """Get platform-specific hook notes."""
        notes = {
            "tiktok": ["Must grab attention within 3 seconds", "Use trending formats", "Visual impact crucial"],
            "youtube": ["Thumbnail and title work together", "Promise clear value", "Create curiosity gap"],
            "instagram": ["Visual first impression matters", "Story integration important", "Mobile optimization key"],
            "linkedin": ["Professional value proposition", "Industry relevance", "Thought leadership angle"]
        }
        return notes.get(platform.lower(), notes["youtube"])
    
    def _get_main_content_structure(self, topic: str, duration_seconds: int) -> List[str]:
        """Get main content structure suggestions."""
        if duration_seconds <= 60:
            return ["One key point with example", "Quick demonstration", "Clear takeaway"]
        elif duration_seconds <= 300:
            return ["3-5 key points", "Examples for each point", "Interactive elements", "Visual demonstrations"]
        else:
            return ["Detailed breakdown of topic", "Multiple examples and case studies", "Step-by-step processes", "Q&A or interaction segments"]
    
    def _get_transition_suggestions(self, platform: str, style: str) -> List[str]:
        """Get transition suggestions for video."""
        return [
            "Visual transitions between points",
            "Audio cues for section changes",
            "Graphics overlays for emphasis",
            "Smooth camera movements"
        ]
    
    def _identify_engagement_moments(self, duration_seconds: int) -> List[str]:
        """Identify key engagement moments in the video."""
        moments = ["Strong opening hook"]
        
        if duration_seconds > 30:
            moments.append("Mid-video interaction point")
        if duration_seconds > 60:
            moments.append("Quarter-way engagement check")
            moments.append("Three-quarter engagement boost")
        
        moments.append("Strong call-to-action at end")
        return moments
    
    def _calculate_total_shots(self, duration_seconds: int) -> str:
        """Calculate total number of shots needed."""
        base_shots = max(5, duration_seconds // 15)  # One shot per 15 seconds minimum
        return f"{base_shots}-{base_shots * 2} shots recommended"
    
    def _suggest_filming_order(self) -> List[str]:
        """Suggest optimal filming order."""
        return [
            "Set up all equipment and lighting",
            "Record all talking head segments first",
            "Capture B-roll and demonstration footage",
            "Record any special effects or graphics shots",
            "Get backup takes of key segments"
        ]
    
    def _get_equipment_recommendations(self, style: str, platform: str) -> Dict[str, List[str]]:
        """Get equipment recommendations."""
        return {
            "camera": ["Smartphone with good camera", "DSLR/Mirrorless", "Webcam (for basic content)"],
            "audio": ["Lavalier microphone", "Shotgun microphone", "Audio recorder"],
            "lighting": ["Natural window light", "LED panel lights", "Ring light"],
            "stabilization": ["Tripod", "Gimbal stabilizer", "Phone mount"]
        }
    
    def _get_lighting_recommendations(self, style: str) -> List[str]:
        """Get lighting recommendations."""
        return [
            "Soft, even lighting on subject",
            "Avoid harsh shadows",
            "Consider background lighting",
            "Test lighting before full recording"
        ]
    
    def _get_audio_requirements(self, platform: str) -> List[str]:
        """Get audio requirements for platform."""
        return [
            "Clear, intelligible speech",
            "Minimal background noise",
            "Consistent audio levels",
            "Platform-appropriate music (if any)"
        ]
    
    def _get_platform_editing_specs(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific editing specifications."""
        specs = {
            "youtube": {
                "pacing": "Moderate, allow for comprehension",
                "graphics": "Professional overlays and lower thirds",
                "music": "Royalty-free background music optional",
                "captions": "Recommended for accessibility"
            },
            "tiktok": {
                "pacing": "Fast, dynamic editing",
                "graphics": "Use platform native effects",
                "music": "Trending sounds preferred",
                "captions": "Auto-captions available"
            },
            "instagram": {
                "pacing": "Medium, optimized for mobile viewing",
                "graphics": "Brand-consistent visual elements",
                "music": "Licensed music through platform",
                "captions": "Essential for silent viewing"
            }
        }
        return specs.get(platform.lower(), specs["youtube"])
    
    def _get_export_settings(self, platform: str) -> Dict[str, str]:
        """Get export settings for platform."""
        settings = {
            "youtube": {
                "format": "MP4",
                "codec": "H.264",
                "bitrate": "8-12 Mbps for 1080p",
                "audio": "AAC, 128 kbps"
            },
            "tiktok": {
                "format": "MP4",
                "codec": "H.264",
                "bitrate": "6-8 Mbps",
                "audio": "AAC, 128 kbps"
            },
            "instagram": {
                "format": "MP4",
                "codec": "H.264",
                "bitrate": "6-8 Mbps",
                "audio": "AAC, 128 kbps"
            }
        }
        return settings.get(platform.lower(), settings["youtube"])
    
    def _get_platform_engagement_tactics(self, platform: str) -> List[str]:
        """Get platform-specific engagement tactics."""
        tactics = {
            "youtube": [
                "Ask viewers to subscribe and ring the bell",
                "Use end screens and cards effectively",
                "Respond to comments with questions",
                "Create playlists for binge-watching"
            ],
            "tiktok": [
                "Use trending hashtags and sounds",
                "Encourage duets and stitches",
                "Reply to comments with videos",
                "Post consistently for algorithm favor"
            ],
            "instagram": [
                "Use Instagram Stories for behind-the-scenes",
                "Create polls and questions in Stories",
                "Use relevant hashtags strategically",
                "Cross-post to feed and Stories"
            ],
            "linkedin": [
                "Ask professional questions in comments",
                "Share in relevant LinkedIn groups",
                "Tag industry colleagues appropriately",
                "Follow up with additional insights"
            ]
        }
        return tactics.get(platform.lower(), tactics["youtube"])


class ScriptWritingTool(BaseTool):
    """Tool for writing compelling video scripts."""
    
    name: str = "script_writing_tool"
    description: str = "Write engaging video scripts with strong hooks and clear narratives"
    
    def _run(
        self,
        video_concept: str,
        platform: str,
        duration: str,
        style: str,
        target_audience: str,
        key_points: Union[str, List[str]] = ""
    ) -> str:
        """Write complete video script based on concept and requirements."""
        
        try:
            if isinstance(key_points, str):
                key_points = [point.strip() for point in key_points.split(',') if point.strip()]
            
            script_data = {
                "script_info": {
                    "video_concept": video_concept,
                    "platform": platform,
                    "duration": duration,
                    "style": style,
                    "target_audience": target_audience,
                    "key_points": key_points,
                    "created_at": datetime.now().isoformat()
                },
                "script_structure": self._create_script_structure(video_concept, platform, duration, style, target_audience, key_points),
                "delivery_notes": self._create_delivery_notes(platform, style),
                "visual_cues": self._create_visual_cues(platform, video_concept),
                "engagement_elements": self._create_engagement_elements(platform, target_audience),
                "revision_suggestions": self._create_revision_suggestions()
            }
            
            return json.dumps(script_data, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Script writing failed: {str(e)}")
            return self._generate_script_error_response(str(e))
    
    def _create_script_structure(self, video_concept: str, platform: str, duration: str, style: str, target_audience: str, key_points: List[str]) -> Dict[str, Any]:
        """Create detailed script structure with actual dialogue."""
        
        duration_seconds = self._parse_duration(duration)
        
        # Create platform-appropriate hook
        hook = self._write_hook(video_concept, platform, target_audience)
        
        # Create introduction
        introduction = self._write_introduction(video_concept, target_audience, style)
        
        # Create main content sections
        main_content = self._write_main_content(video_concept, key_points, duration_seconds, platform)
        
        # Create conclusion with CTA
        conclusion = self._write_conclusion(video_concept, platform, target_audience)
        
        return {
            "full_script": {
                "hook": {
                    "text": hook,
                    "delivery_time": "0-5 seconds",
                    "tone": "Energetic and attention-grabbing",
                    "visual_notes": "Close-up shot, direct eye contact"
                },
                "introduction": {
                    "text": introduction,
                    "delivery_time": "5-15 seconds",
                    "tone": "Welcoming and professional",
                    "visual_notes": "Medium shot, confident posture"
                },
                "main_content": main_content,
                "conclusion": {
                    "text": conclusion,
                    "delivery_time": f"{duration_seconds-15}-{duration_seconds} seconds",
                    "tone": "Confident and motivating",
                    "visual_notes": "Return to close-up, strong eye contact"
                }
            },
            "estimated_word_count": self._estimate_word_count(duration_seconds),
            "pacing_notes": self._get_pacing_notes(platform, duration_seconds),
            "alternative_versions": self._create_alternative_versions(video_concept, platform)
        }
    
    def _write_hook(self, video_concept: str, platform: str, target_audience: str) -> str:
        """Write compelling hook based on concept and platform."""
        
        hook_templates = {
            "question": f"Did you know that most people get {video_concept.split()[0]} completely wrong?",
            "stat": f"Here's a shocking fact about {video_concept.split()[0]} that will change how you think about it.",
            "story": f"Last week, something happened that completely changed my perspective on {video_concept.split()[0]}.",
            "problem": f"If you're struggling with {video_concept.split()[0]}, this video will solve your biggest challenge.",
            "controversial": f"I'm about to share an unpopular opinion about {video_concept.split()[0]} that might upset some people."
        }
        
        # Select hook type based on platform
        if platform.lower() == "tiktok":
            return hook_templates["stat"]  # TikTok loves quick facts
        elif platform.lower() == "linkedin":
            return hook_templates["problem"]  # LinkedIn focuses on solutions
        elif platform.lower() == "youtube":
            return hook_templates["question"]  # YouTube likes curiosity
        else:
            return hook_templates["story"]  # Stories work well universally
    
    def _write_introduction(self, video_concept: str, target_audience: str, style: str) -> str:
        """Write engaging introduction."""
        
        if style.lower() == "professional":
            return f"Hi everyone, I'm here to share some insights about {video_concept} that I think will be really valuable for {target_audience}. In the next few minutes, we'll cover the key points that will help you understand and apply this effectively."
        elif style.lower() == "casual":
            return f"Hey there! So I've been diving deep into {video_concept} lately, and I discovered some really cool stuff that I just had to share with you. Whether you're new to this or already familiar, I think you'll find these insights super helpful."
        elif style.lower() == "energetic":
            return f"What's up everyone! Today we're talking about {video_concept}, and trust me, this is going to be game-changing! I'm so excited to break this down for you because this information is going to help you level up immediately."
        else:
            return f"Welcome! Today we're exploring {video_concept}, and I'm going to share some practical insights that will make a real difference for {target_audience}. Let's dive right in."
    
    def _write_main_content(self, video_concept: str, key_points: List[str], duration_seconds: int, platform: str) -> Dict[str, Any]:
        """Write main content sections based on key points."""
        
        if not key_points:
            # Generate default key points
            key_points = [
                f"Understanding the basics of {video_concept}",
                f"Common mistakes people make with {video_concept}",
                f"Best practices for {video_concept}",
                f"How to get started with {video_concept}"
            ]
        
        # Calculate time per section
        available_time = duration_seconds - 20  # Minus hook, intro, and conclusion
        time_per_section = available_time // len(key_points)
        
        content_sections = {}
        current_time = 15  # Start after introduction
        
        for i, point in enumerate(key_points[:4]):  # Limit to 4 key points max
            section_name = f"point_{i+1}"
            
            content_sections[section_name] = {
                "key_point": point,
                "script_text": self._write_content_section(point, video_concept, platform),
                "delivery_time": f"{current_time}-{current_time + time_per_section} seconds",
                "visual_suggestions": self._get_visual_suggestions_for_point(point, platform),
                "transition": self._write_transition(i, len(key_points), point)
            }
            
            current_time += time_per_section
        
        return content_sections
    
    def _write_content_section(self, key_point: str, video_concept: str, platform: str) -> str:
        """Write content for a specific section."""
        
        # Base content structure
        content = f"Let's talk about {key_point.lower()}. "
        
        if platform.lower() == "tiktok":
            # TikTok needs quick, punchy content
            content += f"Here's what you need to know: {key_point.replace('Understanding', 'You need to understand').replace('Common mistakes', 'Stop making this mistake').replace('Best practices', 'Here's what works').replace('How to get started', 'Start by doing this')}. It's really that simple!"
        
        elif platform.lower() == "linkedin":
            # LinkedIn needs professional, detailed content
            content += f"From my experience in the industry, {key_point.lower()} is crucial for success. Here's the professional approach I recommend: focus on the fundamentals first, then build complexity. This strategy has worked consistently for the professionals I've worked with."
        
        elif platform.lower() == "youtube":
            # YouTube allows for more detailed explanation
            content += f"This is really important because {key_point.lower()} directly impacts your results. Let me break this down step by step so you can apply this immediately. First, you'll want to understand the foundation, then build on that knowledge systematically."
        
        else:
            # General approach for other platforms
            content += f"This is essential because {key_point.lower()} makes all the difference in your success. Here's exactly what you need to do to master this aspect effectively."
        
        return content
    
    def _write_conclusion(self, video_concept: str, platform: str, target_audience: str) -> str:
        """Write compelling conclusion with call-to-action."""
        
        # Summary component
        summary = f"So there you have it - the key insights about {video_concept} that will make a real difference for {target_audience}. "
        
        # Call-to-action based on platform
        if platform.lower() == "youtube":
            cta = "If this was helpful, please give it a thumbs up and subscribe for more content like this. What questions do you have about implementing these strategies? Drop them in the comments below!"
        elif platform.lower() == "tiktok":
            cta = "Follow for more tips like this! And comment below - what's your biggest challenge with this topic? I might make a video answering your question!"
        elif platform.lower() == "linkedin":
            cta = "I'd love to hear your thoughts on this topic. Share your experiences in the comments, and feel free to connect with me for more professional insights like this."
        elif platform.lower() == "instagram":
            cta = "Save this post for later and share it with someone who needs to see this! What's your experience with this? Let me know in the comments!"
        else:
            cta = "What do you think about these insights? Share your thoughts in the comments and let me know what topics you'd like me to cover next!"
        
        return summary + cta
    
    def _create_delivery_notes(self, platform: str, style: str) -> Dict[str, Any]:
        """Create delivery notes for the presenter."""
        
        general_notes = {
            "pace": "Speak clearly but with energy",
            "tone": f"{style} and engaging throughout",
            "eye_contact": "Look directly at camera, especially during key points",
            "gestures": "Use natural hand gestures to emphasize points",
            "energy": "Maintain consistent energy level throughout"
        }
        
        platform_specific = {
            "youtube": {
                "pacing": "Allow pauses for comprehension",
                "personality": "Show expertise while being approachable",
                "interaction": "Speak as if talking to a friend"
            },
            "tiktok": {
                "pacing": "Fast and dynamic, match the platform energy",
                "personality": "High energy, entertaining, trendy",
                "interaction": "Direct and immediate engagement"
            },
            "linkedin": {
                "pacing": "Professional but conversational",
                "personality": "Authoritative yet approachable",
                "interaction": "Professional networking tone"
            },
            "instagram": {
                "pacing": "Engaging and personable",
                "personality": "Authentic and relatable",
                "interaction": "Community-focused approach"
            }
        }
        
        return {
            "general_delivery": general_notes,
            "platform_specific": platform_specific.get(platform.lower(), platform_specific["youtube"]),
            "practice_tips": [
                "Read through script multiple times before recording",
                "Practice key transitions and emphasis points",
                "Time yourself to ensure proper pacing",
                "Record practice runs to check delivery"
            ]
        }
    
    def _create_visual_cues(self, platform: str, video_concept: str) -> List[Dict[str, str]]:
        """Create visual cues and B-roll suggestions."""
        
        return [
            {
                "timing": "During hook",
                "visual": "Close-up shot with strong eye contact",
                "b_roll": f"Quick montage related to {video_concept}"
            },
            {
                "timing": "During main points",
                "visual": "Mix of talking head and demonstration shots",
                "b_roll": "Relevant examples and demonstrations"
            },
            {
                "timing": "During transitions",
                "visual": "Graphics or text overlays",
                "b_roll": "Quick visual breaks between sections"
            },
            {
                "timing": "During conclusion",
                "visual": "Return to close-up for personal connection",
                "b_roll": "Summary graphics or next video teaser"
            }
        ]
    
    def _create_engagement_elements(self, platform: str, target_audience: str) -> Dict[str, List[str]]:
        """Create engagement elements throughout the script."""
        
        return {
            "questions_to_audience": [
                f"Have you experienced this challenge with {target_audience}?",
                "What's been your biggest struggle in this area?",
                "Which tip are you most excited to try?",
                "What questions do you have about this topic?"
            ],
            "interactive_moments": [
                "Pause here for audience to think",
                "Ask viewers to comment their answer",
                "Encourage sharing personal experiences",
                "Request likes if content is helpful"
            ],
            "platform_specific_engagement": self._get_platform_engagement_elements(platform)
        }
    
    def _create_revision_suggestions(self) -> List[str]:
        """Create suggestions for script revision and improvement."""
        
        return [
            "Read script aloud to check natural flow",
            "Ensure each section has a clear purpose",
            "Verify timing aligns with planned video length",
            "Check that language matches target audience level",
            "Confirm call-to-action is clear and compelling",
            "Review for platform-specific optimization opportunities",
            "Test hook effectiveness with sample audience",
            "Ensure key points are memorable and actionable"
        ]
    
    # Helper methods
    
    def _parse_duration(self, duration: str) -> int:
        """Parse duration string to seconds."""
        duration = duration.lower().strip()
        
        if "min" in duration:
            minutes = int(duration.split("min")[0].strip())
            return minutes * 60
        elif "sec" in duration:
            return int(duration.split("sec")[0].strip())
        elif ":" in duration:
            parts = duration.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        else:
            try:
                return int(duration)
            except:
                return 60
    
    def _estimate_word_count(self, duration_seconds: int) -> Dict[str, int]:
        """Estimate word count based on duration."""
        # Average speaking pace: 150-160 words per minute
        words_per_minute = 155
        total_words = int((duration_seconds / 60) * words_per_minute)
        
        return {
            "total_estimated_words": total_words,
            "words_per_minute": words_per_minute,
            "speaking_pace": "Average conversational pace"
        }
    
    def _get_pacing_notes(self, platform: str, duration_seconds: int) -> List[str]:
        """Get pacing notes for the platform and duration."""
        
        base_notes = [
            "Vary speaking pace to maintain interest",
            "Pause briefly after key points for emphasis",
            "Speed up slightly during transitions"
        ]
        
        if platform.lower() == "tiktok":
            base_notes.append("Maintain high energy throughout short duration")
        elif duration_seconds > 300:
            base_notes.append("Include natural breaks for longer content")
        
        return base_notes
    
    def _create_alternative_versions(self, video_concept: str, platform: str) -> Dict[str, str]:
        """Create alternative script versions."""
        
        return {
            "shorter_version": f"Condensed version focusing on top 2-3 points about {video_concept}",
            "longer_version": f"Extended version with more examples and detailed explanations of {video_concept}",
            "different_angle": f"Alternative approach to {video_concept} from different perspective",
            "series_potential": f"This topic could be expanded into a series covering different aspects of {video_concept}"
        }
    
    def _get_visual_suggestions_for_point(self, point: str, platform: str) -> List[str]:
        """Get visual suggestions for specific content points."""
        
        suggestions = [
            f"Show examples related to: {point}",
            "Use graphics to illustrate key concepts",
            "Include demonstrations where applicable"
        ]
        
        if platform.lower() in ["instagram", "tiktok"]:
            suggestions.append("Ensure visuals work well on mobile screens")
        
        return suggestions
    
    def _write_transition(self, current_index: int, total_points: int, current_point: str) -> str:
        """Write smooth transitions between points."""
        
        if current_index == 0:
            return "Now, let's dive into the first key point..."
        elif current_index == total_points - 1:
            return "Finally, and this is really important..."
        else:
            transitions = [
                "Next up...",
                "Here's another crucial aspect...",
                "Building on that...",
                "Now, here's where it gets interesting..."
            ]
            return transitions[current_index % len(transitions)]
    
    def _get_platform_engagement_elements(self, platform: str) -> List[str]:
        """Get platform-specific engagement elements."""
        
        elements = {
            "youtube": [
                "Ask viewers to subscribe and ring notification bell",
                "Encourage comments with specific questions",
                "Mention related videos or playlists",
                "Use end screens effectively"
            ],
            "tiktok": [
                "Use trending hashtags in caption",
                "Encourage duets or stitches",
                "Ask viewers to follow for more content",
                "Create content that invites response videos"
            ],
            "instagram": [
                "Ask viewers to save the post",
                "Encourage sharing to stories",
                "Use interactive story features",
                "Cross-promote in caption and comments"
            ],
            "linkedin": [
                "Ask for professional opinions in comments",
                "Encourage sharing with professional network",
                "Tag relevant industry connections",
                "Invite discussion about industry applications"
            ]
        }
        
        return elements.get(platform.lower(), elements["youtube"])
    
    def _generate_script_error_response(self, error_message: str) -> str:
        """Generate structured error response for script writing."""
        
        return json.dumps({
            "error": True,
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "fallback_structure": {
                "basic_script_format": {
                    "hook": "Attention-grabbing opening (0-5 seconds)",
                    "introduction": "Brief introduction and preview (5-15 seconds)",
                    "main_content": "Key points with examples (majority of video)",
                    "conclusion": "Summary and call-to-action (last 10-15 seconds)"
                },
                "general_tips": [
                    "Write conversationally, as if speaking to a friend",
                    "Include pauses and natural speech patterns",
                    "End sentences with clear punctuation for pacing",
                    "Practice reading aloud before recording"
                ]
            }
        }, indent=2)