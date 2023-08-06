<!-- README.md -->

# Aliased Shell runner for python projects

This runs your python projects/packages from anywhere inside your shell, without the need to install the package or change directory. 
NOTE: Currently only pipenvs are implemented. Only tested on Windows 10. 
Feel free to clone and extend.

NOTE: a sample runAlias.yml file can be found here: https://gitlab.com/larsmielke2/boakboak/-/tree/main/boakboak/apps


# Install
- pipenv install boakboak

# Create app directory and file
- UserDir/boaks/archive.yml (for different app location change settings.py)

# run like
- boak archive -m "mycomment"




### dependencies
- python 3.9 - 3.10
- pyyaml



# Problem boakboak tries to solve?
I have some python based services, which I want to run occasionally from anywhere inside the
shell using an aliased shell call.

Most importantly: I dont want to install all these services into my main environment.

For example:
- I want to save my files to a archive directory, for which I have a archive.py module.
- I want to convert a table to a json or yaml file for which I use a convert.py package.

I want to be able to flexibly add/remove these services from the aliased shell call.




# Usage
Create and runAlias.yml file and name with a memorable alias.

Sample names: archive.yml, cad.yml, unittest.yml, git_sy.yml

Example file:
- name like: /boaks/runAlias.yml (see example in directory below)
- save to: ... \Lib\site-packages\boakboak\apps\runAlias.yml
- or save as boak_packageAlias.yml to the directory of the callable app (same directory as setup.py)
- NOTE: prefix boak can be changed in settings.py

## Run like
boak runAlias -my parameters




## Steps

#### Example: Imaginary project which uses a archive.py module to archive files and folders.
- I will run my module from the shell, using "python -m archive -c 'my_archive_comment'" as I always do.
- From the sucessfully executed shell command, I copy the path, cmds and optional args to archive.yml
- I save the created .yml file in: ~/boaks/archive.yml
- The resulting .yml file has to look like this example: https://gitlab.com/larsmielke2/boakboak/-/tree/main/boakboak/apps

From the shell, I now call:
- boak archive -c 'my_archive_comment'


## How it works

boakboak will use the parameters from apps/runAlias.yml, to run your project/package
- It takes appPath and finds your project/package (returns the first dir with .venv in it)
- It uses .venv file/folder or project name (if Pipfile is found), to identify the executable
- It uses a subprocess call, to run your cmds using identified python.exe

## Logging
- boakboak can log the runtime results in a logfile
    - add a 'logDir' and name to your .yml file like: logDir: path/to/logs
    - log fileName will start with the name follwoed by a timestamp.log

Example:

logDir:  ~/python_venvs\libraries\boakboak\boakboak\test\logs

name: boakboak

this will result in ...\logs\boakboak_2022-05-29-15-38-31-405411.log

## External cmds
- boakboak can take cmds from another file i.e. .gitlab-ci.yml
    - in runAlias.yml file specify cmds like cmds: .gitlab-ci, path, to, cmdstring
    - cmdsstring has to be a comma seperated string representing the path to the script

Example:
runAlias.yml file:
cmds: .gitlab-ci, precommittest, script

.gitlab-ci.yml file:
precommittest:
  stage: test
  when: manual
  allow_failure: true
  tags:
        - test
  script:
    - python -m unittest

resulting cmds now come from script key in .gitlab-ci.yml:
cmds: ['python', '-m', 'unittest']

# License
