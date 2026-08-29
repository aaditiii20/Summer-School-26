#!/usr/bin/env python3
"""
ICD-11 Dataset Downloader - Working version with small batches
Downloads complete ICD-11 clinical terminology dataset
"""

import requests
import csv
import os
import time

def download_icd11_complete():
    """Download complete ICD-11 dataset with small batches"""
    
    print(" ICD-11 Clinical Terminology Complete Download")
    print("Using batch size 100 (confirmed working)")
    print("=" * 55)
    
    # Create output directory
    os.makedirs("data/external", exist_ok=True)
    output_file = "data/external/icd11_clinical_terminology_complete.csv"
    
    # Open CSV file for writing
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Code', 'Description'])  # Header
        
        offset = 0
        batch_size = 100  # Use working batch size
        total_downloaded = 0
        total_rows = None
        
        while True:
            print(f" Batch {offset//batch_size + 1}: downloading records {offset}-{offset+batch_size-1}")
            
            # API call with confirmed working parameters
            url = f"https://datasets-server.huggingface.co/rows?dataset=manjunathshiva%2FICD11-Clinical-Terminology&config=default&split=train&offset={offset}&length={batch_size}"
            
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Get total on first call
                if total_rows is None:
                    total_rows = data.get('num_rows_total', 0)
                    print(f" Total dataset size: {total_rows:,} records")
                    print(f" Estimated download time: {(total_rows/batch_size * 0.5):.1f} seconds")
                    print("-" * 55)
                
                rows = data.get('rows', [])
                if not rows:
                    print(" No more data available")
                    break
                
                # Write rows to CSV
                for row_data in rows:
                    row = row_data.get('row', {})
                    writer.writerow([
                        row.get('Code', '').strip(),
                        row.get('Description', '').strip()
                    ])
                
                total_downloaded += len(rows)
                offset += len(rows)
                
                # Progress update every 10 batches
                if (offset // batch_size) % 10 == 0:
                    if total_rows > 0:
                        progress = (total_downloaded / total_rows) * 100
                        print(f" Progress: {total_downloaded:,}/{total_rows:,} ({progress:.1f}%)")
                
                # Check if we're done
                if len(rows) < batch_size or (total_rows and total_downloaded >= total_rows):
                    break
                
                # Small delay to be respectful to API
                time.sleep(0.1)
                    
            except Exception as e:
                print(f" Error at offset {offset}: {e}")
                break
    
    print("\n" + "=" * 55)
    print(f" Download complete!")
    print(f" File saved: {output_file}")
    print(f" Total records downloaded: {total_downloaded:,}")
    
    # Verify file
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / 1024 / 1024  # MB
        print(f" File size: {file_size:.2f} MB")
        
        # Count lines to verify
        with open(output_file, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f) - 1  # Subtract header
        print(f" Verified: {line_count:,} records in CSV file")
    
    return output_file

if __name__ == "__main__":
    download_icd11_complete()
