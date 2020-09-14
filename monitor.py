#! /usr/bin/env python

import os
import sys
import time

def read_map_entry(label, line):
	s = line.split()
	assert(s[0] == label)
	return int(s[1])

def main(argv):
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
		fmt = '%' + str(9 * maxGroup) + 's'
		print fmt % ('node %d' % node), '| ',
	print

	for node in range(0, numNodes):
		for group in range(0, maxGroup):
			if (group,node) in gn:
				print '%8s' % ('g%d' % group),
			else:
				print '%8s' % '',
		print ' | ',
	print
	for node in range(0, numNodes):
		for group in range(0, maxGroup):
			if (group,node) in gn:
				print '%8s' % ('e%d' % gn[(group,node)]),
			else:
				print '%8s' % '',
		print ' | ',
	print

	prev_timestamp = 0
	while True:
		local_alloc = {}
		busy = {}
		ok = True
		timestamp = None
		atend = False
		for extrank in extranks:

			line = None
			while True:
				newline = files[extrank].readline()
				if newline == '':
					atend = True
					break
				line = newline
				s = newline.split()
				if len(s) == 6:
					ts = float(s[0])
					if timestamp is None:
						timestamp = ts
					else:
						timestamp = max(timestamp, ts)
					# Gone far enough ahead for this rank
					if timestamp > prev_timestamp + 1.99:
						break
			if line is None:
				ok = False
				break
			s = line.split()
			if len(s) < 6:
				ok = False
				break
			# Timestamp, global alloc, local alloc, busy, num ready, tot num ready
			if timestamp is None:
				timestamp = float(s[0])
			else:
				timestamp = min(timestamp, float(s[0]))
			local_alloc[extrank] = int(s[2])
			busy[extrank] = float(s[3])
		
		if ok:
			# print '%3.1f' % timestamp,
			for node in range(0, numNodes):
				for group in range(0, maxGroup):
					if (group,node) in gn:
						extrank = gn[(group,node)]
						print '%2d %4.1f ' % (local_alloc[extrank], busy[extrank]),
					else:
						print '%8s' % '-',
				print ' | ',
			print

		if atend:
			time.sleep(2)
			
if __name__ == '__main__':
	sys.exit(main(sys.argv))


