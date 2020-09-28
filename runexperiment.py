
params = {'use_dlb' : True,
          'instrumentation' : None,
          'trace_location' : '/gpfs/scratch/bsc28/bsc28600/work/20200903_nanos6-cluster/traces',
          'local_period' : None,
          'extrae_preload' : False,
		  'policy' : None,
		  'extrae_as_threads' : True,
		  'rebalance_opts' : None,
		  'tracedir_opts' : None}

def set_param(name, value):
	assert name in params.keys()
	params[name] = value
