# packet_sender

## Introduction
send packet with tcpreplay

## Install

### Install from source

1.  `git clone https://gitee.com/he_weidong/packet_sender.git`
2.  `cd packet_sender`
3.  `python setup.py install --record record.txt`

**make setup install record in record.txt，which will make uninstall convenient**

### Install from pip

```bash
pip install git+https://gitee.com/he_weidong/packet_sender.git
```



#### 卸载

1. `sudo python3 uninstall.py` (仅支持保存了record文件的方式)

#### 使用说明

1.  参数说明：详见`packet-sender -h`结果

##### 示例

1. `packet-sender -i enp3s0 -f pcaps/s7comm.pcap -p 300  replay-modified`


