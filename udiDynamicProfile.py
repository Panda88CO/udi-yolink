#!/usr/bin/env python3
"""
Dynamic profile generation and driver name resolution for udi-yolink.
Supports PG3/PG3x dynamic JSON profiles (updateJsonProfile) and static profile fallbacks.
"""
import os
import re
import json
import xml.etree.ElementTree as ET

try:
    import udi_interface
    logging = udi_interface.LOGGER
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

try:
    from dynamic_profile_data import DYNAMIC_EDITORS, DYNAMIC_NODEDEFS
except ImportError:
    DYNAMIC_EDITORS = None
    DYNAMIC_NODEDEFS = None

_profile_driver_names = None
_raw_nodedefs_cache = None
_raw_editors_cache = None
_dynamic_editors_cache = {}

# Known fallback labels for driver IDs not explicitly declared in primary nodeDef
DRIVER_FALLBACK_LABELS = {
    'GV21': 'On Sec',
    'GV22': 'Off Sec',
    'GV23': 'Total Schedules',
    'GV16': 'On Minute',
    'CLIHUM': 'Humidity',
    'GV4': 'Energy',
    'BATLVL': 'Battery Level',
    'GV2': 'High Temp Alarm',
    'GV11': 'High Temp Alarm Limit',
    'GV13': 'High Humidity Alarm Limit',
}

# Mapping of unit-specific variant nodeDef IDs to unified base nodeDef IDs
VARIANT_TO_BASE_NODEDEF = {
    'yoCOSmokesensF': 'yoCOSmokesens',
    'yoleaksensF': 'yoleaksens',
    'yomotionsensF': 'yomotionsens',
    'yosmremoteF': 'yosmremote',
    'yosoilsensorF': 'yosoilsensor',
    'yothsensF': 'yothsens',
    'yotsensF': 'yotsens',
    'yothermpropf': 'yothermprop',
    'yothermostatf': 'yothermostat',
    'yovibrasensF': 'yovibrasens',
    'yowatermeterCtrlF': 'yowatermeterCtrl',
    'yowatermeterMultiF': 'yowatermeterMulti',
    'yowatermeterOnlyF': 'yowatermeterOnly',
    'yowatermeterSubL': 'yowatermeterSub',
    'yowatermeterSubG': 'yowatermeterSub',
}


def normalize_temp_unit(unit):
    """Normalize temperature unit to 0 (Celsius) or 1 (Fahrenheit)."""
    if unit is None:
        return 0
    if isinstance(unit, str):
        u = unit.strip().upper()
        if u.startswith('F'):
            return 1
        if u.startswith('C'):
            return 0
        try:
            return 1 if int(u) == 1 else 0
        except (ValueError, TypeError):
            return 0
    try:
        return 1 if int(unit) == 1 else 0
    except (ValueError, TypeError):
        return 0


def normalize_water_unit(unit):
    """Normalize water unit to 0 (Gallon), 1 (CCF), 2 (m^3), or 3 (Liter)."""
    if unit is None:
        return 0
    if isinstance(unit, str):
        u = unit.strip().upper()
        if u.startswith('G'):
            return 0
        if u.startswith('C'):
            return 1
        if u.startswith('M'):
            return 2
        if u.startswith('L'):
            return 3
        try:
            val = int(u)
            return val if val in (0, 1, 2, 3) else 0
        except (ValueError, TypeError):
            return 0
    try:
        val = int(unit)
        return val if val in (0, 1, 2, 3) else 0
    except (ValueError, TypeError):
        return 0


def _parse_nls_file(nls_path):
    node_names = {}
    node_icons = {}
    cmd_names = {}
    st_names = {}
    nls_map = {}

    if not os.path.exists(nls_path):
        return node_names, node_icons, cmd_names, st_names, nls_map

    with open(nls_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k, v = k.strip(), v.strip()

            m_nd = re.match(r'^ND-([\w\-]+)-NAME$', k)
            if m_nd:
                node_names[m_nd.group(1)] = v
                continue
            m_icon = re.match(r'^ND-([\w\-]+)-ICON$', k)
            if m_icon:
                node_icons[m_icon.group(1)] = v
                continue
            m_st = re.match(r'^ST-([\w\-]+)-([\w\-]+)-NAME$', k)
            if m_st:
                st_names[(m_st.group(1), m_st.group(2))] = v
                continue
            m_cmd = re.match(r'^CMD-([\w\-]+)-([\w\-]+)-NAME$', k)
            if m_cmd:
                cmd_names[(m_cmd.group(1), m_cmd.group(2))] = v
                continue
            m_enum = re.match(r'^([\w\-]+)-([\w\-]+)$', k)
            if m_enum:
                nls_map.setdefault(m_enum.group(1), {})[m_enum.group(2)] = v

    return node_names, node_icons, cmd_names, st_names, nls_map


def _get_raw_profile_editors():
    """Extract raw editor definitions from in-code profile data or profile/editor/editors.xml."""
    global _raw_editors_cache
    if _raw_editors_cache is not None:
        return _raw_editors_cache

    if DYNAMIC_EDITORS is not None:
        _raw_editors_cache = DYNAMIC_EDITORS
        return _raw_editors_cache

    base_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(base_dir, 'profile', 'editor', 'editors.xml')
    nls_path = os.path.join(base_dir, 'profile', 'nls', 'en_us.txt')

    editors = []
    if os.path.exists(xml_path) and os.path.exists(nls_path):
        try:
            _, _, _, _, nls_map = _parse_nls_file(nls_path)
            tree = ET.parse(xml_path)
            for ed in tree.getroot().findall('.//editor'):
                eid = ed.get('id')
                if not eid:
                    continue
                ranges = []
                for r in ed.findall('.//range'):
                    r_dict = {'uom': r.get('uom', '25')}
                    if r.get('min') is not None:
                        r_dict['min'] = r.get('min')
                    if r.get('max') is not None:
                        r_dict['max'] = r.get('max')
                    if r.get('prec') is not None:
                        r_dict['prec'] = r.get('prec')
                    subset = r.get('subset')
                    if subset:
                        r_dict['subset'] = subset
                    nls_key = r.get('nls')
                    if nls_key and nls_key in nls_map:
                        r_dict['names'] = dict(nls_map[nls_key])
                    ranges.append(r_dict)
                editors.append({'id': eid, 'ranges': ranges})
        except Exception as e:
            logging.warning(f'Could not generate dynamic editors from XML: {e}')

    _raw_editors_cache = editors
    return _raw_editors_cache


def _get_raw_profile_nodedefs():
    """Extract raw nodedef definitions from in-code profile data or profile/nodedef/nodedefs.xml."""
    global _raw_nodedefs_cache
    if _raw_nodedefs_cache is not None:
        return _raw_nodedefs_cache

    if DYNAMIC_NODEDEFS is not None:
        _raw_nodedefs_cache = DYNAMIC_NODEDEFS
        return _raw_nodedefs_cache

    base_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(base_dir, 'profile', 'nodedef', 'nodedefs.xml')
    nls_path = os.path.join(base_dir, 'profile', 'nls', 'en_us.txt')

    nodedefs = []
    if os.path.exists(xml_path) and os.path.exists(nls_path):
        try:
            node_names, node_icons, cmd_names, st_names, _ = _parse_nls_file(nls_path)
            tree = ET.parse(xml_path)
            for nd in tree.getroot().findall('.//nodeDef'):
                nid = nd.get('id')
                nls = nd.get('nls')
                if not nid or not nls:
                    continue
                name = node_names.get(nid, nid)
                icon = node_icons.get(nid, 'GenericCtl')

                properties = []
                for st in nd.findall('.//st'):
                    did = st.get('id')
                    ed = st.get('editor', '')
                    dname = st_names.get((nls, did)) or DRIVER_FALLBACK_LABELS.get(did, did)
                    properties.append({'id': did, 'editor': ed, 'name': dname})

                sends = []
                sends_elem = nd.find('.//sends')
                if sends_elem is not None:
                    for cmd in sends_elem.findall('.//cmd'):
                        cid = cmd.get('id')
                        cname = cmd_names.get((nls, cid), cid)
                        sends.append({'id': cid, 'name': cname})

                accepts = []
                accepts_elem = nd.find('.//accepts')
                if accepts_elem is not None:
                    for cmd in accepts_elem.findall('.//cmd'):
                        cid = cmd.get('id')
                        cname = cmd_names.get((nls, cid), cid)
                        cmd_dict = {'id': cid, 'name': cname}
                        params = []
                        for p in cmd.findall('.//p'):
                            pid = p.get('id', '')
                            ped = p.get('editor', '')
                            pinit = p.get('init', '')
                            p_dict = {'id': pid, 'editor': ped}
                            if pinit:
                                p_dict['init'] = pinit
                            params.append(p_dict)
                        if params:
                            cmd_dict['parameters'] = params
                        accepts.append(cmd_dict)

                nodedefs.append({
                    'id': nid,
                    'name': name,
                    'icon': icon,
                    'properties': properties,
                    'cmds': {'sends': sends, 'accepts': accepts},
                    'links': {'ctl': [], 'rsp': []}
                })
        except Exception as e:
            logging.warning(f'Could not generate dynamic nodedefs from XML: {e}')

    _raw_nodedefs_cache = nodedefs
    return _raw_nodedefs_cache


def _build_dynamic_unit_editors(temp_norm, water_norm):
    """
    Build parameterized editor definitions for temperature and water units.
    """
    unit_editors = {}

    # Temperature editors: 0 = Celsius (uom 4), 1 = Fahrenheit (uom 17)
    wl_names = {
        '98': 'Updating (may take up to 1 hour)',
        '99': 'Unknown'
    }
    if temp_norm == 1:
        temp_uom = '17'
        temp_min = '-40'
        temp_max = '221'
        temp_prec = '1'
        set_min = '40'
        set_max = '100'
        eco_max = '9'
    else:
        temp_uom = '4'
        temp_min = '-40'
        temp_max = '105'
        temp_prec = '1'
        set_min = '5'
        set_max = '38'
        eco_max = '5'

    temp_ranges = [
        {'uom': temp_uom, 'min': temp_min, 'max': temp_max, 'prec': temp_prec},
        {'uom': '25', 'subset': '98,99', 'names': dict(wl_names)}
    ]
    temp_set_ranges = [
        {'uom': temp_uom, 'min': set_min, 'max': set_max, 'prec': '0'}
    ]
    eco_set_ranges = [
        {'uom': temp_uom, 'min': '0', 'max': eco_max, 'prec': '1'}
    ]

    unit_editors['celsius'] = temp_ranges
    unit_editors['farenheit'] = temp_ranges
    unit_editors['celsiusSet'] = temp_set_ranges
    unit_editors['farenheitSet'] = temp_set_ranges
    unit_editors['ecoSet'] = eco_set_ranges
    unit_editors['ecoSetF'] = eco_set_ranges

    # Water volume editors: 0 = Gallon (69), 1 = CCF (6), 2 = m^3 (8), 3 = Liter (35)
    err_names = {
        '0': 'Unknown',
        '99': 'Unknown/Not reported'
    }
    if water_norm == 3:  # Liter
        w_uom = '35'
        w_max = '100000'
        w_prec = '1'
    elif water_norm == 1:  # CCF
        w_uom = '6'
        w_max = '10000'
        w_prec = '1'
    elif water_norm == 2:  # m3
        w_uom = '8'
        w_max = '10000'
        w_prec = '2'
    else:  # Gallon (0)
        w_uom = '69'
        w_max = '10000'
        w_prec = '1'

    water_ranges = [
        {'uom': w_uom, 'min': '0', 'max': w_max, 'prec': w_prec},
        {'uom': '25', 'subset': '0,99', 'names': dict(err_names)}
    ]
    water_set_ranges = [
        {'uom': w_uom, 'min': '0', 'max': w_max, 'prec': w_prec}
    ]

    unit_editors['liter'] = water_ranges
    unit_editors['gallon'] = water_ranges
    unit_editors['literSet'] = water_set_ranges
    unit_editors['gallonSet'] = water_set_ranges

    return unit_editors


def get_dynamic_profile_editors(temp_unit=None, water_unit=None):
    """Generate dynamic JSON editors structure parameterized by temp_unit and water_unit."""
    temp_norm = normalize_temp_unit(temp_unit)
    water_norm = normalize_water_unit(water_unit)
    cache_key = (temp_norm, water_norm)

    global _dynamic_editors_cache
    if _dynamic_editors_cache is not None and cache_key in _dynamic_editors_cache:
        return _dynamic_editors_cache[cache_key]

    base_editors = _get_raw_profile_editors()
    unit_map = _build_dynamic_unit_editors(temp_norm, water_norm)

    result_editors = []
    seen = set()
    for ed in base_editors:
        eid = ed.get('id')
        if eid in unit_map:
            result_editors.append({'id': eid, 'ranges': unit_map[eid]})
            seen.add(eid)
        else:
            result_editors.append(dict(ed))
            seen.add(eid)

    for eid, ranges in unit_map.items():
        if eid not in seen:
            result_editors.append({'id': eid, 'ranges': ranges})

    if _dynamic_editors_cache is None:
        _dynamic_editors_cache = {}
    _dynamic_editors_cache[cache_key] = result_editors
    return result_editors


def get_dynamic_profile_nodedefs(include_variants=False):
    """
    Generate dynamic JSON nodedefs structure.
    If include_variants is False (default), duplicate ...F and ...G/L nodeDefs are omitted,
    reducing the total nodeDef count.
    """
    raw_nodedefs = _get_raw_profile_nodedefs()
    if include_variants:
        return [dict(nd) for nd in raw_nodedefs]

    return [
        dict(nd) for nd in raw_nodedefs
        if nd.get('id') not in VARIANT_TO_BASE_NODEDEF
    ]


def get_dynamic_profile_payload(controller=None, temp_unit=None, water_unit=None, include_variants=False):
    """Return the complete dynamic profile JSON payload matching IoX/PG3 updateJsonProfile schema."""
    if temp_unit is None and controller is not None:
        temp_unit = getattr(controller, 'temp_unit', None)
        if temp_unit is None and hasattr(controller, 'yoAccess') and hasattr(controller.yoAccess, 'get_temp_unit'):
            try:
                temp_unit = controller.yoAccess.get_temp_unit()
            except Exception:
                temp_unit = None
    if water_unit is None and controller is not None:
        water_unit = getattr(controller, 'water_unit', None)
        if water_unit is None and hasattr(controller, 'yoAccess') and hasattr(controller.yoAccess, 'get_water_unit'):
            try:
                water_unit = controller.yoAccess.get_water_unit()
            except Exception:
                water_unit = None

    return {
        'delete': {
            'editors': ['*'],
            'nodedefs': ['*'],
            'linkdefs': ['*'],
        },
        'editors': get_dynamic_profile_editors(temp_unit=temp_unit, water_unit=water_unit),
        'nodedefs': get_dynamic_profile_nodedefs(include_variants=include_variants),
        'linkdefs': [],
    }


def get_profile_driver_names():
    """
    Extract the mapping of (nodeDefId, driver_id) -> display name.
    1. First tries dynamic JSON profile definitions (including all variants and aliases).
    2. If not available from dynamic profiles, falls back to profile directory (nodedefs.xml + en_us.txt).
    Cached after the first load.
    """
    global _profile_driver_names
    if _profile_driver_names is not None:
        return _profile_driver_names

    _profile_driver_names = {}

    # 1. Take names from dynamic profiles if available
    try:
        for nd in get_dynamic_profile_nodedefs(include_variants=True):
            node_id = nd.get('id')
            for prop in nd.get('properties', []):
                driver_id = prop.get('id')
                name = prop.get('name')
                if node_id and driver_id and name:
                    if name == driver_id and driver_id in DRIVER_FALLBACK_LABELS:
                        name = DRIVER_FALLBACK_LABELS[driver_id]
                    _profile_driver_names[(node_id, driver_id)] = name

        # Also map variant aliases from base definitions if missing
        for var_id, base_id in VARIANT_TO_BASE_NODEDEF.items():
            for (nid, did), name in list(_profile_driver_names.items()):
                if nid == base_id and (var_id, did) not in _profile_driver_names:
                    _profile_driver_names[(var_id, did)] = name
    except Exception as e:
        logging.warning(f'Could not load driver names from dynamic profile: {e}')

    # 2. If not available from dynamic profiles, fall back to profile directory
    if not _profile_driver_names:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        xml_path = os.path.join(base_dir, 'profile', 'nodedef', 'nodedefs.xml')
        nls_path = os.path.join(base_dir, 'profile', 'nls', 'en_us.txt')
        if os.path.exists(xml_path) and os.path.exists(nls_path):
            try:
                _, _, _, st_names, _ = _parse_nls_file(nls_path)
                tree = ET.parse(xml_path)
                for node_def in tree.getroot().findall('.//nodeDef'):
                    node_id = node_def.get('id')
                    nls = node_def.get('nls')
                    if not node_id or not nls:
                        continue
                    for st in node_def.findall('.//st'):
                        driver_id = st.get('id')
                        if driver_id and (nls, driver_id) in st_names:
                            _profile_driver_names[(node_id, driver_id)] = st_names[(nls, driver_id)]

                for var_id, base_id in VARIANT_TO_BASE_NODEDEF.items():
                    for (nid, did), name in list(_profile_driver_names.items()):
                        if nid == base_id and (var_id, did) not in _profile_driver_names:
                            _profile_driver_names[(var_id, did)] = name
            except Exception as e:
                logging.warning(f'Could not load driver names from static profile: {e}')

    return _profile_driver_names


def apply_profile_driver_names(node, node_id=None):
    """
    Populate or update 'name' and dynamic 'uom' in each driver dictionary of a node instance
    using definitions extracted from dynamic or static profiles and active unit preferences.
    """
    target_id = node_id or getattr(node, 'id', None)
    if not target_id or not hasattr(node, 'drivers') or not node.drivers:
        return
    # Ensure instance-level drivers list does not mutate class attribute across instances
    node.drivers = [dict(d) for d in node.drivers]
    names = get_profile_driver_names()

    temp_unit = getattr(node, 'temp_unit', None)
    if temp_unit is None and hasattr(node, 'yoAccess') and hasattr(node.yoAccess, 'get_temp_unit'):
        try:
            temp_unit = node.yoAccess.get_temp_unit()
        except Exception:
            temp_unit = None

    water_unit = getattr(node, 'water_unit', None)
    if water_unit is None and hasattr(node, 'yoAccess') and hasattr(node.yoAccess, 'get_water_unit'):
        try:
            water_unit = node.yoAccess.get_water_unit()
        except Exception:
            water_unit = None

    temp_norm = normalize_temp_unit(temp_unit) if temp_unit is not None else None
    water_norm = normalize_water_unit(water_unit) if water_unit is not None else None

    for d in node.drivers:
        driver_id = d.get('driver')
        if not driver_id:
            continue
        if (target_id, driver_id) in names:
            d['name'] = names[(target_id, driver_id)]
        elif target_id in VARIANT_TO_BASE_NODEDEF and (VARIANT_TO_BASE_NODEDEF[target_id], driver_id) in names:
            d['name'] = names[(VARIANT_TO_BASE_NODEDEF[target_id], driver_id)]
        elif driver_id in DRIVER_FALLBACK_LABELS and 'name' not in d:
            d['name'] = DRIVER_FALLBACK_LABELS[driver_id]

        # Dynamically adjust UOM for temperature
        if temp_norm is not None:
            if temp_norm == 1 and d.get('uom') == 4:
                d['uom'] = 17
            elif temp_norm == 0 and d.get('uom') == 17:
                d['uom'] = 4

        # Dynamically adjust UOM for water volume
        if water_norm is not None:
            if d.get('uom') in (69, 35, 6, 8):
                target_uom = {0: 69, 1: 6, 2: 8, 3: 35}.get(water_norm)
                if target_uom is not None:
                    d['uom'] = target_uom


def update_dynamic_profile(controller, include_variants=False):
    """
    Push dynamic JSON profile to IoX/PG3 via updateJsonProfile once nodes are done initializing.
    Falls back to static updateProfile if updateJsonProfile is unavailable or fails.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(base_dir, 'profile')

    if os.path.isdir(profile_dir):
        logging.info("Updating profile (dynamic & static)...")
    else:
        logging.info("Updating profile (dynamic)...")

    json_ok = False
    updater = getattr(controller.poly, "updateJsonProfile", None)
    if callable(updater):
        try:
            payload = get_dynamic_profile_payload(controller=controller, include_variants=include_variants)
            updater(payload, {"waitResponse": True})
            logging.info("Dynamic JSON profile updated successfully via updateJsonProfile")
            json_ok = True
        except Exception as e:
            logging.warning(f"updateJsonProfile failed: {e}; falling back to updateProfile")

    # Only update static profile if the directory exists
    if os.path.isdir(profile_dir):
        try:
            if hasattr(controller.poly, "updateProfile"):
                controller.poly.updateProfile()
                logging.info("Static profile updated successfully via updateProfile")
        except Exception as e:
            if not json_ok:
                logging.error(f"updateProfile failed: {e}")

    if hasattr(controller, 'remove_notice'):
        controller.remove_notice("profile")
    elif hasattr(controller.poly, 'Notices') and 'profile' in controller.poly.Notices:
        try:
            controller.poly.Notices.delete('profile')
        except Exception:
            pass
