#These dicts control the text on the html file. Django form could be an alternative
TITLES = {'page': 'Energy Storage Assessment Platform',
                  'frame_get': 'figES (fine granularity Energy Storage assessment) ',
                  'frame_post': 'figES (fine granularity Energy Storage assessment) - Review or Download Results',
                  'cards': 'Configuration'
          }
FILENAMES = {'output': 'results.csv'
             }

BTN_LABELS = {'dwn': 'Download Results',
              'opt': 'Run Optimization'
              }

batt_field_dict = {'pMax' : {'label': 'Power Rating (MW)',
                            'help': 'Limit the charging and discharging power to this value'
                            },
                  'eCap' : {'label': 'Energy Rating (MWh)',
                            'help': 'Maximum energy that the battery can hold. Equivalent to multiplying duration times power rating'
                            },
                  'eta' : {'label': 'Efficiency',
                            },
                  'disCost' : {'label': 'Discharging Cost',
                              }
                  }                  

soc_field_dict = {'socMin' : {'label': 'Min. SoC allowed (%)',
                              'help': 'Do not discharge the battery below this minimum percentage level'
                              },
                  'socMax' : {'label': 'Max. SoC allowed (%)',
                              'help': 'Do not charge the battery above this maximum percentage level'
                              },
                  'socIni' : {'label': 'Initial SoC (%)',
                              },
                  'socFin' : {'label': 'Final Daily SoC (%)',
                              }
                  }

default_value_dict = {'pMax': '1',
                      'eCap': '2',
                      'eta': '0.92',
                      'disCost':'10',
                      'socMin':'0.1',
                      'socMax':'0.95',
                      'socIni':'0.2',
                      'socFin':'0.2'
                      }

def add_input_dict_defaults(field_dict):
  for keyx in field_dict.keys():
    field_dict[keyx]['value'] = default_value_dict[keyx] 
    if 'isInput' not in field_dict[keyx].keys():
      field_dict[keyx]['isInput'] = True
    if 'type' not in field_dict[keyx].keys():
      field_dict[keyx]['type'] = 'text'
  return field_dict  

def build_batt_card_dict(row_field_list):
  card = {'id': 'batInputs',
          'idb': 'batParams',
          'description':'Battery Parameters',
          'collapse': 'collapse show',
          'field_input': True,
          'file_input': False,
          'field_list': [add_input_dict_defaults(field_dictx) for field_dictx in row_field_list]
          }
  return card

def build_lmp_card_dict(row_field_list):
  card = {'id': 'lmpInput',
          'idb': 'lmpProfile',
          'description':'Electricity Price Profile',
          'collapse': 'collapse show',
          'field_input': False,
          'file_input': True,
          }
  return card

def get_default_card_list():
  card_list = [build_batt_card_dict([batt_field_dict, soc_field_dict]),
               build_lmp_card_dict(None)
               ]
  return card_list
  
def get_result_card_list(request):
  card_list = get_default_card_list()
  for field_dict in card_list[0]['field_list']:
    for keyx in field_dict.keys(): 
      field_dict[keyx]['value'] = request.POST[keyx]
  return card_list
  
#Function to gather values changed by the user.
def get_user_input_dict(request):
  numeric_keys = ['pMax', 'eCap', 'eta', 'disCost', 'socMin', 'socMax', 'socIni', 'socFin']
  user_input_dict = dict()
  for keyx in numeric_keys: 
    user_input_dict[keyx] = float(request.POST[keyx])
  user_input_dict['tSize'] = float(request.POST['tSize'])/60 
  user_input_dict['eMin'] = user_input_dict['socMin']*user_input_dict['eCap']
  user_input_dict['eMax'] = user_input_dict['socMax']*user_input_dict['eCap']
  user_input_dict['eIni'] = user_input_dict['socIni']*user_input_dict['eCap']
  user_input_dict['eFin'] = user_input_dict['socFin']*user_input_dict['eCap']
  return user_input_dict