#!/usr/bin/env python3
"""
Dynamic JSON Profile Size Limit Diagnostic Tool
------------------------------------------------
A standalone diagnostic tool for Universal Devices Polyglot (PG3/PG3x) and IoX
to demonstrate, reproduce, and pinpoint the dynamic JSON profile payload size bug
in polyglot.updateJsonProfile() against live PG3x hardware and MQTT broker.

This tool runs strictly on PG3x hardware (eisy or Polisy). It connects directly
to the PG3x MQTT broker using udi_interface. There is NO mock or simulation mode.

When installed via PG3:
- Configurable via the PG3 Web Dashboard under Configuration -> Custom Configuration Parameters
  (mode, sweep_start, sweep_end, sweep_step, small_kb, large_kb).
- Full reproduction report logged directly in PG3 Node Server Log.
- Reports status to IoX via drivers: ST, GV1 (Result), GV2 (Min Fail KB), GV3 (Max Pass KB).
"""

import sys
import os
import json
import time
import argparse
import logging
from typing import Dict, Any, Tuple, Optional, List

VERSION = "1.0.0"

try:
    import udi_interface
except ImportError:
    udi_interface = None


def log_msg(msg: str):
    """Log to stdout and PG3 LOGGER."""
    print(msg)
    if udi_interface and hasattr(udi_interface, 'LOGGER'):
        try:
            udi_interface.LOGGER.info(msg)
        except Exception:
            pass
    else:
        logging.info(msg)


class ProfileGenerator:
    """Generates valid, realistic IoX/PG3 dynamic profile JSON structures."""

    # Standard editor templates following IoX UOM conventions
    SAMPLE_EDITORS = [
        {"id": "STATUS", "ranges": [{"uom": "25", "subset": "0,1", "names": {"0": "Not Connected", "1": "Connected"}}]},
        {"id": "SWSTATE", "ranges": [{"uom": "25", "subset": "0,1,99", "names": {"0": "Off", "1": "On", "99": "Unknown"}}]},
        {"id": "TEMP_C", "ranges": [{"uom": "4", "min": -40, "max": 100, "prec": 1}, {"uom": "25", "subset": "99", "names": {"99": "Unknown"}}]},
        {"id": "TEMP_F", "ranges": [{"uom": "17", "min": -40, "max": 212, "prec": 1}, {"uom": "25", "subset": "99", "names": {"99": "Unknown"}}]},
        {"id": "HUMIDITY", "ranges": [{"uom": "51", "min": 0, "max": 100, "prec": 1}]},
        {"id": "PERCENT", "ranges": [{"uom": "51", "min": 0, "max": 100, "prec": 0}]},
        {"id": "DELAYSEC", "ranges": [{"uom": "57", "min": 0, "max": 86400, "prec": 0}]},
        {"id": "DELAYMIN", "ranges": [{"uom": "44", "min": 0, "max": 1440, "prec": 0}]},
        {"id": "BATLVL", "ranges": [{"uom": "25", "subset": "0,1,2,3,4,99", "names": {"0": "Low", "1": "MedLow", "2": "Med", "3": "MedHigh", "4": "High", "99": "Unknown"}}]},
        {"id": "DOORSTATE", "ranges": [{"uom": "25", "subset": "0,1,99", "names": {"0": "Closed", "1": "Open", "99": "Unknown"}}]},
        {"id": "MOTIONSTATE", "ranges": [{"uom": "25", "subset": "0,1,99", "names": {"0": "No Motion", "1": "Motion", "99": "Unknown"}}]},
        {"id": "WATERSTATE", "ranges": [{"uom": "25", "subset": "0,1,99", "names": {"0": "Dry", "1": "Wet", "99": "Unknown"}}]},
        {"id": "FLOWRATE", "ranges": [{"uom": "69", "min": 0, "max": 10000, "prec": 1}, {"uom": "25", "subset": "99", "names": {"99": "Unknown"}}]},
        {"id": "POWERWATT", "ranges": [{"uom": "73", "min": -1, "max": 5000, "prec": 2}]},
        {"id": "ENERGYKWH", "ranges": [{"uom": "119", "min": -1, "max": 10000, "prec": 2}]},
        {"id": "CMDOPT", "ranges": [{"uom": "25", "subset": "0,1,2,3", "names": {"0": "DON/DOF", "1": "DON Only", "2": "DOF Only", "3": "None"}}]},
        {"id": "UNIXTIME", "ranges": [{"uom": "151", "min": 1700000000, "max": 9999999999, "prec": 0}]},
    ]

    @classmethod
    def make_editor(cls, index: int) -> Dict[str, Any]:
        """Create a uniquely identified valid editor dictionary."""
        base = cls.SAMPLE_EDITORS[index % len(cls.SAMPLE_EDITORS)]
        ed_id = f"{base['id']}_{index}"
        ranges = []
        for r in base['ranges']:
            r_copy = dict(r)
            if 'names' in r_copy:
                r_copy['names'] = dict(r_copy['names'])
            ranges.append(r_copy)
        return {"id": ed_id, "ranges": ranges}

    @classmethod
    def make_nodedef(cls, index: int, editor_ids: List[str]) -> Dict[str, Any]:
        """Create a uniquely identified valid nodeDef dictionary."""
        node_id = f"NODE_{index:03d}"
        props = []
        for p_idx in range(5):
            ed = editor_ids[(index * 5 + p_idx) % len(editor_ids)] if editor_ids else "STATUS"
            props.append({
                "id": f"GV{p_idx}",
                "editor": ed,
                "name": f"Driver {p_idx} for Node {index}"
            })

        accepts = [
            {
                "id": f"CMD_{c_idx}",
                "name": f"Command {c_idx}",
                "parameters": [
                    {
                        "id": "PARAM1",
                        "name": f"Param {c_idx}",
                        "editor": editor_ids[c_idx % len(editor_ids)] if editor_ids else "STATUS"
                    }
                ]
            }
            for c_idx in range(3)
        ]

        return {
            "id": node_id,
            "name": f"Diagnostic Device Node {index}",
            "icon": "GenericCtl",
            "properties": props,
            "cmds": {
                "accepts": accepts,
                "sends": [{"id": "DON"}, {"id": "DOF"}]
            },
            "links": {"ctl": [], "rsp": []}
        }

    @classmethod
    def generate_payload(cls, target_kb: int) -> Dict[str, Any]:
        """
        Generate a strictly valid IoX/PG3 dynamic profile payload scaled to approximately target_kb KB.
        """
        target_bytes = target_kb * 1024

        editors = [
            {"id": "STATUS", "ranges": [{"uom": "25", "subset": "0,1", "names": {"0": "Not Connected", "1": "Connected"}}]},
            {"id": "READY", "ranges": [{"uom": "25", "subset": "0,1", "names": {"0": "Initializing", "1": "Ready"}}]},
            {"id": "TIME", "ranges": [{"uom": "151", "min": 1700000000, "max": 9999999999, "prec": 0}]},
        ]
        nodedefs = [
            {
                "id": "SETUP",
                "name": "Diagnostic Profile Controller",
                "icon": "GenericCtl",
                "properties": [
                    {"id": "ST", "editor": "STATUS", "name": "Node Server Status"},
                    {"id": "GV1", "editor": "READY", "name": "Profile Status"},
                    {"id": "TIME", "editor": "TIME", "name": "Last Update"}
                ],
                "cmds": {"accepts": [], "sends": [{"id": "DON"}, {"id": "DOF"}]},
                "links": {"ctl": [], "rsp": []}
            }
        ]

        ed_count = 0
        nd_count = 1

        while True:
            payload = {
                "editors": editors,
                "nodedefs": nodedefs,
                "linkdefs": []
            }
            current_bytes = len(json.dumps(payload).encode('utf-8'))
            if current_bytes >= target_bytes:
                break

            editors.append(cls.make_editor(ed_count))
            ed_count += 1

            payload["editors"] = editors
            if len(json.dumps(payload).encode('utf-8')) >= target_bytes:
                break

            editor_ids = [e["id"] for e in editors]
            nodedefs.append(cls.make_nodedef(nd_count, editor_ids))
            nd_count += 1

        return {
            "editors": editors,
            "nodedefs": nodedefs,
            "linkdefs": []
        }

    @classmethod
    def load_payload_from_file(cls, file_path: str) -> Dict[str, Any]:
        """Load profile payload from an external JSON file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Profile JSON file not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict) or 'nodedefs' not in data or 'editors' not in data:
            raise ValueError(f"Invalid profile format in {file_path}. Must contain 'nodedefs' and 'editors'.")
        return data


class TestControlNode(udi_interface.Node if udi_interface else object):
    """Controller node representing the diagnostic tool in IoX / PG3."""
    id = 'TESTCTRL'
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 25, 'name': 'Controller Status'},
        {'driver': 'GV1', 'value': 0, 'uom': 25, 'name': 'Test Result'},
        {'driver': 'GV2', 'value': 0, 'uom': 56, 'name': 'Min Fail Size (KB)'},
        {'driver': 'GV3', 'value': 0, 'uom': 56, 'name': 'Max Pass Size (KB)'},
    ]
    commands = {
        'QUERY': 'query',
        'RUN_TEST': 'cmd_run_test',
        'RUN_SWEEP': 'cmd_run_sweep',
    }

    def __init__(self, polyglot, primary, address, name, runner=None):
        if udi_interface:
            super().__init__(polyglot, primary, address, name)
        self.runner = runner

    def query(self):
        if hasattr(self, 'reportDrivers'):
            self.reportDrivers()

    def cmd_run_test(self, command=None):
        log_msg("[COMMAND] Received RUN_TEST command from IoX.")
        if self.runner:
            self.runner.run_two_tier()

    def cmd_run_sweep(self, command=None):
        log_msg("[COMMAND] Received RUN_SWEEP command from IoX.")
        if self.runner:
            self.runner.run_sweep()


class ProfileRunner:
    """Manages profile loading via live udi_interface connected to PG3x MQTT."""

    def __init__(self):
        if udi_interface is None:
            raise RuntimeError(
                "udi_interface module is not installed.\n"
                "This tool requires PG3x hardware (eisy or Polisy) with udi_interface installed.\n"
                "It cannot run on macOS or non-PG3 environments."
            )
        self.polyglot = None
        self.ctrl_node = None
        self.params = {
            'mode': 'sweep',
            'sweep_start': 20,
            'sweep_end': 100,
            'sweep_step': 10,
            'small_kb': 15,
            'large_kb': 90
        }
        self.last_results = []
        self._init_runner()

    def _init_runner(self):
        if 'PG3INIT' not in os.environ:
            raise RuntimeError(
                "PG3INIT environment variable is not set.\n"
                "udi_interface requires PG3INIT to authenticate and connect to the local PG3x MQTT broker.\n\n"
                "To run this test on your eisy/Polisy:\n"
                "  Option 1 (Recommended): Install and run this as a Custom Node Server via the PG3x Web Dashboard.\n"
                "                         PG3x will supply PG3INIT and establish the live TLS MQTT connection.\n"
                "  Option 2 (SSH CLI): Export PG3INIT from an existing active node server slot before running:\n"
                "                     export PG3INIT=$(tr '\\0' '\\n' < /proc/$(pgrep -f 'udi-YoLink|polyglot' | head -n 1)/environ | grep '^PG3INIT=' | cut -d= -f2-)\n"
                "                     python3 profile_size_test.py"
            )

        # Initialize live Polyglot interface
        self.polyglot = udi_interface.Interface([])

        # Subscribe to PG3 configuration and lifecycle events
        self.polyglot.subscribe(self.polyglot.CUSTOMPARAMS, self.parameter_handler)
        self.polyglot.subscribe(self.polyglot.STOP, self.stop_handler)

        self.polyglot.start(VERSION)
        self.ctrl_node = TestControlNode(self.polyglot, 'testctrl', 'testctrl', 'Profile Test Controller', runner=self)
        if hasattr(self.polyglot, 'addNode'):
            self.polyglot.addNode(self.ctrl_node)
        self.polyglot.ready()
        time.sleep(1.0)

    def stop_handler(self):
        log_msg("[PG3] Received stop signal.")
        self.shutdown()

    def parameter_handler(self, user_data: Dict[str, Any]):
        """Called whenever PG3 pushes Custom Configuration Parameters from the dashboard."""
        if not user_data:
            return

        log_msg(f"\n[PG3 Configuration] Received custom parameters: {user_data}")
        try:
            if 'mode' in user_data and str(user_data['mode']).strip():
                self.params['mode'] = str(user_data['mode']).strip().lower()
            if 'sweep_start' in user_data and str(user_data['sweep_start']).strip():
                self.params['sweep_start'] = int(user_data['sweep_start'])
            if 'sweep_end' in user_data and str(user_data['sweep_end']).strip():
                self.params['sweep_end'] = int(user_data['sweep_end'])
            if 'sweep_step' in user_data and str(user_data['sweep_step']).strip():
                self.params['sweep_step'] = int(user_data['sweep_step'])
            if 'small_kb' in user_data and str(user_data['small_kb']).strip():
                self.params['small_kb'] = int(user_data['small_kb'])
            if 'large_kb' in user_data and str(user_data['large_kb']).strip():
                self.params['large_kb'] = int(user_data['large_kb'])
        except Exception as e:
            log_msg(f"[WARN] Error parsing custom parameters: {e}")

        # Automatically execute configured test/sweep upon receiving parameters
        self.execute_tests()

    def execute_tests(self):
        """Run tests according to current configuration."""
        mode = self.params.get('mode', 'sweep')
        if mode == 'sweep':
            self.run_sweep(
                start_kb=self.params.get('sweep_start', 20),
                end_kb=self.params.get('sweep_end', 100),
                step_kb=self.params.get('sweep_step', 10)
            )
        else:
            self.run_two_tier(
                small_kb=self.params.get('small_kb', 15),
                large_kb=self.params.get('large_kb', 90)
            )

    def run_sweep(self, start_kb: int = None, end_kb: int = None, step_kb: int = None) -> List[Dict[str, Any]]:
        start_kb = start_kb if start_kb is not None else self.params.get('sweep_start', 20)
        end_kb = end_kb if end_kb is not None else self.params.get('sweep_end', 100)
        step_kb = step_kb if step_kb is not None else self.params.get('sweep_step', 10)

        log_msg(f"\n[SWEEP] Starting size sweep from {start_kb} KB to {end_kb} KB (step: {step_kb} KB)...")
        results = []
        for size_kb in range(start_kb, end_kb + 1, step_kb):
            payload = ProfileGenerator.generate_payload(size_kb)
            p_bytes = len(json.dumps(payload).encode('utf-8'))
            nd_cnt = len(payload.get('nodedefs', []))
            ed_cnt = len(payload.get('editors', []))
            log_msg(f"  -> Testing payload ~{size_kb} KB ({p_bytes:,} bytes, {nd_cnt} nodeDefs, {ed_cnt} editors)...")
            success, msg, elapsed = self.update_profile(payload)
            results.append({
                "name": f"Sweep: {size_kb} KB",
                "bytes": p_bytes,
                "size_kb": p_bytes / 1024,
                "size_str": f"{p_bytes/1024:.1f} KB",
                "counts": f"{nd_cnt}nd/{ed_cnt}ed",
                "elapsed": elapsed,
                "success": success,
                "detail": msg
            })

        self.last_results = results
        report = format_report(results)
        log_msg("\n" + report + "\n")
        self._update_node_drivers(results)
        return results

    def run_two_tier(self, small_kb: int = None, large_kb: int = None, dump: bool = False, dump_dir: str = ".") -> List[Dict[str, Any]]:
        small_kb = small_kb if small_kb is not None else self.params.get('small_kb', 15)
        large_kb = large_kb if large_kb is not None else self.params.get('large_kb', 90)

        log_msg(f"\n[TWO-TIER TEST] Running small ({small_kb} KB) vs large ({large_kb} KB) profile test...")
        results = []

        # 1. Small payload
        small_payload = ProfileGenerator.generate_payload(small_kb)
        small_bytes = len(json.dumps(small_payload).encode('utf-8'))
        small_nd = len(small_payload.get('nodedefs', []))
        small_ed = len(small_payload.get('editors', []))
        log_msg(f"   Executing updateJsonProfile for Small Payload ({small_bytes:,} bytes)...")
        small_ok, small_msg, small_el = self.update_profile(small_payload)
        results.append({
            "name": "Test 1: Small Payload",
            "bytes": small_bytes,
            "size_kb": small_bytes / 1024,
            "size_str": f"{small_bytes/1024:.1f} KB",
            "counts": f"{small_nd}nd/{small_ed}ed",
            "elapsed": small_el,
            "success": small_ok,
            "detail": small_msg
        })

        # 2. Large payload
        large_payload = ProfileGenerator.generate_payload(large_kb)
        large_bytes = len(json.dumps(large_payload).encode('utf-8'))
        large_nd = len(large_payload.get('nodedefs', []))
        large_ed = len(large_payload.get('editors', []))
        log_msg(f"   Executing updateJsonProfile for Large Payload ({large_bytes:,} bytes)...")
        large_ok, large_msg, large_el = self.update_profile(large_payload)
        results.append({
            "name": "Test 2: Large Payload",
            "bytes": large_bytes,
            "size_kb": large_bytes / 1024,
            "size_str": f"{large_bytes/1024:.1f} KB",
            "counts": f"{large_nd}nd/{large_ed}ed",
            "elapsed": large_el,
            "success": large_ok,
            "detail": large_msg
        })

        if dump:
            os.makedirs(dump_dir, exist_ok=True)
            small_file = os.path.join(dump_dir, "profile_test_small.json")
            large_file = os.path.join(dump_dir, "profile_test_large.json")
            with open(small_file, 'w', encoding='utf-8') as f:
                json.dump(small_payload, f, indent=2)
            with open(large_file, 'w', encoding='utf-8') as f:
                json.dump(large_payload, f, indent=2)
            log_msg(f"[INFO] Dumped payloads to:\n  - {small_file} ({small_bytes:,} bytes)\n  - {large_file} ({large_bytes:,} bytes)")

        self.last_results = results
        report = format_report(results)
        log_msg("\n" + report + "\n")
        self._update_node_drivers(results)
        return results

    def _update_node_drivers(self, results: List[Dict[str, Any]]):
        if not self.ctrl_node:
            return
        try:
            passed = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]

            # GV1: 1 = All Pass, 2 = Bug Confirmed (both pass & fail), 3 = All Fail
            if passed and failed:
                res_val = 2
            elif passed and not failed:
                res_val = 1
            else:
                res_val = 3

            min_fail_kb = round(min(failed, key=lambda x: x['bytes'])['size_kb'], 1) if failed else 0
            max_pass_kb = round(max(passed, key=lambda x: x['bytes'])['size_kb'], 1) if passed else 0

            if hasattr(self.ctrl_node, 'setDriver'):
                self.ctrl_node.setDriver('ST', 1)
                self.ctrl_node.setDriver('GV1', res_val)
                self.ctrl_node.setDriver('GV2', min_fail_kb)
                self.ctrl_node.setDriver('GV3', max_pass_kb)
            if hasattr(self.ctrl_node, 'reportDrivers'):
                self.ctrl_node.reportDrivers()
        except Exception as e:
            log_msg(f"[WARN] Failed to update node drivers: {e}")

    def update_profile(self, payload: Dict[str, Any]) -> Tuple[bool, str, float]:
        """
        Attempt to send dynamic JSON profile over the live Polyglot MQTT broker.
        Returns: (success: bool, detail_message: str, elapsed_seconds: float)
        """
        payload_json = json.dumps(payload)
        payload_bytes = len(payload_json.encode('utf-8'))
        start_time = time.time()

        updater = getattr(self.polyglot, "updateJsonProfile", None)
        if not callable(updater):
            elapsed = time.time() - start_time
            return False, "polyglot.updateJsonProfile method is not available on this interface", elapsed

        try:
            try:
                updater(payload, {"waitResponse": True})
            except TypeError:
                updater(payload)

            elapsed = time.time() - start_time
            return True, f"Success ({payload_bytes:,} bytes accepted by Polyglot MQTT)", elapsed
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"MQTT/Polyglot Rejection: {e}", elapsed

    def shutdown(self):
        if self.polyglot and hasattr(self.polyglot, 'stop'):
            try:
                self.polyglot.stop()
            except Exception:
                pass


def format_report(results: List[Dict[str, Any]]) -> str:
    """Format diagnostic test results into a clean, presentation-ready ASCII report."""
    lines = []
    lines.append("=" * 80)
    lines.append("        UNIVERSAL DEVICES DYNAMIC JSON PROFILE SIZE REPRODUCTION REPORT")
    lines.append("=" * 80)
    lines.append("Execution Mode : Live PG3x Hardware (udi_interface / TLS MQTT)")
    lines.append(f"Version        : v{VERSION}")
    lines.append(f"Timestamp      : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("-" * 80)
    lines.append(f"{'Test Description':<25} | {'Size':<12} | {'Nodes/Eds':<12} | {'Time':<8} | {'Status':<10}")
    lines.append("-" * 80)

    for r in results:
        status_str = "PASS" if r['success'] else "FAIL (ERROR)"
        lines.append(
            f"{r['name']:<25} | "
            f"{r['size_str']:<12} | "
            f"{r['counts']:<12} | "
            f"{r['elapsed']:<7.2f}s | "
            f"{status_str:<10}"
        )
        if not r['success'] and r.get('detail'):
            lines.append(f"  └── Detail: {r['detail']}")

    lines.append("-" * 80)

    passed_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]

    if passed_tests and failed_tests:
        max_pass = max(passed_tests, key=lambda x: x['bytes'])
        min_fail = min(failed_tests, key=lambda x: x['bytes'])
        lines.append("DIAGNOSTIC CONCLUSION:")
        lines.append(f"  [✓] Smallest failure size : {min_fail['bytes']:,} bytes ({min_fail['size_kb']:.1f} KB)")
        lines.append(f"  [✓] Largest passing size  : {max_pass['bytes']:,} bytes ({max_pass['size_kb']:.1f} KB)")
        lines.append(f"  [!] Failure boundary is located between {max_pass['size_kb']:.1f} KB and {min_fail['size_kb']:.1f} KB.")
        lines.append("  [!] Bug confirmed: Dynamic JSON profiles fail when structure exceeds threshold.")
    elif failed_tests and not passed_tests:
        lines.append("DIAGNOSTIC CONCLUSION: All tested payload sizes failed.")
    else:
        lines.append("DIAGNOSTIC CONCLUSION: All tested payload sizes passed without error.")

    lines.append("=" * 80)
    return "\n".join(lines)


def main():
    if udi_interface is None:
        print("\n" + "=" * 80, file=sys.stderr)
        print("FATAL ERROR: udi_interface is not installed.", file=sys.stderr)
        print("This tool requires PG3x hardware (eisy or Polisy) and cannot run on macOS.", file=sys.stderr)
        print("=" * 80 + "\n", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(
        description="Diagnostic tool to reproduce dynamic JSON profile payload size limit in Polyglot / IoX."
    )
    parser.add_argument(
        "--small-kb",
        type=int,
        default=15,
        help="Target size in KB for small (passing) payload (default: 15)"
    )
    parser.add_argument(
        "--large-kb",
        type=int,
        default=90,
        help="Target size in KB for large (failing) payload (default: 90)"
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Run an incremental size sweep to find the exact threshold where updates fail"
    )
    parser.add_argument(
        "--sweep-start",
        type=int,
        default=20,
        help="Sweep start size in KB (default: 20)"
    )
    parser.add_argument(
        "--sweep-end",
        type=int,
        default=100,
        help="Sweep end size in KB (default: 100)"
    )
    parser.add_argument(
        "--sweep-step",
        type=int,
        default=10,
        help="Sweep step size in KB (default: 10)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to an existing profile JSON file to test directly"
    )
    parser.add_argument(
        "--dump",
        action="store_true",
        help="Dump generated small/large JSON payloads to disk (profile_test_small.json, profile_test_large.json)"
    )
    parser.add_argument(
        "--dump-dir",
        type=str,
        default=".",
        help="Directory to write dumped payloads to (default: current directory)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Keep node server alive after test execution (calls polyglot.runForever)"
    )

    args = parser.parse_args()

    try:
        runner = ProfileRunner()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}\n", file=sys.stderr)
        return 1

    # Check if run with explicit CLI parameters (e.g. from SSH interactive terminal)
    cli_mode_explicit = args.sweep or args.file or args.dump or ('--small-kb' in sys.argv) or ('--large-kb' in sys.argv)

    if cli_mode_explicit:
        log_msg("\nExecuting Dynamic Profile Size Limit Diagnostic Tool via CLI...\n")
        try:
            if args.file:
                payload = ProfileGenerator.load_payload_from_file(args.file)
                p_bytes = len(json.dumps(payload).encode('utf-8'))
                nd_cnt = len(payload.get('nodedefs', []))
                ed_cnt = len(payload.get('editors', []))
                success, msg, elapsed = runner.update_profile(payload)
                report = format_report([{
                    "name": f"File: {os.path.basename(args.file)}",
                    "bytes": p_bytes,
                    "size_kb": p_bytes / 1024,
                    "size_str": f"{p_bytes/1024:.1f} KB",
                    "counts": f"{nd_cnt}nd/{ed_cnt}ed",
                    "elapsed": elapsed,
                    "success": success,
                    "detail": msg
                }])
                log_msg("\n" + report + "\n")
            elif args.sweep:
                runner.run_sweep(args.sweep_start, args.sweep_end, args.sweep_step)
            else:
                runner.run_two_tier(args.small_kb, args.large_kb, dump=args.dump, dump_dir=args.dump_dir)
        finally:
            if not args.daemon:
                runner.shutdown()
                return 0

    # Default PG3 Node Server Mode (managed by PG3 daemon)
    log_msg("[PG3] ProfileSizeTest Node Server started. Waiting for PG3 events / customParams...")
    try:
        # Run tests with default configuration initially
        runner.execute_tests()
        
        # Enter PG3 event loop
        runner.polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        runner.shutdown()

    return 0


if __name__ == "__main__":
    sys.exit(main())
