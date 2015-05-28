from __future__ import division
from psychopy import visual, core, misc, event
import numpy#for maths on arrays
from numpy.random import random, shuffle #we only need these two commands from this lib
# from IPython import embed as shell
from math import *
import random, sys

sys.path.append( 'exp_tools' )
# sys.path.append( os.environ['EXPERIMENT_HOME'] )

from PRFStim import *
from Trial import *

class PRFTrial(Trial):
	def __init__(self, parameters = {}, phase_durations = [], session = None, screen = None, tracker = None):
		super(PRFTrial, self).__init__(parameters = parameters, phase_durations = phase_durations, session = session, screen = screen, tracker = tracker)
		
		self.stim = PRFStim(self.screen, self, self.session, orientation = self.parameters['orientation'])
		
		this_instruction_string = '\t\t\t\t  Left\t\t/\tRight:\n\nFix\t\t\t-\tBlack\t\t/\tWhite\nColor\t\t-\tRG\t\t\t/\tBY\nSpeed\t\t-\tDec\t\t/\tAcc'# self.parameters['task_instruction']
		self.instruction = visual.TextStim(self.screen, text = this_instruction_string, font = 'Helvetica Neue', pos = (0, 0), italic = True, height = 30, alignHoriz = 'center')
		self.instruction.setSize((1200,50))

		self.run_time = 0.0
		self.instruct_time = self.fix_time = self.stimulus_time = self.post_stimulus_time = 0.0
		self.instruct_sound_played = False

		self.response_button_signs = {'z':-1, 'm':1}#'b':1, 'g':-1, 
		
	
	def draw(self):
		"""docstring for draw"""
		if self.phase == 0:
			if self.ID == 0:
				self.instruction.draw()
			else:
				self.session.fixation_outer_rim.draw()
				self.session.fixation_rim.draw()
				self.session.fixation.draw()
		if self.phase == 1:
			self.session.fixation_outer_rim.draw()
			self.session.fixation_rim.draw()
			self.session.fixation.draw()

		elif self.phase == 2:
			self.session.fixation_outer_rim.draw()
			self.session.fixation_rim.draw()
			self.session.fixation.draw()
			
		elif self.phase == 3:
			self.stim.draw(phase = (self.stimulus_time - self.fix_time) / self.phase_durations[3])
		
		elif self.phase == 4:
			self.session.fixation_outer_rim.draw()
			self.session.fixation_rim.draw()
			self.session.fixation.setColor((0,0,0))
			self.session.fixation.draw()
			
		super(PRFTrial, self).draw( )

	def event(self):
		for ev in event.getKeys():
			if len(ev) > 0:
				if ev in ['esc', 'escape', 'q']:
					self.events.append([-99,self.session.clock.getTime()-self.start_time])
					self.stopped = True
					self.session.stopped = True
					print 'run canceled by user'
				# it handles both numeric and lettering modes 
				elif ev == ' ':
					self.events.append([0,self.session.clock.getTime()-self.start_time])
					if self.phase == 0:
						self.phase_forward()
					else:
						self.events.append([-99,self.session.clock.getTime()-self.start_time])
						self.stopped = True
						print 'trial canceled by user'
				elif ev == 't': # TR pulse
					self.events.append([99,self.session.clock.getTime()-self.start_time])
					if self.phase == 0:
						self.phase_forward()
				elif ev in self.response_button_signs.keys():
					# first check, do we even need an answer?
					if self.phase == 3:
						if self.stim.last_sampled_staircase != None:
							# what value were we presenting at?
							test_value = self.session.staircases[self.stim.last_sampled_staircase].quantile()
							if self.session.unique_tasks[self.parameters['unique_task']] == 'Color':
								response = self.response_button_signs[ev]*self.stim.present_color_task_sign
							elif self.session.unique_tasks[self.parameters['unique_task']] == 'Speed':
								response = self.response_button_signs[ev]*self.stim.present_speed_task_sign
							elif self.session.unique_tasks[self.parameters['unique_task']] == 'Fix':
								response = self.response_button_signs[ev]*self.stim.present_fix_task_sign

							# update the staircase
							self.session.staircases[self.stim.last_sampled_staircase].update(test_value,(response+1)/2)
							# now block the possibility of further updates
							self.stim.last_sampled_staircase = None

							log_msg = 'staircase %s bin %d updated from %f after response %s at %f'%( self.session.unique_tasks[self.parameters['unique_task']], self.stim.eccentricity_bin,test_value, str((response+1)/2), self.session.clock.getTime() )
							self.events.append( log_msg )
							print log_msg
							if self.session.tracker:
								self.session.tracker.log( log_msg )



				# add answers based on stimulus changes, and interact with the staircases at hand
				# elif ev == 'b' or ev == 'right': # answer pulse
				event_msg = 'trial ' + str(self.ID) + ' key: ' + str(ev) + ' at time: ' + str(self.session.clock.getTime())
				self.events.append(event_msg)
		
			super(PRFTrial, self).key_event( ev )

	def run(self, ID = 0):
		self.ID = ID
		super(PRFTrial, self).run()
		
		while not self.stopped:
			self.run_time = self.session.clock.getTime() - self.start_time
			# In phase 0, we wait for the t
			if self.phase == 0:
				self.instruct_time = self.session.clock.getTime()
				if (self.ID != 0) * (self.session.scanner == 'n'):
					self.phase_forward()
			# Phase 1 is an additional wait time, only imposed in trial 1, so that participants can get ready after the instruction text disappears
			if self.phase == 1:
				# this trial phase is timed
				self.initial_wait_time = self.session.clock.getTime()
				if ( self.initial_wait_time  - self.instruct_time ) > self.phase_durations[1]:
					self.phase_forward()
			if self.phase == 2:
				self.fix_time = self.session.clock.getTime()
				if not self.instruct_sound_played:
					self.session.play_sound(self.session.unique_tasks[self.parameters['unique_task']].lower())
					self.instruct_sound_played = True
				# this trial phase is timed
				if ( self.fix_time  - self.initial_wait_time ) > self.phase_durations[2]:
					self.phase_forward()
			if self.phase == 3:
				# print 'trial %d phase 3 at %.2f'%(self.ID,self.session.clock.getTime())
				# this trial phase is timed
				self.stimulus_time = self.session.clock.getTime()
				if ( self.stimulus_time - self.fix_time ) > self.phase_durations[3]:
					self.phase_forward()
			if self.phase == 4:
				# print 'trial %d phase 4 at %.2f'%(self.ID,self.session.clock.getTime())
				# this trial phase is timed
				self.post_stimulus_time = self.session.clock.getTime()
				if ( self.post_stimulus_time  - self.stimulus_time ) > self.phase_durations[4]:
					self.stopped = True
		
			# events and draw
			self.event()
			self.draw()
	
		self.stop()
		