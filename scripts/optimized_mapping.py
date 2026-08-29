#!/usr/bin/env python3
"""
Optimized NAMASTE-ICD11 Mapping Generator
Fast and efficient mapping with progress tracking and batch processing
"""

import pandas as pd
import re
import json
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional
import numpy as np
import time

class OptimizedMapper:
    def __init__(self):
        self.namaste_data = None
        self.icd11_data = None
        self.icd11_index = {}  # For faster lookups
        
        # Key medical terms for fast matching
        self.key_terms = {
            'diabetes': ['diabetes', 'madhumeha', 'prameha', 'mellitus', 'hyperglycemia'],
            'fever': ['fever', 'jwara', 'pyrexia', 'hyperthermia', 'temperature'],
            'pain': ['pain', 'vedana', 'ruja', 'shoola', 'ache', 'algia'],
            'infection': ['infection', 'krimi', 'bacterial', 'viral', 'sepsis'],
            'inflammation': ['inflammation', 'shotha', 'itis', 'swelling'],
            'disease': ['disease', 'roga', 'disorder', 'syndrome'],
            'blood': ['blood', 'rakta', 'hemato', 'anemia'],
            'heart': ['heart', 'hridaya', 'cardiac', 'cardio'],
            'liver': ['liver', 'yakrit', 'hepatic', 'hepato'],
            'kidney': ['kidney', 'vrikka', 'renal', 'nephro'],
            'skin': ['skin', 'tvak', 'derma', 'cutaneous'],
            'digestive': ['digestive', 'pachana', 'gastro', 'intestinal'],
            'respiratory': ['respiratory', 'shwasa', 'pulmonary', 'lung'],
            'nervous': ['nervous', 'nadi', 'neuro', 'mental'],
            'bone': ['bone', 'asthi', 'osteo', 'skeletal'],
            'muscle': ['muscle', 'mamsa', 'muscular', 'myalgia']
        }

    def load_data(self):
        """Load datasets with optimizations"""
        print(" Loading datasets...")
        
        # Load NAMASTE data
        namaste_file = "data/mapping/namaste_icd11_complete_7331_mappings.csv"
        self.namaste_data = pd.read_csv(namaste_file)
        print(f" Loaded {len(self.namaste_data)} NAMASTE records")
        
        # Load ICD-11 data with indexing
        icd11_file = "data/external/icd11_clinical_terminology_complete.csv"
        self.icd11_data = pd.read_csv(icd11_file)
        print(f" Loaded {len(self.icd11_data)} ICD-11 records")
        
        # Create search index for faster lookups
        print(" Creating search index...")
        self.create_search_index()
        
        return True

    def create_search_index(self):
        """Create keyword index for faster searching"""
        self.icd11_index = {}
        
        for idx, row in self.icd11_data.iterrows():
            desc = str(row['Description']).lower()
            words = re.findall(r'\w+', desc)
            
            for word in words:
                if len(word) >= 3:  # Only index meaningful words
                    if word not in self.icd11_index:
                        self.icd11_index[word] = []
                    self.icd11_index[word].append(idx)
        
        print(f" Search index created with {len(self.icd11_index)} keywords")

    def fast_similarity(self, namaste_term: str, icd11_term: str) -> float:
        """Fast similarity calculation"""
        if not namaste_term or not icd11_term:
            return 0.0
        
        # Convert to lowercase
        term1 = namaste_term.lower()
        term2 = icd11_term.lower()
        
        # Quick exact match
        if term1 == term2:
            return 1.0
        
        # Quick substring match
        if term1 in term2 or term2 in term1:
            return 0.8
        
        # Key term matching
        for category, terms in self.key_terms.items():
            if any(t in term1 for t in terms) and any(t in term2 for t in terms):
                return 0.7
        
        # Word overlap
        words1 = set(re.findall(r'\w+', term1))
        words2 = set(re.findall(r'\w+', term2))
        if words1 and words2:
            overlap = len(words1.intersection(words2)) / len(words1.union(words2))
            if overlap > 0.3:
                return overlap * 0.6
        
        return 0.0

    def find_fast_match(self, namaste_term: str) -> Tuple[Optional[str], Optional[str], float]:
        """Fast matching using index"""
        best_match = None
        best_code = None
        best_score = 0.0
        
        # Extract keywords from NAMASTE term
        words = re.findall(r'\w+', namaste_term.lower())
        candidate_indices = set()
        
        # Find candidates using index
        for word in words:
            if len(word) >= 3 and word in self.icd11_index:
                candidate_indices.update(self.icd11_index[word][:50])  # Limit candidates
        
        # If no index matches, try key terms
        if not candidate_indices:
            for category, terms in self.key_terms.items():
                if any(term in namaste_term.lower() for term in terms):
                    for word in terms:
                        if word in self.icd11_index:
                            candidate_indices.update(self.icd11_index[word][:20])
        
        # Score candidates
        for idx in list(candidate_indices)[:100]:  # Limit to top 100 candidates
            if idx < len(self.icd11_data):
                icd_row = self.icd11_data.iloc[idx]
                score = self.fast_similarity(namaste_term, str(icd_row['Description']))
                
                if score > best_score and score >= 0.3:
                    best_score = score
                    best_match = str(icd_row['Description'])
                    best_code = str(icd_row['Code'])
        
        return best_match, best_code, best_score

    def create_optimized_mappings(self):
        """Create mappings with optimization"""
        print(" Creating optimized NAMASTE-ICD11 mappings...")
        print(" Using indexed search and smart matching algorithms")
        
        mappings = []
        stats = {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        
        batch_size = 50
        start_time = time.time()
        
        for i in range(0, len(self.namaste_data), batch_size):
            batch_end = min(i + batch_size, len(self.namaste_data))
            batch_data = self.namaste_data.iloc[i:batch_end]
            
            # Process batch
            for idx, row in batch_data.iterrows():
                namaste_english = str(row.get('NAMASTE_Display', ''))
                namaste_traditional = str(row.get('Traditional_Name', ''))
                namaste_code = str(row.get('NAMASTE_Code', ''))
                namaste_system = str(row.get('System', 'Unknown'))
                
                # Search term combining English and traditional
                search_term = f"{namaste_english} {namaste_traditional}"
                icd11_desc, icd11_code, confidence = self.find_fast_match(search_term)
                
                # Classify confidence
                if confidence >= 0.7:
                    confidence_level = "High"
                    stats['high'] += 1
                elif confidence >= 0.5:
                    confidence_level = "Medium"
                    stats['medium'] += 1
                elif confidence >= 0.3:
                    confidence_level = "Low"
                    stats['low'] += 1
                else:
                    confidence_level = "No Match"
                    stats['none'] += 1
                    icd11_desc = "No suitable ICD-11 match found"
                    icd11_code = "UNMAPPED"
                
                # Create mapping
                mapping = {
                    'NAMASTE_Code': namaste_code,
                    'NAMASTE_Display': namaste_english,
                    'NAMASTE_Traditional': namaste_traditional,
                    'NAMASTE_System': namaste_system,
                    'ICD11_Code': icd11_code if icd11_code else "UNMAPPED",
                    'ICD11_Description': icd11_desc if icd11_desc else "No match found",
                    'Mapping_Confidence': f"{confidence:.3f}",
                    'Confidence_Level': confidence_level,
                    'Mapping_Method': "Optimized Semantic Matching",
                    'Last_Updated': "2025-09-04"
                }
                
                mappings.append(mapping)
            
            # Progress update
            processed = batch_end
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            remaining = len(self.namaste_data) - processed
            eta = remaining / rate if rate > 0 else 0
            
            progress = (processed / len(self.namaste_data)) * 100
            print(f" Progress: {processed:,}/{len(self.namaste_data):,} ({progress:.1f}%) | "
                  f"Rate: {rate:.1f}/sec | ETA: {eta:.0f}s")
        
        # Save results
        df = pd.DataFrame(mappings)
        output_file = "data/mapping/namaste_icd11_enhanced_mappings.csv"
        df.to_csv(output_file, index=False)
        
        total = len(mappings)
        print(f"\n Optimized mappings complete!")
        print(f" Results:")
        print(f"   • Total processed: {total:,}")
        print(f"   • High confidence (≥70%): {stats['high']:,} ({stats['high']/total*100:.1f}%)")
        print(f"   • Medium confidence (50-69%): {stats['medium']:,} ({stats['medium']/total*100:.1f}%)")
        print(f"   • Low confidence (30-49%): {stats['low']:,} ({stats['low']/total*100:.1f}%)")
        print(f"   • No match (<30%): {stats['none']:,} ({stats['none']/total*100:.1f}%)")
        print(f"   • Overall success rate: {((total-stats['none'])/total*100):.1f}%")
        print(f" Saved to: {output_file}")
        
        return output_file, stats

def main():
    """Main optimized mapping process"""
    mapper = OptimizedMapper()
    
    try:
        print(" Starting Optimized NAMASTE-ICD11 Mapping")
        print("=" * 50)
        
        # Load data
        mapper.load_data()
        
        # Create mappings
        output_file, stats = mapper.create_optimized_mappings()
        
        # Summary
        total = sum(stats.values())
        success_rate = ((total - stats['none']) / total * 100) if total > 0 else 0
        
        print(f"\n Mapping generation complete!")
        print(f" Overall accuracy: {success_rate:.1f}%")
        print(f" Output: {output_file}")
        
        return 0
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
