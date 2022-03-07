import common

import os
import platform
import subprocess
import sys
from my_path import get_py_path

env = common.prepare_env()

PYTHON_EXECUTABLE = os.path.splitext(sys.executable.split(os.path.sep).pop())[0]
PYTHON_VERSION = sys.version.split(" ")[0]
PYTHON_MINOR_VERSION = '.'.join(PYTHON_VERSION.split(".")[:2])

def do_python(args):
  ret = subprocess.run([ *args, "--version" ], capture_output=True, text=True)
  if ret.stdout.strip():
    PYTHON_VERSION = ret.stdout.strip().split(" ")[1]
    print(
      "%s\t%s\t%s"
      %
      (
        isinstance(args[0], list) and " ".join(args[0]) or args[0],
        PYTHON_VERSION,
        sys.platform
      )
    )

def do_pip(args, PIPEXE):
  ret = subprocess.run([ *args, "-m", PIPEXE, "--version" ], capture_output=True, text=True)
  if ret.stdout.strip():
    if " from " in ret.stdout.strip():
      PIP_VERSION = ret.stdout.strip().split(" from ")[0].split(" ")[1]
      if PIP_VERSION:
        print(
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
print('=' * len(heading))

PYTHON_PATH = env["PYTHON_EXE_PATH"]
PIP_PATH = env["PIP_EXE_PATH"]
PIP_EXECUTABLE = "pip" if "windows" in env["OS_NAME"] else "pip3"
PIP_EXECUTABLE = "pip" if "osx" in env["OS_NAME"] and "actions" in env["CI_SYSTEM"] else PIP_EXECUTABLE
PIP_VERSION = ""

for APP in ["entrando","spritesomething"]:
  print(APP)
  for PYEXE in ["py","python","python3"]:
    args = []
    if PYEXE == "py":
      PYEXE = [ PYEXE, "-" + PYTHON_MINOR_VERSION]
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
            if "already satisfied" in line.strip():
              satisfied = line.strip().split(" in ")
              sver = satisfied[1].split("(").pop().replace(")","")
              print(
                "🟩%s\t%s"
                %
                (
                  satisfied[0],
                  sver
                )
              )
            elif "status 'error'" in line.strip():
              print("🟥" + line.strip())
            else:
              print(line.strip())
          print("")
    except Exception as e:
      print(e)
