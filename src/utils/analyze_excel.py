"""
Excel Data Analysis Script for AYUSH Medical Portal
Analyzes the structure and content of the uploaded Excel files
"""

import pandas as pd
import json
import os

def analyze_excel_file(filename):
    """Analyze an Excel file and return its structure"""
    try:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {filename}")
        print(f"{'='*60}")
        
        # Read the Excel file
        df = pd.read_excel(filename)
        
        print(f" BASIC INFO:")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")
        print(f"   - File size: {os.path.getsize(filename)} bytes")
        
        print(f"\n COLUMN NAMES:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        print(f"\n DATA TYPES:")
        for col in df.columns:
            print(f"   - {col}: {df[col].dtype}")
        
        print(f"\n SAMPLE DATA (First 5 rows):")
        print(df.head().to_string())
        
        print(f"\n DATA SUMMARY:")
        # Show non-null counts
        print(df.info())
        
        print(f"\n UNIQUE VALUES (for key columns):")
        for col in df.columns:
            unique_count = df[col].nunique()
            if unique_count < 20 and unique_count > 1:
                print(f"   - {col}: {unique_count} unique values")
                print(f"     Values: {list(df[col].unique())[:10]}")
        
        return df
        
    except Exception as e:
        print(f" ERROR reading {filename}: {str(e)}")
        return None

def main():
    """Main analysis function"""
    files = [
        "Ayurveda.xls",
        "Sidhha.xls", 
        "Unani.xls",
        "ICD10.xls"
    ]
    
    all_data = {}
    
    print(" AYUSH MEDICAL DATA ANALYSIS")
    print("="*60)
    
    for filename in files:
        if os.path.exists(filename):
            df = analyze_excel_file(filename)
            if df is not None:
                all_data[filename] = df
        else:
            print(f" File not found: {filename}")
    
    # Summary across all files
    print(f"\n{'='*60}")
    print(" OVERALL SUMMARY")
    print(f"{'='*60}")
    
    total_rows = 0
    total_files = 0
    
    for filename, df in all_data.items():
        total_rows += len(df)
        total_files += 1
        print(f" {filename}: {len(df)} records")
    
    print(f"\n TOTALS:")
    print(f"   - Files processed: {total_files}")
    print(f"   - Total records: {total_rows}")
    
    # Save summary to JSON for easy access
    summary = {}
    for filename, df in all_data.items():
        summary[filename] = {
            "rows": len(df),
            "columns": list(df.columns),
            "sample_data": df.head(3).to_dict('records') if len(df) > 0 else []
        }
    
    with open("excel_analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n Analysis complete! Summary saved to 'excel_analysis_summary.json'")
    
    return all_data

if __name__ == "__main__":
    main()
