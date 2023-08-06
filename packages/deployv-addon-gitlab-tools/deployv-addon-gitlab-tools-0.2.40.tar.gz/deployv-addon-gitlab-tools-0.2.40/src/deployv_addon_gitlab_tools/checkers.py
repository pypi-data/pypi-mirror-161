import future
from os import environ
from os.path import isfile, isdir
import re
from sys import exit


CHECK = u'\033[92mV\033[0m '
CROSS = u'\033[91mX\033[0m '
CIRCLE = u'\033[1;33;40mO\033[0m '


def read_varsfile():
    res = []
    with open('variables.sh', 'r') as varsfile:
        lines = varsfile.readlines()
    for line in lines:
        cLine = line.strip()
        if cLine:
            res.append(cLine)
    return res


def get_file_values():
    rx = re.compile(r'^export\s(?P<key>\w.+?)(\s?)=(\s?)\"?(?P<value>[^\"]*)\"?')
    lines = read_varsfile()
    res = {}
    for line in lines:
        matchs = rx.match(line)
        if matchs:
            res.update({
                matchs.group('key'): matchs.group('value')
            })
    return res


def check_varsfile_syntax():
    nLine = 0
    rx = re.compile(r'^export\s\w*=.*')
    lines = read_varsfile()
    for line in lines:
        nLine += 1
        if not rx.match(line):
            print(CROSS + 'Syntax error in line {} variables file: {}'.format(nLine, line))
            exit(1)
    print(CHECK + 'File syntax OK')


def check_varsfile():
    if isfile('variables.sh'):
        print(CHECK + 'Variables file present')
    else:
        print(CROSS + 'Variables file not present, please create and add it to the repository in order to continue.' +
              ' It should be a list of bash exports like: export VERSION=12.0 or export VERSION="12.0"  (one per line)')
        exit(1)


def check_required_envars():
    required = ['VERSION', 'TRAVIS_PYTHON_VERSION', ]
    fail = False
    for v in required:
        if v in environ.keys():
            print(CHECK + 'Variable {} declared in environment'.format(v))
        else:
            print(CROSS + 'Variable {} not declared in environment,'.format(v) +
                  ' please define it to continue in the variables files.' +
                  '\nRemember to use bash syntax. Example: export VERSION=12.0 or export VERSION="12.0"  (one per line)')
            fail = True
    if fail:
        exit(1)


def check_envars():
    fValues = get_file_values()
    failed = []

    for k in fValues:
        if environ.get(k) != fValues[k]:
            failed.append('Failed check for variable: {}'.format(k))
    if failed:
        for f in failed:
            print(CROSS + f)
        print(CROSS + 'Values in your environment don\'t match the ones for variables.sh:' +
              '\n- did you sourced the variables.sh file? if no add "source variables.sh" to your ci file' +
              ' (should be the first line in the script section)' +
              '\n- do you have a repeated value for a particular variable in variables.sh and' +
              ' in the variables section in your ci file?' +
              ' if so please remove the one from the ci file and use it in variables.sh only')
        exit(1)
    else:
        print(CHECK + 'Env vars match your variables.sh')


def check_mainapp():
    fValues = get_file_values()
    main_app = fValues.get('MAIN_APP', False)
    if not main_app:
        print(CIRCLE + 'No main app defined, all modules will be installed')
        return
    apps = main_app.split(',')
    fail = False
    for app in apps:
        if isdir(app):
            print(CHECK + 'Main app "{}" exists and match the one from your vars'.format(app))
        else:
            print(CROSS + 'Got {} from your env vars, but it doesn\'t match any folder in you repo'.format(app) +
                  ' Remember that the MAIN_APP is the app that will be installed and tested,' +
                  ' this have to match one Odoo module in this repository')
            fail = True
    if fail:
        exit(1)


def check_all():
    check_varsfile()
    check_varsfile_syntax()
    check_envars()
    check_required_envars()
    check_mainapp()
