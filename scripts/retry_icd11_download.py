#!/usr/bin/env python3
"""
ICD-11 Dataset Downloader - Rate limit aware version
Downloads complete ICD-11 clinical terminology dataset with retry logic
"""

import requests
import csv
import os
import time
from datetime import datetime

def download_icd11_with_retry():
    """Download complete ICD-11 dataset with rate limit handling"""
    
    print(" ICD-11 Clinical Terminology Download (Rate-Limit Aware)")
    print("Handles API rate limits with automatic retry")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("data/external", exist_ok=True)
    output_file = "data/external/icd11_clinical_terminology_complete.csv"
    
    # Check if file exists and get current progress
    start_offset = 0
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_lines = sum(1 for _ in f) - 1  # Subtract header
        start_offset = existing_lines
        print(f" Found existing file with {existing_lines:,} records")
        print(f" Resuming from offset {start_offset}")
        file_mode = 'a'  # Append mode
    else:
        file_mode = 'w'  # Write mode
    
    # Open CSV file
    with open(output_file, file_mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header only for new files
        if file_mode == 'w':
            writer.writerow(['Code', 'Description'])
        
        offset = start_offset
        batch_size = 100
        total_downloaded = start_offset
        total_rows = None
        retry_count = 0
        max_retries = 3
        
        while True:
            print(f" Batch {offset//batch_size + 1}: records {offset}-{offset+batch_size-1}")
            
            # API call
            url = f"https://datasets-server.huggingface.co/rows?dataset=manjunathshiva%2FICD11-Clinical-Terminology&config=default&split=train&offset={offset}&length={batch_size}"
            
            try:
                response = requests.get(url, timeout=30)
                
                if response.status_code == 429:  # Rate limit
                    retry_count += 1
                    if retry_count <= max_retries:
                        wait_time = 60 * retry_count  # Exponential backoff
                        print(f" Rate limit hit. Waiting {wait_time}s (attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f" Max retries exceeded. Stopping at {total_downloaded:,} records")
                        break
                
                response.raise_for_status()
                retry_count = 0  # Reset on success
                
                data = response.json()
                
                # Get total on first successful call
                if total_rows is None:
                    total_rows = data.get('num_rows_total', 0)
                    print(f" Total dataset size: {total_rows:,} records")
                    remaining = total_rows - start_offset
                    print(f" Remaining to download: {remaining:,} records")
                    print("-" * 60)
                
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
                        print(f" Time: {datetime.now().strftime('%H:%M:%S')}")
                
                # Check if we're done
                if len(rows) < batch_size or (total_rows and total_downloaded >= total_rows):
                    break
                
                # Respectful delay
                time.sleep(0.5)  # Increased delay to avoid rate limits
                    
            except Exception as e:
                print(f" Error at offset {offset}: {e}")
                retry_count += 1
                if retry_count <= max_retries:
                    wait_time = 30 * retry_count
                    print(f" Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f" Max retries exceeded. Stopping.")
                    break
    
    print("\n" + "=" * 60)
    print(f" Download session complete!")
    print(f" File saved: {output_file}")
    print(f" Total records in file: {total_downloaded:,}")
    
    if total_rows:
        completion = (total_downloaded / total_rows) * 100
        print(f" Dataset completion: {completion:.1f}%")
        if completion < 100:
            print(f" Run script again to continue downloading remaining {total_rows - total_downloaded:,} records")
    
    # Verify file
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / 1024 / 1024  # MB
        print(f" File size: {file_size:.2f} MB")
        
        # Show sample of latest data
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) > 5:
                print(f"\n Sample of latest records:")
                for line in lines[-5:]:
                    parts = line.strip().split(',', 1)
                    if len(parts) == 2:
                        print(f"   {parts[0]} - {parts[1][:50]}...")
    
    return output_file

if __name__ == "__main__":
    download_icd11_with_retry()
