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
	print ' --min-degree d          Minimum degree'
	print ' --max-degree d          Maximum degree'
	print ' --local-period          NANOS6_LOCAL_TIME_PERIOD for local policy'
	print ' --extrae                Generate extrae trace'
	print ' --verbose               Generate verbose trace'
	print ' --extrae-as-threads     Set NANOS6_EXTRAE_AS_THREADS=1 (default)'
	print ' --no-extrae-as-threads  Unset NANOS6_EXTRAE_AS_THREADS'
	print ' --nanos6=               Nanos6 library'
	print ' --trace-suffix s        Suffix for trace directory and filename'
	print 'Options forwarded to rebalance.py:'
	print '\n'.join([' --%s' % name for (name,has_arg,shortname) in runexperiment.rebalance_forwarded_opts])
	return 1


# Run experiments
def main(argv):

	min_degree = 1
	max_degree = 3
	continue_after_error = False
	policies = []
	threads = []

	rebalance_arg_values = {}

	try:
		rebalance_getopt = [ name + ('=' if has_arg else '') for (name, has_arg, value) in runexperiment.rebalance_forwarded_opts ]
		print rebalance_getopt

		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'min-per-node=',
									      'max-per-node=', 'min-degree=', 'max-degree', 'local',
										  'global', 'extrae', 'verbose', 'extrae-preload', 'extrae-as-threads',
										  'no-extrae-as-threads', 'no-rebalance',
										  'continue-after-error', 'no-dlb',
										  'local-period=', 'trace-suffix=', 'nanos6='] + rebalance_getopt)

	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()
		elif o == '--min-per-node' or o == '--max-per-node':
			print 'Deprecated --min-per-node and --max-per-node: use --min-degree or --max-degree'
			return Usage()
		elif o == '--min-degree':
			min_degree = int(a)
		elif o == '--max-degree':
			max_degree = int(a)
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
		elif o == '--local-period':
			runexperiment.set_param('local_period', int(a))
		elif o == '--trace-suffix':
			runexperiment.set_param('trace_suffix', a)
		elif o == '--nanos6':
			runexperiment.set_param('debug', a)
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

	runexperiment.init(' '.join(args[1:]), rebalance_arg_values)
	
	runexperiment.do_cmd('pwd')

	for (nodes,deg), desc in sorted(topologies.splits.items()):
		if nodes == num_nodes:
			if deg >= min_degree and deg <= max_degree:

				for policy in policies:
					runexperiment.set_param('policy', policy)
					for extrae_as_threads in threads:
						runexperiment.set_param('extrae_as_threads', extrae_as_threads)


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
