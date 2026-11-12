#!/usr/bin/env python3
"""
Unit tests for Dynamic Profile Size Limit Diagnostic Tool (profile_size_test.py).
"""

import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Add profile_size_test directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from profile_size_test.profile_size_test import ProfileGenerator, ProfileRunner, format_report
except (ImportError, ModuleNotFoundError):
    from profile_size_test import ProfileGenerator, ProfileRunner, format_report


class TestProfileGenerator(unittest.TestCase):
    """Test dynamic JSON profile generator logic."""

    def test_generate_small_payload_schema(self):
        payload = ProfileGenerator.generate_payload(15)
        self.assertIn('editors', payload)
        self.assertIn('nodedefs', payload)
        self.assertIn('linkdefs', payload)
        self.assertTrue(len(payload['editors']) >= 3)
        self.assertTrue(len(payload['nodedefs']) >= 1)

        # Check setup nodeDef exists
        setup_nd = next((nd for nd in payload['nodedefs'] if nd['id'] == 'SETUP'), None)
        self.assertIsNotNone(setup_nd)
        self.assertIn('properties', setup_nd)
        self.assertIn('cmds', setup_nd)

        # Check payload size is approximately 15 KB (+/- 3KB)
        payload_bytes = len(json.dumps(payload).encode('utf-8'))
        self.assertTrue(12000 <= payload_bytes <= 18000)

    def test_generate_large_payload_schema(self):
        payload = ProfileGenerator.generate_payload(80)
        payload_bytes = len(json.dumps(payload).encode('utf-8'))
        self.assertTrue(payload_bytes >= 80 * 1024)
        self.assertTrue(len(payload['nodedefs']) > 50)
        self.assertTrue(len(payload['editors']) > 50)

    def test_load_payload_from_file(self):
        test_file = os.path.join(SCRIPT_DIR, 'temp_test_profile.json')
        sample = {
            'editors': [{'id': 'ED1', 'ranges': []}],
            'nodedefs': [{'id': 'ND1', 'properties': [], 'cmds': {}}],
            'linkdefs': []
        }
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(sample, f)
            loaded = ProfileGenerator.load_payload_from_file(test_file)
            self.assertEqual(loaded['editors'], sample['editors'])
            self.assertEqual(loaded['nodedefs'], sample['nodedefs'])
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_load_payload_from_invalid_file(self):
        test_file = os.path.join(SCRIPT_DIR, 'temp_invalid.json')
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump({'invalid': 123}, f)
            with self.assertRaises(ValueError):
                ProfileGenerator.load_payload_from_file(test_file)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


class TestProfileRunnerMockMode(unittest.TestCase):
    """Test ProfileRunner in mock/simulation mode."""

    def setUp(self):
        self.runner = ProfileRunner(mock=True, broker_limit_kb=64)

    def test_small_payload_passes_mock(self):
        small_payload = ProfileGenerator.generate_payload(15)
        success, msg, elapsed = self.runner.update_profile(small_payload)
        self.assertTrue(success)
        self.assertIn("Success", msg)
        self.assertTrue(elapsed >= 0)

    def test_large_payload_fails_mock(self):
        large_payload = ProfileGenerator.generate_payload(80)
        success, msg, elapsed = self.runner.update_profile(large_payload)
        self.assertFalse(success)
        self.assertIn("RuntimeError", msg)
        self.assertIn("exceeds broker maximum packet threshold", msg)


class TestReportFormatting(unittest.TestCase):
    """Test ASCII diagnostic report formatter."""

    def test_report_includes_boundary_conclusion(self):
        results = [
            {
                "name": "Test 1: Small",
                "bytes": 15000,
                "size_kb": 14.65,
                "size_str": "14.6 KB",
                "counts": "10nd/15ed",
                "elapsed": 0.05,
                "success": True,
                "detail": "Success"
            },
            {
                "name": "Test 2: Large",
                "bytes": 90000,
                "size_kb": 87.89,
                "size_str": "87.9 KB",
                "counts": "90nd/100ed",
                "elapsed": 0.05,
                "success": False,
                "detail": "RuntimeError: Update profile request failed"
            }
        ]
        report = format_report(results, "Simulation / Mock")
        self.assertIn("DYNAMIC JSON PROFILE SIZE REPRODUCTION REPORT", report)
        self.assertIn("PASS", report)
        self.assertIn("FAIL (ERROR)", report)
        self.assertIn("Failure boundary is located between", report)
        self.assertIn("87.9 KB", report)
        self.assertIn("Bug confirmed", report)


if __name__ == '__main__':
    unittest.main()
