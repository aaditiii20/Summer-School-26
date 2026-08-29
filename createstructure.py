import os

root = ""; 

folders = [
    "data_preprocessing",
    "mapping_algorithm",
    "model",
    "testing",
    "chatbot_simulation",
    "backend/api",
    "backend/models",
    "frontend/src/components",
    "frontend/src/services",
    "frontend/public",
    "docs"
]

files = [
    # Data Preprocessing
    "data_preprocessing/extract_mappings.py",
    "data_preprocessing/create_training_dataset.py",
    "data_preprocessing/validation_dataset.py",

    # Mapping Algorithm Development
    "mapping_algorithm/string_similarity.py",
    "mapping_algorithm/semantic_similarity.py",
    "mapping_algorithm/rule_based_mapping.py",
    "mapping_algorithm/confidence_scoring.py",

    # Model Architecture & Training Pipeline
    "model/neural_network.py",
    "model/random_forest.py",
    "model/ensemble.py",
    "model/train.py",
    "model/evaluate.py",
    "model/hyperparameter_tuning.py",
    "model/versioning.py",
    
    # Testing
    "testing/test_model.py",
    "testing/result_analysis.py",
    "testing/test_fhir_integration.py",
    
    # Chatbot Simulation
    "chatbot_simulation/chatbot_ui.py",
    "chatbot_simulation/chatbot_logic.py",

    # Backend
    "backend/api/fhir_endpoints.py",
    "backend/api/auth_oauth2.py",
    "backend/api/audit.py",
    "backend/api/concept_map.py",
    "backend/app.py",
    "backend/requirements.txt",
    
    # Frontend
    "frontend/src/App.js",
    "frontend/src/index.js",
    "frontend/src/components/SearchComponent.js",
    "frontend/src/services/api.js",
    "frontend/public/index.html",

    # Documentation
    "docs/design.md",
    "docs/api_spec.md",
    "docs/ehr_standards.md",
    "docs/user_manual.md",

    "README.md"
]

file_path = "path/to/your/file.txt"

directory = os.path.dirname(file_path)

os.makedirs(directory, exist_ok=True)

if not os.path.exists(file_path):
    with open(file_path, 'w') as f:
        f.write("This is a new file.")

print("File and directory structure created.")
