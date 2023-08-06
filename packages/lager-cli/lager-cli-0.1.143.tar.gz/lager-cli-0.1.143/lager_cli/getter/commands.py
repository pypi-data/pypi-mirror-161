"""
    lager.getter.commands

    Getter commands
"""
import click
from ..config import read_config_file

@click.group(name='get')
def getter():
    """
        Lager getter commands
    """
    pass

@getter.command()
def defaults():
    """
        Get defaults
    """
    config = read_config_file()
    if config.has_option('LAGER', 'gateway_id'):
        gateway_id = config.get('LAGER', 'gateway_id')
    else:
        gateway_id = '<NOT SET>'
    click.echo(f'Default Gateway: {gateway_id}')

    if config.has_option('LAGER', 'serial_port'):
        serial_port = config.get('LAGER', 'serial_port')
    else:
        serial_port = '<NOT SET>'
    click.echo(f'Default Serial Port: {serial_port}')
