import click
import logging
import os
from os import environ
from deployv_addon_gitlab_tools.common import resume_log

_logger = logging.getLogger('deployv.' + __name__)


@click.command()
@click.option('--logpath',
              default=os.path.join('.', environ.get('CI_COMMIT_REF_SLUG', ''),
                   'ODOO_LOG',
                   'odoo.log'),
              help="Path where is saved odoo.log file. Env var: LOGPATH.")
def check_log(logpath):
    """Checks odoo log in image to analize if there are warnings
    and show them."""
    _logger.info('Check log command')
    logpath = os.path.join(logpath, "odoo.log")
    _logger.info("Odoo log path: %s", logpath)

    if not os.path.isfile(logpath):
        _logger.warn('Odoo log file was not found in path: %s', logpath)
        exit(2)

    with open(logpath) as flog:
        sucesss, log = resume_log(flog)

    all_warnings = log.get('warnings')
    all_warnings.extend(log.get('warnings_deprecated'))
    all_warnings.extend(log.get('warnings_trans'))

    if not all_warnings:
        exit(0)

    for warning in all_warnings:
        _logger.warn(warning)
    exit(1)
