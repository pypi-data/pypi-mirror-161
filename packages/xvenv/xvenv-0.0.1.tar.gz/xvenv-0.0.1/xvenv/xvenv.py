"""
(c) 2022 K. Goger 

xvenv automates venv handling, as well as
starting from command line with activating
a venv beforehand

works on linux

all full installation is done by:

    python3 xvenv.py setup ** --clear --copy
    python3 xvenv.py pip
    python3 xvenv.py tools
    python3 xvenv.py test
    python3 xvenv.py build
    python3 xvenv.py install

or call make for all steps above:

    python3 xvenv.py make

or

    python3 xvenv.py make --quick
        -> only steps setup, pip 


call a program within the venv

    python3 xvenv.py run *your-cmd-line*


hint:
with 'run' all rest opts are passed to the next tool

e.g.
python3 xvenv.py run python3 -c "import os; print('hello')"


important:

this is different!

    python3 xvenv.py pip list
        -> will fail since this will install pip in venv

    python3 xvenv.py run pip list
        -> will work as expected


a desktop starter can be created with e.g.
python3 /somefolder/xvenv.py -cwd /otherfolder/repo/pymodule run pymodule-cmdline

"""


import sys
import os
import argparse
import subprocess
import tempfile
import shutil
import shlex

VERSION = "v0.0.0"

try:
    from const import VERSION
except:
    pass
try:
    from .const import VERSION
except:
    pass


VENV = ".venv"
PYTHON = "python3"
PIP = "pip"
TEMPRUN = "e_n_v_i.sh"

args = None
debug = False
verbose = False
python_ = PYTHON
tools_ = ["setuptools", "twine", "wheel", "black", "flake8"]
keep_temp = False
cwd = "."


def proc(args_):
    rc = subprocess.run(args_, capture_output=True)
    if rc:
        if rc.returncode == 0:
            rc.returncode = None
    return rc


def bashwrap(cmd):
    wrap = "#!/bin/bash -il \n"
    wrap += f"cd {cwd}\n"
    wrap += f". {VENV}/bin/activate \n"
    wrap += f"{cmd} \n"
    return wrap


def extrun(cmd):

    # fnam = os.path.join(tempfile.gettempdir(), TEMPRUN)
    fd, fnam = tempfile.mkstemp(prefix="xvenv-", suffix=".sh")
    os.close(fd)

    with open(fnam, "w") as f:
        f.write(cmd)
    rc = proc(
        [
            "bash",
            fnam,
        ]
    )

    if not keep_temp:
        os.remove(fnam)
    else:
        print("keep_temp", fnam)

    return rc


def no_rest_or_die(args_):
    if len(args_.rest) > 0:
        print("unknown opts", *args_.rest)
        sys.exit(1)


def setup(args_):
    no_rest_or_die(args_)
    clear = "--clear" if args_.clear else ""
    copy = "--copies" if args_.copy else "--symlink"
    os.chdir(cwd)
    cmd = f"{args_.python} -m venv {VENV} {clear} {copy}".split()
    rc = proc(cmd)
    return rc


def pip(args_):
    no_rest_or_die(args_)
    cmd = bashwrap(f"{args_.python} -m ensurepip -U")
    rc = extrun(cmd)
    return rc


def tools(args_):
    no_rest_or_die(args_)
    tools = " ".join(args_.tool)
    update = "-U" if args.update_deps else ""
    cmd = bashwrap(f"{args_.python} -m pip install {tools} {update}")
    rc = extrun(cmd)
    return rc


def build(args_):
    no_rest_or_die(args_)
    cmd = bashwrap(f"{args_.python} -m setup sdist build bdist_wheel")
    rc = extrun(cmd)
    return rc


def install(args_):
    no_rest_or_die(args_)
    cmd = bashwrap(f"{args_.python} -m pip install -e .")
    rc = extrun(cmd)
    return rc


def or_die_with_mesg(rc, text=None):
    if rc.returncode:
        print(text if text else "ERROR", file=sys.stderr)
        debug and print(rc, file=sys.stderr)
        sys.exit(1)


def make(args_):
    no_rest_or_die(args_)
    or_die_with_mesg(setup(args_), "setup failed")
    or_die_with_mesg(pip(args_), "pip failed")
    or_die_with_mesg(tools(args_), "tools failed")
    if args.quick:
        return
    or_die_with_mesg(test(args_), "test failed")
    or_die_with_mesg(build(args_), "build failed")
    or_die_with_mesg(install(args_), "install failed")


def run(args_):
    rest = shlex.join(args_.rest)
    cmd = bashwrap(f"{rest}")
    rc = extrun(cmd)
    print(rc.stdout.decode())
    print(rc.stderr.decode(), file=sys.stderr)
    return rc


def test(args_):
    no_rest_or_die(args_)
    cmd = bashwrap(
        f"{args_.python} -c 'import os; import pip; print(pip.__file__);[ print(k,chr(61),v) for k,v in os.environ.items() ]'"
    )
    rc = extrun(cmd)
    for line in rc.stdout.decode().splitlines():
        print(line)
    return rc


def clone(args_):
    no_rest_or_die(args_)
    src = os.path.abspath(__file__)
    fnam = os.path.basename(__file__)
    dest = os.path.join(os.getcwd(), fnam)
    if dest == src:
        print("same base folder", file=sys.stderr)
        return 1
    rc = shutil.copy2(src, dest)
    return rc


def main_func(mkcopy=True):

    global args, debug, verbose, python_, tools_, keep_temp, cwd

    parser = argparse.ArgumentParser(
        prog="xvenv",
        usage=f"{python_} -m %(prog)s [options]",
        description="venv tool",
        epilog="for more information refer to https://github.com/kr-g/xvenv",
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s {VERSION}"
    )
    parser.add_argument(
        "--verbose",
        "-V",
        dest="verbose",
        action="store_true",
        help="show more info (default: %(default)s)",
        default=verbose,
    )
    parser.add_argument(
        "-debug",
        "-d",
        dest="debug",
        action="store_true",
        help="display debug info (default: %(default)s)",
        default=debug,
    )

    parser.add_argument(
        "-python",
        "-p",
        help="display debug info (default: %(default)s)",
        default=python_,
    )
    parser.add_argument(
        "-cwd",
        help="venv working folder (default: %(default)s)",
        default=cwd,
    )
    parser.add_argument(
        "--keep-temp",
        "-kt",
        action="store_true",
        help="keep temporay file (default: %(default)s)",
        default=keep_temp,
    )

    subparsers = parser.add_subparsers(help="sub-command --help")

    setup_parser = subparsers.add_parser("setup", help="setup a venv")
    setup_parser.set_defaults(func=setup)

    setup_parser.add_argument(
        "--clear",
        "-c",
        action="store_true",
        default=False,
        help="clear before install (default: %(default)s)",
    )
    setup_parser.add_argument(
        "--copy",
        "-cp",
        action="store_true",
        default=False,
        help="use copy instead of symlink (default: %(default)s)",
    )

    pip_parser = subparsers.add_parser("pip", help="pip installation")
    pip_parser.set_defaults(func=pip)

    tools_parser = subparsers.add_parser("tools", help="tools installation")
    tools_parser.set_defaults(func=tools)
    tools_parser.add_argument(
        "--update-deps",
        "-u",
        action="store_true",
        default=False,
        help="update deps (default: %(default)s)",
    )
    tools_parser.add_argument(
        "tool",
        nargs="*",
        action="store",
        default=tools_,
        help="tools to install (default: %(default)s)",
    )

    build_parser = subparsers.add_parser(
        "build",
        help="build with setuptools. like calling setup sdist build bdist_wheel",
    )
    build_parser.set_defaults(func=build)

    install_parser = subparsers.add_parser("install", help="pip -e . in venv")
    install_parser.set_defaults(func=install)

    make_parser = subparsers.add_parser(
        "make", help="sets up a venv and installs everything"
    )
    make_parser.set_defaults(func=make)

    make_parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        default=False,
        help="quick install without build and install stel (default: %(default)s)",
    )
    make_parser.add_argument(
        "--clear",
        "-c",
        action="store_true",
        default=False,
        help="clear before install (default: %(default)s)",
    )
    make_parser.add_argument(
        "--copy",
        "-cp",
        action="store_true",
        default=False,
        help="use copy instead of symlink (default: %(default)s)",
    )
    make_parser.add_argument(
        "--update-deps",
        "-u",
        action="store_true",
        default=False,
        help="update deps (default: %(default)s)",
    )
    make_parser.add_argument(
        "tool",
        nargs="*",
        action="store",
        default=tools_,
        help="tools to install (default: %(default)s)",
    )

    run_parser = subparsers.add_parser("run", help="run a command")
    run_parser.set_defaults(func=run)
    # run_parser.add_argument("files", nargs="+", action="store", type=str)

    test_parser = subparsers.add_parser(
        "test", help="test venv environment. outputs pip path and os.environ"
    )
    test_parser.set_defaults(func=test)

    clone_parser = subparsers.add_parser("clone", help="clone xvenv.py to cwd folder")
    clone_parser.set_defaults(func=clone)

    args, rest = parser.parse_known_args()
    args.rest = rest

    debug = args.debug
    debug and print("arguments", args)

    keep_temp = args.keep_temp
    cwd = args.cwd

    verbose = args.verbose

    if "func" in args:
        rc = args.func(args)
        debug and print(rc)
        return rc
    else:
        print("what? use --help")


if __name__ == "__main__":
    main_func()
