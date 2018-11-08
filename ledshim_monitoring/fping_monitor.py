import re
import shutil
import subprocess

from collections import Counter
from typing import NamedTuple, Optional, Sequence, Tuple

from phalski_ledshim.charting import ChartSource, HealthStat, ValueSpecification

if not shutil.which('fping'):
    raise OSError('fping executable not in PATH')


class Status:
    ALIVE = 'alive'
    UNREACHABLE = 'unreachable'
    UNKNOWN_ADDRESS = 'unknown_address'


TargetSpecification = NamedTuple('TargetSpecification', [
    ('target', str),
    ('required', bool),
    ('t_warn', float),
    ('t_err', float)
])

TargetResult = NamedTuple('TargetResult', [
    ('target', str),
    ('xmt', Optional[int]),
    ('rcv', Optional[int]),
    ('loss_percent', Optional[int]),
    ('min', Optional[float]),
    ('avg', Optional[float]),
    ('max', Optional[float]),
    ('text', Optional[str]),
    ('status', str)
])

ResultStats = NamedTuple('ResultStats', [
    ('targets', int),
    ('alive', int),
    ('unreachable', int),
    ('unknown_addresses', int),
])


def parse_fping_result_stderr(stderr: bytes):
    result = {}
    for line in bytes.decode(stderr).split('\n'):
        if not line:
            continue

        m = re.fullmatch(
            '^(?P<target>[^ ]+) {,20}: (?:xmt/rcv/%loss = (?P<xmt>\d+)/(?P<rcv>\d+)/(?P<loss_percent>\d+)%(?:, min/avg/max = (?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+))?|(?P<text>.{,50}))$',
            line)
        if m:
            d = m.groupdict()

            if d['text'] == 'Name or service not known':
                status = Status.UNKNOWN_ADDRESS
            elif d['min']:  # or max or avg, doesn't matter
                status = Status.ALIVE
            else:
                status = Status.UNREACHABLE

            result[d['target']] = TargetResult(
                d['target'],
                int(d['xmt']) if d['xmt'] else None,
                int(d['rcv']) if d['rcv'] else None,
                int(d['loss_percent']) if d['loss_percent'] else None,
                float(d['min']) if d['min'] else None,
                float(d['avg']) if d['avg'] else None,
                float(d['max']) if d['max'] else None,
                d['text'],
                status
            )

    return result


def run_fping(count: int, timeout: int, *args: str):
    result = subprocess.run(
        ['fping', '-c%d' % count, '-t%d' % timeout, '-s'] + list(args), stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE)
    return parse_fping_result_stderr(result.stderr)


def calc_stats(results: Sequence[TargetResult]):
    counter = Counter([r.status for r in results])
    return ResultStats(len(results), counter[Status.ALIVE], counter[Status.UNREACHABLE],
                       counter[Status.UNKNOWN_ADDRESS])


def fping_monitor(pixels: Sequence[int], t_warn: float, t_err: float, *args: TargetSpecification):
    ok = 0.0
    warn = 0.5  # slow ping
    err = 0.8  # really slow ping
    critical = 1.0  # unreachable

    if not args:
        raise ValueError('Empty args, please specify targets')

    targets = args
    ping_count = 1
    ping_timeout = 500

    def get_value():
        result = run_fping(ping_count, ping_timeout, *[t.target for t in targets])

        target_status = {}
        for t in targets:
            r = result[t.target]

            if not r:  # we don't know so assume worst
                return critical

            if not r.status == Status.ALIVE:
                if t.required:
                    return critical

                target_status[t.target] = critical
                continue

            if r.avg < t.t_warn:
                target_status[t.target] = ok
            elif r.avg < t.t_err:
                target_status[t.target] = warn
            else:
                target_status[t.target] = err

        l = target_status.values()
        v = sum(l) / float(len(l))
        return v

    return ChartSource(pixels, HealthStat(len(pixels), ValueSpecification(0.0, 1.0), t_warn, t_err), get_value)


if __name__ == '__main__':
    result = run_fping(1, 500, '10.3.14.14', '1.1.1.1', '10.3.14.13', 'asdfasdfsdfvasdgf.com')
    # result = subprocess.run(['fping', '-c1', '-t500', '-s'] + ['10.3.14.14', '1.1.1.1', '10.3.14.13', 'asdfasdfsdfvasdgf.com'],
    #                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # r = parse_fping_result_stderr(result.stderr)
    print(calc_stats(result.values()))
