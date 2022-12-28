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
                ' NOTE: This argument is mutually exclusive with '
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
@click.option('-i', '--interface', required=True, help="发包的网卡，必填参数")
@click.option('-l', '--level', default='info',
              type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']), help="日志等级")
@click.option('-t', '--fast', is_flag=True, default=False, cls=MutuallyExclusiveOption,
              mutually_exclusive=['pps', 'mbps'], help="尽可能快发送")
@click.option('-p', '--pps', type=int, cls=MutuallyExclusiveOption,
              mutually_exclusive=['fast', 'mbps'], help="包发送速率，pps单位，默认发包20s")
@click.option('-m', '--mbps', type=float, cls=MutuallyExclusiveOption,
              mutually_exclusive=['fast', 'pps'], help="包发送速率，mbps单位")
@click.option('-f', '--file', required=True, callback=check_file, help="重放目标【文件或目录】")
@click.help_option("--help", "-h", help="显示帮助信息并退出")
@click.pass_context
def cli(ctx, interface, level, fast, pps, mbps, file):
    # 检查运行权限
    if not os.getuid() == 0:
        LOGGER.error("You must run this command as root")
        exit(-1)

    ctx.ensure_object(dict)
    ctx.obj['interface'] = interface
    ctx.obj['pps'] = pps
    ctx.obj['mbps'] = mbps
    ctx.obj['fast'] = fast
    ctx.obj['file'] = file


@cli.command()
@click.help_option("--help", "-h", help="显示帮助信息并退出")
@click.pass_context
def replay_raw(ctx):
    packet_sender = PacketSender(ctx.obj['interface'])
    packets = packet_sender.get_pcap_files(ctx.obj['file'])
    for packet in packets:
        if ctx.obj['pps'] is not None:
            packet_sender.send_pps_packet(packet, ctx.obj['pps'])
        elif ctx.obj['mbps'] is not None:
            packet_sender.send_mbps_packet(packet, ctx.obj['mbps'])
        elif ctx.obj['fast'] is not None:
            packet_sender.send_topspeed_packet(packet)
        else:
            LOGGER.error('One of [pps, mbps, fast] can must not  be None.')


@cli.command()
@click.option('-s', '--src_ip', type=str, default=None, help="源ip地址")
@click.option('-d', '--dst_ip', type=str, default=None, help="目的ip地址")
@click.help_option("--help", "-h", help="显示帮助信息并退出")
@click.pass_context
def replay_modified(ctx, src_ip, dst_ip):
    packet_sender = PacketSender(ctx.obj['interface'])
    packets = packet_sender.get_pcap_files(ctx.obj['file'])
    src_ip = DataFaker.fake_ipv4(area='private') if not src_ip else src_ip
    dst_ip = DataFaker.fake_ipv4(area='private') if not dst_ip else dst_ip
    for packet in packets:
        tmp_file = packet_sender.modify_pcap(file=packet, src_ip=src_ip, dst_ip=dst_ip)
        if ctx.obj['pps'] is not None:
            packet_sender.send_pps_packet(tmp_file, ctx.obj['pps'])
        elif ctx.obj['mbps'] is not None:
            packet_sender.send_mbps_packet(tmp_file, ctx.obj['mbps'])
        elif ctx.obj['fast'] is not None:
            packet_sender.send_topspeed_packet(tmp_file)
        else:
            LOGGER.error('One of [pps, mbps, fast] must not given.')


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
