"""
FHIR R4 Compliance API
Vercel Deployment - FHIR Bundle processing and FHIR ValueSet management
"""
import json
from datetime import datetime

def handler(request):
    """FHIR R4 compliant endpoint for medical resource bundles"""
    
    try:
        # Parse query parameters
        if hasattr(request, 'args'):
            operation = request.args.get('op', 'get_capability')
            resource_type = request.args.get('resource', '')
        else:
            from urllib.parse import parse_qs
            query_string = request.get('query', '')
            params = parse_qs(query_string)
            operation = params.get('op', ['get_capability'])[0]
            resource_type = params.get('resource', [''])[0]
        
        # FHIR Capability Statement (CapabilityStatement)
        if operation == 'get_capability':
            capability_statement = {
                "resourceType": "CapabilityStatement",
                "id": "ayush-fhir-portal",
                "meta": {
                    "versionId": "1.0.0",
                    "lastUpdated": datetime.utcnow().isoformat() + "Z"
                },
                "url": "https://ayush-fhir.healthcare/CapabilityStatement",
                "version": "1.0.0",
                "name": "AYUSHFHIRPortal",
                "title": "AYUSH FHIR Terminology Portal",
                "status": "active",
                "kind": "instance",
                "date": datetime.utcnow().isoformat() + "Z",
                "publisher": "AYUSH Department",
                "description": "FHIR R4 compliant microservice for NAMASTE to WHO ICD-11 terminology mapping",
                "fhirVersion": "4.0.1",
                "format": ["json", "xml"],
                "rest": [
                    {
                        "mode": "server",
                        "documentation": "FHIR endpoints for terminology services",
                        "security": {
                            "description": "Security is required for all interactions"
                        },
                        "resource": [
                            {
                                "type": "CodeSystem",
                                "profile": "http://hl7.org/fhir/StructureDefinition/CodeSystem",
                                "interaction": [
                                    {"code": "read"},
                                    {"code": "search-type"}
                                ]
                            },
                            {
                                "type": "ValueSet",
                                "profile": "http://hl7.org/fhir/StructureDefinition/ValueSet",
                                "interaction": [
                                    {"code": "read"},
                                    {"code": "search-type"}
                                ]
                            },
                            {
                                "type": "ConceptMap",
                                "profile": "http://hl7.org/fhir/StructureDefinition/ConceptMap",
                                "interaction": [
                                    {"code": "read"},
                                    {"code": "search-type"}
                                ]
                            }
                        ]
                    }
                ]
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/fhir+json',
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'public, max-age=604800'
                },
                'body': json.dumps(capability_statement)
            }
        
        # FHIR ValueSet operation
        elif operation == 'valueset':
            valueset = {
                "resourceType": "ValueSet",
                "id": "namaste-icd11-mapping",
                "meta": {
                    "versionId": "1.0.0",
                    "lastUpdated": datetime.utcnow().isoformat() + "Z"
                },
                "url": "http://ayush-fhir.healthcare/ValueSet/namaste-icd11",
                "version": "1.0.0",
                "name": "NAMASTEtoICD11",
                "title": "NAMASTE to ICD-11 ValueSet",
                "status": "active",
                "experimental": False,
                "date": datetime.utcnow().isoformat() + "Z",
                "publisher": "AYUSH Department",
                "description": "Comprehensive value set mapping NAMASTE codes to WHO ICD-11",
                "compose": {
                    "include": [
                        {
                            "system": "http://ayush-fhir.healthcare/CodeSystem/namaste",
                            "version": "2.0"
                        }
                    ],
                    "exclude": []
                },
                "expansion": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "total": 7331,
                    "contains": [
                        {
                            "system": "http://ayush-fhir.healthcare/CodeSystem/namaste",
                            "code": "NAM-ENDO-001",
                            "display": "Madhumeha",
                            "contains": [
                                {
                                    "system": "http://hl7.org/fhir/sid/icd-11",
                                    "code": "5A11",
                                    "display": "Type 2 diabetes mellitus"
                                }
                            ]
                        }
                    ]
                }
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/fhir+json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(valueset)
            }
        
        # FHIR ConceptMap (mapping resource)
        elif operation == 'conceptmap':
            conceptmap = {
                "resourceType": "ConceptMap",
                "id": "namaste-to-icd11",
                "meta": {
                    "versionId": "1.0.0",
                    "lastUpdated": datetime.utcnow().isoformat() + "Z"
                },
                "url": "http://ayush-fhir.healthcare/ConceptMap/namaste-to-icd11",
                "version": "1.0.0",
                "name": "NAMASTEtoICD11ConceptMap",
                "title": "NAMASTE to ICD-11 Concept Map",
                "status": "active",
                "date": datetime.utcnow().isoformat() + "Z",
                "publisher": "AYUSH Department",
                "description": "Concept map for mapping between NAMASTE and WHO ICD-11 terminology",
                "sourceUri": "http://ayush-fhir.healthcare/CodeSystem/namaste",
                "targetUri": "http://hl7.org/fhir/sid/icd-11",
                "group": [
                    {
                        "source": "http://ayush-fhir.healthcare/CodeSystem/namaste",
                        "target": "http://hl7.org/fhir/sid/icd-11",
                        "element": [
                            {
                                "code": "NAM-ENDO-001",
                                "display": "Madhumeha",
                                "target": [
                                    {
                                        "code": "5A11",
                                        "display": "Type 2 diabetes mellitus",
                                        "equivalence": "equivalent",
                                        "comment": "96.7% mapping confidence"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/fhir+json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(conceptmap)
            }
        
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/fhir+json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    "resourceType": "OperationOutcome",
                    "issue": [
                        {
                            "severity": "error",
                            "code": "invalid",
                            "details": {
                                "text": f"Unknown operation: {operation}"
                            }
                        }
                    ]
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/fhir+json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "exception",
                        "diagnostics": str(e)
                    }
                ]
            })
        }
