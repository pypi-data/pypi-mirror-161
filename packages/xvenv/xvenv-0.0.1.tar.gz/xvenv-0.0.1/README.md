# xvenv

`xvenv.py` helps to setup and maintain a venv quickly

`xvenv.py` can be installed with pip, or it runs as single stand-alone script.


# use-case: try an new application from pypi

run 

    python3 xvenv.py setup
    python3 xvenv.py pip
    python3 xvenv.py tools *the-package*
    
or just as single command

    python3 xvenv.py make --quick -tool *the-package*

so `xvenv.py` will create a folder `.venv`, and will do there all required steps.

then its possible to start either with normal venv

    source ./bin/activate
    # end start manually
    *the-package-commandline*
    
or 

    python3 xvenv.py run *the-package-commandline*
    

## desktop starter

when done the steps above and the package starts, 
create a desktop starter with

    /usr/bin/python3 xvenv.py -cwd /your-path run *the-package-commandline*
    
    
# use case: build a whole source package 

e.g. when testing the build and installation
when all sources are inside a single folder 
on the harddrive already, `cd` into it and

run 

    python3 xvenv.py setup
    python3 xvenv.py pip
    python3 xvenv.py tools 
    python3 xvenv.py build  
    python3 xvenv.py setup
   
or just as single command

    python3 xvenv.py make 
    
what will install the sources as `editable` inside the venv.

then activate venv manually, or start the tool as described above.

    
# use-case: new development

think about you have started a new development, and now you want its required
to have a venv in addition to encapsulate the dependencies.

run 

    python3 xvenv.py setup
    python3 xvenv.py pip
    python3 xvenv.py tools     

what will create the venv, and install pip, setuptools, twine, black, and flake8 inside
    
as soon the build is ready, test it with

    python3 xvenv.py build
    python3 xvenv.py install
    
what will call `setup sdist build bdist_wheel` internally,
followed by pip install -e .


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


# development status

alpha, the interface/ workflow might change without prior notice

    
# license

[`LICENSE`](./LICENSE.md)

