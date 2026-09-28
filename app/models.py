"""ORM models. Tables and columns mirror smartstockdatabase.sql exactly;
users, purchase_orders and activity_log are additions the dump does not contain."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from .database import Base

Money = Numeric(10, 2, asdecimal=False)


class Store(Base):  # the tenant
    __tablename__ = "stores"
    store_id = Column(Integer, primary_key=True)
    store_name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    category_name = Column(String(100), nullable=False)


class Supplier(Base):
    __tablename__ = "suppliers"
    supplier_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    supplier_name = Column(String(100), nullable=False)
    category = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    total_orders = Column(Integer, default=0)


class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    sku = Column(String(50), nullable=False)
    product_name = Column(String(150), nullable=False)
    selling_price = Column(Money, nullable=False)
    cost_price = Column(Money, nullable=False)
    current_stock = Column(Integer, default=0, nullable=False)
    reorder_threshold = Column(Integer, default=5, nullable=False)
    category = relationship("Category")
    supplier = relationship("Supplier")


class Sale(Base):
    __tablename__ = "sales"
    sale_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    sale_time = Column(DateTime, default=datetime.utcnow)
    total_revenue = Column(Money, nullable=False)
    total_profit = Column(Money, nullable=False)
    items = relationship("SaleItem", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"
    sale_item_id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Money, nullable=False)
    unit_cost = Column(Money, nullable=False)


class StockMovement(Base):
    __tablename__ = "stock_movements"
    movement_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # sale | restock | opening
    quantity = Column(Integer, nullable=False)  # signed: sales negative, restocks positive
    movement_time = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)


# ---- additions (not in the dump) ----

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    store = relationship("Store")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    po_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="ordered")  # ordered | received
    auto_generated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    received_at = Column(DateTime)
    product = relationship("Product")


class ActivityLog(Base):  # feeds the live procurement terminal
    __tablename__ = "activity_log"
    log_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False, index=True)
    level = Column(String(10), default="info")  # info | sale | po
    message = Column(String(300), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
