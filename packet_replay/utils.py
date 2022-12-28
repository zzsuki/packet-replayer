from faker import Factory
import os


# 等价于设置语言区
fake = Factory.create('zh_CN')

# pylint: disable=no-member

class DataFaker:

    @classmethod
    def fake_ipv4(cls, area: str = None, network: bool = False, address_class: str = None, **kwargs):
        if not area:
            return fake.ipv4(network, address_class)
        if area == 'private':
            return fake.ipv4_private(network, address_class)
        if area == 'public':
            return fake.ipv4_public(network, address_class)
        return fake.ipv4(network, address_class)

    @classmethod
    def fake_mac_address(cls):
        return fake.mac_address()

    @classmethod
    def fake_hostname(cls, levels: int = 1, **kwargs):
        return fake.hostname(levels, **kwargs)

    @classmethod
    def fake_port(cls, is_system: bool = False, is_user: bool = False, is_dynamic: bool = False):
        """
        端口号策略
        :param is_dynamic: 动态端口/私有端口/临时端口，49152-65535
        :param is_user: 用户常用端口或注册的端口，1024-49151
        :param is_system: 是否使用系统或常见服务端口，0-1023
            端口定义可见： https://datatracker.ietf.org/doc/html/rfc6335
        :return:
        """
        return fake.port_number(is_system, is_user, is_dynamic)

    @classmethod
    def fake_ipv6(cls):
        return fake.ipv6()


def get_all_files_in_dir(dictionary: str):
    """return all files(include file in subdir) in dictionary"""
    if not os.path.exists(dictionary):
        raise FileNotFoundError(f"{dictionary} doesn't exists")

    file_paths = []
    for root, _, files in os.walk(dictionary):
        for file in files:
            file_paths.append(os.path.abspath(os.path.join(root, file)))
    return file_paths


if __name__ == '__main__':
    print(get_all_files_in_dir('/root/repos/deploy/site.yml'))
