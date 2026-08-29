"""
Quick Portal Functionality Test
Tests core features of the NAMASTE-ICD11 Healthcare Portal
"""

import requests
import json
import time

def test_portal_functionality():
    base_url = "http://localhost:8008"
    
    print(" NAMASTE-ICD11 Portal Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Pipeline Status", f"{base_url}/api/pipeline/status"),
        ("Phase 1 Stats", f"{base_url}/api/pipeline/phase1/stats"),
        ("AI Health Check", f"{base_url}/api/pipeline/phase3/ai-health"),
        ("Search Test", f"{base_url}/api/search/unified?q=fever"),
        ("Translation Test", f"{base_url}/api/translation/namaste-to-icd11?code=AY001"),
        ("AI Symptoms Test", f"{base_url}/api/ai/symptoms?symptoms=fever,headache"),
        ("Quality Metrics", f"{base_url}/api/quality/mapping-accuracy"),
        ("Performance Stats", f"{base_url}/api/monitoring/performance")
    ]
    
    results = {}
    
    for test_name, url in tests:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f" {test_name}: SUCCESS ({response_time:.1f}ms)")
                    results[test_name] = {"status": "SUCCESS", "time": f"{response_time:.1f}ms"}
                except:
                    print(f" {test_name}: SUCCESS - HTML Response ({response_time:.1f}ms)")
                    results[test_name] = {"status": "SUCCESS", "time": f"{response_time:.1f}ms"}
            else:
                print(f"  {test_name}: HTTP {response.status_code} ({response_time:.1f}ms)")
                results[test_name] = {"status": f"HTTP {response.status_code}", "time": f"{response_time:.1f}ms"}
                
        except requests.exceptions.RequestException as e:
            print(f" {test_name}: ERROR - {str(e)}")
            results[test_name] = {"status": "ERROR", "error": str(e)}
    
    print("\n Test Summary:")
    print("=" * 50)
    successful_tests = sum(1 for r in results.values() if r["status"] == "SUCCESS")
    total_tests = len(results)
    
    print(f" Successful Tests: {successful_tests}/{total_tests}")
    print(f" Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        response_times = [float(r["time"].replace("ms", "")) for r in results.values() if "time" in r]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f" Average Response Time: {avg_time:.1f}ms")
    
    print(f"\n Portal Status: {' OPERATIONAL' if successful_tests >= total_tests * 0.7 else ' PARTIAL' if successful_tests > 0 else ' OFFLINE'}")
    print(f" Portal URL: http://localhost:8008")
    print(f" API Documentation: http://localhost:8008/docs")
    
    return results

if __name__ == "__main__":
    test_portal_functionality()
