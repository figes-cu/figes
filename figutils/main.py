import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import CalcValueNoUnc as calc

ZoneName = 'NYC'
filename = 'static/rtp_{}_2010_2019.zip'.format(ZoneName.lower())
RTP = pd.read_csv(filename, header=None, compression='zip')
Ts = 1/12 # time step
TDD = len(RTP.columns)
DD = 365 # select days to look back
lmps = RTP.loc[:,range(TDD-DD-1, TDD)].values.flatten(order='F') 
T = len(lmps) # number of time steps

PowerRating = 1 # power rating in MW
EnergyRating = 2 # energy rating in MWh
MinSoC = 0.1 # minimal SoC
MaxSoC = 0.9 # max SoC

Pr = PowerRating/(EnergyRating * (MaxSoC-MinSoC)) # normalized power rating wrt energy rating
P = Pr*Ts # actual power rating taking time step size into account
eta = .9 # efficiency
c = 0 # marginal discharge cost - degradation
ed = .01 # SoC sample granularity
ef = .0 # final SoC target level, use 0 if none
Ne = int(np.floor(1/ed))+1 # number of SOC samples

vEnd = np.zeros((Ne,))  # generate value function samples

vEnd[:int(np.floor(ef*100))] = 2e2 # use 100 as the penalty for final discharge level
v = np.zeros((Ne, T+1)) # initialize the value function series
# v(1,1) is the marginal value of 0# SoC at the beginning of day 1
# V(Ne, T) is the maringal value of 100# SoC at the beginning of the last operating day
v[:,-1] = vEnd # update final value function


# process index
es = np.linspace(0,1,num=Ne,endpoint=True)
# calculate soc after charge vC = (v_t(e+P*eta))
eC = es + P*eta 
# round to the nearest sample 
iC = np.ceil(eC/ed).astype(int)+1;
iC[iC > (Ne+1)] = Ne + 2;
iC[iC < 2] = 1;
# calculate soc after discharge vC = (v_t(e-P/eta))
eD = es - P/eta 
# round to the nearest sample 
iD = np.floor(eD/ed).astype(int)+1;
iD[iD > (Ne+1)] = Ne + 2;
iD[iD < 2] = 1;


for t in list(reversed(range(T)))[2:]: # start from the last day and move backwards
    vi = v[:,t+1] # input value function from tomorrow
    vo = calc.CalcValueNoUnc(lmps[t], c, P, eta, vi, ed, iC-1, iD-1);
    v[:,t] = vo # record the result 


## plot
DD = 45 # select day to plot
TT = 144 # which time step to plot in this day

SS = (MinSoC + np.arange(0,1+ed/2,ed)*(MaxSoC-MinSoC))*1e2;

ii = (DD-1)*288 + TT;

fig, ax1 = plt.subplots()
color = 'tab:blue'
ax1.set_xlabel('SoC [%]')
ax1.set_ylabel('Marginal eneryg value [$/MWh]', color=color)
ax1.plot(SS, v[:,ii-1], linewidth=2, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:red'
ax2.set_ylabel('Total eneryg value [$]', color=color)  # we already handled the x-label with ax1
ax2.plot(SS, np.cumsum(v[:,ii-1])*ed*2*(MaxSoC-MinSoC), linewidth=2, color=color)
ax2.tick_params(axis='y', labelcolor=color)

#fig.tight_layout()  # otherwise the right y-label is slightly clipped
#plt.show()
