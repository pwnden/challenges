"""Record the time the server measured and reject a report that disagrees with it."""

TOLERANCE_MS = 1000


def recorded_time(marks, report):
    for mark, entry in zip(marks, report):
        if abs(entry['t_ms'] - mark) > TOLERANCE_MS:
            return None
    return marks[-1]
