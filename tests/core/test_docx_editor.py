#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import unittest
import tempfile
from core.docx_editor import (
    create_enhanced_docx_editor, 
    create_custom_syllabus_template,
    enhance_syllabus_docx,
    install_docx_support
)

class TestDocxEditor(unittest.TestCase):

    def test_docx_support_available(self):
        """Test if DOCX editing support is available"""
        available, message = install_docx_support()
        # Should be available since we installed python-docx
        self.assertTrue(available, f"DOCX support not available: {message}")

    def test_create_enhanced_editor(self):
        """Test creating enhanced DOCX editor components"""
        available, Document, Inches, WD_ALIGN_PARAGRAPH, WD_TABLE_ALIGNMENT = create_enhanced_docx_editor()
        
        if available:
            self.assertIsNotNone(Document)
            self.assertIsNotNone(Inches)
            self.assertIsNotNone(WD_ALIGN_PARAGRAPH)
            self.assertIsNotNone(WD_TABLE_ALIGNMENT)
        else:
            self.skipTest("python-docx not available for testing")

    def test_create_custom_template(self):
        """Test creating custom syllabus template"""
        success, result = create_custom_syllabus_template()
        
        if not success:
            self.skipTest(f"Cannot create template: {result}")
        
        self.assertTrue(success)
        self.assertIsNotNone(result)
        
        # Test saving the template
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            try:
                result.save(temp_file.name)
                # Check if file was created
                self.assertTrue(os.path.exists(temp_file.name))
                # Check file size is reasonable (should have content)
                self.assertGreater(os.path.getsize(temp_file.name), 1000)
            finally:
                # Clean up
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)

    def test_enhance_syllabus_docx(self):
        """Test enhancing a DOCX syllabus with schedule data"""
        # First create a template
        success, template_doc = create_custom_syllabus_template()
        
        if not success:
            self.skipTest(f"Cannot create template: {template_doc}")
        
        # Save template to temporary file
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as template_file:
            template_doc.save(template_file.name)
            template_path = template_file.name
        
        # Test data
        schedule_data = [
            "Monday, September 7, 2025",
            "Wednesday, September 9, 2025", 
            "Friday, September 11, 2025 - Patriot Day Remembrance",
            "Monday, September 14, 2025"
        ]
        
        # Create output file
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Test enhancing the template
            success = enhance_syllabus_docx(
                template_path, 
                schedule_data, 
                output_path, 
                'Fall', 
                '2025'
            )
            
            self.assertTrue(success, "Failed to enhance syllabus DOCX")
            
            # Check output file exists and has content
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 1000)
            
        finally:
            # Clean up
            if os.path.exists(template_path):
                os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_enhance_nonexistent_template(self):
        """Test enhancing with non-existent template file"""
        schedule_data = ["Monday, September 7, 2025"]
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            success = enhance_syllabus_docx(
                "nonexistent_template.docx",
                schedule_data,
                output_path,
                'Fall',
                '2025'
            )
            
            # Should fail gracefully
            self.assertFalse(success)
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

if __name__ == '__main__':
    unittest.main()