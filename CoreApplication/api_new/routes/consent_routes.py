# consent_routes.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from bson import ObjectId
# Internal imports
from ..database.db_config import db        # MongoDB connection
from ..models.consent_model import Consent # Pydantic model for consent
from ..utils.mock_data import mock_abha_data  # optional dummy ABHA data
from datetime import datetime
#INITIALISE ROUTER
router=APIRouter(
    prefix="/consent",
    tags=["Consent & ABHA"] 
)
# Create a Pydantic model for input (inside consent_routes.py)
class ConsentRequest(BaseModel):
    email: str | None = None          # optional: can use email OR abha_id
    abha_id: str | None = None
    consent_type: str                 # e.g. "share_with_doctor", "share_with_insurer"
    granted_by: str | None = None     # optional, who gave consent
    expires_at: str | None = None     # optional, can add expiry
    metadata: dict | None = None      # extra info if needed
@router.post("/give-consent")
async def give_consent(request: ConsentRequest):
    # Identify user
    if request.email:
        user = await db["users"].find_one({"email": request.email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        abha_id = user.get("abha_id", None)
    elif request.abha_id:
        abha_id = request.abha_id
    else:
        raise HTTPException(status_code=400, detail="Provide either email or ABHA ID")
    # Check existing consent
    existing = await db["consents"].find_one({
        "abha_id": abha_id,
        "consent_type": request.consent_type,
        "status": "granted"
    })
    if existing:
        return {
            "status": "success",
            "message": "Consent already granted",
            "consent_id": str(existing["_id"])
        }
    #  Create new consent record
    new_consent = {
        "abha_id": abha_id,
        "consent_type": request.consent_type,
        "status": "granted",
        "granted_by": request.granted_by or "self",
        "granted_at": datetime.utcnow().isoformat(),
        "expires_at": request.expires_at,
        "metadata": request.metadata or {},
    }
    #  Insert into MongoDB
    result = await db["consents"].insert_one(new_consent)
    # Return success response
    return {
        "status": "success",
        "message": "Consent granted successfully",
        "consent_id": str(result.inserted_id),
        "consent_type": request.consent_type,
        "abha_id": abha_id
    }
# Revoke Consent Endpoint
@router.post("/revoke-consent")
async def revoke_consent(abha_id: str, consent_type: str):
    consent = await db["consents"].find_one({
        "abha_id": abha_id,
        "consent_type": consent_type,
        "status": "granted"
    })
    if not consent:
        raise HTTPException(status_code=404, detail="Active consent not found")
    await db["consents"].update_one(
        {"_id": consent["_id"]},
        {"$set": {"status": "revoked", "revoked_at": datetime.utcnow().isoformat()}}
    )
    return {
        "status": "success",
        "message": "Consent revoked successfully",
        "consent_type": consent_type,
        "abha_id": abha_id
    }
# Check Consent Endpoint
@router.get("/check-consent")
async def check_consent(abha_id: str, consent_type: str):
    consent = await db["consents"].find_one({
        "abha_id": abha_id,
        "consent_type": consent_type
    })
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")
    return {
        "status": "success",
        "abha_id": abha_id,
        "consent_type": consent_type,
        "current_status": consent["status"]
    }
# Link ABHA MOCK
@router.post("/link-abha")
async def link_abha(email: str):
    # Lookup user
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Mock ABHA data
    fake_abha = mock_abha_data.copy()
    fake_abha["linked_email"] = email
    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"abha_id": fake_abha["abha_id"], "abha_linked": True}}
    )
    return {
        "status": "success",
        "message": "ABHA linked successfully (mock)",
        "abha_data": fake_abha
    }