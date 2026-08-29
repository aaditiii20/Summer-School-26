"""
Authentication & Authorization API
Vercel Deployment - OAuth 2.0 ABHA authentication for AYUSH portal
"""
import json
from datetime import datetime, timedelta
import hashlib
import os

def handler(request):
    """Authentication endpoint with OAuth 2.0 and ABHA support"""
    
    try:
        # Parse query parameters
        if hasattr(request, 'args'):
            auth_type = request.args.get('type', 'token')
            username = request.args.get('username', '')
            password = request.args.get('password', '')
            grant_type = request.args.get('grant_type', 'password')
        else:
            from urllib.parse import parse_qs
            query_string = request.get('query', '')
            params = parse_qs(query_string)
            auth_type = params.get('type', ['token'])[0]
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            grant_type = params.get('grant_type', ['password'])[0]
        
        # Token generation
        if auth_type == 'token' and grant_type == 'password':
            
            # Validate credentials (for demo purposes)
            if not username or not password:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        "error": "invalid_request",
                        "error_description": "Username and password are required"
                    })
                }
            
            # Generate mock token
            token_data = {
                "access_token": hashlib.sha256(f"{username}{datetime.utcnow().isoformat()}".encode()).hexdigest(),
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": hashlib.sha256(f"refresh_{username}_{datetime.utcnow().isoformat()}".encode()).hexdigest(),
                "scope": "read write"
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'no-store',
                    'Pragma': 'no-cache'
                },
                'body': json.dumps(token_data)
            }
        
        # ABHA Authentication
        elif auth_type == 'abha':
            abha_number = request.args.get('abha_number', '') if hasattr(request, 'args') else ''
            
            if not abha_number:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        "error": "invalid_request",
                        "error_description": "ABHA number is required"
                    })
                }
            
            abha_auth_result = {
                "auth_status": "authenticated",
                "abha_number": abha_number,
                "user_profile": {
                    "name": "Patient Name",
                    "age": 45,
                    "gender": "M",
                    "district": "Delhi",
                    "state": "Delhi"
                },
                "healthcare_records": {
                    "total_visits": 23,
                    "recent_visit": "2025-09-10T10:30:00Z",
                    "active_prescriptions": 2,
                    "allergies": ["Penicillin"]
                },
                "access_token": hashlib.sha256(f"abha_{abha_number}".encode()).hexdigest(),
                "token_type": "Bearer",
                "expires_in": 7200
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(abha_auth_result)
            }
        
        # Validate Token
        elif auth_type == 'validate':
            token = request.args.get('token', '') if hasattr(request, 'args') else ''
            
            if not token:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        "error": "invalid_request",
                        "error_description": "Token is required"
                    })
                }
            
            validation_result = {
                "token_valid": True,
                "user": {
                    "id": "user_12345",
                    "role": "healthcare_provider",
                    "permissions": [
                        "read:terminology",
                        "write:translation",
                        "read:analytics",
                        "validate:codes"
                    ]
                },
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
                "scopes": ["read", "write"]
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(validation_result)
            }
        
        # Refresh Token
        elif auth_type == 'refresh':
            refresh_token = request.args.get('refresh_token', '') if hasattr(request, 'args') else ''
            
            if not refresh_token:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        "error": "invalid_request",
                        "error_description": "Refresh token is required"
                    })
                }
            
            new_token = {
                "access_token": hashlib.sha256(f"new_token_{datetime.utcnow().isoformat()}".encode()).hexdigest(),
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": hashlib.sha256(f"new_refresh_{datetime.utcnow().isoformat()}".encode()).hexdigest()
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(new_token)
            }
        
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    "error": "invalid_request",
                    "error_description": f"Unknown auth type: {auth_type}",
                    "available_types": ["token", "abha", "validate", "refresh"]
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "error": "server_error",
                "error_description": str(e)
            })
        }
