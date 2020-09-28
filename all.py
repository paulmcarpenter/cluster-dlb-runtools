#! /usr/bin/env python
import sys
import random
import os
import time
import getopt
import re

import topologies

use_dlb = True
min_per_node = 0
max_per_node = 1000
instrumentation = None
continue_after_error = False
trace_location = '/gpfs/scratch/bsc28/bsc28600/work/20200903_nanos6-cluster/traces'
local_period = None
extrae_preload = False

rebalance_opts = None
tracedir_opts = None



def find_paraver_file():
	files = os.listdir('.')
	for f in files:
		m = re.match('^(.*)\.prv', f)
		if m:
			return m.group(1)
	return None
		


def do_cmd(s):
	print s
	sys.stdout.flush()
	return os.system(s)

def translate(string, d):
	s = ''
	for ch in string:
		s += d.get(ch, ch)
	return s

def tracedir_name(desc, cmd, policy):
	cmd2 = translate(cmd, {' ': '_', '/' : '_'})
	desc2 = translate(desc, {';': '_'})
	global tracedir_opts

	return 'trace-%s-%s-%s%s-%s' % (cmd2, desc2, policy, tracedir_opts, str(os.getpid()))

def run_experiment(nodes, deg, desc, cmd, policy, extrae_as_threads, rebalance=None):
	global instrumentation
	global rebalance_opts
	
	if rebalance is None:
		if policy == 'global':
			hybrid_policy = 'global'
			rebalance = True
		elif policy == 'local':
			hybrid_policy = 'local'
			rebalance = False
		else:
			assert policy =='no-rebalance'
			hybrid_policy = 'global' # Global policy
			rebalance = False # but don't actually rebalance

	print 'Experiment', 'nodes:', nodes, 'deg:', deg, 'desc:', desc, 'cmd:', cmd, policy, 'rebalance:', rebalance

	rebalance_filename = None
	if rebalance:

		do_cmd('rm -f .kill')
		do_cmd('rm -rf .hybrid')

		rebalance_filename = 'rebalance-out-%d-%d.txt' % (nodes,deg)
		do_cmd('${MERCURIUM}/../rebalance/rebalance.py ' + rebalance_opts + '10000 > ' + rebalance_filename + ' &')
		time.sleep(1)

	if instrumentation == 'extrae':
		do_cmd('rm -rf set-0/ TRACE.mpits')

	# Run experiment
	s = 'NANOS6_CLUSTER_SPLIT="%s" ' % desc
	s += 'NANOS6_CLUSTER_HYBRID_POLICY="%s" ' % hybrid_policy
	s += 'MV2_ENABLE_AFFINITY=0 '

	if not instrumentation is None:
		s = s + 'NANOS6=%s-debug ' % instrumentation
	if instrumentation == 'extrae' and extrae_preload:
	 	s = s + 'EXTRAE_ON=1 '

	if extrae_as_threads:
		s = s + 'NANOS6_EXTRAE_AS_THREADS=1 '
	else:
		if 'NANOS6_EXTRAE_AS_THREADS' in os.environ.keys():
			del os.environ['NANOS6_EXTRAE_AS_THREADS']
	if local_period is not None:
		s = s + 'NANOS6_LOCAL_TIME_PERIOD=%d ' % local_period
	else:
		if 'NANOS6_LOCAL_TIME_PERIOD' in os.environ.keys():
			del os.environ['NANOS6_LOCAL_TIME_PERIOD']
	s += 'mpirun -np %d %s ' % (nodes*deg, cmd)
	retval = do_cmd(s)

	if retval != 0:
		return retval

	if rebalance:
		do_cmd('touch .kill')
	if instrumentation == 'extrae':
		# Hack to generate TRACE.mpits file
		prefix = ''
		if os.path.exists('create_paraver_trace.py'):
			prefix = './'
		elif os.path.exists('../create_paraver_trace.py'):
			prefix = '../'

		do_cmd(prefix + 'create_paraver_trace.py')
		do_cmd('mpi2prv -f TRACE.mpits')

		# Now move traces to a subdirectory
		tracefname = tracedir_name(desc, cmd, policy)
		tracedir = trace_location + '/' + tracefname
		prvroot = find_paraver_file()
		do_cmd('rm -rf ' + tracedir)
		do_cmd('mkdir -p ' + tracedir)
		do_cmd('mv TRACE.mpits set-0 ' + tracedir)
		do_cmd('mv ' + prvroot + '.prv ' + tracedir + '/' + tracefname + '.prv')
		do_cmd('mv ' + prvroot + '.pcf ' + tracedir + '/' + tracefname + '.pcf')
		do_cmd('mv ' + prvroot + '.row ' + tracedir + '/' + tracefname + '.row')
		do_cmd('mv .hybrid/ ' + tracedir)
		if not rebalance_filename is None:
			do_cmd('mv ' + rebalance_filename + ' ' + tracedir)

	return 0

# Options to rebalance.py that are forwarded. The order matters for packing arguments
#                             Option        has    Short 
#                                           arg    (for trace)    
rebalance_forwarded_opts = [ ('wait',       True,  'w',  ),
							 ('monitor',    True,  'm'),
							 ('no-fill',    False, 'no-fill'),
							 ('equal',      False, 'equal'),
							 ('min-master', True,  'M'),
							 ('min-slave',  True,  'S'),
							 ('loads',      True,  'L') ]

def Usage():
	print '.all.py <options>  <num_nodes> <cmd> <args...>'
	print 'where:'
	print ' -h                      Show this help'
	print ' --min-per-node d        Minimum degree'
	print ' --max-per-node d        Maximum degree'
	print ' --local-period          NANOS6_LOCAL_TIME_PERIOD for local policy'
	print ' --extrae                Generate extrae trace'
	print ' --verbose               Generate verbose trace'
	print ' --extrae-as-threads     Set NANOS6_EXTRAE_AS_THREADS=1 (default)'
	print ' --no-extrae-as-threads  Unset NANOS6_EXTRAE_AS_THREADS'
	print 'Options forwarded to rebalance.py:'
	print '\n'.join([' --%s' % name for (name,has_arg,shortname) in rebalance_forwarded_opts])
	return 1


# Run experiments
def main(argv):

	global min_per_node
	global max_per_node
	global instrumentation
	global continue_after_error
	global use_dlb
	global local_period
	global rebalance_opts
	global tracedir_opts
	global extrae_preload
	global extrae_preload_file
	os.environ['NANOS6_ENABLE_DLB'] = '1'
	policies = []
	threads = []

	rebalance_arg_values = {}

	try:
		rebalance_getopt = [ name + ('=' if has_arg else '') for (name, has_arg, value) in rebalance_forwarded_opts ]
		print rebalance_getopt

		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'min-per-node=',
									      'max-per-node=', 'local',
										  'global', 'extrae', 'verbose', 'extrae-preload', 'extrae-as-threads',
										  'no-extrae-as-threads', 'no-rebalance',
										  'continue-after-error', 'no-dlb',
										  'local-period='] + rebalance_getopt )

	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()
		elif o == '--min-per-node':
			min_per_node = int(a)
		elif o == '--max-per-node':
			max_per_node = int(a)
		elif o == '--local':
			if not 'local' in policies:
				policies.append('local')
		elif o == '--global':
			if not 'global' in policies:
				policies.append('global')
		elif o == '--no-rebalance':
			policies.append('no-rebalance')
		elif o == '--extrae':
			assert instrumentation is None
			instrumentation = 'extrae'
		elif o == '--verbose':
			assert instrumentation is None
			instrumentation = 'verbose'
		elif o == '--extrae-preload':
			extrae_preload = True
		elif o == '--extrae-as-threads':
			if not True in threads:
				threads.append(True)
		elif o == '--no-extrae-as-threads':
			print '** --no-extrae-as-threads does work well'
			sys.exit(1)
			if not False in threads:
				threads.append(False)
		elif o == '--continue-after-error':
			continue_after_error = True
		elif o == '--no-dlb':
			use_dlb = False
			os.environ['NANOS6_ENABLE_DLB'] = '0'
		elif o == '--local-period':
			local_period = int(a)
		else:
			print o
			try:
				options = ['--' + name for (name, has_arg, shortname) in rebalance_forwarded_opts]
				index = options.index(o)
				name, has_arg, shortname = rebalance_forwarded_opts[index]
				if has_arg:
					rebalance_arg_values[name] = a
				else:
					rebalance_arg_values[name] = True

				print 'forwarded', o
			except ValueError: assert False # Should not get here as getopt already checked options were valid

	# Default
	if threads == []:
		threads = [True]
	if policies == []:
		policies = ['global', 'local']

	assert len(args) >= 2
	num_nodes = int(args[0])
	cmd = ' '.join(args[1:])

	if extrae_preload and instrumentation == 'extrae':
		if not 'EXTRAE_HOME' in os.environ:
			print 'EXTRAE_HOME needs to be set to use --extrae-preload'
			return 1
		cmd2 = translate(cmd, {' ': '_', '/' : '_'})
		extrae_preload_sh = 'preload-%s-%d' % (cmd2, os.getpid())
		fp = open(extrae_preload_sh, 'w')
		extrae_library = '%s/lib/libnanosmpitrace.so' % os.environ['EXTRAE_HOME']
		print >> fp, 'LD_PRELOAD=%s %s' % (extrae_library, cmd)
		fp.close()
		do_cmd('cat ' + extrae_preload_sh)
		cmd = 'sh ' + extrae_preload_sh
	

	do_cmd('pwd')

	for (nodes,deg), desc in sorted(topologies.splits.items()):
		if nodes == num_nodes:
			if deg >= min_per_node and deg <= max_per_node:

				for policy in policies:
					for extrae_as_threads in threads:

						# Tracedir and rebalance options
						rebalance_opts = ''
						tracedir_opts = ''
						if policy == 'local':
							if not local_period is None:
								# Relevant for local
								tracedir_opts += '-%d' % local_period
						else:
							# Relevant for global
							for (arg,has_opt,shortname) in rebalance_forwarded_opts:
								if arg in rebalance_arg_values:
									if has_opt:
										rebalance_opts += '--%s %s ' % (arg, rebalance_arg_values[arg])
										tracedir_opts += '-%s%s' % (arg, rebalance_arg_values[arg])
									else:
										rebalance_opts += '--%s '
										tracedir_opts += '-%s'

						# Clean DLB
						do_cmd('mpirun -np %d dlb_shm -d' % num_nodes)

						retval = run_experiment(nodes, deg, desc, cmd, policy, extrae_as_threads)
						if retval != 0 and (not continue_after_error):
							return 1

						time.sleep(1)
						while os.path.exists('.kill'):
							time.sleep(1)

	if extrae_preload and instrumentation == 'extrae':
		do_cmd('rm ' + extrae_preload_sh)
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
