"""
Example usage of the PDF title extraction module.

This script demonstrates how to use the extract_title function
to extract titles from PDF files.
"""

from pdf_extraction import extract_title
import sys


def main():
    """Main function to demonstrate PDF title extraction."""
    
    # Example 1: Using with a file path
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        print(f"\nExtracting title from: {pdf_file}")
        print("-" * 50)
        
        try:
            title = extract_title(pdf_file)
            
            if title:
                print(f"✓ Title found: {title}")
            else:
                print("✗ No title could be extracted from this PDF")
                
        except FileNotFoundError:
            print(f"✗ Error: File '{pdf_file}' not found")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    else:
        print("\nPDF Title Extraction - Example Usage")
        print("=" * 50)
        print("\nUsage:")
        print("  python example.py <path_to_pdf_file>")
        print("\nExample:")
        print("  python example.py /path/to/document.pdf")
        print("\nHow it works:")
        print("  1. First tries to extract from PDF metadata (fastest)")
        print("  2. Falls back to text extraction with heuristics")
        print("  3. If needed, uses OCR for scanned PDFs (slowest)")
        print("\nFeatures:")
        print("  ✓ Robust waterfall approach")
        print("  ✓ Intelligent heuristic algorithm")
        print("  ✓ Handles digital and scanned PDFs")
        print("  ✓ Fast and efficient")
        print("\n")


if __name__ == "__main__":
    main()
