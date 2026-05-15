import xml.etree.ElementTree as ET
import re
from collections import defaultdict


def _is_comment_or_blank(line):
    stripped = line.strip()
    return not stripped or stripped.startswith('#')

# Parse nodedefs.xml
nodedef_tree = ET.parse('profile/nodedef/nodedefs.xml')
nodedef_root = nodedef_tree.getroot()

# Parse editors.xml
editor_tree = ET.parse('profile/editor/editors.xml')
editor_root = editor_tree.getroot()

# Parse en_us.txt
with open('profile/nls/en_us.txt', 'r') as f:
    en_us_lines = f.readlines()

# Extract editors defined in editors.xml
defined_editors = set()
for editor in editor_root.findall('.//editor'):
    editor_id = editor.get('id')
    if editor_id:
        defined_editors.add(editor_id)

# Extract NLS keys from editors.xml that reference en_us.txt
editor_nls_refs = defaultdict(set)
for editor in editor_root.findall('.//editor'):
    editor_id = editor.get('id')
    for range_elem in editor.findall('.//range'):
        nls = range_elem.get('nls')
        if nls:
            editor_nls_refs[editor_id].add(nls)

# Extract defined NLS keys from en_us.txt
defined_nls_keys = set()
nls_key_lines = {}
for line_num, line in enumerate(en_us_lines, 1):
    if _is_comment_or_blank(line):
        continue
    # Match keys like: swstate-0=Off, swstate-1=On
    match = re.match(r'^(\w+)-(\d+)=', line)
    if match:
        nls_key = match.group(1)
        defined_nls_keys.add(nls_key)
        if nls_key not in nls_key_lines:
            nls_key_lines[nls_key] = line_num

# Extract ST/ND -NAME entries from en_us.txt for duplicate/conflict checks
st_name_entries = []
nd_name_entries = []
for line_num, line in enumerate(en_us_lines, 1):
    if _is_comment_or_blank(line):
        continue

    st_match = re.match(r'^(ST-([^-]+)-([^-]+)-NAME)=(.*)$', line.rstrip('\n'))
    if st_match:
        st_name_entries.append({
            'line': line_num,
            'key': st_match.group(1),
            'nls': st_match.group(2),
            'var': st_match.group(3),
            'rhs': st_match.group(4),
        })
        continue

    nd_match = re.match(r'^(ND-([^-]+)-NAME)=(.*)$', line.rstrip('\n'))
    if nd_match:
        nd_name_entries.append({
            'line': line_num,
            'key': nd_match.group(1),
            'node': nd_match.group(2),
            'rhs': nd_match.group(3),
        })


def _find_conflicting_key_values(entries):
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry['key']].append(entry)

    conflicts = []
    for key, items in grouped.items():
        rhs_values = sorted({item['rhs'] for item in items})
        if len(rhs_values) > 1:
            lines = ', '.join(str(item['line']) for item in sorted(items, key=lambda x: x['line']))
            conflicts.append((key, rhs_values, lines))
    return sorted(conflicts, key=lambda x: x[0])


def _find_duplicate_st_names_by_nls(entries):
    # Duplicate means exact same text after '=' appears multiple times under same ST nls group.
    grouped = defaultdict(list)
    for entry in entries:
        grouped[(entry['nls'], entry['rhs'])].append(entry)

    duplicates = []
    for (nls, rhs), items in grouped.items():
        if len(items) > 1:
            vars_sorted = sorted({item['var'] for item in items})
            lines = ', '.join(str(item['line']) for item in sorted(items, key=lambda x: x['line']))
            duplicates.append({
                'nls': nls,
                'rhs': rhs,
                'vars': vars_sorted,
                'var_count': len(vars_sorted),
                'lines': lines,
                'items': items,
            })
    return sorted(duplicates, key=lambda x: (x['nls'], x['rhs']))


def _build_nls_var_usage(nodedef_xml_root):
    used_pairs = set()
    for node_def in nodedef_xml_root.findall('.//nodeDef'):
        nls = node_def.get('nls')
        if not nls:
            continue
        for st in node_def.findall('./sts/st'):
            st_id = st.get('id')
            if st_id:
                used_pairs.add((nls, st_id))
    return used_pairs


def _build_nodedef_usage(nodedef_xml_root):
    node_ids = set()
    st_pairs = set()
    cmd_pairs = set()
    cmdp_ids = set()

    for node_def in nodedef_xml_root.findall('.//nodeDef'):
        node_id = node_def.get('id')
        nls = node_def.get('nls')

        if node_id:
            node_ids.add(node_id)
        if not nls:
            continue

        for st in node_def.findall('./sts/st'):
            st_id = st.get('id')
            if st_id:
                st_pairs.add((nls, st_id))

        for group in ('accepts', 'sends'):
            for cmd in node_def.findall(f'./cmds/{group}/cmd'):
                cmd_id = cmd.get('id')
                if cmd_id:
                    cmd_pairs.add((nls, cmd_id))
                for param in cmd.findall('./p'):
                    param_id = param.get('id')
                    if param_id:
                        cmdp_ids.add(param_id)

    return {
        'node_ids': node_ids,
        'st_pairs': st_pairs,
        'cmd_pairs': cmd_pairs,
        'cmdp_ids': cmdp_ids,
    }


def _find_orphan_nls_definitions(en_us_text_lines, nodedef_usage):
    orphans = []

    for line_num, line in enumerate(en_us_text_lines, 1):
        if _is_comment_or_blank(line):
            continue

        s = line.rstrip('\n')

        nd_match = re.match(r'^ND-([^-]+)-(NAME|ICON)=', s)
        if nd_match:
            if nd_match.group(1) not in nodedef_usage['node_ids']:
                orphans.append({'line': line_num, 'type': 'ND', 'entry': s})
            continue

        st_match = re.match(r'^ST-([^-]+)-([^-]+)-NAME=', s)
        if st_match:
            key = (st_match.group(1), st_match.group(2))
            if key not in nodedef_usage['st_pairs']:
                orphans.append({'line': line_num, 'type': 'ST', 'entry': s})
            continue

        cmd_match = re.match(r'^CMD-([^-]+)-([^-]+)-NAME=', s)
        if cmd_match:
            key = (cmd_match.group(1), cmd_match.group(2))
            if key not in nodedef_usage['cmd_pairs']:
                orphans.append({'line': line_num, 'type': 'CMD', 'entry': s})
            continue

        cmdp_match = re.match(r'^CMDP-([^-]+)-NAME=', s)
        if cmdp_match:
            cmdp_id = cmdp_match.group(1)
            if cmdp_id not in nodedef_usage['cmdp_ids']:
                orphans.append({'line': line_num, 'type': 'CMDP', 'entry': s})
            continue

    return orphans

# Extract editors used in nodedefs.xml
used_editors = set()
for st in nodedef_root.findall('.//st'):
    editor = st.get('editor')
    if editor:
        used_editors.add(editor)

for cmd in nodedef_root.findall('.//cmd'):
    editor = cmd.get('editor')
    if editor:
        used_editors.add(editor)

for param in nodedef_root.findall('.//p'):
    editor = param.get('editor')
    if editor:
        used_editors.add(editor)

# Find issues
print("=" * 80)
print("NODEDEFS → EDITORS → EN_US.TXT VALIDATION")
print("=" * 80)

# Issue 1: Editors used in nodedefs but not defined in editors.xml
print("\n1. MISSING EDITOR DEFINITIONS (used in nodedefs.xml but not in editors.xml):")
missing_editors = used_editors - defined_editors
if missing_editors:
    for editor in sorted(missing_editors):
        print(f"  ❌ '{editor}' — add <editor id=\"{editor}\"> to profile/editor/editors.xml")
else:
    print("  ✓ All editors are defined")

# Issue 2: NLS references in editors that don't exist in en_us.txt
print("\n2. MISSING NLS KEY DEFINITIONS (referenced in editors.xml but not in en_us.txt):")
missing_nls = []
for editor_id, nls_keys in editor_nls_refs.items():
    for nls_key in nls_keys:
        if nls_key not in defined_nls_keys:
            missing_nls.append((editor_id, nls_key))
            print(f"  ❌ Editor '{editor_id}' references NLS key '{nls_key}' (not in en_us.txt)")

if not missing_nls:
    print("  ✓ All NLS references are defined")

# Issue 3: Unused editors (defined but never used)
print("\n3. UNUSED EDITORS (defined in editors.xml but not used in nodedefs.xml):")
unused_editors = defined_editors - used_editors
if unused_editors:
    print(f"  Found {len(unused_editors)} unused editors. These should be added back to nodedefs.xml:")
    for editor in sorted(unused_editors):
        nls_refs = editor_nls_refs.get(editor, set())
        nls_info = f" (NLS: {', '.join(sorted(nls_refs))})" if nls_refs else ""
        print(f"  ⚠️  {editor}{nls_info}")
else:
    print("  ✓ All editors are used")

# Issue 4: Conflicting -NAME key definitions in en_us.txt
print("\n4. CONFLICTING -NAME KEY DEFINITIONS (same key, different value text):")
st_conflicts = _find_conflicting_key_values(st_name_entries)
nd_conflicts = _find_conflicting_key_values(nd_name_entries)
if not st_conflicts and not nd_conflicts:
    print("  ✓ No conflicting ST/ND -NAME key definitions")
else:
    for key, rhs_values, lines in st_conflicts:
        print(f"  ❌ ST key '{key}' has multiple values: {' | '.join(rhs_values)} (lines: {lines})")
    for key, rhs_values, lines in nd_conflicts:
        print(f"  ❌ ND key '{key}' has multiple values: {' | '.join(rhs_values)} (lines: {lines})")

# Issue 5: Duplicate ST names under same nls group (exact text after '=')
print("\n5. DUPLICATE ST NAME VALUES WITHIN SAME NLS GROUP (exact text after '='):")
duplicate_st_names = _find_duplicate_st_names_by_nls(st_name_entries)
if not duplicate_st_names:
    print("  ✓ No duplicate ST name values under same nls group")
else:
    print(f"  Found {len(duplicate_st_names)} duplicate ST name groups:")
    for dup in duplicate_st_names:
        duplicate_type = 'different vars' if dup['var_count'] > 1 else 'same var repeated'
        print(
            f"  ⚠️  nls='{dup['nls']}' value='{dup['rhs']}' "
            f"vars={', '.join(dup['vars'])} ({duplicate_type}) lines: {dup['lines']}"
        )

# Issue 6: Orphan duplicate ST entries not referenced by nodedefs.xml
print("\n6. ORPHAN DUPLICATE ST -NAME ENTRIES (duplicate entries not used by nodedefs.xml):")
used_nls_var_pairs = _build_nls_var_usage(nodedef_root)
orphan_duplicate_entries = []
for dup in duplicate_st_names:
    for item in dup['items']:
        if (item['nls'], item['var']) not in used_nls_var_pairs:
            orphan_duplicate_entries.append(item)

if not orphan_duplicate_entries:
    print("  ✓ No orphan duplicate ST entries")
else:
    print(f"  Found {len(orphan_duplicate_entries)} orphan duplicate ST entries:")
    for item in sorted(orphan_duplicate_entries, key=lambda x: x['line']):
        print(
            f"  ⚠️  line {item['line']}: ST-{item['nls']}-{item['var']}-NAME={item['rhs']}"
        )

# Issue 7: Orphan ND/ST/CMD/CMDP definitions not referenced by nodedefs.xml
print("\n7. ORPHAN ND/ST/CMD/CMDP DEFINITIONS (not referenced by nodedefs.xml):")
nodedef_usage = _build_nodedef_usage(nodedef_root)
orphan_nls_entries = _find_orphan_nls_definitions(en_us_lines, nodedef_usage)

if not orphan_nls_entries:
    print("  ✓ No orphan ND/ST/CMD/CMDP definitions")
else:
    print(f"  Found {len(orphan_nls_entries)} orphan ND/ST/CMD/CMDP definitions:")
    for item in sorted(orphan_nls_entries, key=lambda x: (x['type'], x['line'])):
        print(f"  ⚠️  line {item['line']} [{item['type']}]: {item['entry']}")

# Issue 8: Summary stats
print("\n8. STATISTICS:")
print(f"  Total editors defined: {len(defined_editors)}")
print(f"  Total editors used: {len(used_editors)}")
print(f"  Total NLS keys defined: {len(defined_nls_keys)}")
print(f"  Total missing editors: {len(missing_editors)}")
print(f"  Total missing NLS keys: {len(missing_nls)}")
print(f"  Total unused editors: {len(unused_editors)}")
print(f"  Total ST key conflicts: {len(st_conflicts)}")
print(f"  Total ND key conflicts: {len(nd_conflicts)}")
print(f"  Total duplicate ST name groups: {len(duplicate_st_names)}")
print(f"  Total orphan duplicate ST entries: {len(orphan_duplicate_entries)}")
print(f"  Total orphan ND/ST/CMD/CMDP entries: {len(orphan_nls_entries)}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
if missing_editors:
    first_missing = sorted(missing_editors)[0]
    print(f"\n• Add missing editor '{first_missing}' to profile/editor/editors.xml")
if unused_editors:
    print(f"\n• Review unused editors — likely need to be added to nodedefs.xml <st> or <cmd> elements:")
    for editor in sorted(unused_editors):
        print(f"    - {editor}")
if duplicate_st_names:
    print("\n• Review duplicate ST name groups. Some are intentional aliases, but stale duplicates can be removed.")
if orphan_duplicate_entries:
    print("\n• Remove or correct orphan ST duplicate entries that do not map to nodedef <st> ids.")
if orphan_nls_entries:
    print("\n• Remove or migrate orphan ND/ST/CMD/CMDP entries in profile/nls/en_us.txt.")