"""
    lager.usb.commands

    Commands for USB interaction
"""
import click
from ..context import get_default_gateway

@click.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.argument('DEVICE', required=False)
@click.argument('ACTION', required=False, type=click.Choice(['on', 'off', 'toggle']))
def usb(ctx, gateway, device, action):
    """
        Control USB ports on a DUT
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    if action is None:
        data = {'action': 'list'}
    else:
        data = {'action': action, 'hub': device}
    session = ctx.obj.session
    resp = session.usb_command(gateway, data)
    output = resp.json()
    if 'error' in output:
        click.secho(output['error'], nl=False, color='red', err=True)
    else:
        if action is None:
            click.echo('Devices:')
            for k, val in output.items():
                click.echo(f'  {k}')
                for line in val.split('\n'):
                    click.echo(f'    {line}')
        else:
            if output['stderr']:
                click.echo(output['stderr'], nl=False, err=True)
            if output['stdout']:
                click.echo(output['stdout'], nl=False)
