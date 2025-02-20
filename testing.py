from flask import Flask, request, jsonify, abort
import sqlite3

app = Flask(__name__)
DATABASE = 'books.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publication_year INTEGER NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def home():
    return jsonify({'message': "Please Visit '/books' to get all the api you need as per your requirement"}), 200


@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    publication_year = data.get('publication_year')

    if not title or not author or not isinstance(publication_year, int):
        return jsonify({'error': 'Invalid input'}), 400

    with get_db_connection() as conn:
        cursor = conn.execute(
            'INSERT INTO books (title, author, publication_year) VALUES (?, ?, ?)',
            (title, author, publication_year)
        )
        conn.commit()
        book_id = cursor.lastrowid

    return jsonify({'id': book_id, 'title': title, 'author': author, 'publication_year': publication_year}), 201


@app.route('/books', methods=['GET'])
def list_books():
    with get_db_connection() as conn:
        books = conn.execute('SELECT * FROM books').fetchall()
    return jsonify([dict(book) for book in books]), 200


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    with get_db_connection() as conn:
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if book is None:
            abort(404, description="Book not found")
    return jsonify(dict(book)), 200


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    publication_year = data.get('publication_year')

    if not title or not author or not isinstance(publication_year, int):
        return jsonify({'error': 'Invalid input'}), 400

    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        if cursor.fetchone() is None:
            abort(404, description="Book not found")

        conn.execute(
            'UPDATE books SET title = ?, author = ?, publication_year = ? WHERE id = ?',
            (title, author, publication_year, book_id)
        )
        conn.commit()

    return jsonify({'id': book_id, 'title': title, 'author': author, 'publication_year': publication_year}), 200


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        if cursor.fetchone() is None:
            abort(404, description="Book not found")

        conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()

    return jsonify({'message': f'Book with ID {book_id} deleted successfully'}), 200


if __name__ == '__main__':
    init_db()
    app.run(debug=True)