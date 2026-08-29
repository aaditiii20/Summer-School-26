"""
Enhanced Excel Portal Server - Complete implementation with dashboard
"""

from fastapi import FastAPI, HTTPException, Query, Depends, Form, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
import csv
import io
import json
import hashlib
import secrets
from datetime import datetime, timedelta
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=" AYUSH Medical Portal - Excel Data Integration",
    description="Comprehensive medical search with real Ayurveda, Siddha, Unani & ICD10 data",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory user storage
USERS_DB = {}
SESSIONS = {}

# Security
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = "ayush_fhir_excel_2025"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def create_session(username: str) -> str:
    """Create a new session token"""
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = {
        "username": username,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    return token

def verify_session(token: str) -> dict:
    """Verify session token"""
    if token not in SESSIONS:
        return None
    
    session = SESSIONS[token]
    if datetime.now() > session["expires_at"]:
        del SESSIONS[token]
        return None
    
    return session

# Enhanced data loading from Excel files
def load_excel_data():
    """Load all medical data from Excel files"""
    try:
        data = {}
        
        # Load Ayurveda data
        logger.info("Loading Ayurveda Excel data...")
        try:
            ayurveda_df = pd.read_excel("Ayurveda.xls")
            ayurveda_records = []
            for _, row in ayurveda_df.iterrows():
                if pd.notna(row.get('NAMC_term')):
                    record = {
                        "code": str(row.get('NAMC_CODE', '')),
                        "namc_id": str(row.get('NAMC_ID', '')),
                        "name": str(row.get('NAMC_term', '')),
                        "sanskrit_name": str(row.get('NAMC_term_diacritical', '')) if pd.notna(row.get('NAMC_term_diacritical')) else "",
                        "devanagari": str(row.get('NAMC_term_DEVANAGARI', '')) if pd.notna(row.get('NAMC_term_DEVANAGARI')) else "",
                        "short_definition": str(row.get('Short_definition', '')) if pd.notna(row.get('Short_definition')) else "",
                        "long_definition": str(row.get('Long_definition', '')) if pd.notna(row.get('Long_definition')) else "",
                        "system": "Ayurveda",
                        "category": "Traditional Medicine - Ayurveda"
                    }
                    ayurveda_records.append(record)
            data['ayurveda'] = ayurveda_records
            logger.info(f"Loaded {len(ayurveda_records)} Ayurveda records")
        except Exception as e:
            logger.error(f"Error loading Ayurveda data: {e}")
            data['ayurveda'] = []
        
        # Load Siddha data
        logger.info("Loading Siddha Excel data...")
        try:
            siddha_df = pd.read_excel("Sidhha.xls")
            siddha_records = []
            for _, row in siddha_df.iterrows():
                if pd.notna(row.get('NAMC_TERM')):
                    record = {
                        "code": str(row.get('NAMC_CODE', '')),
                        "namc_id": str(row.get('NAMC_ID', '')),
                        "name": str(row.get('NAMC_TERM', '')),
                        "tamil_name": str(row.get('Tamil_term', '')) if pd.notna(row.get('Tamil_term')) else "",
                        "short_definition": str(row.get('Short_definition', '')) if pd.notna(row.get('Short_definition')) else "",
                        "long_definition": str(row.get('Long_definition', '')) if pd.notna(row.get('Long_definition')) else "",
                        "reference": str(row.get('Reference', '')) if pd.notna(row.get('Reference')) else "",
                        "system": "Siddha",
                        "category": "Traditional Medicine - Siddha"
                    }
                    siddha_records.append(record)
            data['siddha'] = siddha_records
            logger.info(f"Loaded {len(siddha_records)} Siddha records")
        except Exception as e:
            logger.error(f"Error loading Siddha data: {e}")
            data['siddha'] = []
        
        # Load Unani data
        logger.info("Loading Unani Excel data...")
        try:
            unani_df = pd.read_excel("Unani.xls")
            unani_records = []
            for _, row in unani_df.iterrows():
                if pd.notna(row.get('NUMC_TERM')) or pd.notna(row.get('Arabic_term')):
                    record = {
                        "code": str(row.get('NUMC_CODE', '')),
                        "numc_id": str(row.get('NUMC_ID', '')),
                        "name": str(row.get('NUMC_TERM', '')) if pd.notna(row.get('NUMC_TERM')) else "",
                        "arabic_name": str(row.get('Arabic_term', '')) if pd.notna(row.get('Arabic_term')) else "",
                        "short_definition": str(row.get('Short_definition', '')) if pd.notna(row.get('Short_definition')) else "",
                        "long_definition": str(row.get('Long_definition', '')) if pd.notna(row.get('Long_definition')) else "",
                        "system": "Unani",
                        "category": "Traditional Medicine - Unani"
                    }
                    unani_records.append(record)
            data['unani'] = unani_records
            logger.info(f"Loaded {len(unani_records)} Unani records")
        except Exception as e:
            logger.error(f"Error loading Unani data: {e}")
            data['unani'] = []
        
        # Load ICD10 data
        logger.info("Loading ICD10 Excel data...")
        try:
            icd10_df = pd.read_excel("ICD10.xls")
            icd10_records = []
            for _, row in icd10_df.iterrows():
                if pd.notna(row.get('NAMC_TERM')):
                    record = {
                        "code": str(row.get('NAMC_CODE', '')),
                        "namc_id": str(row.get('NAMC_ID', '')),
                        "name": str(row.get('NAMC_TERM', '')),
                        "block_title": str(row.get('block_title', '')) if pd.notna(row.get('block_title')) else "",
                        "chapter_name": str(row.get('chapt_name', '')) if pd.notna(row.get('chapt_name')) else "",
                        "system": "ICD10",
                        "category": "International Classification - ICD10"
                    }
                    icd10_records.append(record)
            data['icd10'] = icd10_records
            logger.info(f"Loaded {len(icd10_records)} ICD10 records")
        except Exception as e:
            logger.error(f"Error loading ICD10 data: {e}")
            data['icd10'] = []
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading Excel data: {e}")
        return {
            'ayurveda': [],
            'siddha': [],
            'unani': [],
            'icd10': []
        }

# Global data variables
MEDICAL_DATA = {}

# Initialize data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    global MEDICAL_DATA
    MEDICAL_DATA = load_excel_data()
    
    total_records = sum(len(records) for records in MEDICAL_DATA.values())
    logger.info(f"Successfully loaded {total_records} total medical records from Excel files")
    
    for system, records in MEDICAL_DATA.items():
        logger.info(f"  - {system.upper()}: {len(records)} records")

# Authentication endpoints
@app.post("/register", tags=[" Authentication"])
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Register a new user"""
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    USERS_DB[username] = {
        "username": username,
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "role": "user"
    }
    
    return {"message": "Registration successful", "username": username}

@app.post("/login", tags=[" Authentication"])
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """Login user and create session"""
    if username not in USERS_DB:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user = USERS_DB[username]
    if user["password"] != hash_password(password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_session(username)
    
    return {
        "message": "Login successful",
        "token": token,
        "username": username,
        "redirect": "/dashboard"
    }

# Protected route dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    session = verify_session(token)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return session

# Landing page
@app.get("/", response_class=HTMLResponse, tags=[" Landing"])
async def landing_page():
    """Serve the landing page with login/signup"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> AYUSH Medical Portal - Excel Data</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            background: white; 
            border-radius: 20px; 
            padding: 40px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 450px;
            width: 90%;
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .header h1 { 
            color: #2c3e50; 
            font-size: 2rem; 
            margin-bottom: 10px; 
        }
        .header p { 
            color: #666; 
            font-size: 1rem; 
        }
        .stats-highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .stat-item {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
        }
        .stat-number {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .tabs { 
            display: flex; 
            margin-bottom: 30px; 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 5px; 
        }
        .tab { 
            flex: 1; 
            padding: 12px; 
            text-align: center; 
            border-radius: 8px; 
            cursor: pointer; 
            transition: all 0.3s ease; 
            font-weight: 500; 
        }
        .tab.active { 
            background: #3498db; 
            color: white; 
            box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3); 
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            color: #2c3e50; 
            font-weight: 500; 
        }
        .form-group input { 
            width: 100%; 
            padding: 15px; 
            border: 2px solid #e1e8ed; 
            border-radius: 10px; 
            font-size: 16px; 
            transition: border-color 0.3s ease; 
        }
        .form-group input:focus { 
            outline: none; 
            border-color: #3498db; 
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1); 
        }
        .btn { 
            width: 100%; 
            padding: 15px; 
            background: #3498db; 
            color: white; 
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            font-weight: 600; 
            cursor: pointer; 
            transition: all 0.3s ease; 
        }
        .btn:hover { 
            background: #2980b9; 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4); 
        }
        .form-container { 
            display: none; 
        }
        .form-container.active { 
            display: block; 
        }
        .alert { 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px; 
            font-weight: 500; 
        }
        .alert-success { 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb; 
        }
        .alert-error { 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> AYUSH Portal</h1>
            <p>Real medical data from Excel files - Ayurveda, Siddha, Unani & ICD10</p>
        </div>
        
        <div class="stats-highlight">
            <h3> Massive Medical Database</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">2,893</div>
                    <div> Ayurveda Terms</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">1,926</div>
                    <div> Siddha Terms</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">2,522</div>
                    <div> Unani Terms</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">11,145</div>
                    <div> ICD10 Codes</div>
                </div>
            </div>
            <p style="margin-top: 15px; font-size: 18px; font-weight: bold;">18,486+ Total Medical Records!</p>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('login')">Login</div>
            <div class="tab" onclick="switchTab('register')">Sign Up</div>
        </div>
        
        <div id="alerts"></div>
        
        <!-- Login Form -->
        <div id="login-form" class="form-container active">
            <form onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label for="login-username">Username</label>
                    <input type="text" id="login-username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="login-password">Password</label>
                    <input type="password" id="login-password" name="password" required>
                </div>
                <button type="submit" class="btn"> Access Medical Database</button>
            </form>
        </div>
        
        <!-- Registration Form -->
        <div id="register-form" class="form-container">
            <form onsubmit="handleRegister(event)">
                <div class="form-group">
                    <label for="reg-username">Username</label>
                    <input type="text" id="reg-username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="reg-email">Email</label>
                    <input type="email" id="reg-email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="reg-password">Password</label>
                    <input type="password" id="reg-password" name="password" required>
                </div>
                <div class="form-group">
                    <label for="reg-confirm">Confirm Password</label>
                    <input type="password" id="reg-confirm" name="confirm_password" required>
                </div>
                <button type="submit" class="btn"> Create Account</button>
            </form>
        </div>
    </div>

    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            document.querySelectorAll('.form-container').forEach(f => f.classList.remove('active'));
            document.getElementById(tab + '-form').classList.add('active');
            
            document.getElementById('alerts').innerHTML = '';
        }
        
        function showAlert(message, type) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.textContent = message;
            document.getElementById('alerts').innerHTML = '';
            document.getElementById('alerts').appendChild(alertDiv);
        }
        
        async function handleLogin(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showAlert('Login successful! Loading 18,486+ medical records...', 'success');
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('username', data.username);
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 2000);
                } else {
                    showAlert(data.detail || 'Login failed', 'error');
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'error');
            }
        }
        
        async function handleRegister(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showAlert('Registration successful! Please login to access 18,486+ medical records.', 'success');
                    setTimeout(() => {
                        switchTab('login');
                    }, 2000);
                } else {
                    showAlert(data.detail || 'Registration failed', 'error');
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'error');
            }
        }
        
        if (localStorage.getItem('authToken')) {
            window.location.href = '/dashboard';
        }
    </script>
</body>
</html>
    """

# Enhanced dashboard with Excel data search
@app.get("/dashboard", response_class=HTMLResponse, tags=[" Dashboard"])
async def dashboard():
    """Serve the protected dashboard"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> AYUSH Medical Portal - Excel Data Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            padding: 30px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        .header h1 { 
            color: #2c3e50; 
            font-size: 2.5rem; 
            margin-bottom: 10px; 
        }
        .header p { 
            color: #666; 
            font-size: 1.1rem; 
        }
        .user-info { 
            float: right; 
            background: #3498db; 
            color: white; 
            padding: 10px 15px; 
            border-radius: 20px; 
            font-size: 14px; 
            margin-bottom: 20px;
        }
        .logout-btn { 
            background: #e74c3c; 
            color: white; 
            border: none; 
            padding: 8px 12px; 
            border-radius: 15px; 
            cursor: pointer; 
            margin-left: 10px; 
            font-size: 12px;
        }
        .stats-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        .search-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .search-title {
            font-size: 1.5rem;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }
        .search-controls {
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 15px;
            align-items: end;
        }
        .form-group {
            display: flex;
            flex-direction: column;
        }
        .form-group label {
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 500;
        }
        .form-group input, .form-group select {
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
        }
        .btn {
            padding: 12px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #95a5a6;
        }
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        .results-section {
            margin-top: 20px;
        }
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .result-card {
            background: white;
            border: 1px solid #e1e8ed;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .result-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #2c3e50;
        }
        .result-system {
            background: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
        }
        .result-details {
            color: #666;
            line-height: 1.6;
        }
        .result-code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 14px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .no-results {
            text-align: center;
            padding: 40px;
            color: #666;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .download-section {
            background: #e8f5e8;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: center;
        }
        .download-btn {
            background: #27ae60;
            margin: 5px;
        }
        .download-btn:hover {
            background: #229954;
        }
        @media (max-width: 768px) {
            .search-controls {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="user-info">
             <span id="username"></span>
            <button class="logout-btn" onclick="logout()">Logout</button>
        </div>
        <div style="clear: both;"></div>
        
        <div class="header">
            <h1> AYUSH Medical Portal</h1>
            <p>Real Excel Data Integration - 18,486+ Medical Records</p>
        </div>
        
        <div class="stats-overview">
            <div class="stat-card">
                <div class="stat-number">2,893</div>
                <div class="stat-label"> Ayurveda Terms</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">1,926</div>
                <div class="stat-label"> Siddha Terms</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">2,522</div>
                <div class="stat-label"> Unani Terms</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">11,145</div>
                <div class="stat-label"> ICD10 Codes</div>
            </div>
        </div>
        
        <div class="search-section">
            <h2 class="search-title"> Search Medical Database</h2>
            <div class="search-controls">
                <div class="form-group">
                    <label for="search-term">Search Term</label>
                    <input type="text" id="search-term" placeholder="Enter medical term, condition, or code...">
                </div>
                <div class="form-group">
                    <label for="system-filter">Filter by System</label>
                    <select id="system-filter">
                        <option value="">All Systems</option>
                        <option value="ayurveda"> Ayurveda</option>
                        <option value="siddha"> Siddha</option>
                        <option value="unani"> Unani</option>
                        <option value="icd10"> ICD10</option>
                    </select>
                </div>
                <button class="btn" onclick="searchMedicalData()"> Search</button>
            </div>
        </div>
        
        <div class="download-section">
            <h3> Download Complete Datasets</h3>
            <button class="btn download-btn" onclick="downloadData('ayurveda')"> Download Ayurveda Data</button>
            <button class="btn download-btn" onclick="downloadData('siddha')"> Download Siddha Data</button>
            <button class="btn download-btn" onclick="downloadData('unani')"> Download Unani Data</button>
            <button class="btn download-btn" onclick="downloadData('icd10')"> Download ICD10 Data</button>
            <button class="btn download-btn" onclick="downloadData('all')"> Download All Data</button>
        </div>
        
        <div id="results-section" class="results-section" style="display: none;">
            <div class="results-header">
                <h3 id="results-title">Search Results</h3>
                <button class="btn btn-secondary" onclick="clearResults()">Clear Results</button>
            </div>
            <div id="results-container"></div>
        </div>
    </div>

    <script>
        // Check authentication
        const token = localStorage.getItem('authToken');
        const username = localStorage.getItem('username');
        
        if (!token || !username) {
            window.location.href = '/';
        }
        
        document.getElementById('username').textContent = username;
        
        function logout() {
            localStorage.removeItem('authToken');
            localStorage.removeItem('username');
            window.location.href = '/';
        }
        
        async function searchMedicalData() {
            const searchTerm = document.getElementById('search-term').value;
            const systemFilter = document.getElementById('system-filter').value;
            
            if (!searchTerm.trim()) {
                alert('Please enter a search term');
                return;
            }
            
            const resultsSection = document.getElementById('results-section');
            const resultsContainer = document.getElementById('results-container');
            
            resultsSection.style.display = 'block';
            resultsContainer.innerHTML = '<div class="loading"> Searching 18,486+ medical records...</div>';
            
            try {
                let url = `/search?q=${encodeURIComponent(searchTerm)}`;
                if (systemFilter) {
                    url += `&system=${systemFilter}`;
                }
                
                const response = await fetch(url, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!response.ok) {
                    throw new Error('Search failed');
                }
                
                const data = await response.json();
                displayResults(data.results, data.total_found);
                
            } catch (error) {
                resultsContainer.innerHTML = '<div class="no-results"> Search failed. Please try again.</div>';
            }
        }
        
        function displayResults(results, totalFound) {
            const resultsContainer = document.getElementById('results-container');
            const resultsTitle = document.getElementById('results-title');
            
            resultsTitle.textContent = `Search Results (${totalFound} found)`;
            
            if (results.length === 0) {
                resultsContainer.innerHTML = '<div class="no-results"> No results found. Try different search terms.</div>';
                return;
            }
            
            let html = '';
            results.forEach(result => {
                html += `
                    <div class="result-card">
                        <div class="result-header">
                            <div class="result-title">${result.name}</div>
                            <div class="result-system">${result.system}</div>
                        </div>
                        <div class="result-details">
                            <p><strong>Code:</strong> <span class="result-code">${result.code}</span></p>
                            ${result.sanskrit_name ? `<p><strong>Sanskrit:</strong> ${result.sanskrit_name}</p>` : ''}
                            ${result.devanagari ? `<p><strong>Devanagari:</strong> ${result.devanagari}</p>` : ''}
                            ${result.tamil_name ? `<p><strong>Tamil:</strong> ${result.tamil_name}</p>` : ''}
                            ${result.arabic_name ? `<p><strong>Arabic:</strong> ${result.arabic_name}</p>` : ''}
                            ${result.short_definition ? `<p><strong>Definition:</strong> ${result.short_definition}</p>` : ''}
                            ${result.long_definition ? `<p><strong>Details:</strong> ${result.long_definition}</p>` : ''}
                            ${result.block_title ? `<p><strong>Block:</strong> ${result.block_title}</p>` : ''}
                            ${result.chapter_name ? `<p><strong>Chapter:</strong> ${result.chapter_name}</p>` : ''}
                            <p><strong>Category:</strong> ${result.category}</p>
                        </div>
                    </div>
                `;
            });
            
            resultsContainer.innerHTML = html;
        }
        
        function clearResults() {
            document.getElementById('results-section').style.display = 'none';
            document.getElementById('search-term').value = '';
            document.getElementById('system-filter').value = '';
        }
        
        async function downloadData(system) {
            try {
                const response = await fetch(`/download/${system}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!response.ok) {
                    throw new Error('Download failed');
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `${system}_medical_data.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                alert(` ${system.toUpperCase()} data downloaded successfully!`);
                
            } catch (error) {
                alert(' Download failed. Please try again.');
            }
        }
        
        // Enable search on Enter key
        document.getElementById('search-term').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchMedicalData();
            }
        });
    </script>
</body>
</html>
    """

# Enhanced search endpoint
@app.get("/search", tags=[" Search"])
async def search_medical_data(
    q: str = Query(..., description="Search term"),
    system: str = Query("", description="Filter by system"),
    limit: int = Query(20, description="Maximum results"),
    current_user: dict = Depends(get_current_user)
):
    """Search across all medical data from Excel files"""
    try:
        search_term = q.lower()
        results = []
        
        # Search in all systems based on filter
        systems_to_search = [system] if system else ['ayurveda', 'siddha', 'unani', 'icd10']
        
        for sys in systems_to_search:
            if sys in MEDICAL_DATA:
                for record in MEDICAL_DATA[sys]:
                    # Search in multiple fields
                    searchable_text = " ".join([
                        record.get('name', '').lower(),
                        record.get('code', '').lower(),
                        record.get('sanskrit_name', '').lower(),
                        record.get('devanagari', '').lower(),
                        record.get('tamil_name', '').lower(),
                        record.get('arabic_name', '').lower(),
                        record.get('short_definition', '').lower(),
                        record.get('long_definition', '').lower(),
                        record.get('block_title', '').lower(),
                        record.get('chapter_name', '').lower()
                    ])
                    
                    if search_term in searchable_text:
                        results.append(record)
        
        # Sort by relevance (exact matches first)
        exact_matches = [r for r in results if search_term in r.get('name', '').lower()]
        partial_matches = [r for r in results if r not in exact_matches]
        
        sorted_results = exact_matches + partial_matches
        
        return {
            "results": sorted_results[:limit],
            "total_found": len(sorted_results),
            "search_term": q,
            "system_filter": system
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

# Enhanced download endpoints
@app.get("/download/{system}", tags=[" Download"])
async def download_medical_data(
    system: str,
    current_user: dict = Depends(get_current_user)
):
    """Download medical data as CSV"""
    try:
        if system == "all":
            # Combine all data
            all_data = []
            for sys_name, records in MEDICAL_DATA.items():
                all_data.extend(records)
            data_to_export = all_data
            filename = "all_medical_data.csv"
        elif system in MEDICAL_DATA:
            data_to_export = MEDICAL_DATA[system]
            filename = f"{system}_medical_data.csv"
        else:
            raise HTTPException(status_code=404, detail="System not found")
        
        if not data_to_export:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data_to_export[0].keys())
        writer.writeheader()
        writer.writerows(data_to_export)
        
        csv_content = output.getvalue()
        output.close()
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail="Download failed")

# Statistics endpoint
@app.get("/stats", tags=[" Statistics"])
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """Get database statistics"""
    try:
        stats = {}
        total_records = 0
        
        for system, records in MEDICAL_DATA.items():
            count = len(records)
            stats[system] = count
            total_records += count
        
        stats['total'] = total_records
        
        return {
            "statistics": stats,
            "systems": list(MEDICAL_DATA.keys()),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

if __name__ == "__main__":
    print(" Starting AYUSH Medical Portal with Excel Data Integration...")
    print(" Loading 18,486+ medical records from Excel files...")
    print(" Portal will be available at: http://localhost:8002")
    print(" Systems: Ayurveda, Siddha, Unani, ICD10")
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False)
