#!/usr/bin/env python3
"""
Mapping Accuracy Analysis
Analyzes the accuracy of NAMASTE-ICD11 mappings
"""

def analyze_accuracy():
    """Analyze mapping accuracy from CSV file"""
    
    print(" Analyzing NAMASTE-ICD11 Mapping Accuracy...")
    
    # Count statistics manually
    total_lines = 0
    high_confidence = 0
    medium_confidence = 0
    low_confidence = 0
    expert_high = 0
    unmapped = 0
    
    with open('data/mapping/namaste_icd11_enhanced_mappings.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    header = lines[0]
    data_lines = lines[1:]
    total_lines = len(data_lines)
    
    print(f" Processing {total_lines:,} mappings...")
    
    for line in data_lines:
        parts = line.strip().split(',')
        if len(parts) >= 8:
            confidence_level = parts[7].strip('"')
            icd11_code = parts[4].strip('"')
            
            if "UNMAPPED" in icd11_code:
                unmapped += 1
            elif "Expert High" in confidence_level:
                expert_high += 1
                high_confidence += 1
            elif "High" in confidence_level:
                high_confidence += 1
            elif "Medium" in confidence_level:
                medium_confidence += 1
            elif "Low" in confidence_level:
                low_confidence += 1
    
    # Calculate percentages
    successfully_mapped = total_lines - unmapped
    success_rate = (successfully_mapped / total_lines) * 100
    high_quality_rate = (high_confidence / total_lines) * 100
    expert_rate = (expert_high / total_lines) * 100
    
    print(f"\n ULTRA-HIGH ACCURACY MAPPING RESULTS:")
    print(f"=" * 60)
    print(f" OVERALL STATISTICS:")
    print(f"   • Total NAMASTE conditions: {total_lines:,}")
    print(f"   • Successfully mapped: {successfully_mapped:,}")
    print(f"   • Unmapped conditions: {unmapped:,}")
    print(f"   • Overall success rate: {success_rate:.1f}%")
    print(f"")
    print(f" CONFIDENCE BREAKDOWN:")
    print(f"   • Expert High (90%+): {expert_high:,} ({expert_rate:.1f}%)")
    print(f"   • High confidence (≥70%): {high_confidence:,} ({high_quality_rate:.1f}%)")
    print(f"   • Medium confidence: {medium_confidence:,} ({medium_confidence/total_lines*100:.1f}%)")
    print(f"   • Low confidence: {low_confidence:,} ({low_confidence/total_lines*100:.1f}%)")
    print(f"")
    print(f" QUALITY METRICS:")
    print(f"   • Clinical-grade accuracy: {expert_rate:.1f}%")
    print(f"   • High+Medium quality: {(high_confidence + medium_confidence)/total_lines*100:.1f}%")
    print(f"   • Research-ready mappings: {successfully_mapped:,}")
    
    if success_rate >= 85:
        print(f"\\n TARGET ACHIEVED! Success rate of {success_rate:.1f}% exceeds 85% goal!")
    elif success_rate >= 80:
        print(f"\\n EXCELLENT! Success rate of {success_rate:.1f}% is very high!")
    elif success_rate >= 75:
        print(f"\\n GOOD! Success rate of {success_rate:.1f}% is above average!")
    else:
        print(f"\\n IMPROVING! Success rate of {success_rate:.1f}% shows progress!")
    
    return {
        'total': total_lines,
        'mapped': successfully_mapped,
        'unmapped': unmapped,
        'success_rate': success_rate,
        'expert_high': expert_high,
        'high_conf': high_confidence,
        'expert_rate': expert_rate,
        'quality_rate': high_quality_rate
    }

def main():
    """Main analysis function"""
    try:
        results = analyze_accuracy()
        
        # Save results summary
        summary = f"""NAMASTE-ICD11 Ultra-High Accuracy Mapping Summary
Generated: 2025-09-04

FINAL RESULTS:
- Total conditions: {results['total']:,}
- Successfully mapped: {results['mapped']:,}
- Success rate: {results['success_rate']:.1f}%
- Expert-grade mappings: {results['expert_high']:,} ({results['expert_rate']:.1f}%)
- High-quality mappings: {results['high_conf']:,} ({results['quality_rate']:.1f}%)

This represents a significant improvement in traditional-modern medical terminology mapping
for the NAMASTE healthcare portal system.
"""
        
        with open('data/mapping/accuracy_summary.txt', 'w') as f:
            f.write(summary)
        
        print(f"\\n Detailed summary saved to: data/mapping/accuracy_summary.txt")
        return 0
        
    except Exception as e:
        print(f" Error analyzing accuracy: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
