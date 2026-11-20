# Olive & Oak — Online Shopping Management System PRO

A complete local e-commerce college project with an olive-green responsive storefront, 100 seeded products, 5 categories, customer accounts, a smart cart, checkout, order history, an admin dashboard and a persistent SQLite database.

## Start the project (Windows)
1. Extract the complete ZIP folder.
2. Install Python 3.9 or newer if it is not already installed. No extra Python packages are needed.
3. Double-click `START_HERE_WINDOWS.bat`.
4. Your browser should open `http://localhost:8000`.
5. Keep the black terminal window open while using the website. Close it to stop the server.

Alternative: open a terminal in this folder and run `python server.py`, then visit `http://localhost:8000`.

## Start on macOS / Linux
Run `chmod +x START_HERE_MAC_LINUX.sh` once, then `./START_HERE_MAC_LINUX.sh`; open `http://localhost:8000` in your browser.

## Admin login
- Email: `admin@shopsphere.local`
- Password: `Admin@123`

Log in using Account, then choose Admin dashboard in the footer.

## Product catalogue — 100 products total
Each category contains 20 products:
1. Electronics
2. Fashion
3. Home & Kitchen
4. Beauty & Personal Care
5. Sports & Fitness

## Included features
### Customer storefront
- Olive-green responsive storefront and category navigation
- Search and sort by price / rating
- Product availability and stock display
- Wishlist saved in browser local storage
- Shopping cart with add, remove and quantity controls
- `OLIVE10` coupon for 10% off (discount capped at ₹500)
- Delivery fee calculation and estimated GST line
- Customer registration and login
- Checkout with server-side stock validation and stock deduction
- Order history for signed-in customers

### Admin dashboard
- Product, customer and order counts
- Total demo revenue
- Low-stock alerts and recent orders
- Add products and remove products from the catalogue

### Backend and database
- Python 3 standard-library HTTP server (no pip install needed)
- SQLite database included at `data/shop.db`
- Tables: `users`, `products`, `orders`, `order_items`
- Passwords stored as salted PBKDF2-HMAC-SHA256 hashes
- Database is persistent between runs; orders and stock changes are saved

## Project structure
```
Online_Shopping_Management_System_Pro/
├── server.py                  # Python API + server
├── static/
│   └── index.html             # Main website frontend
├── showcase.html              # Frontend-only visual preview
├── data/
│   ├── shop.db                # Pre-seeded SQLite database
│   └── README.txt
├── START_HERE_WINDOWS.bat    # Double-click launcher for Windows
├── START_HERE_MAC_LINUX.sh   # Launcher for macOS/Linux
├── VERIFY_PROJECT.py         # Database/package integrity check
├── requirements.txt
└── README.md
```

## Verify the included database
Run `python VERIFY_PROJECT.py` from this folder. It checks that the database contains the 100-product, 5-category catalogue and required tables.

## Showcase vs. full application
`showcase.html` is a standalone visual preview. For login, database, cart checkout, orders and admin features to work, start the backend and open `http://localhost:8000` (the server serves `static/index.html`). Opening the standalone HTML file directly does not start the backend.

## Important project limitations
This is an educational local demo, not a production-ready public store. No real payments are processed. Server sessions are held in memory and reset when the server stops. Cart and wishlist are stored in the browser. Before public deployment, implement HTTPS, expiring server-side sessions, CSRF protection, rate limiting, stronger production authorization, backups and a real payment provider.

Use fictional test customer information only.
