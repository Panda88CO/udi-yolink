import xml.etree.ElementTree as ET
import os

editors_xml_path = "profile/editor/editors.xml"
nodedefs_xml_path = "profile/nodedef/nodedefs.xml"

if not os.path.exists(editors_xml_path) or not os.path.exists(nodedefs_xml_path):
    print("Files not found.")
    exit(1)

# Parse nodedefs.xml to find used editor IDs
tree_nodedefs = ET.parse(nodedefs_xml_path)
root_nodedefs = tree_nodedefs.getroot()
used_editors = set()

for elem in root_nodedefs.iter():
    if elem.tag in ['st', 'cmd', 'p']:
        editor_id = elem.get('editor')
        if editor_id:
            used_editors.add(editor_id)

# Parse editors.xml to find and remove unused editors
tree_editors = ET.parse(editors_xml_path)
root_editors = tree_editors.getroot()
removed_ids = []

# Iterate over editor elements and remove if not used
all_editors = root_editors.findall('editor')
for editor in all_editors:
    editor_id = editor.get('id')
    if editor_id not in used_editors:
        root_editors.remove(editor)
        removed_ids.append(editor_id)

# Save the updated editors.xml
tree_editors.write(editors_xml_path, encoding='utf-8', xml_declaration=True)

print(f"Removed {len(removed_ids)} editor blocks.")
if removed_ids:
    print(f"Removed IDs: {', '.join(removed_ids)}")
else:
    print("No unused editors found.")
