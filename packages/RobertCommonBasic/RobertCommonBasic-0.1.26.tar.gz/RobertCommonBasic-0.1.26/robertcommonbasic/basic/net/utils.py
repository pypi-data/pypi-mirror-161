import os
import platform
import psutil
import re
import socket
import uuid

from ipaddress import ip_network, ip_address


# 查看当前主机名
def get_host_name():
    return socket.gethostname()


# 根据主机名称获取当前IP
def get_host_ip():
    return socket.gethostbyname(socket.gethostname())


# 获取当前主机IPV4 和IPV6的所有IP地址(所有系统均通用)
def get_host_ips(only_ipv4: bool = True):
    addrs = socket.getaddrinfo(get_host_name(), None)
    return [item[4][0] for item in addrs if ':' not in item[4][0]] if only_ipv4 is True else [item[4][0] for item in addrs]


def get_ip_by_net(ip: str):
    m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
    if m:
        (_ip, net, port) = m.groups()
        if _ip is not None and net is not None:
            __ip = f"{_ip}/{net}"
            ip_start = ip_address(str(ip_network(__ip, False)).split('/')[0])
            ip_end = ip_network(__ip, False).broadcast_address
            for k, v in psutil.net_if_addrs().items():
                for item in v:
                    if item[0] == 2:
                        item_ip = item[1]
                        if ':' not in item_ip:
                            item_ip = ip_address(item_ip)
                            if ip_start <= item_ip < ip_end:
                                return f"{item_ip}" if port is None else f"{item_ip}:{port}"
    return ip


def check_ip(ip: str):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    return False


# 获取MAC地址
def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)]).upper()


# 获取网段ip
def get_networks(ip: str):
    ips = []
    m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
    if m:
        (_ip, net, port) = m.groups()
        __ip = f"{_ip}/{net}" if net is not None else f"{_ip}/24"
        ip_start = ip_address(str(ip_network(__ip, False)).split('/')[0])
        num_addresses = ip_network(__ip, False).num_addresses
        for i in range(num_addresses):
            ips.append(str(ip_address(ip_start) + i))
    return ips


# 更改本机地址
def change_local_ip(ip: str) -> str:
    m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
    if m:
        (_ip, net, port) = m.groups()
        if _ip is not None and net is not None:
            ips = get_networks(ip)

            __ip = f"{_ip}/{net}"
            for k, v in psutil.net_if_addrs().items():
                for item in v:
                    if item[0] == 2:
                        item_ip = item[1]
                        if ':' not in item_ip:
                            item_ip = str(item_ip)
                            if item_ip in ips:
                                return f"{item_ip}:47808" if port is None else f"{item_ip}:{port}"
    return ip


def get_inuse_fun(ip: str, port: int, protocol: str = 'tcp'):

    def is_inuse_windows(ip, port, protocol):
        results = os.popen(f'netstat -p {protocol} -an | findstr "{ip}:{port}"').readlines()
        for result in results:
            if len(result) > 0 and result.find('LISTENING'):
                return True
        return False

    def is_inuse_linux(ip, port, protocol):
        cmd = f'netstat -tl | grep ":{port}"' if protocol == 'tcp' else f'netstat -ul | grep ":{port}"'
        results = os.popen(cmd).readlines()
        for result in results:
            if len(result) > 0 and result.find('LISTEN'):
                return True
        return False

    machine = platform.platform().lower()
    if 'windows-' in machine:
        return is_inuse_windows(ip, port, protocol)
    elif 'linux-' in machine:
        return is_inuse_linux(ip, port, protocol)
    else:
        raise Exception('Error, sorry, platform is unknown')


# 检测端口是否占用
def check_ip_in_use(ip: str, protocol: str='tcp') -> str:
    m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
    if m:
        (_ip, net, port) = m.groups()
        if _ip is not None and port is not None:
            return get_inuse_fun(_ip, int(str(port)), protocol)
    return False