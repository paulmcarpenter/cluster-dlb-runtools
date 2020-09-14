#! /usr/bin/env python

import os
import sys
import time
import getopt

def read_map_entry(label, line):
	s = line.split()
	assert(s[0] == label)
	return int(s[1])

def Usage():
	print './monitor.py <options>'
	print 'where:'
	print ' -h                      Show this help'
	print ' --alloc                 Show allocated #cores'
	print ' --enabled               Show enabled #cores from DLB'
	print ' --busy                  Show busy #cores'
	print ' --localtasks            Show local ready tasks'
	print ' --totaltasks            Show total ready tasks in group'
	return 1

fmt_spec = {'alloc' : '%2d', 'enabled' : '%2d', 'busy' : '%4.1f', 'localtasks' : '%4d', 'totaltasks' : '%4d'}

def format_value(value, typ):
	field = value[typ]
	if typ in ['localtasks', 'totaltasks']:
		if field > 999:
			return '>999'
	return fmt_spec[typ] % field

fmt_width = {'alloc': 2, 'enabled': 2, 'busy': 5, 'localtasks' : 4, 'totaltasks' : 4}

def main(argv):

	cols = []

	try:
		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'alloc', 'enabled', 'busy',
										  'localtasks', 'totaltasks'] )

	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()
		if o == '--alloc':
			cols.append('alloc')
		elif o == '--enabled':
			cols.append('enabled')
		elif o == '--busy':
			cols.append('busy')
		elif o == '--localtasks':
			cols.append('localtasks')
		elif o == '--totaltasks':
			cols.append('totaltasks')
	
	if len(cols) == 0:
		cols = ['enabled', 'busy']

	empty_fmt_width = sum([fmt_width[col] for col in cols]) + len(cols)-1
	empty_fmt = '%' + str(empty_fmt_width) + 's'
	print 'empty_fmt', empty_fmt

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
		fmt = '%' + str((empty_fmt_width+1) * maxGroup) + 's'
		print fmt % ('node %d' % node), '| ',
	print

	for node in range(0, numNodes):
		for group in range(0, maxGroup):
			if (group,node) in gn:
				print empty_fmt % ('g%d' % group),
			else:
				print empty_fmt  % '',
		print ' | ',
	print
	for node in range(0, numNodes):
		for group in range(0, maxGroup):
			if (group,node) in gn:
				print empty_fmt  % ('e%d' % gn[(group,node)]),
			else:
				print empty_fmt  % '',
		print ' | ',
	print

	prev_timestamp = 0
	while True:
		values = dict([ (extrank, {}) for extrank in extranks])
		# local_alloc = {}
		# busy = {}
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
			values[extrank]['alloc'] = int(s[1])
			values[extrank]['enabled'] = int(s[2])
			values[extrank]['busy'] = float(s[3])
			values[extrank]['localtasks'] = int(s[4])
			values[extrank]['totaltasks'] = int(s[4])
		
		if ok:
			# print '%3.1f' % timestamp,
			for node in range(0, numNodes):
				for group in range(0, maxGroup):
					if (group,node) in gn:
						extrank = gn[(group,node)]
						#print '%2d %4.1f ' % (local_alloc[extrank], busy[extrank]),
						for col in cols:
							print format_value(values[extrank], col),
						print '',
					else:
						print empty_fmt % '-',
				print ' | ',
			print

		if atend:
			time.sleep(2)
			
if __name__ == '__main__':
	sys.exit(main(sys.argv))


