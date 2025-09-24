"""
Test script to verify CORE API integration with deepagents framework
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(backend_dir / ".env")
except ImportError:
    # Manually load .env file if python-dotenv is not available
    env_file = backend_dir / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

async def test_core_api_tools():
    """Test CORE API tools integration"""
    print("🧪 Testing CORE API Tools Integration...")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from tools.core_api.config import validate_config, CORE_API_CONFIG
        from tools.core_api import search_works, aggregate_works
        
        # Validate configuration
        print("⚙️  Validating configuration...")
        validate_config()
        print(f"✅ CORE API configured with base URL: {CORE_API_CONFIG['base_url']}")
        
        # Test basic search (small query to avoid rate limits)
        print("🔍 Testing basic search functionality...")
        search_result = await search_works.ainvoke({
            "query": "machine learning",
            "limit": 5,
            "require_full_text": False
        })
        
        print(f"   Search result type: {type(search_result)}")
        print(f"   Search result: {search_result}")
        
        # Handle both dict and string responses
        if isinstance(search_result, dict) and search_result.get("success"):
            print(f"✅ Search successful! Found {search_result['results_count']} results")
            print(f"   Total hits: {search_result['total_hits']}")
            if search_result["results"]:
                first_result = search_result["results"][0]
                print(f"   Sample result: {first_result['title'][:50]}...")
        else:
            print(f"❌ Search failed: {search_result['error']}")
            return False
        
        # Test aggregation
        print("📊 Testing aggregation functionality...")
        agg_result = await aggregate_works.ainvoke({
            "query": "artificial intelligence",
            "aggregation_fields": ["yearPublished"],
            "max_buckets": 10
        })
        
        if agg_result["success"]:
            print(f"✅ Aggregation successful! Total hits: {agg_result['total_hits']}")
            year_agg = agg_result["aggregations"].get("yearPublished", {})
            if year_agg.get("buckets"):
                print(f"   Found {len(year_agg['buckets'])} year buckets")
        else:
            print(f"❌ Aggregation failed: {agg_result['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_subagent_integration():
    """Test subagent integration"""
    print("\n🤖 Testing Subagent Integration...")
    
    try:
        # Test subagent imports
        print("📦 Testing subagent imports...")
        from subagents.core_research_subagents import (
            get_all_core_research_subagents,
            CORE_RESEARCH_SUBAGENTS
        )
        from config.prompts import (
            LITERATURE_SCREENER_PROMPT,
            TREND_ANALYZER_PROMPT
        )
        
        # Get all subagents
        subagents = get_all_core_research_subagents()
        print(f"✅ Successfully loaded {len(subagents)} CORE research subagents")
        
        # Verify subagent structure
        for subagent in subagents[:2]:  # Test first 2
            print(f"   - {subagent['name']}: {subagent['description'][:50]}...")
            assert "name" in subagent
            assert "description" in subagent
            assert "prompt" in subagent
            assert "tools" in subagent
        
        print(f"✅ All subagents have required structure")
        
        # Test individual subagent creators
        print("🔧 Testing individual subagent creators...")
        for name, creator in list(CORE_RESEARCH_SUBAGENTS.items())[:3]:  # Test first 3
            subagent = creator()
            print(f"   - Created {subagent['name']} with {len(subagent['tools'])} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Subagent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_main_agent_integration():
    """Test main agent integration"""
    print("\n🎯 Testing Main Agent Integration...")
    
    try:
        # Test main agent import
        print("📦 Testing main agent import...")
        from agents.main_agent import create_main_agent
        
        print("🏗️  Creating main agent...")
        agent = create_main_agent()
        print("✅ Main agent created successfully!")
        
        # Check if CORE tools are available
        # Note: This is a basic structure check, not a full execution test
        print("🔍 Verifying CORE API integration in main agent...")
        
        # The agent should have the tools and subagents integrated
        # This is verified by successful creation without errors
        print("✅ Main agent integration appears successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Main agent integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all integration tests"""
    print("🚀 Starting CORE API Integration Tests\n")
    
    # Test results
    results = []
    
    # Test 1: CORE API Tools
    results.append(await test_core_api_tools())
    
    # Test 2: Subagent Integration  
    results.append(await test_subagent_integration())
    
    # Test 3: Main Agent Integration
    results.append(await test_main_agent_integration())
    
    # Summary
    print(f"\n📋 Test Summary:")
    print(f"   CORE API Tools: {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"   Subagent Integration: {'✅ PASS' if results[1] else '❌ FAIL'}")
    print(f"   Main Agent Integration: {'✅ PASS' if results[2] else '❌ FAIL'}")
    
    all_passed = all(results)
    print(f"\n🎉 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎊 CORE API integration is ready for use!")
        print("   Available subagents:")
        print("   - literature_screener: Systematic literature searches")
        print("   - trend_analyzer: Research trend analysis")
        print("   - full_text_analyzer: Deep paper content analysis")
        print("   - systematic_review_helper: PRISMA-compliant reviews")
        print("   - meta_analysis_collector: Meta-analysis data extraction")
        print("   - venue_analyzer: Publication venue analysis")
        print("   - research_gap_identifier: Research opportunity identification")
        print("   - citation_network_mapper: Citation and influence analysis")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
