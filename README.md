# SmartStock

Multi-tenant retail inventory SaaS with a monochrome dashboard and an exponential-smoothing reorder engine.

## Run

    pip install -r requirements.txt
    python run.py            # http://127.0.0.1:8000  (API docs at /docs)

On first start the app creates `smartstock.db` (SQLite), imports `database/smartstockdatabase.sql`, and creates a login
for the imported store:

    email:    admin@smartstock.com
    password: smartstock-demo        (change with SMARTSTOCK_ADMIN_PASSWORD before first run)

The imported store has no sales yet. Click **Load 30 days of sample sales** on the dashboard so the forecaster has history.

## PostgreSQL

    pip install psycopg2-binary
    export DATABASE_URL=postgresql+psycopg2://user:pass@localhost/smartstock   # an empty database
    python run.py

The importer loads the dump itself, so `psql` is not needed. If you would rather load it with `psql -f`, the dump needs
psql 17.6+ for the `\restrict` lines and PostgreSQL 17+ for `SET transaction_timeout`; the app then adds only its own tables.

## How the dump maps to the app

- Tables and columns are used as they are: stores, categories, suppliers, products, sales, sale_items, stock_movements.
- Added by the app: `users` (login per store), `purchase_orders`, `activity_log`.
- Every product in the dump has a NULL supplier. Purchase orders fall back to the supplier whose `category` matches the
  product's category (Groceries, Dairy). Other products show "No supplier" until you pick one in the table.
- Reorder point = the larger of the product's `reorder_threshold` and forecast daily demand x (lead time + 3 days).
  Lead time defaults to 3 days (`SMARTSTOCK_LEAD_DAYS`) because the dump has no lead-time column.
- A sale writes one `sales` row, one `sale_items` row per product and a negative `stock_movements` row. Receiving a
  purchase order adds a positive `restock` movement and raises stock.

## Settings

`DATABASE_URL`, `SMARTSTOCK_SECRET` (JWT signing key, set this in production), `SMARTSTOCK_ADMIN_PASSWORD`,
`SMARTSTOCK_LEAD_DAYS`, `HOST`, `PORT`, `RELOAD=1`.
"# smartstock" 
