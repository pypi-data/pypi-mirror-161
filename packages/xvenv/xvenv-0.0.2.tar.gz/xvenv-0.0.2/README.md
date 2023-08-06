# xvenv

`xvenv.py` helps to setup and maintain a venv quickly

`xvenv.py` can be installed with pip, or it runs as single stand-alone script.

when installed via pip the command execution `python3 xvenv.py` 
can be replaced just by `xvenv`.


# use-case: try an new application from pypi

run 

    xvenv setup
    xvenv pip
    xvenv tools -tool *the-package*
    
or just as single command

    xvenv make --quick -tool *the-package*



so `xvenv` will create a folder `.venv`, and will do there all required steps.

then its possible to start either with normal venv

    source ./bin/activate
    # end start manually
    *the-package-commandline*
    
or 

    xvenv run *the-package-commandline*
    

## desktop starter

when done the steps above and the package starts, 
create a desktop starter with

    /usr/bin/python3 xvenv.py -cwd /your-path run *the-package-commandline*
    
    
# installation

## pip

it's **recommended** to install from pip with

    pip install xvenv


## stand-alone or clone

put this in your `~/.bashrc`, or `~/.bash_aliases`

    alias xvenv="python3 ~/repo/xvenv/xvenv/xvenv.py"

    # or ... any path where it resides in

to use it from cmd-line

    
# use case: build a whole source package 

e.g. when testing the build and installation
when all sources are inside a single folder 
on the harddrive already, `cd` into it and

run 

    xvenv setup
    xvenv pip
    xvenv tools 
    xvenv build  
    xvenv setup
   
or just as single command

    xvenv make 
    xvenv make -u 
        -> to update the tools packages
    
what will install the sources as `editable` inside the venv.

then activate venv manually, or start the tool as described above.

    
# use-case: new development

think about you have started a new development, and now you want its required
to have a venv in addition to encapsulate the dependencies.

run 

    xvenv setup
    xvenv pip
    xvenv tools   
    
or
    xvenv tools -u
        -> to update the tools packages

what will create the venv, and install pip, setuptools, twine, black, and flake8 inside
    
as soon the build is ready, test it with

    xvenv build
    xvenv install
    
what will call `setup sdist build bdist_wheel` internally,
followed by pip install -e .


# more packages ?

run 

    xvenv tools -tool *pack1* *pack2* ...

or

    xvenv tools -tool *pack1* *pack2* ... -u
        -> to update the tools packages
  
to install more packages into the venv


# removing a venv

just delete the `.venv` folder manuall if the venv is nor required any more,
there are no further dependencies.

     xvenv drop
     

# another use case: install thonny and thonny-gitonic

just open a new bash and run

    mkdir thonnygitonic
    cd $_
    xvenv -V make -q -tool thonny thonny-gitonic
    
what will do a quick installation and print verbose output

then run with 

    xvenv run thonny


# all cmd-line opts

all cmd-line opts described here [`README_CMDLINE`](./README_CMDLINE.md)


# what's new ?

check
[`CHANGELOG`](./CHANGELOG.md)
for latest ongoing, or upcoming news.


# limitations

check 
[`BACKLOG`](./BACKLOG.md)
for open development tasks and limitations.


# platform

as of now just linux

Contributions are Welcome to helping with Windows and Mac !!!


# development status

alpha, the interface/ workflow might change without prior notice

    
# license

[`LICENSE`](./LICENSE.md)

