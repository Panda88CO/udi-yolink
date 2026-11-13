# Dynamic JSON Profile Size Limit Diagnostic Tool

A standalone diagnostic tool for **Universal Devices Polyglot (PG3 / PG3x)** and **IoX** to demonstrate, reproduce, and pinpoint the dynamic JSON profile payload size bug in `polyglot.updateJsonProfile()`.

> **Note**: This tool runs **strictly on PG3x hardware** (eisy or Polisy) using authentic `udi_interface` connected to the local Polyglot MQTT broker. There is **no mock or simulation mode**.

---

## The Bug

When a node server / plugin uses modern **Dynamic JSON Profiles** (`updateJsonProfile`):
- **Small payloads** (~10–15 KB) are accepted and processed immediately by Polyglot and IoX.
- **Large payloads** (typically > ~64 KB, and full profiles ~90–100 KB) fail with `RuntimeError: Update profile request failed` or cause MQTT packet rejection / broker buffer drops.

This issue commonly affects node servers with comprehensive profiles (such as YoLink, which supports over 50 device models and dozens of editor definitions).

---

## How It Connects to Polyglot & MQTT

In Polyglot v3 (PG3x), node servers communicate with PG3 and IoX over a local TLS MQTT broker (`localhost:8883`).

When PG3 starts a node server, it provides an environment variable named **`PG3INIT`** (a base64-encoded JSON payload containing `uuid`, `profileNum`, `token`, `mqttHost`, `mqttPort`, and `isPG3x`). 

When `udi_interface.Interface([])` is instantiated, it parses `PG3INIT` to authenticate and establish the TLS MQTT session. Without `PG3INIT`, the interface cannot connect to the broker.

---

## How to Run on PG3x Hardware (eisy / Polisy)

### Method 1: Install as a Custom Node Server in PG3x (Recommended)

This is the most authentic and direct way to test:
1. In the **PG3x Web Dashboard**, navigate to **Node Server Store** -> **Add Custom Node Server** (or install from local directory `/var/polyglot/nodes/ProfileSizeTest` or GitHub URL on branch `profile-size-test`).
2. PG3x will assign a slot, launch `profile_size_test.py` with authentic `PG3INIT`, and connect to the live Mosquitto MQTT broker over TLS.
3. On startup, it automatically executes the sweep using the default parameters and writes the complete ASCII report directly into the **PG3 Node Server Log** (`Log` -> `Real Time Log` or `Download Log`).
4. **Configuring Sweep Parameters in PG3x:**
   - In the PG3x Web Dashboard, navigate to **Node Servers** -> **ProfileSizeTest** -> **Configuration**.
   - Under **Custom Configuration Parameters**, adjust any parameter:
     - `mode`: `sweep` (or `test` for small vs large)
     - `sweep_start`: `20` (starting KB)
     - `sweep_end`: `100` (ending KB)
     - `sweep_step`: `10` (increment KB)
     - `small_kb`: `15`
     - `large_kb`: `90`
   - Click **Save Changes** — the node server automatically receives the update, executes the new sweep immediately, and logs the report.
5. **IoX Node & Drivers:**
   The controller node in IoX reports:
   - `ST`: Status (1 = Ready)
   - `GV1`: Result Status (1 = All Passed, 2 = Bug Confirmed, 3 = All Failed)
   - `GV2`: Smallest Failure Size (KB)
   - `GV3`: Largest Passing Size (KB)

### Method 2: Command-Line via SSH (Passing `PG3INIT`)

If you want to run the tool interactively from an SSH terminal on your eisy:

1. SSH into your eisy:
   ```bash
   ssh admin@eisy.local
   ```
2. Navigate to the tool directory:
   ```bash
   cd /var/polyglot/nodes/ProfileSizeTest
   ```
3. Export `PG3INIT` from an active node server process (such as YoLink or any running slot):
   ```bash
   export PG3INIT=$(tr '\0' '\n' < /proc/$(pgrep -f "udi_interface|polyglot" | head -n 1)/environ | grep '^PG3INIT=' | cut -d= -f2-)
   ```
4. Run the diagnostic tool:
   ```bash
   # Standard comparative test (Small 15 KB vs Large 90 KB)
   python3 profile_size_test.py
   ```

---

## CLI Options

| Flag | Default | Description |
|---|---|---|
| `--small-kb` | `15` | Target size in KB for small (passing) payload |
| `--large-kb` | `90` | Target size in KB for large (failing) payload |
| `--sweep` | `False` | Run incremental size sweep to find exact failure byte cutoff |
| `--sweep-start` | `20` | Sweep start size in KB |
| `--sweep-end` | `100` | Sweep end size in KB |
| `--sweep-step` | `10` | Sweep step size in KB |
| `--file <path>` | `None` | Test a specific profile JSON file directly |
| `--dump` | `False` | Dump generated test payloads to disk for inspection |
| `--daemon` | `False` | Keep node server running after test (`polyglot.runForever()`) |

### Example CLI Commands

```bash
# Pinpoint the exact failure boundary from 30 KB to 100 KB in 10 KB steps
python3 profile_size_test.py --sweep --sweep-start 30 --sweep-end 100 --sweep-step 10

# Test an exported production profile JSON file
python3 profile_size_test.py --file my_yolink_profile.json

# Dump the generated payloads to disk
python3 profile_size_test.py --dump
```

---

## Sample Diagnostic Report

```text
================================================================================
        UNIVERSAL DEVICES DYNAMIC JSON PROFILE SIZE REPRODUCTION REPORT
================================================================================
Execution Mode : Live PG3x Hardware (udi_interface / TLS MQTT)
Timestamp      : 2026-11-13 10:15:30
--------------------------------------------------------------------------------
Test Description          | Size         | Nodes/Eds    | Time     | Status    
--------------------------------------------------------------------------------
Test 1: Small Payload     | 15.1 KB      | 16nd/19ed    | 0.32s    | PASS      
Test 2: Large Payload     | 90.8 KB      | 94nd/96ed    | 0.08s    | FAIL (ERROR)
  └── Detail: MQTT/Polyglot Rejection: RuntimeError: Update profile request failed
--------------------------------------------------------------------------------
DIAGNOSTIC CONCLUSION:
  [✓] Smallest failure size : 93,007 bytes (90.8 KB)
  [✓] Largest passing size  : 15,492 bytes (15.1 KB)
  [!] Failure boundary is located between 15.1 KB and 90.8 KB.
  [!] Bug confirmed: Dynamic JSON profiles fail when structure exceeds threshold.
================================================================================
```

---

## Running Automated Tests

```bash
python3 test_profile_size.py
```
