import common                   # app common functions

import os                       # for os data, filesystem manipulation
import platform                 # for python data
import subprocess               # for running shell commands
import sys                      # for system commands
import traceback                # for errors
from my_path import get_py_path # pathing help

env = common.prepare_env()  # get environment variables

WIDTH = 60 # width for labels

PYTHON_EXECUTABLE = os.path.splitext(sys.executable.split(os.path.sep).pop())[0]  # get command to run python
PYTHON_VERSION = sys.version.split(" ")[0]                                        # get python version
PYTHON_MINOR_VERSION = '.'.join(PYTHON_VERSION.split(".")[:2])                    # get python major.minor version

# get python debug info
def do_python(args):
  ret = subprocess.run([ *args, "--version" ], capture_output=True, text=True)
  if ret.stdout.strip():
    PYTHON_VERSION = ret.stdout.strip().split(" ")[1]
    PY_STRING = (
      "%s\t%s\t%s"
      %
      (
        isinstance(args[0], list) and " ".join(args[0]) or args[0],
        PYTHON_VERSION,
        sys.platform
      )
    )
    print(PY_STRING)
    print('.' * WIDTH)

# get pip debug info
def do_pip(args, PIPEXE):
  ret = subprocess.run([ *args, "-m", PIPEXE, "--version" ], capture_output=True, text=True)
  if ret.stdout.strip():
    if " from " in ret.stdout.strip():
      PIP_VERSION = ret.stdout.strip().split(" from ")[0].split(" ")[1]
      if PIP_VERSION:
        PIP_LATEST = "???" # remember to do something with this...
        PIP_STRING = (
          "%s\t%s\t%s\t%s\t%s\t%s"
          %
          (
            isinstance(args[0], list) and " ".join(args[0]) or args[0],
            PYTHON_VERSION,
            sys.platform,
            PIP_EXECUTABLE,
            PIP_VERSION,
            PIP_LATEST
          )
        )
        print(PIP_STRING)
        print('.' * WIDTH)

# print python debug info
heading = (
  "%s-%s-%s"
  %
  (
    PYTHON_EXECUTABLE,
    PYTHON_VERSION,
    sys.platform
  )
)
print(heading)
print('=' * WIDTH)

PYTHON_PATH = env["PYTHON_EXE_PATH"]  # path to python
PIP_PATH = env["PIP_EXE_PATH"]        # path to pip

# figure out pip executable
PIP_EXECUTABLE = "pip" if "windows" in env["OS_NAME"] else "pip3"
PIP_EXECUTABLE = "pip" if "osx" in env["OS_NAME"] and "actions" in env["CI_SYSTEM"] else PIP_EXECUTABLE

PIP_VERSION = "" # holder for pip's version

# process entrando & spritesomething, or arg from commandline
APPS = ["entrando","spritesomething"]
if len(sys.argv) > 1:
  APPS = [ sys.argv[1] ]

# foreach app
for APP in APPS:
  # print app name
  print(APP)
  print('-' * WIDTH)
  # foreach py executable
  for PYEXE in ["py","python3","python"]:
    args = []
    # if it's the py launcher, specify the version
    if PYEXE == "py":
      PYEXE = [ PYEXE, "-" + PYTHON_MINOR_VERSION]
      # if it ain't windows, skip it
      if "windows" not in env["OS_NAME"]:
        continue

    # build executable command
    if isinstance(PYEXE, list):
      args = [ *PYEXE ]
    else:
      args = [ PYEXE ]

    try:
      do_python(args) # print python debug data

      # foreach py executable
      for PIPEXE in ["pip","pip3"]:
        do_pip(args, PIPEXE)        # print pip debug data
        # upgrade pip
        ret = subprocess.run([ *args, "-m", PIPEXE, "install", "--upgrade", "pip" ], capture_output=True, text=True)
        # get output
        if ret.stdout.strip():
          # if it's not already satisfied, update it
          if "already satisfied" not in ret.stdout.strip():
            print(ret.stdout.strip())
            do_pip(args, PIPEXE)

        # install modules from list
        ret = subprocess.run([ *args, "-m", PIPEXE, "install", "-r", os.path.join(
          ".",
          "resources",
          "app",
          "meta",
          "manifests",
          "pip_requirements_" + APP + ".txt"
        )], capture_output=True, text=True)

        # if there's output
        if ret.stdout.strip():
          for line in ret.stdout.strip().split("\n"):
            # if there's an error, print it and bail
            if "status 'error'" in line.strip():
              print(
                "[%s] %s"
                %
                (
                  "_",
                  line.strip()
                )
              )
              exit(1)
            # if it's already satisfied or building a wheel, print version data
            elif "already satisfied" in line.strip() or \
              "Building wheel" in line.strip() or \
              "Created wheel" in line.strip():
              satisfied = line.strip().split(" in ")
              sver = ((len(satisfied) > 1) and satisfied[1].split("(").pop().replace(")","")) or ""
              print(
                (
                  "[%s] %s\t%s"
                  %
                  (
                    "X",
                    satisfied[0],
                    sver
                  )
                )
              )
            # ignore lines about certain things
            elif "Collecting" in line.strip() or \
              "Downloading" in line.strip() or \
              "eta 0:00:00" in line.strip() or \
              "Preparing metadata" in line.strip() or \
              "Stored in" in line.strip():
              pass
            # else, I don't know what it is, print it
            else:
              print(line.strip())
          print("")
    # if something else went fucky, print it
    except Exception as e:
      traceback.print_exc()
