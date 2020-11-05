#! /usr/bin/env python
import sys
import os

tasks = [3,4]

infile = 'tmp.prv'
outfile = 'tmp.cut.prv'

ifp = open(infile)
ofp = open(outfile, 'w')

print >> ofp, ifp.readline().strip()

for line in ifp.readlines():
	s = line.split(':')
	typ = int(s[0])
	keep = True
	if typ == 1:
		# State record 1:cpu_id:appl_id:task_id:thread_id:begin_time:end_time:state
		task_id = int(s[3])
		if not task_id in tasks:
			keep = False
	elif typ == 2:
		# Event record 2:cpu_id:appl_id:task_id:thread_id:time{:event_type:event_value}+
		task_id = int(s[3])
		if not task_id in tasks:
			keep = False
	elif typ == 3:
		# Communication record 3:object_send:lsend:psend:object_recv:lrecv:precv:size:tag
		# object: cpu_send_id:ptask_send_id:task_send_id:thread_send_id
		task_send_id = int(s[3])
		task_recv_id = int(s[9])
		if (not task_send_id in tasks) or (not task_recv_id in tasks):
			keep = False
	if keep:
		print >> ofp, line.strip()
ifp.close()
ofp.close()




