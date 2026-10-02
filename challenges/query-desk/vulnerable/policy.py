def search(database, name):
    # Intentionally vulnerable: input becomes part of the SQL expression.
    query = f"SELECT name, note FROM members WHERE name = '{name}' AND public = 1"
    return query, database.execute(query).fetchall()
