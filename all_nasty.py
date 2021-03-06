#! /usr/bin/env python

# Script to run large number of random tests generated using nasty.py
#
# Usage: ./all_nasty.py <num_nodes>
#
# where <num_nodes> is the maximum number of MPI processes to create,
# which is reflected in the maximum value for the node(..) clause.

import os
import sys
import random
import subprocess
import getopt

vranks = None
degree = None
use_dlb = False
max_num_nodes = None
use_asan = False
dlb_nodes = False

testgen_opts_noarg = ['no-hash', 'no-taskwait', 'no-taskwaiton', 'no-taskwaitnoflush', 'no-wait-clause']
runhybrid_opts_noarg = ['local', 'global', 'no-dlb', 'no-rebalance']
runhybrid_opts_arg = ['local-period', 'enable-drom', 'enable-lewi', 'config-override', 'debug']

def Usage():
	print('all_nasty.py <options> <num_nodes>')
	print('where:')
	print(' -h                      Show this help')
	print('--asan                   Build with ASan')
	print(' --continue-after-error  To try to find more errors')
	print(' --max-tasks t           Maximum number of tasks')
	print(' --iterations n          Number of tests')
	print(' --vranks v              Enable cluster+DLB and set number of vranks')
	print(' --degree d              Enable cluster+DLB and set degree')
	print('Arguments passed to ompss-2-testgen:')
	for o in testgen_opts_noarg:
		print(' --%s' % o)
	print('Arguments passed to runhybrid:')
	for o in runhybrid_opts_noarg + runhybrid_opts_arg:
		print(' --%s' % o)
	return 1


# Iterate over all combinations of the arguments in order
def iterate_args(args):
	# Take first arg
	assert len(args) >= 1
	a = args[0][0]	# Option
	os = args[0][1] # Values
	if os is None:
		# Bare option
		opt_vals = [ [a] ]
	else:
		if a == '--nodes':
			global max_num_nodes
			opt_vals = [ [a, str(o)]  for o in os if o <= max_num_nodes]
		else:
			opt_vals = [ [a, str(o)]  for o in os]

	if len(args) == 1:
		# Last option: yield all the values separately
		for opt_val in opt_vals:
			yield opt_val
	else:
		rest_vals = iterate_args(args[1:])
		for r in rest_vals:
			for opt_val in opt_vals:
				yield opt_val + r

# Iterate over all combinations of the arguments in random order
def random_iterate_args(args):
	all_args = list(iterate_args(args))
	random.shuffle(all_args)
	return all_args
	
		
def get_nodes(args):
	for j,a in enumerate(args):
		if a == '--nodes':
			assert j < len(args)-1
			return int(args[j+1])
	assert False # No --nodes argument
		

def generate_compile_and_run(args, nasty_args_fixed, runhybrid_args):

	global use_asan
	global vranks
	global degree

	# Create the test program
	gen_cmd = ['ompss-2-testgen'] + args
	gen_cmd.extend(nasty_args_fixed)

	ret = 1
	with open('nasty.c', 'w') as fout:
		ret = subprocess.call(gen_cmd, stdout=fout)
		if ret != 0:
			subprocess.call(['cat', 'nasty.c'])
	if ret != 0:
		return None

	# Compile the test program
	if use_asan:
		asan_opts = '-fsanitize=address -fno-omit-frame-pointer -ggdb '
	else:
		asan_opts = ''
	build_cmd = 'mcc %s--ompss-2 -o nasty nasty.c' % asan_opts

	print(build_cmd)
	ret = os.system(build_cmd)
	if ret != 0:
		print('Could not build program')
		sys.exit(1)

	if use_dlb:
		# In DLB mode, use the actual number of nodes
		runhybrid_nodes = dlb_nodes
	else:
		# Otherwise use the number of nodes passed to ompss-2-testgen
		runhybrid_nodes = get_nodes(args)
	
	# Now run it
	command = ['runhybrid.py'] + runhybrid_args + [str(runhybrid_nodes), './nasty']
	print(' '.join(command))
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	for line in p.stdout.readlines():
		print(line.decode('utf-8').rstrip())
	for line in p.stderr.readlines():
		print(line.decode('utf-8').rstrip())
	p.stdout.close()
	p.stderr.close()
	sys.stdout.flush()
	ret = p.wait()
	return ret


def main(argv):

	global use_asan
	global vranks
	global degree
	global use_dlb
	global dlb_nodes

	iterations = 100000
	continue_after_error = False
	max_tasks = None
	nasty_args_fixed = []
	runhybrid_args = []

	try:
		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'asan', 'continue-after-error', 'iterations=', 'max-tasks=', 'vranks=', 'degree=']
										 + testgen_opts_noarg
										 + runhybrid_opts_noarg
										 + [o + '=' for o in runhybrid_opts_arg])

	except getopt.error as msg:
		print(msg)
		print("for help use --help")
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage()
		elif o == '--asan':
			use_asan = True
		elif o == '--continue-after-error':
			continue_after_error = True
		elif o == '--iterations':
			iterations = int(a)
		elif o == '--max-tasks':
			max_tasks = int(a)
		elif o == '--vranks':
			vranks = int(a)
		elif o == '--degree':
			degree = int(a)
		elif len(o) > 2 and o[2:] in testgen_opts_noarg:
			nasty_args_fixed.append(o)
		elif len(o) > 2 and o[2:] in runhybrid_opts_noarg:
			runhybrid_args.append(o)
		elif len(o) > 2 and o[2:] in runhybrid_opts_arg:
			runhybrid_args.append(o)
			runhybrid_args.append(a)
		else:
			assert False

	if len(args) != 1:
		return Usage()

	global max_num_nodes
	max_num_nodes = int(args[0])

	if vranks is None:
		runhybrid_args.append('--no-dlb')
		use_dlb = False
	else:
		if degree is None:
			degree = max_num_nodes
		runhybrid_args.extend(['--vranks', str(vranks)])
		runhybrid_args.extend(['--degree', str(degree)])
		dlb_nodes = max_num_nodes
		use_dlb = True

	def get_tasks_list():
		candidates = list(range(30,100,5)) + [200,500,1000]
		if max_tasks is None:
			return candidates
		else:
			if max_tasks > 40:
				return [nt for nt in candidates if nt <= max_tasks]
			else:
				return list(range(1,max_tasks))

	if use_dlb:
		valid_num_nodes = range(1, degree+1)
	else:
		valid_num_nodes = range(1, max_num_nodes+1)

	# All valid combinations of the arguments
	nasty_args = [ ('--nodes', valid_num_nodes),
				   ('--tasks', get_tasks_list() ),
				   ('--nesting', [2,3,4,5,10]),
				   ('--seed', range(1,20) )]

	fail_num = 1
	failures = 0
	total = 0
	nocompiles = 0

	# Do in a random order in case we run out of time
	for k, args in enumerate(random_iterate_args(nasty_args)):
	
		print('Test', k)
		if k >= iterations:
			break

		total += 1
		ret = generate_compile_and_run(args, nasty_args_fixed, runhybrid_args)
		if ret is None:
			# Did not generate or compile: skip rest
			print('Did not generate or compile')
			nocompiles += 1
			if not continue_after_error:
				break
		elif ret != 0:
			print('Experiment failed!')
			failures += 1
			if not continue_after_error:
				break
	
	if failures == 0 and nocompiles == 0:
		print('All tests passed')
	else:
		print('ERROR: ', nocompiles, 'did not compile and', failures, 'failed, of total', total, 'tests')
	
	return 0
			

if __name__ == '__main__':
	sys.exit(main(sys.argv))
