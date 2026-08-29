# claim_routes.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
# Internal imports
from ..database.db_config import db
from ..models.claim_model import Claim   # optional model for validation
# Pydantic model for claim input
class ClaimRequest(BaseModel):
    email: str
    diagnosis_code: str
    hospital_name: str
    treatment_cost: float
    claim_reason: str | None = None
# Initialize Router
router = APIRouter(
    prefix="/claim",
    tags=["Claim Logic (Mock)"]
)
# Submit Claim Endpoint
@router.post("/submit-claim")
async def submit_claim(request: ClaimRequest):
    # Find user
    user = await db["users"].find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Create claim entry
    claim_doc = {
        "user_id": str(user["_id"]),
        "email": request.email,
        "diagnosis_code": request.diagnosis_code,
        "hospital_name": request.hospital_name,
        "treatment_cost": request.treatment_cost,
        "claim_reason": request.claim_reason or "General",
        "status": "submitted",
        "submitted_at": datetime.utcnow().isoformat()
    }
    result = await db["claims"].insert_one(claim_doc)
    return {
        "status": "success",
        "message": "Claim submitted successfully",
        "claim_id": str(result.inserted_id)
    }
# Validate Claim (Mock Fraud Check)
@router.get("/validate-claim/{claim_id}")
async def validate_claim(claim_id: str):
    claim = await db["claims"].find_one({"_id": ObjectId(claim_id)})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    # Mock fraud check logic (simple example)
    is_fraud = False
    if claim["treatment_cost"] > 100000:  # arbitrary threshold
        is_fraud = True
    # Update claim status
    new_status = "rejected" if is_fraud else "approved"
    await db["claims"].update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": {"status": new_status, "validated_at": datetime.utcnow().isoformat()}}
    )
    return {
        "status": "success",
        "message": "Claim validated",
        "claim_id": claim_id,
        "fraud_flag": is_fraud,
        "final_status": new_status
    }
#Get All Claims of a User
@router.get("/user-claims/{email}")
async def get_user_claims(email: str):
    claims_cursor = db["claims"].find({"email": email})
    claims = []
    async for claim in claims_cursor:
        claim["_id"] = str(claim["_id"])
        claims.append(claim)
    if not claims:
        raise HTTPException(status_code=404, detail="No claims found for this user")
    return {
        "status": "success",
        "total_claims": len(claims),
        "claims": claims
    }
