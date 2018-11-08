import docker

from phalski_ledshim import Color
from phalski_ledshim.charting import ChartSource, BinNumber
from typing import Sequence, Optional


def docker_container_monitor(pixels: Sequence[int], fg_color: Color, bg_color: Optional[Color] = None):
    if bg_color is None:
        bg_color = fg_color.dim(-0.75)

    docker_client = None

    def get_value(client):
        if client[0] is None:
            client[0] = docker.from_env()

        try:
            return len(client[0].containers.list())
        except:
            client[0] = None
            return 0

    return ChartSource(pixels, BinNumber(len(pixels), fg_color, bg_color), lambda: get_value([docker_client]))
