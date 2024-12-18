import sqlite3
import time
import random

def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    """)

def insert_data(cursor, num_records):
    cursor.executemany(
        "INSERT INTO test_data (title, content) VALUES (?, ?)",
        [(f"Title {i}", f"Content {i}") for i in range(num_records)]
    )

def measure_query_time(cursor, query, params=None):
    start_time = time.time()
    cursor.execute(query, params or ())
    cursor.fetchall()
    end_time = time.time()
    return end_time - start_time

if __name__ == "__main__":
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()

    create_table(cursor)

    record_counts = [1000, 10000, 100000, 1000000]
    results = []

    for count in record_counts:
        print(f"\nТест для {count} записів")

        cursor.execute("DELETE FROM test_data")
        connection.commit()

        start_time = time.time()
        insert_data(cursor, count)
        connection.commit()
        insert_time = time.time() - start_time

        select_time = measure_query_time(cursor, "SELECT * FROM test_data")

        update_time = measure_query_time(
            cursor,
            "UPDATE test_data SET title = ?, content = ? WHERE id = ?",
            ("Updated Title", "Updated Content", random.randint(1, count))
        )
        connection.commit()

        delete_time = measure_query_time(
            cursor,
            "DELETE FROM test_data WHERE id = ?",
            (random.randint(1, count),)
        )
        connection.commit()

        results.append((count, insert_time, select_time, update_time, delete_time))

    print("\nРезультати тестування:")
    print(f"{'Кількість записів':<15}{'INSERT (с)':<15}{'SELECT (с)':<15}{'UPDATE (с)':<15}{'DELETE (с)':<15}")
    for count, insert_time, select_time, update_time, delete_time in results:
        print(f"{count:<15}{insert_time:<15.5f}{select_time:<15.5f}{update_time:<15.5f}{delete_time:<15.5f}")

    with open("performance_results.txt", "w") as file:
        file.write("Результати тестування:\n")
        file.write(f"{'Кількість записів':<15}{'INSERT (с)':<15}{'SELECT (с)':<15}{'UPDATE (с)':<15}{'DELETE (с)':<15}\n")
        for count, insert_time, select_time, update_time, delete_time in results:
            file.write(f"{count:<15}{insert_time:<15.5f}{select_time:<15.5f}{update_time:<15.5f}{delete_time:<15.5f}\n")

    print("\nРезультати тестування збережено у файл 'performance_results.txt'.")
    connection.close()
