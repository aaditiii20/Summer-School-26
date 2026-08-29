import os

#  Root folder (change if needed)
root = os.path.join("CoreApplication", "api_new")

#  Define the new folders and files to create
structure = {
    "": ["main.py"],

    "routes": [
        "auth_routes.py",
        "consent_routes.py",
        "claim_routes.py",
        "analytics_routes.py",
        "offline_routes.py",
        "fhir_routes.py"
    ],

    "models": [
        "user_model.py",
        "patient_model.py",
        "claim_model.py",
        "consent_model.py",
        "__init__.py"
    ],

    "database": [
        "db_config.py",
        "fhir_schema.py"
    ],

    "utils": [
        "auth_utils.py",
        "rbac_utils.py",
        "security_utils.py",
        "mock_data.py"
    ],

    "tests": [
        "test_auth.py",
        "test_claims.py",
        "test_database.py"
    ]
}

#  Create folders and files
for folder, files in structure.items():
    folder_path = os.path.join(root, folder)
    os.makedirs(folder_path, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                pass  # Create empty file
            print(f"Created: {file_path}")
        else:
            print(f"Already exists: {file_path}")

print("\n Backend file structure created successfully!")
