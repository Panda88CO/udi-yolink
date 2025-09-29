## Quick context for AI coding agents

This repo implements a Polyglot/ISY node server for YoLink devices (YoSmart API v2). The codebase is Python 3.x and structured as a small device-oriented node server that speaks to YoLink over REST/MQTT and exposes device state through Polyglot drivers/nodes.

Keep the changes tightly focused: edits usually affect the MQTT/auth flow (yoLink_init_V4.py), the device MQTT handling (yolink_mqtt_classV3.py) or the per-device node modules `udiYo*.py`.

Key files to read first
- `udi-YoLink.py` - server entry / node orchestration (Polyglot hooks, param handling, node creation).
- `yoLink_init_V4.py` - YoLinkInitPAC: core auth, MQTT client, queues, token refresh, cloud vs local modes.
- `yolink_mqtt_classV3.py` - per-device MQTT message handling, helper methods and device API request patterns.
- `udiYolinkLib.py` - common helpers used by nodes (driver helpers, persistence, time and unit conversions).
- `udiYo*.py` - per-device node implementations (many files, one per supported device).
- `requirements.txt` - external dependencies used for local development.

Big-picture architecture (short)
- One central access object: YoLinkInitPAC (in `yoLink_init_V4.py`) manages tokens, an MQTT client and several queues (publishQueue, retryQueue, messageQueue).
- Device-specific wrappers (instances of classes from `yolink_mqtt_classV3.py` and `udiYo*.py`) subscribe via yoAccess to device MQTT topics and expose Polyglot nodes/drivers.
- The main Polyglot node server (`udi-YoLink.py`) creates device nodes by iterating the list returned from YoLink API and choosing the appropriate `udiYo*` class by `type` and sometimes by `modelName`.

Important dataflows and message formats
- Authentication: YoLinkInitPAC.refresh_token() talks to TOKEN_URL (default `https://api.yosmart.com/open/yolink/token`) and stores a token with `expirationTime`.
- MQTT topics: cloud mode uses topic prefix `yl-home/` and local mode uses `ylsubnet/` (see `yoLink_init_V4.py`).
- Device control payloads use a `method` field and targetDevice/token, for example (constructed in `yolink_mqtt_classV3.py`):

  {"method": "Switch.setState", "targetDevice": "<deviceId>", "token": "<device-token>", ...}

API / rate-limit conventions
- YoLinkInitPAC enforces a local rate-tracking structure: `MAX_MESSAGES`, `MAX_TIME` and `time_tracking_dict` to avoid overrunning the YoLink cloud.
- The node server exposes configurable parameters (via Polyglot Custom params) that affect limits: `CALLS_PER_MIN`, `DEV_CALLS_PER_MIN`.

Project-specific conventions and gotchas
- Node address naming: nodes use the last 14 characters of `deviceId` as the address (see `udi-YoLink.py` addNodes logic).
- Persistent command state: per-node small JSON files (named `<address>.json`) are used to store command state/structs (see `udiYolinkLib.py` save/retrieve helpers).
- Temperature units: `TEMP_UNIT` maps to integers (0=C, 1=F, 2=K); conversions are handled in `udiYolinkLib.py` and `udi-YoLink.py`.
- Many device/node files rely on Polyglot's `udi_interface`; when developing locally there is fallback logging if `udi_interface` isn't installed — tests run without Polyglot will still exercise most code paths but some functionality expects the Polyglot runtime.
- Local vs cloud mode: if `home_id` is provided for YoLinkInitPAC it uses local mode and different MQTT/topic behavior; local token endpoints use port `:1080` in this codebase.

Development / run workflows (discoverable from repo)
- Install a Python venv and dependencies listed in `requirements.txt`.
  - Example (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- To run the node server locally for debugging you can run the main script directly (no Polyglot daemon required for simple runs):

```powershell
python udi-YoLink.py
```

  Expect missing Polyglot behavior unless `udi_interface` is available; logs will fall back to standard logging.

Where to change behavior (common edit points)
- Auth / token logic: `yoLink_init_V4.py` — refresh_token(), request_new_token(), local_refresh_token(). Any token lifetime or margin changes belong here.
- MQTT handling / subscribe topics: `yoLink_init_V4.py` (client setup, on_connect, subscribe) and per-device `yolink_mqtt_classV3.py` (subscribe_mqtt callbacks and data parsing).
- Device mapping and node creation rules: `udi-YoLink.py` addNodes() — add or change how certain models map to specialized node classes.
- Driver and UI behavior: `udiYolinkLib.py` my_setDriver, driver UOM usage and conversions.

Examples to copy when making edits
- Creating a device control payload (from `yolink_mqtt_classV3.py`):

  data = {"method": "<Type>.setState", "targetDevice": deviceId, "token": deviceToken, ...}

- Adding a new device node: follow `addNodes()` in `udi-YoLink.py` — pick a unique address via `poly.getValidAddress(nodename)` using the `deviceId[-14:]` pattern and add `self.Parameters[address] = dev['name']`.

Files and constants to reference in PRs
- `requirements.txt` — dependency list
- `loginInfoExample.json` — shows where credentials are expected for quick testing
- `README.md` — high-level user-facing installation notes; keep user instructions in sync with behavior in `yoLink_init_V4.py`.

Checklist for PRs touching runtime behavior
- Update `README.md` if user-visible config steps change (e.g., new Custom param names).
- Run a quick smoke run locally (activate venv, pip install -r requirements.txt, run `python udi-YoLink.py`) and copy relevant logs into PR if behavior changes.
- Preserve existing parameter names: `UAID`, `SECRET_KEY`, `MQTT_URL`, `MQTT_PORT`, `TOKEN_URL`, `TEMP_UNIT`, `NBR_TTS`, `CALLS_PER_MIN` unless intentionally renaming — document in the PR.

If anything above is unclear or you want me to expand (for example, add example unit tests, or wire a local integration test that exercises token refresh + a fake MQTT broker), tell me which area to expand and I'll iterate.
