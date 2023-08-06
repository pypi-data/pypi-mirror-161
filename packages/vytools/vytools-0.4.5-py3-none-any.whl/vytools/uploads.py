import requests, json
import vytools.utils as utils
import vytools.printer as printer

def _checkupdate(datatype, type_name, url, uname, token, check_only, onsuccess, items):
  if not utils.ok_dependency_loading('upload', type_name, items):
    return False,'Dependency not found'
  headers = {'token':token, 'username':uname}
  try:
    item = items[type_name]
    item['check_only'] = check_only
    res = requests.post(url+'/update_'+datatype, json=item, headers=headers)
    result = res.json()
    success = True
    if not check_only and result['processed'] == True:
      success = onsuccess(item, url, headers, result)
    return success, result
  except Exception as exc:
    return False, str(exc)

def _update(datatype, uploadlst, url, uname, token, onsuccess, items, update_list):
  for type_name in uploadlst:
    succ,res = _checkupdate(datatype, type_name, url, uname, token, False, onsuccess, items)
    if succ:
      printer.print_success('Successfully updated {} "{}"'.format(datatype,type_name))
      update_list.append(type_name)
    else:
      return False
  return True

def upload(datatype, lst, url, uname, token, check_first, update_list, onsuccess, items):
  uploadlst = lst if lst else items
  uploadlst = utils.sort([tn for tn in uploadlst if tn.startswith(datatype+':')], items)

  if not check_first:
    return _update(datatype, uploadlst, url, uname, token, onsuccess, items, update_list)

  while (len(uploadlst) > 0): # Do this in batches
    updatable_list = []
    not_yet_updatable_list = []
    oksofar = True
    for type_name in uploadlst:
      if not oksofar:
        not_yet_updatable_list.append(type_name) 
      else:
        succ, result = _checkupdate(datatype, type_name, url, uname, token, True, onsuccess, items)
        if not succ:
          printer.print_fail('{} "{}" failed upload check'.format(datatype,type_name))
          return False
        elif result.get('processed',False) == False:
          oksofar = False
          not_yet_updatable_list.append(type_name) 
        elif result.get('change',None) == False:
          printer.print_info('{} "{}" is already up to date'.format(datatype, type_name))
        elif type(result.get('change',None)) == str:
          printer.print_info('{} "{}" is different locally than at {} and can be uploaded'.format(datatype, type_name, url))
          updatable_list.append({'type_name':type_name,'question':result.get('change',None)})
        else:
          printer.print_fail('{} "{}" did not have a "change" element which shouldnt happen'.format(datatype, type_name))
          return False

    if len(updatable_list) == 0:
      break
    elif input('Would you like to upload all these without seeing the diff of each? (y/n) (n means you will be shown individual diffs)').lower() == 'y':
      if not _update(datatype, [it['type_name'] for it in updatable_list], url, uname, token, onsuccess, items, update_list):
        return False
    else:
      for it in updatable_list:
        if it['question'] and input(it['question']).lower() == 'y':
          if not _update(datatype, [it['type_name']], url, uname, token, onsuccess, items, update_list):
            return False

    uploadlst = not_yet_updatable_list
  return True