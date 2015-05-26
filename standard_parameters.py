

# standard parameters
standard_parameters = {
	
	## common parameters:
	'stim_size': 0.66667,					# twenty degree diameter aperture - ten degree radius
	'num_elements' : 2000,
	'period' : 36.0,				
	'refresh_frequency' : 2.0,				# 1/refresh_frequency is the redraw duration
	'task_rate' : 3.0,						# this + minimum_pulse_gap is average of exponential distribution
	'minimum_pulse_gap':2.0,
	'baseline_speed_for_task': 5.0,
	'baseline_color_for_task': 0.75,
	'element_size': 45.0,
	'element_spatial_frequency': 2.0,

	## attention experiment variables:
	'orientation' : 0.0,
	'bar_width_ratio': 0.1,				# 0.2 times the stimulus radius

	## mapper variables:
	'stimulus_repetitions': 30,			# for each trial type (of which there are 5)		
	'mapper_period': 3.0,

}

# screen_res = (2560, 1440)
screen_res = (1680, 1050)
background_color = (-0.75,-0.75,-0.75)
