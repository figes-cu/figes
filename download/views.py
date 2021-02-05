from django.views import View
from django.http import HttpResponse

import pandas as pd

import sys
import os

if sys.platform == "linux" or sys.platform == "linux2":
    dwn_dir = '/tmp'
elif sys.platform == "win32":
     dwn_dir = 'static/tmp'
else: 
  print('unknown os')

class Download(View):
  def get(self, request):
    file_str = request.session.get('file_str')
    response = HttpResponse(content_type='text/csv', content=file_str)
    response['Content-Disposition'] = 'attachment; filename="results.csv"'
    return response

