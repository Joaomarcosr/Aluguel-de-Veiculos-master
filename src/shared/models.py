import decimal
import uuid

from flask_sqlalchemy import SQLAlchemy

from src.shared.global_db import GlobalDB

db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.String, unique=True, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Numeric(10, 2), nullable=False)


class ShoppingCart(db.Model):
    id = db.Column(db.String, unique=True, primary_key=True, default=uuid.uuid4)
    products = db.relationship('ProductsInShoppingCart', back_populates='shopping_cart')
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'), nullable=True)

    def show_items(self):
        items = []
        for p in self.products:
            product = GlobalDB.instance().db.session.query(Product) \
                .filter(Product.id == p.product_id).first()
            items.append(
                {
                    "product_id": p.product_id,
                    "name": product.name,
                    "quantity": p.quantity,
                    "price": product.price,
                    "subtotal": decimal.Decimal(
                        product.price * decimal.Decimal(p.quantity)
                    ).quantize(decimal.Decimal('0.01'))
                }
            )
        return items

    def subtotal(self):
        total = decimal.Decimal(0)
        for i in self.show_items():
            total += i['subtotal']
        return total

    def discount(self):
        if self.coupon_id is not None:
            coupon = GlobalDB.instance().db.session.query(Coupon).\
                filter(Coupon.id == self.coupon_id).first()
            return ((coupon.discount_percentage * self.subtotal()) / decimal.Decimal(100)).\
                quantize(decimal.Decimal('0.01'))
        return '0'

    def total(self):
        total = decimal.Decimal(0)
        for i in self.show_items():
            total += i['subtotal']
        total -= decimal.Decimal(self.discount())
        return total.quantize(decimal.Decimal('0.01'))


class ProductsInShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product_id = db.Column('product_id', db.String, db.ForeignKey('product.id'))
    shopping_cart_id = db.Column('shopping_cart_id', db.String, db.ForeignKey('shopping_cart.id'))
    product = db.relationship("Product")
    shopping_cart = db.relationship("ShoppingCart", back_populates="products")


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), nullable=False)
    discount_percentage = db.Column(db.Numeric(10, 2), nullable=False)
    is_valid = db.Column(db.Boolean, default=False, nullable=False)
