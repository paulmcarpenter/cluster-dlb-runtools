#! /usr/bin/env python

import os
import sys
import time
import getopt

use_colours = True

def black(s):
    return s

def weak_red(s):
    return '\033[0;31m' + s + '\033[0;m'  if use_colours else s

def red(s):
    return '\033[1;31m' + s + '\033[0;m'  if use_colours else s

def weak_green(s):
    return '\033[0;32m' + s + '\033[0;m'  if use_colours else s

def green(s):
    return '\033[1;32m' + s + '\033[0;m'  if use_colours else s

def weak_blue(s):
    return '\033[0;34m' + s + '\033[0;m'  if use_colours else s

def blue(s):
    return '\033[1;34m' + s + '\033[0;m'  if use_colours else s

def weak_magenta(s):
    return '\033[0;35m' + s + '\033[0;m'  if use_colours else s

def magenta(s):
    return '\033[1;35m' + s + '\033[0;m'  if use_colours else s


def read_map_entry(label, line):
	s = line.split()
	assert(s[0] == label)
	return int(s[1])

def Usage():
	print './monitor.py <options>'
	print 'where:'
	print ' -h                      Show this help'
	print ' --alloc                 Show allocated #cores'
	print ' --enabled               Show active owned #cores from DLB'
	print ' --owned                 Show owned #cores from DLB'
	print ' --lent                  Show number lent cores from DLB'
	print ' --busy                  Show busy #cores'
	print ' --localtasks            Show local ready tasks'
	print ' --totaltasks            Show total ready tasks in group'
	print ' --promised              Show local num. promised tasks'
	print ' --immovable             Show local num. immovable tasks'
	return 1

fmt_spec = {'alloc' : '%2d', 'enabled' : '%2d', 'busy' : '%4.1f', 'localtasks' : '%4d', 'totaltasks' : '%4d',
			'promised' : '%4d', 'immovable' : '%4d', 'requests' : '%4d', 'requestacks' : '%4d', 'owned' : '%4d',
			'lent' : '%4d', 'borrowed' : '%4d', '13' : '%4d'}

def format_value(value, typ):
	field = value[typ]
	if typ in ['localtasks', 'totaltasks', 'promised', 'immovable']:
		if False and field > 999:
			return '>999'
	formatted = fmt_spec[typ] % field
	if typ == 'alloc':
		return red(formatted)
	elif typ == 'enabled':
		return weak_red(formatted)
	elif typ == 'busy':
		return magenta(formatted)
	elif typ == 'localtasks':
		return green(formatted)
	elif typ == 'totaltasks':
		return weak_green(formatted)
	elif typ == 'requests':
		return blue(formatted)
	elif typ == 'requestacks':
		return weak_blue(formatted)
	elif typ == 'owned':
		return blue(formatted)
	elif typ == 'lent':
		return blue(formatted)
	elif typ == 'borrowed':
		return blue(formatted)
	elif typ == '13':
		return blue(formatted)
	else:
		return formatted

fmt_width = {'alloc': 2, 'enabled': 2, 'busy': 5, 'localtasks' : 4, 'totaltasks' : 4, 'promised' : 4, 'immovable' : 4, 
			'requests' : 4, 'requestacks' : 4, 'owned' : 4, 'lent' : 4, 'borrowed' : 4, '13' : 4}

def main(argv):

	cols = []
	squash = True

	try:
		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'squash', 'alloc', 'enabled', 'busy',
										  'localtasks', 'totaltasks',
										  'promised', 'immovable',
										  'requests', 'requestacks',
										  'owned', 'lent', 'borrowed', '13'] )

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
		elif o == '--promised':
			cols.append('promised')
		elif o == '--immovable':
			cols.append('immovable')
		elif o == '--requests':
			cols.append('requests')
		elif o == '--requestacks':
			cols.append('requestacks')
		elif o == '--owned':
			cols.append('owned')
		elif o == '--lent':
			cols.append('lent')
		elif o == '--borrowed':
			cols.append('borrowed')
		elif o == '--13':
			cols.append('13')
		elif o == '--squash':
			squash = True
	
	if len(cols) == 0:
		cols = ['alloc', 'enabled', 'busy']

	empty_fmt_width = sum([fmt_width[col] for col in cols]) + len(cols)-1
	empty_fmt = '%' + str(empty_fmt_width) + 's'

	if squash:
		none_fmt = '%4s'
	else:
		none_fmt = empty_fmt

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
				print none_fmt  % '',
		print ' | ',
	print
	for node in range(0, numNodes):
		for group in range(0, maxGroup):
			if (group,node) in gn:
				print empty_fmt  % ('e%d' % gn[(group,node)]),
			else:
				print none_fmt  % '',
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
				if len(s) >= 6:
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
			values[extrank]['totaltasks'] = int(s[5])
			values[extrank]['promised'] = int(s[6])
			values[extrank]['immovable'] = int(s[7])
			values[extrank]['requests'] = int(s[8])
			values[extrank]['requestacks'] = int(s[9])
			values[extrank]['owned'] = int(s[10])
			values[extrank]['lent'] = int(s[11])
			values[extrank]['borrowed'] = int(s[12])
			if len(s) >= 14:
				values[extrank]['13'] = int(s[13])

		
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
						print none_fmt % '-',
				print ' | ',
			print

		if atend:
			time.sleep(1)
			
if __name__ == '__main__':
	sys.exit(main(sys.argv))


