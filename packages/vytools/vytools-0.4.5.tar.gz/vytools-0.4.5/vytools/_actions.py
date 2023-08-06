import json, copy, subprocess
from vytools.config import CONFIG, ITEMS
from getpass import getpass

import vytools.utils
import vytools.stage
import vytools.compose
import vytools.episode
import vytools.definition
import vytools.bundle
import vytools.nodule
import vytools.object
import vytools.printer

def scan(contextpaths=None):
  if contextpaths:
    vytools.printer.print_def('\nScanning the following directories for vy items:'+'\n  '.join(['']+contextpaths)+'\n\n')
  CONFIG.set('scanned',contextpaths)

  items = {}
  items['info:repository_path_list'] = vytools.utils.get_init_info_repository_path_list(items)
  success = True
  success &= vytools.definition.find_all(items, contextpaths=contextpaths)
  success &= vytools.object.find_all(items, contextpaths=contextpaths)
  success &= vytools.utils.find_all_vydirectories(items, contextpaths=contextpaths)
  success &= vytools.stage.find_all(items, contextpaths=contextpaths)
  success &= vytools.compose.find_all(items, contextpaths=contextpaths)
  success &= vytools.episode.find_all(items, contextpaths=contextpaths)
  success &= vytools.bundle.find_all(items, contextpaths=contextpaths)
  success &= vytools.nodule.find_all(items, contextpaths=contextpaths)

  # if success: # Check for missing dependencies
  for i,it in items.items():
    for dependency in it['depends_on']:
      if dependency not in items:
        vytools.printer.print_warn(' * Item {j} (depended on by {i}) is not in the list of found items'.format(i=i, j=dependency))
        success = False

  # if success: # Reverse dependency chain
  for i in items:
    items[i]['depended_on'] = []
  for i in items:
    for d in items[i]['depends_on']:
      if d in items:
        items[d]['depended_on'].append(i)

  if success:
    thinglist = [item for item in items]
    sorted_things = vytools.utils.sort(thinglist, items)
    for itemid in items: # Sort the depends_on of each thing
      items[itemid]['depends_on'] = [i for i in sorted_things if i in items[itemid]['depends_on']]

  ITEMS.clear()
  ITEMS.update(items)
  CONFIG.set('items',[i for i in items]) # Always write items?
  return success

def build(original_list, items=None, anchors=None, build_level=0, jobpath=None, compose=None):
  if items is None: items = ITEMS
  if anchors is None: anchors = {}
  built = []
  stages = []
  for type_name in original_list:
    if type_name.startswith('stage:') and type_name not in stages:
      stages.append(type_name)
    elif type_name.startswith('compose:') and type_name in items:
      anchor_copy = copy.deepcopy(anchors)
      build_level = max(0,build_level) # Don't write for a compose if run at this level
      if False == vytools.compose.build(type_name, items=items, anchors=anchor_copy, built=built, build_level=build_level, eppath=jobpath):
        return False
    elif type_name.startswith('episode:') and type_name in items:
      anchor_copy = copy.deepcopy(anchors)
      build_level = max(0,build_level) # Don't write for a compose if run at this level
      if False == vytools.episode.build(type_name, built, anchors=anchor_copy, items=items, build_level=build_level, eppath=jobpath, compose=compose):
        return False

  if len(stages) > 0:
    if not vytools.utils.exists(stages, items):
      return False
    anchor_copy = copy.deepcopy(anchors)
    if not vytools.stage.build(stages, items, anchor_copy, built, build_level, jobpath=jobpath):
      return False
  return built

def run(original_list, items=None, anchors=None, clean=False, save=False, object_mods=None, jobpath=None, cmd=None, persist=False, compose=None):
  if items is None: items=ITEMS
  if anchors is None: anchors = {}
  results = {}
  for type_name in original_list:
    anchor_copy = copy.deepcopy(anchors)
    if type_name.startswith('stage:'):
      results[type_name] = vytools.stage.run(type_name, items=items, anchors=anchor_copy, jobpath=jobpath, cmd=cmd)
    elif type_name.startswith('compose:'):
      epid = type_name.replace(':','__')
      results[type_name] = vytools.compose.run(epid, type_name, items=items, anchors=anchor_copy, object_mods=object_mods, jobpath=jobpath, persist=persist)
    elif type_name.startswith('episode:'):
      results[type_name] = vytools.episode.run(type_name, items=items, anchors=anchor_copy, save=save, clean=clean, object_mods=object_mods, jobpath=jobpath, persist=persist, compose=compose)
  return results

def upload(original_list, url, username=None, token=None, check_first=True, items=None):
  if items is None: items=ITEMS
  username = input('Enter username:') if username is None else username
  token = getpass('Enter token:') if token is None else token
  results = []
  bundleok = vytools.bundle.upload(original_list, url, username, token, check_first, results, items=items)
  if not bundleok:
    return False, results
  noduleok = vytools.nodule.upload(original_list, url, username, token, check_first, results, items=items)
  if not noduleok:
    return False, results
  return True, results

def _recursive_list(name, spctop, items, field):
  def list_all_dependencies(name, spc, visited, items):
    if name not in items:
      vytools.printer.print_def(spc+name+'[?]')
    elif name in visited:
      vytools.printer.print_def(spc+name+'[*]')
    else:
      vytools.printer.print_def(spc+name)
      visited.append(name)
      for d in items[name][field]:
        list_all_dependencies(d, spc+spctop, visited, items)
  visited = []
  list_all_dependencies(name, spctop, visited, items)

def get_sorted_images():
  images = {}
  image_list = vytools.stage.DOCKER_CLIENT.images.list()
  image_id_list = [image.id for image in image_list]
  for image in image_list:
    labels = image.attrs['Config']['Labels']
    has_image_dependencies = bool(labels and 'tools.vy.images' in labels)
    images[image.id] = {
      'tags':image.tags,
      'depends_on':[],
      'repos':[] if not labels or 'tools.vy.repos' not in labels else labels['tools.vy.repos'].split(','),
      'attrs':image.attrs,
      'has_image_dependencies':has_image_dependencies
    }
    if has_image_dependencies:
      depimages = [x.split('=')[-1] for x in labels['tools.vy.images'].split(',')]
      images[image.id]['depends_on'] = [x for x in depimages if x in image_id_list]
  sorted_image_list = vytools.utils.sort(images.keys(), images)
  return (images, sorted_image_list)

IMAGE_SEP = ','
def image_name_label(hash,images):
  return 'image:'+(IMAGE_SEP.join(images[hash]['tags']) if hash in images else hash)

def get_images(original_list):
  (images, sorted_image_list) = get_sorted_images()
  image_list = {}
  for hid in [False, True]:
    for k in sorted_image_list:
      ok = not original_list or any([tag in original_list for tag in images[k]['tags']])
      if ok and images[k]['has_image_dependencies'] == hid:
        label = image_name_label(k,images)
        depended_on = [image_name_label(it,images) for it,i in images.items() if k in i['depends_on']]
        depends_on =  [image_name_label(it,images) for it in images[k]['depends_on']]
        tags = label.replace('image:','')
        image_list[label] = {
          'hashid':k,
          'name':tags,
          'thingtype':'image',
          'not_vy': not hid,
          'depends_on':depends_on,
          'repos':images[k]['repos'],
          'attrs':images[k]['attrs'],
          'depended_on':depended_on
        }
  return image_list

def image_info(images, print_dependencies, prefx):
  sorted_image_list = vytools.utils.sort(images.keys(), images)
  for k in sorted_image_list:
    if k in images:
      im = images[k]
      nobody_depends_on = ' ' if not len(im['depended_on']) == 0 else '*'
      depends_on_nobody = '-' if im['not_vy'] else '*' if len(im['depends_on']) == 0 else ' '
      vytools.printer.print_def(prefx+'|{}|{}|'.format(depends_on_nobody,nobody_depends_on) + k.replace('image:',''))
      if print_dependencies:
        vytools.printer.print_def(prefx+' -Depended on by:')
        for x in im['depended_on']: vytools.printer.print_def(prefx+'     '+x)
        vytools.printer.print_def(prefx+' -Depends on:')
        for x in im['depends_on']: vytools.printer.print_def(prefx+'     '+x)
        for x in im['repos']: vytools.printer.print_plus(prefx+'     '+x)
  vytools.printer.print_info(prefx+'|-| | = Not built by vy or built before version 0.2.7')
  vytools.printer.print_info(prefx+'|*| | = This image depends on no other images')
  vytools.printer.print_info(prefx+'| |*| = No other vy images depend on this image')

def info(original_list=[], items=None, list_dependencies=False, list_private=False, list_images=False, expand=False):    
  if items is None: items=ITEMS
  results = {'images':{}}
  CONFIG.info(list_private=list_private)
  dep_spaces = '   '
  for i in original_list:
    if i in items:
      vytools.printer.print_def(i, attrs=['bold'])
      vytools.printer.print_def(json.dumps(items[i], indent=6, sort_keys=True))
      if i.startswith('object:') and expand:
        item = items[i]
        obj,deps = vytools.object.expand(item['data'], item['definition'], items)
        vytools.printer.print_def(json.dumps(obj, indent=6, sort_keys=True))
      if list_dependencies:
        vytools.printer.print_def(dep_spaces + 'dependencies', attrs=['bold'])
        _recursive_list(i, dep_spaces, items, 'depends_on')
        vytools.printer.print_def(dep_spaces + 'dependents', attrs=['bold'])
        _recursive_list(i, dep_spaces, items, 'depended_on')

      repo_versions = vytools.utils.get_repo_versions([i],items)
      sorted_repo_versions = sorted([v for v in repo_versions.values()])
      vytools.printer.print_def('This item depends directly or indirectly on these repositories which are currently at these versions:')
      for x in sorted_repo_versions:
        vytools.printer.print_plus('  '+x)
      if i.startswith('stage:') and list_images:
        vytools.printer.print_def('This item was used to create these images:')
        image_list = get_images(vytools.stage.stages(i))
        image_info(image_list,list_dependencies,'  ')

    else:
      vytools.printer.print_def('Unknown item {i}'.format(i=i), attrs=['bold'])

  if not original_list:
    vytools.printer.print_def('  Repositories in this context')
    repo_versions = vytools.utils.get_all_repo_versions(items)
    for x in sorted([v for v in repo_versions.values()]):
      vytools.printer.print_plus('    '+x)
  
    if list_images:
      vytools.printer.print_def('  Images on this device')
      results['images'] = get_images([])
      image_info(results['images'], list_dependencies, '    ')
  return results

def clean():
  while True:
    im = get_images([])
    images = [x for x in im.values() if not x['not_vy'] and not x['depended_on']]
    if len(images) == 0:
      break
    try:
      count = 0
      for x in images:
        vytools.printer.print_def('#{} {}'.format(str(count).ljust(5,' '),x['name']))
        count+=1
      nu = int(input('Enter the list # of the image to be deleted [from 0 to {} or, to exit without deleting: -1]:'.format(len(images)-1)))
      if nu >= 0 and nu < len(images) and input('Are you sure you want to permanently delete docker image {} (y/n)'.format(images[nu]['name'])).lower() == 'y':
        for tag in images[nu]['name'].split(IMAGE_SEP):
          subprocess.check_output(['docker','rmi',tag])
        vytools.stage.prune()
      else:
        break
    except Exception as exc:
      return