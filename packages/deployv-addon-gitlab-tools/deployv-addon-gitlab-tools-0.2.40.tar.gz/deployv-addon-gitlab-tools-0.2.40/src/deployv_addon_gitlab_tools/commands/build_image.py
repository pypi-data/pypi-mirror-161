# coding: utf-8

import click
from deployv_addon_gitlab_tools import common
import logging
from os import environ
import signal
import sys


_logger = logging.getLogger('deployv.' + __name__)


signal.signal(signal.SIGTERM, common.reciveSignal)
signal.signal(signal.SIGINT, common.reciveSignal)


@click.command()
@click.option('--ci_commit_ref_name', default=environ.get('CI_COMMIT_REF_NAME'),
              help=("The branch or tag name for which project is built."
                    " Env var: CI_COMMIT_REF_NAME."))
@click.option('--ci_pipeline_id', default=environ.get('CI_PIPELINE_ID'),
              help=("The unique id of the current pipeline that GitLab CI"
                    " uses internally. Env var: CI_PIPELINE_ID."))
@click.option('--ci_repository_url', default=environ.get('CI_REPOSITORY_URL'),
              help=("The URL to clone the Git repository."
                    " Env var: CI_REPOSITORY_URL."))
@click.option('--base_image', default=environ.get('BASE_IMAGE'),
              help=("Env var: BASE_IMAGE."))
@click.option('--odoo_repo', default=environ.get('ODOO_REPO'),
              help=("Env var: ODOO_REPO."))
@click.option('--odoo_branch', default=environ.get('ODOO_BRANCH'),
              help=("Env var: ODOO_BRANCH."))
@click.option('--version', default=environ.get('VERSION'),
              help=("Env var: VERSION."))
@click.option('--install', default=environ.get('MAIN_APP'),
              help=("Env var: MAIN_APP."))
@click.option('--ci_job_id', default=environ.get('CI_JOB_ID'),
              help=("The unique id of the current job that GitLab CI uses internally."
                    " Env var: CI_JOB_ID."))
@click.option('--psql_image', default=False,
              help=("Override the default postgresql image to use for the tests"
                    "(Notice that this will override the PSQL_VERSION too)"))
@click.option('--image_repo_url', default=environ.get('IMAGE_REPO_URL', "quay.io/vauxoo"),
              help=("The URL where the image repository is located."
                    " Env var: IMAGE_REPO_URL."))
@click.option('--push_image', is_flag=True,
              help="If set it will push the image when on the main branch after the tests")
def build_image(**kwargs):
    config = common.prepare(**kwargs)

    if config.get('push_image'):
        if not config.get('orchest_registry', False) or not config.get('orchest_token', False):
            _logger.error('To push the image you need to set ORCHEST_REGISTRY and ORCHEST_TOKEN env vars')
            sys.exit(1)

    common.clean_containers(config)
    common.pull_images([config['base_image'], ])
    common.run_build_image(config)
    is_latest = False

    if config.get('push_image'):
        # TODO: if we decide to build and push every image, just move the _IMAGE_TAG outside the if
        if not common.is_dev_repo(config):
            tag_latest = 'latest'
            if config.get('docker_image_repo'):
                tag_latest = '%s-%s-latest' % (config['main_app'], config['version'])
            common.push_image(config, config['instance_image'], tag_latest)
            is_latest = True
        common.push_image(config, config['instance_image'], config['image_tag'])
        common.notify_orchest(config, is_latest=is_latest)
        common.save_imagename(config)
    common.clear_images(config)
    sys.exit(0)
