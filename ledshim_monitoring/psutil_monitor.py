import psutil

from socket import AddressFamily
from typing import Sequence, Optional

from phalski_ledshim import color, chart


def ip_to_int(ip: str):
    parts = ip.split('.')
    if not len(parts) == 4:
        raise AssertionError('ip does not contain 4 blocks')

    octets = [int(x) for x in parts]
    n = 0
    for i, o in enumerate(reversed(octets)):
        n |= o << 8 * i

    return n


def inet_addr(net_if_name: str):
    net_if = next(filter(lambda x: x[0] == net_if_name, psutil.net_if_addrs().items()))
    if not net_if:
        raise ValueError('net_if not found: %s' % net_if_name)

    name, addrs = net_if
    addr = next(filter(lambda x: x.family == AddressFamily.AF_INET, addrs))
    if not addr:
        raise ValueError('no inet addr configured for net_if: %s' % net_if_name)

    return addr


def extract_host_id(addr):
    return ip_to_int(addr.address) & ~ip_to_int(addr.netmask)


def get_host_id_of_inet_addr(net_if_name: str):
    try:
        id = extract_host_id(inet_addr(net_if_name))
        print(id)
        return id
    except ValueError:
        return 0


def cpu_mem_monitor(pixels: Sequence[int], brightness: float = 1.0, bg_shade: float = -0.75, invert_bars: bool = False):
    value_sources = (lambda: psutil.cpu_percent(), lambda: psutil.virtual_memory().percent)
    red, blue = tuple(reversed(value_sources)) if invert_bars else value_sources

    return chart.Factory.red_blue_bar_chart_source(pixels,
                                                   red,
                                                   blue,
                                                   chart.Factory.spec(0, 100, False, True),
                                                   chart.Factory.spec(0, 100, False, True),
                                                   brightness,
                                                   bg_shade)


def cpu_monitor(pixels: Sequence[int], fg_color: color.Color = color.NamedColor.WHITE,
                bg_color: Optional[color.Color] = None):
    return chart.Factory.bar_chart_source(pixels, lambda: psutil.cpu_percent(), chart.Factory.spec(0, 100, False, True),
                                          fg_color, bg_color or color.Factory.dim(fg_color, 0.25))


def mem_monitor(pixels: Sequence[int], fg_color: color.Color = color.NamedColor.WHITE,
                bg_color: Optional[color.Color] = None):
    return chart.Factory.bar_chart_source(pixels, lambda: psutil.virtual_memory().percent,
                                          chart.Factory.spec(0, 100, False, True), fg_color,
                                          bg_color or color.Factory.dim(fg_color, 0.25))


def disk_usage_monitor(pixels: Sequence[int], path: str = '/', fg_color: color.Color = color.NamedColor.WHITE,
                       bg_color: Optional[color.Color] = None):
    return chart.Factory.bar_chart_source(pixels, lambda: psutil.disk_usage(path).percent,
                                          chart.Factory.spec(0, 100, False, True), fg_color,
                                          bg_color or color.Factory.dim(fg_color, 0.25))


def cpu_health_monitor(pixels: Sequence[int], t_warn_percent: float = 75, t_err_percent: float = 90):
    return chart.Factory.health_stat_source(pixels, lambda: psutil.cpu_percent(), chart.Factory.spec(0, 100),
                                            t_warn_percent, t_err_percent)


def mem_health_monitor(pixels: Sequence[int], t_warn_percent: float = 75, t_err_percent: float = 90):
    return chart.Factory.health_stat_source(pixels, lambda: psutil.virtual_memory().percent, chart.Factory.spec(0, 100),
                                            t_warn_percent, t_err_percent)


def disk_usage_health_monitor(pixels: Sequence[int], path: str, t_warn_percent: float = 75, t_err_percent: float = 90):
    return chart.Factory.health_stat_source(pixels, lambda: psutil.disk_usage(path).percent, chart.Factory.spec(0, 100),
                                            t_warn_percent, t_err_percent)


def host_id_monitor(pixels: Sequence[int], net_if_name: str, fg_color: color.Color = color.NamedColor.WHITE,
                    bg_color: Optional[color.Color] = None):
    return chart.Factory.bin_number_source(pixels, lambda: get_host_id_of_inet_addr(net_if_name), True, fg_color,
                                           bg_color or color.Factory.dim(fg_color, 0.25))
