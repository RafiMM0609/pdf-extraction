# PDF Title Extraction Tool

A robust Python tool for extracting titles from PDF documents using a smart waterfall approach.

## Features

- **Intelligent Title Extraction**: Uses a 3-tier waterfall approach to ensure maximum reliability
- **Priority 1 - Metadata Extraction**: Fastest method, extracts from PDF metadata
- **Priority 2 - Text Analysis**: Extracts from digital text with smart heuristics
- **Priority 3 - OCR Fallback**: Handles scanned PDFs using Tesseract OCR
- **Heuristic-Based Detection**: Advanced algorithm to identify titles from text
- **Comprehensive Testing**: Full test suite with 17+ unit tests

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. For OCR functionality, install Tesseract OCR:
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage

### As a Python Module

```python
from pdf_extraction import extract_title

# Extract title from a PDF file
title = extract_title("path/to/your/document.pdf")

if title:
    print(f"Title: {title}")
else:
    print("No title found")
```

### Command Line Interface

```bash
python pdf_extraction.py path/to/your/document.pdf
```

## How It Works

The `extract_title()` function uses a waterfall approach with three priority levels:

### Priority 1: Metadata Extraction (Fastest)
- Opens the PDF using `pypdf`
- Checks the `reader.metadata.title` field
- Returns immediately if a valid title is found
- **Advantage**: Fastest and most reliable when metadata is available

### Priority 2: Digital Text Extraction (Moderate Speed)
- Extracts raw text from the first page using `pypdf`
- Applies **Heuristic A** to identify the most likely title
- Works well for digital PDFs with selectable text
- **Advantage**: Works when metadata is missing but text is available

### Priority 3: OCR Extraction (Slowest, Fallback)
- Converts the first page to a high-quality image (300 DPI)
- Uses Tesseract OCR to extract text
- Applies **Heuristic A** to the OCR results
- **Advantage**: Handles scanned PDFs and images

### Heuristic A Algorithm

The heuristic algorithm identifies titles by analyzing:
- **Position**: Earlier lines are preferred
- **Length**: Lines between 10-100 characters are ideal
- **Case**: Title Case or ALL CAPS indicates a title
- **Content**: Filters out dates, metadata keywords, and excessive punctuation
- **Scoring**: Uses a weighted scoring system to find the best candidate

## API Reference

### `extract_title(pdf_path: str) -> Optional[str]`

Extracts the title from a PDF document.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
- `str`: The extracted title, or `None` if no title could be found

**Raises:**
- `FileNotFoundError`: If the PDF file does not exist
- `Exception`: For other errors during PDF processing

**Example:**
```python
from pdf_extraction import extract_title

try:
    title = extract_title("document.pdf")
    print(title)
except FileNotFoundError:
    print("PDF file not found")
except Exception as e:
    print(f"Error: {e}")
```

## Running Tests

Run the test suite to verify the installation:

```bash
python -m unittest test_pdf_extraction -v
```

## Requirements

- Python 3.7+
- pypdf >= 3.0.0
- pdf2image >= 1.16.0
- pytesseract >= 0.3.10
- Pillow >= 10.0.0
- Tesseract OCR (system dependency)

## Project Structure

```
pdf-extraction/
├── pdf_extraction.py       # Main extraction module
├── test_pdf_extraction.py  # Comprehensive test suite
├── requirements.txt        # Python dependencies
└── Readme.md              # This file
```

## Design Principles

1. **Maintainability**: Clean, well-documented code with type hints
2. **Efficiency**: Fast metadata extraction prioritized over slower methods
3. **Robustness**: Multiple fallback strategies ensure high success rate
4. **Testing**: Comprehensive test coverage for reliability

## License

This project is open source and available for use and modification. 