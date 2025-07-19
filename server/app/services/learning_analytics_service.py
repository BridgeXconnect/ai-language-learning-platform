"""
Learning Analytics Service for AI Language Learning Platform
Implements analytics dashboard, progress tracking, and performance insights for AI Tutor Agent.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

@dataclass
class LearningMetrics:
    """Learning performance metrics for a user."""
    user_id: int
    total_study_time: float  # hours
    lessons_completed: int
    assessments_taken: int
    average_score: float
    progress_percentage: float
    learning_streak: int  # consecutive days
    last_activity: datetime
    preferred_learning_style: str
    difficulty_level: str

@dataclass
class CourseAnalytics:
    """Analytics for a specific course."""
    course_id: int
    total_enrollments: int
    completion_rate: float
    average_completion_time: float  # days
    average_score: float
    difficulty_distribution: Dict[str, int]
    popular_modules: List[str]
    dropoff_points: List[str]

@dataclass
class SystemAnalytics:
    """System-wide learning analytics."""
    total_users: int
    active_users: int
    total_courses: int
    total_lessons: int
    average_session_duration: float
    peak_usage_hours: List[int]
    popular_content: List[str]
    system_performance: Dict[str, float]

class LearningAnalyticsService:
    """Service for comprehensive learning analytics and insights."""
    
    def __init__(self):
        self.user_metrics: Dict[int, LearningMetrics] = {}
        self.course_analytics: Dict[int, CourseAnalytics] = {}
        self.system_analytics: Optional[SystemAnalytics] = None
        self.learning_patterns: Dict[str, Any] = {}
        self.recommendation_engine: Dict[str, Any] = {}
        
        logger.info("LearningAnalyticsService initialized")
    
    async def track_user_activity(self, user_id: int, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track user learning activity and update metrics."""
        logger.info(f"Tracking activity for user {user_id}")
        
        # Initialize user metrics if not exists
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = LearningMetrics(
                user_id=user_id,
                total_study_time=0.0,
                lessons_completed=0,
                assessments_taken=0,
                average_score=0.0,
                progress_percentage=0.0,
                learning_streak=0,
                last_activity=datetime.now(),
                preferred_learning_style="visual",
                difficulty_level="intermediate"
            )
        
        metrics = self.user_metrics[user_id]
        
        # Update metrics based on activity
        activity_type = activity_data.get("type")
        
        if activity_type == "lesson_completed":
            metrics.lessons_completed += 1
            metrics.total_study_time += activity_data.get("duration", 0) / 3600  # Convert to hours
            metrics.progress_percentage = min(100.0, metrics.progress_percentage + activity_data.get("progress_increment", 0))
        
        elif activity_type == "assessment_completed":
            metrics.assessments_taken += 1
            score = activity_data.get("score", 0)
            
            # Update average score
            if metrics.assessments_taken == 1:
                metrics.average_score = score
            else:
                metrics.average_score = ((metrics.average_score * (metrics.assessments_taken - 1)) + score) / metrics.assessments_taken
        
        elif activity_type == "learning_style_preference":
            metrics.preferred_learning_style = activity_data.get("learning_style", metrics.preferred_learning_style)
        
        elif activity_type == "difficulty_adjustment":
            metrics.difficulty_level = activity_data.get("difficulty", metrics.difficulty_level)
        
        # Update learning streak
        current_time = datetime.now()
        time_diff = current_time - metrics.last_activity
        
        if time_diff.days <= 1:  # Activity within 24 hours
            metrics.learning_streak += 1
        else:
            metrics.learning_streak = 1
        
        metrics.last_activity = current_time
        
        # Generate insights
        insights = await self._generate_user_insights(user_id, metrics)
        
        return {
            "user_id": user_id,
            "metrics_updated": True,
            "current_metrics": {
                "total_study_time": metrics.total_study_time,
                "lessons_completed": metrics.lessons_completed,
                "assessments_taken": metrics.assessments_taken,
                "average_score": metrics.average_score,
                "progress_percentage": metrics.progress_percentage,
                "learning_streak": metrics.learning_streak
            },
            "insights": insights
        }
    
    async def _generate_user_insights(self, user_id: int, metrics: LearningMetrics) -> Dict[str, Any]:
        """Generate personalized insights for a user."""
        insights = {
            "performance_trend": "improving",
            "recommended_actions": [],
            "learning_patterns": {},
            "achievements": []
        }
        
        # Analyze performance trend
        if metrics.average_score > 80:
            insights["performance_trend"] = "excellent"
        elif metrics.average_score > 70:
            insights["performance_trend"] = "good"
        elif metrics.average_score > 60:
            insights["performance_trend"] = "improving"
        else:
            insights["performance_trend"] = "needs_improvement"
        
        # Generate recommendations
        if metrics.learning_streak < 3:
            insights["recommended_actions"].append("Try to maintain a daily learning routine")
        
        if metrics.average_score < 70:
            insights["recommended_actions"].append("Review previous lessons and practice more")
        
        if metrics.progress_percentage < 50:
            insights["recommended_actions"].append("Focus on completing more lessons to stay on track")
        
        # Identify learning patterns
        insights["learning_patterns"] = {
            "preferred_style": metrics.preferred_learning_style,
            "optimal_difficulty": metrics.difficulty_level,
            "study_frequency": "daily" if metrics.learning_streak > 7 else "occasional"
        }
        
        # Track achievements
        if metrics.learning_streak >= 7:
            insights["achievements"].append("7-day learning streak")
        if metrics.lessons_completed >= 10:
            insights["achievements"].append("10 lessons completed")
        if metrics.average_score >= 85:
            insights["achievements"].append("High performer")
        
        return insights
    
    async def analyze_course_performance(self, course_id: int, course_data: Dict[str, Any]) -> CourseAnalytics:
        """Analyze performance metrics for a specific course."""
        logger.info(f"Analyzing course performance for course {course_id}")
        
        # Simulate course analytics calculation
        await asyncio.sleep(1)
        
        analytics = CourseAnalytics(
            course_id=course_id,
            total_enrollments=course_data.get("enrollments", 0),
            completion_rate=course_data.get("completion_rate", 0.75),
            average_completion_time=course_data.get("avg_completion_days", 30),
            average_score=course_data.get("avg_score", 78.5),
            difficulty_distribution={
                "beginner": course_data.get("beginner_count", 25),
                "intermediate": course_data.get("intermediate_count", 45),
                "advanced": course_data.get("advanced_count", 30)
            },
            popular_modules=course_data.get("popular_modules", ["Module 1", "Module 3", "Module 2"]),
            dropoff_points=course_data.get("dropoff_points", ["Lesson 5", "Assessment 2"])
        )
        
        self.course_analytics[course_id] = analytics
        return analytics
    
    async def generate_system_analytics(self) -> SystemAnalytics:
        """Generate comprehensive system-wide analytics."""
        logger.info("Generating system-wide analytics")
        
        # Calculate system metrics
        total_users = len(self.user_metrics)
        active_users = len([u for u in self.user_metrics.values() 
                          if (datetime.now() - u.last_activity).days <= 7])
        
        total_courses = len(self.course_analytics)
        total_lessons = sum(analytics.total_enrollments for analytics in self.course_analytics.values())
        
        # Calculate average session duration
        session_durations = [metrics.total_study_time for metrics in self.user_metrics.values()]
        avg_session_duration = statistics.mean(session_durations) if session_durations else 0
        
        # Determine peak usage hours (simulated)
        peak_usage_hours = [9, 10, 14, 15, 19, 20]  # Morning and evening peaks
        
        # Identify popular content
        popular_content = []
        for analytics in self.course_analytics.values():
            popular_content.extend(analytics.popular_modules[:2])
        
        # System performance metrics
        system_performance = {
            "response_time": 120,  # ms
            "uptime": 99.9,  # percentage
            "error_rate": 0.1,  # percentage
            "concurrent_users": active_users
        }
        
        self.system_analytics = SystemAnalytics(
            total_users=total_users,
            active_users=active_users,
            total_courses=total_courses,
            total_lessons=total_lessons,
            average_session_duration=avg_session_duration,
            peak_usage_hours=peak_usage_hours,
            popular_content=popular_content[:5],
            system_performance=system_performance
        )
        
        return self.system_analytics
    
    async def generate_learning_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Generate personalized learning recommendations."""
        logger.info(f"Generating recommendations for user {user_id}")
        
        if user_id not in self.user_metrics:
            return {"error": "User not found"}
        
        metrics = self.user_metrics[user_id]
        
        # Analyze learning patterns
        patterns = await self._analyze_learning_patterns(user_id)
        
        # Generate recommendations based on patterns and performance
        recommendations = []
        
        # Performance-based recommendations
        if metrics.average_score < 70:
            recommendations.append({
                "type": "practice",
                "title": "Focus on Practice",
                "description": "Your scores indicate you need more practice. Try reviewing previous lessons.",
                "priority": "high"
            })
        
        if metrics.learning_streak < 3:
            recommendations.append({
                "type": "consistency",
                "title": "Build Learning Habit",
                "description": "Try to study daily to build a consistent learning habit.",
                "priority": "medium"
            })
        
        # Content-based recommendations
        if metrics.preferred_learning_style == "visual":
            recommendations.append({
                "type": "content",
                "title": "Visual Learning Resources",
                "description": "Explore our video lessons and interactive diagrams.",
                "priority": "medium"
            })
        
        # Difficulty-based recommendations
        if metrics.difficulty_level == "beginner" and metrics.average_score > 80:
            recommendations.append({
                "type": "progression",
                "title": "Ready for Intermediate",
                "description": "You're doing great! Consider moving to intermediate level.",
                "priority": "low"
            })
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "learning_patterns": patterns,
            "next_best_action": recommendations[0] if recommendations else None
        }
    
    async def _analyze_learning_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze learning patterns for a user."""
        metrics = self.user_metrics[user_id]
        
        patterns = {
            "study_frequency": "daily" if metrics.learning_streak > 7 else "occasional",
            "preferred_time": "evening",  # Could be calculated from actual data
            "learning_style": metrics.preferred_learning_style,
            "difficulty_preference": metrics.difficulty_level,
            "performance_trend": "improving" if metrics.average_score > 75 else "stable",
            "engagement_level": "high" if metrics.learning_streak > 5 else "moderate"
        }
        
        return patterns
    
    async def generate_progress_report(self, user_id: int, timeframe: str = "month") -> Dict[str, Any]:
        """Generate detailed progress report for a user."""
        logger.info(f"Generating progress report for user {user_id}")
        
        if user_id not in self.user_metrics:
            return {"error": "User not found"}
        
        metrics = self.user_metrics[user_id]
        
        # Calculate progress metrics
        progress_data = {
            "current_period": {
                "lessons_completed": metrics.lessons_completed,
                "study_time": metrics.total_study_time,
                "assessments_taken": metrics.assessments_taken,
                "average_score": metrics.average_score
            },
            "trends": {
                "progress_trend": "increasing",
                "score_trend": "stable",
                "engagement_trend": "improving"
            },
            "goals": {
                "next_milestone": "Complete 5 more lessons",
                "target_score": 85,
                "target_streak": 10
            },
            "achievements": []
        }
        
        # Add achievements
        if metrics.learning_streak >= 7:
            progress_data["achievements"].append("7-day learning streak")
        if metrics.lessons_completed >= 10:
            progress_data["achievements"].append("10 lessons completed")
        if metrics.average_score >= 80:
            progress_data["achievements"].append("High performer")
        
        return progress_data
    
    async def generate_analytics_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive analytics dashboard data."""
        logger.info("Generating analytics dashboard")
        
        # Ensure system analytics are up to date
        if not self.system_analytics:
            await self.generate_system_analytics()
        
        dashboard_data = {
            "overview": {
                "total_users": self.system_analytics.total_users,
                "active_users": self.system_analytics.active_users,
                "total_courses": self.system_analytics.total_courses,
                "total_lessons": self.system_analytics.total_lessons
            },
            "performance": {
                "average_session_duration": self.system_analytics.average_session_duration,
                "system_uptime": self.system_analytics.system_performance["uptime"],
                "response_time": self.system_analytics.system_performance["response_time"]
            },
            "user_engagement": {
                "peak_hours": self.system_analytics.peak_usage_hours,
                "popular_content": self.system_analytics.popular_content,
                "completion_rates": {}
            },
            "course_analytics": {}
        }
        
        # Add course-specific analytics
        for course_id, analytics in self.course_analytics.items():
            dashboard_data["course_analytics"][f"course_{course_id}"] = {
                "enrollments": analytics.total_enrollments,
                "completion_rate": analytics.completion_rate,
                "average_score": analytics.average_score,
                "popular_modules": analytics.popular_modules
            }
        
        # Add completion rates
        for course_id, analytics in self.course_analytics.items():
            dashboard_data["user_engagement"]["completion_rates"][f"course_{course_id}"] = analytics.completion_rate
        
        return dashboard_data
    
    async def predict_learning_outcomes(self, user_id: int) -> Dict[str, Any]:
        """Predict learning outcomes for a user."""
        logger.info(f"Predicting learning outcomes for user {user_id}")
        
        if user_id not in self.user_metrics:
            return {"error": "User not found"}
        
        metrics = self.user_metrics[user_id]
        
        # Simple prediction model based on current metrics
        current_score = metrics.average_score
        study_time = metrics.total_study_time
        consistency = metrics.learning_streak
        
        # Predict final score
        predicted_score = min(100, current_score + (consistency * 2) + (study_time * 0.5))
        
        # Predict completion time
        remaining_progress = 100 - metrics.progress_percentage
        daily_progress = 5 if consistency > 3 else 2
        predicted_days = max(1, int(remaining_progress / daily_progress))
        
        # Predict success probability
        success_factors = [
            current_score / 100,  # Current performance
            min(consistency / 10, 1),  # Consistency
            min(study_time / 50, 1),  # Study time
            metrics.progress_percentage / 100  # Progress
        ]
        
        success_probability = statistics.mean(success_factors)
        
        return {
            "user_id": user_id,
            "predictions": {
                "predicted_final_score": round(predicted_score, 1),
                "predicted_completion_days": predicted_days,
                "success_probability": round(success_probability * 100, 1),
                "confidence_level": "high" if success_probability > 0.8 else "medium"
            },
            "recommendations": {
                "focus_areas": ["Practice more", "Maintain consistency"] if success_probability < 0.7 else ["Keep up the good work"],
                "study_schedule": "Daily" if consistency < 5 else "Current schedule is working well"
            }
        }
    
    async def generate_insights_report(self) -> Dict[str, Any]:
        """Generate comprehensive insights report."""
        logger.info("Generating insights report")
        
        # Calculate various insights
        insights = {
            "user_behavior": {},
            "content_performance": {},
            "system_insights": {},
            "recommendations": []
        }
        
        # User behavior insights
        if self.user_metrics:
            avg_study_time = statistics.mean([m.total_study_time for m in self.user_metrics.values()])
            avg_score = statistics.mean([m.average_score for m in self.user_metrics.values()])
            avg_streak = statistics.mean([m.learning_streak for m in self.user_metrics.values()])
            
            insights["user_behavior"] = {
                "average_study_time_hours": round(avg_study_time, 2),
                "average_score": round(avg_score, 1),
                "average_learning_streak": round(avg_streak, 1),
                "most_common_learning_style": self._get_most_common_learning_style(),
                "engagement_trend": "increasing" if avg_streak > 3 else "stable"
            }
        
        # Content performance insights
        if self.course_analytics:
            avg_completion_rate = statistics.mean([a.completion_rate for a in self.course_analytics.values()])
            avg_course_score = statistics.mean([a.average_score for a in self.course_analytics.values()])
            
            insights["content_performance"] = {
                "average_completion_rate": round(avg_completion_rate * 100, 1),
                "average_course_score": round(avg_course_score, 1),
                "most_popular_course": self._get_most_popular_course(),
                "content_effectiveness": "high" if avg_completion_rate > 0.7 else "moderate"
            }
        
        # System insights
        if self.system_analytics:
            insights["system_insights"] = {
                "user_retention_rate": round((self.system_analytics.active_users / self.system_analytics.total_users) * 100, 1),
                "peak_usage_period": f"{self.system_analytics.peak_usage_hours[0]}:00 - {self.system_analytics.peak_usage_hours[-1]}:00",
                "system_reliability": "excellent" if self.system_analytics.system_performance["uptime"] > 99.5 else "good"
            }
        
        # Generate recommendations
        insights["recommendations"] = [
            "Consider adding more interactive content to improve engagement",
            "Implement gamification features to increase learning streaks",
            "Add personalized learning paths based on user preferences",
            "Optimize content delivery during peak usage hours"
        ]
        
        return insights
    
    def _get_most_common_learning_style(self) -> str:
        """Get the most common learning style among users."""
        styles = [m.preferred_learning_style for m in self.user_metrics.values()]
        if styles:
            return Counter(styles).most_common(1)[0][0]
        return "visual"
    
    def _get_most_popular_course(self) -> str:
        """Get the most popular course based on enrollments."""
        if self.course_analytics:
            return max(self.course_analytics.items(), 
                      key=lambda x: x[1].total_enrollments)[1].popular_modules[0]
        return "No courses available"
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get a summary of all analytics data."""
        return {
            "total_users_tracked": len(self.user_metrics),
            "total_courses_analyzed": len(self.course_analytics),
            "system_analytics_available": self.system_analytics is not None,
            "last_updated": datetime.now().isoformat()
        }
    
    async def cleanup(self):
        """Clean up resources."""
        logger.info("LearningAnalyticsService cleanup completed")

# Global instance
learning_analytics = LearningAnalyticsService() 