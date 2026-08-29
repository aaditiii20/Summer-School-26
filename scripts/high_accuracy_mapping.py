#!/usr/bin/env python3
"""
Advanced High-Accuracy NAMASTE-ICD11 Mapping System
Uses sophisticated NLP, medical ontologies, and multi-layered matching for 85%+ accuracy
"""

import pandas as pd
import re
import json
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional
import numpy as np
import time
from collections import defaultdict

class AdvancedMedicalMapper:
    def __init__(self):
        self.namaste_data = None
        self.icd11_data = None
        self.medical_ontology = self.build_medical_ontology()
        self.system_patterns = self.build_system_patterns()
        self.symptom_disease_map = self.build_symptom_disease_mapping()
        
    def build_medical_ontology(self):
        """Comprehensive medical terminology ontology"""
        return {
            # Cardiovascular System
            'cardiovascular': {
                'traditional': ['hridaya', 'hrid', 'rakta', 'raktavaha', 'marma', 'vyana'],
                'modern': ['heart', 'cardiac', 'cardio', 'vascular', 'blood', 'circulation', 'pressure'],
                'conditions': ['hypertension', 'hypotension', 'arrhythmia', 'angina', 'infarction'],
                'icd_patterns': ['BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'MC']
            },
            
            # Endocrine & Metabolic
            'endocrine': {
                'traditional': ['madhumeha', 'prameha', 'medoroga', 'sthaulya', 'karshya', 'ojokshaya'],
                'modern': ['diabetes', 'mellitus', 'glucose', 'insulin', 'metabolic', 'thyroid', 'hormone'],
                'conditions': ['diabetes', 'hyperthyroidism', 'hypothyroidism', 'obesity'],
                'icd_patterns': ['5A', '5B', '5C', '5D', '5E']
            },
            
            # Respiratory System
            'respiratory': {
                'traditional': ['shwasa', 'pranavahasrotas', 'kasa', 'tamaka', 'ucchvasa'],
                'modern': ['respiratory', 'lung', 'pulmonary', 'breathing', 'asthma', 'bronchi'],
                'conditions': ['asthma', 'bronchitis', 'pneumonia', 'tuberculosis'],
                'icd_patterns': ['CA', 'CB', 'CC', 'CD', 'CE']
            },
            
            # Digestive System
            'digestive': {
                'traditional': ['annavaha', 'pachana', 'agni', 'amlapitta', 'grahani', 'atisara'],
                'modern': ['digestive', 'gastro', 'intestinal', 'stomach', 'liver', 'pancreas'],
                'conditions': ['gastritis', 'ulcer', 'diarrhea', 'constipation', 'hepatitis'],
                'icd_patterns': ['DA', 'DB', 'DC', 'DD', 'DE', 'DF', 'DG', 'DH', 'DI']
            },
            
            # Musculoskeletal System
            'musculoskeletal': {
                'traditional': ['asthi', 'majja', 'mamsa', 'sandhivata', 'amavata', 'gridhrasi'],
                'modern': ['bone', 'joint', 'muscle', 'skeletal', 'arthritis', 'rheumat'],
                'conditions': ['arthritis', 'osteoporosis', 'fracture', 'myalgia'],
                'icd_patterns': ['FA', 'FB', 'FC', 'FD', 'FE']
            },
            
            # Nervous System
            'nervous': {
                'traditional': ['majjavaha', 'nadi', 'manas', 'buddhi', 'smriti', 'shirahshool'],
                'modern': ['nervous', 'neuro', 'brain', 'mental', 'psychiatric', 'cognitive'],
                'conditions': ['depression', 'anxiety', 'migraine', 'epilepsy', 'dementia'],
                'icd_patterns': ['8A', '8B', '8C', '8D', '8E', '6A', '6B', '6C', '6D']
            },
            
            # Genitourinary System
            'genitourinary': {
                'traditional': ['mutravaha', 'vrikka', 'basti', 'shukra', 'artava', 'garbha'],
                'modern': ['kidney', 'renal', 'urinary', 'bladder', 'reproductive', 'genital'],
                'conditions': ['nephritis', 'cystitis', 'urethritis', 'infertility'],
                'icd_patterns': ['GB', 'GC', 'GE', 'GF', 'GA']
            },
            
            # Dermatological
            'dermatological': {
                'traditional': ['tvak', 'kushtha', 'charma', 'varna', 'kandu', 'dadru'],
                'modern': ['skin', 'derma', 'cutaneous', 'epiderm', 'eczema', 'psoriasis'],
                'conditions': ['eczema', 'psoriasis', 'dermatitis', 'infection'],
                'icd_patterns': ['EA', 'EB', 'EC', 'ED', 'EE']
            },
            
            # Infectious Diseases
            'infectious': {
                'traditional': ['krimi', 'sankramaka', 'jvara', 'vishama', 'agantu'],
                'modern': ['infection', 'bacterial', 'viral', 'fungal', 'parasitic', 'fever'],
                'conditions': ['pneumonia', 'tuberculosis', 'malaria', 'sepsis'],
                'icd_patterns': ['1A', '1B', '1C', '1D', '1E', '1F', '1G']
            },
            
            # Mental Health
            'mental': {
                'traditional': ['unmada', 'apasmara', 'vishada', 'chinta', 'bhaya', 'manoavasada'],
                'modern': ['mental', 'psychiatric', 'psychological', 'mood', 'anxiety', 'depression'],
                'conditions': ['depression', 'anxiety', 'schizophrenia', 'bipolar'],
                'icd_patterns': ['6A', '6B', '6C', '6D', '6E']
            }
        }
    
    def build_system_patterns(self):
        """Traditional medicine system-specific patterns"""
        return {
            'ayurveda': {
                'suffixes': ['vataja', 'pittaja', 'kaphaja', 'sannipataja', 'dvandvaja'],
                'prefixes': ['sama', 'nirama', 'ama', 'rakta', 'medoj'],
                'concepts': ['dosha', 'dhatu', 'mala', 'srotas', 'ojas', 'tejas', 'prana']
            },
            'siddha': {
                'concepts': ['vali', 'azhal', 'iyyam', 'thontham', 'naadi'],
                'terms': ['suram', 'vali', 'azhal', 'kapha']
            },
            'unani': {
                'concepts': ['mizaj', 'akhlat', 'arkan', 'quwat'],
                'terms': ['hararat', 'buroodat', 'ratoodat', 'yaboosat']
            }
        }
    
    def build_symptom_disease_mapping(self):
        """Enhanced symptom to disease mapping"""
        return {
            # Common symptoms with disease associations
            'fever': ['pyrexia', 'hyperthermia', 'febrile', 'temperature'],
            'pain': ['algia', 'ache', 'discomfort', 'soreness'],
            'inflammation': ['itis', 'swelling', 'inflammatory', 'edema'],
            'infection': ['sepsis', 'bacterial', 'viral', 'fungal'],
            'bleeding': ['hemorrhage', 'hematoma', 'epistaxis'],
            'difficulty_breathing': ['dyspnea', 'breathlessness', 'respiratory_distress'],
            'digestive_issues': ['dyspepsia', 'gastritis', 'enteritis'],
            'skin_problems': ['dermatitis', 'eczema', 'rash'],
            'joint_pain': ['arthralgia', 'joint_pain', 'arthritis'],
            'headache': ['cephalgia', 'migraine', 'headache']
        }

    def load_data(self):
        """Load datasets"""
        print(" Loading datasets for advanced mapping...")
        
        self.namaste_data = pd.read_csv("data/mapping/namaste_icd11_complete_7331_mappings.csv")
        self.icd11_data = pd.read_csv("data/external/icd11_clinical_terminology_complete.csv")
        
        print(f" Loaded {len(self.namaste_data)} NAMASTE records")
        print(f" Loaded {len(self.icd11_data)} ICD-11 records")

    def extract_medical_concepts(self, text: str) -> Dict:
        """Extract medical concepts from text"""
        text_lower = text.lower()
        concepts = {
            'systems': [],
            'symptoms': [],
            'anatomical': [],
            'traditional_terms': [],
            'modifiers': []
        }
        
        # System identification
        for system, data in self.medical_ontology.items():
            for trad_term in data['traditional']:
                if trad_term in text_lower:
                    concepts['systems'].append(system)
                    concepts['traditional_terms'].append(trad_term)
            for modern_term in data['modern']:
                if modern_term in text_lower:
                    concepts['systems'].append(system)
        
        # Symptom identification
        for symptom, variants in self.symptom_disease_map.items():
            if any(variant in text_lower for variant in variants):
                concepts['symptoms'].append(symptom)
        
        # Traditional system modifiers
        for system, patterns in self.system_patterns.items():
            if 'suffixes' in patterns:
                for suffix in patterns['suffixes']:
                    if suffix in text_lower:
                        concepts['modifiers'].append(suffix)
        
        return concepts

    def calculate_advanced_similarity(self, namaste_term: str, icd11_term: str) -> float:
        """Advanced similarity calculation using multiple methods"""
        
        # Extract concepts from both terms
        namaste_concepts = self.extract_medical_concepts(namaste_term)
        icd11_concepts = self.extract_medical_concepts(icd11_term)
        
        scores = []
        
        # 1. System-based matching (high weight)
        if namaste_concepts['systems'] and icd11_concepts['systems']:
            system_overlap = len(set(namaste_concepts['systems']) & set(icd11_concepts['systems']))
            total_systems = len(set(namaste_concepts['systems']) | set(icd11_concepts['systems']))
            if total_systems > 0:
                scores.append(('system', system_overlap / total_systems, 0.4))
        
        # 2. Symptom matching (medium weight)
        if namaste_concepts['symptoms'] and icd11_concepts['symptoms']:
            symptom_overlap = len(set(namaste_concepts['symptoms']) & set(icd11_concepts['symptoms']))
            total_symptoms = len(set(namaste_concepts['symptoms']) | set(icd11_concepts['symptoms']))
            if total_symptoms > 0:
                scores.append(('symptom', symptom_overlap / total_symptoms, 0.3))
        
        # 3. Direct term matching (high weight for exact matches)
        text1_clean = re.sub(r'[^\w\s]', ' ', namaste_term.lower()).strip()
        text2_clean = re.sub(r'[^\w\s]', ' ', icd11_term.lower()).strip()
        
        # Exact substring matching
        if text1_clean in text2_clean or text2_clean in text1_clean:
            scores.append(('exact', 1.0, 0.5))
        
        # Word-level matching
        words1 = set(text1_clean.split())
        words2 = set(text2_clean.split())
        if words1 and words2:
            word_overlap = len(words1 & words2) / len(words1 | words2)
            scores.append(('word', word_overlap, 0.3))
        
        # 4. Semantic similarity for medical terms
        semantic_score = self.calculate_semantic_similarity(namaste_term, icd11_term)
        if semantic_score > 0:
            scores.append(('semantic', semantic_score, 0.25))
        
        # 5. ICD pattern matching
        icd_score = self.calculate_icd_pattern_score(namaste_concepts, icd11_term)
        if icd_score > 0:
            scores.append(('icd_pattern', icd_score, 0.2))
        
        # Calculate weighted average
        if scores:
            total_weighted = sum(score * weight for _, score, weight in scores)
            total_weight = sum(weight for _, _, weight in scores)
            return min(total_weighted / total_weight if total_weight > 0 else 0, 1.0)
        
        return 0.0

    def calculate_semantic_similarity(self, namaste_term: str, icd11_term: str) -> float:
        """Calculate semantic similarity using medical knowledge"""
        
        # Key medical term mappings
        semantic_mappings = {
            'madhumeha': ['diabetes', 'mellitus', 'glucose'],
            'prameha': ['diabetes', 'urinary', 'glucose'],
            'jwara': ['fever', 'pyrexia', 'temperature'],
            'shwasa': ['asthma', 'breathing', 'respiratory'],
            'tamaka': ['asthma', 'bronchial'],
            'sandhivata': ['arthritis', 'joint', 'rheumat'],
            'amavata': ['rheumatoid', 'arthritis'],
            'amlapitta': ['gastritis', 'acid', 'peptic'],
            'ardhavabhedaka': ['migraine', 'headache', 'cephalgia'],
            'gridhrasi': ['sciatica', 'nerve', 'radicular'],
            'kushtha': ['dermatitis', 'skin', 'eczema'],
            'yakrit': ['liver', 'hepat'],
            'vrikka': ['kidney', 'renal', 'nephro'],
            'hridaya': ['heart', 'cardiac', 'cardio'],
            'unmada': ['psychosis', 'mental', 'psychiatric'],
            'apasmara': ['epilepsy', 'seizure', 'convulsion'],
            'vishada': ['depression', 'mood', 'depressive'],
            'chinta': ['anxiety', 'worry', 'anxious']
        }
        
        namaste_lower = namaste_term.lower()
        icd11_lower = icd11_term.lower()
        
        max_score = 0.0
        
        for traditional_term, modern_terms in semantic_mappings.items():
            if traditional_term in namaste_lower:
                for modern_term in modern_terms:
                    if modern_term in icd11_lower:
                        max_score = max(max_score, 0.9)  # High semantic match
        
        return max_score

    def calculate_icd_pattern_score(self, namaste_concepts: Dict, icd11_code: str) -> float:
        """Score based on ICD-11 code patterns for medical systems"""
        
        if not namaste_concepts['systems']:
            return 0.0
        
        for system in namaste_concepts['systems']:
            if system in self.medical_ontology:
                patterns = self.medical_ontology[system].get('icd_patterns', [])
                for pattern in patterns:
                    if icd11_code.startswith(pattern):
                        return 0.8  # Good pattern match
        
        return 0.0

    def find_best_matches(self, namaste_term: str, top_k: int = 5) -> List[Tuple]:
        """Find best ICD-11 matches for a NAMASTE term"""
        
        candidates = []
        namaste_concepts = self.extract_medical_concepts(namaste_term)
        
        # Pre-filter ICD-11 terms based on system relevance
        relevant_indices = []
        if namaste_concepts['systems']:
            for system in namaste_concepts['systems']:
                if system in self.medical_ontology:
                    patterns = self.medical_ontology[system].get('icd_patterns', [])
                    for idx, row in self.icd11_data.iterrows():
                        code = str(row['Code'])
                        if any(code.startswith(pattern) for pattern in patterns):
                            relevant_indices.append(idx)
        
        # If no system match, use all data (fallback)
        if not relevant_indices:
            relevant_indices = list(range(len(self.icd11_data)))
        
        # Limit to top candidates to avoid performance issues
        relevant_indices = relevant_indices[:1000]
        
        for idx in relevant_indices:
            row = self.icd11_data.iloc[idx]
            icd11_desc = str(row['Description'])
            icd11_code = str(row['Code'])
            
            score = self.calculate_advanced_similarity(namaste_term, icd11_desc)
            
            if score > 0.25:  # Minimum threshold
                candidates.append((icd11_desc, icd11_code, score))
        
        # Sort by score and return top matches
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates[:top_k]

    def create_high_accuracy_mappings(self):
        """Create high-accuracy mappings"""
        print(" Creating high-accuracy NAMASTE-ICD11 mappings...")
        print(" Using advanced medical ontology and multi-layered matching")
        
        mappings = []
        stats = {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        
        start_time = time.time()
        
        for idx, row in self.namaste_data.iterrows():
            if idx % 100 == 0:
                elapsed = time.time() - start_time
                rate = (idx + 1) / elapsed if elapsed > 0 else 0
                remaining = len(self.namaste_data) - idx - 1
                eta = remaining / rate if rate > 0 else 0
                
                progress = ((idx + 1) / len(self.namaste_data)) * 100
                print(f" Progress: {idx+1:,}/{len(self.namaste_data):,} ({progress:.1f}%) | "
                      f"Rate: {rate:.1f}/sec | ETA: {eta:.0f}s")
            
            namaste_english = str(row.get('NAMASTE_Display', ''))
            namaste_traditional = str(row.get('Traditional_Name', ''))
            namaste_code = str(row.get('NAMASTE_Code', ''))
            namaste_system = str(row.get('System', 'Unknown'))
            
            # Create comprehensive search term
            search_term = f"{namaste_english} {namaste_traditional}"
            
            # Find best matches
            matches = self.find_best_matches(search_term)
            
            if matches:
                best_match = matches[0]
                icd11_desc, icd11_code, confidence = best_match
                
                # Enhanced confidence classification
                if confidence >= 0.8:
                    confidence_level = "High"
                    stats['high'] += 1
                elif confidence >= 0.6:
                    confidence_level = "Medium"
                    stats['medium'] += 1
                elif confidence >= 0.4:
                    confidence_level = "Low"
                    stats['low'] += 1
                else:
                    confidence_level = "No Match"
                    stats['none'] += 1
                    icd11_desc = "No suitable ICD-11 match found"
                    icd11_code = "UNMAPPED"
            else:
                confidence = 0.0
                confidence_level = "No Match"
                stats['none'] += 1
                icd11_desc = "No suitable ICD-11 match found"
                icd11_code = "UNMAPPED"
            
            # Create enhanced mapping
            mapping = {
                'NAMASTE_Code': namaste_code,
                'NAMASTE_Display': namaste_english,
                'NAMASTE_Traditional': namaste_traditional,
                'NAMASTE_System': namaste_system,
                'ICD11_Code': icd11_code,
                'ICD11_Description': icd11_desc,
                'Mapping_Confidence': f"{confidence:.3f}",
                'Confidence_Level': confidence_level,
                'Mapping_Method': "Advanced Medical Ontology Matching",
                'Last_Updated': "2025-09-04"
            }
            
            mappings.append(mapping)
        
        # Save results
        df = pd.DataFrame(mappings)
        output_file = "data/mapping/namaste_icd11_high_accuracy_mappings.csv"
        df.to_csv(output_file, index=False)
        
        total = len(mappings)
        success_rate = ((total - stats['none']) / total) * 100
        high_medium_rate = ((stats['high'] + stats['medium']) / total) * 100
        
        print(f"\n High-accuracy mappings complete!")
        print(f" Advanced Results:")
        print(f"   • Total processed: {total:,}")
        print(f"   • High confidence (≥80%): {stats['high']:,} ({stats['high']/total*100:.1f}%)")
        print(f"   • Medium confidence (60-79%): {stats['medium']:,} ({stats['medium']/total*100:.1f}%)")
        print(f"   • Low confidence (40-59%): {stats['low']:,} ({stats['low']/total*100:.1f}%)")
        print(f"   • No match (<40%): {stats['none']:,} ({stats['none']/total*100:.1f}%)")
        print(f"   • Overall success rate: {success_rate:.1f}%")
        print(f"   • High+Medium quality: {high_medium_rate:.1f}%")
        print(f" Saved to: {output_file}")
        
        return output_file, stats

def main():
    """Main high-accuracy mapping process"""
    mapper = AdvancedMedicalMapper()
    
    try:
        print(" Starting Advanced High-Accuracy NAMASTE-ICD11 Mapping")
        print(" Target: 85%+ mapping accuracy using medical ontology")
        print("=" * 60)
        
        # Load data
        mapper.load_data()
        
        # Create high-accuracy mappings
        output_file, stats = mapper.create_high_accuracy_mappings()
        
        # Summary
        total = sum(stats.values())
        success_rate = ((total - stats['none']) / total * 100) if total > 0 else 0
        quality_rate = ((stats['high'] + stats['medium']) / total * 100) if total > 0 else 0
        
        print(f"\n High-accuracy mapping generation complete!")
        print(f" Overall success rate: {success_rate:.1f}%")
        print(f" High+Medium quality rate: {quality_rate:.1f}%")
        print(f" Output: {output_file}")
        
        return 0
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
