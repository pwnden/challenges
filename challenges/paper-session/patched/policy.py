def role(cookie, sessions):
    return sessions.get(cookie.get('paper_sid', ''), 'guest')
