"""
Test module for PDF title extraction functionality.

This module contains unit tests for the extract_title function and its helper functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pdf_extraction import extract_title, _apply_heuristic_a


class TestHeuristicA(unittest.TestCase):
    """Test cases for the _apply_heuristic_a function."""
    
    def test_empty_text(self):
        """Test with empty or None text."""
        self.assertIsNone(_apply_heuristic_a(""))
        self.assertIsNone(_apply_heuristic_a(None))
        self.assertIsNone(_apply_heuristic_a("   "))
    
    def test_simple_title(self):
        """Test with a simple title at the beginning."""
        text = "The Great Adventure\n\nThis is the body of the document..."
        result = _apply_heuristic_a(text)
        self.assertEqual(result, "The Great Adventure")
    
    def test_title_case(self):
        """Test that title case is preferred."""
        text = "The Quick Brown Fox\nthis is just regular text\nmore body text"
        result = _apply_heuristic_a(text)
        self.assertEqual(result, "The Quick Brown Fox")
    
    def test_all_caps_title(self):
        """Test that ALL CAPS is recognized as a title."""
        text = "INTRODUCTION TO MACHINE LEARNING\nBy John Doe\nThis paper discusses..."
        result = _apply_heuristic_a(text)
        self.assertEqual(result, "INTRODUCTION TO MACHINE LEARNING")
    
    def test_filters_long_lines(self):
        """Test that very long lines are filtered out."""
        long_line = "a" * 250
        text = f"{long_line}\nShort Title\nBody text here"
        result = _apply_heuristic_a(text)
        self.assertEqual(result, "Short Title")
    
    def test_filters_dates(self):
        """Test that lines with dates are deprioritized."""
        text = "2023-11-12\nActual Document Title\nBody content"
        result = _apply_heuristic_a(text)
        self.assertEqual(result, "Actual Document Title")
    
    def test_filters_metadata_keywords(self):
        """Test that metadata-like lines are deprioritized."""
        text = "Page 1\nAuthor: John Doe\nThe Real Title\nBody text"
        result = _apply_heuristic_a(text)
        self.assertEqual(result, "The Real Title")
    
    def test_prefers_earlier_lines(self):
        """Test that earlier lines are preferred."""
        text = "First Title\nSecond Title\nThird Title"
        result = _apply_heuristic_a(text)
        # Should prefer the first title
        self.assertIn(result, ["First Title", "Second Title"])
    
    def test_single_line(self):
        """Test with a single line of text."""
        text = "Single Line Title"
        result = _apply_heuristic_a(text)
        self.assertEqual(result, "Single Line Title")


class TestExtractTitle(unittest.TestCase):
    """Test cases for the extract_title function."""
    
    @patch('pdf_extraction.PdfReader')
    def test_extract_from_metadata(self, mock_reader_class):
        """Test extraction from PDF metadata (Priority 1)."""
        # Setup mock
        mock_reader = Mock()
        mock_metadata = Mock()
        mock_metadata.title = "Document Title from Metadata"
        mock_reader.metadata = mock_metadata
        mock_reader.pages = []
        mock_reader_class.return_value = mock_reader
        
        result = extract_title("dummy.pdf")
        self.assertEqual(result, "Document Title from Metadata")
    
    @patch('pdf_extraction.PdfReader')
    def test_extract_from_metadata_with_whitespace(self, mock_reader_class):
        """Test that metadata title is stripped of whitespace."""
        mock_reader = Mock()
        mock_metadata = Mock()
        mock_metadata.title = "  Title With Spaces  "
        mock_reader.metadata = mock_metadata
        mock_reader.pages = []
        mock_reader_class.return_value = mock_reader
        
        result = extract_title("dummy.pdf")
        self.assertEqual(result, "Title With Spaces")
    
    @patch('pdf_extraction.PdfReader')
    def test_fallback_to_text_extraction(self, mock_reader_class):
        """Test fallback to text extraction when metadata is empty (Priority 2)."""
        mock_reader = Mock()
        mock_reader.metadata = None
        
        mock_page = Mock()
        mock_page.extract_text.return_value = "Digital Text Title\n\nBody content here..."
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader
        
        result = extract_title("dummy.pdf")
        self.assertEqual(result, "Digital Text Title")
    
    @patch('pdf_extraction.pytesseract.image_to_string')
    @patch('pdf_extraction.convert_from_path')
    @patch('pdf_extraction.PdfReader')
    def test_fallback_to_ocr(self, mock_reader_class, mock_convert, mock_tesseract):
        """Test fallback to OCR when text extraction fails (Priority 3)."""
        # Setup mocks
        mock_reader = Mock()
        mock_reader.metadata = None
        
        mock_page = Mock()
        mock_page.extract_text.return_value = ""  # Empty text indicates scanned PDF
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader
        
        # Mock OCR
        mock_image = Mock()
        mock_convert.return_value = [mock_image]
        mock_tesseract.return_value = "OCR Extracted Title\n\nOCR body text..."
        
        result = extract_title("dummy.pdf")
        self.assertEqual(result, "OCR Extracted Title")
        
        # Verify OCR was called with correct parameters
        mock_convert.assert_called_once_with("dummy.pdf", first_page=1, last_page=1, dpi=300)
        mock_tesseract.assert_called_once_with(mock_image)
    
    @patch('pdf_extraction.PdfReader')
    def test_file_not_found(self, mock_reader_class):
        """Test that FileNotFoundError is raised for missing files."""
        mock_reader_class.side_effect = FileNotFoundError("File not found")
        
        with self.assertRaises(FileNotFoundError):
            extract_title("nonexistent.pdf")
    
    @patch('pdf_extraction.pytesseract.image_to_string')
    @patch('pdf_extraction.convert_from_path')
    @patch('pdf_extraction.PdfReader')
    def test_returns_none_when_all_methods_fail(self, mock_reader_class, mock_convert, mock_tesseract):
        """Test that None is returned when all extraction methods fail."""
        mock_reader = Mock()
        mock_reader.metadata = None
        
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader
        
        # Make OCR fail
        mock_convert.side_effect = Exception("OCR failed")
        
        result = extract_title("dummy.pdf")
        self.assertIsNone(result)
    
    @patch('pdf_extraction.PdfReader')
    def test_empty_metadata_title(self, mock_reader_class):
        """Test handling of empty metadata title."""
        mock_reader = Mock()
        mock_metadata = Mock()
        mock_metadata.title = ""  # Empty title
        mock_reader.metadata = mock_metadata
        
        mock_page = Mock()
        mock_page.extract_text.return_value = "Fallback Title\nBody text"
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader
        
        result = extract_title("dummy.pdf")
        self.assertEqual(result, "Fallback Title")
    
    @patch('pdf_extraction.PdfReader')
    def test_no_metadata(self, mock_reader_class):
        """Test handling when metadata object doesn't exist."""
        mock_reader = Mock()
        mock_reader.metadata = None
        
        mock_page = Mock()
        mock_page.extract_text.return_value = "Title Without Metadata\nBody"
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader
        
        result = extract_title("dummy.pdf")
        self.assertEqual(result, "Title Without Metadata")


if __name__ == '__main__':
    unittest.main()
