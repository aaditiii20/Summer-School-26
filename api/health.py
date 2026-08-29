"""
Health Check API for Vercel Deployment
Comprehensive health monitoring for the AYUSH FHIR Terminology Portal
"""
from datetime import datetime
import json
import os
import sys

def handler(request):
    """Health check endpoint for Vercel with detailed system status"""
    
    # System health indicators
    try:
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Check essential modules
        dependencies = {
            "pandas": False,
            "fastapi": False,
            "uvicorn": False,
            "pydantic": False
        }
        
        for module in dependencies:
            try:
                __import__(module)
                dependencies[module] = True
            except ImportError:
                pass
        
        # Determine overall health
        all_deps_ok = all(dependencies.values())
        overall_status = "healthy" if all_deps_ok else "degraded"
        
        # Health check response with detailed metrics
        health_data = {
            "status": overall_status,
            "service": "AYUSH FHIR Terminology Portal",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "platform": "Vercel",
            "environment": "production",
            "system": {
                "python_version": python_version,
                "dependencies": dependencies,
                "all_dependencies_ok": all_deps_ok
            },
            "uptime_status": "operational",
            "api_endpoints": {
                "health": "/api/health",
                "search": "/api/search",
                "validation": "/api/validation",
                "insurance": "/api/insurance",
                "documentation": "/docs"
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Cache-Control': 'no-cache'
            },
            'body': json.dumps(health_data)
        }
        
    except Exception as e:
        # Return error response
        error_data = {
            "status": "unhealthy",
            "service": "AYUSH FHIR Terminology Portal",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e)
        }
        
        return {
            'statusCode': 503,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_data)
        }
