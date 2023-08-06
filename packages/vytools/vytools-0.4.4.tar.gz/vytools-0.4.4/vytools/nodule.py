import json, io
import vytools.utils as utils
import vytools.printer
from vytools.config import ITEMS
import vytools.uploads as uploads
import cerberus

SCHEMA = utils.BASE_SCHEMA.copy()

SCHEMA.update({
  'thingtype':{'type':'string', 'allowed':['nodule']},
  'name':{'type':'string','maxlength': 128},
  'pubu':{'type':'string','maxlength': 128},
  'prbu':{'type':'string','maxlength': 128},
  'levl':{'type': 'integer', 'allowed': [1, 2, 3, 4]},
  'prvt':{'type': 'dict'},
  'pblc':{'type': 'dict'},
})

VALIDATE = cerberus.Validator(SCHEMA)

def parse(name, pth, items):
  item = {
    'name':name,
    'thingtype':'nodule',
    'pubu':'orph',
    'prbu':'orph',
    'levl':2,
    'prvt':{},
    'pblc':{},
    'depends_on':[],
    'path':pth,
    'loaded':True    
  }
  try:
    content = json.load(io.open(pth, 'r', encoding='utf-8-sig'))
    for key in ['levl','pubu','prbu','prvt','pblc']:
      item[key] = content.get(key,item[key])
  except Exception as exc:
    vytools.printer.print_fail('Failed to parse nodule "{n}" at "{p}": {e}'.format(n=name, p=pth, e=exc))
    return False

  return utils._add_item(item, items, VALIDATE)

def find_all(items, contextpaths=None):
  success = utils.search_all(r'(.+)\.nodule\.json', parse, items, contextpaths=contextpaths)
  for (type_name, item) in items.items():
    if type_name.startswith('nodule:'):
      (typ, name) = type_name.split(':',1)
      item['depends_on'] = []
      successi = True
      for key in ['pubu','prbu']:
        val = item[key]
        if val == 'orph':
          pass
        elif val.startswith('bundle:') and val in items:
          item['depends_on'].append(val)
        else:
          successi = False
          vytools.printer.print_fail('nodule "{n}" references "{r}" as the {p}, it should reference a valid bundle name (e.g. "bundle:mybundle").'.format(n=name, p=key, r=val))
        success &= successi
      item['loaded'] &= successi
      utils._check_self_dependency(type_name, item)
  return success

def onsuccess(item, url, headers, result):
  return True

def upload(lst, url, uname, token, check_first, update_list, items=None):
  if items is None: items = ITEMS
  return uploads.upload('nodule', lst, url, uname, token, check_first, update_list, onsuccess, items=items)