from fastapi import FastApi
from routes import multilingual_routes
from routes import(
    auth_routes,
    consent_routes,
    claim_routes,
    fhir_routes,
    offline_routes,
    analytics_routes
)

app=FastApi(title="ARYAVARTTA-SIH BACKEND")#IT IS WHERE WE CREATE OUR FIRST FASTAPI APPLICATION INSTANCE
#Include file routes
app.include_router(auth_routes.router)
app.include_router(consent_routes.router)
app.include_router(claim_routes.router)
app.include_router(analytics_routes.router)
app.include_router(fhir_routes.router)
app.include_router(offline_routes.router)
app.include_router(multilingual_routes.router)
#DATABASE SETUP
from database.db_config import connect_to_mongo
# Connect to MongoDB
connect_to_mongo()
@app.get("/")
def root():
    return {"message": "Backend running successfully"}

#  Run using:  uvicorn main:app --reload