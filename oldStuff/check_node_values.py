#!/usr/bin/python2

# check node server editor and nodedef files

# Copyright (C) 2019 Robert Paauwe
#
#  TODO:
#    1. Take file names from command line

import xml.etree.ElementTree as ET

issues = 0

# Open the editors file and check for errors
editor_tree = ET.parse('profile/editor/editors.xml')
root = editor_tree.getroot()
editors = {}
for item in root:

    #print item.tag, item.attrib['id']
    for ranges in item:
        #print ' - ', ranges.tag, ranges.attrib
        editors[item.attrib['id']] = ranges.attrib['uom']
        if 'prec' in ranges.attrib:
            if 'subset' in ranges.attrib:
                print ('ERROR in editor',item.attrib['id'], 'subset and prec')
                issues += 1
            if 'min' not in ranges.attrib or 'max' not in ranges.attrib:
                print ('ERROR in editor' + item.attrib['id'] + 'prec requires min and max')
                issues += 1

        if 'step' in ranges.attrib:
            if 'subset' in ranges.attrib:
                print ('ERROR in editor' + item.attrib['id'] + 'subset and step')
                issues += 1
            if 'min' not in ranges.attrib or 'max' not in ranges.attrib:
                print ('ERROR in editor'  + item.attrib['id'] +'step requires min and max')
                issues += 1

        if ranges.attrib['uom'] == 25 and 'nls' not in ranges.attrib:
            print ('ERROR in editor' + item.attrib['id'] + 'NLS missing')
            issues += 1

if issues == 0:
    print ("No errors found in editors.xml")
    print ("")

# Read in the NLS file and build a dictionary.
nls = {}
with open('profile/nls/en_us.txt') as fp:
    for line in fp:
        line = line.rstrip()
        if line != "" and line[0] != '#':
            pair = line.split(" = ")
            nls[pair[0]] = pair[1]

# Now parse the node definitions and build the appropriate driver arrays
node_tree = ET.parse('profile/nodedef/nodedefs.xml')
root = node_tree.getroot()
for item in root:
    # this is a node definition
    for node in item:
        if node.tag == 'sts':
            print ("Driver array for node", item.attrib['id'])
            print ("drivers = [")
            for status in node:
                # status has attributes id and editor
                if 'editor' not in status.attrib:
                    print ("WARNING: node status" + status.attrib['id'] + "has no editor defined.")
                    print("\t{'driver': '%s', 'value': 0, 'uom': --}," % (status.attrib['id']))
                else:
                    print("\t{'driver': '%s', 'value': 0, 'uom': %s}," % (status.attrib['id'], editors[status.attrib['editor']]))
            print ("\t]")

node_tree = ET.parse('profile/nodedef/nodedefs.xml')
root = node_tree.getroot()
for item in root:
 #   nodeType = item.attrib['nodeType']
    nodeNls = item.attrib['nls']
    nodeId = item.attrib['id']

    # look up node name
    name = 'ND-' + nodeId + '-NAME'
    print(str(nodeId))
    if name in nls:
        print("node name = %s" % nls[name])
    else:
        print("ERROR: node name missing or incorrect")

    name = 'ND-' + nodeId + '-ICON'
    if name in nls:
        print("node icon = %s" % nls[name])
    else:
        print("ERROR: node icon missing or incorrect")

    for node in item:
        if node.tag == 'sts':
            for status in node:
                name = 'ST-' + nodeNls + '-' + status.attrib['id'] + '-NAME'
                if name in nls:
                    print("status %s has name = %s" % (status.attrib['id'], nls[name]))
                else:
                    print("ERROR: status %s name is missing or incorrect" % status.attrib['id'])

    
