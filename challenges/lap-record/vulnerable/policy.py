"""Deliberate gap in this synthetic training service: reported times are recorded as sent."""


def recorded_time(marks, report):
    return report[-1]['t_ms']
