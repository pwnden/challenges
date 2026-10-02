def search(database, name):
    query = "SELECT name, note FROM members WHERE name = ? AND public = 1"
    return query, database.execute(query, (name,)).fetchall()
