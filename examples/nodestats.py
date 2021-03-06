import logging

# logging.basicConfig(level=logging.DEBUG)

from phalski_ledshim import app, color
from ledshim_monitoring import cpu_mem_monitor, disk_usage_health_monitor, host_id_monitor, fping_monitor, \
    TargetSpecification, docker_container_monitor

app = app.App(0.5)
app.configure_worker(30, host_id_monitor(app.pixels[0:4], 'eth0', color.NamedColor.TEAL))
app.configure_worker(2, docker_container_monitor(app.pixels[5:11], color.NamedColor.OLIVE))
app.configure_worker(0.5, cpu_mem_monitor(list(reversed(app.pixels[12:22])), 1.0, 0.15))
app.configure_worker(30, disk_usage_health_monitor(app.pixels[23:24], '/'))
app.configure_worker(5, fping_monitor(app.pixels[25:26], 0.5, 0.9999,
                                      TargetSpecification('10.3.14.14', True, 100, 300),
                                      TargetSpecification('1.1.1.1', False, 100, 300),
                                      TargetSpecification('8.8.8.8', False, 100, 300)
                                      )),
app.configure_worker(5, fping_monitor(app.pixels[26:27], 0.01, 0.25,
                                      TargetSpecification('10.3.14.1', False, 100, 300),
                                      TargetSpecification('10.3.14.2', False, 100, 300),
                                      TargetSpecification('10.3.14.3', False, 100, 300),
                                      TargetSpecification('10.3.14.4', False, 100, 300),
                                      TargetSpecification('10.3.14.5', False, 100, 300),
                                      TargetSpecification('10.3.14.6', False, 100, 300),
                                      TargetSpecification('10.3.14.7', False, 100, 300),
                                      TargetSpecification('10.3.14.8', False, 100, 300),
                                      )
                     )
app.exec()
