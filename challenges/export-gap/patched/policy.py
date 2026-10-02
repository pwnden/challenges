def export_allowed(note, user):
    return user is not None and note['owner'] == user
