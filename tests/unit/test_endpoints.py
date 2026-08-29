#!/usr/bin/env python3
"""
Quick endpoint test script for AYUSH FHIR Terminology Microservice
Tests all major endpoints to ensure they're working correctly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, url, data=None, params=None):
    """Test an endpoint and return the result"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, params=params)
        
        return {
            "status": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "success": False,
            "error": str(e)
        }

def main():
    """Test all endpoints"""
    print(" Testing AYUSH FHIR Terminology Microservice Endpoints")
    print("=" * 60)
    
    tests = [
        # System endpoints
        ("GET", f"{BASE_URL}/health", None, None, "Health Check"),
        
        # WHO ICD-11 endpoints
        ("GET", f"{BASE_URL}/who-icd/status", None, None, "WHO Status"),
        ("GET", f"{BASE_URL}/who-icd/search", None, {"q": "diabetes"}, "WHO Search"),
        
        # NAMASTE endpoints
        ("GET", f"{BASE_URL}/api/v1/namaste/search", None, {"q": "diabetes"}, "NAMASTE Search"),
        ("GET", f"{BASE_URL}/namaste/conditions", None, None, "NAMASTE Conditions"),
        
        # FHIR endpoints
        ("POST", f"{BASE_URL}/fhir/CodeSystem/$lookup", None, {
            "system": "http://who.int/icd/11",
            "code": "1A00"
        }, "FHIR CodeSystem Lookup"),
    ]
    
    results = []
    for method, url, data, params, description in tests:
        print(f"\n Testing: {description}")
        print(f"   {method} {url}")
        if params:
            print(f"   Params: {params}")
        if data:
            print(f"   Data: {data}")
        
        result = test_endpoint(method, url, data, params)
        results.append((description, result))
        
        if result["success"]:
            print(f"    SUCCESS (Status: {result['status']})")
            if isinstance(result["data"], dict):
                # Show some key info
                if "total_found" in result["data"]:
                    print(f"    Results: {result['data']['total_found']} found")
                elif "data_loaded" in result["data"]:
                    print(f"    Data: {result['data']['total_entries']} entries loaded")
                elif "services" in result["data"]:
                    print(f"    Health: {sum(result['data']['services'].values())} services active")
        else:
            print(f"    FAILED (Status: {result['status']})")
            if 'error' in result:
                print(f"    Error: {result['error']}")
    
    # Summary
    print("\n" + "=" * 60)
    print(" SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result["success"])
    total = len(results)
    
    for description, result in results:
        status = " PASS" if result["success"] else " FAIL"
        print(f"{status} {description}")
    
    print(f"\n Overall: {passed}/{total} endpoints working ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(" ALL ENDPOINTS WORKING! System is ready for SIH Hackathon!")
    else:
        print("  Some endpoints need attention.")

if __name__ == "__main__":
    main()
