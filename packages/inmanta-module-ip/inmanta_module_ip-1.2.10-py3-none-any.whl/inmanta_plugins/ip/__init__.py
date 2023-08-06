"""
    Copyright 2016 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""
import netaddr
from inmanta.plugins import plugin


@plugin
def hostname(fqdn: "string") -> "string":
    """
    Return the hostname part of the fqdn
    """
    return fqdn.split(".")[0]


@plugin
def network(ip: "ip::ip", cidr: "string") -> "string":
    """
    Given the ip and the cidr, return the network address
    """
    net = netaddr.IPNetwork(f"{ip}/{cidr}")
    return str(net.network)


@plugin
def cidr_to_network(cidr: "string") -> "string":
    """
    Given cidr return the network address
    """
    net = netaddr.IPNetwork(cidr)
    return str(net.network)


@plugin
def netmask(cidr: "number") -> "ip::ip":
    """
    Given the cidr, return the netmask
    """
    net = netaddr.IPNetwork(f"255.255.255.255/{cidr}")
    return str(net.netmask)


@plugin
def concat(host: "std::hoststring", domain: "std::hoststring") -> "std::hoststring":
    """
    Concat host and domain
    """
    return "%s.%s" % (host, domain)


@plugin
def net_to_nm(network_addr: "string") -> "string":
    net = netaddr.IPNetwork(network_addr)
    return str(net.netmask)


@plugin
def ipnet(addr: "ip::cidr_v10", what: "string") -> "string":
    """
    Return the ip, prefixlen, netmask or network address of the CIDR

    :param addr: CIDR
    :param what: The required result:

     - ip: The IP address of `addr` object.
     - prefixlen: The prefix length of `addr` object.
     - netmask: The subnet mask of `addr` object.
     - network: The network address of `addr` object.

    For instance:

        | std::print(ipnet("192.168.1.100/24", "ip"))         -->  192.168.1.100
        | std::print(ipnet("192.168.1.100/24", "prefixlen"))  -->  24
        | std::print(ipnet("192.168.1.100/24", "netmask"))    -->  255.255.255.0
        | std::print(ipnet("192.168.1.100/24", "network"))    -->  192.168.1.0
    """
    net = netaddr.IPNetwork(addr)
    if what == "ip":
        return str(net.ip)

    elif what == "prefixlen":
        return str(net.prefixlen)

    elif what == "netmask":
        return str(net.netmask)

    elif what == "network":
        return str(net.network)


@plugin
def ipindex(addr: "ip::cidr_v10", position: "number") -> "string":
    """
    Return the address at position in the network.
    """
    net = netaddr.IPNetwork(addr)
    return str(net[position])


@plugin
def is_valid_ip(addr: "string") -> "bool":
    try:
        net = netaddr.IPAddress(addr)
        return net.version == 4
    except Exception:
        return False


@plugin
def is_valid_cidr_v6(addr: "string") -> "bool":
    if "/" not in addr:
        return False
    try:
        net = netaddr.IPNetwork(addr)
        return net.version == 6
    except Exception:
        return False


@plugin
def is_valid_ip_v6(addr: "string") -> "bool":
    try:
        net = netaddr.IPAddress(addr)
        return net.version == 6
    except Exception:
        return False


@plugin
def is_valid_cidr(addr: "string") -> "bool":
    if "/" not in addr:
        return False
    try:
        net = netaddr.IPNetwork(addr)
        return net.version == 4
    except Exception:
        return False


@plugin
def is_valid_cidr_v10(addr: "string") -> "bool":
    """
    Validate if the string matches a v6 or a v4 network in CIDR notation
    """
    if "/" not in addr:
        return False
    try:
        netaddr.IPNetwork(addr)
        return True
    except Exception:
        return False


@plugin
def is_valid_ip_v10(addr: "string") -> "bool":
    """
    Validate if the string matches a v6 or v4 address
    """
    try:
        netaddr.IPAddress(addr)
        return True
    except Exception:
        return False


@plugin
def add(addr: "ip::ip_v10", n: "number") -> "ip::ip_v10":
    """
    Add a number to the given ip.
    """
    return str(netaddr.IPAddress(addr) + n)


@plugin
def is_valid_netmask(netmask: "string") -> "bool":
    """
    Validate if the string matches a netmask
    """
    try:
        return netaddr.IPAddress(netmask).is_netmask()
    except Exception:
        return False
