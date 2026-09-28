import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from . import __version__, auth, demo, importer, ml_engine, models, schemas
from .database import Base, SessionLocal, engine, get_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://ismartstockapp.netlify.app",  # <--- PASTE YOUR NETLIFY URL HERE
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LEAD_DAYS = int(os.getenv("SMARTSTOCK_LEAD_DAYS", "3"))  # the dump has no supplier lead time column


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # creates only what is missing (users, purchase_orders, activity_log, or all on SQLite)
    with SessionLocal() as db:
        importer.bootstrap(db)  # imports database/smartstockdatabase.sql on an empty database
    yield


app = FastAPI(title="SmartStock", version=__version__, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ---------- helpers ----------

def log(db: Session, store_id: int, message: str, level: str = "info"):
    db.add(models.ActivityLog(store_id=store_id, level=level, message=message))


def get_product(db: Session, user: models.User, product_id: int) -> models.Product:
    p = db.get(models.Product, product_id)
    if not p or p.store_id != user.store_id:
        raise HTTPException(404, "Product not found")
    return p


def check_owned(db: Session, model, pk, user: models.User, label: str):
    if pk is not None:
        row = db.get(model, pk)
        if not row or row.store_id != user.store_id:
            raise HTTPException(404, f"{label} not found")


def store_products(db: Session, store_id: int):
    return (db.query(models.Product).options(joinedload(models.Product.category))
            .filter_by(store_id=store_id).order_by(models.Product.product_name).all())


def sales_by_product(db: Session, store_id: int, only: int = None) -> dict:
    since = datetime.utcnow() - timedelta(days=ml_engine.HISTORY_DAYS + 1)
    q = (db.query(models.SaleItem.product_id, models.SaleItem.quantity, models.Sale.sale_time)
         .join(models.Sale, models.Sale.sale_id == models.SaleItem.sale_id)
         .filter(models.Sale.store_id == store_id, models.Sale.sale_time >= since))
    if only:
        q = q.filter(models.SaleItem.product_id == only)
    grouped = {}
    for pid, qty, when in q:
        grouped.setdefault(pid, []).append((qty, when))
    return grouped


def load_context(db: Session, store_id: int):
    suppliers = db.query(models.Supplier).filter_by(store_id=store_id).all()
    open_pos = {o.product_id: o for o in db.query(models.PurchaseOrder).filter_by(store_id=store_id, status="ordered")}
    return suppliers, open_pos


def resolve_supplier(p: models.Product, suppliers: list):
    """Explicit supplier first; otherwise the supplier whose category matches the product's category."""
    if p.supplier_id:
        return next((s for s in suppliers if s.supplier_id == p.supplier_id), None)
    if p.category:
        name = p.category.category_name.lower()
        return next((s for s in suppliers if s.category and s.category.lower() == name), None)
    return None


def product_view(p: models.Product, sales: dict, suppliers: list, open_pos: dict) -> dict:
    sup = resolve_supplier(p, suppliers)
    ev = ml_engine.evaluate(p.current_stock, ml_engine.daily_series(sales.get(p.product_id, [])), LEAD_DAYS, p.reorder_threshold)
    po = open_pos.get(p.product_id)
    return {"id": p.product_id, "name": p.product_name, "sku": p.sku,
            "category": p.category.category_name if p.category else None,
            "stock": p.current_stock, "price": p.selling_price, "cost": p.cost_price, "threshold": p.reorder_threshold,
            "supplier_id": p.supplier_id, "supplier": sup.supplier_name if sup else None,
            "open_po": {"id": po.po_id, "quantity": po.quantity} if po else None, **ev}


def place_order_if_needed(db: Session, p: models.Product, view: dict, suppliers: list, open_pos: dict):
    """Auto-procurement: raise a PO when the forecast says stock is critical and none is open."""
    if view["status"] != "critical" or p.product_id in open_pos:
        return None
    sup = resolve_supplier(p, suppliers)
    po = models.PurchaseOrder(store_id=p.store_id, product_id=p.product_id, quantity=view["suggested_qty"],
                              supplier_id=sup.supplier_id if sup else None)
    db.add(po)
    db.flush()
    if sup:
        sup.total_orders = (sup.total_orders or 0) + 1
    open_pos[p.product_id] = po
    log(db, p.store_id, f"PO #{po.po_id} raised: {po.quantity} x {p.product_name} from "
        f"{sup.supplier_name if sup else 'no supplier assigned'} (stock {p.current_stock}, reorder point {view['reorder_point']}).", "po")
    return po


def receive(db: Session, o: models.PurchaseOrder):
    o.status, o.received_at = "received", datetime.utcnow()
    o.product.current_stock += o.quantity
    db.add(models.StockMovement(product_id=o.product_id, movement_type="restock", quantity=o.quantity, notes=f"PO #{o.po_id} received"))
    log(db, o.store_id, f"PO #{o.po_id} received: {o.quantity} x {o.product.product_name} added to stock.", "po")


# ---------- auth ----------

@app.post("/api/auth/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(models.User).filter_by(email=email).first():
        raise HTTPException(409, "An account with this email already exists")
    store = models.Store(store_name=payload.store_name.strip(), email=email)
    db.add(store)
    db.flush()
    user = models.User(store_id=store.store_id, email=email, hashed_password=auth.hash_password(payload.password))
    db.add(user)
    log(db, store.store_id, "Store created. Add your first product to get started.")
    db.commit()
    return {"access_token": auth.create_access_token(user.user_id, store.store_id)}


@app.post("/api/auth/token", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=form.username.lower()).first()
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email or password is incorrect")
    return {"access_token": auth.create_access_token(user.user_id, user.store_id)}


@app.get("/api/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(auth.get_current_user)):
    return {"user_id": user.user_id, "email": user.email, "store_id": user.store_id, "store_name": user.store.store_name}


# ---------- catalogue ----------

@app.get("/api/categories")
def list_categories(user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    rows = db.query(models.Category).filter_by(store_id=user.store_id).order_by(models.Category.category_name).all()
    return [{"id": c.category_id, "name": c.category_name} for c in rows]


@app.get("/api/suppliers")
def list_suppliers(user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    rows = db.query(models.Supplier).filter_by(store_id=user.store_id).order_by(models.Supplier.supplier_name).all()
    return [{"id": s.supplier_id, "name": s.supplier_name, "category": s.category, "total_orders": s.total_orders} for s in rows]


@app.get("/api/products")
def list_products(user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    sales, (suppliers, open_pos) = sales_by_product(db, user.store_id), load_context(db, user.store_id)
    return [product_view(p, sales, suppliers, open_pos) for p in store_products(db, user.store_id)]


@app.post("/api/products", status_code=201)
def create_product(payload: schemas.ProductIn, user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    check_owned(db, models.Category, payload.category_id, user, "Category")
    check_owned(db, models.Supplier, payload.supplier_id, user, "Supplier")
    if db.query(models.Product).filter_by(store_id=user.store_id, sku=payload.sku).first():
        raise HTTPException(409, f"SKU {payload.sku} already exists")
    p = models.Product(store_id=user.store_id, **payload.model_dump())
    db.add(p)
    db.flush()
    if p.current_stock:
        db.add(models.StockMovement(product_id=p.product_id, movement_type="opening", quantity=p.current_stock, notes="Opening stock"))
    log(db, user.store_id, f"Product added: {p.product_name} ({p.sku}), {p.current_stock} in stock.")
    db.commit()
    suppliers, open_pos = load_context(db, user.store_id)
    return product_view(p, {}, suppliers, open_pos)


@app.patch("/api/products/{product_id}")
def patch_product(product_id: int, payload: schemas.ProductPatch, user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    p = get_product(db, user, product_id)
    data = payload.model_dump(exclude_unset=True)
    check_owned(db, models.Supplier, data.get("supplier_id"), user, "Supplier")
    for key, value in data.items():
        if key == "supplier_id" or value is not None:  # supplier_id may be cleared with null
            setattr(p, key, value)
    log(db, user.store_id, f"Updated {p.product_name}: {', '.join(data)}.")
    db.commit()
    suppliers, open_pos = load_context(db, user.store_id)
    return product_view(p, sales_by_product(db, user.store_id, p.product_id), suppliers, open_pos)


@app.get("/api/products/{product_id}/forecast")
def product_forecast(product_id: int, user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    p = get_product(db, user, product_id)
    series = ml_engine.daily_series(sales_by_product(db, user.store_id, p.product_id).get(p.product_id, []))
    today, days = datetime.utcnow().date(), ml_engine.HISTORY_DAYS
    return {"labels": [(today - timedelta(days=days - 1 - i)).strftime("%d %b") for i in range(days)],
            "history": series,
            "forecast_labels": [(today + timedelta(days=i + 1)).strftime("%d %b") for i in range(ml_engine.HORIZON_DAYS)],
            "forecast": ml_engine.forecast(series)}


# ---------- point of sale ----------

@app.post("/api/sales", status_code=201)
def create_sale(payload: schemas.SaleIn, user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    wanted = {}
    for line in payload.items:
        wanted[line.product_id] = wanted.get(line.product_id, 0) + line.quantity
    products = {}
    for pid, qty in wanted.items():
        p = get_product(db, user, pid)
        if p.current_stock < qty:
            raise HTTPException(400, f"Only {p.current_stock} of {p.product_name} left in stock")
        products[pid] = p
    items = [models.SaleItem(product_id=pid, quantity=q, unit_price=products[pid].selling_price,
                             unit_cost=products[pid].cost_price) for pid, q in wanted.items()]
    revenue = round(sum(i.quantity * i.unit_price for i in items), 2)
    profit = round(sum(i.quantity * (i.unit_price - i.unit_cost) for i in items), 2)
    sale = models.Sale(store_id=user.store_id, items=items, total_revenue=revenue, total_profit=profit)
    db.add(sale)
    db.flush()
    for pid, q in wanted.items():
        products[pid].current_stock -= q
        db.add(models.StockMovement(product_id=pid, movement_type="sale", quantity=-q, notes=f"Sale #{sale.sale_id}"))
    log(db, user.store_id, f"Sale #{sale.sale_id}: {sum(wanted.values())} unit(s) across {len(wanted)} product(s), Rs {revenue:,.2f}.", "sale")
    db.flush()
    suppliers, open_pos = load_context(db, user.store_id)
    raised = []
    for pid, p in products.items():
        view = product_view(p, sales_by_product(db, user.store_id, pid), suppliers, open_pos)
        po = place_order_if_needed(db, p, view, suppliers, open_pos)
        if po:
            raised.append(po.po_id)
    db.commit()
    return {"sale_id": sale.sale_id, "revenue": revenue, "profit": profit, "purchase_orders": raised}


# ---------- ML engine + procurement ----------

@app.post("/api/ml/run")
def run_engine(user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Re-forecast every product and raise purchase orders where needed."""
    sales, (suppliers, open_pos) = sales_by_product(db, user.store_id), load_context(db, user.store_id)
    created = 0
    for p in store_products(db, user.store_id):
        if place_order_if_needed(db, p, product_view(p, sales, suppliers, open_pos), suppliers, open_pos):
            created += 1
    log(db, user.store_id, f"Forecast run complete. {created} purchase order(s) raised.")
    db.commit()
    return {"orders_created": created}


@app.get("/api/purchase-orders")
def list_orders(user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    rows = db.query(models.PurchaseOrder).filter_by(store_id=user.store_id).order_by(models.PurchaseOrder.po_id.desc()).all()
    return [{"id": o.po_id, "product": o.product.product_name, "quantity": o.quantity, "status": o.status,
             "created_at": o.created_at.isoformat()} for o in rows]


@app.post("/api/purchase-orders/receive-all")
def receive_all(user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    orders = db.query(models.PurchaseOrder).filter_by(store_id=user.store_id, status="ordered").all()
    for o in orders:
        receive(db, o)
    db.commit()
    return {"received": len(orders)}


@app.post("/api/purchase-orders/{order_id}/receive")
def receive_order(order_id: int, user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    o = db.get(models.PurchaseOrder, order_id)
    if not o or o.store_id != user.store_id:
        raise HTTPException(404, "Purchase order not found")
    if o.status == "received":
        raise HTTPException(400, "Purchase order already received")
    receive(db, o)
    db.commit()
    return {"id": o.po_id, "status": o.status, "stock": o.product.current_stock}


# ---------- dashboard ----------

@app.get("/api/metrics")
def metrics(user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    revenue, profit, count = db.query(
        func.coalesce(func.sum(models.Sale.total_revenue), 0), func.coalesce(func.sum(models.Sale.total_profit), 0),
        func.count(models.Sale.sale_id)).filter(models.Sale.store_id == user.store_id).one()
    sales, (suppliers, open_pos) = sales_by_product(db, user.store_id), load_context(db, user.store_id)
    products = store_products(db, user.store_id)
    low = sum(1 for p in products if product_view(p, sales, suppliers, open_pos)["status"] == "critical")
    return {"revenue": round(revenue, 2), "gross_profit": round(profit, 2),
            "margin_pct": round(profit / revenue * 100, 1) if revenue else 0,
            "active_skus": len(products), "low_stock": low, "sales_count": count}


@app.get("/api/activity")
def activity(limit: int = 60, user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(models.ActivityLog).filter_by(store_id=user.store_id)
            .order_by(models.ActivityLog.log_id.desc()).limit(min(limit, 200)).all())
    return [{"id": r.log_id, "level": r.level, "message": r.message, "created_at": r.created_at.isoformat()} for r in reversed(rows)]


@app.post("/api/demo/history")
def demo_history(user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Generate 30 days of sample sales for a store that has none, so the forecaster has data."""
    if db.query(func.count(models.Sale.sale_id)).filter(models.Sale.store_id == user.store_id).scalar():
        raise HTTPException(409, "This store already has sales history")
    if not db.query(models.Product).filter_by(store_id=user.store_id).first():
        raise HTTPException(400, "Add at least one product first")
    made = demo.load_demo_history(db, user.store_id)
    log(db, user.store_id, f"Loaded {made} sample sales covering the last {ml_engine.HISTORY_DAYS} days.")
    db.commit()
    return {"sales_created": made}


@app.get("/api/health")
def health():
    return {"status": "ok", "version": __version__, "engine": f"ses alpha={ml_engine.ALPHA}", "database": engine.dialect.name}


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
