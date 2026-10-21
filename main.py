import json
import sqlite3
import re

def main():
    with open("task1_d.json", "r", encoding="utf-8") as f:
        raw_text = f.read()

    json_text = re.sub(r':(\w+)=>', r'"\1":', raw_text)
    data = json.loads(json_text)

    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS books")
    
    cursor.execute("""
        CREATE TABLE books (
            id TEXT,
            title TEXT,
            author TEXT,
            genre TEXT,
            publisher TEXT,
            year INTEGER,
            price TEXT
        )
    """)

    insert_sql = """
        INSERT INTO books (id, title, author, genre, publisher, year, price) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    records = [
        (
            str(item["id"]),
            item["title"], 
            item["author"], 
            item["genre"], 
            item["publisher"], 
            item["year"], 
            item["price"]
        )
        for item in data
    ]
    
    cursor.executemany(insert_sql, records)
    conn.commit()

    cursor.execute("DROP TABLE IF EXISTS summary")
    
    summary_sql = """
        CREATE TABLE summary AS
        SELECT 
            year AS publication_year,
            COUNT(*) AS book_count,
            ROUND(
                AVG(
                    CASE 
                        WHEN SUBSTR(price, 1, 1) = '€' THEN CAST(SUBSTR(price, 2) AS REAL) * 1.2
                        WHEN SUBSTR(price, 1, 1) = '$' THEN CAST(SUBSTR(price, 2) AS REAL)
                    END
                ), 2
            ) AS average_price
        FROM books
        GROUP BY year
        ORDER BY year ASC;
    """
    cursor.execute(summary_sql)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM books")
    print(f"Row count in 'books' table: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM summary")
    print(f"Row count in 'summary' table: {cursor.fetchone()[0]}\n")

    print(f"{'publication_year':<17} | {'book_count':<11} | {'average_price'}")
    print("-" * 47)

    cursor.execute("SELECT publication_year, book_count, average_price FROM summary")
    for row in cursor.fetchall():
        print(f"{row[0]:<17} | {row[1]:<11} | {row[2]:.2f}")

    conn.close()

if __name__ == "__main__":
    main()