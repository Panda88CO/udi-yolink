import xml.etree.ElementTree as ET
import re
from collections import defaultdict

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
    # Match keys like: swstate-0=Off, swstate-1=On
    match = re.match(r'^(\w+)-(\d+)=', line)
    if match:
        nls_key = match.group(1)
        defined_nls_keys.add(nls_key)
        if nls_key not in nls_key_lines:
            nls_key_lines[nls_key] = line_num

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

# Issue 4: Summary stats
print("\n4. STATISTICS:")
print(f"  Total editors defined: {len(defined_editors)}")
print(f"  Total editors used: {len(used_editors)}")
print(f"  Total NLS keys defined: {len(defined_nls_keys)}")
print(f"  Total missing editors: {len(missing_editors)}")
print(f"  Total missing NLS keys: {len(missing_nls)}")
print(f"  Total unused editors: {len(unused_editors)}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
if missing_editors:
    print(f"\n• Add missing editor '{missing_editors.pop()}' to profile/editor/editors.xml")
if unused_editors:
    print(f"\n• Review unused editors — likely need to be added to nodedefs.xml <st> or <cmd> elements:")
    for editor in sorted(unused_editors):
        print(f"    - {editor}")