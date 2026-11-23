# Olive & Oak — Customer Shopping Website

A customer-focused online shopping demo built with a Python HTTP backend, SQLite database, and HTML/CSS/JavaScript frontend. The admin dashboard and admin demo account have been removed.

## Customer features
- 5 categories and 100 products (20 per category)
- Product search, category filtering, price/rating sorting
- Shopping cart with quantity controls
- Wishlist saved in the browser
- Coupon code `OLIVE10` (10% off, capped at ₹500)
- Customer registration, login and logout
- Customer order history
- Checkout with server-side stock validation and SQLite order storage
- Olive-green responsive design

## Run on Windows
1. Install Python 3.9 or newer.
2. Double-click `START_HERE_WINDOWS.bat`.
3. Open http://localhost:8000 in your browser.

Or open a terminal in this folder and run:
```bash
python server.py
```

## Important: Vercel deployment
The screenshot shows the frontend running on Vercel, but the account form calls `/api/register` and `/api/login`. The Python server in this project is a separate local server; uploading only the HTML to Vercel does not deploy those API routes or the SQLite database. That is why the browser receives a non-JSON server response and displays a JSON parsing error.

For working accounts on a public Vercel URL, deploy a Python API backend and connect it to a persistent hosted database (for example PostgreSQL). A SQLite file stored inside a serverless deployment is not a reliable persistent database. This ZIP runs fully as a local Python + SQLite app. The updated frontend now displays a clear backend-not-deployed message instead of the confusing JSON parser error.

## Notes
- Demo checkout does not process real payments.
- Passwords are stored as PBKDF2 hashes.
- Sessions are held in server memory and reset when the server restarts.
- Cart and wishlist are stored in browser local storage.
- This is an educational demo, not a production payment system.
