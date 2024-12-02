import sqlite3
import random

# Упражнение №1: Создание и заполнение таблиц

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  --Обратите внимание на id
    reader_id INTEGER,
    book_id INTEGER,
    taking_date TEXT,
    returning_date TEXT,
    FOREIGN KEY (reader_id) REFERENCES Readers(id),
    FOREIGN KEY (book_id) REFERENCES Books(id)
);
    
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Readers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Records (
        reader_id INTEGER,
        book_id INTEGER,
        taking_date TEXT,
        returning_date TEXT,
        FOREIGN KEY (reader_id) REFERENCES Readers(id),
        FOREIGN KEY (book_id) REFERENCES Books(id)
    )
''')


authors = ["Лев Толстой", "Фёдор Достоевский", "Антон Чехов", "Михаил Булгаков"]
titles = ["Война и мир", "Преступление и наказание", "Вишнёвый сад", "Мастер и Маргарита"]

for i in range(5):
    author = random.choice(authors)
    title = random.choice(titles) + f" ({i+1})" # Добавляем номера для уникальности
    year = random.randint(1850, 2023)
    cursor.execute("INSERT INTO Books (author, title, publish_year) VALUES (?, ?, ?)", (author, title, year))

for i in range(3):
    name = f"Читатель {i+1}"
    cursor.execute("INSERT INTO Readers (name) VALUES (?)", (name,))


readers = cursor.execute("SELECT id FROM Readers").fetchall()
books = cursor.execute("SELECT id FROM Books").fetchall()

for i in range(5):
    reader_id = random.choice(readers)[0]
    book_id = random.choice(books)[0]
    taking_date = f"2024-10-{random.randint(1, 20)}"
    returning_date = None if random.random() < 0.5 else f"2024-11-{random.randint(1, 20)}"
    cursor.execute("INSERT INTO Records (reader_id, book_id, taking_date, returning_date) VALUES (?, ?, ?, ?)", (reader_id, book_id, taking_date, returning_date))


conn.commit()



# Упражнение №2: Select запросы

# 1. Книги, находящиеся в данный момент на руках у читателей
cursor.execute('''
    SELECT
        b.id,
        b.title
    FROM
        Books b
    JOIN
        Records r ON b.id = r.book_id
    WHERE
        r.returning_date IS NULL
''')
print("Книги, находящиеся на руках у читателей:")
for row in cursor.fetchall():
    print(row)

# 2. Имена читателей и названия книг, которые они когда-либо брали
cursor.execute('''
    SELECT
        r.name,
        b.title
    FROM
        Readers r
    JOIN
        Records rec ON r.id = rec.reader_id
    JOIN
        Books b ON rec.book_id = b.id
''')
print("\nИмена читателей и названия книг, которые они брали:")
for row in cursor.fetchall():
    print(row)


# 3. Количество книг для каждого автора
cursor.execute('''
    SELECT
        author,
        COUNT(*) AS num_books
    FROM
        Books
    GROUP BY
        author
''')
print("\nКоличество книг для каждого автора:")
for row in cursor.fetchall():
    print(row)



# Упражнение №3: FULL OUTER JOIN (с помощью UNION ALL)

cursor.execute('''
    SELECT
        r.name,
        b.title
    FROM Readers r
    LEFT JOIN Records rec ON r.id = rec.reader_id
    LEFT JOIN Books b ON rec.book_id = b.id

    UNION ALL

    SELECT
        r.name,
        b.title
    FROM Readers r
    RIGHT JOIN Records rec ON r.id = rec.reader_id
    RIGHT JOIN Books b ON rec.book_id = b.id
''')
print("\nFULL OUTER JOIN (с помощью UNION ALL):")
for row in cursor.fetchall():
    print(row)

conn.close()
