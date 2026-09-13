from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Book

Base.metadata.create_all(bind=engine)


class BookCreate(BaseModel):
    title: str
    author: str
    price: float
    category: str
    in_stock: bool = True
    published_year: int | None = None


class BookPatch(BaseModel):
    title: str | None = None
    author: str | None = None
    price: float | None = None
    category: str | None = None
    in_stock: bool | None = None
    published_year: int | None = None


class BookRead(BookCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get("/books", response_model=list[BookRead])
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()


@app.get("/books/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/categories", response_model=list[str])
def get_categories(db: Session = Depends(get_db)):
    return [category for (category,) in db.query(Book.category).distinct().all()]


@app.get("/categories/{category}", response_model=list[BookRead])
def get_books_by_category(category: str, db: Session = Depends(get_db)):
    return db.query(Book).filter(Book.category == category).all()


@app.put("/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in book.model_dump().items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.patch("/books/{book_id}", response_model=BookRead)
def update_book_partial(book_id: int, book: BookPatch, db: Session = Depends(get_db)):
    db_book = db.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}


#first version of the code,
# from fastapi import FastAPI, Query
# import sqlite3
# from pydantic import BaseModel

# class BookCreate(BaseModel):
#     title: str
#     author: str
#     price: float
#     category: str
#     in_stock: bool
#     published_year: int


# def get_db():
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     return conn, cursor

# conn, cursor = get_db()

# # Create the books table if it doesn't exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS books (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         title TEXT NOT NULL,
#         author TEXT NOT NULL,
#         price REAL NOT NULL,
#         category TEXT NOT NULL,
#         in_stock BOOLEAN NOT NULL DEFAULT 1,
#         published_year INTEGER 
#     )
# ''')
# conn.commit()
# conn.close()

# app = FastAPI()


# #Add a new book
# @app.post("/books")
# def create_book(book: BookCreate):
#     conn, cursor = get_db()
#     cursor.execute('''
#         INSERT INTO books (title, author, price, category, in_stock, published_year)
#         VALUES (?, ?, ?, ?, ?, ?)
#     ''', (book.title, book.author, book.price, book.category, book.in_stock, book.published_year))
#     conn.commit()
#     conn.close()
#     return {"message": "Book added successfully"}

# #Get all books
# @app.get("/books")
# def get_books(
#     category: str | None = None,
#     published_after: int | None = None,
#     max_price: float | None = None,
#     sort_by: str = Query("id", pattern="^(id|title|author|price|category|in_stock|published_year)$"),
#     limit: int = Query(100, ge=1, le=1000),
#     skip: int = Query(0, ge=0),
# ):
#     conn, cursor = get_db()
#     filters = [
#         ('category = ?', category),
#         ('published_year > ?', published_after),
#         ('price <= ?', max_price),
#     ]
#     conditions = [condition for condition, value in filters if value is not None]
#     params = [value for _, value in filters if value is not None]
#     query = 'SELECT * FROM books'
#     if conditions:
#         query += ' WHERE ' + ' AND '.join(conditions)
#     query += f' ORDER BY {sort_by} LIMIT ? OFFSET ?'
#     params += [limit, skip]
#     cursor.execute(query, params)
#     books = cursor.fetchall()
#     conn.close()
#     return {"books": books}

# #Get book by ID
# @app.get("/books/{book_id}")
# def get_book(book_id: int):
#     conn, cursor = get_db()
#     cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
#     book = cursor.fetchone()
#     conn.close()
#     if book:
#         return {"book": book}
#     else:
#         return {"message": "Book not found"}

# #List all categories
# @app.get("/categories")
# def get_categories():
#     conn, cursor = get_db()
#     cursor.execute('SELECT DISTINCT category FROM books')
#     categories = [row[0] for row in cursor.fetchall()]
#     conn.close()
#     return {"categories": categories}

# #Get books by category
# @app.get("/categories/{category}/books")
# def get_books_by_category(category: str):
#     conn, cursor = get_db()
#     cursor.execute('SELECT * FROM books WHERE category = ?', (category,))
#     books = cursor.fetchall()
#     conn.close()
#     return {"books": books}

# #Update entire book by ID
# @app.put("/books/{book_id}")
# def update_book(book_id: int, book: BookCreate):
#     conn, cursor = get_db()
#     cursor.execute('''
#         UPDATE books
#         SET title = ?, author = ?, price = ?, category = ?, in_stock = ?, published_year = ?
#         WHERE id = ?
#     ''', (book.title, book.author, book.price, book.category, book.in_stock, book.published_year, book_id))
#     conn.commit()
#     conn.close()
#     return {"message": "Book updated successfully"}

# #Update specfic fields of a book by ID
# @app.patch("/books/{book_id}")

# #Delete book by ID
# @app.delete("/books/{book_id}")
# def delete_book(book_id: int):
#     conn, cursor = get_db()
#     cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
#     conn.commit()
#     conn.close()
#     return {"message": "Book deleted successfully"}