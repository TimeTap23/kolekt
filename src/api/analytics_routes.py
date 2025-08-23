"""
Enhanced Analytics API Routes
Provides comprehensive analytics data with proper validation and error handling
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from src.services.authentication import get_current_user
from src.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)
analytics_router = APIRouter()

# Pydantic models for request/response validation
class AnalyticsRangeRequest(BaseModel):
    range_key: str = Field(..., description="Time range: 7d, 30d, 90d, 1y")
    user_id: Optional[str] = Field(None, description="Optional user ID filter")

class AnalyticsMetricsResponse(BaseModel):
    total_posts: int
    total_engagement: int
    avg_engagement_rate: float
    total_reach: int
    total_threadstorms: int
    total_characters: int
    total_api_calls: int
    most_used_tone: str
    conversion_rate: float
    churn_rate: float
    monthly_revenue: float

class ChartDataPoint(BaseModel):
    date: str
    value: float
    label: str

class AnalyticsChartResponse(BaseModel):
    engagement_over_time: List[ChartDataPoint]
    posts_by_platform: List[ChartDataPoint]
    content_performance: List[ChartDataPoint]
    user_growth: List[ChartDataPoint]

class InsightItem(BaseModel):
    icon: str
    title: str
    description: str
    impact: str
    confidence: float

class AnalyticsInsightsResponse(BaseModel):
    insights: List[InsightItem]
    recommendations: List[str]
    trends: List[str]

@analytics_router.get("/range/{range_key}")
async def get_analytics_range(
    range_key: str, 
    user_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive analytics data for specified time range
    
    Args:
        range_key: Time range (7d, 30d, 90d, 1y)
        user_id: Optional user ID filter
        current_user: Authenticated user
    
    Returns:
        Comprehensive analytics data with metrics, charts, and insights
    """
    try:
        # Validate range_key
        valid_ranges = ["7d", "30d", "90d", "1y"]
        if range_key not in valid_ranges:
            raise HTTPException(status_code=400, detail=f"Invalid range. Must be one of: {valid_ranges}")
        
        analytics_service = AnalyticsService()
        
        # Get analytics data based on range
        if range_key == "7d":
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        elif range_key == "30d":
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        elif range_key == "90d":
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
        
        # Get comprehensive metrics
        metrics = await analytics_service.get_comprehensive_metrics(
            user_id=user_id or current_user.get("user_id"),
            start_date=start_date,
            end_date=end_date
        )
        
        # Get chart data
        charts = await analytics_service.get_chart_data(
            user_id=user_id or current_user.get("user_id"),
            start_date=start_date,
            end_date=end_date
        )
        
        # Get insights
        insights = await analytics_service.get_insights(
            user_id=user_id or current_user.get("user_id"),
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "range": range_key,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "metrics": metrics,
            "charts": charts,
            "insights": insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics range error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load analytics data")

@analytics_router.get("/metrics/detailed")
async def get_detailed_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed metrics breakdown with performance indicators
    """
    try:
        analytics_service = AnalyticsService()
        
        detailed_metrics = await analytics_service.get_detailed_metrics(
            user_id=current_user.get("user_id")
        )
        
        return {
            "success": True,
            "metrics": detailed_metrics
        }
        
    except Exception as e:
        logger.error(f"Detailed metrics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load detailed metrics")

@analytics_router.get("/performance/trends")
async def get_performance_trends(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get performance trends and patterns
    """
    try:
        analytics_service = AnalyticsService()
        
        trends = await analytics_service.get_performance_trends(
            user_id=current_user.get("user_id")
        )
        
        return {
            "success": True,
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Performance trends error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load performance trends")

@analytics_router.get("/insights/ai-powered")
async def get_ai_insights(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get AI-powered insights and recommendations
    """
    try:
        analytics_service = AnalyticsService()
        
        ai_insights = await analytics_service.get_ai_insights(
            user_id=current_user.get("user_id")
        )
        
        return {
            "success": True,
            "insights": ai_insights
        }
        
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load AI insights")

@analytics_router.post("/track")
async def track_analytics_event(
    event_type: str,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Track analytics event with metadata
    """
    try:
        analytics_service = AnalyticsService()
        
        await analytics_service.track_event(
            user_id=current_user.get("user_id"),
            event_type=event_type,
            metadata=metadata or {}
        )
        
        return {"success": True, "event_tracked": event_type}
        
    except Exception as e:
        logger.error(f"Event tracking error: {e}")
        raise HTTPException(status_code=500, detail="Failed to track event")

@analytics_router.get("/export")
async def export_analytics_data(
    format: str = Query("json", description="Export format: json, csv"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Export analytics data in specified format
    """
    try:
        analytics_service = AnalyticsService()
        
        export_data = await analytics_service.export_data(
            user_id=current_user.get("user_id"),
            format=format
        )
        
        return {
            "success": True,
            "format": format,
            "data": export_data,
            "exported_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")


