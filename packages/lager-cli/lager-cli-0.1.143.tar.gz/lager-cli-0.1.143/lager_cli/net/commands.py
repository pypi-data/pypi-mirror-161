"""
    lager.lister.commands

    List commands
"""
import click
from ..context import get_default_gateway
from texttable import Texttable

def channel_num(mux, mapping):
    point = mux['scope_points'][0][1]
    if mux['role'] == 'analog':
        return ord(point) - ord('A') + 1
    if mux['role'] == 'logic':
        return int(point) + 1
    try:
        numeric = int(point, 10)
        return numeric
    except ValueError:
        return ord(point) - ord('A') + 1

def get_nets(ctx, gateway):
    session = ctx.obj.session
    resp = session.all_muxes(gateway)
    resp.raise_for_status()
    return resp.json()['muxes']


def display_nets(muxes, netname):
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 't', 't'])
    table.set_cols_align(['l', 'r', 'r'])
    table.add_row(['name', 'type', 'channel'])
    for mux in muxes:
        for mapping in mux['mappings']:
            if netname is None or netname == mapping['net']:
                channel = channel_num(mux, mapping)
                table.add_row([mapping['net'], mux['role'], channel])

    click.echo(table.draw())

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
def net(ctx, gateway):
    """
        Lager net commands
    """
    if ctx.invoked_subcommand is not None:
        return

    if gateway is None:
        gateway = get_default_gateway(ctx)

    muxes = get_nets(ctx, gateway)

    display_nets(muxes, None)

def validate_net(ctx, muxes, netname, role):
    for mux in muxes:
        if mux['role'] != role:
            continue
        for mapping in mux['mappings']:
            if mapping['net'] == netname:
                return mapping
    raise click.UsageError(f'{role.title()} net with name `{netname}` not found!', ctx=ctx)

@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.option('--mcu', required=False)
@click.option('--clear', is_flag=True, default=False, required=False, help='Clear the associated mux')
@click.argument('NETNAME')
def mux(ctx, gateway, mcu, clear, netname):
    """
        Activate a Net
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)
    session = ctx.obj.session

    data = {
        'action': 'mux',
        'mcu': mcu,
        'params': {
            'clear': clear,
            'netname': netname,
        }
    }
    session.net_action(gateway, data).json()


@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.argument('NETNAME')
def show(ctx, gateway, netname):
    """
        Show the available nets which match a given name
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    muxes = get_nets(ctx, gateway)
    display_nets(muxes, netname)

@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.option('--mcu', required=False)
@click.option('--voltdiv', help='Volts per division')
@click.option('--timediv', help='Time per division')
@click.option('--voltoffset', help='Voltage offset')
@click.option('--timeoffset', help='Time offset')
@click.argument('NETNAME')
def trace(ctx, gateway, mcu, voltdiv, timediv, voltoffset, timeoffset, netname):
    """
        Trace options
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session

    data = {
        'action': 'trace',
        'mcu': mcu,
        'params': {
            'voltdiv': voltdiv,
            'timediv': timediv,
            'voltoffset': voltoffset,
            'timeoffset': timeoffset,
            'netname': netname,
        }
    }
    session.net_action(gateway, data).json()


@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.option('--mcu', required=False)
@click.option('--level', help='Voltage trigger level')
@click.option('--slope', help='Slope direction to trigger on')
@click.option('--mode', help='Trigger mode, e.g. Normal, Single Shot, Automatic')
@click.argument('NETNAME')
@click.argument('TRIGGERTYPE')
def trigger(ctx, gateway, mcu, level, slope, mode, netname, triggertype):
    """
        Options for setting the trigger parameters
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session

    data = {
        'action': 'trigger',
        'mcu': mcu,
        'params': {
            'level': level,
            'slope': slope,
            'mode': mode,
            'triggertype': triggertype,
            'netname': netname,
        }
    }
    session.net_action(gateway, data).json()


@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.option('--mcu', required=False)
@click.option('--vavg', is_flag=True, default=False, help='Average voltage')
@click.option('--freq', is_flag=True, default=False, help='Signal Frequency')
@click.argument('NETNAME')
def measure(ctx, gateway, mcu, vavg, freq, netname):
    """
        Measure voltage or frequency
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session

    data = {
        'action': 'measure',
        'mcu': mcu,
        'params': {
            'vavg': vavg,
            'freq': freq,
            'netname': netname,
        }
    }
    session.net_action(gateway, data).json()


@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.option('--mcu', required=False)
@click.option('--set-a', help='Set (x,y) location of cursor a')
@click.option('--set-b', help='Set (x,y) location of cursor b')
@click.option('--set-ax', help='Set (x) location of cursor a')
@click.option('--set-bx', help='Set (x) location of cursor b')
@click.option('--set-ay', help='Set (y) location of cursor a')
@click.option('--set-by', help='Set (y) location of cursor b')
@click.option('--move-a', help='Move cursor a from current position by (delta x, delta y)')
@click.option('--move-b')
@click.option('--move-ax')
@click.option('--move-bx')
@click.option('--move-ay')
@click.option('--move-by')
@click.option('--a-values', is_flag=True, default=False)
@click.option('--b-values', is_flag=True, default=False)
@click.argument('NETNAME')
def cursor(ctx, gateway, mcu, set_a, set_b, set_ax, set_bx, set_ay, set_by, move_a, move_b, move_ax, move_bx, move_ay, move_by, a_values, b_values, netname):
    """
        Adjust the scope's cursor
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session

    data = {
        'action': 'cursor',
        'mcu': mcu,
        'params': {
            'set_a': set_a,
            'set_b': set_b,
            'set_ax': set_ax,
            'set_bx': set_bx,
            'set_ay': set_ay,
            'set_by': set_by,
            'move_a': move_a,
            'move_b': move_b,
            'move_ax': move_ax,
            'move_bx': move_bx,
            'move_ay': move_ay,
            'move_by': move_by,
            'a_values': a_values,
            'b_values': b_values,
            'netname': netname,
        }
    }
    session.net_action(gateway, data).json()

@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.option('--mcu', required=False)
@click.option('--soc')
@click.option('--full')
@click.option('--empty')
@click.option('--curr-limit')
@click.option('--capacity')
@click.argument('NETNAME')
def battery(ctx, gateway, mcu, soc, full, empty, curr_limit, capacity, netname):
    """
        Control the battery simulator
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session

    data = {
        'action': 'battery',
        'mcu': mcu,
        'params': {
            'soc': soc,
            'full': full,
            'empty': empty,
            'curr_limit': curr_limit,
            'capacity': capacity,
            'netname': netname,
        }
    }
    session.net_action(gateway, data).json()


@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.option('--mcu', required=False)
@click.option('--max-settings', is_flag=True, default=False)
@click.option('--voltage')
@click.option('--current')
@click.argument('NETNAME')
def supply(ctx, gateway, mcu, max_settings, voltage, current, netname):
    """
        Control the power supply
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session

    data = {
        'action': 'supply',
        'mcu': mcu,
        'params': {
            'max_settings': max_settings,
            'voltage': voltage,
            'current': current,
            'netname': netname,
        }
    }
    session.net_action(gateway, data).json()


@net.command()
@click.pass_context
@click.option('--gateway', '--dut', required=False, help='ID of gateway to which DUT is connected')
@click.option('--mcu', required=False)
@click.option('--max-settings', is_flag=True, default=False)
@click.option('--voltage')
@click.option('--resistance')
@click.option('--current')
@click.option('--power')
@click.argument('NETNAME')
def eload(ctx, gateway, mcu, max_settings, voltage, resistance, current, power, netname):
    """
        Control the electronic load
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session

    data = {
        'action': 'eload',
        'mcu': mcu,
        'params': {
            'max_settings': max_settings,
            'voltage': voltage,
            'resistance': resistance,
            'current': current,
            'power': power,
            'netname': netname,
        }
    }
    session.net_action(gateway, data).json()
