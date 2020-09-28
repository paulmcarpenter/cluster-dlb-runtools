#! /usr/bin/env python
import sys
import random
import os
import time
import getopt
import re

import topologies
import runexperiment


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
	print '\n'.join([' --%s' % name for (name,has_arg,shortname) in runexperiment.rebalance_forwarded_opts])
	return 1


# Run experiments
def main(argv):

	global min_per_node
	global max_per_node
	global continue_after_error
	global extrae_preload_file
	os.environ['NANOS6_ENABLE_DLB'] = '1'
	policies = []
	threads = []

	rebalance_arg_values = {}

	try:
		rebalance_getopt = [ name + ('=' if has_arg else '') for (name, has_arg, value) in runexperiment.rebalance_forwarded_opts ]
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
			print 'max-per-node done'
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
			assert runexperiment.params['instrumentation'] is None
			runexperiment.set_param('instrumentation', 'extrae')
		elif o == '--verbose':
			assert runexperiment.params['instrumentation'] is None
			runexperiment.set_param('instrumentation', 'verbose')
		elif o == '--extrae-preload':
			runexperiment.set_param('extrae_preload', True)
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
			runexperiment.params['use_dlb'] = False
			os.environ['NANOS6_ENABLE_DLB'] = '0'
		elif o == '--local-period':
			runexperiment.set_param('local_period', int(a))
		else:
			try:
				options = ['--' + name for (name, has_arg, shortname) in runexperiment.rebalance_forwarded_opts]
				index = options.index(o)
				name, has_arg, shortname = runexperiment.rebalance_forwarded_opts[index]
				if has_arg:
					rebalance_arg_values[name] = a
				else:
					rebalance_arg_values[name] = True

			except ValueError:
				assert False # Should not get here as getopt already checked options were valid

	# Default
	if threads == []:
		threads = [True]
	if policies == []:
		policies = ['global', 'local']

	assert len(args) >= 2
	num_nodes = int(args[0])

	runexperiment.init(' '.join(args[1:]))
	
	runexperiment.do_cmd('pwd')

	for (nodes,deg), desc in sorted(topologies.splits.items()):
		if nodes == num_nodes:
			if deg >= min_per_node and deg <= max_per_node:

				for policy in policies:
					runexperiment.set_param('policy', policy)
					for extrae_as_threads in threads:
						runexperiment.set_param('extrae_as_threads', extrae_as_threads)

						# Tracedir and rebalance options
						rebalance_opts = ''
						tracedir_opts = ''
						if policy == 'local':
							if not runexperiment.params['local_period'] is None:
								# Relevant for local
								tracedir_opts += '-%d' % runexperiment.params['local_period']
						else:
							# Relevant for global
							for (arg,has_opt,shortname) in runexperiment.rebalance_forwarded_opts:
								if arg in rebalance_arg_values:
									if has_opt:
										rebalance_opts += '--%s %s ' % (arg, rebalance_arg_values[arg])
										tracedir_opts += '-%s%s' % (arg, rebalance_arg_values[arg])
									else:
										rebalance_opts += '--%s '
										tracedir_opts += '-%s'
						runexperiment.set_param('rebalance_opts', rebalance_opts)
						runexperiment.set_param('tracedir_opts', tracedir_opts)

						# Clean DLB
						runexperiment.do_cmd('mpirun -np %d dlb_shm -d' % num_nodes)

						retval = runexperiment.run_experiment(nodes, deg, desc)
						if retval != 0 and (not continue_after_error):
							return 1

						time.sleep(1)
						while os.path.exists('.kill'):
							time.sleep(1)

	runexperiment.shutdown()
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
