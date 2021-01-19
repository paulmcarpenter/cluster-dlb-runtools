#! /usr/bin/env python
import sys
import getopt

def Usage():
	print("""trace_stats.py <options> <prv_file>
where:
	-h              Show this help
""")
	return 1

counts = {}

def inc(k):
	counts[k] = 1 + counts.get(k, 0)

def summarize():
	total = sum([c for (k,c) in counts.items()])
	evs = reversed(sorted([(c,k) for (k,c) in counts.items()]))
	for c,k in evs:
		print('%4.1f%% %d %s' % (c*100.0 / total, c,k))

def main(argv):
	try:
		opts, args = getopt.getopt( argv[1:],
									'h', ['help'])

	except getopt.error as msg:
		print(msg)
		print('for help use --help')
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()

	fp = open(sys.argv[1])
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

	summarize()
	fp.close()
	return 1


if __name__ == '__main__':
	sys.exit(main(sys.argv))
