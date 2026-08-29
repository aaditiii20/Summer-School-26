#!/usr/bin/env python3
"""
ICD-11 Clinical Terminology Dataset Downloader
Downloads complete dataset from Hugging Face and saves as CSV
"""

import requests
import pandas as pd
import json
import time
from typing import List, Dict

def fetch_icd11_batch(offset: int, length: int = 1000) -> Dict:
    """Fetch a batch of ICD-11 data from Hugging Face API"""
    url = "https://datasets-server.huggingface.co/rows"
    params = {
        "dataset": "manjunathshiva/ICD11-Clinical-Terminology",
        "config": "default",
        "split": "train",
        "offset": offset,
        "length": length
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching batch at offset {offset}: {e}")
        return None

def download_complete_icd11_dataset() -> pd.DataFrame:
    """Download the complete ICD-11 dataset"""
    all_rows = []
    offset = 0
    batch_size = 1000
    total_rows = None
    
    print(" Starting ICD-11 Clinical Terminology Dataset Download")
    print("=" * 60)
    
    while True:
        print(f" Fetching batch: offset {offset}, size {batch_size}")
        
        batch_data = fetch_icd11_batch(offset, batch_size)
        if not batch_data:
            print(f" Failed to fetch batch at offset {offset}")
            break
            
        # Get total rows from first batch
        if total_rows is None:
            total_rows = batch_data.get('num_rows_total', 0)
            print(f" Total rows to download: {total_rows:,}")
        
        # Extract rows
        rows = batch_data.get('rows', [])
        if not rows:
            print(" No more data to fetch")
            break
            
        # Process rows
        for row_data in rows:
            row = row_data.get('row', {})
            all_rows.append({
                'Code': row.get('Code', ''),
                'Description': row.get('Description', '')
            })
        
        # Update offset
        offset += len(rows)
        
        # Progress update
        progress = (offset / total_rows * 100) if total_rows > 0 else 0
        print(f" Progress: {offset:,}/{total_rows:,} ({progress:.1f}%)")
        
        # Check if we've got all data
        if offset >= total_rows:
            break
            
        # Small delay to be respectful to the API
        time.sleep(0.1)
    
    print(f" Download complete! Retrieved {len(all_rows):,} records")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_rows)
    return df

def main():
    """Main function to download and save ICD-11 dataset"""
    try:
        # Download dataset
        df = download_complete_icd11_dataset()
        
        # Save as CSV
        output_file = "data/external/icd11_clinical_terminology_complete.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print("\n" + "=" * 60)
        print(" Dataset Information:")
        print(f"   • Total records: {len(df):,}")
        print(f"   • Columns: {list(df.columns)}")
        print(f"   • Output file: {output_file}")
        print(f"   • File size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # Show sample data
        print("\n Sample Records:")
        print(df.head(10).to_string(index=False))
        
        # Show statistics
        print(f"\n Statistics:")
        print(f"   • Unique codes: {df['Code'].nunique():,}")
        print(f"   • Average description length: {df['Description'].str.len().mean():.1f} chars")
        print(f"   • Longest description: {df['Description'].str.len().max()} chars")
        
        print("\n ICD-11 Clinical Terminology dataset successfully downloaded!")
        
    except Exception as e:
        print(f" Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
