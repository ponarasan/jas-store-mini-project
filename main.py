from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, SessionLocal

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
def home():
    return {"message": "Welcome to JAS Store API"}


@app.get("/products", response_model=list[schemas.ProductResponse])
def get_products(db: db_dependency):
    return db.query(models.Product).all()


@app.get("/products/{product_id}",
         response_model=schemas.ProductResponse)
def get_product(product_id: int, db: db_dependency):

    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@app.post("/products",
          response_model=schemas.ProductResponse,
          status_code=201)
def create_product(
        product: schemas.ProductCreate,
        db: db_dependency):

    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.put("/products/{product_id}")
def update_product(
        product_id: int,
        updated_product: schemas.ProductCreate,
        db: db_dependency):

    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.name = updated_product.name
    product.description = updated_product.description
    product.price = updated_product.price
    product.stock = updated_product.stock

    db.commit()

    return {"message": "Product updated successfully"}


@app.delete("/products/{product_id}")
def delete_product(
        product_id: int,
        db: db_dependency):

    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}