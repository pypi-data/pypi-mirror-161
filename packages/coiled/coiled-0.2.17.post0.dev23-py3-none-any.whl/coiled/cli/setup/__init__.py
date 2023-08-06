import click

from ..utils import CONTEXT_SETTINGS
from .aws import aws_setup
from .entry import setup_wizard


@click.group(context_settings=CONTEXT_SETTINGS)
def setup():
    """Setup Coiled with cloud provider"""
    pass


setup.add_command(setup_wizard, "wizard")
setup.add_command(aws_setup, "aws")
