# packet-sender

## Introduction
send packet with tcpreplay

## Install

### Dependencies

#### Debian/Ubuntu

```bash
sudo apt install -y tcpreplay
```

#### CentOS/RedHat

```bash
yum install -y tcpreplay
```

### Install from source

1.  `git clone https://github.com/zzsuki/packet-replayer.git`
2.  `cd packet-replayer`
3.  `python setup.py install --record record.txt`

**make setup install record in record.txt，which will make uninstall convenient**

### Install from pip

```bash
pip install git+https://github.com/zzsuki/packet-replayer.git
```

### Uninstall

- when install by setup: `sudo python3 uninstall.py` (built-in uninstall script, which will remove all materials in record.txt)
- when install by pip: `pip uninstall packet-replayer`


### Usage

```bash
Usage: packet-replayer [OPTIONS] COMMAND [ARGS]...

  Packet replay tool based on tcpreplay and tcpwrite Only ``pps`` can set
  duration by setting env ``DURATION``.

Options:
  -i, --interface TEXT            Interface to replay, like `-i` in tcpreplay,
                                  required.  [required]
  -l, --level [debug|info|warning|error|critical]
                                  log level, Optional.
  -t, --fast                      replay as fast as possible NOTE: This
                                  argument is mutually exclusive with
                                  arguments: [mbps, pps].
  -p, --pps INTEGER               replay as given pps(packet per second),
                                  default replay 20s NOTE: This argument is
                                  mutually exclusive with  arguments: [mbps,
                                  fast].
  -m, --mbps FLOAT                replay as given bandwidth(units: `mbps`)
                                  NOTE: This argument is mutually exclusive
                                  with  arguments: [pps, fast].
  -f, --file TEXT                 file or directory to replay, when directory,
                                  replay all pcap files in it.  [required]
  -h, --help                      show help message and exit

Commands:
  replay-modified  replay pcap and modify src ip and dst ip
  replay-raw       replay pcap without any modification
```

#### Example

1. `packet-replayer -i enp3s0 -f pcaps/s7comm.pcap -p 300  replay-raw` will replay raw pcap `pcaps/s7comm.pcap` on interface `enp3s0` at 300pps and last 20s


