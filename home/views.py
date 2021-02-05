#Application uses Class Views
#https://docs.djangoproject.com/en/3.1/topics/class-based-views/intro/
from django.shortcuts import render
from django.views import View
#Python libraries
import io
import numpy as np
import os
import pandas as pd

#Custom libraries 
import figutils.figbkh as bkh
import figutils.figio as figio
import figutils.fightml as fhtml
import figutils.essolverlag as es_l

#GET creates the initial view
#POST is called with Optimize button

class Home(View):
  def get(self, request):
    card_list = fhtml.get_default_card_list()
    #Customizable plot
    lmps = pd.read_csv("static/lmp_example_60min.csv", header=None).values.flatten()
    bk_script2, bk_div2 = bkh.create_bk_lmp_doms_2(lmps)
    ###
    return render(request,
                  "home.html",
                  {"page_title": fhtml.TITLES['page'],
                   "cards": card_list,
                   "tsize_value": '60', 
                   "frame_title": fhtml.TITLES['frame_get'],
                   "cards_title": fhtml.TITLES['cards'],
                   "btn_label": fhtml.BTN_LABELS,
                   "bk_script2": bk_script2,
                   "bk_div2": bk_div2,
                   "show_results": False
                   }
                  )

  def post(self, request):
    input_dict = fhtml.get_user_input_dict(request)
    result_card_list = fhtml.get_result_card_list(request)
    lmps, custom_flag = figio.get_uploaded_lmps(request)
    if lmps is None:
        lmps = pd.read_csv("static/lmp_example_60min.csv", header=None).values.flatten()
        bk_script2, bk_div2 = bkh.create_bk_lmp_doms_2(lmps)
    pDopt, pCopt, eopt, profit,theta = es_l.get_opt_results(lmps,
                                                  T = input_dict['tSize'],
                                                  eIni = input_dict['eIni'],
                                                  pMax = input_dict['pMax'],
                                                  eMin = input_dict['eMin'],
                                                  eMax = input_dict['eMax'],
                                                  eFin = input_dict['eFin'],
                                                  c = input_dict['disCost'],
                                                  eta = input_dict['eta'])
    
    #Generate result file and save it to a session
    results_df = pd.DataFrame({'pD':pDopt, 'pC': pCopt, 'eopt': eopt, 'theta': theta})
    file_str = io.StringIO()
    results_df.to_csv(file_str, index=False)
    request.session['file_str'] = file_str.getvalue()
    #Bokeh plots
    bk_script, bk_div = bkh.create_bk_lmp_doms_1(lmps, pDopt, pCopt)
    bk_r_script, bk_r_div = bkh.create_bk_result_doms_1(eopt,
                                                        eMin=input_dict['eMin'],
                                                        eIni=input_dict['eIni'],
                                                        eMax=input_dict['eMax'],
                                                        )
    #Refresh customazible bokeh plot
    if custom_flag:
        bk_script2, bk_div2 = bkh.create_bk_lmp_doms_2(lmps)
    else:
        lmps = pd.read_csv("static/lmp_example_60min.csv", header=None).values.flatten()
        bk_script2, bk_div2 = bkh.create_bk_lmp_doms_2(lmps)
    return render(request,
                  "home.html",
                  {"page_title": fhtml.TITLES['page'],
                   "cards": result_card_list,
                   "tsize_value": request.POST['tSize'],
                   "frame_title": fhtml.TITLES['frame_post'],
                   "cards_title": fhtml.TITLES['cards'],
                   "btn_label": fhtml.BTN_LABELS,
                   "show_results": True,
                   "bk_script": bk_script,
                   "bk_div": bk_div,
                   "bk_r_script": bk_r_script,
                   "bk_r_div": bk_r_div,
                   "bk_script2": bk_script2,
                   "bk_div2": bk_div2,
                   "dwn_filename": fhtml.FILENAMES['output'],
                   "revenue": 'Objective function value = ${:0.3f}'.format(profit)
                   }
                  )

    
                  