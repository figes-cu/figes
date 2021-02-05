# -*- coding: utf-8 -*-
"""
# Title: Solve the arbitrage using Lagrange Algorithm
# Inputs:
#   lmps - price series
#   N - number of price intervals
#   T - duration of price interval in hour
#   eIni - initial SoC in MWh
#   pMax - power rating in MW
#   eMin - minimal energy level in MWh
#   eMax - maximum energy level in MWh
#   eFin - final SoC target in MWh
#   c - marginal discharge cost (degradation) $/MWh
#   eta - charge and discharge efficiency
# Outputs:
#   thetaOut - dual results
#   pOut - optimized power series
#   eOutSim - resulting SoC series
#   ProfitOut - profit result
"""
import numpy as np

def runPolicy(theta, lmps, T, eIni, pMax, eMin, eMax, eFin, c, eta):
  N = len(lmps)
  if (eFin<eMin):
    print('Final eFin is lower than eMin, which violates Energy constrains')
  # D - indicator of theta value, 1 for too big, -1 for too small
  # initialize power series
  x = np.zeros((N,))
  dtheta = 1e-3
  # discharge at full power rating for when price is higher than...
  x[lmps >= ((theta-dtheta)/eta + c)] = pMax
  # do not discharge when price is negative
  x[lmps < 0] = 0
  # charge at full power rating for when price is lower than...
  x[lmps <= (theta+dtheta)*eta] = -pMax;
  # add efficiency to calculate SoC impact
  # calculate unconstrained SoC series
  e = eIni - np.cumsum(x*(x>0)/eta+x*(x<0)*eta)*T
  # simulate control until reach SoC bounds - except last step
  D = 0
  n=0
  for n in range(N-1):
    # if reached upper bound first
    if e[n] > eMax:
      D = 1
      break
    # if reached lower bound first
    elif e[n] < eMin:
      D = -1
      break
  #At the end of the loop D==0 & n=N-2 if it did not reach a limit
  if D==0:
    n = N - 1
  #  if e[n+1] > eMax:
  #    D = 1;
  # for the last step, need to include the final SoC target
  # Even after the last step it landed between eFin and eMax
    if e[n] <=max(eMin, eFin):
      D = -1;
    else:
      D = 1
  return D, n+1, x[0:n+1], e[0:n+1]

#%%
def solveTheta(lmps, T, eIni, pMax, eMin, eMax, eFin, c, eta):
  eps = 1e-3
  # Title: Find the Optimal Dual and the correlating Primal results
  ub = np.max(lmps)# upper search bound
  lb = 0 # lower search bound
  N = len(lmps)

  while (ub-lb)>=eps:# error greater than 1e-4
    theta = (ub+lb)/2 # set a value for theta
    # simulate the SoC and return 
    #   D - higher (D>0) or lower (D<0) guess of theta value
    #   n - time step simulated 
    #   p - power output series til n
    #   e - SoC output series til n

    D, n, p, e = runPolicy(theta, lmps, T, eIni, pMax, eMin, eMax, eFin, c, eta)
    #print(D, n, theta)
    if D > 0: # if guessed too high, reduce upper bound
      ub = theta
    elif D < 0: # if guessed too low, increase lower bound
      lb = theta
  # final SoC
  ef = e[-1]

  # The main function below is to identify the marginal charge/discharge
  # interval and modulate it according to the upper/lower energy limit
  while True:
    # identify the marginal interval
    thetaS = np.sort(np.concatenate(((lmps[:n]-c)*eta, lmps[:n]/eta)))
    I = np.argsort(np.concatenate(((lmps[:n]-c)*eta, lmps[:n]/eta)))
    i = np.argmin(np.abs(thetaS-theta))
    mI = I[i];
#    print('mI, n and theta', mI, n, theta)
    if mI <= n-1: # marginal segment is to discharge
      if p[mI] > 0: # marginal segment is indeed discharge
        eM = np.max(e[mI:])
        nn = mI + np.argmax(e[mI:])
        if (nn >= mI) & (eM + pMax*T/eta > eMax): # could reach upper bound earlier
          p[mI] = p[mI] - (eMax-eM)/T*eta
          n = nn+1
          ef = eMax
          p = p[:n]
        else: 
          if n == N: # if final interval, use final SoC target
              p[mI] = p[mI] - (eFin-ef)/T*eta;
          else:
              p[mI] = p[mI] - (eMin-ef)/T*eta;
          ef = eMin;
        theta = thetaS[i];
        break
      else: # conjesture is wrong, adjust theta and try again
          theta = theta - eps;
          [D, n, p, e] = runPolicy(theta, lmps, T, eIni, pMax, eMin, eMax, eFin, c, eta)
          ef = e[-1]    
    else: # marginal segment is to charge
      mI = mI-n
      if p[mI] < 0: # marginal segment is indeed charge
          eM = np.min(e[mI:])
          nn = mI + np.argmin(e[mI:])
          if (nn >= mI) & (eM - pMax*T*eta < eMin): # could reach lower bound earlier
              p[mI] = p[mI] - (eMin-eM)/eta/T
              n = nn+1
              ef = eMin
              p = p[:n]
          else:
              if n == N: # if final interval, use final SoC target
                  p[mI] = p[mI] - (eFin-ef)/eta/T
              else:
                  p[mI] = p[mI] - (eMax-ef)/eta/T
              ef = eMax
          theta = thetaS[i];
          break
      else: # conjesture is wrong, adjust theta and try again
          theta = theta + eps;
          [D, n, p, e] = runPolicy(theta, lmps, T, eIni, pMax, eMin, eMax, eFin, c, eta)
          ef = e[-1]
  return theta, n, p, ef
#%%
def esSolverLag(lmps, T, eIni, pMax, eMin, eMax, eFin, c, eta):
  # initialize power and dual series
  N = len(lmps)
  pOut = np.zeros((N,))
  thetaOut = np.zeros((N,))
  # initialize SoC and interval
  e = eIni
  n = 0
  eOut = eIni*np.ones((N,))
  while n<N:
    # find the first dual and the associated optimal control profile
    theta, nn, p, ef = solveTheta(lmps[n:], T, e, pMax, eMin, eMax, eFin, c, eta);
    # update final SoC
#    print('selected n:', n,n+nn, 'theta:', theta )
    e = ef
    # record results
    pOut[n:(n+nn)] = p;
    thetaOut[n:(n+nn)] = theta;
    # start from the last of the sovled period
    n = n+nn;

  eOut = eIni - np.cumsum(pOut*(pOut>0)/eta+pOut*(pOut<0)*eta)*T;
  return pOut*(pOut>0), -pOut*(pOut<0), eOut, thetaOut


def get_opt_results(lmps, T, eIni, pMax, eMin, eMax, eFin, c, eta):
  pDopt, pCopt, eopt, theta = esSolverLag(lmps, T, eIni, pMax, eMin, eMax, eFin, c, eta)
  nmax = len(eopt)
  rLag = np.sum((lmps[0:nmax]-c)*pDopt[0:nmax])*T
  cLag = np.sum(lmps[0:nmax]*pCopt[0:nmax])*T
  profit = rLag-cLag
  return pDopt, pCopt, eopt, profit, theta
