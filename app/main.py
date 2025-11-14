# app/main.py
from typing import Optional

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import engine, SessionLocal
from app.models import Base, CustomerDB, OrderDb
from app.schemas import(
    CustomerCreate, CustomerRead, CustomerUpdate,
    OrderCreate, OrderRead
) 


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev/exam). Prefer Alembic in production.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

def commit_or_rollback(db: Session, error_msg:str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback
        raise HTTPException(status_code=409, detial=error_msg)


# ---- Health ----
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/customers", response_model=list[CustomerRead])
def list_customers(db: Session = Depends(get_db)):
    stmt = select(CustomerDB.order_by(CustomerDB.id))
    result = db.execute(stmt).scalers().all()

@app.get("/api/customers/{customer_id}", response_model = CustomerRead)
def get_customer(customer_id: int, db:Session = Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="User not found")
    return customer

@app.post("/api/customers", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def add_customer(payload: CustomerCreate, db: Session= Depends(get_db)):
    customer = CustomerDB(payload.model_dump())
    db.add(customer)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=490, details="Customer already Exists")
    return user

@app.put("/api/customers/{customer_id}", response_model = CustomerRead)
def replace_customer(customer_id: int, payload: CustomerCreate, db:Session = Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="User not found")

    customer.name = payload.name
    customer.email = payload.email
    customer.customer_since = payload.customer_since
    customer.customer_id = payload.customer_id

    try:
        db.commit()
        db.refresh()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail = "Customer update failed")
    return customer

@app.delete("/api/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)) -> Response:
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code = 404, detail = "Customer not found")
    db.delete_customer
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/api/customers/{customer_id}", response_model = CustomerRead)
def patch_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code = 404, detail = "Customer not found")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer,field,value)

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code = 409, detail = "Customer patch failed")
    return customer

@app.post("/api/orders", response_model = OrderRead, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    customer = db.get(CustomerDB, order.customer_id)
    if not customer:
        raise HTTPException(status_code = 404, detail = "Customer not found")

    ord = OrderDb(
        order_number = order.order_number,
        total_cents = order.total_cents,
        customer_id = order.customer_id
    )
    db.add(ord)
    commit_or_rollback(db, "Order Creation failed")
    db.refresh(ord)
    return ord

@app.get("api/orders", response_model = list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    stmt = select(OrderDb).order_by(OrderDb.id)
    return db.execute(stmt).scalars().all()

@app.get("api/orders/{order_id}", response_model = list[OrderRead])
def get_order(order_id: int, db: Session=Depends(get_db)):
    stmt = select(OrderDb).where(OrderDb.id == order_id).options(selectinload(OrderDb.customer))
    ord = db.execute(stmt).scalar_one_or_none()
    if not ord:
        raise HTTPException(status_code=404, detail="Order not found")
    return ord
    
