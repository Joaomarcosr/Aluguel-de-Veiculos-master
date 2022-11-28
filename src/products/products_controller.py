from flask import jsonify, make_response

from src.products.response_dto import ResponseDto
from src.shared.global_db import GlobalDB
from src.shared.models import Product


class ProductsController:

    @staticmethod
    def get_product(product_id):
        product = GlobalDB.instance().db.session.query(Product) \
            .filter(Product.id == product_id).first()
        if product is not None:
            return jsonify(ResponseDto.to_getting(product))
        else:
            return make_response(jsonify({}), 404)

    @staticmethod
    def get_products():
        products = GlobalDB.instance().db.session.query(Product).all()
        return jsonify(products=[ResponseDto.to_listing(p) for p in products])
