import xml.etree.ElementTree as ET
import re
from collections import defaultdict


def _extract_tag_id(line, tag_name):
    """Extract id from a line containing a specific XML tag."""
    match = re.search(rf'<{tag_name}\b[^>]*\bid\s*=\s*["\']([^"\']+)["\']', line)
    return match.group(1) if match else "(unknown)"


def validate_parent_child_structure(path, parent_tag, child_tag):
    """Validate raw XML lines for parent/child structural mistakes.

    Detects:
      - child tags outside an open parent block
      - unclosed parent blocks
      - parent closed on the same line and followed by child lines
    """
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
    except Exception as exc:
        return [f"❌ Could not read {path}: {exc}"]

    # Remove XML comments so commented tags do not produce false positives.
    content = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    lines = content.splitlines()

    issues = []
    parent_stack = []  # list of (line_num, parent_id)
    recent_single_line_parent = None  # (line_num, parent_id)

    has_child_re = re.compile(rf'<{child_tag}\b')
    has_parent_open_re = re.compile(rf'<{parent_tag}\b')
    has_parent_close_re = re.compile(rf'</{parent_tag}\s*>')
    self_closing_parent_re = re.compile(rf'<{parent_tag}\b[^>]*?/>')

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue

        has_child = bool(has_child_re.search(stripped))
        has_parent_open = bool(has_parent_open_re.search(stripped))
        has_parent_close = bool(has_parent_close_re.search(stripped))
        is_self_closing_parent = bool(self_closing_parent_re.search(stripped))
        parent_id = _extract_tag_id(stripped, parent_tag) if has_parent_open else "(unknown)"

        # If we moved beyond the line where parent was closed inline and did not
        # encounter the relevant child, clear it to avoid stale matches.
        if recent_single_line_parent and line_num > recent_single_line_parent[0] and not has_child:
            recent_single_line_parent = None

        # Same-line close (<parent .../> or <parent ...></parent>) can cause
        # following child lines to be orphaned.
        if has_parent_open and (is_self_closing_parent or has_parent_close):
            recent_single_line_parent = (line_num, parent_id)
        elif has_parent_open:
            parent_stack.append((line_num, parent_id))
            recent_single_line_parent = None

        if has_child and not parent_stack:
            if recent_single_line_parent:
                parent_line, recent_parent_id = recent_single_line_parent
                issues.append(
                    f"❌ line {line_num}: <{child_tag}> is outside <{parent_tag}>; prior <{parent_tag} id='{recent_parent_id}'> on line {parent_line} was closed on the same line"
                )
            else:
                issues.append(
                    f"❌ line {line_num}: <{child_tag}> is outside an open <{parent_tag}> block"
                )

        # Handle explicit close tags for multiline parents.
        if has_parent_close and not is_self_closing_parent:
            close_count = len(re.findall(rf'</{parent_tag}\s*>', stripped))
            for _ in range(close_count):
                if parent_stack:
                    parent_stack.pop()
                elif not has_parent_open:
                    issues.append(
                        f"❌ line {line_num}: found </{parent_tag}> without matching <{parent_tag}>"
                    )

    for open_line, open_parent_id in parent_stack:
        issues.append(
            f"❌ line {open_line}: <{parent_tag} id='{open_parent_id}'> is not closed with </{parent_tag}>"
        )

    return issues


def validate_subsection_structure():
    """Validate multiple parent/child subsection patterns before XML parsing."""
    checks = [
        ('profile/nodedef/nodedefs.xml', 'nodeDefs', 'nodeDef'),
        ('profile/nodedef/nodedefs.xml', 'nodeDef', 'sts'),
        ('profile/nodedef/nodedefs.xml', 'nodeDef', 'cmds'),
        ('profile/nodedef/nodedefs.xml', 'sts', 'st'),
        ('profile/nodedef/nodedefs.xml', 'cmds', 'sends'),
        ('profile/nodedef/nodedefs.xml', 'cmds', 'accepts'),
        ('profile/nodedef/nodedefs.xml', 'cmd', 'p'),
        ('profile/editor/editors.xml', 'editors', 'editor'),
        ('profile/editor/editors.xml', 'editor', 'range'),
    ]

    grouped_issues = defaultdict(list)
    for path, parent_tag, child_tag in checks:
        rule_issues = validate_parent_child_structure(path, parent_tag, child_tag)
        if rule_issues:
            grouped_issues[path].append((parent_tag, child_tag, rule_issues))

    # Specialized check: <cmd> should be within either <accepts> or <sends>.
    cmd_container_issues = validate_cmd_in_valid_container('profile/nodedef/nodedefs.xml')
    if cmd_container_issues:
        grouped_issues['profile/nodedef/nodedefs.xml'].append(
            ('accepts|sends', 'cmd', cmd_container_issues)
        )

    return grouped_issues


def validate_cmd_in_valid_container(path):
    """Ensure <cmd> tags are inside either <accepts> or <sends> blocks."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
    except Exception as exc:
        return [f"❌ Could not read {path}: {exc}"]

    content = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    lines = content.splitlines()
    issues = []

    accepts_depth = 0
    sends_depth = 0
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue

        accepts_depth += len(re.findall(r'<accepts\b[^>]*>', stripped))
        sends_depth += len(re.findall(r'<sends\b[^>]*>', stripped))

        # Ignore closing tags and only inspect cmd opening tags.
        if re.search(r'<cmd\b', stripped) and not re.search(r'</cmd\s*>', stripped):
            if accepts_depth == 0 and sends_depth == 0:
                issues.append(f"❌ line {line_num}: <cmd> is outside both <accepts> and <sends>")

        accepts_depth -= len(re.findall(r'</accepts\s*>', stripped))
        sends_depth -= len(re.findall(r'</sends\s*>', stripped))

    return issues


structure_issues = validate_subsection_structure()
if structure_issues:
    print("=" * 80)
    print("PROFILE STRUCTURE VALIDATION")
    print("=" * 80)
    for path in sorted(structure_issues.keys()):
        print(f"\n{path}:")
        for parent_tag, child_tag, issues in structure_issues[path]:
            print(f"  Rule <{parent_tag}> -> <{child_tag}>")
            for issue in issues:
                print(f"    {issue}")
    raise SystemExit(1)
print("✓ PROFILE STRUCTURE VALIDATION passed (nodedefs.xml + editors.xml)")

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