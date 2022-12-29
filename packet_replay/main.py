"""
 # @ Author: zzsuki
 # @ Create Time: 2020-08-12 06:57:32
 # @ Modified by: zzsuki
 # @ Modified time: 2020-08-12 07:00:19
 # @ Description:
"""
import os

from .replayer import PacketSender
from .logger import get_logger
import click
from .utils import DataFaker
import logging
import sys


LOGGER = get_logger(__file__)
BASH_PATH = os.path.dirname(__file__)


# pylint: disable=unused-argument

class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        _help = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = _help + (
                '. NOTE: This argument is mutually exclusive with '
                ' arguments: [' + ex_str + '].'
            )
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                f"Illegal usage: `{self.name}` is mutually exclusive with arguments `{', '.join(self.mutually_exclusive)}`."
            )

        return super().handle_parse_result(
            ctx,
            opts,
            args
        )


def check_file(ctx, param, value):
    if value is None:
        raise click.BadParameter('file不能为None')
    if not os.path.exists(value):
        raise click.BadParameter('文件不存在，请确认')

    return value


LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    'info': logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


@click.group()
@click.option('-i', '--interface', required=True, help="Interface to replay, like `-i` in tcpreplay.")
@click.option('-l', '--level', default='info',
              type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']), help="log level, Optional.")
@click.option('-t', '--fast', is_flag=True, default=False, cls=MutuallyExclusiveOption,
              mutually_exclusive=['pps', 'mbps'], help="replay as fast as possible")
@click.option('-p', '--pps', type=int, cls=MutuallyExclusiveOption,
              mutually_exclusive=['fast', 'mbps'], help="replay as given pps(packet per second), default replay 20s")
@click.option('-m', '--mbps', type=float, cls=MutuallyExclusiveOption,
              mutually_exclusive=['fast', 'pps'], help="replay as given bandwidth(units: `mbps`)")
@click.option('-f', '--file', required=True, callback=check_file, help="file or directory to replay, when directory, replay all pcap files in it.")
@click.help_option("--help", "-h", help="show help message and exit")
@click.pass_context
def cli(ctx, interface, level, fast, pps, mbps, file):
    """
    Packet replay tool based on tcpreplay and tcpwrite
    Only ``pps`` can set duration by setting env ``DURATION``.
    """
    # 检查运行权限
    if not os.getuid() == 0:
        LOGGER.error("You must run this command as root")
        sys.exit(-1)

    ctx.ensure_object(dict)
    ctx.obj['interface'] = interface
    ctx.obj['pps'] = pps
    ctx.obj['mbps'] = mbps
    ctx.obj['fast'] = fast
    ctx.obj['file'] = file


@cli.command()
@click.help_option("--help", "-h", help="show help message and exit")
@click.pass_context
def replay_raw(ctx):
    """replay pcap without any modification"""
    packet_sender = PacketSender(ctx.obj['interface'])
    packets = packet_sender.get_pcap_files(ctx.obj['file'])
    for packet in packets:
        if ctx.obj['pps'] is not None:
            packet_sender.replay_pps_packet(packet, ctx.obj['pps'])
        elif ctx.obj['mbps'] is not None:
            packet_sender.replay_mbps_packet(packet, ctx.obj['mbps'])
        elif ctx.obj['fast'] is not None:
            packet_sender.replay_topspeed_packet(packet)
        else:
            LOGGER.error('One of [pps, mbps, fast] can must not  be None.')


@cli.command()
@click.option('-s', '--src_ip', type=str, default=None, help="src ip address")
@click.option('-d', '--dst_ip', type=str, default=None, help="dst ip address")
@click.help_option("--help", "-h", help="show help message and exit")
@click.pass_context
def replay_modified(ctx, src_ip, dst_ip):
    """replay pcap and modify src ip and dst ip"""
    packet_sender = PacketSender(ctx.obj['interface'])
    packets = packet_sender.get_pcap_files(ctx.obj['file'])
    src_ip = DataFaker.fake_ipv4(area='private') if not src_ip else src_ip
    dst_ip = DataFaker.fake_ipv4(area='private') if not dst_ip else dst_ip
    for packet in packets:
        tmp_file = packet_sender.modify_pcap(file=packet, src_ip=src_ip, dst_ip=dst_ip)
        if ctx.obj['pps'] is not None:
            packet_sender.replay_pps_packet(tmp_file, ctx.obj['pps'])
        elif ctx.obj['mbps'] is not None:
            packet_sender.replay_mbps_packet(tmp_file, ctx.obj['mbps'])
        elif ctx.obj['fast'] is not None:
            packet_sender.replay_topspeed_packet(tmp_file)
        else:
            LOGGER.error('One of [pps, mbps, fast] must not given.')


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
