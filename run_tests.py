#!/usr/bin/env python
"""
Test runner script for Niagara University Scheduler

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py core         # Run core tests only
    python run_tests.py event        # Run event filtering tests only
    python run_tests.py docx         # Run DOCX editing tests only
"""

import sys
import unittest

def run_tests(suite_name=None):
    """Run test suites based on the provided name"""
    
    if suite_name == 'core':
        # Run core functionality tests
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTest(loader.loadTestsFromName('tests.core.test_event_filtering'))
        suite.addTest(loader.loadTestsFromName('tests.core.test_calendar_loader'))
        suite.addTest(loader.loadTestsFromName('tests.core.test_docx_editor'))
        
    elif suite_name == 'event':
        # Run just event filtering tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('tests.core.test_event_filtering')
        
    elif suite_name == 'docx':
        # Run just DOCX editing tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('tests.core.test_docx_editor')
        
    else:
        # Run all tests
        loader = unittest.TestLoader()
        suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    suite_name = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_tests(suite_name)
    sys.exit(0 if success else 1)