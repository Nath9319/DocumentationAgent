import sys
import json
from core.document_analyzer import DocumentAnalyzer

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_doc_technical_analyzer.py <output_directory>")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    analyzer = DocumentAnalyzer()
    
    print(f"Analyzing documentation in: {output_dir}")
    results = analyzer.analyze_existing_output(output_dir)
    
    # Save analysis results
    output_file = f"{output_dir}/technical_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Technical analysis saved to: {output_file}")
    print(f"Analyzed {results['parsed_documents']['statistics']['total_documents']} documents")
    print(f"Extracted {results['parsed_documents']['statistics']['total_entities']} entities")

if __name__ == "__main__":
    main()