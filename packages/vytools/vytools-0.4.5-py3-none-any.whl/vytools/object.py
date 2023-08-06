
import vytools.utils as utils
import vytools.definition
import json, io
import cerberus

SCHEMA = utils.BASE_SCHEMA.copy()
SCHEMA.update({
  'thingtype':{'type':'string', 'allowed':['object']},
  'definition':{'type':'string', 'maxlength': 64},
  'data':{'type': 'dict'}
})
VALIDATE = cerberus.Validator(SCHEMA)

def parse(name, pth, items):
  item = {
    'name':name,
    'thingtype':'object',
    'depends_on':[],
    'path':pth,
    'loaded':True
  }
  try:
    content = json.load(io.open(pth, 'r', encoding='utf-8-sig'))
    item['definition'] = content['definition']
    item['data'] = content['data']
  except Exception as exc:
    vytools.printer.print_fail('Failed to parse object "{n}" at "{p}": {e}'.format(n=name, p=pth, e=exc))
    return False

  return utils._add_item(item, items, VALIDATE)

def element_length(element):
  return -1 if 'length' not in element else (0 if element['length'] == '?' else int(element['length']))

def check_length(element, obj):
  length = element_length(element)
  if type(obj) == list and length == -1:
    return 'Element "{e}" should not be a list'.format(e=element['name'])
  elif type(obj) != list and length > -1:
    return 'Element "{e}" should be a list'.format(e=element['name'])
  elif type(obj) == list and length > 0 and len(obj) != length:
    return 'Element "{e}" should be a list of length {n}'.format(e=element['name'], n=length)
  return True

def _make_object_mod_sub(object_mods, key):
  return {k.replace(key+'.','',1):v for k,v in object_mods.items() if k.startswith(key+'.')}

def _make_object_mod_sub_i(object_mods, key, i):
  object_mods_sub_r = _make_object_mod_sub(object_mods, key + '.$')
  object_mods_sub_i = _make_object_mod_sub(object_mods, key + '.'+str(i))
  object_mods_sub_r.update(object_mods_sub_i)
  return object_mods_sub_r

def expand(data_, definition_=None, items=None, object_mods=None):
  if items is None: items = vytools.ITEMS
  dependencies = []
  if type(data_) == str:
    dependencies += [data_]
    if not data_.startswith('object:'):
      vytools.printer.print_fail('Cannot expand the item "{}" since it is not an "object:"'.format(data_))
    elif data_ not in items:
      vytools.printer.print_fail('Cannot expand the item "{}" since it is not in the list of known objects'.format(data_))
    else:
      (data__, deps_) = expand(items[data_]['data'], items[data_]['definition'], items, object_mods=object_mods)
      if (data__ is None): return (data__, deps_)
      dependencies += [d for d in deps_ if d not in dependencies]
      return (data__, dependencies)
    return (None, [])

  data = {}
  if object_mods is None: object_mods = {}
  if definition_ is None or definition_ not in items:
    vytools.printer.print_fail('The definition {d} does not exist'.format(d=definition_))
    return (None, [])

  definition = items[definition_]
  for el in definition['element']:
    if el['type'] in utils.BASE_DATA_TYPES:
      # TODO make sure these are correct, also, could be list
      rhs = object_mods.get(el['name'], data_.get(el['name'], utils.BASE_DATA_TYPES[el['type']]))
    elif el['type'] in items:
      obj = object_mods.get(el['name'], data_.get(el['name'],{}))
      if type(obj) == str:
        if obj in items:
          defin = items[obj]['definition']
          if defin == el['type']:
            dependencies += [obj]
            obj = items[obj]['data']
          else:
            vytools.printer.print_fail('The internal definition of object:\n "{o}" ({d1}) does not match the desired {d2}'.format(o=obj,d1=defin,d2=el['type']))
            return (None, [])
        else:
          vytools.printer.print_fail('The object "{o}" does not exist'.format(o=obj))
          return (None, [])
      if type(obj) == list:
        rhs = []
        ocount = 0
        for o in obj:
          dms = _make_object_mod_sub_i(object_mods,el['name'],ocount)
          rhsi,deps_ = expand(o, el['type'], items, object_mods=dms)
          if rhsi is None: return (rhs, deps_)
          dependencies += [d for d in deps_ if d not in dependencies]
          rhs.append(rhsi)
          ocount += 1
      else:
        dms = _make_object_mod_sub(object_mods,el['name'])
        rhs,deps_ = expand(obj, el['type'], items, object_mods=dms)
        if rhs is None: return (rhs, deps_)
        dependencies += [d for d in deps_ if d not in dependencies]
    else:
      return (None, [])
    data[el['name']] = rhs
  return (data, dependencies)

def object_validate(obj, sigtypename, top, items, trace, add_missing_fields):
  success = True
  if sigtypename in utils.BASE_DATA_TYPES:
    pass #TODO validate types
  elif sigtypename in items:
    if type(obj) == str: # This must be a reference to another object
      if obj not in items:
        success = False
        vytools.printer.print_fail('Object "{top}" references object "{o}" at {trace} which does not seem to exist'.format(o=obj, top=top, trace=trace))
      elif not obj.startswith('object:'):
        success = False
        vytools.printer.print_fail('Object "{top}" references object "{o}" at {trace} which is not of type "object:"'.format(o=obj, top=top, trace=trace))
      else:
        item = items[obj]
        if item['definition'] != sigtypename:
          success = False
          vytools.printer.print_fail(('Object definitions dont match in "{top}":\n'+
            '  {top} expects an object of definition type "{d1}" in position {trace}\n'+
            '  but references object "{o}" which is of definition type "{d2}"').format(o=obj, 
                      top=top, d2=item['definition'], d1=sigtypename, trace=trace))
        else:
          items[top]['depends_on'].append(obj)
    elif type(obj) == dict:
      definition = items[sigtypename]
      foundelements = []
      for e in definition['element']:
        key = e['name']
        if key not in obj:
          if key in add_missing_fields['fields']:
            add_missing_fields['added'] = True
            obj[key] = add_missing_fields['fields'][key]
          elif e.get('optional',False):
            pass
          else:
            success = False
            vytools.printer.print_fail('Expected element "{e}" in data of {top} at {trace}'.format(e=key, top=top, trace=trace+'.'+key))
        else:
          successi = check_length(e, obj[key])
          if successi == True:
            if type(obj[key]) == list:
              count=0
              for v in obj[key]:
                success &= object_validate(v, e['type'], top, items, trace+'.'+str(count), add_missing_fields)
                count += 1
            else:
              success &= object_validate(obj[key], e['type'], top, items, trace+'.'+key, add_missing_fields)
          else:
            vytools.printer.print_fail('Failed to parse element "{}" of "{}": {}'.format(key,top,successi))
            successi = False
          success &= successi
    else:
      success = False
      vytools.printer.print_fail('Bad type in object {top}'.format(top=top))
  else:
    success = False
    vytools.printer.print_fail('Unknown calibration definition "{s}"'.format(s=sigtypename))
  return success

def find_all(items, add_missing_fields=None, contextpaths=None):
  if add_missing_fields is None: add_missing_fields = {'fields':{},'added':False}
  success = utils.search_all(r'(.+)\.object\.json', parse, items, contextpaths=contextpaths)
  for (type_name, item) in items.items():
    successi = True
    if type_name.startswith('object:'):
      (typ, name) = type_name.split(':',1)
      item['depends_on'] = []
      # Add definition to dependency
      if item['definition'] in items:
        item['depends_on'].append(item['definition'])
      else:
        successi = False
        vytools.printer.print_fail('object "{n}" has an invalid definition {t}'.format(n=name, t=item['definition']))
      successi = object_validate(item['data'], item['definition'], type_name, items, '',add_missing_fields)
      success &= successi
      item['loaded'] &= successi
      vytools.utils._check_self_dependency(type_name, item)

      if add_missing_fields['added']:
        add_missing_fields['added'] = False
        with open(item['path'],'r+') as rw:
            d = json.loads(rw.read())
            d['data'] = item['data']
            rw.seek(0)
            rw.write(json.dumps(d,indent=2,sort_keys=True))
            rw.truncate()
  return success
