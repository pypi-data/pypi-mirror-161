import os, re, subprocess, re, json, copy
from pathlib import Path
from vytools.config import CONFIG, SEARCHED_REPO_PATHS
import vytools.printer

BASE_DATA_TYPES = {'float32':0,'float64':0,'uint64':0,
  'int64':0,'uint32':0,'int32':0,'uint16':0,'int16':0,'uint8':0,
  'int8':0,'string':'','bool':False,'byte':0,'char':''}

BASE_SCHEMA = {
  'path': {'type':'string', 'maxlength': 1024,'required':True},
  'name': {'type':'string', 'maxlength': 64,'required':True},
  'depends_on':{'type':'list','schema': {'type': 'string', 'maxlength':64},'required':True},
  'loaded':{'type':'boolean','required':True}
}

REPO_SCHEMA = BASE_SCHEMA.copy()
REPO_SCHEMA.update({
  'source': {'type':'string', 'maxlength': 32},
  'account': {'type':'string', 'maxlength': 32},
  'reponame': {'type':'string', 'maxlength': 128},
  'url': {'type':'string', 'maxlength': 512},
  'type': {'type':'string', 'allowed': ['git','hg']},
})

def check_and_get_path(lst):
  if len(lst) == 0: return False
  try:
    return Path(os.sep.join(lst)).resolve(strict=True)
  except:
    return False

def path_split(pth):
  return [part2 for part1 in pth.split('/') for part2 in part1.split(os.sep)]

def get_thing_path(name, items):
  if '..' in name: return None
  ns = path_split(name)
  pth = items.get(ns[0],{}).get('path',None)
  if not pth:
    vytools.printer.print_fail('Failed to find a path for item "{}"'.format(ns[0]))
    return None
  pth = os.sep.join([pth]+ns[1:]) if len(ns)>1 else pth
  if not os.path.exists(pth):
    vytools.printer.print_fail('The directory/file at "{}" does not exist'.format(pth))
    return None
  return pth
  
def find_all_vydirectories(items, contextpaths=None):
  success = search_all(None, None, items, checkvydir=True, contextpaths=contextpaths)
  return success

def repo_version(typ, pth):
  try:
    if typ == 'hg':
      return subprocess.check_output(['hg','--cwd',pth,'id','-i']).decode('utf8').strip()  # unfortunately THIS CHANGES FILES IN THE .Hg folder
    elif typ == 'git':
      hash_ = subprocess.check_output(['git','-C',pth,'rev-parse','HEAD']).decode('utf8').strip()
      changes = subprocess.check_output(['git','-C',pth,'status','--porcelain']).decode('utf8').strip()
      hash_ += '+' if len(changes) > 0 else ''
      return hash_ #subprocess.check_output(['git','-C',pth,'rev-parse','HEAD']).decode('utf8').strip()
    else:
      return '-'
  except Exception as exc:
    vytools.printer.print_fail('Failed to get hash of repo: '+str(exc))
    return '-'

def parse_repo(pth, items):
  if pth in SEARCHED_REPO_PATHS: return SEARCHED_REPO_PATHS[pth]
  SEARCHED_REPO_PATHS[pth] = False

  if os.path.exists(os.path.join(pth,'.git')): # Can be directory or file so use exists
    typ = 'git'
    options = ['origin','remote'] # to do more here
    cmdprefx = ['git','-C',pth,'config','--get']
  elif os.path.isdir(os.path.join(pth,'.hg')):
    typ = 'hg'
    options = ['default'] # to do more here
    cmdprefx = ['hg','--cwd',pth,'paths']
  else:
    return SEARCHED_REPO_PATHS[pth]

  s = {'type':typ,'path':pth,'depends_on':[],'version':'','thingtype':'repo','loaded':True}
  url = None
  for o in options: 
    try:
      cmd = cmdprefx + ['remote.{o}.url'.format(o=o) if typ == 'git' else o]
      url = subprocess.check_output(cmd).decode('utf-8').strip()
      if len(url) > 0: break
    except Exception as exc:
      pass
  if not url:
    vytools.printer.print_fail('Failed to get remote for repository at {p}'.format(p=pth))
    return SEARCHED_REPO_PATHS[pth]

  # e.g.
  # git@bitbucket.org:account/name.git
  # https://username@bitbucket.org/account/name.git
  # https://github.com/account/name.git
  # git@github.com:account/name.git
  s['url'] = url
  urlparts = url.split('@',1)[-1]
  urlparts = re.split('/|:',urlparts)
  if len(urlparts) < 3:
    s['loaded'] = False
    vytools.printer.print_fail('Failed to parse url "{u}" for repository at {p}'.format(u=url,p=pth))
    return SEARCHED_REPO_PATHS[pth]

  s['source'] = urlparts[0]
  s['account'] = urlparts[1]
  s['reponame'] = urlparts[2].replace('.git','').replace('.hg','')
  name_root = s['account']+'|'+s['reponame']
  name = name_root
  count = 0
  while 'repo:'+name in items:
    name = name_root+'|'+str(count)
    count += 1
  s['name'] = name
  type_name = 'repo:'+s['type'] + '|' + s['source'] + '|' + s['name']
  items[type_name] = s

  # Add to info:
  repo_path_list = get_init_info_repository_path_list(items)
  repo_path_list['list'].append({'path':pth,'name':type_name})
  repo_path_list['list'].sort(key=len)
  repo_path_list['list'].reverse()
  items['info:repository_path_list'] = repo_path_list

  SEARCHED_REPO_PATHS[pth] = True
  return SEARCHED_REPO_PATHS[pth]

def get_init_info_repository_path_list(items):
  return items.get('info:repository_path_list',{'list':[],'depends_on':[]})

def repo_version_string(repo, version=None):
  if version == None:
    version = repo_version(repo['type'], repo['path'])
  return repo['type'] + '|' + repo['source'] + '|' + repo['name'] + '|' + version

def get_repo_versions(lst, items):
  repo_versions = {}
  def get_version(name):
    if name in items:
      item = items[name]
      rname = get_repo_from_path(item['path'], items.get('info:repository_path_list',None))
      if rname is not None:
        repo_versions[rname] = repo_version_string(items[rname])
      for d in item['depends_on']: 
        get_version(d)
  for l in lst: get_version(l)
  return repo_versions

def get_all_repo_versions(items):
  return {k:repo_version_string(items[k]) for k in items if k.startswith('repo:')}

def get_repository_paths(rep_str_lst, contextpaths=None):
  sp = contextpaths if contextpaths else CONFIG.get('contexts')
  items = {}
  newcp = []
  success = True
  search_all(None, None, items, contextpaths=sp, find_repos_only=True)
  repo_versions = get_all_repo_versions(items)
  vytools.printer.print_def('Found repositories:')
  for item in sorted([v for v in repo_versions.values()]):
    vytools.printer.print_def('  '+item)
  for r in rep_str_lst:
    found = False
    for i,item in repo_versions.items():
      found = item.startswith(r)
      if found:
        newcp.append(items[i]['path'])
        break
    if not found:
      success = False
      vytools.printer.print_fail('Failed to find repository matching {n} in the searched directories {p}'.format(n=r,p=','.join(sp)))
  SEARCHED_REPO_PATHS.clear()
  return (success, newcp)

def get_repo_from_path(path, repo_path_list):
  if repo_path_list is None:
    vytools.printer.print_fail('"info:repository_path_list" does not exist in the list of items')
  else:
    ipaths = [path]+[str(p) for p in Path(path).parents]
    for r in repo_path_list['list']:
      if r['path'] in ipaths:
        return r['name']
  return None

def is_vydir(files):
  vydir = None
  for f in files:
    if f.endswith('.vydirectory'):
      vydir = f.replace('.vydirectory','',-1)
      break
    if f.endswith('.vydir'):
      vydir = f.replace('.vydir','',-1)
      break
  if vydir and vydir == 'vy':
    vytools.printer.print_fail('"vy" is a reserved vydirectory name')
    vydir = None
  return vydir

def search_all(fname_regex, func, items, checkvydir=False, contextpaths=None, find_repos_only=False):
  if contextpaths is None: contextpaths = CONFIG.get('contexts')
  success = False
  if contextpaths:
    success = True
    exclude = set(['.vy','.git','.hg'])
    for cp in contextpaths:
      for root, dirs, files in os.walk(cp, topdown=True):
        if '.vyignore' in files:
          dirs[:] = []
          continue
        isrepo = parse_repo(root, items)
        dirs[:] = [d for d in dirs if d not in exclude]
        if isrepo and find_repos_only:
          dirs[:] = []
          continue
        if checkvydir:
          vydir = is_vydir(files)
          if vydir: 
            item = {'name':vydir, 'thingtype':'vydir', 'depends_on':[], 'path':root, 'loaded':True}
            success &= _add_item(item, items, True)
        elif fname_regex and func:
          for f in files:
            m = re.match(fname_regex,f,re.I)
            if m:
              success &= func(m.group(1), os.path.join(root, f), items)
  return success

def topological_sort(source):
    pending = [(name, set(deps)) for name, deps in source]        
    emitted = []
    while pending:
      next_pending = []
      next_emitted = []
      for entry in pending:
        name, deps = entry
        deps.difference_update(set((name,)), emitted)
        if deps:
          next_pending.append(entry)
        else:
          yield name
          emitted.append(name)
          next_emitted.append(name)
      if not next_emitted:
        raise ValueError("cyclic dependency detected {n}: pending={p}".format(n=name,p=pending))
      pending = next_pending
      emitted = next_emitted
    return emitted

def exists(lst, items, pad=''):
  success = True
  for l in lst:
    if l not in items:
      success = False
      vytools.printer.print_fail('"{n}" was not found {p}'.format(n=l,p=pad))
    else:
      success &= exists(items[l]['depends_on'],items,'(depended on by {})'.format(l))
  return success

def recursive_get_check(l,lst,items):
  if l not in lst and l in items:
    lst.append(l)
    for ll in items[l].get('depends_on',[]):
      recursive_get_check(ll,lst,items)

def sort(lst, items):
  all_in_list = []
  for l in lst:
    recursive_get_check(l, all_in_list, items)
  return [x for x in topological_sort([(k,set(items[k]['depends_on'])) for k in all_in_list]) if x in lst]

def ok_dependency_loading(action,type_name,items):
  if type_name not in items or not items[type_name]['loaded']:
    vytools.printer.print_fail('Cannot {} "{}" because it did not load properly'.format(action,type_name))
    return False
  for d in items[type_name]['depends_on']:
    if not ok_dependency_loading(action,d,items):
      return False
  return True

def _check_self_dependency(id,item):
  n = len(item['depends_on'])
  item['depends_on'][:] = [dep for dep in item['depends_on'] if dep != id]
  if n != len(item['depends_on']):
    item['loaded'] &= False
    vytools.printer.print_fail('Item "{n}" should not depend on itself'.format(n=id))

def _check_add(nme, typ, item, items, parent):
  if nme.startswith(typ+':') and nme in items:
    item['depends_on'].append(nme)
    return True
  elif typ == 'vydir' and nme.startswith(typ+':') and nme.split('/')[0] in items:
    item['depends_on'].append(nme.split('/')[0])
    return True
  vytools.printer.print_fail('Failed to find subitem "{n}" referenced by "{p}".\n  - "{n}" is not of type {t} or does not exist'.format(n=nme, t=typ, p=parent))
  return False

def _add_item(item, items, validate):
  typ = item['thingtype']
  name = item['name']
  pth = item['path']
  tname = typ+':'+name
  if tname in items:
    pthp = items[tname]['path']
    i1 = copy.deepcopy(items[tname])
    i2 = copy.deepcopy(item)
    del i1['path']
    del i2['path']
    if json.dumps(i1,sort_keys=True) == json.dumps(i2,sort_keys=True):
      vytools.printer.print_warn('Identical objects "{t}" at:\n    "{p}" (loaded) and \n    "{p2}" (not loaded)'.format(t=tname, p=pth, p2=pthp))
    else:
      vytools.printer.print_fail('"{t}" at "{p}" was not loaded because a same name item was already loaded from {p2}'.format(t=tname, p=pth, p2=pthp))
    return False
  elif validate==True or validate.validate(item):
    items[tname] = item
    return True
  else:
    vytools.printer.print_fail('"{n}" at "{p}" failed validation {s}'.format(n=tname, p=pth, s=validate.errors))
    return False

def missing_item(type_name, items):
  if not items:
    vytools.printer.print_fail('No items are included. Do you have items defined? Have you scanned for them?')
  else:
    examples = []
    for k in items.keys():
      if not any([e.startswith(k.split(':')[0]+':') for e in examples]):
       examples.append(k)
    vytools.printer.print_fail('Item "{}" not found in vy items. Check the spelling and format.  Example items:\n  {}'.format(type_name,'\n  '.join(examples)))
