#! /usr/bin/env python

import os
import sys
import time
import getopt
import re

use_colours = True
if not sys.stdout.isatty():
	use_colours = False

# Allow --14 up to --30 (depending on value of {max,max}_numbered_field)
min_numbered_field = 14
max_numbered_field = 30

def read_appranks_or_nodes(s):
	ll = s.split(',')
	vv = []
	for l in ll:
		m = re.match('([0-9][0-9]*)-([0-9][0-9]*)', l)
		if m:
			first = int(m.group(1))
			last = int(m.group(2))
			for e in range(first,last+1):
				vv.append(e)
		else:
			vv.append(int(l))
	return vv
		

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

def yellow(s):
    if not use_colours:
        return s
    return '\033[1;33m' + s + '\033[0;m'  if use_colours else s


def apprankDigit(apprank):
	if apprank < 10:
		return chr(ord('0') + apprank)
	else:
		return chr(ord('a') + (apprank-10))

def read_map_entry(label, line, mapfilename):
	s = line.split()
	if len(s) < 1 or s[0] != label:
		print(f'Bad map file {mapfilename}')
		sys.exit(1)
	return int(s[1])

class ReadLog:
	def __init__(self, filename):
		self._fp = open(filename, 'r')
		self._splitline = None
		self._timestamp = None
		self.done = False

	def __del__(self):
		self._fp.close()
	
	def try_read_next(self):
		line = self._fp.readline()
		if line.startswith('DONE'):
			self.done = True
			self._splitline = None
			self._timestamp = None
		elif line == '':
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
	print( ' -f, --follow            Continuous output while program runs')
	print( ' --order-by apprank/node Group by apprank or node (default apprank)')
	print( ' --alloc                 Show allocated #cores')
	print( ' --enabled               Show active owned #cores from DLB')
	print( ' --owned                 Show owned #cores from DLB')
	print( ' --lent                  Show number lent cores from DLB')
	print( ' --busy                  Show busy #cores')
	print( ' --useful-busy           Show useful busy #cores')
	print( ' --localtasks            Show local ready tasks')
	print( ' --totaltasks            Show total ready tasks in apprank')
	print( ' --apprankbusy           Show total apprank busy cores')
	print( ' --immovable             Show local num. immovable tasks')
	print( ' --%d,--%d,...,--%d      Show numbered fields reserved for debug' % \
			(min_numbered_field, min_numbered_field+1, max_numbered_field) )
	print( ' --appranks l            List of appranks (use with order-by apprank)')
	print( ' --nodes l               List of nodes (use with order-by node)')
	print( ' --barchart busy         Draw a barchart of busy')
	return 1

fmt_spec = {'alloc' : '%2d', 'enabled' : '%2d', 'busy' : '%4.1f', 'useful-busy' : '%4.1f', 'localtasks' : '%4d', 'totaltasks' : '%4d',
			'apprankbusy' : '%4.1f', 'immovable' : '%4d', 'requests' : '%4d', 'requestacks' : '%4d', 'owned' : '%4d',
			'lent' : '%4d', 'borrowed' : '%4d'}

fmt_width = {'alloc' : 2, 'enabled' : 2, 'busy' : 4, 'useful-busy' : 4, 'localtasks' : 4, 'totaltasks' : 4,
			'apprankbusy' : 4, 'immovable' : 4, 'requests' : 4, 'requestacks' : 4, 'owned' : 4,
			'lent' : 4, 'borrowed' : 4}

fmt_no_value = {'alloc' : '%2s', 'enabled' : '%2s', 'busy' : '%4s', 'useful-busy' : '%4s', 'localtasks' : '%4s', 'totaltasks' : '%4s',
			'apprankbusy' : '%4s', 'immovable' : '%4s', 'requests' : '%4s', 'requestacks' : '%4s', 'owned' : '%4s',
			'lent' : '%4s', 'borrowed' : '%4s'}

fmt_desc = {'alloc' : 'Allocated cores (target number to own)',
			'enabled' : 'Enabled cores (owned-lent+borrowed)',
			'busy' : 'Busy cores',
			'useful-busy' : 'Useful busy cores (running tasks)',
			'localtasks' : 'Local ready tasks',
			'totaltasks' : 'Total ready tasks on apprank',
			'apprankbusy' : 'Busy cores on apprank',
			'immovable' : 'Immovable tasks (if(0), nooffload, sent to host scheduler)',
			'requests' : 'Request messages',
			'requestacks' : 'Request Ack messages',
			'owned' : 'Owned cores (via DROM)',
			'lent' : 'Lent cores (via LeWI)',
			'borrowed' : 'Borrowed cores (via LeWI)'}

for f in range(min_numbered_field, max_numbered_field+1):
	fmt_spec[str(f)] = '%4.1f'
	fmt_width[str(f)] = 4
	fmt_no_value[str(f)] = '%4s'
	fmt_desc[str(f)] = '%d - reserved for debug' % f

def colour_value(formatted, typ):
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
	
def format_value(value, typ):
	field = value[typ]
	if typ in ['localtasks', 'totaltasks', 'promised', 'immovable']:
		if False and field > 999:
			return '>999'
	formatted = fmt_spec[typ] % field
	return colour_value(formatted, typ)

def make_barchart(values, extranks1, fieldname, width, extrankApprank):
	def colour_code(apprank):
		d = {'0' : '\033[1;34m', # blue
			 '1' : '\033[1;31m', # red
			 '2' : '\033[1;33m', # yellow
			 '3' : '\033[1;32m', # green
			 '4' : '\033[1;35m', # magenta
			 '5' : '\033[1;36m', # cyan
			 '6' : '\033[38;5;105m',
			 '7' : '\033[38;5;9m',
			 '8' : '\033[0;34m', # weak blue
			 '9' : '\033[0;31m', # weak red
			 'a' : '\033[0;33m', # weak yellow
			 'b' : '\033[0;32m', # weak green
			 'c' : '\033[0;35m', # weak magenta
			 'd' : '\033[0;36m', # weak cyan
			 'e' : '\033[38;5;210m',
			 'f' : '\033[38;5;249m'
			 }

		return d.get(apprank, '\033[0;m')
	
	# Build to correct width without colouring
	s = ''
	curWidth = 0
	for extrank in extranks1:
		if not extrank in values.keys():
			return '?' * width
		val = values[extrank][fieldname]
		numchars = int((val * width) / 48)
		apprank = extrankApprank[extrank]
		#print('apprank', apprank, 'value', numchars)
		s = s + apprankDigit(apprank) * numchars
		curWidth += numchars
	if curWidth < width:
		s = s + ' ' * (width - curWidth)
	elif curWidth > width:
		s = s + '   '
		s = s[:width-3] + '...'

	cur_col = None
	s2 = ''
	if use_colours:
		for ch in s:
			if ch != cur_col:
				cur_col = ch
				s2 = s2 + colour_code(cur_col)
			s2 = s2 + ch
		if ch != None:
			s2 = s2 + '\033[0;m'

	return s2


def no_value(typ):
	return fmt_no_value[typ] % '#'

def is_number_option(o):
	# Recognise numbered options, e.g. --14, --15, ...
	m = re.match('--[0-9][0-9]*', o)
	return not m is None

def find_hybrid_dir():
	if os.path.exists('.hybrid'):
		return '.hybrid'
	if os.path.exists('map0') and os.path.exists('utilization0'):
		return '.'
	print('Cannot find hybrid directory: not .hybrid or .')
	sys.exit(1)

def main(argv): 
	cols = []
	squash = True
	print_timestamp = True
	order_by = 'apprank'  # 'apprank' or 'node'
	follow = False
	subsample = 1
	show_appranks = None
	show_nodes = None
	hybrid_dir = find_hybrid_dir()
	barchart = None

	try:
		numbered_opts = [str(f) for f in range(min_numbered_field, max_numbered_field+1) ]

		opts, args = getopt.getopt( argv[1:],
									'hf', ['help', 'order-by=',
										  'alloc', 'enabled', 'busy', 'useful-busy',
										  'localtasks', 'totaltasks',
										  'apprankbusy', 'immovable',
										  'requests', 'requestacks',
										  'owned', 'lent', 'borrowed',
										  'follow',
										  'barchart=',
										  'subsample=', 'appranks=', 'nodes='] + numbered_opts)

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
		elif o == '--apprankbusy':
			cols.append('apprankbusy')
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
		elif o == '--subsample':
			subsample = int(a)
		elif o == '--appranks':
			show_appranks = read_appranks_or_nodes(a)
		elif o == '--nodes':
			show_nodes = read_appranks_or_nodes(a)
		elif o == '--barchart':
			barchart = a
			order_by = 'node'
		elif o == '--order-by':
			order_by = a
			if not order_by in ['node', 'apprank']:
				print(order_by)
				print('Bad order-by: valid values are node, apprank')
				return 1
		elif is_number_option(o):
			cols.append(o[2:])
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
	extrankNode = {}
	extrankApprank = {}
	gn = {}
	maxApprank = 0
	cpusOnNode = None

	mapfiles = [f for f in os.listdir(hybrid_dir) if f.startswith('map')]
	for mapfile in mapfiles:
		mapfilename = hybrid_dir + '/' + mapfile
		with open(mapfilename, 'r') as f:
			extrank = read_map_entry('externalRank', f.readline(), mapfilename)
			apprankNum = read_map_entry('apprankNum', f.readline(), mapfilename)
			internalRank = read_map_entry('internalRank', f.readline(), mapfilename)
			nodeNum = read_map_entry('nodeNum', f.readline(), mapfilename)
			_ = read_map_entry('indexThisNode', f.readline(), mapfilename)
			myCpusOnNode = read_map_entry('cpusOnNode', f.readline(), mapfilename)
			if cpusOnNode is None:
				cpusOnNode = myCpusOnNode
			elif cpusOnNode != myCpusOnNode:
				print('Inconsistent cpusOnNode')
				return 1

		if not nodeNum in extranksOnNode:
			extranksOnNode[nodeNum] = []
		extranksOnNode[nodeNum].append(extrank)
		extranks.append(extrank)
		extrankNode[extrank] = nodeNum
		extrankApprank[extrank] = apprankNum
		assert not (apprankNum, nodeNum) in gn
		gn[(apprankNum, nodeNum)] = extrank
		maxApprank = max(maxApprank, apprankNum+1)

	numNodes = max(extranksOnNode.keys()) + 1

	files = {}
	for extrank in extranks:
		files[extrank] = hybrid_dir + '/utilization%d' % extrank

	if order_by == 'node':
		if not show_appranks is None:
			print('Cannot use --appranks with --order-by node\n')
			return 1
		if show_nodes is None:
			show_nodes = range(0,numNodes)
		else:
			for n in show_nodes:
				if n < 0 or n >= numNodes:
					print('Node %d in --nodes is invalid\n', n)
					return 1
		extranks_pr = [  [gn[(apprank,node)] for apprank in range(0,maxApprank) if (apprank,node) in gn] for node in show_nodes ]
	elif order_by == 'apprank':
		if not show_nodes is None:
			print('Cannot use --nodes with --order-by apprank\n')
			return 1
		if show_appranks is None:
			show_appranks = range(0,maxApprank)
		else:
			for a in show_appranks:
				if a < 0 or a >= maxApprank:
					print('Apprank %a in --appranks is invalid\n', a)
					return 1
		extranks_pr = [  [gn[(apprank,node)] for node in range(0,numNodes) if (apprank,node) in gn] for apprank in show_appranks ]
	else:
		assert false

	if barchart is None:
		width_per_extrank = sum([fmt_width[col]+1 for col in cols])+1
		# Header line 1
		if print_timestamp:
			print('%5s ' % '', end='')
		for k,extranks1 in enumerate(extranks_pr):
			if order_by == 'node':
				desc = 'Node %d' % k
			else:
				desc = 'Apprank %d' % k
			total_width = width_per_extrank * len(extranks1)
			print( desc.center(total_width) + ' | ', end = ' ')
		print()
		# Header line 2
		if print_timestamp:
			print('%5s ' % '', end='')
		for k,extranks1 in enumerate(extranks_pr):
			for extrank in extranks1:
				if order_by == 'node':
					desc = 'a%d' % extrankApprank[extrank]
				else:
					desc = 'n%d' % extrankNode[extrank]
				print( desc.center(width_per_extrank), end = '')
			print(' | ', end = ' ')
		print()
	else:
		screenwidth = os.get_terminal_size().columns
		width_per_node = int((screenwidth-6) / numNodes) - 3
		if print_timestamp:
			print('%5s ' % '', end='')
		for node in range(0, numNodes):
			desc = 'Node %d' % node
			print( desc.center(width_per_node+1) + ' |', end='') 
		print()

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
				if readlogs[extrank].done:
					done = True
					break
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
				values[extrank]['apprankbusy'] = int(s[7])
				values[extrank]['immovable'] = int(s[8])
				values[extrank]['requests'] = int(s[9])
				values[extrank]['requestacks'] = int(s[10])
				values[extrank]['owned'] = int(s[11])
				values[extrank]['lent'] = int(s[12])
				values[extrank]['borrowed'] = int(s[13])
				# Collect all other fields in numbered field for debug
				idx = 14
				while len(s) >= idx+1:
					values[extrank][str(idx)] = float(s[idx])
					idx += 1

		curr_timestamp += 0.5

		if (linenum % subsample) != 0:
			continue

		if num_valid > 0:
			if print_timestamp:
				print('%5.1f ' % curr_timestamp, end='')

			for extranks1 in extranks_pr:
				if not barchart is None:
					bar = make_barchart(values, extranks1, barchart, width_per_node, extrankApprank)
					print(bar, ' |', end='')
				else:
					for extrank in extranks1:
						#print '%2d %4.1f ' % (local_alloc[extrank], busy[extrank]),
						if extrank in values:
							for col in cols:
								print(format_value(values[extrank], col), end=' ')
						else:
							for col in cols:
								print(no_value(col), end=' ')
						print(' ', end='')
					print(' |  ', end='')
			print()

	print()
	print('Legend:')
	if barchart is None:
		for k,col in enumerate(cols):
			desc = '%2d. %s' % (k, fmt_desc[col])
			print(colour_value(desc, col))
	else:
		maxApprankNum = apprankDigit(maxApprank - 1)
		print(f'  {barchart}: number is apprank number from 0 to {maxApprankNum}')

		

			
if __name__ == '__main__':
	sys.exit(main(sys.argv))


