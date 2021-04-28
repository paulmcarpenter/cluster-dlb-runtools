#! /usr/bin/env python

import os
import sys
import time
import getopt

use_colours = True
if not sys.stdout.isatty():
	use_colours = False


def black(s):
    return s

def weak_red(s):
    if not use_colours:
        return s
    return '\033[0;31m' + s + '\033[0;m'  if use_colours else s

def red(s):
    if not use_colours:
        return s
    return '\033[1;31m' + s + '\033[0;m'  if use_colours else s

def weak_green(s):
    if not use_colours:
        return s
    return '\033[0;32m' + s + '\033[0;m'  if use_colours else s

def green(s):
    if not use_colours:
        return s
    return '\033[1;32m' + s + '\033[0;m'  if use_colours else s

def weak_blue(s):
    if not use_colours:
        return s
    return '\033[0;34m' + s + '\033[0;m'  if use_colours else s

def blue(s):
    if not use_colours:
        return s
    return '\033[1;34m' + s + '\033[0;m'  if use_colours else s

def weak_magenta(s):
    if not use_colours:
        return s
    return '\033[0;35m' + s + '\033[0;m'  if use_colours else s

def magenta(s):
    if not use_colours:
        return s
    return '\033[1;35m' + s + '\033[0;m'  if use_colours else s


def read_map_entry(label, line):
	s = line.split()
	assert(s[0] == label)
	return int(s[1])

class ReadLog:
	def __init__(self, fp):
		self._fp = fp
		self._splitline = None
		self._timestamp = None
	
	def try_read_next(self):
		line = self._fp.readline()
		if line == '':
			self._splitline = None
			self._timestamp = None
		else:
			self._splitline = line.split()
			self._timestamp = float(self._splitline[0])

	def timestamp(self):
		if self._splitline is None:
			self.try_read_next()
		return self._timestamp

	def current(self):
		if self._splitline is None:
			self.try_read_next()
		return self._splitline

	def get_next(self):
		self.try_read_next()



def Usage():
	print( './monitor.py <options>')
	print( 'where:')
	print( ' -h                      Show this help')
	print( ' --order-by vrank/node   Group by vrank or node')
	print( ' --alloc                 Show allocated #cores')
	print( ' --enabled               Show active owned #cores from DLB')
	print( ' --owned                 Show owned #cores from DLB')
	print( ' --lent                  Show number lent cores from DLB')
	print( ' --busy                  Show busy #cores')
	print( ' --useful-busy           Show useful busy #cores')
	print( ' --localtasks            Show local ready tasks')
	print( ' --totaltasks            Show total ready tasks in apprank')
	print( ' --promised              Show local num. promised tasks')
	print( ' --immovable             Show local num. immovable tasks')
	return 1

fmt_spec = {'alloc' : '%2d', 'enabled' : '%2d', 'busy' : '%4.1f', 'useful-busy' : '%4.1f', 'localtasks' : '%4d', 'totaltasks' : '%4d',
			'promised' : '%4d', 'immovable' : '%4d', 'requests' : '%4d', 'requestacks' : '%4d', 'owned' : '%4d',
			'lent' : '%4d', 'borrowed' : '%4d', '14' : '%4.1f', '15' : '%4.1f', '16' : '%4.1f'}

fmt_no_value = {'alloc' : '%2s', 'enabled' : '%2s', 'busy' : '%4s', 'useful-busy' : '%4s', 'localtasks' : '%4s', 'totaltasks' : '%4s',
			'promised' : '%4s', 'immovable' : '%4s', 'requests' : '%4s', 'requestacks' : '%4s', 'owned' : '%4s',
			'lent' : '%4s', 'borrowed' : '%4s', '14' : '%4s', '15' : '%4s', '16' : '%4s'}

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
	elif typ == 'useful-busy':
		return weak_magenta(formatted)
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
	else:
		return formatted

def no_value(typ):
	return fmt_no_value[typ] % '#'

fmt_width = {'alloc': 2, 'enabled': 2, 'busy': 5, 'useful-busy': 5, 'localtasks' : 4, 'totaltasks' : 4, 'promised' : 4, 'immovable' : 4, 
			'requests' : 4, 'requestacks' : 4, 'owned' : 4, 'lent' : 4, 'borrowed' : 4, '14' : 4, '15' : 4, '16' : 4}
def main(argv): 
	cols = []
	squash = True
	print_timestamp = True
	order_by = 'vrank'  # 'vrank' or 'node'
	follow = False
	subsample = 1

	try:
		opts, args = getopt.getopt( argv[1:],
									'hf', ['help', 'order-by=',
										  'alloc', 'enabled', 'busy', 'useful-busy',
										  'localtasks', 'totaltasks',
										  'promised', 'immovable',
										  'requests', 'requestacks',
										  'owned', 'lent', 'borrowed', '14', '15',  '16', 'follow',
										  'subsample='] )

	except getopt.error as msg:
		print(msg)
		print("for help use --help")
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()
		elif o in ('-f', '--follow'):
			follow = True
		elif o == '--alloc':
			cols.append('alloc')
		elif o == '--enabled':
			cols.append('enabled')
		elif o == '--busy':
			cols.append('busy')
		elif o == '--useful-busy':
			cols.append('useful-busy')
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
		elif o == '--14':
			cols.append('14')
		elif o == '--15':
			cols.append('15')
		elif o == '--16':
			cols.append('16')
		elif o == '--subsample':
			subsample = int(a)
		elif o == '--order-by':
			order_by = a
			if not order_by in ['node', 'vrank']:
				print(order_by)
				print('Bad order-by: valid values are node, vrank')
				return 1
		else:
			assert(False)
	
	if len(cols) == 0:
		cols = ['alloc', 'enabled', 'busy']

	empty_fmt_width = sum([fmt_width[col] for col in cols]) + len(cols)-1
	empty_fmt = '%' + str(empty_fmt_width) + 's'

	if squash:
		none_fmt = '%2s'
	else:
		none_fmt = empty_fmt

	extranksOnNode = {}
	extranks = []
	gn = {}
	maxGroup = 0

	mapfiles = [f for f in os.listdir('.hybrid') if f.startswith('map')]
	for mapfile in mapfiles:
		with open('.hybrid/' + mapfile, 'r') as f:
			extrank = read_map_entry('externalRank', f.readline())
			apprankNum = read_map_entry('apprankNum', f.readline())
			internalRank = read_map_entry('internalRank', f.readline())
			nodeNum = read_map_entry('nodeNum', f.readline())

		if not nodeNum in extranksOnNode:
			extranksOnNode[nodeNum] = []
		extranksOnNode[nodeNum].append(extrank)
		extranks.append(extrank)
		assert not (apprankNum, nodeNum) in gn
		gn[(apprankNum, nodeNum)] = extrank
		maxGroup = max(maxGroup, apprankNum+1)

	numNodes = max(extranksOnNode.keys()) + 1

	files = {}
	for extrank in extranks:
		files[extrank] = open('.hybrid/utilization%d' % extrank, 'r')

	# for node in range(0, numNodes):
	# 	fmt = '%' + str((empty_fmt_width+1) * maxGroup) + 's'
	# 	print fmt % ('node %d' % node), '| ',
	# print

	# for node in range(0, numNodes):
	# 	for apprank in range(0, maxGroup):
	# 		if (apprank,node) in gn:
	# 			print empty_fmt % ('g%d' % apprank),
	# 		else:
	# 			print none_fmt  % '',
	# 	print ' | ',
	# print
	# for node in range(0, numNodes):
	# 	for apprank in range(0, maxGroup):
	# 		if (apprank,node) in gn:
	# 			print empty_fmt  % ('e%d' % gn[(apprank,node)]),
	# 		else:
	# 			print none_fmt  % '',
	# 	print ' | ',
	# print

	readlogs = dict( [(extrank, ReadLog(files[extrank])) for extrank in extranks])

	curr_timestamp = 0
	done = False
	linenum = 0
	while not done:
		linenum += 1
		values = {}
		atend = False
		num_valid = 0

		for extrank in extranks:

			# Get current line from all
			s = None
			while True:
				if readlogs[extrank].timestamp() is None:
					if not follow:
						done = True
						break
					time.sleep(0.1)
					continue
				if readlogs[extrank].timestamp() > curr_timestamp:
					# Keep for next time, nothing to report
					break
				s = readlogs[extrank].current()
				readlogs[extrank].get_next()

			# Get current line from all
			if not s is None:
				num_valid += 1
				values[extrank] = {}
				values[extrank]['alloc'] = int(s[1])
				values[extrank]['enabled'] = int(s[2])
				values[extrank]['busy'] = float(s[3])
				values[extrank]['useful-busy'] = float(s[4])
				values[extrank]['localtasks'] = int(s[5])
				values[extrank]['totaltasks'] = int(s[6])
				values[extrank]['promised'] = int(s[7])
				values[extrank]['immovable'] = int(s[8])
				values[extrank]['requests'] = int(s[9])
				values[extrank]['requestacks'] = int(s[10])
				values[extrank]['owned'] = int(s[11])
				values[extrank]['lent'] = int(s[12])
				values[extrank]['borrowed'] = int(s[13])
				if len(s) >= 15:
					values[extrank]['14'] = float(s[14])
				if len(s) >= 16:
					values[extrank]['15'] = float(s[15])
				if len(s) >= 17:
					values[extrank]['16'] = float(s[16])

		curr_timestamp += 0.5

		if (linenum % subsample) != 0:
			continue

		if print_timestamp:
			print('%5.1f ' % curr_timestamp, end='')

		if num_valid > 0:
			if order_by == 'node':
				extranks_pr = [  [gn[(apprank,node)] for apprank in range(0,maxGroup) if (apprank,node) in gn] for node in range(0, numNodes) ]
			elif order_by == 'vrank':
				extranks_pr = [  [gn[(apprank,node)] for node in range(0,numNodes) if (apprank,node) in gn] for apprank in range(0,maxGroup) ]
			else:
				assert false

			for extranks1 in extranks_pr:
				for extrank in extranks1:
					#print '%2d %4.1f ' % (local_alloc[extrank], busy[extrank]),
					if extrank in values:
						for col in cols:
							print(format_value(values[extrank], col), end=' ')
					else:
						for col in cols:
							print(no_value(col), end=' ')
					print(' ', end='')
				else:
					print(none_fmt % '-', end=' ')
				print(' |  ', end='')
		print()

	for extrank in extranks:
		files[extrank].close()

			
if __name__ == '__main__':
	sys.exit(main(sys.argv))


