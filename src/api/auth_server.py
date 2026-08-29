"""
AYUSH FHIR Terminology Microservice - WITH AUTHENTICATION
Beginner-friendly website with login/signup and search interface
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=" AYUSH Medical Search Portal",
    description="Secure medical terminology search with WHO ICD-11 and Traditional Indian Medicine (AYUSH)",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory user storage (in production, use a proper database)
USERS_DB = {}
SESSIONS = {}

# Security
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = "ayush_fhir_2025"
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

# Load WHO data (same as before)
def load_who_data():
    """Load WHO ICD-11 data from JSON file"""
    try:
        with open("data/who_comprehensive_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        all_conditions = []
        if 'who_icd11_comprehensive' in data:
            for category, conditions in data['who_icd11_comprehensive'].items():
                for condition in conditions:
                    condition['category'] = category.replace('_', ' ').title()
                    all_conditions.append(condition)
        
        logger.info(f"Loaded {len(all_conditions)} WHO conditions from JSON")
        return all_conditions
        
    except Exception as e:
        logger.error(f"Failed to load WHO data: {e}")
        return []

# Load NAMASTE data (same expanded version as before)
def load_namaste_data():
    """Load expanded NAMASTE data"""
    conditions = {
        "NAM-COND-001": {
            "namaste_code": "NAM-COND-001",
            "name": "Vata Dosha Imbalance",
            "sanskrit_name": "Vata Vikruti",
            "description": "Constitutional imbalance characterized by dryness, coldness, and irregularity",
            "symptoms": ["Joint pain", "Constipation", "Anxiety", "Insomnia", "Dry skin", "Tremors"],
            "category": "Constitutional Disorders",
            "icd11_mapping": "ZA00.0Y",
            "severity": "mild_to_severe",
            "system": "Ayurveda"
        },
        "NAM-COND-002": {
            "namaste_code": "NAM-COND-002",
            "name": "Madhumeha (Diabetes)",
            "sanskrit_name": "Madhumeha",
            "description": "Metabolic disorder characterized by excessive urination and sweet urine",
            "symptoms": ["Excessive urination", "Excessive thirst", "Weight loss", "Fatigue", "Blurred vision"],
            "category": "Metabolic Disorders",
            "icd11_mapping": "5A14",
            "severity": "moderate_to_severe",
            "system": "Ayurveda"
        },
        # Add more conditions...
    }
    
    medicines = {
        "NAM-MED-001": {
            "namaste_code": "NAM-MED-001",
            "name": "Ashwagandha",
            "sanskrit_name": "Ashvagandha",
            "scientific_name": "Withania somnifera",
            "indications": ["Stress", "Weakness", "Insomnia", "Immunity", "Arthritis"],
            "category": "Rasayana (Rejuvenative)",
            "dosage": "1-3g twice daily",
            "system": "Ayurveda"
        }
        # Add more medicines...
    }
    
    procedures = {
        "NAM-PROC-001": {
            "namaste_code": "NAM-PROC-001",
            "name": "Panchakarma",
            "sanskrit_name": "Panchakarma",
            "description": "Five-action purification and detoxification therapy",
            "indications": ["Chronic diseases", "Detoxification", "Rejuvenation"],
            "category": "Shodhana (Purification)",
            "duration": "14-21 days",
            "system": "Ayurveda"
        }
        # Add more procedures...
    }
    
    return {
        "conditions": conditions,
        "medicines": medicines,
        "procedures": procedures
    }

# Global data variables
WHO_DATA = []
NAMASTE_DATA = {}

# Initialize data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    global WHO_DATA, NAMASTE_DATA
    WHO_DATA = load_who_data()
    NAMASTE_DATA = load_namaste_data()
    logger.info(f"Loaded {len(WHO_DATA)} WHO conditions and {len(NAMASTE_DATA['conditions'])} NAMASTE conditions")

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
    
    # Store user
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
    
    # Create session
    token = create_session(username)
    
    return {
        "message": "Login successful",
        "token": token,
        "username": username,
        "redirect": "/dashboard"
    }

@app.post("/logout", tags=[" Authentication"])
async def logout(token: str = Form(...)):
    """Logout user and destroy session"""
    if token in SESSIONS:
        del SESSIONS[token]
    
    return {"message": "Logout successful"}

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

# Landing page with login/signup
@app.get("/", response_class=HTMLResponse, tags=[" Landing"])
async def landing_page():
    """Serve the landing page with login/signup"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> AYUSH Medical Search Portal</title>
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
        .features { 
            margin-top: 30px; 
            padding-top: 20px; 
            border-top: 1px solid #e1e8ed; 
        }
        .features h3 { 
            color: #2c3e50; 
            margin-bottom: 15px; 
            text-align: center; 
        }
        .feature-list { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 10px; 
        }
        .feature-item { 
            background: #f8f9fa; 
            padding: 10px; 
            border-radius: 8px; 
            font-size: 14px; 
            text-align: center; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> AYUSH Portal</h1>
            <p>Medical terminology search for WHO ICD-11 & Traditional Medicine</p>
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
                <button type="submit" class="btn"> Login</button>
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
        
        <div class="features">
            <h3> Features</h3>
            <div class="feature-list">
                <div class="feature-item"> WHO ICD-11 Search</div>
                <div class="feature-item"> AYUSH Terminology</div>
                <div class="feature-item"> CSV Downloads</div>
                <div class="feature-item"> Smart Search</div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tab) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update form containers
            document.querySelectorAll('.form-container').forEach(f => f.classList.remove('active'));
            document.getElementById(tab + '-form').classList.add('active');
            
            // Clear alerts
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
                    showAlert('Login successful! Redirecting...', 'success');
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('username', data.username);
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
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
                    showAlert('Registration successful! Please login.', 'success');
                    setTimeout(() => {
                        switchTab('login');
                    }, 1500);
                } else {
                    showAlert(data.detail || 'Registration failed', 'error');
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'error');
            }
        }
        
        // Check if already logged in
        if (localStorage.getItem('authToken')) {
            window.location.href = '/dashboard';
        }
    </script>
</body>
</html>
    """

# Protected dashboard
@app.get("/dashboard", response_class=HTMLResponse, tags=[" Dashboard"])
async def dashboard():
    """Serve the protected dashboard"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> AYUSH Medical Search Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #f8f9fa; 
            line-height: 1.6; 
        }
        .navbar { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 15px 0; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .nav-container { 
            max-width: 1200px; 
            margin: 0 auto; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 0 20px; 
        }
        .nav-brand { 
            color: white; 
            font-size: 1.5rem; 
            font-weight: bold; 
        }
        .nav-user { 
            color: white; 
            display: flex; 
            align-items: center; 
            gap: 15px; 
        }
        .logout-btn { 
            background: rgba(255,255,255,0.2); 
            color: white; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 20px; 
            cursor: pointer; 
            transition: all 0.3s ease; 
        }
        .logout-btn:hover { 
            background: rgba(255,255,255,0.3); 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 30px 20px; 
        }
        .welcome-section { 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            margin-bottom: 30px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
            text-align: center; 
        }
        .welcome-section h1 { 
            color: #2c3e50; 
            margin-bottom: 10px; 
        }
        .welcome-section p { 
            color: #666; 
            font-size: 1.1rem; 
        }
        .search-section { 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            margin-bottom: 30px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
        }
        .search-section h2 { 
            color: #2c3e50; 
            margin-bottom: 20px; 
            text-align: center; 
        }
        .search-input { 
            width: 100%; 
            padding: 15px; 
            border: 2px solid #e1e8ed; 
            border-radius: 10px; 
            font-size: 16px; 
            margin-bottom: 20px; 
        }
        .search-input:focus { 
            outline: none; 
            border-color: #3498db; 
        }
        .search-buttons { 
            display: flex; 
            gap: 10px; 
            flex-wrap: wrap; 
            justify-content: center; 
            margin-bottom: 20px; 
        }
        .search-btn { 
            background: #3498db; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 8px; 
            font-size: 14px; 
            cursor: pointer; 
            transition: all 0.3s ease; 
        }
        .search-btn:hover { 
            background: #2980b9; 
            transform: translateY(-2px); 
        }
        .quick-search { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 10px; 
            margin-top: 20px; 
        }
        .quick-btn { 
            background: #ecf0f1; 
            color: #2c3e50; 
            padding: 12px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 14px; 
            transition: all 0.3s ease; 
        }
        .quick-btn:hover { 
            background: #d5dbdb; 
            transform: translateY(-1px); 
        }
        .download-section { 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            margin-bottom: 30px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
        }
        .download-section h2 { 
            color: #2c3e50; 
            margin-bottom: 20px; 
            text-align: center; 
        }
        .download-buttons { 
            display: flex; 
            gap: 15px; 
            flex-wrap: wrap; 
            justify-content: center; 
        }
        .download-btn { 
            padding: 15px 30px; 
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            cursor: pointer; 
            transition: all 0.3s ease; 
            color: white; 
            font-weight: 600; 
        }
        .download-btn.who { background: #e74c3c; }
        .download-btn.ayush { background: #f39c12; }
        .download-btn.combined { background: #27ae60; }
        .download-btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(0,0,0,0.3); 
        }
        .results { 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            margin-top: 20px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
            display: none; 
        }
        .result-item { 
            padding: 20px; 
            border-left: 4px solid #3498db; 
            margin-bottom: 15px; 
            background: #f8f9fa; 
            border-radius: 0 8px 8px 0; 
        }
        .result-title { 
            font-weight: bold; 
            color: #2c3e50; 
            font-size: 1.2rem; 
            margin-bottom: 5px; 
        }
        .result-code { 
            color: #e74c3c; 
            font-family: monospace; 
            font-size: 0.9rem; 
        }
        .result-description { 
            color: #666; 
            margin-top: 8px; 
        }
        .loading { 
            text-align: center; 
            color: #666; 
            padding: 40px; 
            font-size: 1.1rem; 
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            padding: 20px; 
            border-radius: 10px; 
            margin-top: 15px; 
        }
        .stats-section { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px; 
            border-radius: 15px; 
            text-align: center; 
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-top: 20px; 
        }
        .stat-item { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 10px; 
        }
        .stat-number { 
            font-size: 2rem; 
            font-weight: bold; 
            margin-bottom: 5px; 
        }
        .stat-label { 
            font-size: 0.9rem; 
            opacity: 0.9; 
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-brand"> AYUSH Medical Portal</div>
            <div class="nav-user">
                <span>Welcome, <span id="username">User</span>!</span>
                <button class="logout-btn" onclick="logout()"> Logout</button>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="welcome-section">
            <h1> Welcome to Your Medical Search Dashboard</h1>
            <p>Access comprehensive medical terminology from WHO ICD-11 and Traditional Indian Medicine (AYUSH)</p>
        </div>
        
        <div class="search-section">
            <h2> Search Medical Conditions</h2>
            <input type="text" id="search-input" class="search-input" placeholder="Type any medical condition, symptom, or disease name...">
            
            <div class="search-buttons">
                <button class="search-btn" onclick="searchAll()"> Search All Systems</button>
                <button class="search-btn" onclick="searchWHO()">WHO ICD-11 Only</button>
                <button class="search-btn" onclick="searchAYUSH()">AYUSH Only</button>
            </div>
            
            <div class="quick-search">
                <button class="quick-btn" onclick="quickSearch('diabetes')"> Diabetes</button>
                <button class="quick-btn" onclick="quickSearch('hypertension')"> Hypertension</button>
                <button class="quick-btn" onclick="quickSearch('arthritis')"> Arthritis</button>
                <button class="quick-btn" onclick="quickSearch('asthma')"> Asthma</button>
                <button class="quick-btn" onclick="quickSearch('depression')"> Depression</button>
                <button class="quick-btn" onclick="quickSearch('vata')"> Vata Dosha</button>
            </div>
        </div>
        
        <div class="download-section">
            <h2> Download Medical Datasets</h2>
            <p style="text-align: center; color: #666; margin-bottom: 20px;">Export comprehensive medical terminology data for research and analysis</p>
            
            <div class="download-buttons">
                <button class="download-btn who" onclick="downloadCSV('who')"> WHO ICD-11 CSV</button>
                <button class="download-btn ayush" onclick="downloadCSV('namaste')"> AYUSH Traditional CSV</button>
                <button class="download-btn combined" onclick="downloadCSV('combined')"> Combined Dataset CSV</button>
            </div>
        </div>
        
        <div class="stats-section">
            <h2> Database Statistics</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number" id="who-count">41</div>
                    <div class="stat-label">WHO ICD-11 Conditions</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="ayush-count">25+</div>
                    <div class="stat-label">AYUSH Conditions</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="medicine-count">13+</div>
                    <div class="stat-label">Traditional Medicines</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="procedure-count">16+</div>
                    <div class="stat-label">Therapeutic Procedures</div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="results" class="results">
        <h3>Search Results</h3>
        <div id="results-content"></div>
    </div>

    <script>
        // Check authentication
        const token = localStorage.getItem('authToken');
        const username = localStorage.getItem('username');
        
        if (!token) {
            window.location.href = '/';
        }
        
        document.getElementById('username').textContent = username || 'User';
        
        function logout() {
            localStorage.removeItem('authToken');
            localStorage.removeItem('username');
            window.location.href = '/';
        }
        
        function quickSearch(term) {
            document.getElementById('search-input').value = term;
            searchAll();
        }
        
        async function searchAll() {
            const query = document.getElementById('search-input').value.trim();
            if (!query) {
                alert('Please enter a search term');
                return;
            }
            
            showLoading();
            
            try {
                const [whoResponse, ayushResponse] = await Promise.all([
                    fetch(`/who/search?query=${encodeURIComponent(query)}`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }),
                    fetch(`/namaste/search?query=${encodeURIComponent(query)}&type=conditions`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    })
                ]);
                
                const whoData = await whoResponse.json();
                const ayushData = await ayushResponse.json();
                
                displayAllResults(whoData, ayushData, query);
            } catch (error) {
                showError('Search failed. Please check your connection and try again.');
            }
        }
        
        async function searchWHO() {
            const query = document.getElementById('search-input').value.trim();
            if (!query) return;
            
            showLoading();
            
            try {
                const response = await fetch(`/who/search?query=${encodeURIComponent(query)}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                displayWHOResults(data, query);
            } catch (error) {
                showError('WHO search failed. Please try again.');
            }
        }
        
        async function searchAYUSH() {
            const query = document.getElementById('search-input').value.trim();
            if (!query) return;
            
            showLoading();
            
            try {
                const response = await fetch(`/namaste/search?query=${encodeURIComponent(query)}&type=conditions`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                displayAYUSHResults(data, query);
            } catch (error) {
                showError('AYUSH search failed. Please try again.');
            }
        }
        
        function downloadCSV(type) {
            const urls = {
                'who': '/export/csv/who',
                'namaste': '/export/csv/namaste',
                'combined': '/export/csv/combined'
            };
            
            const names = {
                'who': 'WHO ICD-11',
                'namaste': 'NAMASTE AYUSH',
                'combined': 'Combined WHO + AYUSH'
            };
            
            if (urls[type]) {
                showLoading();
                document.getElementById('results-content').innerHTML = `
                    <div class="loading"> Preparing ${names[type]} CSV download...</div>
                    <div style="margin-top: 15px; padding: 15px; background: #e8f5e8; border-radius: 6px;">
                        <strong>Download Started!</strong><br>
                        Your CSV file should download automatically.
                    </div>
                `;
                
                // Create download link with authentication
                const link = document.createElement('a');
                link.href = urls[type] + `?token=${token}`;
                link.download = '';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        }
        
        function displayAllResults(whoData, ayushData, query) {
            let html = `<h4>Results for "${query}"</h4>`;
            
            if (whoData.results && whoData.results.length > 0) {
                html += '<h5> WHO ICD-11 Results</h5>';
                whoData.results.slice(0, 5).forEach(item => {
                    html += createResultItem(item, 'WHO');
                });
            }
            
            if (ayushData.results && ayushData.results.length > 0) {
                html += '<h5> AYUSH Traditional Medicine Results</h5>';
                ayushData.results.slice(0, 5).forEach(item => {
                    html += createResultItem(item, 'AYUSH');
                });
            }
            
            if ((!whoData.results || whoData.results.length === 0) && 
                (!ayushData.results || ayushData.results.length === 0)) {
                html += '<div class="result-item">No results found. Try different keywords.</div>';
            }
            
            document.getElementById('results-content').innerHTML = html;
            document.getElementById('results').style.display = 'block';
        }
        
        function displayWHOResults(data, query) {
            let html = `<h4>WHO ICD-11 Results for "${query}"</h4>`;
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(item => {
                    html += createResultItem(item, 'WHO');
                });
            } else {
                html += '<div class="result-item">No WHO results found.</div>';
            }
            
            document.getElementById('results-content').innerHTML = html;
            document.getElementById('results').style.display = 'block';
        }
        
        function displayAYUSHResults(data, query) {
            let html = `<h4>AYUSH Results for "${query}"</h4>`;
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(item => {
                    html += createResultItem(item, 'AYUSH');
                });
            } else {
                html += '<div class="result-item">No AYUSH results found.</div>';
            }
            
            document.getElementById('results-content').innerHTML = html;
            document.getElementById('results').style.display = 'block';
        }
        
        function createResultItem(item, type) {
            const code = type === 'WHO' ? item.code : item.namaste_code;
            const symptoms = item.symptoms ? item.symptoms.join(', ') : '';
            
            return `
                <div class="result-item">
                    <div class="result-title">${item.name}</div>
                    <div class="result-code">${type} Code: ${code}</div>
                    <div class="result-description">${item.description}</div>
                    ${symptoms ? `<div style="color: #27ae60; font-size: 0.9rem; margin-top: 5px;">Symptoms: ${symptoms}</div>` : ''}
                </div>
            `;
        }
        
        function showLoading() {
            document.getElementById('results-content').innerHTML = '<div class="loading"> Searching medical databases...</div>';
            document.getElementById('results').style.display = 'block';
        }
        
        function showError(message) {
            document.getElementById('results-content').innerHTML = `<div class="error">${message}</div>`;
            document.getElementById('results').style.display = 'block';
        }
        
        // Enter key search
        document.getElementById('search-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchAll();
            }
        });
        
        // Load statistics
        fetch('/stats', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.namaste) {
                document.getElementById('ayush-count').textContent = Object.keys(data.namaste.conditions || {}).length;
                document.getElementById('medicine-count').textContent = Object.keys(data.namaste.medicines || {}).length;
                document.getElementById('procedure-count').textContent = Object.keys(data.namaste.procedures || {}).length;
            }
            if (data.who) {
                document.getElementById('who-count').textContent = data.who.length;
            }
        })
        .catch(() => {
            // Fallback numbers
            document.getElementById('ayush-count').textContent = '25+';
            document.getElementById('medicine-count').textContent = '13+';
            document.getElementById('procedure-count').textContent = '16+';
        });
    </script>
</body>
</html>
    """

# Protected search endpoints (same as before but with authentication)
@app.get("/who/search", tags=["WHO ICD-11"])
async def search_who_data(
    query: str = Query(..., min_length=2),
    current_user: dict = Depends(get_current_user)
):
    """Search WHO ICD-11 data (protected)"""
    results = []
    query_lower = query.lower()
    
    for condition in WHO_DATA:
        searchable_text = f"{condition.get('name', '')} {condition.get('description', '')} {' '.join(condition.get('symptoms', []))}"
        if query_lower in searchable_text.lower():
            results.append(condition)
        
        if len(results) >= 10:
            break
    
    return {
        "query": query,
        "total_results": len(results),
        "results": results,
        "user": current_user["username"]
    }

@app.get("/namaste/search", tags=["NAMASTE AYUSH"])
async def search_namaste_data(
    query: str = Query(..., min_length=2),
    type: str = Query("conditions", regex="^(conditions|medicines|procedures|all)$"),
    current_user: dict = Depends(get_current_user)
):
    """Search NAMASTE AYUSH data (protected)"""
    results = []
    query_lower = query.lower()
    
    search_data = {}
    if type == "conditions" or type == "all":
        search_data.update(NAMASTE_DATA["conditions"])
    if type == "medicines" or type == "all":
        search_data.update(NAMASTE_DATA["medicines"])
    if type == "procedures" or type == "all":
        search_data.update(NAMASTE_DATA["procedures"])
    
    for code, item in search_data.items():
        searchable_text = f"{item.get('name', '')} {item.get('description', '')} {item.get('sanskrit_name', '')}"
        if 'symptoms' in item:
            searchable_text += f" {' '.join(item['symptoms'])}"
        if 'indications' in item:
            searchable_text += f" {' '.join(item['indications'])}"
        
        if query_lower in searchable_text.lower():
            results.append(item)
        
        if len(results) >= 10:
            break
    
    return {
        "query": query,
        "type": type,
        "total_results": len(results),
        "results": results,
        "user": current_user["username"]
    }

# CSV export endpoints (protected)
@app.get("/export/csv/who", tags=[" Data Export"])
async def export_who_csv(
    current_user: dict = Depends(get_current_user)
):
    """Export WHO ICD-11 data as CSV file (protected)"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "WHO_Code", "Name", "Description", "Category", "Symptoms", 
        "ICD11_Code", "System", "Data_Source"
    ])
    
    for condition in WHO_DATA:
        symptoms = "; ".join(condition.get("symptoms", []))
        writer.writerow([
            condition.get("code", ""),
            condition.get("name", ""),
            condition.get("description", ""),
            condition.get("category", ""),
            symptoms,
            condition.get("icd11_code", ""),
            "WHO ICD-11",
            "WHO International Classification of Diseases"
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.StringIO(output.getvalue()), 
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=who_icd11_conditions.csv"}
    )

# Statistics endpoint (protected)
@app.get("/stats", tags=[" Statistics"])
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """Get database statistics (protected)"""
    return {
        "who": WHO_DATA,
        "namaste": NAMASTE_DATA,
        "user": current_user["username"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
