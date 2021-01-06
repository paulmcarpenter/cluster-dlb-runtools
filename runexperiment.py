import sys
import os
import re
import time

global tracedir_opts
global extrae_preload_sh

nanos6_override_prefix = {}
extrae_preload_sh = None

def add_override(keyvals, key, value):
	assert not key in keyvals
	keyvals[key] = value

def add_override_prefix(key, value):
	global nanos6_override_prefix
	add_override(nanos6_override_prefix, key, value)

def get_nanos6_override(keyvals):
	items = sorted(keyvals.items())
	return ','.join([ '%s=%s' % (key,value) for (key,value) in items])



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
		  'use_hybrid' : True,
          'instrumentation' : None,
          'trace_location' : '/gpfs/scratch/bsc28/bsc28600/work/20200903_nanos6-cluster/traces',
          'local_period' : None,
          'extrae_preload' : False,
		  'policy' : None,
		  'extrae_as_threads' : True,
		  'trace_suffix' : '',
		  'oversubscribe' : True,
          #'debug' : 'debug'}
          'debug' : True,
		  'enable_drom' : True,
		  'enable_lewi' : True}


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
	print(s)
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

	prefix  = 'trace-%s-%s-%s%s%s' % (cmd2, desc2, policy, tracedir_opts, trace_suffix)

	tracefname    = '%s-%s' % (prefix, str(os.getpid()))
	tracenodename = '%s-node-%s' % (prefix, str(os.getpid()))
	return tracefname, tracenodename


def init(cmd, rebalance_arg_values):

	global extrae_preload_sh
	if params['use_dlb']:
		add_override_prefix('dlb.enabled', 'true')
	else:
		add_override_prefix('dlb.enabled', 'false')

	add_override_prefix('dlb.enable_drom', 'true' if params['enable_drom'] else 'false')
	add_override_prefix('dlb.enable_lewi', 'true' if params['enable_lewi'] else 'false')

	if params['extrae_preload'] and params['instrumentation'] == 'extrae':
		if not 'EXTRAE_HOME' in os.environ:
			print('EXTRAE_HOME needs to be set to use --extrae-preload')
			return 1
		cmd2 = translate(cmd, {' ': '_', '/' : '_'})
		extrae_preload_sh = 'preload-%s-%d' % (cmd2, os.getpid())
		fp = open(extrae_preload_sh, 'w')
		extrae_library = '%s/lib/libnanosmpitrace.so' % os.environ['EXTRAE_HOME']
		print('LD_PRELOAD=%s %s' % (extrae_library, cmd), file = fp)
		fp.close()
		do_cmd('cat ' + extrae_preload_sh)
		cmd = 'sh ' + extrae_preload_sh
	params['cmd'] = cmd
	params['rebalance_arg_values'] = rebalance_arg_values


def shutdown():
	global extrae_preload_sh
	if params['extrae_preload'] and params['instrumentation'] == 'extrae':
		do_cmd('rm ' + extrae_preload_sh)


def run_experiment(nodes, deg, vranks, desc):
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
	elif policy =='no-rebalance':
		hybrid_policy = 'global' # Global policy
		rebalance = False # but don't actually rebalance
	else:
		assert policy is None
		assert not params['use_hybrid']
		hybrid_policy = None
		rebalance = False

	print('Experiment', 'vranks:', vranks, 'nodes:', nodes, 'deg:', deg, 'desc:', desc, 'cmd:', cmd, policy, 'rebalance:', rebalance)

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
	global nanos6_override_prefix
	nanos6_override = nanos6_override_prefix
	s = ''
	runtools_dir = os.path.abspath(os.path.dirname(__file__))
	if params['use_hybrid']:
		add_override(nanos6_override, 'cluster.hybrid.split', desc)
		add_override(nanos6_override, 'cluster.hybrid.policy', hybrid_policy)
		s = s + 'NANOS6_CONFIG=%s/nanos6-hybrid.toml ' % runtools_dir
	else:
		s = s + 'NANOS6_CONFIG=%s/nanos6-no-hybrid.toml ' % runtools_dir

	if params['use_dlb'] or params['oversubscribe']:
		s += 'MV2_ENABLE_AFFINITY=0 '
	else:
		s += 'MV2_ENABLE_AFFINITY=1 '

	debug = params['debug']
	assert debug == True or debug == False
	add_override(nanos6_override, 'version.debug', 'true' if debug else 'false')

	if not params['instrumentation'] is None:
		add_override(nanos6_override, 'version.instrument', instrumentation)
	else:
		add_override(nanos6_override, 'version.instrument', 'none')

	if params['instrumentation']== 'extrae' and params['extrae_preload']:
	 	s = s + 'EXTRAE_ON=1 '

	if extrae_as_threads:
		add_override(nanos6_override, 'instrument.extrae.as_threads', 'true')
	else:
		add_override(nanos6_override, 'instrument.extrae.as_threads', 'false')
	if params['use_hybrid'] and params['local_period'] is not None:
		add_override(nanos6_override, 'cluster.hybrid.local_time_period', params['local_period'])

	s += ' NANOS6_CONFIG_OVERRIDE=\"%s\" ' % get_nanos6_override(nanos6_override)
	
	s += 'mpirun -np %d %s ' % (vranks*deg, cmd)
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
		tracefname, tracenodename = tracedir_name(desc, cmd, policy)
		tracedir = params['trace_location'] + '/' + tracefname
		prvroot = find_paraver_file()
		print('prvroot:', prvroot)
		if prvroot:
			#do_cmd('rm -rf ' + tracedir)
			do_cmd('num_cores ' + prvroot + '.prv ' + prvroot + '-node.prv')
			do_cmd('mkdir -p ' + tracedir)
			do_cmd('mv TRACE.mpits ' + tracedir)
			do_cmd('mv ' + prvroot + '.prv ' + tracedir + '/' + tracefname + '.prv')
			do_cmd('mv ' + prvroot + '.pcf ' + tracedir + '/' + tracefname + '.pcf')
			do_cmd('mv ' + prvroot + '.row ' + tracedir + '/' + tracefname + '.row')
			do_cmd('mv ' + prvroot + '-node.prv ' + tracedir + '/' + tracenodename + '.prv')
			do_cmd('mv ' + prvroot + '-node.pcf ' + tracedir + '/' + tracenodename + '.pcf')
			do_cmd('mv ' + prvroot + '-node.row ' + tracedir + '/' + tracenodename + '.row')
			do_cmd('mv .hybrid/ ' + tracedir)
		do_cmd('rm -rf set-0')

		if not rebalance_filename is None:
			do_cmd('mv ' + rebalance_filename + ' ' + tracedir)

	return 0
