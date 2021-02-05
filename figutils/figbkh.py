# -*- coding: utf-8 -*-
"""
"""
from bokeh import events
from bokeh.plotting import figure
from bokeh.models import BoxAnnotation, ColumnDataSource, PointDrawTool, CustomJS
from bokeh.embed import components

#Bokeh plot globals
p_height = 300
p_width = 1200

def create_bk_lmp_plot_1(lmps, pDopt, pCopt):
  p = figure(
          title="Selected LMPs",
          plot_width=p_width, plot_height=p_height,
          toolbar_location=None,
          )
  p.toolbar.active_drag = None
  p.toolbar.active_scroll = None
  p.toolbar.active_tap = None
  p.xaxis.axis_label = "Period"
  p.yaxis.axis_label = "LMP ($/MWh)"
  
  N = len(lmps)
  x_range = list(range(N+1))
  labelx = 'LMP'
  p.step(x_range,
         list(lmps)+[lmps[-1]],
         line_width=2,
         mode='after',
         legend_label = labelx)
  for ii in range(N):
    if pDopt[ii]>1e-3:
      p.add_layout(BoxAnnotation(left=x_range[ii],
                                 right=x_range[ii+1],
                                 fill_alpha=0.2,
                                 fill_color='green'))
    elif pCopt[ii]>1e-3:
      p.add_layout(BoxAnnotation(left=x_range[ii],
                                 right=x_range[ii+1],
                                 fill_alpha=0.2,
                                 fill_color='red'))
  return p

#bokeh plots should be converted to components to embed in html
def create_bk_lmp_doms_1(lmps, pDopt, pCopt):

  return components(create_bk_lmp_plot_1(lmps, pDopt, pCopt))

def create_bk_result_1(eopt, eMin, eIni, eMax):
  N = len(eopt)
  x_range = list(range(N+1))
  p2 = figure(
          title="Optimized Battery Energy",
          plot_width=p_width, plot_height=p_height,
          toolbar_location=None,
#          x_axis_type="datetime"
          )
  p2.toolbar.active_drag = None
  p2.toolbar.active_scroll = None
  p2.toolbar.active_tap = None
  p2.xaxis.axis_label = "Period"
  p2.yaxis.axis_label = "Energy (MWh)"
  # add a line renderer
  p2.step(x_range, [eIni] + list(eopt), line_width=2, mode='center')    
  p2.line([x_range[0], x_range[-1]],
          [eMin, eMin],
          line_width=1,
          line_dash='dashed',
          color='red')    
  p2.line([x_range[0], x_range[-1]],
          [eMax, eMax],
          line_width=1,
          line_dash='dashed',
          color='red')    

  return p2

def create_bk_result_doms_1(eopt, eMin, eIni, eMax):
  return components(create_bk_result_1(eopt, eMin, eIni, eMax))  
  
#Customazible LMP curve
def create_bk_lmp_plot_2(lmps):
  x= [x for x in range(24)]
  data = {'x_values': x,
          'y_values': lmps}
  source = ColumnDataSource(data=data)
  p3 = figure(
          title="Move each rectangles on top of each value to create a custom LMP curve",
          plot_width=p_width, plot_height=p_height,
          toolbar_location=None,
          y_range=(-50, 100)
          )
 
  xyp = p3.rect(x='x_values', y='y_values', width=1, height=5, source=source, color='navy', alpha=0.8)

  draw_tool = PointDrawTool(renderers=[xyp])
  draw_tool.add = False

  p3.add_tools(draw_tool)
  p3.toolbar.active_tap = draw_tool
  p3.toolbar.active_drag = None
  p3.toolbar.active_scroll = None
  p3.xaxis.axis_label = "Period"
  p3.yaxis.axis_label = "LMP ($/MWh)"
  
  #Every time that the plot is changed these JS callbacks are activated
  js_restrict_x_coor = CustomJS(args=dict(source=source), code="""
                            source.data.x_values = [...Array(24).keys()];
                            source.change.emit();
                            """
                            )
  js_update_values =  CustomJS(args=dict(source=source), code="""
                            var newlmps_input = document.getElementById("newlmps");
                            newlmps_input.value = source.data.y_values;
                            var tSize_input = document.getElementById("tSize");
                            tSize_input.value = '60';
                            """
                            )
  p3.js_on_event(events.Pan, js_restrict_x_coor)
  p3.js_on_event(events.PanEnd, js_update_values)
  return p3

def create_bk_lmp_doms_2(lmps):
  
  return components(create_bk_lmp_plot_2(lmps))

