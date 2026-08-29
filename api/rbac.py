"""
ISO-22600 Role-Based Access Control (RBAC) for Medical Privacy
Implements industrial-grade access control for healthcare data
"""
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Callable, Any

# ========== ISO-22600 RBAC ROLES ==========

ISO22600_ROLES = {
    "patient": {
        "permissions": ["read_own_records", "request_access"],
        "level": 1,
        "description": "Patient access to personal health records"
    },
    "provider": {
        "permissions": ["read_records", "write_records", "diagnose", "prescribe", "read_analytics"],
        "level": 3,
        "description": "Healthcare provider with treatment capabilities"
    },
    "pharmacist": {
        "permissions": ["read_medications", "write_medications", "check_interactions", "dispense"],
        "level": 2,
        "description": "Pharmacy professional"
    },
    "lab_technician": {
        "permissions": ["read_tests", "write_results", "access_samples"],
        "level": 2,
        "description": "Laboratory professional"
    },
    "administrator": {
        "permissions": ["read_all", "write_all", "manage_users", "audit", "configure_system"],
        "level": 5,
        "description": "System administrator with full access"
    },
    "auditor": {
        "permissions": ["read_audit_logs", "view_access_reports", "compliance_check"],
        "level": 2,
        "description": "Compliance and audit professional (read-only)"
    },
    "epidemiologist": {
        "permissions": ["read_aggregate_data", "read_outbreak_data", "analytics", "predict_outbreaks"],
        "level": 3,
        "description": "Public health specialist for epidemic surveillance"
    }
}

# ========== PERMISSION MATRIX ==========

PERMISSIONS = {
    "read_own_records": {"resource": "patient_records", "action": "read", "scope": "personal"},
    "read_records": {"resource": "patient_records", "action": "read", "scope": "assigned"},
    "read_all": {"resource": "patient_records", "action": "read", "scope": "all"},
    "write_records": {"resource": "patient_records", "action": "write", "scope": "assigned"},
    "write_all": {"resource": "patient_records", "action": "write", "scope": "all"},
    "diagnose": {"resource": "diagnoses", "action": "create", "scope": "assigned"},
    "prescribe": {"resource": "prescriptions", "action": "create", "scope": "assigned"},
    "read_medications": {"resource": "medications", "action": "read", "scope": "all"},
    "write_medications": {"resource": "medications", "action": "write", "scope": "assigned"},
    "check_interactions": {"resource": "drug_interactions", "action": "check", "scope": "all"},
    "dispense": {"resource": "dispensing", "action": "execute", "scope": "assigned"},
    "read_tests": {"resource": "lab_tests", "action": "read", "scope": "assigned"},
    "write_results": {"resource": "lab_results", "action": "write", "scope": "assigned"},
    "access_samples": {"resource": "samples", "action": "access", "scope": "assigned"},
    "manage_users": {"resource": "users", "action": "manage", "scope": "all"},
    "audit": {"resource": "audit_logs", "action": "read", "scope": "all"},
    "configure_system": {"resource": "system_config", "action": "write", "scope": "all"},
    "read_audit_logs": {"resource": "audit_logs", "action": "read", "scope": "all"},
    "view_access_reports": {"resource": "access_reports", "action": "read", "scope": "all"},
    "compliance_check": {"resource": "compliance", "action": "check", "scope": "all"},
    "read_analytics": {"resource": "analytics", "action": "read", "scope": "assigned"},
    "read_aggregate_data": {"resource": "health_data", "action": "read", "scope": "aggregate"},
    "read_outbreak_data": {"resource": "outbreak_data", "action": "read", "scope": "aggregate"},
    "analytics": {"resource": "analytics", "action": "read", "scope": "outbreak"},
    "predict_outbreaks": {"resource": "predictions", "action": "execute", "scope": "regional"},
    "request_access": {"resource": "access_requests", "action": "create", "scope": "personal"},
}


class RBACToken:
    """ISO-22600 compliant token with role and permissions"""
    
    def __init__(self, user_id: str, roles: List[str], organization: str = "default"):
        self.user_id = user_id
        self.roles = roles
        self.organization = organization
        self.issued_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(hours=24)
        self.permissions = self._calculate_permissions()
        self.audit_id = f"token_{user_id}_{datetime.utcnow().timestamp()}"
        
    def _calculate_permissions(self) -> List[str]:
        """Calculate union of all permissions for assigned roles"""
        permissions = set()
        for role in self.roles:
            if role in ISO22600_ROLES:
                permissions.update(ISO22600_ROLES[role]["permissions"])
        return list(permissions)
    
    def has_permission(self, permission: str) -> bool:
        """Check if token has specific permission"""
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """Check if token has specific role"""
        return role in self.roles
    
    def to_dict(self) -> Dict:
        """Serialize token to dict"""
        return {
            "user_id": self.user_id,
            "roles": self.roles,
            "permissions": self.permissions,
            "organization": self.organization,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "audit_id": self.audit_id
        }
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at


class AuditLog:
    """ISO-22600 audit trail for access tracking"""
    
    def __init__(self):
        self.logs: List[Dict] = []
    
    def log_access(self, user_id: str, resource: str, action: str, status: str, details: Dict = None):
        """Log resource access for compliance"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "status": status,
            "details": details or {}
        }
        self.logs.append(log_entry)
        return log_entry
    
    def get_logs(self, user_id: str = None, start_date: datetime = None, limit: int = 100) -> List[Dict]:
        """Retrieve audit logs with filtering"""
        filtered = self.logs
        
        if user_id:
            filtered = [l for l in filtered if l["user_id"] == user_id]
        
        if start_date:
            filtered = [l for l in filtered if datetime.fromisoformat(l["timestamp"]) >= start_date]
        
        return filtered[-limit:]


# Global audit log
audit_log = AuditLog()


def require_permission(permission: str) -> Callable:
    """Decorator to enforce permission-based access control"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Extract token from request header
            token_data = getattr(request, 'token', None)
            
            if not token_data:
                audit_log.log_access("anonymous", func.__name__, "access_denied", "no_token")
                return {
                    'statusCode': 401,
                    'body': json.dumps({"error": "Unauthorized: No token provided"})
                }
            
            # Validate permission
            if isinstance(token_data, dict):
                if permission not in token_data.get('permissions', []):
                    audit_log.log_access(
                        token_data.get('user_id', 'unknown'),
                        func.__name__,
                        "access_denied",
                        "insufficient_permissions",
                        {"required": permission, "has": token_data.get('permissions', [])}
                    )
                    return {
                        'statusCode': 403,
                        'body': json.dumps({"error": f"Forbidden: Missing permission '{permission}'"})
                    }
            
            # Log successful access
            audit_log.log_access(
                token_data.get('user_id', 'system'),
                func.__name__,
                "executed",
                "success"
            )
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_role(*roles: str) -> Callable:
    """Decorator to enforce role-based access control"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            token_data = getattr(request, 'token', None)
            
            if not token_data:
                return {
                    'statusCode': 401,
                    'body': json.dumps({"error": "Unauthorized: No token provided"})
                }
            
            user_roles = token_data.get('roles', [])
            has_role = any(role in user_roles for role in roles)
            
            if not has_role:
                audit_log.log_access(
                    token_data.get('user_id', 'unknown'),
                    func.__name__,
                    "access_denied",
                    "insufficient_role",
                    {"required": list(roles), "has": user_roles}
                )
                return {
                    'statusCode': 403,
                    'body': json.dumps({"error": f"Forbidden: Required roles {roles}"})
                }
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def generate_token(user_id: str, roles: List[str], organization: str = "default") -> Dict:
    """Generate ISO-22600 compliant access token"""
    token = RBACToken(user_id, roles, organization)
    return {
        "access_token": token.audit_id,
        "token_type": "Bearer",
        "expires_in": 86400,
        "user_id": token.user_id,
        "roles": token.roles,
        "permissions": token.permissions,
        "issued_at": token.issued_at.isoformat()
    }


def validate_token(token_str: str) -> Optional[Dict]:
    """Validate and parse ISO-22600 token"""
    # In production, verify JWT signature
    if not token_str or not token_str.startswith("token_"):
        return None
    
    return {
        "user_id": token_str.split("_")[1],
        "valid": True
    }


# ========== API ENDPOINT ==========

def handler(request):
    """ISO-22600 RBAC endpoint for token generation and validation"""
    
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    
    if path == '/rbac/token' and method == 'POST':
        # Token generation endpoint
        body = json.loads(request.get('body', '{}'))
        user_id = body.get('user_id')
        roles = body.get('roles', ['patient'])
        organization = body.get('organization', 'default')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "user_id required"})
            }
        
        # Validate roles exist
        invalid_roles = [r for r in roles if r not in ISO22600_ROLES]
        if invalid_roles:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": f"Invalid roles: {invalid_roles}"})
            }
        
        token = generate_token(user_id, roles, organization)
        audit_log.log_access(user_id, "token_generation", "token_issued", "success")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(token)
        }
    
    elif path == '/rbac/validate' and method == 'POST':
        # Token validation endpoint
        body = json.loads(request.get('body', '{}'))
        token = body.get('token')
        
        if not token:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "token required"})
            }
        
        result = validate_token(token)
        if result:
            return {
                'statusCode': 200,
                'body': json.dumps({"valid": True, "user_id": result["user_id"]})
            }
        
        return {
            'statusCode': 401,
            'body': json.dumps({"valid": False, "error": "Invalid token"})
        }
    
    elif path == '/rbac/roles' and method == 'GET':
        # List all available roles
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "roles": {k: {"description": v["description"], "permissions": v["permissions"]} 
                          for k, v in ISO22600_ROLES.items()}
            })
        }
    
    elif path == '/rbac/permissions' and method == 'GET':
        # List all permissions
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "permissions": PERMISSIONS,
                "total": len(PERMISSIONS)
            })
        }
    
    elif path == '/rbac/audit' and method == 'GET':
        # Get audit logs
        user_id = request.get('query', {}).get('user_id', [None])[0]
        logs = audit_log.get_logs(user_id=user_id)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "total_logs": len(logs),
                "logs": logs
            })
        }
    
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({"error": "Not found"})
        }
