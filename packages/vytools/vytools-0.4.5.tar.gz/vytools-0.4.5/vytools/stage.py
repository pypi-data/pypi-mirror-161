import os, re, subprocess, time, shlex, json, sys
import vytools.utils as utils
import vytools.printer
from vytools.config import CONFIG, ITEMS
from pathlib import Path
import cerberus

try:
  DOCKER_VERSION = subprocess.check_output(['docker','version']).decode('utf-8').strip()
except:
  DOCKER_VERSION = None

try:
  subprocess.check_output(['docker-compose','--help'])
  DOCKER_COMPOSE = ['docker-compose']
except:
  DOCKER_COMPOSE = ['docker','compose']

try:
  import docker
  DOCKER_CLIENT = docker.from_env()
except: # linux only
  vytools.printer.print_warn('Python docker module was not installed. Falling back to commandline')
  class docker_image: # .id, .tags, .attrs['Config']['Labels']
    def __init__(self,id):
      self.id = id
      try:
        x = json.loads(subprocess.check_output(['docker','inspect',id]).decode('utf-8'))
      except Exception as exc:
        x = [{'RepoTags':None}]
        vytools.printer.print_fail('docker inspect command failed. docker not installed?: {}'.format(exc))
      self.tags = x[0]['RepoTags']
      self.attrs = x[0]


  class docker_images:
    def __init__(self):
      pass
    def list(self):
      lscmd = ['docker','image','ls','-q']
      try:
        return [docker_image(id) for id in subprocess.check_output(lscmd).decode('utf8').strip('').split()]
      except Exception as exc:
        vytools.printer.print_fail('"docker image ls -q" command failed. docker not installed?: {}'.format(exc))
      return []

    def get(self,id):
      return docker_image(id)

  class docker_client:
    def __init__(self):
      self.images = docker_images()
    
    def inspect_container(id):
      return docker_image(id).attrs

  DOCKER_CLIENT = docker_client()

#todo NOT SURE THIS IS THE RIGHT REGEX
COPY_STAGE_A = re.compile(r'^copy[\s]+--from=[\'"]?([\w-]+)',re.I | re.M)
COPY_STAGE_B = re.compile(r'^from[\s]+([\w\-:\.\/]+)',re.I | re.M)
COPY_REPO = re.compile(r'^copy[\s]+[\'"]?([\w-]+)',re.I | re.M)

SCHEMA = utils.BASE_SCHEMA.copy()
SCHEMA.update({
  'thingtype':{'type':'string', 'allowed':['stage']},
  'build_context':{'type':'string', 'maxlength': 1024},
  'secrets':{'type':'list','schema': {'type': 'string', 'maxlength':64}},
  'ssh':{'type':'list','schema': {'type': 'string', 'maxlength':64}},
  'args':{
    'type':'list',
    'schema': {
      'type': 'dict',
      'schema': {
        'key': {'type': 'string', 'maxlength': 64},
        'value': {'type': 'string', 'maxlength': 64}
      }
    }
  }
})

VALIDATE = cerberus.Validator(SCHEMA)

def get_repo_info(name):
  return {'type':'git','source':'bitbucket','account':'autonomoussolutions','name':name}

def line_before_escape(line):
  return re.split(r'([^\\]#)',line)[0]      # All characters before unescaped # (comments)

def remove_quotes(line):
  if line.startswith('"') and line.endswith('"'):
    return line.strip('"')
  elif line.startswith("'") and line.endswith("'"):
    return line.strip("'")
  else:
    return line

def parse_build_context(name, stage_path, build_context, items):
  if build_context.startswith('vydir:') or build_context.startswith('repo:'):
    spl = utils.path_split(build_context)
    vydir_or_repo = spl[0]
    if vydir_or_repo in items and '..' not in build_context:
      bc = utils.check_and_get_path([items[vydir_or_repo]['path']]+spl[1:])
      if not bc:
        vytools.printer.print_fail('Path "{p}" for stage {n} does not exist'.format(p=build_context,n=name))
      else:
        return (bc,[vydir_or_repo])
    else:
      vytools.printer.print_fail('Stage build context "{p}" for stage {n} is not known'.format(p=build_context,n=name))
  elif os.path.isabs(build_context):
    vytools.printer.print_fail('Stage "{}" has build context "{}" which is an absolute path. It should be relative to the .stage.dockerfile'.format(name,build_context))
  else:
    try:
      return (Path(os.path.join(os.path.dirname(stage_path),build_context)).resolve(),[])
    except Exception as exc:
      vytools.printer.print_fail('Stage build context "{p}" for stage {n} may not be a directory'.format(p=build_context,n=name))
  return (False,[])

def dependencies(stage_text):  
  dependency = []
  build_context = '.'
  external_images = []
  for linex in stage_text.splitlines(): # TODO would be nice to preserve backslash continuation lines as one line
    m = re.search(r'^#vy(.+)', linex, re.I | re.M)
    if m:
      lsplit = shlex.split(linex)
      if len(lsplit) > 2:
        if lsplit[1].lower() == 'context':
          build_context = lsplit[2]
        elif lsplit[1].lower() == 'source' and lsplit[2] not in external_images:
          external_images.append(lsplit[2])

  args = []
  started = False
  for linex in stage_text.splitlines(): # TODO would be nice to preserve backslash continuation lines as one line
    line = linex.strip()
    if line.startswith('#'): continue         # need this
    line = line_before_escape(line)           # All characters before unescaped # (comments)
    m = re.match(COPY_STAGE_A, line)
    if not m:
      m = re.match(COPY_STAGE_B, line)
      if m: started = True
    if m and 'stage:'+m.group(1) not in dependency and m.group(1) not in external_images:
      dependency.append('stage:'+m.group(1))  # add dependency
    if started: # For multistage builds only get args AFTER FROM (only these will work)
      m = re.match(r'^[\s]*arg[\s]+(.+)',line,re.I)
      if m:
        argline = line_before_escape(m.group(1)).split('=',1)
        argkey = argline[0].strip()
        argval = argline[1].strip() if len(argline) > 1 else ''
        if argkey not in [a['key'] for a in args]:
          args.append({'key':argkey, 'value':remove_quotes(argval)}) 
  return (dependency, args, build_context)

def parse(namein, pth, items):
  name = namein.lower() # Stages must be unique case insensitively
  stage_text = Path(pth).read_text()
  secrets = []
  ssh = []
  for line in stage_text.splitlines():
    m = re.search(r'--mount=type=secret(.+)',line,re.I | re.M)
    if m:
      m = re.search(r'id=([^\s]+)',m.group(1),re.I | re.M)
      if m and m.group(1) not in secrets:
        secrets.append(m.group(1))
    m = re.search(r'--mount=type=ssh(.+)',line,re.I | re.M)
    if m:
      m = re.search(r'id=([^\s]+)',m.group(1),re.I | re.M)
      if m and m.group(1) not in ssh:
        ssh.append(m.group(1))
  type_name = 'stage:'+name
  (dependency, args, build_context) = dependencies(stage_text)
  (build_context,deps) = parse_build_context(name, pth, build_context.strip(), items)
  if build_context == False:
    return False
  else:
    dependency += deps
    item = {'name':name,
      'thingtype':'stage',
      'path':pth,
      'args':args,
      'secrets':secrets,
      'ssh':ssh,
      'build_context':str(build_context),
      'depends_on':dependency,
      'loaded':True
    }
    vytools.utils._check_self_dependency(type_name, item)
    return utils._add_item(item, items, VALIDATE)

TAGSAFE = lambda v : re.sub(r'[^a-zA-Z0-9\-\_]','_',v)
ARGTAG = lambda k,a : TAGSAFE(k) + '.' + TAGSAFE(a[k])
def taglist(_stage_name_, items):
  stage = items[_stage_name_]
  my_dep_args = [sa['key'] for sa in stage['args']]
  for s in stage['depends_on']:
    if s.startswith('stage:'):
      my_dep_args += [a for a in taglist(s, items) if a not in my_dep_args]
  return my_dep_args

def stage_args(stage_name, items, build_arg_dict=None):
  if build_arg_dict is None: build_arg_dict = {}
  my_dep_args = taglist(stage_name, items)
  this_args = {}
  for key in my_dep_args:
    if key in build_arg_dict:
      this_args[key] = build_arg_dict[key]
    else:
      vytools.printer.print_fail('Building {s} requires setting build argument "{b}"'.format(s=stage_name,b=key))
      return False
  return this_args

def stage_prefix(stage_name):
  return 'vy__' + stage_name.replace('stage:','',1).lower()

def stages(stage_item):
  cmd = ['docker','images','--filter=reference=' + stage_prefix(stage_item) + ':*','--format','{{.Repository}}:{{.Tag}}']
  return subprocess.check_output(cmd).decode('utf-8').strip().split()

def stage_tag(stage_name, items, build_arg_dict=None):
  this_args = stage_args(stage_name, items, build_arg_dict)
  if this_args == False: return (False,False)
  keys = list(this_args.keys())
  keys.sort()
  lst = [ARGTAG(key, this_args) for key in keys]
  tag = stage_prefix(stage_name) + (':' + '.'.join(lst) if len(lst) > 0 else ':latest')
  return (tag, this_args)

def get_built_stage_repos(tag):
  cmd = ['docker', 'inspect', '--format', '\'{{ index .Config.Labels "tools.vy.repos"}}\'', tag]
  try:
    vyreposi = subprocess.check_output(cmd).decode('utf-8').strip().strip("'")
    return [] if len(vyreposi) == 0 else vyreposi.split(',')
  except Exception as exc:
    vytools.printer.print_def(' '.join(cmd)+'\n'+repr(exc))
  return []

def get_built_stage_versions(stage, items, build_args, checked):
  def _get_built_stage_versions(type_name, checked, top):
    if type_name not in items or not type_name.startswith('stage:'):
      return []
    item = items[type_name]
    tag, this_args = stage_tag(type_name, items, build_arg_dict=build_args)
    if tag and tag in checked:
      return checked[tag].copy()
    elif tag:
      stage_versions = []
      for d in item['depends_on']: 
        stage_versions += [sv for sv in _get_built_stage_versions(d, checked, False) if sv not in stage_versions]
      if not top:
        stage_versions += [sv for sv in get_built_stage_repos(tag) if sv not in stage_versions]
      else:
        # stages can depend on their own path and possibly vydirs
        pths = [item['path']] + [items[d]['path'] for d in item['depends_on'] if d.startswith('vydir:')]
        for pth in pths:
          repo = utils.get_repo_from_path(pth, items.get('info:repository_path_list',None))
          if repo in items:
            this_stage_repostr = utils.repo_version_string(items[repo])
            if this_stage_repostr not in stage_versions:
              stage_versions.append(this_stage_repostr)

      checked[tag] = stage_versions.copy()
      return stage_versions

  stage_versions = _get_built_stage_versions('stage:' + stage['name'], checked, True)
  return sorted(stage_versions)

def __build__(stage, already_tagged, build_arg_dict, items, checked_versions, jobpath=None):
  if jobpath is None: jobpath = CONFIG.job_path()
  if not jobpath:
    return False, []
  ok,secret_cmds = CONFIG.secrets_cmd(stage['secrets'],stage['ssh'])
  if not ok:
    vytools.printer.print_fail('Failed to build '+stage['name'])
    return False, []

  stage_name = 'stage:'+stage['name']
  if not vytools.utils.ok_dependency_loading('build', stage_name, items):
    return False

  dfile_dir = os.path.join(jobpath,'__dockerfiles__')
  os.makedirs(dfile_dir, exist_ok=True)

  contents = Path(stage['path']).read_text() # use semicolon for windows friendly
  text = '# syntax=docker/dockerfile:experimental\n'
  for (k,v) in build_arg_dict.items():
    text += 'ARG {k}="{v}"\n'.format(k=k,v=v)
  dep_stage_ids = []
  for s in stage['depends_on']:
    if s.startswith('stage:'):
      st = already_tagged[s]
      dep_stage_ids.append(st['tag']+'='+DOCKER_CLIENT.images.get(st['tag']).attrs['Id'])
      text += 'FROM {t} as {s}\n'.format(t=st['tag'], s=st['name'])
  for line in contents.splitlines(): #TODO nice to preserve backslash continuation
    text += line+'\n'
    if re.search(r'^[\s]*FROM ',line,re.I):
      text += 'LABEL tools.vy.remove=true\nLABEL tools.vy.tag=-\n'

  tag = already_tagged[stage_name]['tag']
  stage_versions = get_built_stage_versions(stage, items, build_arg_dict, checked_versions)
  text += 'LABEL tools.vy.repos={}\n'.format(','.join(stage_versions))
  text += 'LABEL tools.vy.images="{}"\n'.format(','.join(dep_stage_ids))
  text += 'LABEL tools.vy.tag={}\n'.format(tag)
  text += '# ----------------------------------------\n\n\n'

  build_context = stage['build_context']
  df = os.path.join(dfile_dir, tag.replace(':',';')+'.dockerfile') # semi-colon for windows friendly
  with open(df,'w') as w: w.write(text)
  cmd = ['docker', 'build', '--force-rm', '-f', df, '-t', tag]  # don't tag because of cleanup , '-t', node['s['tag']']
  cmd += ['--progress=plain']
  for (k,v) in build_arg_dict.items():
    cmd += ['--build-arg',k+'='+v]
  cmd += secret_cmds + [build_context]
  
  # vytools.printer.print_info(' '.join(cmd)+'\n\n'+text)
  with open(df+'.log','w') as logfile:
    vytools.printer.print_def(' '.join(cmd))
    kwargs = {'stdout':subprocess.PIPE,'stderr':subprocess.STDOUT,'universal_newlines':True}
    if sys.platform != 'win32': kwargs['env'] = {'DOCKER_BUILDKIT':'1'}
    proc = subprocess.Popen(cmd, **kwargs)
    for line in proc.stdout:
      vytools.printer.print_def(line.strip(),fp=logfile)
    proc.wait()

  success = proc.returncode == 0
  if success:
    already_tagged[stage_name]['hash'] = subprocess.check_output(['docker','inspect','--format','{{.ID}}',tag]).decode('utf-8').strip()
    clean_up(['dangling=true','label=tools.vy.tag='+tag])
    # os.remove(df)
  else:
    vytools.printer.print_fail('Failed to build '+tag)
  return success, stage_versions

def sorted_vy_images(filters):
  cmd = ['docker','images']
  for f in filters:
    cmd += ['--filter',f]
  cmd += ['--format','{{.CreatedAt}}\t{{.ID}}\t{{.Repository}}\t{{.Tag}}']
  imlist = subprocess.check_output(cmd).decode('utf8').strip()
  if len(imlist) > 0:
    images = []
    for im in imlist.split('\n'):
      imageid = im.split('\t')
      images.append({'created':imageid[0], 'id':imageid[1], 'repst':imageid[2], 'tag':imageid[3]})
    return sorted(images, key=lambda k: k['created'], reverse=True) # Most recent first
  return []

def prune():
  subprocess.run(['docker','builder','prune','-f']) # Todo, why do I need this? Why is their a build cache when everything builds successfully?

def clean_up(filters):
  prune()
  untagged = [im['id'] for im in sorted_vy_images(filters)]
  untagged.reverse()
  if len(untagged) > 0:
    while True:
      try:
        vytools.printer.print_info('Attempting to remove dangling images:'+str(untagged))
        subprocess.check_output(['docker','rmi']+untagged)
        break
      except Exception as exc:
        vytools.printer.print_warn(str(exc))
        time.sleep(5)

def find_all(items, contextpaths=None):
  # r'[.]*dockerfile[.]*'
  return utils.search_all(r'(.+)\.stage\.dockerfile', parse, items, contextpaths=contextpaths)

def build(stages, items, anchors, already_built, build_level, jobpath=None):
  # build_level = 1 # Rebuild all - unless you've already
  # build_level = 0 # Rebuild top level - unless you've already sometime 
  # build_level = -1 # Don't build anything
  if not utils.exists(stages, items):
    vytools.printer.print_fail('  Failed to build {}'.format(stages))
    return False

  existing_images = [im['repst']+':'+im['tag'] for im in sorted_vy_images(['label=tools.vy.tag'])]
  checked_versions = {}
  already_tagged = {}
  def __multistage__(stage_name):
    if not stage_name.startswith('stage:'):
      return True
    stage = items[stage_name]
    for s in stage['depends_on']:
      if __multistage__(s) == False: return False
    if stage_name not in already_tagged:
      tag,this_args = stage_tag(stage_name, items, anchors)
      if not tag: return False
      already_tagged[stage_name] = {'tag':tag,'name':stage['name'],'skipped':False,'stage_versions':[]}
      oktobuild = ((build_level == 0 and stage_name in stages) or
                  (build_level == 1) or (tag not in existing_images)) and tag not in already_built
      if oktobuild:
        vytools.printer.print_info(' * Building: {s} --as-- {i}'.format(s=stage_name,i=tag))
        success, stage_versions = __build__(stage, already_tagged, this_args, items, checked_versions, jobpath) # Build this stage
        if not success:
          vytools.printer.print_fail(' * Failed {s} --as-- {i}'.format(s=stage_name,i=tag))
          return False
        if stage_versions:
          already_tagged[stage_name]['stage_versions'] = stage_versions
        already_built.append(tag)
        vytools.printer.print_success(' * Finished: {s} --as-- {i}\n\n'.format(s=stage_name,i=tag))
      elif tag not in already_built:
        already_tagged[stage_name]['stage_versions'] = get_built_stage_versions(stage, items, this_args, checked_versions)
      else:
        already_tagged[stage_name]['skipped'] = True
        # # I think this is cumbersome/notuseful printing
        # if tag not in already_built:
        #   vytools.printer.print_info('* Skipping: {s} as {i}'.format(s=stage_name,i=tag))
        # else: 
        #   vytools.printer.print_info('* Already built: {s} as {i}'.format(s=stage_name,i=tag))
    return True

  for top_name in stages:
    if False == __multistage__(top_name):
      return False

  if build_level != -1:
    for tag in already_tagged:
      if not already_tagged[tag]['skipped']:
        vytools.printer.print_success(' * Built {n} --as-- {t}'.format(n=tag,t=already_tagged[tag]['tag']))
      # else: # I think this is cumbersome/notuseful printing
        # vytools.printer.print_info(' * Skipped {n} as {t}'.format(n=tag,t=already_tagged[tag]['tag']))
  return already_tagged #sum([int(v['hash'],16) for v in already_tagged.values()])

def run(type_name, items=None, anchors=None, jobpath=None, cmd=None):
  if items is None: items = ITEMS
  if not vytools.utils.ok_dependency_loading('run', type_name, items):
    return False

  if anchors is None: anchors = {}
  already_built = []
  built = build([type_name], items, anchors, already_built, -1, jobpath=jobpath)
  if built and type_name in built:
    if jobpath is None: jobpath = CONFIG.job_path()
    if not jobpath:
      return False
    tag = built[type_name]['tag']
    datadir = os.path.join(jobpath,'__data__')
    os.makedirs(datadir,exist_ok=True)
    vytools.printer.print_info('** Running {t} with "{p}" mounted to "/__vydata__" in the container'.format(t=tag,p=datadir))
    dcmd = ['docker','run','--rm', '-it', '-v', datadir+':/__vydata__', tag]
    if cmd is not None: 
      dcmd += shlex.split(cmd)
    proc = subprocess.run(dcmd,stderr=subprocess.STDOUT)
    # else:
    #   volumes = {}
    #   volumes[datadir] = {'bind':'/__vydata__','mode':'rw'}
    #   x=DOCKER_CLIENT.containers.run(tag,cmd,remove=True,volumes=volumes)
    #   print(x)