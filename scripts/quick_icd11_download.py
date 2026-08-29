#!/usr/bin/env python3
"""
Quick ICD-11 Dataset Downloader - Optimized version
Downloads ICD-11 clinical terminology in efficient batches
"""

import requests
import json
import csv
import os

def download_icd11_quick():
    """Download ICD-11 dataset efficiently"""
    
    print(" Quick ICD-11 Clinical Terminology Download")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("data/external", exist_ok=True)
    output_file = "data/external/icd11_clinical_terminology_complete.csv"
    
    # Open CSV file for writing
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Code', 'Description'])  # Header
        
        offset = 0
        batch_size = 2000  # Larger batches for efficiency
        total_downloaded = 0
        
        while True:
            print(f" Downloading batch: offset {offset}")
            
            # API call
            url = f"https://datasets-server.huggingface.co/rows?dataset=manjunathshiva%2FICD11-Clinical-Terminology&config=default&split=train&offset={offset}&length={batch_size}"
            
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                rows = data.get('rows', [])
                if not rows:
                    break
                
                # Write rows to CSV
                for row_data in rows:
                    row = row_data.get('row', {})
                    writer.writerow([
                        row.get('Code', ''),
                        row.get('Description', '')
                    ])
                
                total_downloaded += len(rows)
                offset += len(rows)
                
                # Progress
                total_rows = data.get('num_rows_total', 0)
                if total_rows > 0:
                    progress = (total_downloaded / total_rows) * 100
                    print(f" Progress: {total_downloaded:,}/{total_rows:,} ({progress:.1f}%)")
                
                # Check if done
                if len(rows) < batch_size or total_downloaded >= total_rows:
                    break
                    
            except Exception as e:
                print(f" Error: {e}")
                break
    
    print(f"\n Download complete!")
    print(f" File saved: {output_file}")
    print(f" Total records: {total_downloaded:,}")
    
    return output_file

if __name__ == "__main__":
    download_icd11_quick()
