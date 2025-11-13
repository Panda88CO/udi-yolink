import xml.etree.ElementTree as ET
import re
from collections import defaultdict

# Parse nodedefs.xml
tree = ET.parse('profile/nodedef/nodedefs.xml')
root = tree.getroot()

# Extract all state definitions from nodedefs.xml
expected_states = defaultdict(set)
nodedef_map = {}

for nodedef in root.findall('.//nodeDef'):
    node_id = nodedef.get('id')
    nls = nodedef.get('nls')
    if nls:
        nodedef_map.setdefault(nls, []).append(node_id)
        for st in nodedef.findall('.//st'):
            st_id = st.get('id')
            if st_id:
                expected_states[nls].add(st_id)

# Parse en_us.txt
with open('profile/nls/en_us.txt', 'r') as f:
    lines = f.readlines()

# Extract all defined entries and track duplicates
defined_entries = defaultdict(set)
duplicates = []
incomplete_entries = []

for line_num, line in enumerate(lines, 1):
    # Look for incomplete entries (missing -NAME=)
    if re.match(r'^ST-[\w\-]+-[\w\-]+$', line.strip()):
        incomplete_entries.append((line_num, line.strip()))
    
    # Look for complete entries
    match = re.match(r'^ST-([\w\-]+)-([\w\-]+)-NAME=', line)
    if match:
        nls, st_id = match.groups()
        key = (nls, st_id)
        if key in defined_entries[nls]:
            duplicates.append((line_num, nls, st_id))
        defined_entries[nls].add(st_id)

# Find missing definitions
print("=" * 70)
print("NLS VALIDATION REPORT - en_us.txt vs nodedefs.xml")
print("=" * 70)

print("\n1. INCOMPLETE ENTRIES (missing -NAME=):")
if incomplete_entries:
    for line_num, entry in incomplete_entries:
        print(f"  Line {line_num}: {entry}")
else:
    print("  ✓ None found")

print("\n2. DUPLICATE DEFINITIONS:")
if duplicates:
    for line_num, nls, st_id in duplicates:
        print(f"  Line {line_num}: ST-{nls}-{st_id}-NAME= (duplicate)")
else:
    print("  ✓ None found")

print("\n3. MISSING ST DEFINITIONS:")
missing_count = 0
for nls in sorted(expected_states.keys()):
    missing = expected_states[nls] - defined_entries[nls]
    if missing:
        nodeids = ', '.join(nodedef_map.get(nls, []))
        print(f"\n  {nls} (nodeDefs: {nodeids}):")
        for st_id in sorted(missing):
            print(f"    ❌ ST-{nls}-{st_id}-NAME=")
            missing_count += 1

if missing_count == 0:
    print("  ✓ All expected states are defined")

print("\n4. STATISTICS:")
print(f"  Total defined: {sum(len(v) for v in defined_entries.values())}")
print(f"  Total expected: {sum(len(v) for v in expected_states.values())}")
print(f"  Missing: {missing_count}")
print(f"  Duplicates: {len(duplicates)}")
print(f"  Incomplete: {len(incomplete_entries)}")
print("\n" + "=" * 70)