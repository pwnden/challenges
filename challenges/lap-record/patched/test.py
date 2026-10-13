"""Keep the honest run, the time gaps and the reset working while rejecting a forged record."""
import runpy
import time
from pathlib import Path

solve = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'solve/solve.py'))
Client, run_course = solve['Client'], solve['run_course']


def check():
    client = Client()
    status, track = client.request('/api/track')
    assert status == 200 and track['best_ms'] is None and 'trophy' not in track
    assert [row['name'] for row in track['leaderboard']] == ['바람개비', '도토리', '구름', '솜사탕']
    assert Client().request('/api/run/start', {})[0] == 401
    status, run = client.request('/api/run/start', {})
    assert status == 200
    run_id = run['run_id']
    assert client.request('/api/run/checkpoint', {'run_id': run_id, 'id': 1})[0] == 429
    assert client.request('/api/run/checkpoint', {'run_id': run_id, 'id': 2})[0] == 400
    assert client.request('/api/run/checkpoint', {'run_id': 999, 'id': 1})[0] == 404
    assert client.request('/api/run/finish', {'run_id': run_id, 'checkpoints': []})[0] == 409
    run_id, marks = run_course(client)
    honest = [{'id': number, 't_ms': value} for number, value in enumerate(marks, 1)]
    for report in ([], honest[:-1], [{'id': 1, 't_ms': 5}] + honest[1:], [{'id': 1, 't_ms': True}] + honest[1:]):
        assert client.request('/api/run/finish', {'run_id': run_id, 'checkpoints': report})[0] in (400, 422)
    forged = [{'id': number, 't_ms': number * 1000} for number in range(1, 7)]
    assert client.request('/api/run/finish', {'run_id': run_id, 'checkpoints': forged})[0] == 422
    status, result = client.request('/api/run/finish', {'run_id': run_id, 'checkpoints': honest})
    assert status == 200 and result['best_ms'] == marks[-1] and 'trophy' not in result
    assert result['best_ms'] >= 12000
    assert client.request('/api/run/finish', {'run_id': run_id, 'checkpoints': honest})[0] == 409
    status, again = client.request('/api/reset', {})
    assert status == 200 and again['best_ms'] is None
    print('an honest run, spacing between stars and reset work; forged times are rejected')


if __name__ == '__main__':
    check()
