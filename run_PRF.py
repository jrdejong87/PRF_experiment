import sys

sys.path.append( 'exp_tools' )

from PRFSession import *
from plot_staircases import *
import appnope

def main():
	initials = raw_input('Your initials: ')
	run_nr = int(raw_input('Run number: '))
	scanner = raw_input('Are you in the scanner (y/n)?: ')

	appnope.nope()

	ts = PRFSession( initials, run_nr, scanner, tracker_on = False )
	ts.run()

	plot_staircases(initials, run_nr)
	
if __name__ == '__main__':
	main()