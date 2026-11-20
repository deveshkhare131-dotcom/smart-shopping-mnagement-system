#!/usr/bin/env python3
"""Local e-commerce demo server backed by SQLite (Python standard library only)."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import sqlite3, json, hashlib, secrets, os, mimetypes, time

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "shop.db"
SESSIONS = {}
CATEGORIES = [
    ("Electronics", "⚡", "Gadgets, audio and everyday tech"),
    ("Fashion", "👕", "Clothing and accessories"),
    ("Home & Kitchen", "🏡", "Useful essentials for your home"),
    ("Beauty & Personal Care", "✨", "Daily care and grooming"),
    ("Sports & Fitness", "🏃", "Move, train and play"),
]
CAT_PRODUCTS = {
"Electronics": ["Wireless Headphones","Bluetooth Speaker","Smart Watch","USB-C Fast Charger","Power Bank 20000mAh","Mechanical Keyboard","Wireless Mouse","HD Webcam","Laptop Stand","USB-C Hub","Gaming Headset","Portable SSD 1TB","LED Desk Lamp","Smart LED Bulb","Phone Tripod","Fitness Band","Noise-Cancel Earbuds","HDMI Cable","Laptop Sleeve","Mini Projector"],
"Fashion": ["Classic Cotton T-Shirt","Casual Denim Jeans","Everyday Sneakers","Canvas Backpack","Slim Fit Shirt","Zip Hoodie","Summer Dress","Running Cap","Leather Wallet","Analog Watch","Sunglasses","Cotton Kurta","Formal Trousers","Sports Socks Pack","Crossbody Bag","Winter Jacket","Printed Scarf","Belt","Casual Sandals","Polo T-Shirt"],
"Home & Kitchen": ["Stainless Steel Bottle","Non-stick Frying Pan","Ceramic Dinner Set","Cotton Bedsheet","Storage Organizer","LED Night Light","Electric Kettle","Coffee Mug Set","Kitchen Knife Set","Wall Clock","Laundry Basket","Vacuum Flask","Food Storage Containers","Table Runner","Door Mat","Cushion Covers","Hand Blender","Water Dispenser","Desk Organizer","Bath Towel Set"],
"Beauty & Personal Care": ["Daily Face Cleanser","Hydrating Moisturizer","SPF 50 Sunscreen","Gentle Shampoo","Nourishing Conditioner","Body Lotion","Lip Balm","Face Serum","Hair Brush","Beard Grooming Kit","Hand Wash","Body Wash","Toothbrush Set","Nail Care Kit","Makeup Pouch","Aloe Vera Gel","Face Toner","Hair Oil","Travel Toiletry Kit","Bath Essentials Set"],
"Sports & Fitness": ["Yoga Mat","Adjustable Dumbbells","Resistance Bands","Stainless Shaker","Skipping Rope","Gym Gloves","Sports Water Bottle","Cricket Bat","Football","Badminton Racket","Tennis Ball Pack","Cycling Helmet","Running Belt","Foam Roller","Knee Support","Training T-Shirt","Fitness Tracker","Exercise Bench","Agility Ladder","Yoga Blocks"],
}
def db():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; return con
def pw_hash(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 180000).hex()
    return salt+"$"+digest
def verify(pw, stored):
    try:
        salt, digest=stored.split("$",1)
        return secrets.compare_digest(pw_hash(pw,salt).split("$",1)[1],digest)
    except Exception: return False
def init_db():
    DB.parent.mkdir(exist_ok=True)
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,is_admin INTEGER DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,category TEXT NOT NULL,description TEXT NOT NULL,price REAL NOT NULL,stock INTEGER NOT NULL,rating REAL NOT NULL,emoji TEXT NOT NULL,active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,total REAL NOT NULL,status TEXT DEFAULT 'Confirmed',created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS order_items(id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER NOT NULL,product_id INTEGER NOT NULL,name TEXT NOT NULL,price REAL NOT NULL,quantity INTEGER NOT NULL,FOREIGN KEY(order_id) REFERENCES orders(id));
        """)
        if not c.execute("SELECT 1 FROM users WHERE email='admin@shopsphere.local'").fetchone():
            c.execute("INSERT INTO users(name,email,password_hash,is_admin) VALUES(?,?,?,1)",("Shop Admin","admin@shopsphere.local",pw_hash("Admin@123")))
        if c.execute("SELECT COUNT(*) n FROM products").fetchone()["n"] == 0:
            emojis=["🎧","🔊","⌚","🔌","🔋","⌨️","🖱️","📷","💻","🔗","🎮","💾","💡","🌟","📱","⌚","🎵","🧵","👜","📽️"]
            for ci,(cat,names) in enumerate(CAT_PRODUCTS.items()):
                for i,name in enumerate(names):
                    price=round(249+((ci*317+i*173)%5200),2)
                    stock=0 if i in (8,17) and ci==2 else 8+(i*7+ci*3)%43
                    c.execute("INSERT INTO products(name,category,description,price,stock,rating,emoji) VALUES(?,?,?,?,?,?,?)",
                        (name,cat,f"{name} — quality pick from our {cat} collection. Practical, reliable and selected for everyday use.",price,stock,round(3.8+((i+ci)%12)/10,1),emojis[i%len(emojis)]))
        c.commit()
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def send_json(self,code,obj):
        data=json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","Content-Type, X-Session"); self.send_header("Access-Control-Allow-Methods","GET,POST,PUT,DELETE,OPTIONS"); self.end_headers(); self.wfile.write(data)
    def body(self):
        n=int(self.headers.get("Content-Length",0)); return json.loads(self.rfile.read(n) or b"{}")
    def user(self):
        token=self.headers.get("X-Session","")
        return SESSIONS.get(token)
    def require(self,admin=False):
        u=self.user()
        if not u: self.send_json(401,{"error":"Please log in first"}); return None
        if admin and not u["is_admin"]: self.send_json(403,{"error":"Admin access required"}); return None
        return u
    def do_OPTIONS(self): self.send_json(200,{"ok":True})
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ("/","/index.html"):
            p=ROOT/"static"/"index.html"; data=p.read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data); return
        if path=="/api/products":
            q=parse_qs(urlparse(self.path).query); cat=q.get("category",[""])[0]; search=q.get("q",[""])[0].lower()
            with db() as c:
                rows=c.execute("SELECT * FROM products WHERE active=1 AND (?='' OR category=?) AND (?='' OR lower(name) LIKE ?) ORDER BY category,name",(cat,cat,search,"%"+search+"%")).fetchall()
            self.send_json(200,{"products":[dict(x) for x in rows],"categories":[{"name":a,"emoji":b,"description":d} for a,b,d in CATEGORIES]}); return
        if path=="/api/me":
            u=self.user(); self.send_json(200,{"user":u}); return
        if path=="/api/orders":
            u=self.require()
            if not u:return
            with db() as c:
                orders=c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC",(u["id"],)).fetchall()
                out=[]
                for o in orders:
                    x=dict(o); x["items"]=[dict(i) for i in c.execute("SELECT name,price,quantity FROM order_items WHERE order_id=?",(o["id"],))]
                    out.append(x)
            self.send_json(200,{"orders":out}); return
        if path=="/api/admin/summary":
            u=self.require(True)
            if not u:return
            with db() as c:
                summary={"products":c.execute("SELECT COUNT(*) n FROM products WHERE active=1").fetchone()["n"],
                         "customers":c.execute("SELECT COUNT(*) n FROM users WHERE is_admin=0").fetchone()["n"],
                         "orders":c.execute("SELECT COUNT(*) n FROM orders").fetchone()["n"],
                         "revenue":c.execute("SELECT COALESCE(SUM(total),0) n FROM orders").fetchone()["n"],
                         "low_stock":[dict(x) for x in c.execute("SELECT id,name,stock,category FROM products WHERE stock<10 AND active=1 ORDER BY stock LIMIT 8")],
                         "recent":[dict(x) for x in c.execute("SELECT orders.id,users.name customer,total,status,orders.created_at FROM orders JOIN users ON users.id=orders.user_id ORDER BY orders.id DESC LIMIT 8")]}
            self.send_json(200,summary); return
        if path=="/api/admin/products":
            u=self.require(True)
            if not u:return
            with db() as c: rows=[dict(x) for x in c.execute("SELECT * FROM products WHERE active=1 ORDER BY id DESC")]
            self.send_json(200,{"products":rows}); return
        self.send_json(404,{"error":"Not found"})
    def do_POST(self):
        path=urlparse(self.path).path; b=self.body()
        if path=="/api/register":
            name=b.get("name","").strip(); email=b.get("email","").strip().lower(); pw=b.get("password","")
            if not name or "@" not in email or len(pw)<8: return self.send_json(400,{"error":"Enter a name, valid email and password of at least 8 characters"})
            try:
                with db() as c: cur=c.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",(name,email,pw_hash(pw))); uid=cur.lastrowid
            except sqlite3.IntegrityError: return self.send_json(409,{"error":"An account with this email already exists"})
            token=secrets.token_urlsafe(32); u={"id":uid,"name":name,"email":email,"is_admin":False}; SESSIONS[token]=u
            return self.send_json(201,{"token":token,"user":u})
        if path=="/api/login":
            email=b.get("email","").strip().lower(); pw=b.get("password","")
            with db() as c: row=c.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
            if not row or not verify(pw,row["password_hash"]): return self.send_json(401,{"error":"Incorrect email or password"})
            u={"id":row["id"],"name":row["name"],"email":row["email"],"is_admin":bool(row["is_admin"])}
            token=secrets.token_urlsafe(32); SESSIONS[token]=u
            return self.send_json(200,{"token":token,"user":u})
        if path=="/api/logout":
            SESSIONS.pop(self.headers.get("X-Session",""),None); return self.send_json(200,{"ok":True})
        if path=="/api/orders":
            u=self.require()
            if not u:return
            items=b.get("items",[])
            if not items:return self.send_json(400,{"error":"Your cart is empty"})
            try:
                with db() as c:
                    c.execute("BEGIN IMMEDIATE"); total=0; valid=[]
                    for it in items:
                        p=c.execute("SELECT * FROM products WHERE id=? AND active=1",(int(it["id"]),)).fetchone()
                        qty=int(it["quantity"])
                        if not p or qty<1 or p["stock"]<qty: raise ValueError("Some items are out of stock. Refresh your cart.")
                        total+=p["price"]*qty; valid.append((p,qty))
                    discount=min(float(b.get("discount",0)),total*0.25); total=round(total-discount,2)
                    cur=c.execute("INSERT INTO orders(user_id,total) VALUES(?,?)",(u["id"],total)); oid=cur.lastrowid
                    for p,qty in valid:
                        c.execute("UPDATE products SET stock=stock-? WHERE id=?",(qty,p["id"]))
                        c.execute("INSERT INTO order_items(order_id,product_id,name,price,quantity) VALUES(?,?,?,?,?)",(oid,p["id"],p["name"],p["price"],qty))
                    c.commit()
                return self.send_json(201,{"message":"Order placed successfully","order_id":oid,"total":total})
            except Exception as e:
                try:c.rollback()
                except:pass
                return self.send_json(400,{"error":str(e)})
        if path=="/api/admin/products":
            u=self.require(True)
            if not u:return
            try:
                with db() as c:
                    cur=c.execute("INSERT INTO products(name,category,description,price,stock,rating,emoji) VALUES(?,?,?,?,?,?,?)",
                        (b["name"],b["category"],b.get("description",""),float(b["price"]),int(b["stock"]),4.5,b.get("emoji","🛍️")))
                return self.send_json(201,{"id":cur.lastrowid})
            except Exception as e:return self.send_json(400,{"error":str(e)})
        self.send_json(404,{"error":"Not found"})
    def do_PUT(self):
        path=urlparse(self.path).path
        if path.startswith("/api/admin/products/"):
            u=self.require(True)
            if not u:return
            pid=path.rsplit("/",1)[-1]; b=self.body()
            try:
                with db() as c:c.execute("UPDATE products SET name=?,category=?,description=?,price=?,stock=? WHERE id=?",
                    (b["name"],b["category"],b.get("description",""),float(b["price"]),int(b["stock"]),pid))
                return self.send_json(200,{"ok":True})
            except Exception as e:return self.send_json(400,{"error":str(e)})
        self.send_json(404,{"error":"Not found"})
    def do_DELETE(self):
        path=urlparse(self.path).path
        if path.startswith("/api/admin/products/"):
            u=self.require(True)
            if not u:return
            pid=path.rsplit("/",1)[-1]
            with db() as c:c.execute("UPDATE products SET active=0 WHERE id=?",(pid,))
            return self.send_json(200,{"ok":True})
        self.send_json(404,{"error":"Not found"})

if __name__=="__main__":
    init_db()
    print("ShopSphere running at http://localhost:8000")
    print("Admin: admin@shopsphere.local / Admin@123")
    ThreadingHTTPServer(("127.0.0.1",8000),Handler).serve_forever()
