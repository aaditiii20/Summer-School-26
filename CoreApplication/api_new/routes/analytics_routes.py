# analytics_routes.py
from fastapi import APIRouter
from datetime import datetime
# Internal imports
from ..database.db_config import db
from ..utils.mock_data import mock_analytics_data   # optional static data helper
#Initialize Router
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics (Mock)"]
)
#Disease / Morbidity Stats
@router.get("/morbidity")
async def get_morbidity_stats():
    # Static JSON 
    data = {
        "region": "North India",
        "total_cases": 10500,
        "top_diseases": {
            "Diabetes": 2200,
            "Hypertension": 1850,
            "Asthma": 900,
            "Heart Disease": 650
        },
        "last_updated": datetime.utcnow().isoformat()
    }
    return {
        "status": "success",
        "message": "Morbidity data fetched successfully",
        "data": data
    }
# Region-wise Claim Insights 
@router.get("/claim-insights")
async def get_claim_insights():
    pipeline = [
        {"$group": {"_id": "$hospital_name", "total_claims": {"$sum": 1}}},
        {"$sort": {"total_claims": -1}}
    ]
    results = await db["claims"].aggregate(pipeline).to_list(length=None)
    # Format results
    formatted = [{"hospital": r["_id"], "total_claims": r["total_claims"]} for r in results]
    return {
        "status": "success",
        "message": "Claim insights fetched successfully",
        "data": formatted
    }
# Consent 
@router.get("/consent-summary")
async def consent_summary():
    granted_count = await db["consents"].count_documents({"status": "granted"})
    revoked_count = await db["consents"].count_documents({"status": "revoked"})

    return {
        "status": "success",
        "message": "Consent summary generated successfully",
        "data": {
            "total_granted": granted_count,
            "total_revoked": revoked_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
