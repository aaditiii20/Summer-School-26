#!/usr/bin/env python3
"""
AYUSH FHIR Terminology Microservice - Development Mode
"""

import sys
import os
import uvicorn
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("Starting AYUSH FHIR Microservice in Development Mode...")
    print("Access at: http://localhost:8004")
    uvicorn.run("api.master_portal:app", host="0.0.0.0", port=8004, reload=True)
