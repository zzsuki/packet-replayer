import os
import sys

from setuptools import setup, find_packages


with open('README.md') as mdf:
    long_description = mdf.read()


def pip_install(packet_name: str) -> None:
    """
    Install packet

    Args:
        param packet_name (str): Packet name.

    Returns:
        void: None
    """

    os.system(f"{sys.executable} -m pip install {packet_name}")


def read_requirements(path):
    """
    Read requirements

    :param path: path
    """

    requires = []

    with open(path) as fp:
        install_requires = fp.read().split("\n")

        for ir in install_requires:
            if "-r" in ir:
                path = os.path.join(os.path.split(path)[0], ir.split(" ")[1])
                requires.extend(read_requirements(path))
            elif ir and "git" not in ir:
                requires.append(ir)

    return requires


setup(
    name="packet_replay",
    version="1.0.0",
    author="zzsuki",
    author_email="zzsuki@163.com",
    maintainer="zzsuki",
    maintainer_email="zzsuki@163.com",
    url="https://github.com/zzsuki/packet-sender.git",
    download_url="https://github.com/zzsuki/packet-sender.git",
    license="Not open source",
    description="packet sender based on tcpreplay",
    long_description=long_description,
    keywords=[
        "packet replay",
        "tcpreplay",
    ],
    zip_safe=False,
    packages=find_packages(),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "packet-replayer = packet_replay.main:cli",
        ],
    },
    include_package_data=True,  # MANIFEST.in
    setup_requires=[
        "setuptools",
    ],
    platforms="linux",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Not open source License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
)
