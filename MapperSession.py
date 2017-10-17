from __future__ import division
from psychopy import visual, core, misc, event
import numpy as np
from IPython import embed as shell
from math import *

import os, sys, time, pickle
import pygame
from pygame.locals import *
# from pygame import mixer, time

import Quest

sys.path.append( 'exp_tools' )
# sys.path.append( os.environ['EXPERIMENT_HOME'] )

from Session import *
from MapperTrial import *
from constants import *

import appnope
appnope.nope()

class MapperSession(EyelinkSession):
	def __init__(self, subject_initials, index_number, scanner, tracker_on):
		super(MapperSession, self).__init__( subject_initials, index_number)
		

		background_color = (np.array(BGC)/255*2)-1
		screen = self.create_screen( size = DISPSIZE, full_screen =FULLSCREEN, physical_screen_distance = SCREENDIST, background_color = background_color, physical_screen_size = (SCREENSIZE) )
		event.Mouse(visible=False, win=screen)

		print self.pixels_per_degree

		self.standard_parameters = standard_parameters
		self.response_button_signs = response_button_signs
		self.standard_parameters['scanner'] = scanner

		# text_file_name = "data/%s_color_ratios.txt"%self.subject_initials
		# assert os.path.isfile(text_file_name), 'NO COLOR RATIO TEXT FILE PRESENT!!!!!!!!'
		# text_file = open(text_file_name, "r")
		# RG_BY_ratio = float(text_file.readline().split('ratio: ')[-1][:-1])
		RG_BY_ratio = 1
		# text_file.close()
		if RG_BY_ratio > 1:
			self.standard_parameters['RG_color'] = 1
			self.standard_parameters['BY_color'] = 1/RG_BY_ratio
		else:
			self.standard_parameters['BY_color'] = 1
			self.standard_parameters['RG_color'] = 1/RG_BY_ratio


		# text_file_name = "data/%s_speed_ratios.txt"%self.subject_initials
		# assert os.path.isfile(text_file_name), 'NO SPEED RATIO TEXT FILE PRESENT!!!!!!!!'
		# text_file = open(text_file_name, "r")
		# self.fast_ratio = float(text_file.readline().split('ratio: ')[-1][:-1])
		# self.slow_ratio = 1-self.fast_ratio
		self.fast_ratio = self.slow_ratio = 0.5

		self.create_output_file_name(task='mapper')
		if tracker_on:
			self.create_tracker(auto_trigger_calibration = 1, calibration_type = 'HV9')
			if self.tracker_on:
				self.tracker_setup()
		else:
			self.create_tracker(tracker_on = False)
		
		self.scanner = scanner
		self.prepare_trials()

		self.ready_for_next_pulse = True
		self.exp_start_time = 0.0
		self.stim_value = 0

		# setup fix transient and redraws in session to let it continuously run. This happens in multitudes of 'time_steps'
		# self.transient_occurences = np.cumsum(np.random.exponential(self.standard_parameters['task_rate'], size = 20000) + self.standard_parameters['minimum_pulse_gap'])
		self.time_steps = self.standard_parameters['fix_time_steps']
		self.transient_occurrences = np.round(np.cumsum(np.random.exponential(self.standard_parameters['task_rate'], size = 20000) + self.standard_parameters['minimum_pulse_gap']) * (1/self.time_steps)) / (1/self.time_steps)

	
	def prepare_trials(self):
		"""docstring for prepare_trials(self):"""
		
		# create random m-sequence for the 5 trial types of length (5^3)-1 = 124. I then add the first trial type to the end of the array, so that all trial types have even occurences
		from psychopy.contrib import mseq
		# self.tasks = np.array(['fix_no_stim','no_color_no_speed','yes_color_no_speed','no_color_yes_speed','yes_color_yes_speed'])
		self.tasks = np.array(['fix_no_stim','no_color_yes_speed','yes_color_yes_speed'])#,'no_color_yes_speed','yes_color_yes_speed'])
		self.trial_array = np.hstack([[0]*self.standard_parameters['pre_post_ITI'],mseq.mseq(len(self.tasks),3,1,np.random.randint(200)),[0]*self.standard_parameters['pre_post_ITI']]) # base (number of trial types), power (sequence length is base^power-1), shift (to shift last values of sequence to first), random sequence out of the 200 possibilities

		self.phase_durations = np.array([
			-0.001, # instruct time
			-0.001, # wait for t at beginnning of every trial
			self.standard_parameters['TR'] * self.standard_parameters['mapper_stim_in_TR'],   #stimulation time
			self.standard_parameters['TR'] * self.standard_parameters['mapper_ITI_in_TR'] ]) # ITI time

		print self.screen.background_color
		# stimuli
		fix_size = self.standard_parameters['fix_size'] * self.pixels_per_degree
		fix_rim_size = self.standard_parameters['fix_size'] * self.pixels_per_degree * 1.33
		fix_outer_rim_size = self.standard_parameters['fix_size'] * self.pixels_per_degree * 2
		# fixation point
		self.fixation_rim = visual.PatchStim(self.screen, mask='raisedCos',tex=None, size=fix_rim_size, pos = np.array((0.0,0.0)), color = (-1.0,-1.0,-1.0), maskParams = {'fringeWidth':0.4})
		self.fixation_outer_rim = visual.PatchStim(self.screen, mask='raisedCos',tex=None, size=fix_outer_rim_size, pos = np.array((0.0,0.0)), color = self.screen.background_color, maskParams = {'fringeWidth':0.4})
		self.fixation = visual.PatchStim(self.screen, mask='raisedCos',tex=None, size=fix_size, pos = np.array((0.0,0.0)), color = self.screen.background_color, opacity = 1.0, maskParams = {'fringeWidth':0.4})
		
		screen_width, screen_height = self.screen_pix_size
		stim_ratio = (self.standard_parameters['max_ecc']*2) * self.pixels_per_degree / self.screen_pix_size[1]
		ecc_mask = filters.makeMask(matrixSize = 2048, shape='raisedCosine', radius=stim_ratio*self.screen_pix_size[1]/self.screen_pix_size[0], center=(0.0, 0.0), range=[1, -1], fringeWidth=0.1 )

		self.mask_stim = visual.PatchStim(self.screen, mask=ecc_mask,tex=None, size=(self.screen_pix_size[0], self.screen_pix_size[0]), pos = np.array((0.0,0.0)), color = self.screen.background_color) # 
	
		# this will be roughly 4 * 124 = 496, which is 8:15 minutes
		self.exp_duration = np.sum(self.phase_durations) * len(self.trial_array)

	def close(self):
		super(MapperSession, self).close()

	def run(self):
		"""docstring for fname"""
		# cycle through trials
		for i in range(len(self.trial_array)):
			# prepare the parameters of the following trial based on the shuffled trial array
			this_trial_parameters = self.standard_parameters.copy()
			this_trial_parameters['task'] = self.trial_array[i]

			these_phase_durations = self.phase_durations.copy()
			this_trial = MapperTrial(this_trial_parameters, phase_durations = these_phase_durations, session = self, screen = self.screen, tracker = self.tracker)
			
			# run the prepared trial
			this_trial.run(ID = i)
			if self.stopped == True:
				break
		self.close()
	

