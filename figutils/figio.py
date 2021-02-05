# -*- coding: utf-8 -*-
"""
"""
import numpy as np
import pandas as pd

#functions to gel lmps
def get_uploaded_lmps(request):
  lmps = None
  custom_flag = False
  f = request.FILES['userlmpFile'] if 'userlmpFile' in request.FILES else None
  if f is not None:
    lmps,_ = read_lmps(f)
  else:
    if 'newlmps' in request.POST:
      lmps_str = request.POST['newlmps']
      if len(lmps_str)>0:
        lmps = np.array([float(lx) for lx in lmps_str.lstrip('[').rstrip(']').split(',')])
        custom_flag = True
      else:
        lmps = pd.read_csv("static/lmp_example_60min.csv", header=None).values.flatten()
        custom_flag = True
  return lmps, custom_flag

def read_lmps(f):
  lmp_success = -1
  try:
    lmps = pd.read_csv(f, header=None).values.flatten()
  except:
    print('Cannot read your file')
  else:
    N = max(lmps.shape)# number of steps
    lmps = lmps+np.array(range(N))*1e-6 #eliminate uncertainty for periods with equal lmp prices
    lmp_success = 0
  return lmps, lmp_success