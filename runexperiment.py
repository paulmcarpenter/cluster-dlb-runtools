import sys
import os
import re
import time

global tracedir_opts

# Options to rebalance.py that should be forwarded. The order matters for packing arguments
#                             Option        has    Short 
#                                           arg    (for trace)    
rebalance_forwarded_opts = [ ('wait',       True,  'w',  ),
							 ('monitor',    True,  'm'),
							 ('no-fill',    False, 'no-fill'),
							 ('equal',      False, 'equal'),
							 ('min-master', True,  'M'),
							 ('min-slave',  True,  'S'),
							 ('loads',      True,  'L') ]

params = {'use_dlb' : True,
          'instrumentation' : None,
          'trace_location' : '/gpfs/scratch/bsc28/bsc28600/work/20200903_nanos6-cluster/traces',
          'local_period' : None,
          'extrae_preload' : False,
		  'policy' : None,
		  'extrae_as_threads' : True,
		  'trace_suffix' : '',
          #'debug' : 'debug'}
          'debug' : ''}


def set_param(name, value):
	assert name in params.keys()
	params[name] = value


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
        trace_suffix = params['trace_suffix']
        if len(trace_suffix) >= 1 and trace_suffix[0] != '-':
            trace_suffix = '-' + trace_suffix
	global tracedir_opts

	return 'trace-%s-%s-%s%s%s-%s' % (cmd2, desc2, policy, tracedir_opts, trace_suffix, str(os.getpid()))


def init(cmd, rebalance_arg_values):

	if params['use_dlb']:
		os.environ['NANOS6_ENABLE_DLB'] = '1'
	else:
		os.environ['NANOS6_ENABLE_DLB'] = '0'

	if params['extrae_preload'] and params['instrumentation'] == 'extrae':
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
	params['cmd'] = cmd
	params['rebalance_arg_values'] = rebalance_arg_values


def shutdown():
	if params['extrae_preload'] and params['instrumentation'] == 'extrae':
		do_cmd('rm ' + extrae_preload_sh)


def run_experiment(nodes, deg, desc):
	global tracedir_opts
	cmd = params['cmd']
	policy = params['policy']
	extrae_as_threads = params['extrae_as_threads']


	# Tracedir and rebalance options
	rebalance_opts = ''
	tracedir_opts = ''
	if policy == 'local':
		if not params['local_period'] is None:
			# Relevant for local
			tracedir_opts += '-%d' % params['local_period']
	else:
		# Relevant for global
		rebalance_arg_values = params['rebalance_arg_values']
		for (arg,has_opt,shortname) in rebalance_forwarded_opts:
			if arg in rebalance_arg_values:
				if has_opt:
					rebalance_opts += '--%s %s ' % (arg, rebalance_arg_values[arg])
					tracedir_opts += '-%s%s' % (arg, rebalance_arg_values[arg])
				else:
					rebalance_opts += '--%s '
					tracedir_opts += '-%s'

	# Clean DLB
	if params['use_dlb']:
		do_cmd('mpirun -np %d dlb_shm -d' % nodes)


	
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

	if params['instrumentation'] == 'extrae':
		do_cmd('rm -rf set-0/ TRACE.mpits')

	# Run experiment
	s = 'NANOS6_CLUSTER_SPLIT="%s" ' % desc
	s += 'NANOS6_CLUSTER_HYBRID_POLICY="%s" ' % hybrid_policy
	s += 'MV2_ENABLE_AFFINITY=0 '

	debug = params['debug']
	if not params['instrumentation'] is None:
		if debug != '':
			debug = '-' + debug
		s = s + 'NANOS6=%s%s ' % (params['instrumentation'], debug)
	else:
		s = s + 'NANOS6=%s ' % debug

	if params['instrumentation']== 'extrae' and params['extrae_preload']:
	 	s = s + 'EXTRAE_ON=1 '

	if extrae_as_threads:
		s = s + 'NANOS6_EXTRAE_AS_THREADS=1 '
	else:
		if 'NANOS6_EXTRAE_AS_THREADS' in os.environ.keys():
			del os.environ['NANOS6_EXTRAE_AS_THREADS']
	if params['local_period'] is not None:
		s = s + 'NANOS6_LOCAL_TIME_PERIOD=%d ' % params['local_period']
	else:
		if 'NANOS6_LOCAL_TIME_PERIOD' in os.environ.keys():
			del os.environ['NANOS6_LOCAL_TIME_PERIOD']
	s += 'mpirun -np %d %s ' % (nodes*deg, cmd)
	retval = do_cmd(s)

	if retval != 0:
		return retval

	if rebalance:
		do_cmd('touch .kill')
	if params['instrumentation'] == 'extrae':
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
		tracedir = params['trace_location'] + '/' + tracefname
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
