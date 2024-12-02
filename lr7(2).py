
import sqlite3
import datetime

def connect_db():
    """Подключается к существующей базе данных."""
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.OperationalError:
        print("База данных library.db не найдена.  Убедитесь, что вы запустили скрипт создания таблиц.")
        return None, None

def list_books(cursor):
    cursor.execute("SELECT id, author, title, publish_year FROM Books")
    print("\nСписок книг:")
    if cursor.rowcount == 0:
        print("Список книг пуст.")
    else:
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Автор: {row[1]}, Название: {row[2]}, Год издания: {row[3]}")

def list_readers(cursor):
    cursor.execute("SELECT id, name FROM Readers")
    print("\nСписок читателей:")
    if cursor.rowcount == 0:
        print("Список читателей пуст.")
    else:
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Имя: {row[1]}")

def add_book(cursor, conn):
    author = input("Введите автора: ")
    title = input("Введите название: ")
    try:
        year = int(input("Введите год издания: "))
    except ValueError:
        print("Некорректный год издания.")
        return
    cursor.execute("INSERT INTO Books (author, title, publish_year) VALUES (?, ?, ?)", (author, title, year))
    conn.commit()
    print("Книга добавлена.")

def add_reader(cursor, conn):
    name = input("Введите имя читателя: ")
    cursor.execute("INSERT INTO Readers (name) VALUES (?)", (name,))
    conn.commit()
    print("Читатель добавлен.")

def issue_book(cursor, conn):
    list_books(cursor)
    try:
        book_id = int(input("Введите ID книги: "))
        cursor.execute("SELECT * FROM Books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if book is None:
            raise ValueError("Книга с таким ID не найдена.")
    except ValueError as e:
        print(f"Ошибка: {e}")
        return

    list_readers(cursor)
    try:
        reader_id = int(input("Введите ID читателя: "))
        cursor.execute("SELECT * FROM Readers WHERE id = ?", (reader_id,))
        reader = cursor.fetchone()
        if reader is None:
            raise ValueError("Читатель с таким ID не найден.")

        cursor.execute("SELECT * FROM Records WHERE book_id = ? AND returning_date IS NULL", (book_id,))
        existing_record = cursor.fetchone()
        if existing_record:


            raise ValueError(f"Книга {book[2]} уже выдана.")
    except ValueError as e:
        print(f"Ошибка: {e}")
        return

    cursor.execute("INSERT INTO Records (reader_id, book_id, taking_date) VALUES (?, ?, ?)", (reader_id, book_id, datetime.date.today().strftime("%Y-%m-%d")))
    conn.commit()
    print("Книга выдана.")

def return_book(cursor, conn):
    cursor.execute("""
        SELECT rec.id, rec.reader_id, b.title, rec.taking_date FROM Records rec
        JOIN Books b ON rec.book_id = b.id WHERE rec.returning_date IS NULL;
    """)
    rows = cursor.fetchall()
    if not rows:
        print("Нет книг, взятых на данный момент.")
        return
    print("\nСписок взятых книг:")
    for i, row in enumerate(rows):
        print(f"{i+1}. ID записи: {row[0]}, Читатель ID: {row[1]}, Книга: {row[2]}, Дата выдачи: {row[3]}")

    try:
        record_id = int(input("Введите ID записи, которую нужно вернуть: ")) -1
        if record_id < 0 or record_id >= len(rows):
            raise ValueError("Некорректный ID записи.")
        cursor.execute(f"UPDATE Records SET returning_date = '{datetime.date.today().strftime('%Y-%m-%d')}' WHERE id = {rows[record_id][0]};")
        conn.commit()
        print("Книга принята.")
    except (ValueError, IndexError) as e:
        print(f"Ошибка: {e}")
    except sqlite3.Error as e:
        print(f"Ошибка SQL: {e}")


def custom_query(cursor):
    query = input("Введите SQL-запрос: ")
    try:
        cursor.execute(query)
        print("Результат запроса:")
        for row in cursor.fetchall():
            print(row)
    except sqlite3.Error as e:
        print(f"Ошибка SQL: {e}")


def main():
    conn, cursor = connect_db()
    if conn is None:
        return

    while True:
        print("\nМеню:")
        print("1. Вывести список книг")
        print("2. Вывести список читателей")
        print("3. Добавить книгу")
        print("4. Добавить читателя")
        print("5. Выдать книгу")
        print("6. Принять книгу")
        print("7. Произвольный запрос (SQL)")
        print("8. Выход")

        choice = input("Выберите пункт меню: ")

        if choice == '1':
            list_books(cursor)
        elif choice == '2':
            list_readers(cursor)
        elif choice == '3':
            add_book(cursor, conn)
        elif choice == '4':
            add_reader(cursor, conn)
        elif choice == '5':
            issue_book(cursor, conn)
        elif choice == '6':
            return_book(cursor, conn)
        elif choice == '7':
            custom_query(cursor)
        elif choice == '8':
            break
        else:
            print("Неверный выбор.")

    conn.close()

if __name__ == "__main__":
    main()