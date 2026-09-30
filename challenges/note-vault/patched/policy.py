def read_note(notes, note_id, user):
    note = notes.get(note_id)
    if note is None or note["owner"] != user:
        return None
    return note
