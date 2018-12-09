import docker

from typing import Sequence, Optional

from phalski_ledshim import chart, color


def docker_container_monitor(pixels: Sequence[int], fg_color: color.Color, bg_color: Optional[color.Color] = None):
    docker_client = None

    def get_value(client):
        if client[0] is None:
            client[0] = docker.from_env()

        try:
            return len(client[0].containers.list())
        except:
            client[0] = None
            return 0

    return chart.Factory.bin_number_source(pixels, lambda: get_value([docker_client]), True, fg_color, bg_color or color.Factory.dim(fg_color, 0.25))
