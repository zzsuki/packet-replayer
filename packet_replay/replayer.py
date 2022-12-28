"""
 # @ Author: zzsuki
 # @ Create Time: 2020-11-23 14:58:28
 # @ Modified by: zzsuki
 # @ Modified time: 2020-11-23 14:58:32
 # @ Description:
"""
import os
from .logger import get_logger
import shortuuid


LOGGER = get_logger(__file__)
PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PCAPS_ROOT_PATH = '/tmp'


class PacketSender:

    def __init__(self, interface):
        self.interface = interface
        if not self.interface:
            raise ValueError('Interface not given or set.')
        self.temp_pcap = os.path.join(PCAPS_ROOT_PATH, f'{shortuuid.ShortUUID().random(length=10)}temp.pcap')
        self.cache_pcap = os.path.join(PCAPS_ROOT_PATH, f'{shortuuid.ShortUUID().random(length=10)}cache.pcap')

    @staticmethod
    def get_pcap_files(dictionary):
        """
        find all file endswith `pcap` or `pcapng` in dictionary(include subdirectory)
        """
        if not os.path.exists(dictionary):
            raise FileNotFoundError(f'{dictionary} does not exist.')

        src_file_paths: list = []
        if not os.path.isdir(dictionary):
            src_file_paths.append(os.path.abspath(dictionary))

        for root, _, files in os.walk(dictionary):
            for file in files:
                src_file_paths.append(os.path.abspath(os.path.join(root, file)))
        src_pcap_files = list(filter(lambda x: x.endswith('pcap') or x.endswith('pcapng'), src_file_paths))
        return src_pcap_files

    def tcpprep(self, file, auto='client'):
        """divide pacp in client and server"""
        cmd = f'tcpprep -a {auto} -i {file} -o {self.cache_pcap}'
        os.system(cmd)
        return self.cache_pcap

    # def modify_ip(self, file, src_ip, dst_ip):
    #     """
    #     modify ip in pcap file
    #     """
    #     cmd = f'tcprewrite -e {src_ip}:{dst_ip} -c {self.tcpprep(file)} -i {file} -o {self.temp_pcap}'
    #     os.system(cmd)
    #     LOGGER.info(f'[+] : IP was set to {src_ip} and {dst_ip}')

    #     return self.temp_pcap

    # -K ： use cache to send
    # -p :  packets sent per second
    # -L :  packets limit nums to send
    # -l :  loop nums of pcap_file
    # -t :  send packet as fast as tcpreplay can

    def send_pps_packet(self, file, pps: int):
        """基于pps发包"""
        if not os.path.exists(file):
            LOGGER.error(f'[+] pcap file {file} does not exists')
            return
        DURATION = os.environ.get('DURATION', '20')
        cmd = f'tcpreplay -i {self.interface} -K -p {pps} -L {pps * DURATION} -l {pps * DURATION} {file}'
        try:
            os.system(cmd)
            LOGGER.info(f'[+] : Packets sent with {pps} pps ..')
        except Exception as e:
            LOGGER.error(e, exc_info=True)

    def send_mbps_packet(self, file, mbps: float):
        """基于带宽发包, 不支持设置持续时间(因为带宽无法换算为pps)"""
        if not os.path.exists(file):
            LOGGER.error(f'[+] pcap file {file} does not exists')
            return
        cmd = f'tcpreplay -i {self.interface} -K -M {mbps} -l {10000000} {file}'
        try:
            os.system(cmd)
            LOGGER.info(f'[+] : Packets sent with {mbps} Mbps ..')
        except Exception as e:
            LOGGER.error(e, exc_info=True)

    def send_topspeed_packet(self, file):
        """
        最快速度发包
        """
        if not os.path.exists(file):
            LOGGER.error(f'[+] pcap file {file} does not exists')
            return

        cmd = f'tcpreplay -i {self.interface} -K -t -l {10000000} {file}'
        try:
            os.system(cmd)
            LOGGER.info('[+] : Packets sent as fast as possible ..')
        except Exception as e:
            LOGGER.error(e, exc_info=True)

    def modify_pcap(self, file, src_ip, dst_ip, src_mac=None, dst_mac=None):
        """
        修改pcap文件中的ip和mac地址
        """
        cmd = f'tcprewrite -e {src_ip}:{dst_ip} -c {self.tcpprep(file)} -i {file} -o {self.temp_pcap}'
        # gen mac expr
        if src_mac is None or dst_mac is None:
            mac_expr = ''
            LOGGER.warning(f"Got None mac address: {src_mac, dst_mac}, won't modify mac address")
        else:
            mac_expr = f"--enet-dmac={src_mac},{dst_mac} --enet-smac={dst_mac},{src_mac}"
        # gen ip expr
        if src_ip is None or dst_ip is None:
            ip_expr = ''
            LOGGER.warning(f"Got None ip address: {src_mac, dst_mac}, won't modify ip address")
        else:
            ip_expr = f'-e {src_ip}:{dst_ip}'
        # gen full cmd
        cmd = f"tcprewrite {mac_expr} {ip_expr} -c {self.tcpprep(file)} -i {file} -o {self.temp_pcap}"
        os.system(cmd)
        LOGGER.info(f'[+] : IP was set to {src_ip} and {dst_ip}, MAC was set to {src_mac} and {dst_mac}')
        return self.temp_pcap

    # def send_packet_in_dir(self, directory):
    #     src_pcap_files = self.get_pcap_file(directory)
    #     for pcap_file in src_pcap_files:
    #         self.send_pcap_file(pcap_file, is_raw_pcap)

    # def send_all_packets(self):
    #     # send ics protocol
    #     self.send_packet_in_dir('{}/pcaps'.format(PROJECT_PATH), is_raw_pcap)

    def __repr__(self):
        return f'<{self.__class__.__name__}> {self.interface}'

    def __str__(self):
        return self.__repr__()

    def __del__(self):
        if os.path.exists(self.cache_pcap):
            os.remove(self.cache_pcap)
            LOGGER.info(f'[+] : Sending Finished, {self.cache_pcap} has been removed.')
        if os.path.exists(self.temp_pcap):
            os.remove(self.temp_pcap)
            LOGGER.info(f'[+] : Sending Finished, {self.temp_pcap} has been removed.')


if __name__ == '__main__':
    # ps = PacketSender()
    # print(PCAPS_ROOT_PATH)
    ...
