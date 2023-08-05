# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@panodata.org>
# License: GNU Affero General Public License, Version 3
import logging
import sys

import click

from kahn.core import ForwardingEngine
from kahn.util import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
@click.option("--verbose", is_flag=True, required=False, help="Increase log verbosity.")
@click.option("--debug", is_flag=True, required=False, help="Enable debug messages.")
@click.pass_context
def cli(ctx, verbose, debug):
    log_level = logging.INFO
    if verbose or debug:
        log_level = logging.DEBUG
    setup_logging(level=log_level)


@click.command()
@click.option("--source", type=str, required=True, help="Where to receive telemetry data from")
@click.option("--target", type=str, required=True, help="Where to send telemetry data to")
@click.pass_context
def forward(ctx, source: str, target: str):
    forwarder = ForwardingEngine(source=source, target=target)
    forwarder.run()
    print("Ready.", file=sys.stderr)


cli.add_command(forward, name="forward")
