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
	print('.all.py <options>  <num_nodes> <cmd> <args...>')
	print('where:')
	print(' -h                      Show this help')
	print(' --vranks                Number of vranks')
	print(' --degree d              Set degree')
	print(' --local                 Use local policy (and enable hybrid)')
	print(' --global                Use global policy (and enable hybrid)')
	print(' --no-dlb                Do not use DLB (must not have hybrid enabled)')
	print(' --no-rebalance          No rebalance policy')
	print(' --local-period          cluster.hybrid.local_time_period for local policy')
	print(' --instrumentation       Set instrumentation, e.g. extrae, verbose or stats')
	print(' --extrae-as-threads     Set instrument.extrae.as_threads=true (default)')
	print(' --no-extrae-as-threads  Unset instrument.extrae.as_threads=false')
	print(' --debug true/false      Enable or disable debug mode')
	print(' --trace-suffix s        Suffix for trace directory and filename')
	print(' --continue-after-error  To try to find more errors')
	print(' --enable-drom val       Enable or disable DROM (val=true/false)')
	print(' --enable-lewi val       Enable or disable LeWI (val=true/false)')
	print(' --config-override s     Strings to put in config override')
	print('Options forwarded to rebalance.py:')
	print('\n'.join([' --%s' % name for (name,has_arg,shortname) in runexperiment.rebalance_forwarded_opts]))
	return 1

def getTrueOrFalse(s):
	if s == 'true':
		return True
	elif s == 'false':
		return False
	else:
		print('Bad true or false value ', s)
		sys.exit(1)

# Run experiments
def main(argv):

	degree = 1
	vranks = None
	continue_after_error = False
	policy = None
	extrae_as_threads = False

	# Sensible initial value
	runexperiment.set_param('local_period', 150)
	rebalance_arg_values = {'monitor' : 150}

	try:
		rebalance_getopt = [ name + ('=' if has_arg else '') for (name, has_arg, value) in runexperiment.rebalance_forwarded_opts ]

		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'degree=', 'vranks=',
										  'local', 'global', 'extrae', 'verbose', 'instrumentation=',
										  'extrae-preload', 'extrae-as-threads',
										  'no-extrae-as-threads', 'no-rebalance',
										  'continue-after-error', 'no-dlb',
										  'local-period=', 'trace-suffix=', 'debug=',
										  'enable-drom=', 'enable-lewi=', 'config-override='] + rebalance_getopt)

	except getopt.error as msg:
		print(msg)
		print('for help use --help')
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()
		elif o == '--degree':
			degree = int(a)
		elif o == '--vranks':
			vranks = int(a)
		elif o == '--local':
			if not policy is None:
				print('Do not specify more than one policy')
				return 1
			policy = 'local'
		elif o == '--global':
			if not policy is None:
				print('Do not specify more than one policy')
				return 1
			policy = 'global'
		elif o == '--no-rebalance':
			if not policy is None:
				print('Do not specify more than one policy')
				return 1
			policy = 'no-rebalance'
		elif o == '--extrae':
			assert runexperiment.params['instrumentation'] is None
			runexperiment.set_param('instrumentation', 'extrae')
		elif o == '--verbose':
			assert runexperiment.params['instrumentation'] is None
			runexperiment.set_param('instrumentation', 'verbose')
		elif o == '--instrumentation':
			assert runexperiment.params['instrumentation'] is None
			runexperiment.set_param('instrumentation', a)
		elif o == '--extrae-preload':
			runexperiment.set_param('extrae_preload', True)
		elif o == '--extrae-as-threads':
			extrae_as_threads = True
		elif o == '--no-extrae-as-threads':
			extrae_as_threads = False
		elif o == '--continue-after-error':
			continue_after_error = True
		elif o == '--no-dlb':
			runexperiment.params['use_dlb'] = False
		elif o == '--local-period':
			runexperiment.set_param('local_period', int(a))
		elif o == '--trace-suffix':
			runexperiment.set_param('trace_suffix', a)
		elif o == '--debug':
			runexperiment.set_param('debug', getTrueOrFalse(a))
		elif o == '--enable-drom':
			runexperiment.set_param('enable_drom', getTrueOrFalse(a))
		elif o == '--enable-lewi':
			runexperiment.set_param('enable_lewi', getTrueOrFalse(a))
		elif o == '--config-override':
			runexperiment.set_param('config_override', a)
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

	if policy is None:
		runexperiment.set_param('use_hybrid', False)
	else:
		runexperiment.set_param('use_hybrid', True)

	if runexperiment.params['use_dlb'] is False:
		if runexperiment.params['use_hybrid'] == True:
			print('Cannot disable DLB in hybrid version')
			return 1

	if len(args) < 2:
		return Usage()
	nodes = int(args[0])
	if vranks is None:
		vranks = nodes

	runexperiment.init(' '.join(args[1:]), rebalance_arg_values)
	
	if runexperiment.params['use_dlb'] is True:
		desc = topologies.get_topology(nodes, degree, vranks)
	else:
		desc = ''

	runexperiment.set_param('policy', policy)
	runexperiment.set_param('extrae_as_threads', extrae_as_threads)

	retval = runexperiment.run_experiment(nodes, degree, vranks, desc)
	if retval != 0 and (not continue_after_error):
		return 1

	time.sleep(1)
	while os.path.exists('.kill'):
		time.sleep(1)

	runexperiment.shutdown()
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
