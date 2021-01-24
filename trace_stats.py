#! /usr/bin/env python
import sys
import getopt

def Usage():
	print("""trace_stats.py <options> <prv_file>
where:
	-h              Show this help
	--event type    Show statistics for a particular event type
""")
	return 1

counts = {}

def inc(k):
	counts[k] = 1 + counts.get(k, 0)

def summarize():
	total = sum([c for (k,c) in counts.items()])
	evs = reversed(sorted([(c,k) for (k,c) in counts.items()]))
	for c,k in evs:
		print('%4.1f%% %6d  %s' % (c*100.0 / total, c,k))

def main(argv):
	event_type = None
	try:
		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'event='])

	except getopt.error as msg:
		print(msg)
		print('for help use --help')
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()
		elif o == '--event':
			event_type = int(a)
		else:
			assert False

	if len(args) == 0:
		return Usage()
	fp = open(args[0])

	if event_type is None:
		# Table of event types
		for k,line in enumerate(fp):
			if k % 1000000 == 0:
				summarize()
			if line.startswith('1'):
				inc('State ')
			elif line.startswith('2'):
				s = line.split(':')
				s = s[6:]
				while len(s) >= 2:
					if s[0] == '9000000':
						inc('Event ' + s[0] + ':' + s[1].rstrip())
					inc('Event ' + s[0])
					s = s[2:]
			elif line.startswith('3'):
				inc('Comm ')
	else:
		# Table of event values for given type
		for k,line in enumerate(fp):
			if k % 1000000 == 0:
				summarize()
			if line.startswith('2'):
				s = line.split(':')
				s = s[6:]
				while len(s) >= 2:
					if int(s[0]) == event_type:
						inc('Event ' + s[0] + ':' + s[1].rstrip())
					s = s[2:]

	summarize()
	fp.close()
	return 1


if __name__ == '__main__':
	sys.exit(main(sys.argv))
