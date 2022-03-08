import common

import os
import platform
import subprocess
import sys
import traceback
from my_path import get_py_path

env = common.prepare_env()

WIDTH = 60

PYTHON_EXECUTABLE = os.path.splitext(sys.executable.split(os.path.sep).pop())[0]
PYTHON_VERSION = sys.version.split(" ")[0]
PYTHON_MINOR_VERSION = '.'.join(PYTHON_VERSION.split(".")[:2])

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

def do_pip(args, PIPEXE):
  ret = subprocess.run([ *args, "-m", PIPEXE, "--version" ], capture_output=True, text=True)
  if ret.stdout.strip():
    if " from " in ret.stdout.strip():
      PIP_VERSION = ret.stdout.strip().split(" from ")[0].split(" ")[1]
      if PIP_VERSION:
        PIP_STRING = (
          "%s\t%s\t%s\t%s\t%s"
          %
          (
            isinstance(args[0], list) and " ".join(args[0]) or args[0],
            PYTHON_VERSION,
            sys.platform,
            PIP_EXECUTABLE,
            PIP_VERSION
          )
        )
        print(PIP_STRING)
        print('.' * WIDTH)

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

PYTHON_PATH = env["PYTHON_EXE_PATH"]
PIP_PATH = env["PIP_EXE_PATH"]
PIP_EXECUTABLE = "pip" if "windows" in env["OS_NAME"] else "pip3"
PIP_EXECUTABLE = "pip" if "osx" in env["OS_NAME"] and "actions" in env["CI_SYSTEM"] else PIP_EXECUTABLE
PIP_VERSION = ""

APPS = ["entrando","spritesomething"]
if len(sys.argv) > 1:
  APPS = [ sys.argv ]

for APP in APPS:
  print(APP)
  print('-' * WIDTH)
  for PYEXE in ["py","python","python3"]:
    args = []
    if PYEXE == "py":
      PYEXE = [ PYEXE, "-" + PYTHON_MINOR_VERSION]
      if "windows" not in env["OS_NAME"]:
        continue
    if isinstance(PYEXE, list):
      args = [ *PYEXE ]
    else:
      args = [ PYEXE ]
    try:
      do_python(args)
      for PIPEXE in ["pip","pip3"]:
        do_pip(args, PIPEXE)
        ret = subprocess.run([ *args, "-m", PIPEXE, "install", "--upgrade", "pip" ], capture_output=True, text=True)
        if ret.stdout.strip():
          if "already satisfied" not in ret.stdout.strip():
            print(ret.stdout.strip())
            do_pip(args, PIPEXE)
        ret = subprocess.run([ *args, "-m", PIPEXE, "install", "-r", os.path.join(
          ".",
          "resources",
          "app",
          "meta",
          "manifests",
          "pip_requirements_" + APP + ".txt"
        )], capture_output=True, text=True)
        if ret.stdout.strip():
          for line in ret.stdout.strip().split("\n"):
            if "status 'error'" in line.strip():
              print(
                "[%s] %s"
                %
                (
                  "X",
                  line.strip()
                )
              )
              exit(1)
            elif "already satisfied" in line.strip() or "Building wheel" in line.strip():
              satisfied = line.strip().split(" in ")
              sver = ((len(satisfied) > 1) and satisfied[1].split("(").pop().replace(")","")) or ""
              print(
                (
                  "[%s] %s\t%s"
                  %
                  (
                    "✓",
                    satisfied[0],
                    sver
                  )
                )
              )
            else:
              print(line.strip())
          print("")
    except Exception as e:
      traceback.print_exc()
