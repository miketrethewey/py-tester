import common                     # app common functions

import json                       # json manipulation
import os                         # for os data, filesystem manipulation
import platform                   # for python data
import subprocess                 # for running shell commands
import sys                        # for system commands
import traceback                  # for errors
from my_path import get_py_path   # pathing help

env = common.prepare_env()  # get environment variables

WIDTH = 70  # width for labels

PYTHON_EXECUTABLE = os.path.splitext(sys.executable.split(os.path.sep).pop())[
    0]  # get command to run python
# get python version
PYTHON_VERSION = sys.version.split(" ")[0]
# get python major.minor version
PYTHON_MINOR_VERSION = '.'.join(PYTHON_VERSION.split(".")[:2])
PIP_VERSION = ""
PIP_FLOAT_VERSION = 0
VERSIONS = {}


def get_module_version(module):
    # pip index versions [module]                             // >= 21.2
    # pip install [module]==                                  // >= 21.1
    # pip install --use-deprecated=legacy-resolver [module]== // >= 20.3
    # pip install [module]==                                  // >=  9.0
    # pip install [module]==blork                             // <   9.0
    global PIP_FLOAT_VERSION
    ret = ""
    ver = ""

    if float(PIP_FLOAT_VERSION) >= 21.2:
        ret = subprocess.run([*args, "-m", PIPEXE, "index",
                             "versions", module], capture_output=True, text=True)
        lines = ret.stdout.strip().split("\n")
        lines = lines[2::]
        vers = (list(map(lambda x: x.split(' ')[-1], lines)))
        if len(vers) > 1:
            ver = vers[1]
    elif float(PIP_FLOAT_VERSION) >= 21.1:
        ret = subprocess.run(
            [*args, "-m", PIPEXE, "install", f"{module}=="], capture_output=True, text=True)
    elif float(PIP_FLOAT_VERSION) >= 20.3:
        ret = subprocess.run([*args, "-m", PIPEXE, "install", "--use-deprecated=legacy-resolver",
                             f"{module}=="], capture_output=True, text=True)
    elif float(PIP_FLOAT_VERSION) >= 9.0:
        ret = subprocess.run(
            [*args, "-m", PIPEXE, "install", f"{module}=="], capture_output=True, text=True)
    elif float(PIP_FLOAT_VERSION) < 9.0:
        ret = subprocess.run([*args, "-m", PIPEXE, "install",
                             f"{module}==blork"], capture_output=True, text=True)

    # if ver == "" and ret.stderr.strip():
    #     ver = (ret.stderr.strip().split("\n")[0].split(",")[-1].replace(')', '')).strip()

    return ver


def do_python(args):
    # get python debug info
    ret = subprocess.run([*args, "--version"], capture_output=True, text=True)
    if ret.stdout.strip():
        PYTHON_VERSION = ret.stdout.strip().split(" ")[1]
        PY_STRING = (
            "%s\t%s\t%s"
            %
            (
                ((isinstance(args[0], list) and " ".join(
                  args[0])) or args[0]).strip(),
                PYTHON_VERSION,
                sys.platform
            )
        )
        print(PY_STRING)
        print('.' * WIDTH)


def do_pip(args, PIPEXE):
    global VERSIONS
    # get pip debug info
    ret = subprocess.run([*args, "-m", PIPEXE, "--version"],
                         capture_output=True, text=True)
    if ret.stdout.strip():
        if " from " in ret.stdout.strip():
            PIP_VERSION = ret.stdout.strip().split(" from ")[
                0].split(" ")[1]
            if PIP_VERSION:
                b, f, a = PIP_VERSION.partition('.')
                global PIP_FLOAT_VERSION
                PIP_FLOAT_VERSION = b+f+a.replace('.', '')
                PIP_LATEST = get_module_version("pip")

                VERSIONS["py"] = {"version": PYTHON_VERSION,
                                  "platform": sys.platform}
                VERSIONS["pip"] = {
                    "version": [
                        PIP_VERSION,
                        PIP_FLOAT_VERSION
                    ],
                    "latest": PIP_LATEST
                }

                PIP_STRING = (
                    "%s\t%s\t%s\t%s\t%s\t%s"
                    %
                    (
                        ((isinstance(args[0], list) and " ".join(
                            args[0])) or args[0]).strip(),
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

PIP_VERSION = ""  # holder for pip's version

# process entrando & spritesomething, or arg from commandline
APPS = ["entrando", "spritesomething"]
if len(sys.argv) > 1:
    APPS = [sys.argv[1]]

# foreach app
for APP in APPS:
    # print app name
    print(APP)
    print('-' * WIDTH)
    VERSIONS[APP] = {}
    success = False
    # foreach py executable
    for PYEXE in ["py", "python3", "python"]:
        if success:
            continue

        args = []
        # if it's the py launcher, specify the version
        if PYEXE == "py":
            PYEXE = [PYEXE, "-" + PYTHON_MINOR_VERSION]
            # if it ain't windows, skip it
            if "windows" not in env["OS_NAME"]:
                continue

        # build executable command
        if isinstance(PYEXE, list):
            args = [*PYEXE]
        else:
            args = [PYEXE]

        try:
            do_python(args)  # print python debug data

            # foreach py executable
            for PIPEXE in ["pip3", "pip"]:
                do_pip(args, PIPEXE)        # print pip debug data
                # upgrade pip
                ret = subprocess.run(
                    [*args, "-m", PIPEXE, "install", "--upgrade", "pip"], capture_output=True, text=True)
                # get output
                if ret.stdout.strip():
                    # if it's not already satisfied, update it
                    if "already satisfied" not in ret.stdout.strip():
                        print(ret.stdout.strip())
                        do_pip(args, PIPEXE)

                # install modules from list
                ret = subprocess.run([*args, "-m", PIPEXE, "install", "-r", os.path.join(
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
                        elif "already satisfied" in line or \
                            "Building wheel" in line or \
                                "Created wheel" in line:
                            satisfied = line.strip().split(" in ")
                            sver = ((len(satisfied) > 1) and satisfied[1].split(
                                "(").pop().replace(")", "")) or ""

                            if "Created wheel" in line:
                                line = line.strip().split(':')
                                satisfied = [line[0]]
                                sver = line[1].split('-')[1]

                            modulename = satisfied[0].replace(
                                "Requirement already satisfied: ", "")
                            VERSIONS[APP][modulename] = {"installed": sver, "latest": (sver and get_module_version(
                                satisfied[0].split(" ")[-1])).strip() or ""}

                            print(
                                (
                                    "[%s] %s\t%s\t%s"
                                    %
                                    (
                                        "Building wheel" in line and '.' or "X",
                                        satisfied[0].ljust(
                                            len("Requirement already satisfied: ") + len("python-bps-continued")),
                                        VERSIONS[APP][modulename
                                                      ]["installed"],
                                        VERSIONS[APP][modulename]["latest"]
                                    )
                                )
                            )
                        # ignore lines about certain things
                        elif "Collecting" in line or \
                            "Downloading" in line or \
                            "eta 0:00:00" in line or \
                            "Preparing metadata" in line or \
                            "Successfully built" in line or \
                                "Stored in" in line:
                            pass
                        # else, I don't know what it is, print it
                        else:
                            print(line.strip())
                    print("")
                    with open(os.path.join(".", "resources", "user", "manifests", "settings.json"), "w") as settings:
                        settings.write(json.dumps(
                            {"py": args, "pip": PIPEXE, "pipline": " ".join(args) + " -m " + PIPEXE, "versions": VERSIONS}, indent=2))
                    with open(os.path.join(".", "resources", "user", "manifests", "pipline.txt"), "w") as settings:
                        settings.write(" ".join(args) + " -m " + PIPEXE)
                    success = True
        # if something else went fucky, print it
        except Exception as e:
            traceback.print_exc()
