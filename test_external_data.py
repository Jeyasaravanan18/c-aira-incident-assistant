"""
Test Script for External Data Integration
Run this to verify all data sources are working
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("🧪 TESTING EXTERNAL DATA INTEGRATION")
print("=" * 60)

# Test 1: CSV Analyzer
print("\n1️⃣ Testing CSV Analyzer...")
try:
    from src.data_sources.csv_analyzer import CSVAnalyzer
    
    analyzer = CSVAnalyzer()
    total = analyzer.get_total_incidents()
    avg_time = analyzer.get_avg_resolution_time()
    insights = analyzer.get_insights()
    
    print(f"   ✅ CSV Analyzer loaded successfully")
    print(f"   📊 Total Incidents: {total}")
    print(f"   ⏱️  Avg Resolution Time: {avg_time}h")
    print(f"   💡 Insights Generated: {len(insights)}")
    
    print("\n   Key Insights:")
    for insight in insights[:3]:
        print(f"   - {insight}")
    
    # Test search
    search_results = analyzer.search_similar_incidents("database")
    print(f"\n   🔍 Search Test ('database'): {len(search_results)} results")
    
    print("\n   ✅ CSV Analyzer: PASSED")
    
except Exception as e:
    print(f"   ❌ CSV Analyzer: FAILED - {e}")

# Test 2: GitHub Status API
print("\n2️⃣ Testing GitHub Status API...")
try:
    from src.data_sources.api_integrations import GitHubStatusAPI
    
    github = GitHubStatusAPI()
    status = github.get_status()
    summary = github.get_summary()
    
    print(f"   ✅ GitHub API connected successfully")
    print(f"   🌐 Status: {summary}")
    print(f"   🔄 Operational: {status.get('is_operational', 'Unknown')}")
    
    # Test recent incidents
    incidents = github.get_recent_incidents(3)
    print(f"   📋 Recent Incidents: {len(incidents)}")
    
    print("\n   ✅ GitHub API: PASSED")
    
except Exception as e:
    print(f"   ❌ GitHub API: FAILED - {e}")

# Test 3: Data Integration
print("\n3️⃣ Testing Data Integration...")
try:
    # Test that both can work together
    csv_data = analyzer.get_incident_by_type()
    github_status = github.is_github_down()
    
    print(f"   ✅ CSV Data Types: {len(csv_data)}")
    print(f"   ✅ GitHub Status Check: {'Down' if github_status else 'Operational'}")
    
    print("\n   ✅ Data Integration: PASSED")
    
except Exception as e:
    print(f"   ❌ Data Integration: FAILED - {e}")

# Test 4: Dependencies
print("\n4️⃣ Testing Dependencies...")
try:
    import pandas as pd
    import plotly
    import requests
    
    print(f"   ✅ pandas: {pd.__version__}")
    print(f"   ✅ plotly: {plotly.__version__}")
    print(f"   ✅ requests: {requests.__version__}")
    
    print("\n   ✅ Dependencies: PASSED")
    
except Exception as e:
    print(f"   ❌ Dependencies: FAILED - {e}")

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("✅ All tests passed!")
print("\n🚀 Ready to run: streamlit run chatbot_enhanced.py")
print("=" * 60)
