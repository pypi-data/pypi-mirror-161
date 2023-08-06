# vytools: Tools for distributed continuous integration 

## Installation and Setup

```bash
pip install vytools
```
or often
```bash
pip3 install vytools
```

To take advantage of autocompletion add the following to your ~/.bashrc file 

```bash
eval "$(register-python-argcomplete vytools)"
```

## Configuration

vytools searches a set of directories for specialized "vy" components. These directories comprise the vy "context" which must be specified before vy can be used. In addition a "jobs" directory will need to be specified. You can also configure "secrets".

### CONTEXT PATHS [required configuration]

Point to directories (comma or semi-colon delimited) which contain the vy components with command line:
```bash
vytools --contexts "/some/path/to/contexts/dir,/path/to/another/contexts/dir"
```

Or in a python script
```python
import vytools
vytools.CONFIG.set('contexts',['/some/path/to/contexts/dir','/path/to/another/contexts/dir'])
```

### JOBS [required configuration]
Vy places artifacts from each job into a jobs directory. Point to a default directory which will be populated with jobs artifacts:

```bash
vytools --jobs "/some/path/to/jobs/dir"
```

or use python
```python
import vytools
vytools.CONFIG.set('jobs','/some/path/to/jobs/dir')
```

### SECRETS [optional configuration]

Set a secret id (e.g. SECRETA and SECRETB) or private ssh key (e.g. MYSSHKEY) and point to files containing the docker build secrets associated with those ids or private ssh keys with command line:
```bash
vytools --secret SECRETA="/some/path/to/secrets/dir/secreta.txt" --secret SECRETB="/path/to/anothersecret" --ssh MYSSHKEY=/home/user/.ssh/mysecretkey
```

Or in a python script
```python
import vytools
vytools.CONFIG.set('secrets',{'SECRETA':'/some/path/to/secrets/dir/secreta.txt','SECRETB':'/path/to/anothersecret'})
vytools.CONFIG.set('ssh',{'MYSSHKEY':'/home/user/.ssh/myprivatekey'})
```

The secret files can be used with [docker build secrets](https://docs.docker.com/develop/develop-images/build_enhancements/#new-docker-build-secret-information). For example the above secrets could be used as follows without exposing the secret in the build cache:

```dockerfile
RUN --mount=type=secret,id=SECRETA wget --header="Authorization: Bearer $(cat /run/secrets/SECRETA)" https://some_url/some_artifact.tar.gz
RUN --mount=type=ssh,id=MYSSHKEY git clone git@github.com:username/repo.git
```
