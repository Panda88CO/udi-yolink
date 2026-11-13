#!/usr/bin/env python3
"""
Unit tests for Dynamic Profile Size Limit Diagnostic Tool (profile_size_test.py).
Verifies generator, PG3x interface handling, error trapping, and report formatting.
"""

import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

class MockNode:
    id = ''
    drivers = []
    commands = {}
    def __init__(self, *args, **kwargs):
        pass

# Ensure udi_interface is mockable in test environments lacking PG3 hardware
if 'udi_interface' not in sys.modules:
    mock_udi = MagicMock()
    mock_udi.Node = MockNode
    sys.modules['udi_interface'] = mock_udi

import profile_size_test as pst_mod
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


class TestProfileRunnerLiveHardware(unittest.TestCase):
    """Test ProfileRunner behavior with PG3x hardware interface."""

    def test_missing_udi_interface_raises_runtime_error(self):
        with patch.object(pst_mod, 'udi_interface', None):
            with self.assertRaises(RuntimeError) as ctx:
                ProfileRunner()
            self.assertIn("udi_interface module is not installed", str(ctx.exception))

    def test_missing_pg3init_raises_runtime_error(self):
        # Ensure PG3INIT is absent
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                ProfileRunner()
            self.assertIn("PG3INIT environment variable is not set", str(ctx.exception))
            self.assertIn("Custom Node Server via the PG3x Web Dashboard", str(ctx.exception))

    def test_live_runner_initialization_with_pg3init(self):
        mock_iface_inst = MagicMock()
        mock_udi = MagicMock()
        mock_udi.Interface.return_value = mock_iface_inst
        mock_udi.Node = MockNode

        with patch.dict(os.environ, {'PG3INIT': 'fake_base64_init'}):
            with patch.object(pst_mod, 'udi_interface', mock_udi):
                with patch('time.sleep', return_value=None):
                    runner = ProfileRunner()
                    mock_udi.Interface.assert_called_once_with([])
                    mock_iface_inst.start.assert_called_once_with('1.0.0')
                    mock_iface_inst.ready.assert_called_once()
                    self.assertEqual(runner.polyglot, mock_iface_inst)

    def test_update_profile_success(self):
        mock_iface_inst = MagicMock()
        mock_iface_inst.updateJsonProfile = MagicMock(return_value=True)
        mock_udi = MagicMock()
        mock_udi.Interface.return_value = mock_iface_inst
        mock_udi.Node = MockNode

        with patch.dict(os.environ, {'PG3INIT': 'fake_base64_init'}):
            with patch.object(pst_mod, 'udi_interface', mock_udi):
                with patch('time.sleep', return_value=None):
                    runner = ProfileRunner()
                    sample_payload = ProfileGenerator.generate_payload(10)
                    success, msg, elapsed = runner.update_profile(sample_payload)

                    self.assertTrue(success)
                    self.assertIn("Success", msg)
                    mock_iface_inst.updateJsonProfile.assert_called_once_with(sample_payload, {"waitResponse": True})

    def test_update_profile_mqtt_rejection(self):
        mock_iface_inst = MagicMock()
        mock_iface_inst.updateJsonProfile = MagicMock(side_effect=RuntimeError("MQTT 413: Payload Too Large"))
        mock_udi = MagicMock()
        mock_udi.Interface.return_value = mock_iface_inst
        mock_udi.Node = MockNode

        with patch.dict(os.environ, {'PG3INIT': 'fake_base64_init'}):
            with patch.object(pst_mod, 'udi_interface', mock_udi):
                with patch('time.sleep', return_value=None):
                    runner = ProfileRunner()
                    sample_payload = ProfileGenerator.generate_payload(80)
                    success, msg, elapsed = runner.update_profile(sample_payload)

                    self.assertFalse(success)
                    self.assertIn("MQTT/Polyglot Rejection", msg)
                    self.assertIn("MQTT 413: Payload Too Large", msg)


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
                "detail": "MQTT/Polyglot Rejection: MQTT 413: Payload Too Large"
            }
        ]
        report = format_report(results)
        self.assertIn("DYNAMIC JSON PROFILE SIZE REPRODUCTION REPORT", report)
        self.assertIn("Execution Mode : Live PG3x Hardware (udi_interface / TLS MQTT)", report)
        self.assertIn("PASS", report)
        self.assertIn("FAIL (ERROR)", report)
        self.assertIn("Failure boundary is located between", report)
        self.assertIn("87.9 KB", report)
        self.assertIn("Bug confirmed", report)


if __name__ == '__main__':
    unittest.main()
