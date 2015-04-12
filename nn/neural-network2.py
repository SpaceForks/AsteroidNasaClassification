import random
import math
import matplotlib
from numpy import*
from pylab import*


## Setup parameters and state variables
	T       = 50                  # total time to simulate (msec)
	dt      = 0.125               # simulation time step (msec)
	time    = arange(0, T+dt, dt) # time array
	t_rest  = 0                   # initial refractory time

## LIF properties
	Vm      = zeros(len(time))    # potential (V) trace over time
	Rm      = 1                   # resistance (kOhm)
	Cm      = 10                  # capacitance (uF)
	tau_m   = Rm*Cm               # time constant (msec)
	tau_ref = 4                   # refractory period (msec)
	Vth     = 1                   # spike threshold (V)
	V_spike = 0.5                 # spike delta (V)

## Stimulus
	I       = 1.5                 # input current (A)

def network(wavelengths, fluxes):
	for flux in fluxes:
		if 

## iterate over each time step
	for i, t in enumerate(time):
		if t > t_rest:
			Vm[i] = Vm[i-1] + (-Vm[i-1] + I*Rm) / tau_m * dt
		if t >= Vth:
			Vm[i] += V_spike
			t_rest = t + tau_ref

## plot membrane potential trace
	plot(time, Vm)
	title('Neural Network')
	ylabel('Flux (normalized across data)')
	xlabel('Wavelength (nanometers)')
	ylim([0,2])
	show()
