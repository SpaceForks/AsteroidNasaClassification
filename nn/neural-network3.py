from brian2 import *

#start_scope()
N = 100
tau = 10*ms
v0_max = 3.
duration = 1000*ms

eqs = '''
dv/dt = (v0-v)/tau : 1 (unless refractory)
v0 : 1
'''

G   = NeuronGroup(N, eqs, threshold='v>1', reset='v = 0', refractory=5*ms)
G.v = 'rand()'

#statemon = StateMonitor(G, 'v', record=0)
M = SpikeMonitor(G)

G.v0 = 'i*v0_max/(N-1)'

run(duration)

figure(figsize=(12,4))
subplot(121)
plot(M.t/ms, M.i, '.k')
xlabel('Time (ms)')
ylabel('Neuron index')
subplot(122)
plot(G.v0, M.count/duration)
xlabel('v0')
ylabel('Firing rate (sp/s)')
title('Neural Network Analysis')
show()

#eqs = '''
#dV/dt  = (ge+gi-(V+49*mV))/(20*ms) : volt
#dge/dt = -ge/(5*ms)                : volt
#dgi/dt = -gi/(10*ms)               : volt
#'''
#P = NeuronGroup(4000, model=eqs, threshold=-50*mV, reset=-60*mV)
#Pe = P.subgroup(3200)
#Pi = P.subgroup(800)
#Ce = Connection(Pe, P, 'ge')
#Ci = Connection(Pi, P, 'gi')
#Ce.connect_random(Pe, P, p=0.02, weight=1.62*mV)
#Ci.connect_random(Pi, P, p=0.02, weight=-9*mV)
#M = SpikeMonitor(P)
#P.V = -60*mV+10*mV*rand(len(P))
#run(.5*second)
#raster_plot(M)
#show()

