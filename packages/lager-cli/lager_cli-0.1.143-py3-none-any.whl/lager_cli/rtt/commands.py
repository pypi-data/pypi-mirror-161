from threading import Thread
import click
from ..context import get_default_gateway, ensure_debugger_running
from ..paramtypes import MemoryAddressType
from ..openocd.commands import run_openocd_tunnel
import socket
import time

RTT_COMMANDS = """
rtt server stop 9090
rtt stop
reset halt
resume
rtt setup {start_addr} {memory_size} "{name}"
rtt start
rtt server start 9090 0
""".strip()

def read_until(s):
    output = []
    while True:
        byte = s.recv(1)
        output.append(byte)
        if byte == b'>':
            break
    return b''.join(output)

def threaded_function(start_addr, memory_size, name, host, port):
    commands = RTT_COMMANDS.format(
        start_addr=start_addr,
        memory_size=memory_size,
        name=name,
    )
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, port))
                read_until(s)
                for command in commands.split("\n"):
                    command = command.strip() + '\r\n'
                    s.sendall(command.encode())
                    time.sleep(0.05)
                    read_until(s)
                return
            except ConnectionRefusedError:
                continue
            except Exception as e:
                raise
                print(e)


@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--name', required=False, default="SEGGER RTT", help='RTT block name')
@click.option('--host', default='localhost', help='interface for telnet to bind. '
              'Use --host \'*\' to bind to all interfaces.', show_default=True)
@click.option('--port', default=4444, help='Port for telnet', show_default=True)
@click.option('--rtt-port', default=9090, help='Local RTT port', show_default=True)
@click.argument('start_addr', type=MemoryAddressType())
@click.argument('memory_size', type=MemoryAddressType())
def rtt(ctx, gateway, name, host, port, rtt_port, start_addr, memory_size):
    if gateway is None:
        gateway = get_default_gateway(ctx)

    ensure_debugger_running(gateway, ctx)

    thread = Thread(target=threaded_function, args=(start_addr, memory_size, name, host, port))
    thread.start()
    run_openocd_tunnel(ctx, host, port, gateway, rtt, rtt_port)
    thread.join()

