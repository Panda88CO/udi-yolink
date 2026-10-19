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
_dynamic_nodedefs_cache = None
_dynamic_editors_cache = None

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


def get_dynamic_profile_editors():
    """Generate dynamic JSON editors structure from in-code profile data or profile/editor/editors.xml."""
    global _dynamic_editors_cache
    if _dynamic_editors_cache is not None:
        return _dynamic_editors_cache

    if DYNAMIC_EDITORS is not None:
        _dynamic_editors_cache = DYNAMIC_EDITORS
        return _dynamic_editors_cache

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

    _dynamic_editors_cache = editors
    return _dynamic_editors_cache


def get_dynamic_profile_nodedefs():
    """Generate dynamic JSON nodedefs structure from in-code profile data or profile/nodedef/nodedefs.xml."""
    global _dynamic_nodedefs_cache
    if _dynamic_nodedefs_cache is not None:
        return _dynamic_nodedefs_cache

    if DYNAMIC_NODEDEFS is not None:
        _dynamic_nodedefs_cache = DYNAMIC_NODEDEFS
        return _dynamic_nodedefs_cache

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

    _dynamic_nodedefs_cache = nodedefs
    return _dynamic_nodedefs_cache


def get_dynamic_profile_payload():
    """Return the complete dynamic profile JSON payload matching IoX/PG3 updateJsonProfile schema."""
    return {
        'delete': {
            'editors': ['*'],
            'nodedefs': ['*'],
            'linkdefs': ['*'],
        },
        'editors': get_dynamic_profile_editors(),
        'nodedefs': get_dynamic_profile_nodedefs(),
        'linkdefs': [],
    }


def get_profile_driver_names():
    """
    Extract the mapping of (nodeDefId, driver_id) -> display name.
    1. First tries dynamic JSON profile definitions.
    2. If not available from dynamic profiles, falls back to profile directory (nodedefs.xml + en_us.txt).
    Cached after the first load.
    """
    global _profile_driver_names
    if _profile_driver_names is not None:
        return _profile_driver_names

    _profile_driver_names = {}

    # 1. Take names from dynamic profiles if available
    try:
        for nd in get_dynamic_profile_nodedefs():
            node_id = nd.get('id')
            for prop in nd.get('properties', []):
                driver_id = prop.get('id')
                name = prop.get('name')
                if node_id and driver_id and name:
                    if name == driver_id and driver_id in DRIVER_FALLBACK_LABELS:
                        name = DRIVER_FALLBACK_LABELS[driver_id]
                    _profile_driver_names[(node_id, driver_id)] = name
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
            except Exception as e:
                logging.warning(f'Could not load driver names from static profile: {e}')

    return _profile_driver_names


def apply_profile_driver_names(node, node_id=None):
    """
    Populate or update 'name' in each driver dictionary of a node instance
    using definitions extracted from dynamic or static profiles.
    """
    target_id = node_id or getattr(node, 'id', None)
    if not target_id or not hasattr(node, 'drivers') or not node.drivers:
        return
    # Ensure instance-level drivers list does not mutate class attribute across instances
    node.drivers = [dict(d) for d in node.drivers]
    names = get_profile_driver_names()
    for d in node.drivers:
        driver_id = d.get('driver')
        if not driver_id:
            continue
        if (target_id, driver_id) in names:
            d['name'] = names[(target_id, driver_id)]
        elif driver_id in DRIVER_FALLBACK_LABELS and 'name' not in d:
            d['name'] = DRIVER_FALLBACK_LABELS[driver_id]


def update_dynamic_profile(controller):
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
            payload = get_dynamic_profile_payload()
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
