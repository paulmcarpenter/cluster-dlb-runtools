#! /usr/bin/env python
import sys

counts = {}

def inc(k):
	counts[k] = 1 + counts.get(k, 0)

def summarize():
	total = sum([c for (k,c) in counts.items()])
	evs = reversed(sorted([(c,k) for (k,c) in counts.items()]))
	for c,k in evs:
		print '%4.1f%% %d %s' % (c*100.0 / total, c,k)

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
				inc('Event ' + s[0] + ':' + s[1])
			else:
				inc('Event ' + s[0])
			s = s[2:]
	elif line.startswith('3'):
		inc('Comm ')

summarize()
fp.close()
