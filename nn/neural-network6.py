import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from brian2 import *

count = 0
gs = gridspec.GridSpec(1, 2)

def NN(f):
	# Morphology
	morpho = Soma(25*um)#was 30
	morpho.L = Cylinder(diameter=1*um, length=100*um, n=75)#was 50
	morpho.R = Cylinder(diameter=1*um, length=100*um, n=75)

	# Passive channels
	gL = 1e-4*siemens/cm**2
	EL = -50*mV #was 70
	Es = 0*mV
	taus = 1*ms
	eqs='''
	Im = gL*(EL-v) : amp/meter**2
	Is = gs*(Es-v) : amp (point current)
	dgs/dt = -gs/taus : siemens
	'''

	neuron = SpatialNeuron(morphology=morpho, model=eqs,
                       Cm=1*uF/cm**2, Ri=100*ohm*cm)
	neuron.v = EL

	# Regular inputs
	stimulation = NeuronGroup(2, 'dx/dt = f*Hz : 1', threshold='x>1', reset='x=0')
	stimulation.x = [0, 0.5] # Asynchronous

	# Synapses
	w = 20*nS
	S = Synapses(stimulation, neuron, pre = 'gs += w')
	S.connect(0, morpho.L[99.9*um])
	S.connect(1, morpho.R[99.9*um])

	# Monitors
	mon_soma = StateMonitor(neuron, 'v', record=[0])
	mon_L = StateMonitor(neuron.L, 'v', record=True)
	mon_R = StateMonitor(neuron, 'v', record=morpho.R[99.9*um])

	run(50*ms, report='text')

	if count == 0:
		ax1 = subplot(gs[0,0])
		#ax1.subplot(3,2,1)
		ax1.plot(mon_L.t/ms, mon_soma[0].v/mV, 'k')
		ax1.plot(mon_L.t/ms, mon_L[morpho.L[99.9*um]].v/mV, 'r')
		ax1.plot(mon_L.t/ms, mon_R[morpho.R[99.9*um]].v/mV, 'b')
		#title('Convergence of Neurons')
		title('Synaptic Delays in Firing Neurons')
		xlabel('Time (ms)')
		ylabel('v (mV)')
		ax2 = subplot(gs[0,1])
		#ax1.subplot(3,2,2)
		for i in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]:
    			ax2.plot(mon_L.t/ms, mon_L.v[i, :]/mV)
		#title('Synaptic Delays in Firing Neurons')
		title('Convergence of Neurons')
		xlabel('Time (ms)')
		#ylabel('v (mV)')

	#suptitle('Neural Network Analysis of Asteroids', fontsize = 18)
	elif count == 1:
		ax3 = subplot(gs[1,0])
		#ax1.subplot(3,2,3)
		ax3.plot(mon_L.t/ms, mon_soma[0].v/mV, 'k')
		ax3.plot(mon_L.t/ms, mon_L[morpho.L[99.9*um]].v/mV, 'r')
		ax3.plot(mon_L.t/ms, mon_R[morpho.R[99.9*um]].v/mV, 'b')
		#title('Convergence of Neurons')
		title('Synaptic Delays in Firing Neurons')
		#xlabel('Time (ms)')
		ylabel('v (mV)')
		ax4 = subplot(gs[1,1])	
		#ax1.subplot(3,2,4)
		for i in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]:
    			ax4.plot(mon_L.t/ms, mon_L.v[i, :]/mV)
		#title('Synaptic Delays in Firing Neurons')
		title('Convergence of Neurons')
		#xlabel('Time (ms)')
		#ylabel('v (mV)')
	elif count == 2:
		ax5 = subplot(gs[2,0])
		#subplot(325)
		ax5.plot(mon_L.t/ms, mon_soma[0].v/mV, 'k')
		ax5.plot(mon_L.t/ms, mon_L[morpho.L[99.9*um]].v/mV, 'r')
		ax5.plot(mon_L.t/ms, mon_R[morpho.R[99.9*um]].v/mV, 'b')
		#title('Convergence of Neurons')
		title('Synaptic Delays in Firing Neurons')
		xlabel('Time (ms)')
		ylabel('v (mV)')
		ax6 = subplot(gs[2,1])
		subplot(326)
		for i in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]:
	    		ax6.plot(mon_L.t/ms, mon_L.v[i, :]/mV)
		#title('Synaptic Delays in Firing Neurons')
		title('Convergence of Neurons')
		xlabel('Time (ms)')
		#ylabel('v (mV)')	
	suptitle('Neural Network Analysis of Asteroids', fontsize = 18)
	#++count

NN(5)
show()
