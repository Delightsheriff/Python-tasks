from fastapi import FastAPI
import sqlite3

def get_db():
	conn = sqlite3.connect("database.db")
	cursor = conn.cursor()
	return conn, cursor

conn, cursor = get_db()

cursor.execute("""
	CREATE TABLE IF NOT EXISTS menu_items (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT UNIQUE NOT NULL,
		category TEXT NOT NULL,
		price REAL NOT NULL,
		vegetarian BOOLEAN NOT NULL
	)
""")

items = [
	("Garlic Bread", "appetizers", 6.00, True),
	("Caesar Salad", "appetizers", 8.00, True),
	("Chicken Wings", "appetizers", 10.00, False),
	("Mozzarella Sticks", "appetizers", 7.00, True),
	("Margherita Pizza", "main-courses", 14.00, True),
	("Grilled Chicken", "main-courses", 18.00, False),
	("Beef Burger", "main-courses", 16.00, False),
	("Vegetable Pasta", "main-courses", 15.00, True),
	("Grilled Salmon", "main-courses", 22.00, False),
	("Chocolate Cake", "desserts", 8.00, True),
	("Cheesecake", "desserts", 7.00, True),
	("Ice Cream", "desserts", 5.00, True),
]

cursor.executemany("""
	INSERT OR IGNORE INTO menu_items (name, category, price, vegetarian)
	VALUES (?, ?, ?, ?)
""", items)
conn.commit()
conn.close()



app = FastAPI()


@app.get("/menu")
def get_menu():
	return {"message": "Welcome to our restaurant menu!"}


@app.get("/appetizers")
def get_appetizers():
		conn, cursor = get_db()
		cursor.execute("SELECT name FROM menu_items WHERE category = ?", ("appetizers",))
		items = [row[0] for row in cursor.fetchall()]
		conn.close()
		return items


@app.get("/main-courses")
def get_main_courses():
		conn, cursor = get_db()
		cursor.execute("SELECT name FROM menu_items WHERE category = ?", ("main-courses",))
		items = [row[0] for row in cursor.fetchall()]
		conn.close()
		return items


@app.get("/desserts")
def get_desserts():
		conn, cursor = get_db()
		cursor.execute("SELECT name FROM menu_items WHERE category = ?", ("desserts",))
		items = [row[0] for row in cursor.fetchall()]
		conn.close()
		return items


@app.get("/item/{item_name}")
def get_item(item_name: str):
		conn, cursor = get_db()
		cursor.execute(
			"SELECT name, category, price, vegetarian FROM menu_items WHERE lower(name) = lower(?)",
			(item_name,),
		)
		item = cursor.fetchone()
		conn.close()
		if item is None:
			return {"error": "Item not found"}
		return {
			"name": item[0],
			"category": item[1],
			"price": f"${item[2]:.2f}",
			"vegetarian": bool(item[3]),
		}


@app.get("/category/{category_name}")
def get_category(category_name: str):
		conn, cursor = get_db()
		cursor.execute(
			"SELECT name FROM menu_items WHERE lower(category) = lower(?)",
			(category_name,),
		)
		items = [row[0] for row in cursor.fetchall()]
		conn.close()
		if not items:
			return {"error": "Category not found"}
		return items


@app.get("/price/{item_name}")
def get_price(item_name: str):
		conn, cursor = get_db()
		cursor.execute(
			"SELECT price FROM menu_items WHERE lower(name) = lower(?)",
			(item_name,),
		)
		item = cursor.fetchone()
		conn.close()
		if item is None:
			return {"error": "Item not found"}
		return f"${item[0]:.2f}"


@app.get("/vegetarian-options")
def get_vegetarian_options():
		conn, cursor = get_db()
		cursor.execute("SELECT name FROM menu_items WHERE vegetarian = 1")
		items = [row[0] for row in cursor.fetchall()]
		conn.close()
		return items


@app.get("/most-expensive")
def get_most_expensive():
		conn, cursor = get_db()
		cursor.execute(
			"SELECT name, category, price, vegetarian FROM menu_items ORDER BY price DESC LIMIT 1"
		)
		item = cursor.fetchone()
		conn.close()
		return {
			"name": item[0],
			"category": item[1],
			"price": f"${item[2]:.2f}",
			"vegetarian": bool(item[3]),
		}


@app.get("/total-items")
def get_total_items():
		conn, cursor = get_db()
		cursor.execute("SELECT category, COUNT(*) FROM menu_items GROUP BY category")
		counts = dict(cursor.fetchall())
		conn.close()
		return {
			"appetizers": counts.get("appetizers", 0),
			"main-courses": counts.get("main-courses", 0),
			"desserts": counts.get("desserts", 0),
			"total": sum(counts.values()),
		}
