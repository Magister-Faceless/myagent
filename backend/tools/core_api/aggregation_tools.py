"""
Aggregation and analysis tools for CORE API
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from collections import Counter

from deepagents.tools import tool

from .config import CORE_API_CONFIG, get_api_headers
from .utils import (
    make_api_request, 
    build_query_string,
    generate_filename
)

@tool(description="Aggregate CORE API search results by specified fields for trend analysis")
async def aggregate_works(
    query: str,
    aggregation_fields: List[str],
    date_range: Optional[Dict[str, str]] = None,
    require_full_text: bool = False,
    max_buckets: int = 100
) -> Dict[str, Any]:
    """
    Aggregate search results by specified fields for statistical analysis
    
    Args:
        query: Search query using CORE query language
        aggregation_fields: Fields to aggregate by (e.g., ['yearPublished', 'fieldOfStudy'])
        date_range: Dict with 'start_year' and 'end_year' keys
        require_full_text: Only include works with full text available
        max_buckets: Maximum number of buckets per aggregation
        
    Returns:
        dict: Aggregation results with statistics
        
    Supported aggregation fields:
        - yearPublished: Publication year
        - authors: Author names
        - documentType: Document type
        - publishedDate: Publication date
        - language: Language
        - publisher: Publisher
        - dataProvider: Data provider
        - fieldOfStudy: Field of study
    """
    try:
        # Validate aggregation fields
        valid_fields = [
            "yearPublished", "authors", "documentType", "publishedDate",
            "language", "publisher", "dataProvider", "fieldOfStudy"
        ]
        
        invalid_fields = [f for f in aggregation_fields if f not in valid_fields]
        if invalid_fields:
            return {
                "success": False,
                "error": f"Invalid aggregation fields: {invalid_fields}. Valid fields: {valid_fields}",
                "query": query
            }
        
        # Build complete query
        complete_query = build_query_string(
            base_query=query,
            date_range=date_range,
            require_full_text=require_full_text
        )
        
        # Prepare request
        url = f"{CORE_API_CONFIG['base_url']}/search/works/aggregate"
        headers = get_api_headers()
        
        request_data = {
            "q": complete_query,
            "aggregations": aggregation_fields
        }
        
        async with aiohttp.ClientSession() as session:
            response_data = await make_api_request(
                session=session,
                url=url,
                method="POST",
                json_data=request_data,
                headers=headers,
                timeout=CORE_API_CONFIG["timeout"]
            )
        
        # Process aggregation results
        aggregations = response_data.get("aggregations", {})
        processed_aggregations = {}
        
        for field, buckets in aggregations.items():
            if isinstance(buckets, list):
                # Sort buckets by count (descending) and limit
                sorted_buckets = sorted(buckets, key=lambda x: x.get("doc_count", 0), reverse=True)
                limited_buckets = sorted_buckets[:max_buckets]
                
                processed_aggregations[field] = {
                    "total_buckets": len(buckets),
                    "shown_buckets": len(limited_buckets),
                    "buckets": limited_buckets,
                    "top_values": [
                        {"value": bucket.get("key"), "count": bucket.get("doc_count", 0)}
                        for bucket in limited_buckets[:10]
                    ]
                }
        
        # Calculate summary statistics - use correct field name
        total_hits = response_data.get("total_hits", response_data.get("totalHits", 0))
        
        return {
            "success": True,
            "query": complete_query,
            "total_hits": total_hits,
            "aggregation_fields": aggregation_fields,
            "aggregations": processed_aggregations,
            "summary": {
                "most_common_values": {
                    field: agg["top_values"][:5] if agg["top_values"] else []
                    for field, agg in processed_aggregations.items()
                },
                "diversity_scores": {
                    field: len(agg["buckets"]) / max(agg["total_buckets"], 1)
                    for field, agg in processed_aggregations.items()
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "aggregation_fields": aggregation_fields
        }

@tool(description="Analyze publication trends over time for a research topic")
async def time_trend_analysis(
    query: str,
    start_year: int = 2010,
    end_year: Optional[int] = None,
    require_full_text: bool = False,
    include_predictions: bool = False
) -> Dict[str, Any]:
    """
    Analyze publication trends over time for a specific research topic
    
    Args:
        query: Search query using CORE query language
        start_year: Starting year for analysis
        end_year: Ending year for analysis (default: current year)
        require_full_text: Only include works with full text available
        include_predictions: Whether to include trend predictions
        
    Returns:
        dict: Trend analysis results with statistics and insights
    """
    try:
        from datetime import datetime
        
        if end_year is None:
            end_year = datetime.now().year
        
        # Validate year range
        if start_year >= end_year:
            return {
                "success": False,
                "error": f"Start year ({start_year}) must be less than end year ({end_year})",
                "query": query
            }
        
        # Get yearly aggregation
        date_range = {"start_year": str(start_year), "end_year": str(end_year)}
        
        aggregation_result = await aggregate_works(
            query=query,
            aggregation_fields=["yearPublished"],
            date_range=date_range,
            require_full_text=require_full_text
        )
        
        if not aggregation_result["success"]:
            return aggregation_result
        
        # Process yearly data
        year_buckets = aggregation_result["aggregations"]["yearPublished"]["buckets"]
        
        # Create complete year series (fill missing years with 0)
        year_data = {}
        for year in range(start_year, end_year + 1):
            year_data[year] = 0
        
        # Fill in actual data
        for bucket in year_buckets:
            year = int(bucket["key"])
            if start_year <= year <= end_year:
                year_data[year] = bucket["doc_count"]
        
        # Calculate trend statistics
        years = sorted(year_data.keys())
        counts = [year_data[year] for year in years]
        
        # Basic statistics
        total_publications = sum(counts)
        avg_per_year = total_publications / len(years) if years else 0
        max_year = years[counts.index(max(counts))] if counts and max(counts) > 0 else None
        min_year = years[counts.index(min(counts))] if counts else None
        
        # Growth rate calculation
        growth_rates = []
        for i in range(1, len(counts)):
            if counts[i-1] > 0:
                growth_rate = ((counts[i] - counts[i-1]) / counts[i-1]) * 100
                growth_rates.append(growth_rate)
        
        avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        
        # Trend direction
        if len(counts) >= 2:
            recent_trend = "increasing" if counts[-1] > counts[-2] else "decreasing" if counts[-1] < counts[-2] else "stable"
        else:
            recent_trend = "insufficient_data"
        
        # Peak analysis
        peak_years = []
        if len(counts) >= 3:
            for i in range(1, len(counts) - 1):
                if counts[i] > counts[i-1] and counts[i] > counts[i+1]:
                    peak_years.append(years[i])
        
        result = {
            "success": True,
            "query": query,
            "time_period": {"start_year": start_year, "end_year": end_year},
            "yearly_data": [{"year": year, "count": year_data[year]} for year in years],
            "statistics": {
                "total_publications": total_publications,
                "average_per_year": round(avg_per_year, 2),
                "peak_year": max_year,
                "peak_count": max(counts) if counts else 0,
                "lowest_year": min_year,
                "lowest_count": min(counts) if counts else 0,
                "average_growth_rate": round(avg_growth_rate, 2),
                "recent_trend": recent_trend
            },
            "insights": {
                "peak_years": peak_years,
                "growth_periods": _identify_growth_periods(years, counts),
                "decline_periods": _identify_decline_periods(years, counts),
                "stability_assessment": _assess_stability(counts)
            }
        }
        
        # Add predictions if requested
        if include_predictions and len(counts) >= 3:
            predictions = _simple_trend_prediction(years, counts, 3)
            result["predictions"] = predictions
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

def _identify_growth_periods(years: List[int], counts: List[int]) -> List[Dict[str, Any]]:
    """Identify periods of sustained growth"""
    growth_periods = []
    current_period = None
    
    for i in range(1, len(counts)):
        if counts[i] > counts[i-1]:
            if current_period is None:
                current_period = {"start_year": years[i-1], "start_count": counts[i-1]}
            current_period["end_year"] = years[i]
            current_period["end_count"] = counts[i]
        else:
            if current_period and (current_period["end_year"] - current_period["start_year"]) >= 2:
                growth_rate = ((current_period["end_count"] - current_period["start_count"]) / 
                              current_period["start_count"]) * 100 if current_period["start_count"] > 0 else 0
                current_period["growth_rate"] = round(growth_rate, 2)
                growth_periods.append(current_period)
            current_period = None
    
    # Check final period
    if current_period and (current_period["end_year"] - current_period["start_year"]) >= 2:
        growth_rate = ((current_period["end_count"] - current_period["start_count"]) / 
                      current_period["start_count"]) * 100 if current_period["start_count"] > 0 else 0
        current_period["growth_rate"] = round(growth_rate, 2)
        growth_periods.append(current_period)
    
    return growth_periods

def _identify_decline_periods(years: List[int], counts: List[int]) -> List[Dict[str, Any]]:
    """Identify periods of sustained decline"""
    decline_periods = []
    current_period = None
    
    for i in range(1, len(counts)):
        if counts[i] < counts[i-1]:
            if current_period is None:
                current_period = {"start_year": years[i-1], "start_count": counts[i-1]}
            current_period["end_year"] = years[i]
            current_period["end_count"] = counts[i]
        else:
            if current_period and (current_period["end_year"] - current_period["start_year"]) >= 2:
                decline_rate = ((current_period["start_count"] - current_period["end_count"]) / 
                               current_period["start_count"]) * 100 if current_period["start_count"] > 0 else 0
                current_period["decline_rate"] = round(decline_rate, 2)
                decline_periods.append(current_period)
            current_period = None
    
    # Check final period
    if current_period and (current_period["end_year"] - current_period["start_year"]) >= 2:
        decline_rate = ((current_period["start_count"] - current_period["end_count"]) / 
                       current_period["start_count"]) * 100 if current_period["start_count"] > 0 else 0
        current_period["decline_rate"] = round(decline_rate, 2)
        decline_periods.append(current_period)
    
    return decline_periods

def _assess_stability(counts: List[int]) -> Dict[str, Any]:
    """Assess the stability of publication trends"""
    if len(counts) < 3:
        return {"assessment": "insufficient_data"}
    
    # Calculate coefficient of variation
    mean_count = sum(counts) / len(counts)
    variance = sum((x - mean_count) ** 2 for x in counts) / len(counts)
    std_dev = variance ** 0.5
    cv = (std_dev / mean_count) * 100 if mean_count > 0 else 0
    
    # Stability assessment
    if cv < 20:
        stability = "very_stable"
    elif cv < 40:
        stability = "moderately_stable"
    elif cv < 60:
        stability = "somewhat_volatile"
    else:
        stability = "highly_volatile"
    
    return {
        "assessment": stability,
        "coefficient_of_variation": round(cv, 2),
        "mean_publications": round(mean_count, 2),
        "standard_deviation": round(std_dev, 2)
    }

def _simple_trend_prediction(years: List[int], counts: List[int], forecast_years: int) -> Dict[str, Any]:
    """Simple linear trend prediction"""
    # Use last 5 years for trend calculation
    recent_years = years[-5:]
    recent_counts = counts[-5:]
    
    if len(recent_years) < 2:
        return {"error": "Insufficient data for prediction"}
    
    # Simple linear regression
    n = len(recent_years)
    sum_x = sum(recent_years)
    sum_y = sum(recent_counts)
    sum_xy = sum(x * y for x, y in zip(recent_years, recent_counts))
    sum_x2 = sum(x * x for x in recent_years)
    
    # Calculate slope and intercept
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n
    
    # Generate predictions
    last_year = years[-1]
    predictions = []
    
    for i in range(1, forecast_years + 1):
        pred_year = last_year + i
        pred_count = max(0, round(slope * pred_year + intercept))  # Ensure non-negative
        predictions.append({"year": pred_year, "predicted_count": pred_count})
    
    return {
        "method": "linear_regression",
        "trend_slope": round(slope, 2),
        "predictions": predictions,
        "confidence": "low"  # Simple method has low confidence
    }
