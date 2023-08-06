# coding: utf-8

import click
from deployv_addon_gitlab_tools.checkers import check_all
from deployv_addon_gitlab_tools.common import check_credentials, prepare
import logging
from os import environ


_logger = logging.getLogger('deployv.' + __name__)


@click.command()
@click.option('--private_deploy_key',
              default=environ.get('PRIVATE_DEPLOY_KEY', False),
              help="Env var: PRIVATE_DEPLOY_KEY.")
@click.option('--ignore_checks',
              default=environ.get('IGNORE_CHECKS', False),
              help="Env var: IGNORE_CHECKS.")
def check_keys(private_deploy_key, ignore_checks):
    """Checks if the .ssh folder exists, creates it and add the private key
    if necessary"""
    _logger.info('Check keys command')
    if not ignore_checks:
        check_all()
    config = prepare(private_deploy_key=private_deploy_key)
    check_credentials(config)
