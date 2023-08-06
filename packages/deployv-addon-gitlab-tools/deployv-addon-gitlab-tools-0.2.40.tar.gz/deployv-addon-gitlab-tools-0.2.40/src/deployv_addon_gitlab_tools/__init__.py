# coding: utf-8

import click
import logging
from deployv_addon_gitlab_tools.commands import (
    check_keys, test_images, upload_image, deployv_tests, push_coverage,
    build_image, test_image, check_log, test_repo
)

__version__ = "0.2.40"
_logger = logging.getLogger('deployv.' + __name__)


@click.group(invoke_without_command=True)
@click.pass_context
def gitlab_tools(ctx):
    """Deployv addon: Gitlab tools.
    """
    ctx.command.config = ctx.parent.command.config
    parent = ctx.parent.params
    _logger.log(
        getattr(logging, parent.get('log_level', 'INFO')),
        "Deployv addon: Gitlab tools (ver: %s).",
        __version__
    )
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())


for command in [
        check_keys.check_keys,
        test_images.test_images,
        upload_image.upload_image,
        deployv_tests.deployv_tests,
        push_coverage.push_coverage,
        build_image.build_image,
        test_image.test_image,
        check_log.check_log,
        test_repo.test_repo,
]:
    gitlab_tools.add_command(command)


@click.command()
def cli():
    click.echo("You can use 'Deployv addon: Gitlab Tools' from 'deployvcmd'.")
    click.echo("Run 'deployvcmd gitlab_tools --help' for more information.")
