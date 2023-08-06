import hashlib, json, io, glob, requests, os
import vytools.utils as utils
import vytools.printer
import vytools.uploads as uploads
from vytools.config import ITEMS
import cerberus
from pathlib import Path

SCHEMA = utils.BASE_SCHEMA.copy()
SCHEMA.update({
  'thingtype':{'type':'string', 'allowed':['bundle']},
  'publish':{'type':'boolean','required':False},
  'bundles':{
    'type':'list',
    'schema': {
      'type': 'dict',
      'schema': {
        'name': {'type': 'string', 'maxlength': 128},
        'serch': {'type': 'string', 'maxlength': 128},
        'rplce': {'type': 'string', 'maxlength': 128}
      }
    }
  },
  'philes':{
    'type':'list',
    'schema': {
      'type': 'dict',
      'schema': {
        'path': {'type': 'string', 'maxlength': 1024},
        'name': {'type': 'string', 'maxlength': 128},
        'hash': {'type': 'string', 'maxlength': 32}
      }
    }
  }
})

VALIDATE = cerberus.Validator(SCHEMA)

def fhash(pth):
  md5 = hashlib.md5()
  BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
  try:
    with open(pth, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
  except Exception as exc:
    vytools.printer.print_fail('Failed to get hash for {}: {}'.format(pth,exc))
  return md5.hexdigest()

def parse(name, pth, items):
  item = {
    'name':name,
    'thingtype':'bundle',
    'philes':[],
    'bundles':[],
    'depends_on':[],
    'path':pth,
    'loaded':True
  }
  try:
    content = json.load(io.open(pth, 'r', encoding='utf-8-sig'))
    item['bundles'] = content.get('bundles',[])
    item['publish'] = content.get('publish',False)
    for phile in content.get('philes',[]):
      path = phile.get('path',None)
      prefix = phile.get('prefix',None)
      rplce = phile.get('rplce',None)
      serch = phile.get('serch',None)
      if path is not None:
        thisdir = os.getcwd()
        try:
          dirpath = os.path.dirname(pth)
          os.chdir(dirpath)
          file_list = glob.glob(path,recursive=True)
          for file in file_list:
            filepath = os.path.join(dirpath,file)
            if not os.path.isfile(filepath) or any([file.endswith(ext) for ext in ['.nodule.json','.bundle.json','.vydir']]):
              continue
            newname = file if not prefix else prefix+file
            if serch is not None and rplce is not None:
              newname = newname.replace(serch,rplce)
            item['philes'].append({
              'name':newname,
              'hash':fhash(filepath),
              'path':filepath
            })
            # print(item['philes'][-1])
        except Exception as exc:
          vytools.printer.print_fail('Failed to parse bundle "{n}" at "{p}": {e}'.format(n=name, p=pth, e=exc))
          return False
        os.chdir(thisdir)
  except Exception as exc:
    vytools.printer.print_fail('Failed to parse bundle "{n}" at "{p}": {e}'.format(n=name, p=pth, e=exc))
    return False

  return utils._add_item(item, items, VALIDATE)

def find_all(items, contextpaths=None):
  success = utils.search_all(r'(.+)\.bundle\.json', parse, items, contextpaths=contextpaths)
  for (type_name, item) in items.items():
    if type_name.startswith('bundle:'):
      (typ, name) = type_name.split(':',1)
      item['depends_on'] = []
      successi = True
      for e in item['bundles']:
        if e['name'] in items:
          item['depends_on'].append(e['name'])
        else:
          successi = False
          vytools.printer.print_fail('bundle "{n}" has a reference to a bundle {t}'.format(n=name, t=e['name']))
      success &= successi
      item['loaded'] &= successi
      utils._check_self_dependency(type_name, item)
  return success

def onsuccess(item, url, headers, result):
  refresh = result.get('refresh')
  success = True
  for phile in item['philes']:
    if phile['name'] in refresh:
      res = requests.post(url+'/update_phile', json={'_id':refresh[phile['name']],
        'hash':phile['hash'],
        'content':Path(phile['path']).read_text()},headers=headers)
      if not res.json().get('processed',False):
        success = False
        vytools.printer.print_fail('  - Failed to update phile "{}": {}'.format(phile['name'],res.json()))
      else:
        vytools.printer.print_success('  - Uploaded updated phile "{}"'.format(phile['name']))
  res = requests.post(url+'/clean_philes', json={}, headers=headers)
  return success
  
def upload(lst, url, uname, token, check_first, update_list, items=None):
  if items is None: items = ITEMS
  return uploads.upload('bundle', lst, url, uname, token, check_first, update_list, onsuccess, items=items)