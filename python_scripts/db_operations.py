from django.db import connection


def reset_sequence(table):
    table = 'bushelper_' + table.lower()
    with connection.cursor() as cursor:
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name LIKE %s", [table])
