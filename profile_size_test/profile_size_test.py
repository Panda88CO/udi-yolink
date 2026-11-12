#!/usr/bin/env python3
"""
Dynamic JSON Profile Size Limit Diagnostic Tool
------------------------------------------------
A standalone diagnostic tool for Universal Devices Polyglot (PG3/PG3x) and IoX
to demonstrate, reproduce, and pinpoint the dynamic JSON profile payload size bug
in polyglot.updateJsonProfile().

Bug Summary:
  - Small profile payloads (e.g. ~10-15 KB) are accepted and processed successfully.
  - Large profile payloads (e.g. > ~64 KB, full profiles ~90-100 KB) fail with
    MQTT packet rejection, broker buffer drops, or RuntimeError.
"""

import sys
import os
import json
import time
import argparse
from typing import Dict, Any, Tuple, Optional, List

# Try importing udi_interface for live PG3 execution
try:
    import udi_interface
    HAS_UDI = True
except ImportError:
    HAS_UDI = False


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
        # Add 5 drivers per nodeDef
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
        
        # Start with base controller setup definition
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

        # Iteratively expand editors and nodeDefs until target size is reached
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

            # Add an editor
            editors.append(cls.make_editor(ed_count))
            ed_count += 1

            # Check size after editor
            payload["editors"] = editors
            if len(json.dumps(payload).encode('utf-8')) >= target_bytes:
                break

            # Add a nodeDef referencing available editors
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


class ProfileRunner:
    """Manages profile loading via live udi_interface or mock simulation."""

    def __init__(self, mock: bool = False, broker_limit_kb: int = 64):
        self.mock = mock or not HAS_UDI
        self.broker_limit_bytes = broker_limit_kb * 1024
        self.polyglot = None
        self._init_runner()

    def _init_runner(self):
        if self.mock:
            return
        
        try:
            # Initialize live Polyglot interface
            self.polyglot = udi_interface.Interface([])
            
            # Minimal node required by PG3 runtime
            class TestControlNode(udi_interface.Node):
                id = 'TESTCTRL'
                drivers = [{'driver': 'ST', 'value': 1, 'uom': 25, 'name': 'Controller'}]
                commands = {}
            
            self.polyglot.start('1.0.0')
            TestControlNode(self.polyglot, 'testctrl', 'testctrl', 'Test Controller')
            self.polyglot.ready()
            time.sleep(1.0)
        except Exception as e:
            print(f"[WARN] Failed to initialize live udi_interface ({e}). Falling back to simulation mode.")
            self.mock = True
            self.polyglot = None

    def update_profile(self, payload: Dict[str, Any], timeout: float = 10.0) -> Tuple[bool, str, float]:
        """
        Attempt to send dynamic JSON profile.
        Returns: (success: bool, detail_message: str, elapsed_seconds: float)
        """
        payload_json = json.dumps(payload)
        payload_bytes = len(payload_json.encode('utf-8'))
        start_time = time.time()

        if self.mock:
            # Simulate real PG3 / MQTT broker buffer limits
            time.sleep(0.05)
            elapsed = time.time() - start_time
            if payload_bytes > self.broker_limit_bytes:
                err_msg = (
                    f"RuntimeError: Update profile request failed: payload size ({payload_bytes} bytes) "
                    f"exceeds broker maximum packet threshold ({self.broker_limit_bytes} bytes / {self.broker_limit_bytes // 1024} KB)"
                )
                return False, err_msg, elapsed
            return True, f"Success (Simulated acceptance of {payload_bytes} bytes)", elapsed

        # Live Polyglot mode
        try:
            updater = getattr(self.polyglot, "updateJsonProfile", None)
            if not callable(updater):
                elapsed = time.time() - start_time
                return False, "polyglot.updateJsonProfile method is not available on this interface", elapsed

            # Call with waitResponse
            try:
                updater(payload, {"waitResponse": True})
            except TypeError:
                updater(payload)

            elapsed = time.time() - start_time
            return True, f"Success ({payload_bytes} bytes accepted by Polyglot)", elapsed
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Error: {e}", elapsed

    def shutdown(self):
        if self.polyglot and hasattr(self.polyglot, 'stop'):
            try:
                self.polyglot.stop()
            except Exception:
                pass


def format_report(results: List[Dict[str, Any]], runner_mode: str) -> str:
    """Format diagnostic test results into a clean, presentation-ready ASCII report."""
    lines = []
    lines.append("=" * 80)
    lines.append("        UNIVERSAL DEVICES DYNAMIC JSON PROFILE SIZE REPRODUCTION REPORT")
    lines.append("=" * 80)
    lines.append(f"Execution Mode : {runner_mode}")
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
    
    # Analysis & conclusion
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
        "--mock",
        action="store_true",
        help="Force simulation mode for local verification without PG3"
    )
    parser.add_argument(
        "--broker-limit-kb",
        type=int,
        default=64,
        help="Simulated broker buffer limit in KB for mock mode (default: 64)"
    )

    args = parser.parse_args()

    runner = ProfileRunner(mock=args.mock, broker_limit_kb=args.broker_limit_kb)
    runner_mode = "Simulation / Mock" if runner.mock else "Live Polyglot (udi_interface)"

    print(f"\nStarting Dynamic Profile Size Limit Diagnostic Tool [{runner_mode}]...\n")

    results = []

    try:
        # Case 1: Custom file specified
        if args.file:
            print(f"Loading external profile from: {args.file}")
            payload = ProfileGenerator.load_payload_from_file(args.file)
            p_bytes = len(json.dumps(payload).encode('utf-8'))
            nd_cnt = len(payload.get('nodedefs', []))
            ed_cnt = len(payload.get('editors', []))
            print(f"Testing external payload: {p_bytes:,} bytes ({p_bytes/1024:.2f} KB)...")
            success, msg, elapsed = runner.update_profile(payload)
            results.append({
                "name": f"File: {os.path.basename(args.file)}",
                "bytes": p_bytes,
                "size_kb": p_bytes / 1024,
                "size_str": f"{p_bytes/1024:.1f} KB",
                "counts": f"{nd_cnt}nd/{ed_cnt}ed",
                "elapsed": elapsed,
                "success": success,
                "detail": msg
            })

        # Case 2: Sweep mode
        elif args.sweep:
            print(f"Running size sweep from {args.sweep_start} KB to {args.sweep_end} KB (step: {args.sweep_step} KB)...")
            for size_kb in range(args.sweep_start, args.sweep_end + 1, args.sweep_step):
                payload = ProfileGenerator.generate_payload(size_kb)
                p_bytes = len(json.dumps(payload).encode('utf-8'))
                nd_cnt = len(payload.get('nodedefs', []))
                ed_cnt = len(payload.get('editors', []))
                print(f"  -> Testing payload ~{size_kb} KB ({p_bytes:,} bytes, {nd_cnt} nodeDefs, {ed_cnt} editors)...")
                success, msg, elapsed = runner.update_profile(payload)
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

        # Case 3: Standard Comparative Two-Tier Test (Small vs Large)
        else:
            # 1. Small payload (expected to pass)
            print(f"1. Generating Small Payload (~{args.small_kb} KB)...")
            small_payload = ProfileGenerator.generate_payload(args.small_kb)
            small_bytes = len(json.dumps(small_payload).encode('utf-8'))
            small_nd = len(small_payload.get('nodedefs', []))
            small_ed = len(small_payload.get('editors', []))
            print(f"   Executing updateJsonProfile for Small Payload ({small_bytes:,} bytes)...")
            small_ok, small_msg, small_el = runner.update_profile(small_payload)
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

            # 2. Large payload (expected to fail)
            print(f"2. Generating Large Payload (~{args.large_kb} KB)...")
            large_payload = ProfileGenerator.generate_payload(args.large_kb)
            large_bytes = len(json.dumps(large_payload).encode('utf-8'))
            large_nd = len(large_payload.get('nodedefs', []))
            large_ed = len(large_payload.get('editors', []))
            print(f"   Executing updateJsonProfile for Large Payload ({large_bytes:,} bytes)...")
            large_ok, large_msg, large_el = runner.update_profile(large_payload)
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

            # Dump payloads if requested
            if args.dump:
                os.makedirs(args.dump_dir, exist_ok=True)
                small_file = os.path.join(args.dump_dir, "profile_test_small.json")
                large_file = os.path.join(args.dump_dir, "profile_test_large.json")
                with open(small_file, 'w', encoding='utf-8') as f:
                    json.dump(small_payload, f, indent=2)
                with open(large_file, 'w', encoding='utf-8') as f:
                    json.dump(large_payload, f, indent=2)
                print(f"\n[INFO] Dumped payloads to:\n  - {small_file} ({small_bytes:,} bytes)\n  - {large_file} ({large_bytes:,} bytes)")

    finally:
        runner.shutdown()

    # Print Report
    report = format_report(results, runner_mode)
    print("\n" + report + "\n")

    # If standard test: exit 0 if small passed and large failed (bug successfully reproduced!)
    if not args.sweep and not args.file and len(results) == 2:
        small_pass = results[0]['success']
        large_fail = not results[1]['success']
        if small_pass and large_fail:
            print("[SUCCESS] Bug reproduction complete: Small payload PASSED and Large payload FAILED as expected.\n")
            return 0
        elif not small_pass:
            print("[WARN] Small payload failed. Check Polyglot connectivity or schema validation.\n")
            return 1
        else:
            print("[INFO] Large payload did not fail. Payload size may be below current broker threshold.\n")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

