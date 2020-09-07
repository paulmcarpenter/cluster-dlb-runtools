#! /usr/bin/env python

import os
import time

def read_map_entry(label, line):
	s = line.split()
	assert(s[0] == label)
	return int(s[1])

extranksOnNode = {}
extranks = []
gn = {}
maxGroup = 0

mapfiles = [f for f in os.listdir('.hybrid') if f.startswith('map')]
for mapfile in mapfiles:
	f = open('.hybrid/' + mapfile, 'r')
	extrank = read_map_entry('externalRank', f.readline())
	groupNum = read_map_entry('groupNum', f.readline())
	internalRank = read_map_entry('internalRank', f.readline())
	nodeNum = read_map_entry('nodeNum', f.readline())

	if not nodeNum in extranksOnNode:
		extranksOnNode[nodeNum] = []
	extranksOnNode[nodeNum].append(extrank)
	extranks.append(extrank)
	assert not (groupNum, nodeNum) in gn
	gn[(groupNum, nodeNum)] = extrank
	maxGroup = max(maxGroup, groupNum+1)

numNodes = max(extranksOnNode.keys()) + 1

files = {}
for extrank in extranks:
	files[extrank] = open('.hybrid/utilization%d' % extrank, 'r')

for node in range(0, numNodes):
	fmt = '%' + str(4 * maxGroup) + 's'
	print fmt % ('node %d' % node), '| ',
print

for node in range(0, numNodes):
	for group in range(0, maxGroup):
		if (group,node) in gn:
			print '%3s' % ('g%d' % group),
		else:
			print '   ',
	print ' | ',
print
for node in range(0, numNodes):
	for group in range(0, maxGroup):
		if (group,node) in gn:
			print '%3s' % ('e%d' % gn[(group,node)]),
		else:
			print '   ',
	print ' | ',
print

while True:
	local_alloc = {}
	ok = True
	for extrank in extranks:
		line = None
		while True:
			newline = files[extrank].readline()
			if newline == '':
				break
			line = newline
		if line is None:
			ok = False
			break
		s = line.split()
		if len(s) < 6:
			ok = False
			break
		# Timestamp, global alloc, local alloc, busy, num ready, tot num ready
		local_alloc[extrank] = int(s[2])
	
	if ok:
		for node in range(0, numNodes):
			for group in range(0, maxGroup):
				if (group,node) in gn:
					print '%3d' % local_alloc[gn[(group,node)]],
				else:
					print '  -',
			print ' | ',
		print




	time.sleep(2)
		



