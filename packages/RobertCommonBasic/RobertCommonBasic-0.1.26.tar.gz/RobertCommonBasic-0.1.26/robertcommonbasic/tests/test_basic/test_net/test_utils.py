from robertcommonbasic.basic.net.utils import *


def test_ip():
    print(get_host_name())
    print(get_host_ip())
    adds = get_host_ips()
    for addr in adds:
        print(addr)


def test_port():
    r1 = check_ip_in_use(f"192.168.1.36:47808", 'udp')
    print(r1)


test_port()