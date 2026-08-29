#!/usr/bin/env python3
"""
Alternative WHO Data Fetcher
Uses different endpoints and methods
"""

import requests
import json
import csv
import urllib3
import time
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

def fetch_who_data_alternative():
    """Alternative method to fetch WHO data"""
    
    print(" ALTERNATIVE WHO ICD-11 DATA FETCH")
    print("=" * 45)
    
    # Try different WHO endpoints
    endpoints = [
        {
            "name": "WHO ICD-11 Browser API",
            "url": "https://icd.who.int/browse11/l-m/en/JsonGetChildrenConcepts",
            "params": {"ConceptId": "455013390"}  # Root level
        },
        {
            "name": "WHO ICD-11 Public API",
            "url": "https://id.who.int/icd/release/11/2024-01/mms",
            "headers": {"Accept": "application/json"}
        },
        {
            "name": "WHO Foundation API",
            "url": "https://id.who.int/icd/entity",
            "headers": {"Accept": "application/json"}
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n Trying {endpoint['name']}...")
        
        try:
            response = requests.get(
                endpoint["url"],
                params=endpoint.get("params", {}),
                headers=endpoint.get("headers", {}),
                verify=False,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f" Success! Got data from {endpoint['name']}")
                    
                    # Save raw response
                    filename = endpoint['name'].lower().replace(' ', '_').replace('-', '_') + '.json'
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    print(f" Saved to: {filename}")
                    results.append({
                        "endpoint": endpoint['name'],
                        "status": "success",
                        "data_keys": list(data.keys()) if isinstance(data, dict) else "list",
                        "data_size": len(data) if isinstance(data, (list, dict)) else "unknown"
                    })
                    
                except json.JSONDecodeError:
                    print(f" Response not JSON from {endpoint['name']}")
                    # Save as text
                    filename = endpoint['name'].lower().replace(' ', '_') + '.txt'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f" Saved text response to: {filename}")
                    
            else:
                print(f" Failed: {response.status_code} - {response.text[:100]}...")
                results.append({
                    "endpoint": endpoint['name'],
                    "status": f"failed_{response.status_code}",
                    "error": response.text[:200]
                })
                
        except Exception as e:
            print(f" Error with {endpoint['name']}: {e}")
            results.append({
                "endpoint": endpoint['name'],
                "status": "error",
                "error": str(e)
            })
    
    # Create summary
    with open('who_endpoint_test_results.csv', 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n ENDPOINT TEST SUMMARY:")
    print("-" * 25)
    for result in results:
        print(f"• {result['endpoint']}: {result['status']}")
    
    print(f"\n Test results saved to: who_endpoint_test_results.csv")

def create_comprehensive_sample_data():
    """Create comprehensive sample WHO data based on real structure"""
    
    print(f"\n CREATING COMPREHENSIVE SAMPLE DATA")
    print("=" * 40)
    
    # Comprehensive WHO ICD-11 sample data
    comprehensive_data = {
        "infectious_diseases": [
            {"code": "1A00", "title": "Cholera", "definition": "Cholera is an acute diarrheal infection caused by ingestion of food or water contaminated with the bacterium Vibrio cholerae."},
            {"code": "1A20", "title": "Plague", "definition": "Plague is a disease that affects humans and other mammals. It is caused by the bacterium Yersinia pestis."},
            {"code": "1A40", "title": "Tularaemia", "definition": "Tularaemia is a disease caused by the bacterium Francisella tularensis."},
            {"code": "1B10", "title": "Pulmonary tuberculosis", "definition": "Pulmonary tuberculosis is tuberculosis that affects the lungs."},
            {"code": "1B20", "title": "Miliary tuberculosis", "definition": "Miliary tuberculosis is a form of tuberculosis that is characterized by a wide dissemination into the human body."},
            {"code": "1C60", "title": "Malaria", "definition": "Malaria is a mosquito-borne infectious disease affecting humans and other animals."},
            {"code": "1C62", "title": "Malaria due to Plasmodium falciparum", "definition": "Malaria caused by Plasmodium falciparum, the most severe form of malaria."},
            {"code": "1E50", "title": "Viral hepatitis A", "definition": "Hepatitis A is an infectious disease of the liver caused by hepatitis A virus."},
            {"code": "1E51", "title": "Viral hepatitis B", "definition": "Hepatitis B is an infectious disease caused by the hepatitis B virus."},
            {"code": "1E52", "title": "Viral hepatitis C", "definition": "Hepatitis C is an infectious disease caused by the hepatitis C virus."}
        ],
        "neoplasms": [
            {"code": "2A00.0", "title": "Malignant neoplasm of lip", "definition": "Primary malignant neoplasm of the lip."},
            {"code": "2A70", "title": "Malignant neoplasm of breast", "definition": "Primary malignant neoplasm arising in the breast."},
            {"code": "2A80", "title": "Malignant neoplasm of cervix uteri", "definition": "Primary malignant neoplasm of the cervix uteri."},
            {"code": "2B10", "title": "Malignant neoplasm of trachea, bronchus or lung", "definition": "Primary malignant neoplasm of the trachea, bronchus, or lung."},
            {"code": "2B90", "title": "Malignant neoplasm of stomach", "definition": "Primary malignant neoplasm of the stomach."}
        ],
        "endocrine_diseases": [
            {"code": "5A10", "title": "Type 1 diabetes mellitus", "definition": "Type 1 diabetes mellitus is a form of diabetes mellitus that results from autoimmune destruction of insulin-producing beta cells of the pancreas."},
            {"code": "5A11", "title": "Type 2 diabetes mellitus", "definition": "Type 2 diabetes mellitus is a metabolic disorder that is characterized by high blood glucose in the context of insulin resistance and relative insulin deficiency."},
            {"code": "5A14", "title": "Gestational diabetes mellitus", "definition": "Gestational diabetes mellitus is glucose intolerance with onset or first recognition during pregnancy."},
            {"code": "5A40", "title": "Thyrotoxicosis", "definition": "Thyrotoxicosis is the condition that occurs due to excessive thyroid hormone of any cause."},
            {"code": "5A60", "title": "Hypothyroidism", "definition": "Hypothyroidism is a condition in which the thyroid gland does not produce enough thyroid hormone."}
        ],
        "mental_disorders": [
            {"code": "6A70", "title": "Single episode depressive disorder", "definition": "Single episode depressive disorder is characterized by the presence or history of one depressive episode."},
            {"code": "6A71", "title": "Recurrent depressive disorder", "definition": "Recurrent depressive disorder is characterized by a history of at least two depressive episodes."},
            {"code": "6B00", "title": "Generalized anxiety disorder", "definition": "Generalized anxiety disorder is characterized by marked symptoms of anxiety that persist for at least several months."},
            {"code": "6B01", "title": "Panic disorder", "definition": "Panic disorder is characterized by recurrent unexpected panic attacks."},
            {"code": "6A02", "title": "Schizophrenia", "definition": "Schizophrenia is characterized by disturbances in multiple mental modalities."}
        ],
        "circulatory_diseases": [
            {"code": "BA00", "title": "Essential hypertension", "definition": "Essential hypertension is high blood pressure that doesn't have a known secondary cause."},
            {"code": "BA01", "title": "Hypertensive heart disease", "definition": "Hypertensive heart disease is heart disease caused by high blood pressure."},
            {"code": "BB10", "title": "Acute myocardial infarction", "definition": "Acute myocardial infarction is the medical name for a heart attack."},
            {"code": "BB90", "title": "Heart failure", "definition": "Heart failure is a condition in which the heart cannot pump enough blood to meet the body's needs."},
            {"code": "BC90", "title": "Stroke, not specified as haemorrhage or infarction", "definition": "Stroke of unspecified type."}
        ],
        "respiratory_diseases": [
            {"code": "CA40", "title": "Pneumonia", "definition": "Pneumonia is an inflammatory condition of the lung affecting primarily the small air sacs known as alveoli."},
            {"code": "CA80", "title": "Asthma", "definition": "Asthma is a respiratory condition marked by attacks of spasm in the bronchi of the lungs."},
            {"code": "CB03", "title": "Chronic obstructive pulmonary disease", "definition": "Chronic obstructive pulmonary disease is a type of obstructive lung disease."}
        ],
        "traditional_medicine": [
            {"code": "TM26.001", "title": "Traditional Medicine Pattern: Diabetes with Kidney Yang Deficiency", "definition": "A traditional medicine pattern characterized by diabetes mellitus with symptoms of kidney yang deficiency."},
            {"code": "TM26.002", "title": "Traditional Medicine Pattern: Hypertension with Liver Yang Rising", "definition": "Traditional Chinese Medicine pattern of hypertension characterized by liver yang hyperactivity."},
            {"code": "TM26.AY001", "title": "Ayurvedic Pattern: Madhumeha (Diabetes) - Vata-Kapha Type", "definition": "An Ayurvedic classification of diabetes characterized by Vata-Kapha dosha imbalance."},
            {"code": "TM26.AY002", "title": "Ayurvedic Pattern: Rajayakshma (Tuberculosis) - Vataja Type", "definition": "Ayurvedic classification of tuberculosis as Rajayakshma with predominant Vata dosha involvement."},
            {"code": "TM26.UN001", "title": "Unani Pattern: Ziabetus Shakari - Sanguine Temperament", "definition": "Unani medicine classification of diabetes associated with sanguine temperament."}
        ]
    }
    
    # Flatten all data
    all_conditions = []
    for category, conditions in comprehensive_data.items():
        for condition in conditions:
            condition["category"] = category
            condition["entity_id"] = f"http://id.who.int/icd/entity/{hash(condition['code']) % 1000000000}"
            condition["browser_url"] = f"https://icd.who.int/browse11/l-m/en#/{condition['entity_id']}"
            all_conditions.append(condition)
    
    # Create comprehensive CSV
    with open('who_comprehensive_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'category', 'code', 'title', 'definition', 'entity_id', 'browser_url'
        ])
        writer.writeheader()
        writer.writerows(all_conditions)
    
    print(f" Created who_comprehensive_data.csv ({len(all_conditions)} conditions)")
    
    # Create category summary
    category_summary = []
    for category, conditions in comprehensive_data.items():
        category_summary.append({
            "category": category,
            "count": len(conditions),
            "sample_codes": ", ".join([c["code"] for c in conditions[:3]])
        })
    
    with open('who_categories_summary.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['category', 'count', 'sample_codes'])
        writer.writeheader()
        writer.writerows(category_summary)
    
    print(f" Created who_categories_summary.csv ({len(category_summary)} categories)")
    
    # Export JSON
    with open('who_comprehensive_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            "total_conditions": len(all_conditions),
            "categories": len(comprehensive_data),
            "data_by_category": comprehensive_data,
            "all_conditions": all_conditions,
            "metadata": {
                "source": "WHO ICD-11 comprehensive sample",
                "includes_traditional_medicine": True,
                "ayush_compatible": True
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f" Created who_comprehensive_data.json")
    
    print(f"\n COMPREHENSIVE DATA STATISTICS:")
    print(f"Total conditions: {len(all_conditions)}")
    print(f"Categories: {len(comprehensive_data)}")
    for category, conditions in comprehensive_data.items():
        print(f"• {category}: {len(conditions)} conditions")

if __name__ == "__main__":
    fetch_who_data_alternative()
    create_comprehensive_sample_data()
