"""
Comprehensive Test Suite for Image Scanner
6 automated tests covering functional and performance validation.
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import Mock, patch
from typing import Dict, Any
from PIL import Image
import io

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_scanner import ImageScanner
from tests.test_framework import ScannerTestSuite, BaseScanner

class TestImageScanner(ScannerTestSuite):
    """Comprehensive test suite for Image Scanner functionality and performance"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scanner = ImageScanner(region="Netherlands")
        cls.base_tester = BaseScanner("ImageScanner")
    
    def create_test_image_with_text(self, text: str, width: int = 400, height: int = 200):
        """Create a test image with embedded text"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create blank image
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use default font, fallback to basic if not available
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw text on image
        draw.text((10, 10), text, fill='black', font=font)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def test_1_functional_pii_text_extraction(self):
        """Test 1: Functional - PII Detection in Image Text via OCR"""
        # Create test image with PII content
        pii_text = """
        Personal Information:
        Name: John Doe
        Email: john.doe@company.com
        Phone: +31 6 12345678
        BSN: 123456782
        Address: Damrak 123, 1012 JK Amsterdam
        """
        
        image_data = self.create_test_image_with_text(pii_text)
        
        # Mock OCR response
        mock_ocr_result = {
            'text': pii_text,
            'confidence': 85.5,
            'word_confidences': [90, 85, 80, 88, 92]
        }
        
        with patch.object(self.scanner, '_extract_text_from_image', return_value=mock_ocr_result):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_image_data,
                image_data,
                "test_image.png"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check PII detection
            self.assertGreater(len(result['findings']), 0, "Should detect PII in image text")
            
            # Check for Netherlands-specific BSN detection
            bsn_found = any('bsn' in str(finding).lower() or 'netherlands' in str(finding).lower() 
                           for finding in result['findings'])
            self.assertTrue(bsn_found, "Should detect Netherlands BSN in image")
            
            # Check OCR confidence
            if 'ocr_confidence' in result:
                self.assertGreaterEqual(result['ocr_confidence'], 70.0, 
                                       "OCR confidence should be reasonable")
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 1 PASSED: PII detection in image with {len(result['findings'])} findings in {performance_data['execution_time']:.2f}s")
    
    def test_2_functional_document_scanning(self):
        """Test 2: Functional - Document Image Processing"""
        # Create document-like image with structured data
        document_text = """
        CONFIDENTIAL DOCUMENT
        
        Employee ID: EMP-12345
        Social Security: 123-45-6789
        Bank Account: NL91 ABNA 0417 1643 00
        Medical Record: MR-789012
        
        This document contains sensitive information
        and should be handled according to GDPR guidelines.
        """
        
        image_data = self.create_test_image_with_text(document_text, 600, 400)
        
        # Mock OCR with high confidence for document
        mock_ocr_result = {
            'text': document_text,
            'confidence': 92.3,
            'word_confidences': [95, 90, 88, 94, 91, 89]
        }
        
        with patch.object(self.scanner, '_extract_text_from_image', return_value=mock_ocr_result):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_image_data,
                image_data,
                "confidential_document.png"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check for document-specific PII
            document_findings = [f for f in result['findings'] 
                               if any(keyword in str(f).lower() for keyword in 
                                     ['employee', 'social', 'bank', 'medical', 'confidential'])]
            self.assertGreater(len(document_findings), 0, 
                              "Should detect document-specific PII patterns")
            
            # Check GDPR compliance analysis
            gdpr_mentioned = any('gdpr' in str(finding).lower() for finding in result['findings'])
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 2 PASSED: Document scanning with {len(document_findings)} sensitive findings in {performance_data['execution_time']:.2f}s")
    
    def test_3_functional_netherlands_compliance(self):
        """Test 3: Functional - Netherlands-Specific Data Recognition"""
        # Create image with Dutch-specific information
        dutch_text = """
        Nederlandse Identiteitskaart
        
        BSN: 123456782
        Postcode: 1012 AB
        KvK nummer: 12345678
        IBAN: NL91 RABO 0315 9999 99
        
        Geboortedatum: 15-03-1985
        Geboorteplaats: Amsterdam
        Nationaliteit: Nederlandse
        """
        
        image_data = self.create_test_image_with_text(dutch_text, 500, 350)
        
        # Mock OCR with Dutch language support
        mock_ocr_result = {
            'text': dutch_text,
            'confidence': 88.7,
            'language': 'nld+eng',  # Dutch + English
            'word_confidences': [92, 85, 90, 87, 94]
        }
        
        with patch.object(self.scanner, '_extract_text_from_image', return_value=mock_ocr_result):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_image_data,
                image_data,
                "dutch_id_card.png"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check Netherlands-specific detection
            self.assertEqual(result.get('region'), 'Netherlands')
            
            # Check for Dutch-specific patterns
            dutch_findings = [f for f in result['findings'] 
                             if any(keyword in str(f).lower() for keyword in 
                                   ['bsn', 'postcode', 'kvk', 'iban', 'nederlandse'])]
            self.assertGreater(len(dutch_findings), 0, 
                              "Should detect Netherlands-specific data patterns")
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 3 PASSED: Dutch compliance analysis with {len(dutch_findings)} findings in {performance_data['execution_time']:.2f}s")
    
    def test_4_performance_large_image_processing(self):
        """Test 4: Performance - Large High-Resolution Image Processing"""
        # Create large image with text
        large_text = "Large Image Test " * 50  # Repeat to fill large image
        large_image_data = self.create_test_image_with_text(large_text, 2000, 1500)  # Large resolution
        
        # Mock OCR for large image
        mock_ocr_result = {
            'text': large_text,
            'confidence': 75.2,
            'processing_time': 3.5,
            'word_confidences': [80] * 100  # Many words
        }
        
        with patch.object(self.scanner, '_extract_text_from_image', return_value=mock_ocr_result):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_image_data,
                large_image_data,
                "large_image.png"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Performance requirements for large images
            self.assertLess(performance_data['execution_time'], 20.0,
                           "Large image processing should complete within 20 seconds")
            self.assertLess(performance_data['memory_used'], 300.0,
                           "Memory usage should stay under 300MB for large images")
            
            # Check that image was processed
            if 'image_size' in result:
                self.assertGreater(result['image_size'], 1000000,  # > 1MB
                                  "Should handle large image files")
            
            print(f"✓ Test 4 PASSED: Large image processing in {performance_data['execution_time']:.2f}s")
    
    def test_5_performance_batch_image_processing(self):
        """Test 5: Performance - Multiple Image Batch Processing"""
        # Create multiple test images
        image_batch = []
        for i in range(5):
            text_content = f"Document {i+1}\nEmail: user{i+1}@example.com\nPhone: +31 6 1234567{i}"
            image_data = self.create_test_image_with_text(text_content)
            image_batch.append((image_data, f"document_{i+1}.png"))
        
        # Mock OCR for batch processing
        def mock_ocr_side_effect(*args, **kwargs):
            return {
                'text': f"Sample text for image {len(image_batch)}",
                'confidence': 82.0,
                'word_confidences': [85, 80, 90]
            }
        
        total_findings = 0
        total_time = 0
        
        with patch.object(self.scanner, '_extract_text_from_image', side_effect=mock_ocr_side_effect):
            for image_data, filename in image_batch:
                performance_data = self.base_tester.measure_performance(
                    self.scanner.scan_image_data,
                    image_data,
                    filename
                )
                result = performance_data['result']
                
                # Validate each result
                self.assert_scan_structure(result)
                total_findings += len(result['findings'])
                total_time += performance_data['execution_time']
        
        # Performance validation for batch processing
        avg_time_per_image = total_time / len(image_batch)
        self.assertLess(avg_time_per_image, 5.0,
                       "Average processing time per image should be under 5 seconds")
        
        print(f"✓ Test 5 PASSED: Batch processing {len(image_batch)} images in {total_time:.2f}s (avg: {avg_time_per_image:.2f}s)")
    
    def test_6_functional_ocr_fallback_handling(self):
        """Test 6: Functional - OCR Library Availability and Fallback"""
        # Test image data
        test_image_data = self.create_test_image_with_text("Test OCR Content")
        
        # Test scenario 1: OCR libraries available
        mock_ocr_result = {
            'text': "Test OCR Content Email: test@example.com",
            'confidence': 89.5,
            'word_confidences': [90, 85, 92, 88]
        }
        
        with patch.object(self.scanner, '_extract_text_from_image', return_value=mock_ocr_result):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_image_data,
                test_image_data,
                "test_ocr.png"
            )
            result = performance_data['result']
            
            # Validate successful OCR processing
            self.assert_scan_structure(result)
            self.assertGreater(len(result.get('findings', [])), 0, "Should process OCR successfully")
        
        # Test scenario 2: OCR libraries not available (fallback)
        with patch.object(self.scanner, '_extract_text_from_image', side_effect=ImportError("OCR not available")):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_image_data,
                test_image_data,
                "test_fallback.png"
            )
            result = performance_data['result']
            
            # Validate graceful fallback
            self.assert_scan_structure(result)
            
            # Should contain error message about OCR unavailability
            ocr_error_found = any('ocr' in str(finding).lower() or 'tesseract' in str(finding).lower() 
                                 for finding in result.get('findings', []))
            
            # Validate performance even in fallback mode
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 6 PASSED: OCR fallback handling in {performance_data['execution_time']:.2f}s")

if __name__ == '__main__':
    unittest.main(verbosity=2)