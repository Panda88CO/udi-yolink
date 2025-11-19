"""
Validate udiYo*.py Node implementations against profile/nodedef/nodedefs.xml

Handles:
  - Multiple udi_interface.Node classes per file
  - drivers list matches <st> elements in corresponding nodeDef
  - id and self.id assignments map to nodeDef @id attributes (anywhere in class)
  - commands dict matches <cmd> elements in <accepts> section of nodeDef
  - Ignores commented-out <st> and <cmd> elements in XML
  - Ignores commented-out commands in Python commands dict
  
Follows udi-yolink coding conventions and copilot-instructions:
  - Skips files without udi_interface.Node classes
  - Reports missing/extra drivers, commands
  - Validates chain: nodedefs.xml → en_us.txt for ST labels
"""
import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

def remove_docstrings(content):
    """Remove triple-quoted docstrings from Python code."""
    content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    return content

def remove_commented_code(content):
    """Remove single-line comments from Python code (preserving strings)."""
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        in_string = False
        quote_char = None
        for i, char in enumerate(line):
            if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
            if char == '#' and not in_string:
                line = line[:i]
                break
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

# ============================================================================
# [1/4] Parse profile/nodedef/nodedefs.xml
# ============================================================================
print("[1/4] Parsing profile/nodedef/nodedefs.xml...")
try:
    nodedef_tree = ET.parse('profile/nodedef/nodedefs.xml')
    nodedef_root = nodedef_tree.getroot()
except Exception as e:
    print(f"❌ Failed to parse nodedefs.xml: {e}")
    exit(1)

nodedef_map = {}  # {nodedef_id: {'nls': str, 'sts': set, 'cmds': set}}
for nodedef in nodedef_root.findall('.//nodeDef'):
    node_id = nodedef.get('id')
    nls = nodedef.get('nls')
    if node_id:
        sts = set()
        cmds = set()
        
        # Extract <st id="..."> elements (XML parser skips comments automatically)
        for st in nodedef.findall('.//st'):
            st_id = st.get('id')
            if st_id:
                sts.add(st_id)
        
        # Extract <cmd id="..."> elements ONLY from <accepts> section
        accepts_elem = nodedef.find('.//accepts')
        if accepts_elem is not None:
            for cmd in accepts_elem.findall('.//cmd'):
                cmd_id = cmd.get('id')
                if cmd_id:
                    cmds.add(cmd_id)
        
        nodedef_map[node_id] = {
            'nls': nls,
            'sts': sts,
            'cmds': cmds
        }

print(f"   ✓ {len(nodedef_map)} nodeDef entries\n")

# ============================================================================
# [2/4] Parse profile/nls/en_us.txt for ST labels
# ============================================================================
print("[2/4] Parsing profile/nls/en_us.txt...")
try:
    with open('profile/nls/en_us.txt', 'r', encoding='utf-8') as f:
        en_us_lines = f.readlines()
except Exception as e:
    print(f"⚠️  Could not parse en_us.txt: {e}\n")
    en_us_lines = []

st_labels = {}  # {(nls, st_id): (line_num, label)}
for line_num, line in enumerate(en_us_lines, 1):
    match = re.match(r'^ST-([\w\-]+)-([\w\-]+)-NAME=(.+)', line.strip())
    if match:
        nls, st_id, label = match.groups()
        st_labels[(nls, st_id)] = (line_num, label)

print(f"   ✓ {len(st_labels)} ST labels\n")

# ============================================================================
# [3/4] Scan udiYo*.py files with udi_interface.Node classes
# ============================================================================
print("[3/4] Scanning udiYo*.py files with udi_interface.Node classes...\n")
udiyo_files = sorted([f for f in os.listdir('.') if f.startswith('udiYo') and f.endswith('.py')])

issues = defaultdict(list)
skipped = []
validated = []

for filename in udiyo_files:
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Skip if no udi_interface.Node classes
        if 'udi_interface.Node' not in content:
            skipped.append(filename)
            continue
        
        # Remove docstrings and comments ONLY for parsing (keep original for position tracking)
        content_clean = remove_docstrings(content)
        content_clean = remove_commented_code(content_clean)
        
        # Find ALL udi_interface.Node classes in the CLEANED content
        class_matches = list(re.finditer(r'class\s+(\w+)\s*\(\s*udi_interface\.Node\s*\)', content_clean))
        
        if not class_matches:
            skipped.append(filename)
            continue
        
        # For each class, extract its drivers and commands
        for class_idx, class_match in enumerate(class_matches):
            class_name = class_match.group(1)
            class_start = class_match.start()
            
            # Determine the end of this class (start of next class or end of file)
            if class_idx + 1 < len(class_matches):
                class_end = class_matches[class_idx + 1].start()
            else:
                class_end = len(content_clean)
            
            class_content = content_clean[class_start:class_end]
            
            # Extract id = '...' for this class (can appear anywhere in class)
            static_id_match = re.search(r"id\s*=\s*['\"]([^'\"]+)['\"]", class_content)
            static_id = static_id_match.group(1) if static_id_match else None
            
            # Extract self.id = '...' (temperature unit variants)
            self_ids = re.findall(r"self\.id\s*=\s*['\"]([^'\"]+)['\"]", class_content)
            
            # Collect all node IDs for this class
            all_ids = {static_id} if static_id else set()
            all_ids.update(self_ids)
            all_ids.discard(None)
            
            if not all_ids:
                issues[filename].append(f"❌ class {class_name}: NO id= defined")
                continue
            
            # Extract drivers list for this class: drivers = [{'driver': 'ST', ...}, ...]
            drivers_match = re.search(r"drivers\s*=\s*\[(.*?)\]", class_content, re.DOTALL)
            py_drivers = set()
            if drivers_match:
                driver_block = drivers_match.group(1)
                py_drivers = set(re.findall(r"['\"]driver['\"]\s*:\s*['\"]([^'\"]+)['\"]", driver_block))
            else:
                issues[filename].append(f"❌ class {class_name}: NO drivers list found")
                continue
            
            # Extract commands dict for this class: commands = {'DON': method, ...}
            commands_match = re.search(r"commands\s*=\s*\{(.*?)\}", class_content, re.DOTALL)
            py_commands = set()
            if commands_match:
                commands_block = commands_match.group(1)
                py_commands = set(re.findall(r"['\"](\w+)['\"]\s*:", commands_block))
            
            # Validate each ID
            file_errors = 0
            for node_id in sorted(all_ids):
                if node_id not in nodedef_map:
                    issues[filename].append(f"  ❌ class {class_name}: id='{node_id}' NOT in nodedefs.xml")
                    file_errors += 1
                    continue
                
                nd = nodedef_map[node_id]
                
                # Check drivers ↔ <st> elements (order-independent)
                missing_sts = nd['sts'] - py_drivers
                if missing_sts:
                    issues[filename].append(
                        f"  ⚠️  class {class_name} id='{node_id}': missing drivers {sorted(missing_sts)}"
                    )
                    file_errors += 1
                
                extra_sts = py_drivers - nd['sts']
                if extra_sts:
                    issues[filename].append(
                        f"  ⚠️  class {class_name} id='{node_id}': extra drivers {sorted(extra_sts)}"
                    )
                    file_errors += 1
                
                # Check commands ↔ <cmd> in <accepts> section
                missing_cmds = nd['cmds'] - py_commands
                if missing_cmds:
                    issues[filename].append(
                        f"  ⚠️  class {class_name} id='{node_id}': missing commands {sorted(missing_cmds)}"
                    )
                    file_errors += 1
                
                extra_cmds = py_commands - nd['cmds']
                if extra_cmds:
                    issues[filename].append(
                        f"  ⚠️  class {class_name} id='{node_id}': extra commands {sorted(extra_cmds)}"
                    )
                    file_errors += 1
                
                # Check ST labels in en_us.txt
                nls = nd['nls']
                for st in nd['sts']:
                    st_key = (nls, st)
                    if st_key not in st_labels:
                        issues[filename].append(
                            f"  ❌ class {class_name} id='{node_id}' state '{st}': missing ST-{nls}-{st}-NAME in en_us.txt"
                        )
                        file_errors += 1
            
            if file_errors == 0:
                validated.append((filename, class_name, sorted(all_ids)))
    
    except Exception as e:
        issues[filename].append(f"❌ PARSE ERROR: {str(e)}")

# ============================================================================
# [4/4] REPORT
# ============================================================================
print("=" * 100)
print("VALIDATION REPORT: udiYo*.py ↔ nodedefs.xml ↔ en_us.txt")
print("=" * 100)

print(f"\n✅ PASSING ({len(validated)}):")
for filename, class_name, ids in validated:
    id_str = ', '.join(ids) if ids else '(none)'
    print(f"   {filename:45s} {class_name:25s} {id_str}")

if issues:
    print(f"\n❌ ISSUES ({len(issues)}):")
    for filename in sorted(issues.keys()):
        print(f"\n   {filename}:")
        for issue in issues[filename]:
            print(f"   {issue}")

if skipped:
    print(f"\n⏭️  SKIPPED - no udi_interface.Node ({len(skipped)}):")
    for filename in skipped:
        print(f"   {filename}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Total udiYo*.py files:    {len(udiyo_files)}")
print(f"Classes validated:        {len(validated)}")
print(f"Files with issues:        {len(issues)}")
print(f"Files skipped:            {len(skipped)}")
print(f"nodeDefs in profile:      {len(nodedef_map)}")
print(f"ST labels in en_us.txt:   {len(st_labels)}")
print("=" * 100)

exit(1 if issues else 0)