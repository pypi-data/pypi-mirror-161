from termcolor import cprint
import os
import logging
logging.basicConfig(level=logging.INFO)

INFOCOLOR = 'cyan'
SUCCESSCOLOR = 'green'
FAILCOLOR = 'red'
WARNCOLOR = 'yellow'

BUFFER = None
def set_buffer(buffer):
  global BUFFER
  BUFFER = buffer

def printer__(strng, color=None, attrs=None, fp=None):
  if attrs is None: attrs = []
  if fp:
    fp.write(strng+os.linesep)

  if BUFFER is not None:
    BUFFER.append(strng)
  if color or attrs:
    cprint(strng, color=color, attrs=attrs)
  else:
    print(strng)

def print_def(strng, attrs=None, color=None, fp=None):
  printer__(strng, attrs=attrs, color=color, fp=fp)

def print_plus(strng, fp=None):
  color = WARNCOLOR if strng.endswith('+') else SUCCESSCOLOR
  printer__(strng, color=color, fp=fp)

def print_warn(*argv):
  # logging.warning(' '.join([str(a) for a in argv]))
  printer__(' '.join(argv),color=WARNCOLOR)

def print_info(*argv):
  # logging.info(' '.join([str(a) for a in argv]))
  printer__(' '.join(argv),color=INFOCOLOR)

def print_success(*argv):
  # logging.info(' '.join([str(a) for a in argv]))
  printer__(' '.join(argv),color=SUCCESSCOLOR)

def print_fail(*argv):
  # logging.error(' '.join([str(a) for a in argv]))
  printer__(' '.join(argv),color=FAILCOLOR)
