# coding: utf-8

import click
import logging
from os import environ, path, walk, rename
import paramiko
from sys import exit


_logger = logging.getLogger('deployv.' + __name__)


def check_vars():
    return environ.get('COVERAGE_PASS', False)


def get_values():
    res = {
        'username': 'coverage',
        'password': environ.get('COVERAGE_PASS'),
        'commit_slug': environ.get('CI_COMMIT_REF_SLUG'),
        'project_name': environ.get('CI_PROJECT_NAME')
    }
    return res


def get_sftp_client(username, password):
    _logger.info('Connecting to the remote host')
    transport = paramiko.Transport(('coverage.vauxoo.com', 8451))
    transport.connect(username=username,
                      password=password)
    return paramiko.SFTPClient.from_transport(transport)


def push_files():
    values = get_values()
    local_path = path.join('.', '{}-{}'.format(
        values.get('commit_slug'),
        values.get('project_name')
    ))
    remote_path = '.'
    _logger.info('Pushing files from: %s', local_path)
    sftp = get_sftp_client(values.get('username'), values.get('password'))
    try:
        rename(values.get('commit_slug'), local_path)
    except OSError:
        _logger.warn('Nothing to report from %s', values.get('commit_slug'))
        _logger.warn('\nThis job is failing because the coverage report folder is empty this is due to:' +
                     '\n  - No tests were executed' +
                     '\n  - The test job is not properly configured' +
                     '\n  - The results from the tests are stored in a different folder that the expected' +
                     '\nPlease note that this job should be allowed to fail (allow_failure: true) and the pipeline'
                     '\n will be yellow until this is fixed, but this shouldn\'t avoid the merge unless is unexpected.' +
                     '\nFor more information check the project template: ' +
                     '\n https://git.vauxoo.com/vauxoo/project-template/blob/master/%7B%7Bcookiecutter.project_name%7D%7D/.gitlab-ci.yml')
        exit(1)

    for root, dirs, files in walk(local_path):
        _logger.debug('Root: %s .. Dirs: %s .. Files: %s', root, dirs, files)
        remote = path.join(remote_path, root)
        _logger.debug('Creating remote folder: %s', remote)
        try:
            sftp.mkdir(remote)
        except Exception as error:
            _logger.warning(str(error))
            pass

        for f in files:
            _logger.debug('Uploading file: %s', f)
            if f not in ['odoo.log', '.coveragerc']:
                sftp.put(path.join(root, f), path.join(remote_path, root, f))

    _logger.info('Pushed files')


def show_url():
    values = get_values()
    print("Coverage report can be found in:")
    print("https://coverage.vauxoo.com/{}-{}".format(values.get('commit_slug'), values.get('project_name')))


def push_coverage_result():
    if not check_vars():
        _logger.error('Variable COVERAGE_PASS is not defined, required to push the files')
        exit(1)
    push_files()
    show_url()
    exit(0)


@click.command()
def push_coverage():
    push_coverage_result()
