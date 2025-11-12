"""
PDF Title Extraction Module

This module provides functionality to extract titles from PDF documents using
a robust waterfall approach with three priority levels:
1. Metadata extraction (fastest, most reliable)
2. Digital text extraction with heuristics
3. OCR extraction for scanned PDFs (slowest, fallback)
"""

from typing import Optional
import re
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract


def _apply_heuristic_a(text: str) -> Optional[str]:
    """
    Apply Heuristic A to identify the most likely title from extracted text.
    
    Heuristic A prioritizes:
    - Lines at the beginning of the document
    - Lines with larger font sizes (if detectable)
    - Lines that are shorter (typical for titles)
    - Lines that don't look like body text
    - Lines with title-case formatting
    
    Args:
        text: Raw text extracted from the PDF
        
    Returns:
        The identified title or None if no strong candidate is found
    """
    if not text or not text.strip():
        return None
    
    # Split into lines and clean them
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return None
    
    # Look at the first few lines (titles are typically at the top)
    candidate_lines = lines[:10]
    
    # Filter out very long lines (likely body text, not titles)
    # Titles are typically less than 200 characters
    candidate_lines = [line for line in candidate_lines if len(line) < 200]
    
    if not candidate_lines:
        return None
    
    # Score each candidate line
    best_score = -1
    best_candidate = None
    
    for idx, line in enumerate(candidate_lines):
        score = 0
        
        # Earlier lines get higher scores
        score += (len(candidate_lines) - idx) * 2
        
        # Shorter lines preferred (within reason)
        if 10 <= len(line) <= 100:
            score += 3
        elif len(line) < 10:
            score -= 2  # Too short might be header/footer
        
        # Title case or ALL CAPS suggests a title
        if line.istitle() or line.isupper():
            score += 4
        
        # Avoid lines that look like metadata or dates
        if re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', line):
            score -= 3
        if re.search(r'^(page|vol|volume|author|date)', line, re.IGNORECASE):
            score -= 3
        
        # Lines with mostly alphanumeric characters are preferred
        alpha_ratio = sum(c.isalnum() or c.isspace() for c in line) / len(line)
        if alpha_ratio > 0.8:
            score += 2
        
        # Avoid lines with lots of punctuation (except basic ones)
        special_chars = sum(c in '!@#$%^&*()[]{}|\\<>' for c in line)
        if special_chars > 3:
            score -= 2
        
        if score > best_score:
            best_score = score
            best_candidate = line
    
    # Only return if we have a reasonable confidence
    if best_score > 3:
        return best_candidate
    
    # If no strong candidate, return the first non-trivial line
    if candidate_lines:
        return candidate_lines[0]
    
    return None


def extract_title(pdf_path: str) -> Optional[str]:
    """
    Extract the title from a PDF document using a robust waterfall approach.
    
    The function tries three methods in order of reliability and speed:
    1. Metadata extraction (fastest, most reliable)
    2. Digital text extraction with heuristics
    3. OCR extraction for scanned PDFs (slowest, fallback)
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        The extracted title as a string, or None if no title could be found
        
    Raises:
        FileNotFoundError: If the PDF file does not exist
        Exception: For other errors during PDF processing
    """
    try:
        # Priority 1: Extract from metadata
        reader = PdfReader(pdf_path)
        
        # Check if metadata exists and has a title
        if reader.metadata and reader.metadata.title:
            title = reader.metadata.title.strip()
            if title:
                return title
        
        # Priority 2: Extract from digital text using pypdf
        if len(reader.pages) > 0:
            first_page = reader.pages[0]
            text = first_page.extract_text()
            
            # If we got text, apply heuristics
            if text and text.strip():
                title = _apply_heuristic_a(text)
                if title:
                    return title
        
        # Priority 3: OCR with PyTesseract (for scanned PDFs)
        # This is reached when extract_text() returns empty or no strong candidate found
        try:
            # Convert first page to image at high DPI for better OCR
            images = convert_from_path(
                pdf_path,
                first_page=1,
                last_page=1,
                dpi=300
            )
            
            if images:
                # Perform OCR on the first page
                ocr_text = pytesseract.image_to_string(images[0])
                
                # Apply heuristics to OCR text
                if ocr_text and ocr_text.strip():
                    title = _apply_heuristic_a(ocr_text)
                    if title:
                        return title
        
        except Exception as ocr_error:
            # OCR might fail if tesseract is not installed or other issues
            # We silently continue as this is the last fallback
            pass
        
        # All methods failed
        return None
        
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        try:
            title = extract_title(pdf_file)
            if title:
                print(f"Title: {title}")
            else:
                print("No title found")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python pdf_extraction.py <pdf_file>")
