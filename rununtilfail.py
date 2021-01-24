#! /usr/bin/env python
import os
import sys
import random
import copy
import getopt

buffered = False
buffered_filename = 'out-rununtilfail.txt'

def Usage(argv):
	print(argv[0] + """ [options] -- <ompss-2-testgen arguments>
-h, --help         Show this help
--trials           Maximum number of trials 
""")
	return 1

# Execute a command
def command(cmd):
	print(cmd)
	ret = os.system(cmd)
	return ret


def main(argv):

	global use_asan
	trials = 10000
	global ompssgen_args

	initial_control = None
	new = False
	try:
		opts, args = getopt.getopt( argv[1:],
									'h', ['help', 'continue', 'new', 'asan', 'trials='] )

	except getopt.error as msg:
		print(msg)
		print('for help use --help')
		sys.exit(2)
	for o, a in opts:
		if o in ('-h', '--help'):
			return Usage(argv)
		elif o == '--trials':
			trials = int(a)

	if len(args) == 0:
		return Usage(argv)
	
	cmd = ' '.join(args)
	if buffered:
		cmd = cmd + ' > ' + buffered_filename

	# Run number of trials given by --trials (or one) and
	# return True only if they all pass
	for trial in range(0,trials):
		print('Trial', trial)
		ret = command(cmd)
		if buffered:
			os.system('cat ' + buffered_filename)
		if ret != 0:
			print('Failed program at trial', trial)
			return False
	return True



if __name__ == '__main__':
	sys.exit(main(sys.argv))




