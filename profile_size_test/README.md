# Dynamic JSON Profile Size Limit Diagnostic Tool

This standalone project demonstrates and reproduces the payload size limitation bug in **Universal Devices Polyglot (PG3 / PG3x)** and **IoX** when calling `polyglot.updateJsonProfile()`.

---

## The Bug

When a node server / plugin uses modern **Dynamic JSON Profiles** (`updateJsonProfile`):
- **Small payloads** (~10–15 KB) are accepted and processed immediately by Polyglot and IoX.
- **Large payloads** (typically > ~64 KB, and full profiles ~90–100 KB) fail with `RuntimeError: Update profile request failed` or cause MQTT packet rejection / broker buffer drops.

This issue commonly affects node servers with comprehensive profiles (such as YoLink, which supports over 50 device models and dozens of editor definitions).

---

## Features

- **Completely Standalone**: Zero external dependencies needed for CLI simulation mode.
- **Dual Execution Modes**:
  - **Live Mode**: Directly tests against a running Polyglot v3 daemon using `udi_interface`.
  - **Simulation Mode (`--mock`)**: Allows testing and verifying behavior locally on macOS / Linux without Polyglot.
- **Comparative Two-Tier Test**: Runs a small payload (~15 KB, expected to pass) and a large payload (~90 KB, expected to fail).
- **Threshold Sweep (`--sweep`)**: Automatically sweeps payload sizes in increments to find the exact byte cutoff where failures begin.
- **External File Testing (`--file`)**: Can test any arbitrary dynamic profile JSON file.
- **Payload Dumping (`--dump`)**: Exports generated small and large JSON payloads for inspection and sharing with Universal Devices developers.

---

## Usage

### 1. Direct Command-Line Execution (CLI)

Run on your **eisy / Polisy** (or any machine):

```bash
# Standard comparative test (Small 15 KB vs Large 90 KB)
python3 profile_size_test.py

# Sweep mode: pinpoint exact threshold from 30 KB to 100 KB in 10 KB steps
python3 profile_size_test.py --sweep --sweep-start 30 --sweep-end 100 --sweep-step 10

# Test a specific profile JSON dump file
python3 profile_size_test.py --file my_profile.json

# Dump generated test payloads to disk
python3 profile_size_test.py --dump
```

### 2. Simulation / Offline Mode

Test locally on macOS or Linux without a live PG3 daemon:

```bash
python3 profile_size_test.py --mock
python3 profile_size_test.py --mock --sweep
```

### 3. Running as a Standalone NodeServer in PG3

To install this diagnostic tool as its own independent plugin in PG3:
1. In Polyglot PG3 dashboard, add a custom node server slot.
2. Point it to this repository / directory.
3. Start the node server; it will run the diagnostic suite and log results to the PG3 debug log.

---

## Sample Diagnostic Report

```text
================================================================================
        UNIVERSAL DEVICES DYNAMIC JSON PROFILE SIZE REPRODUCTION REPORT
================================================================================
Execution Mode : Simulation / Mock
Timestamp      : 2026-11-12 09:03:08
--------------------------------------------------------------------------------
Test Description          | Size         | Nodes/Eds    | Time     | Status    
--------------------------------------------------------------------------------
Test 1: Small Payload     | 15.1 KB      | 16nd/19ed    | 0.06   s | PASS      
Test 2: Large Payload     | 90.8 KB      | 94nd/96ed    | 0.06   s | FAIL (ERROR)
  └── Detail: RuntimeError: Update profile request failed: payload size (93007 bytes) exceeds broker maximum packet threshold (65536 bytes / 64 KB)
--------------------------------------------------------------------------------
DIAGNOSTIC CONCLUSION:
  [✓] Smallest failure size : 93,007 bytes (90.8 KB)
  [✓] Largest passing size  : 15,492 bytes (15.1 KB)
  [!] Failure boundary is located between 15.1 KB and 90.8 KB.
  [!] Bug confirmed: Dynamic JSON profiles fail when structure exceeds threshold.
================================================================================
```

---

## Running Unit Tests

```bash
python3 test_profile_size.py
```
