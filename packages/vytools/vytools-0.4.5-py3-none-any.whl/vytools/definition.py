
import vytools.utils as utils
import vytools.printer as printer
import json, io
import cerberus

SCHEMA = utils.BASE_SCHEMA.copy()
SCHEMA.update({
  'thingtype':{'type':'string', 'allowed':['definition']},
  'element':{
    'type':'list',
    'schema': {
      'type': 'dict',
      'schema': {
        'name': {'type': 'string', 'maxlength': 64},
        'optional': {'type': 'boolean', 'required':False},
        'length': {'type': 'string'},
        'type': {'type': 'string'}
      }
    }
  }
})
VALIDATE = cerberus.Validator(SCHEMA)

def parse(name, pth, items):
  item = {
    'name':name,
    'thingtype':'definition',
    'depends_on':[],
    'element':[],
    'path':pth,
    'loaded':True
  }
  try:
    content = json.load(io.open(pth, 'r', encoding='utf-8-sig'))
    item['element'] = content['element']
  except Exception as exc:
    printer.print_fail('Failed to parse definition "{n}" at "{p}": {e}'.format(n=name, p=pth, e=exc))
    return False

  return utils._add_item(item, items, VALIDATE)

def find_all(items, contextpaths=None):
  success = utils.search_all(r'(.+)\.definition\.json', parse, items, contextpaths=contextpaths)
  for (type_name, item) in items.items():
    if type_name.startswith('definition:'):
      (typ, name) = type_name.split(':',1)
      item['depends_on'] = []
      successi = True
      for e in item['element']:
        if e['type'] in utils.BASE_DATA_TYPES:
          pass
        elif e['type'] in items:
          item['depends_on'].append(e['type'])
        else:
          successi = False
          printer.print_fail('definition "{n}" has an invalid element type {t}'.format(n=name, t=e['type']))
      success &= successi
      item['loaded'] &= successi
      utils._check_self_dependency(type_name, item)
          
  return success
