import json
import unittest

from app import app
from src.shared.global_db import GlobalDB
from src.shared.models import Product, ProductsInShoppingCart, ShoppingCart


class TestCreateCart(unittest.TestCase):

    def test_should_create_shopping_cart_with_success(self):
        # PREPARE TEMP DATA
        tmp_product = Product(name="PRODUTO X", stock=5, price=12.99)
        GlobalDB.instance().db.session.add(tmp_product)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().post(
            '/shoppingcarts',
            data=json.dumps({
                'items': [
                    {'product_id': tmp_product.id, 'quantity': 3}
                ]
            }),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 201
        assert data['id'] is not None

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == data['id']).delete()
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == data['id']).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_return_error_with_stock_insufficient(self):
        # PREPARE TEMP DATA
        tmp_product = Product(name="PRODUTO X", stock=5, price=12.99)
        GlobalDB.instance().db.session.add(tmp_product)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().post(
            '/shoppingcarts',
            data=json.dumps({
                'items': [
                    {'product_id': tmp_product.id, 'quantity': 10}
                ]
            }),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 422
        assert data['message'] == f'Estoque não é suficiente para o produto: {tmp_product.id}'
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_return_error_without_items(self):
        response = app.test_client().post(
            '/shoppingcarts',
            data=json.dumps({}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 422
        assert data['message'] == f'Deve informar uma lista de items'

    def test_should_return_error_with_item_args_invalid(self):
        response = app.test_client().post(
            '/shoppingcarts',
            data=json.dumps({
                'items': [
                    {'fake': '123', 'quantity': 10}
                ]
            }),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 422
        assert data['message'] == 'Atributo: product_id não informado. ' \
                                  'Verifique se o item contem product_id e quantity'
