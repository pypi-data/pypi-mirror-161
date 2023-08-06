"""
(c) 2022 K. Goger - https://github.com/kr-g/

xvenv automates venv handling, as well as
starting from command line with activating
a venv beforehand

works on linux

a full installation is done by:

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
import glob
from functools import wraps
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


def dprint(*args_, **kwargs_):
    debug and print(*args_, **kwargs_)


def vprint(*args_, **kwargs_):
    (debug or verbose) and print(*args_, **kwargs_)


#
# def trprint():
#     import inspect
#
#     cf = inspect.currentframe()
#     f = cf.f_back
#     fi = inspect.getframeinfo(f)
#     ca = inspect.getargvalues(f)
#     dprint("*TRACE*", fi.function, ca.locals)
#


def trprint(func):
    def _w():
        @wraps(func)
        def __w(*a, **kw):
            try:
                dprint("*TRACE*", "enter", func.__name__, a, kw)
                return func(*a, *kw)
            finally:
                dprint("*TRACE*", "leave", func.__name__, a, kw)

        return __w

    return _w()


@trprint
def proc(args_):
    proc = subprocess.Popen(args_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dprint("proc.returncode", proc.returncode)
    if proc:
        while True:
            outs = proc.stdout.readline().decode()
            if len(outs) == 0:
                break
            vprint(outs, end="")

    dprint("done proc.returncode", proc.returncode)

    if proc.returncode == 0:
        return

    return proc.returncode


@trprint
def bashwrap(cmd):
    wrap = "#!/bin/bash -l \n"
    wrap += f'cd "{cwd}" \n'
    wrap += f'. "{VENV}/bin/activate" \n'
    wrap += f"{cmd} \n"
    return wrap


@trprint
def extrun(cmd):
    # fnam = os.path.join(tempfile.gettempdir(), TEMPRUN)
    fd, fnam = tempfile.mkstemp(prefix="xvenv-", suffix=".sh")
    os.close(fd)

    dprint("tempfile", fnam)

    with open(fnam, "w") as f:
        f.write(cmd)

    rc = proc(
        [
            "/bin/bash",
            "-l",
            fnam,
        ]
    )

    if not keep_temp:
        os.remove(fnam)
    else:
        print("keep_temp", fnam)

    return rc


@trprint
def no_rest_or_die(args_):
    if len(args_.rest) > 0:
        print("unknown opts", *args_.rest)
        sys.exit(1)


@trprint
def setup(args_):
    no_rest_or_die(args_)

    clear = "--clear" if args_.clear else ""
    copy = "--copies" if args_.copy else "--symlink"
    os.chdir(cwd)
    cmd = f"{args_.python} -m venv {VENV} {clear} {copy}".split()
    rc = proc(cmd)
    return rc


@trprint
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


@trprint
def clean(args_):
    no_rest_or_die(args_)

    for fld in ["build", "dist", "*.egg-info"]:
        vprint("clean", fld)
        for fnam in glob.iglob(fld):
            dprint("clean", fnam)
            shutil.rmtree(fnam, ignore_errors=False, onerror=report)


class VerboseOn(object):
    def __enter__(self):
        global verbose
        self.bak = verbose
        verbose = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        global verbose
        verbose = self.bak


@trprint
def build(args_):
    no_rest_or_die(args_)

    with VerboseOn():
        print("building...")
        if args_.build_clean:
            or_die_with_mesg(clean(args_), "build clean failed")

        cmd = bashwrap(f"{args_.python} -m setup sdist build bdist_wheel")
        rc = extrun(cmd)
        return rc


@trprint
def install(args_):
    no_rest_or_die(args_)

    with VerboseOn():
        print("installing...")
        cmd = bashwrap(f"{args_.python} -m pip install -e .")
        rc = extrun(cmd)
        return rc


@trprint
def binst(args_):
    or_die_with_mesg(build(args_), "build failed")
    or_die_with_mesg(install(args_), "install failed")


@trprint
def or_die_with_mesg(rc, text=None):
    if rc:
        print(text if text else "ERROR", file=sys.stderr)
        debug and print(rc, file=sys.stderr)
        sys.exit(1)


@trprint
def make(args_):
    no_rest_or_die(args_)

    print("making...")

    or_die_with_mesg(setup(args_), "setup failed")
    or_die_with_mesg(pip(args_), "pip failed")
    or_die_with_mesg(tools(args_), "tools failed")

    if args.quick:
        return

    or_die_with_mesg(test(args_), "test failed")
    or_die_with_mesg(build(args_), "build failed")
    or_die_with_mesg(install(args_), "install failed")


@trprint
def run(args_):
    rest = shlex.join(args_.rest)
    cmd = bashwrap(f"{rest}")
    rc = extrun(cmd)
    return rc


@trprint
def test(args_):
    no_rest_or_die(args_)

    # switch verbose on for qtest
    global verbose
    verbose = True

    cmd = bashwrap(
        f"{args_.python} -c 'import os; import pip; print(pip.__file__);[ print(k,chr(61),v) for k,v in os.environ.items() ]'"
    )
    rc = extrun(cmd)
    return rc


@trprint
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


def report(*args):
    print("ERROR", args, file=sys.stderr)


@trprint
def drop(args_):
    no_rest_or_die(args_)

    cwd = os.getcwd()
    fnam = os.path.abspath(os.path.join(cwd, VENV))
    if os.path.exists(fnam):
        if os.path.isdir(fnam):
            rc = input(f"really drop {fnam} ? (y)es/(N)o : ")
            rc = rc.strip().lower()
            if rc in ["y", "yes"]:
                print("removing...")
                shutil.rmtree(fnam, ignore_errors=False, onerror=report)
            else:
                print("aborted")
        else:
            print("not an folder", fnam, file=sys.stderr)
            return 1
    else:
        print("not found folder", fnam, file=sys.stderr)
        return 1


def getcfg(fnam):
    if os.path.exists(fnam):
        return f"--config {fnam}"
    return ""


@trprint
def qtest(args_):
    no_rest_or_die(args_)

    verbose_ = "-v" if debug else ""
    exclude_ = "--exclude " + args.exclude if args.exclude else ""

    with VerboseOn():

        if args_.format:
            vprint("formating...")
            BLACK_CFG = "black.cfg"
            cfg = getcfg(BLACK_CFG)
            dprint("black cfg", cfg)
            rc = extrun(f"black {cfg} {verbose_} {exclude_} .")
            or_die_with_mesg(rc, "black failed")

        if args_.lint:
            vprint("linting...")
            FLAKE8_CFG = "flake8.cfg"
            cfg = getcfg(FLAKE8_CFG)
            dprint("lint cfg", cfg)
            exclude_ = "--exclude '.venv'" if exclude_ == "" else exclude_
            dprint("exclude", exclude_)
            rc = extrun(f"flake8 {cfg} {verbose_} {exclude_}")

        if args_.unit_test:
            vprint("testing...")
            rc = extrun(f"{python_} -m unittest {verbose_}")

    if not any([args_.format, args_.lint, args_.unit_test]):
        print("what? use --help")


def main_func():

    global args, debug, verbose, python_, tools_, keep_temp, cwd

    parser = argparse.ArgumentParser(
        prog="xvenv",
        usage=f"{python_} -m %(prog)s [options]",
        description="venv mangement and builder tool",
        epilog="for more information refer to https://github.com/kr-g/%(prog)s",
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
        help="clear before setup (default: %(default)s)",
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
        "-tool",
        nargs="*",
        action="store",
        default=tools_,
        help="tool to install (default: %(default)s)",
    )

    clean_parser = subparsers.add_parser(
        "clean",
        help="clean all build folders",
    )
    clean_parser.set_defaults(func=clean)

    build_parser = subparsers.add_parser(
        "build",
        help="build with setuptools. like calling setup sdist build bdist_wheel",
    )
    build_parser.set_defaults(func=build)
    build_parser.add_argument(
        "--build-clean",
        "-bclr",
        action="store_true",
        default=False,
        help="clean all build related folders (default: %(default)s)",
    )

    install_parser = subparsers.add_parser(
        "install", help="pip install editabe in venv"
    )
    install_parser.set_defaults(func=install)

    binst_parser = subparsers.add_parser("binst", help="build and install")
    binst_parser.set_defaults(func=binst)
    binst_parser.add_argument(
        "--build-clean",
        "-bclr",
        action="store_true",
        default=False,
        help="clean all build related folders (default: %(default)s)",
    )

    make_parser = subparsers.add_parser(
        "make", help="sets up a venv and installs everything"
    )
    make_parser.set_defaults(func=make)

    make_parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        default=False,
        help="quick install without build and install steps (default: %(default)s)",
    )
    make_parser.add_argument(
        "--clear",
        "-c",
        action="store_true",
        default=False,
        help="clear before setup (default: %(default)s)",
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
        "-tool",
        nargs="*",
        action="store",
        default=tools_,
        help="tool to install (default: %(default)s)",
    )
    make_parser.add_argument(
        "--build-clean",
        "-bclr",
        action="store_true",
        default=False,
        help="clean all build related folders (default: %(default)s)",
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

    drop_parser = subparsers.add_parser(
        "drop", help="removes the '.venv' folder, and all contents"
    )
    drop_parser.set_defaults(func=drop)

    qtest_parser = subparsers.add_parser("qtest", help="run quality helpers")
    qtest_parser.set_defaults(func=qtest)

    qtest_parser.add_argument(
        "--exclude",
        "-ex",
        type=str,
        default=None,
        help="rexclude folder. (default: %(default)s)",
    )

    qtest_parser.add_argument(
        "--format",
        "--pep8",
        "-f",
        action="store_true",
        default=False,
        help="run black, use black.cfg file for configuration",
    )
    qtest_parser.add_argument(
        "--lint",
        "-l",
        action="store_true",
        default=False,
        help="run flake8, use flake.cfg file for configuration",
    )
    qtest_parser.add_argument(
        "--unit-test",
        "--test",
        "-t",
        action="store_true",
        default=False,
        help="run unittest",
    )

    #

    args, rest = parser.parse_known_args()
    args.rest = rest

    debug = args.debug
    debug and print("arguments", args)

    keep_temp = args.keep_temp
    cwd = args.cwd

    verbose = args.verbose

    if "func" in args:
        rc = args.func(args)
        debug and print("result:", rc)
        return rc
    else:
        print("what? use --help")


if __name__ == "__main__":
    main_func()
