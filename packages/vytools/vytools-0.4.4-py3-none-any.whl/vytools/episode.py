
import vytools.utils
import vytools.compose
import vytools.definition
import vytools.object
import vytools.composerun
from vytools.config import ITEMS
import json, os, copy, io
import cerberus

SCHEMA = vytools.utils.BASE_SCHEMA.copy()

INHERIT_ITEMS = {
  'tags':{'type':'list', 'required': False, 'schema': {'type': 'string', 'maxlength':64}},
  'expectation':{'type':'boolean', 'required': False},
}

SCHEMA.update(INHERIT_ITEMS)
SCHEMA.update({
  'thingtype':{'type':'string', 'allowed':['episode']},
  'compose':{'type':'string', 'maxlength': 64},
  'object_mods':{'type': 'dict', 'required': False},
  'passed':{'type':'boolean', 'required': False},
  'anchors':{'type': 'dict', 'required': False, 'keysrules': {'type': 'string', 'regex': vytools.compose.KEYSRULES}},
  'repos':{'type':'list', 'required': False, 'schema':{'type':'string','maxlength':1024}},
  'stage_repos':{'type':'list', 'required': False, 'schema':{'type':'string','maxlength':1024}}
})
VALIDATE = cerberus.Validator(SCHEMA)

def parse(name, pth, items):
  item = {
    'name':name,
    'thingtype':'episode',
    'path':pth,
    'loaded':True
  }
  type_name = 'episode:' + name
  item['depends_on'] = []
  try:
    content = json.load(io.open(pth, 'r', encoding='utf-8-sig'))
    if 'anchors' not in content: content['anchors'] = {}
      
    for sc in SCHEMA:
      if sc in content: # and sc not in ['repos']: TODO I want this sometimes so I took the filter out. Hopefully I don't have to put it back in
        item[sc] = content[sc]

    if vytools.utils._check_add(item['compose'], 'compose', item, items, type_name):
      for anchor_key, anchor_val in content['anchors'].items():
        if anchor_val.startswith('object:'):
          vytools.utils._check_add(anchor_val, 'object', item, items, type_name)

      vytools.utils._check_self_dependency(type_name, item)
      return vytools.utils._add_item(item, items, VALIDATE)
    else:
      return False
  except Exception as exc:
    vytools.printer.print_fail('Failed to parse episode "{n}" at "{p}": {e}'.format(n=name, p=pth, e=exc))
    return False


def find_all(items, contextpaths=None):
  return vytools.utils.search_all(r'(.+)\.episode\.json', parse, items, contextpaths=contextpaths)

def get_anchors(episode, anchor_dict=None):
  if anchor_dict is None: anchor_dict = {}
  anchors = episode.get('anchors',{})
  anchors.update(anchor_dict)
  return anchors

def build(type_name, built, items=None, anchors=None, compose=None, build_level=0, object_mods=None, eppath=None):
  if items is None: items = ITEMS
  if not vytools.utils.ok_dependency_loading('build', type_name, items):
    return False

  item = items[type_name]
  extracted_anchors = get_anchors(item, anchors)
  rootcompose = compose if compose is not None  else item['compose']
  return vytools.compose.build(rootcompose, items=items, anchors=extracted_anchors, built=built, 
                        build_level=build_level, object_mods=object_mods, eppath=eppath)

def get_episode_id(episode):
  return None if '..' in episode['name'] else episode['name'].lower()

def get_episode(episode_name, items=None):
  if items is None: items = ITEMS
  if episode_name not in items:
    vytools.utils.missing_item(episode_name, items)
    return None
  return items[episode_name]

def get_episode_path(episode_name, items=None, jobpath=None):
  ep = get_episode(episode_name, items=items)
  if ep:
    epid = get_episode_id(ep)
    return vytools.composerun.runpath(epid,jobpath=jobpath)
  return None

def artifact_paths(episode_name, items=None, jobpath=None):
  ep = get_episode(episode_name, items=items)
  if ep:
    eppath = get_episode_path(episode_name, items=items, jobpath=jobpath)
    if eppath:
      return vytools.compose.artifact_paths(ep.get('compose',None), items, eppath=eppath)
  return {}

def run(type_name, items=None, anchors=None, clean=False, save=False, object_mods=None, jobpath=None, compose=None, persist=False):
  if items is None: items = ITEMS
  if type_name not in items:
    vytools.utils.missing_item(type_name, items)
    return False
  episode = items[type_name]
  if not vytools.utils.ok_dependency_loading('run', type_name, items):
    return False
  epid = get_episode_id(episode)
  eppath = vytools.composerun.runpath(epid,jobpath=jobpath)
  if epid is None or eppath is None: return False
  if 'object_mods' not in episode:
    episode['object_mods'] = {}
  obj_mods = copy.deepcopy(episode['object_mods'])
  if object_mods is not None:
    obj_mods.update(object_mods)
  extracted_anchors = get_anchors(episode, anchors)
  rootcompose = episode['compose'] if compose is None else compose
  results = vytools.composerun.run(epid, rootcompose, 
    items=items, anchors=extracted_anchors, clean=clean, 
    object_mods=obj_mods, jobpath=jobpath,
    dont_track=vytools.utils.get_repo_from_path(episode['path'], items.get('info:repository_path_list',None)),
    persist=persist)

  apaths = None
  if results and eppath and os.path.exists(eppath):
    if 'artifact_paths' in results:
      apaths = results['artifact_paths']
      del results['artifact_paths']
    for x in INHERIT_ITEMS:
      if x in episode: results[x] = episode[x]
    with open(os.path.join(eppath, episode['name']+'.episode_.json'),'w') as w2:
      w2.write(json.dumps(results, sort_keys=True, indent=2))
    if save and 'path' in episode:
      # TODO: what should I do to update the episode object loaded in vytools
      with open(episode['path'],'w') as w2:
        w2.write(json.dumps(results, sort_keys=True, indent=2))

  if apaths:
    results['artifact_paths'] = apaths
  return results

