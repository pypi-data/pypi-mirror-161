import os, json, re
import vytools.printer
from pathlib import Path

_FOLDER = os.path.dirname(os.path.realpath(__file__))
_CONFIGFILE = os.path.join(_FOLDER,'vyconfig.json')
_FIELDS = ['contexts','items','jobs','menu','secrets','ssh','scanned']
SEARCHED_REPO_PATHS = {}
ITEMS = {}
ITEMTYPES = ['repo','vydir','definition','object','stage','compose','episode','bundle','nodule']
KEYMATCH = re.compile("^[A-Za-z_0-9]+$")


def check_folder(field,values):
  success = True
  for v in values:
    if not os.path.isdir(v):
      vytools.printer.print_fail('The path "{v}" is not a directory. Create this directory before setting it as your "{f}" directory'.format(v=v,f=field))
      success = False
  return success

class __CONFIG:
  def __init__(self):
    # // 'BITBUCKET_SSH':'/home/nate/.ssh/bitbucketnopassphrase'
    self._data = {}
    try:
      self._data = json.loads(Path(_CONFIGFILE).read_text().strip())
    except:
      pass
  
  def __write(self):
    with open(_CONFIGFILE,'w') as w:
      w.write(json.dumps(self._data))

  def set(self,field,value):
    if field in _FIELDS:
      if field in ['contexts','scanned']:
        if value is None and field == 'scanned':
          self._data[field] = value
        elif check_folder(field, value):
          self._data[field] = [str(Path(v).resolve()) for v in value]
      elif field == 'jobs':
        if check_folder(field, [value]):
          self._data[field] = str(Path(value).resolve())
          ign = os.path.join(self._data[field],'.vyignore')
          if not os.path.exists(ign):
            with open(ign,'w'): pass
      elif field == 'ssh':
        if 'ssh' not in self._data: self._data['ssh'] = {}
        self._data['ssh'].update({k:v for k,v in value.items() if KEYMATCH.search(k)}) # update everything
        self._data['ssh'] = {k:v for k,v in self._data['ssh'].items() if KEYMATCH.search(k) and v != '-'} #remove '-'
      elif field == 'secrets':
        if 'secrets' not in self._data: self._data['secrets'] = {}
        self._data['secrets'].update({k:v for k,v in value.items() if KEYMATCH.search(k)}) # update everything
        self._data['secrets'] = {k:v for k,v in self._data['secrets'].items() if KEYMATCH.search(k) and v != '-'} #remove '-'
      else: # menu, items
        self._data[field] = value
      self.__write()

  def get(self,field):
    return self._data[field] if self._data and field in self._data else None

  def secrets_cmd(self, secret_list, ssh_list):
    cmd = []
    ok = True
    lists = {'secret':secret_list, 'ssh':ssh_list}
    for typ,lst in lists.items():
      for secret in lst:
        if typ == 'secret' and 'secrets' in self._data and secret in self._data['secrets']:
          cmd += ['--secret','id='+secret+',src='+self._data['secrets'][secret]]
        elif typ == 'ssh' and 'ssh' in self._data and secret in self._data['ssh']:
          cmd += ['--ssh',secret+'='+self._data['ssh'][secret]]
        else:
          if typ == 'secret':
            msg = '\n  Secret "{s}" has not been configured. (vytools config --help)\n'.format(s=secret)
            vytools.printer.print_fail(msg)
          else:
            msg = '\n  Ssh key "{s}" has not been configured (vytools config --help)\n'.format(s=secret)
            vytools.printer.print_fail(msg)
          ok = False
    return (ok, cmd)

  def info(self, list_private=False):
    vytools.printer.print_def('VyTools Configuration & Summary:', attrs=['bold'])
    vytools.printer.print_def('  Configuration saved at: '+_CONFIGFILE)
    vytools.printer.print_def('  Contexts = {s}'.format(s=','.join(self.get('contexts'))))
    if list_private:
      for ss in ['ssh','secrets']:
        for k,v in self._data.get(ss,{}).items():
          vytools.printer.print_def('  Private file ({t}) {k} @ {v}'.format(t=ss,k=k,v=v))
    jobpath = self.job_path()
    if jobpath:
      vytools.printer.print_def('  Jobs at {s}'.format(s=jobpath))
    vytools.printer.print_def('  Items found:')
    items = self.get('items')
    typs = {}
    if items:
      for i in items:
        typ = i.split(':')[0]
        if typ not in typs: typs[typ] = 0
        typs[typ] += 1
    for typ in typs:
      vytools.printer.print_def('    - {n} {t} items'.format(t=typ,n=typs[typ]))

  def job_path(self):
    jp = self.get('jobs')
    if not jp:
      failmsg = 'No jobs path specified, specify path with vytools --jobs , (e.g. "vytools --jobs path/to/folder/for/jobs" info)'
      vytools.printer.print_fail(failmsg)
      vytools.printer.print_fail(failmsg)
      return None
    return jp

CONFIG = __CONFIG()

