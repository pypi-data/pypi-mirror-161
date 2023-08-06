# coding: utf-8

from deployv_addon_gitlab_tools.common import check_env_vars, prepare
from deployv.helpers import utils
from docker import APIClient as Client
from os import environ, unsetenv
import subprocess
import shlex
import sys
import click
import logging
import json
import requests


_logger = logging.getLogger('deployv.' + __name__)
_cli = Client(timeout=600)


def build_image():
    format_values = {
        'url': environ['CI_REPOSITORY_URL'],
        'version': environ['CI_COMMIT_REF_NAME'],
        'base': environ['BASE_IMAGE'],
        'odoo_repo': environ['ODOO_REPO'],
        'odoo_branch': environ['ODOO_BRANCH'],
        'name': environ['_IMAGE_NAME'],
    }
    _logger.info('Bulding image %s', environ['_IMAGE_NAME'])
    cmd = (
        'deployvcmd build -u {url} -v {version} -i {base} -O {odoo_repo}#{odoo_branch} -T {name}'
        .format(**format_values)
    )
    subprocess.check_call(shlex.split(cmd))
    image_sha = _cli.images(name=environ['_IMAGE_NAME'], quiet=True)
    res = image_sha and image_sha[0].decode().split(':')[1][:10]
    return res


def push_image(tags):
    if environ.get('https_proxy', False):
        unsetenv('https_proxy')
    for tag in tags:
        _logger.info('Pushing image %s to %s:%s', environ['_IMAGE_NAME'], environ['_IMAGE_REPO'], tag)
        _cli.tag(environ['_IMAGE_NAME'], environ['_IMAGE_REPO'], tag=tag)
        for result in _cli.push(environ['_IMAGE_REPO'], tag=tag, stream=True):
            result = json.loads(utils.decode(result))
            if result.get('error'):
                _logger.error(result.get('error'))
                sys.exit(1)


def notify_orchest(tag, customer, is_latest=False):
    image_name = '{image}:{tag}'.format(image=environ['_IMAGE_REPO'],
                                        tag=tag)
    res = requests.post(
        environ['ORCHEST_REGISTRY'], data=json.dumps({
            'image_name': image_name, 'is_latest': is_latest, 'branch_name': environ['CI_COMMIT_REF_NAME'],
            'job_id': environ['CI_JOB_ID'], 'project_id': environ['CI_PROJECT_ID'],
            'commit': environ['CI_COMMIT_SHA'][:7], 'customer_id': customer}),
        headers={'Content-Type': 'application/json', 'Orchest-Token': environ['ORCHEST_TOKEN']})
    if res.status_code != 200:
        _logger.error('Failed to notify orchest about the new image: %s', res.text)
        sys.exit(1)
    data = res.json()
    if data.get('error'):
        _logger.error('Failed to notify orchest about the new image: %s',
                      data.get('error').get('data', {}).get('name'))
        sys.exit(1)
    _logger.info('Successfully notified orchest about the new image: %s', image_name)


@click.command()
@click.option('--ci_project_name', default=environ.get('CI_PROJECT_NAME'),
              help=("The project name that is currently being built."
                    " Env var: CI_PROJECT_NAME."))
@click.option('--CI_COMMIT_SHA', default=environ.get('CI_COMMIT_SHA'),
              help=("The commit revision for which project is built."
                    " Env var: CI_COMMIT_SHA."))
@click.option('--CI_COMMIT_REF_NAME', default=environ.get('CI_COMMIT_REF_NAME'),
              help=("The branch or tag name for which project is built."
                    " Env var: CI_COMMIT_REF_NAME."))
@click.option('--CI_REPOSITORY_URL', default=environ.get('CI_REPOSITORY_URL'),
              help=("The URL to clone the Git repository."
                    " Env var: CI_REPOSITORY_URL."))
@click.option('--base_image', default=environ.get('BASE_IMAGE'),
              help=("Env var: BASE_IMAGE."))
@click.option('--odoo_repo', default=environ.get('ODOO_REPO'),
              help=("Env var: ODOO_REPO."))
@click.option('--odoo_branch', default=environ.get('ODOO_BRANCH'),
              help=("Env var: ODOO_BRANCH."))
@click.option('--image_repo_url', default=environ.get('IMAGE_REPO_URL', "quay.io/vauxoo"),
              help=("The URL where the image repository is located."
                    " Env var: IMAGE_REPO_URL."))
@click.option('--orchest_registry', default=environ.get('ORCHEST_REGISTRY'),
              help=("Env var: ORCHEST_REGISTRY."))
@click.option('--orchest_token', default=environ.get('ORCHEST_TOKEN'),
              help=("Env var: ORCHEST_TOKEN."))
def upload_image(**kwargs):
    config = prepare(**kwargs)
    customer = environ.get('CUSTOMER', environ.get('CI_PROJECT_NAME'))
    version_tag = environ.get('VERSION').replace('.', '')
    image_name = '{customer}_{ver}'.format(
        customer=customer.replace(' ', '').replace(',', '_'),
        ver=version_tag
    )

    environ.update({'_IMAGE_NAME': image_name})
    image_sha = build_image()
    tags = [image_sha]
    is_latest = False
    if environ.get('CI_COMMIT_REF_NAME') == environ.get('VERSION'):
        tags.append('latest')
        is_latest = True
    customer_img = '{customer}{ver}'.format(customer=customer.strip(),
                                            ver=version_tag)
    image_repo = '{url}/{image}'.format(url=environ.get('IMAGE_REPO_URL'),
                                        image=customer_img)
    environ.update({'_IMAGE_REPO': image_repo})
    push_image(tags)
    notify_orchest(image_sha, customer_img, is_latest=is_latest)
    sys.exit(0)
