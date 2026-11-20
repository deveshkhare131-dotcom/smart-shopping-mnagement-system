"""Quick integrity check for the ShopSphere SQLite project."""
from pathlib import Path
import sqlite3
ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "shop.db"
assert (ROOT / "server.py").is_file(), "server.py is missing"
assert (ROOT / "static" / "index.html").is_file(), "Frontend is missing"
assert DB.is_file(), "Database is missing; run python server.py once to create it"
con = sqlite3.connect(DB)
products = con.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0]
categories = con.execute("SELECT COUNT(DISTINCT category) FROM products WHERE active=1").fetchone()[0]
expected = {"users", "products", "orders", "order_items"}
tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
assert products >= 100, f"Expected at least 100 active products, found {products}"
assert categories == 5, f"Expected 5 categories, found {categories}"
assert expected.issubset(tables), f"Missing database tables: {expected - tables}"
print(f"OK: {products} products in {categories} categories; database tables: {', '.join(sorted(expected))}")
