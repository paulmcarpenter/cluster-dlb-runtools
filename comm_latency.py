#! /usr/bin/env python
import sys

message_names = [
	'SYS_FINISH',
	'DATA_RAW',
	'DMALLOC',
	'DFREE',
	'DATA_FETCH',
	'DATA_SEND',
	'TASK_NEW',
	'TASK_FINISHED',
	'SATISFIABILITY',
	'RELEASE_ACCESS' ]

counts = {}

def inc(k):
	counts[k] = 1 + counts.get(k, 0)

def summarize():
	total = sum([c for (k,c) in counts.items()])
	evs = reversed(sorted([(c,k) for (k,c) in counts.items()]))
	for c,k in evs:
		print('%4.1f%% %d %s' % (c*100.0 / total, c,k))

tots = {}
nums = {}
maxs = {}

fp = open(sys.argv[1])
for k,line in enumerate(fp):
	if k % 1000000 == 0:
		summarize()
	if line.startswith('3'):
		s = line.split(':')
		assert len(s) == 15
		if int(s[14]) == 9700000:
			# Cluster MPI message
			message_type = int(s[13])
			latency = float(s[11]) - float(s[5])
			maxs[message_type] = max(latency, maxs.get(message_type,0))
			tots[message_type] = latency + tots.get(message_type,0)
			nums[message_type] = 1 + nums.get(message_type,0)

summarize()
fp.close()

for k,name in enumerate(message_names):
	if k in nums:
		print('%-16s avg = %.2f ms max = %.2f ms' % \
				(name, 1.0 * tots[k] / nums[k] / 1e6, 1.0 * maxs[k] / 1e6))
	else:
		print('%-16s none' % name)
		

