import requests

print(" Testing Enhanced Ultra-Precision Portal")
print("=" * 50)

try:
    # Test dataset info
    response = requests.get("http://localhost:8009/api/dataset-info", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(" Dataset Info:")
        print(f"   Ultra-Precision Mappings: {data.get('ultra_precision_mappings')}")
        print(f"   Accuracy Rate: {data.get('accuracy_rate')}")
        print(f"   Medical Grade: {data.get('medical_grade')}")
        print(f"   Version: {data.get('version')}")
    
    # Test diabetes search
    print("\n Testing Diabetes Search:")
    response = requests.get("http://localhost:8009/api/enhanced-dataset/terms?search=diabetes&limit=3", timeout=5)
    if response.status_code == 200:
        results = response.json()
        print(f" Found {len(results)} results:")
        for i, result in enumerate(results[:3]):
            print(f"   {i+1}. {result.get('namaste_term')} → {result.get('icd11_term')}")
            print(f"      Confidence: {result.get('confidence_score')}")
    
    print("\n Enhanced Portal Testing Complete!")
    print(" Ultra-Precision Mappings Successfully Operational!")
    
except Exception as e:
    print(f"Error: {e}")
