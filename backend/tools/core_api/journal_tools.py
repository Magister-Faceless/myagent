"""
Journal and publication venue tools for CORE API
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional

from deepagents.tools import tool

from .config import CORE_API_CONFIG, get_api_headers
from .utils import make_api_request, clean_text

@tool(description="Search for journals and publication venues in CORE API")
async def search_journals(
    query: str,
    limit: int = 50,
    offset: int = 0,
    subjects: Optional[List[str]] = None,
    publisher: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for journals and publication venues
    
    Args:
        query: Search query for journal names or topics
        limit: Maximum number of results (default: 50)
        offset: Offset for pagination (default: 0)
        subjects: List of subject areas to filter by
        publisher: Publisher name to filter by
        
    Returns:
        dict: Journal search results with metadata
    """
    try:
        # Build query with filters
        query_parts = [query] if query else []
        
        if subjects:
            subject_filter = " OR ".join([f'subjects:"{subject}"' for subject in subjects])
            query_parts.append(f"({subject_filter})")
        
        if publisher:
            query_parts.append(f'publisher:"{publisher}"')
        
        complete_query = " AND ".join(query_parts) if query_parts else "*"
        
        # Prepare request
        url = f"{CORE_API_CONFIG['base_url']}/search/journals"
        params = {
            "q": complete_query,
            "limit": min(limit, 100),
            "offset": offset
        }
        
        headers = get_api_headers()
        
        async with aiohttp.ClientSession() as session:
            response_data = await make_api_request(
                session=session,
                url=url,
                method="GET",
                params=params,
                headers=headers,
                timeout=CORE_API_CONFIG["timeout"]
            )
        
        # Process results
        results = response_data.get("results", [])
        processed_results = []
        
        for journal in results:
            processed_journal = {
                "core_id": journal.get("id"),
                "title": clean_text(journal.get("title", ""), 200),
                "issn": journal.get("identifiers", {}).get("issn"),
                "eissn": journal.get("identifiers", {}).get("eissn"),
                "publisher": journal.get("publisher"),
                "subjects": journal.get("subjects", []),
                "language": journal.get("language"),
                "country": journal.get("country"),
                "homepage_url": journal.get("homepageUrl"),
                "oai_pmh_url": journal.get("oaiPmhUrl"),
                "article_count": journal.get("countByStatus", {}).get("total", 0),
                "open_access": journal.get("openAccess", False)
            }
            processed_results.append(processed_journal)
        
        return {
            "success": True,
            "query": complete_query,
            "total_hits": response_data.get("totalHits", len(results)),
            "results_count": len(processed_results),
            "offset": offset,
            "limit": limit,
            "results": processed_results,
            "has_more": response_data.get("totalHits", 0) > (offset + len(results))
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "results": []
        }

@tool(description="Get detailed information for a specific journal by ID or ISSN")
async def get_journal_by_id(
    identifier: str
) -> Dict[str, Any]:
    """
    Retrieve detailed information for a specific journal
    
    Args:
        identifier: Journal ID, ISSN, or eISSN (can use 'issn:' prefix)
        
    Returns:
        dict: Detailed journal information
    """
    try:
        # Clean identifier
        identifier = identifier.strip()
        
        # Prepare request
        url = f"{CORE_API_CONFIG['base_url']}/journals/{identifier}"
        headers = get_api_headers()
        
        async with aiohttp.ClientSession() as session:
            response_data = await make_api_request(
                session=session,
                url=url,
                method="GET",
                headers=headers,
                timeout=CORE_API_CONFIG["timeout"]
            )
        
        # Process journal data
        journal = response_data
        
        processed_journal = {
            "core_id": journal.get("id"),
            "title": clean_text(journal.get("title", ""), 300),
            "issn": journal.get("identifiers", {}).get("issn"),
            "eissn": journal.get("identifiers", {}).get("eissn"),
            "publisher": journal.get("publisher"),
            "subjects": journal.get("subjects", []),
            "language": journal.get("language"),
            "country": journal.get("country"),
            "homepage_url": journal.get("homepageUrl"),
            "oai_pmh_url": journal.get("oaiPmhUrl"),
            "open_access": journal.get("openAccess", False),
            "article_counts": journal.get("countByStatus", {}),
            "description": clean_text(journal.get("description", ""), 500),
            "keywords": journal.get("keywords", []),
            "editorial_board": journal.get("editorialBoard", []),
            "submission_guidelines": journal.get("submissionGuidelines"),
            "peer_review_policy": journal.get("peerReviewPolicy"),
            "publication_frequency": journal.get("publicationFrequency"),
            "first_publication_year": journal.get("firstPublicationYear"),
            "last_publication_year": journal.get("lastPublicationYear")
        }
        
        # Calculate additional metrics
        total_articles = processed_journal["article_counts"].get("total", 0)
        years_active = None
        if (processed_journal["first_publication_year"] and 
            processed_journal["last_publication_year"]):
            years_active = (processed_journal["last_publication_year"] - 
                           processed_journal["first_publication_year"] + 1)
        
        processed_journal["metrics"] = {
            "total_articles": total_articles,
            "years_active": years_active,
            "articles_per_year": (total_articles / years_active) if years_active and years_active > 0 else None,
            "subject_diversity": len(processed_journal["subjects"])
        }
        
        return {
            "success": True,
            "identifier": identifier,
            "journal": processed_journal
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "identifier": identifier
        }

@tool(description="Analyze top publication venues for a research topic")
async def analyze_top_venues_for_topic(
    query: str,
    limit: int = 20,
    require_full_text: bool = False,
    date_range: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Analyze top publication venues (publishers/journals) for a research topic
    
    Args:
        query: Research topic query
        limit: Number of top venues to analyze
        require_full_text: Only include works with full text
        date_range: Dict with 'start_year' and 'end_year' keys
        
    Returns:
        dict: Analysis of top venues with recommendations
    """
    try:
        from .aggregation_tools import aggregate_works
        
        # Get publisher aggregation
        publisher_agg = await aggregate_works(
            query=query,
            aggregation_fields=["publisher"],
            date_range=date_range,
            require_full_text=require_full_text,
            max_buckets=limit
        )
        
        if not publisher_agg["success"]:
            return publisher_agg
        
        # Get top publishers
        publisher_buckets = publisher_agg["aggregations"]["publisher"]["buckets"]
        top_publishers = [
            {
                "name": bucket["key"],
                "article_count": bucket["doc_count"],
                "percentage": round((bucket["doc_count"] / publisher_agg["total_hits"]) * 100, 2)
            }
            for bucket in publisher_buckets[:limit]
        ]
        
        # Analyze venue characteristics
        venue_analysis = []
        
        for publisher in top_publishers[:10]:  # Analyze top 10 in detail
            # Search for journals from this publisher
            journal_search = await search_journals(
                query="",
                publisher=publisher["name"],
                limit=10
            )
            
            if journal_search["success"]:
                journals = journal_search["results"]
                
                # Calculate publisher metrics
                total_journals = len(journals)
                open_access_journals = sum(1 for j in journals if j.get("open_access"))
                subject_areas = set()
                for journal in journals:
                    subject_areas.update(journal.get("subjects", []))
                
                venue_info = {
                    "publisher": publisher["name"],
                    "article_count": publisher["article_count"],
                    "market_share": publisher["percentage"],
                    "journal_count": total_journals,
                    "open_access_ratio": round((open_access_journals / total_journals) * 100, 2) if total_journals > 0 else 0,
                    "subject_diversity": len(subject_areas),
                    "main_subjects": list(subject_areas)[:5],
                    "sample_journals": [
                        {
                            "title": j["title"],
                            "issn": j["issn"],
                            "subjects": j["subjects"][:3]
                        }
                        for j in journals[:3]
                    ]
                }
                venue_analysis.append(venue_info)
            
            # Small delay to respect rate limits
            await asyncio.sleep(0.1)
        
        # Generate recommendations
        recommendations = _generate_venue_recommendations(venue_analysis, query)
        
        return {
            "success": True,
            "query": query,
            "total_articles_analyzed": publisher_agg["total_hits"],
            "top_publishers": top_publishers,
            "detailed_analysis": venue_analysis,
            "recommendations": recommendations,
            "summary": {
                "most_prolific_publisher": top_publishers[0]["name"] if top_publishers else None,
                "market_concentration": sum(p["percentage"] for p in top_publishers[:5]),
                "venue_diversity": len(top_publishers),
                "open_access_opportunities": sum(1 for v in venue_analysis if v.get("open_access_ratio", 0) > 50)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

def _generate_venue_recommendations(venue_analysis: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """Generate publication venue recommendations"""
    if not venue_analysis:
        return {"error": "No venue data available for recommendations"}
    
    # Categorize venues
    high_impact = [v for v in venue_analysis if v["market_share"] > 10]
    open_access = [v for v in venue_analysis if v.get("open_access_ratio", 0) > 70]
    diverse_subjects = [v for v in venue_analysis if v.get("subject_diversity", 0) > 5]
    
    recommendations = {
        "tier_1_high_impact": {
            "description": "Top-tier venues with high market share",
            "venues": [
                {
                    "publisher": v["publisher"],
                    "rationale": f"High market share ({v['market_share']}%) with {v['journal_count']} journals",
                    "sample_journals": v["sample_journals"]
                }
                for v in high_impact[:3]
            ]
        },
        "open_access_friendly": {
            "description": "Publishers with strong open access commitment",
            "venues": [
                {
                    "publisher": v["publisher"],
                    "rationale": f"{v['open_access_ratio']}% open access journals",
                    "sample_journals": v["sample_journals"]
                }
                for v in open_access[:3]
            ]
        },
        "interdisciplinary": {
            "description": "Publishers with diverse subject coverage",
            "venues": [
                {
                    "publisher": v["publisher"],
                    "rationale": f"Covers {v['subject_diversity']} subject areas",
                    "main_subjects": v["main_subjects"],
                    "sample_journals": v["sample_journals"]
                }
                for v in diverse_subjects[:3]
            ]
        }
    }
    
    # Overall strategy
    strategy = {
        "primary_targets": [v["publisher"] for v in venue_analysis[:3]],
        "backup_options": [v["publisher"] for v in venue_analysis[3:6]],
        "considerations": [
            "Target high-impact publishers for maximum visibility",
            "Consider open access options for broader reach",
            "Match journal scope with research topic",
            "Review recent publications in target journals"
        ]
    }
    
    recommendations["strategy"] = strategy
    return recommendations
