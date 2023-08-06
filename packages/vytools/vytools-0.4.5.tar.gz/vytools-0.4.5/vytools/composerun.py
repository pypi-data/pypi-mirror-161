
import subprocess, os, shutil, signal, copy, json
import vytools.utils
import vytools.printer
import vytools.compose
from vytools.stage import DOCKER_COMPOSE
from vytools.config import ITEMS, CONFIG

global SHUTDOWN
SHUTDOWN = {}
def _shutdown_reset():
  global SHUTDOWN
  SHUTDOWN['path'] = ''
  SHUTDOWN['down'] = []
  SHUTDOWN['logs'] = []
  SHUTDOWN['services'] = []
  
_shutdown_reset()

def stop():
  logs = subprocess.run(SHUTDOWN['logs'], cwd=SHUTDOWN['path'], stdout=subprocess.PIPE)
  subprocess.run(SHUTDOWN['down'], cwd=SHUTDOWN['path'])
  _shutdown_reset()
  return logs

def compose_exit_code(eppath):
  success = True
  try:
    anyzeros = False
    if not os.path.isdir(eppath):
      return False
    services = subprocess.check_output(SHUTDOWN['services'], 
        cwd=SHUTDOWN['path']).decode('utf8').strip().split('\n')
    for service in services:
      try:
        exitcode = subprocess.check_output(['docker', 'container', 'inspect',service,'--format','{{.State.ExitCode}}']).decode('utf8').strip()
      except Exception as exc:
        success = False
        exitcode = '1'
        vytools.printer.print_fail('Failed to get exit code for {s}: {e}'.format(s=service, e=exc))
      anyzeros |= int(exitcode) == 0
      vytools.printer.print_info('---- Service '+service+' exited with code '+exitcode)
    return success and anyzeros
  except Exception as exc:
    vytools.printer.print_fail('Failed to get exit codes'+str(exc))
    return False

ORIGINAL_SIGINT = signal.getsignal(signal.SIGINT)
def exit_gracefully(signum, frame):
  signal.signal(signal.SIGINT, ORIGINAL_SIGINT) # restore the original signal handler
  # logs = stop()
  #sys.exit(signum) # TODO is this right? pass out signum?

def runpath(epid, jobpath=None):
  if jobpath is None: jobpath = CONFIG.job_path()
  return os.path.join(jobpath,epid) if epid and jobpath else None

def run(epid, compose_name, items=None, anchors=None, clean=False, object_mods=None, jobpath=None, dont_track=None, persist=False):
  if anchors is None: anchors = {}
  if object_mods is None: object_mods = {}
  global SHUTDOWN
  epidupper = epid
  epid = epid.lower()
  if items is None: items = ITEMS
  if not vytools.utils.ok_dependency_loading('run', compose_name, items):
    return False

  # TODO test epid, lower case, alphanumeric starts with alpha?
  eppath = runpath(epid,jobpath)
  if not eppath: return False

  if clean:
    try:
      shutil.rmtree(eppath)
    except Exception as exc:
      vytools.printer.print_fail('Failed to clean folder {n}'.format(n=eppath))
      return False

  os.makedirs(eppath,exist_ok=True)
  built = []
  # Compile compose files and any volumes
  cbuild = vytools.compose.build(compose_name, items=items, anchors=copy.deepcopy(anchors),
            built=built, build_level=-1, object_mods=object_mods, eppath=eppath) # get components
  if cbuild == False: return False
  if eppath and os.path.exists(eppath):
    with open(os.path.join(eppath, 'vyanchors.json'),'w') as w:
      json.dump(cbuild['anchors'],w,sort_keys=True,indent=1)

  cmd = DOCKER_COMPOSE + cbuild['command'] + ['--project-name', epid]
  cmdup = cmd+['up', '--abort-on-container-exit']
  SHUTDOWN['down'] = cmd + ['down']
  if not persist: SHUTDOWN['down'] += ['--volumes']
  SHUTDOWN['jobid'] = epid
  SHUTDOWN['path'] = eppath
  SHUTDOWN['logs'] = cmd + ['logs']
  SHUTDOWN['services'] = cmd + ['ps','-q']
  try:
    signal.signal(signal.SIGINT, exit_gracefully)
  except Exception as exc:
    vytools.printer.print_warn(str(exc))
    
  with open(os.path.join(eppath,'start.sh'),'w') as w2:
    w2.write(' '.join(cmdup))

  vytools.printer.print_info('Episode Path = '+eppath)
  with open(os.path.join(eppath,'logs.txt'),'w') as logfile:
    proc = subprocess.Popen(cmdup, cwd=eppath, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in proc.stdout:
      vytools.printer.print_def(line.strip(),fp=logfile)
    proc.wait()
  
  compose_exit = compose_exit_code(eppath)
  stop()
  
  repo_versions = vytools.utils.get_repo_versions(cbuild['dependencies'], items)
  stage_versions = cbuild['stage_versions']
  passed = compose_exit and proc.returncode == 0

  with open(os.path.join(eppath,'logs.txt'),'a') as logfile:
    color = vytools.printer.SUCCESSCOLOR if passed else vytools.printer.FAILCOLOR
    vytools.printer.print_def('Test "{}" {} and was built/run from the following'.format(epidupper,'passed' if passed else 'failed'), color=color, fp=logfile)
    if dont_track and dont_track in repo_versions:
      this_repo_version = repo_versions[dont_track]
      stage_versions = [sv for sv in stage_versions if sv != this_repo_version]
      vytools.printer.print_def(' - "episode" repositories|versions:',fp=logfile)
      vytools.printer.print_plus('   - '+this_repo_version, fp=logfile)
      del repo_versions[dont_track] # Remove the repository containing this episode

    vytools.printer.print_def(' - "dependency" repositories|versions:', fp=logfile)

    sorted_repo_versions = sorted([v for v in repo_versions.values()])
    for v in sorted_repo_versions:
      vytools.printer.print_plus('   - '+v, fp=logfile)
    vytools.printer.print_def(' - "stage" repositories|versions:', fp=logfile)
    others = [k for k in stage_versions if k not in sorted_repo_versions]
    for v in others:
      vytools.printer.print_plus('   - '+v, fp=logfile)

  return {
    'compose':compose_name,
    'repos':sorted_repo_versions,
    'stage_repos':others,
    'passed':passed,
    'object_mods':object_mods,
    'anchors':anchors,
    'artifact_paths':vytools.compose.artifact_paths(compose_name, items=items, eppath=eppath)
  }
