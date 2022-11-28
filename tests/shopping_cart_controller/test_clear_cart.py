import json
import unittest
import uuid

from app import app
from src.shared.global_db import GlobalDB
from src.shared.models import ShoppingCart, Product, ProductsInShoppingCart


class TestClearCart(unittest.TestCase):

    def test_should_clear_cart(self):
        # PREPARE TEMP DATA
        tmp_cart = ShoppingCart(id=uuid.uuid4())
        GlobalDB.instance().db.session.add(tmp_cart)
        tmp_product = Product(id=uuid.uuid4(), name="PRODUTO X", stock=5, price=12.99)
        GlobalDB.instance().db.session.add(tmp_product)
        product_in_shopping_cart = ProductsInShoppingCart()
        product_in_shopping_cart.product_id = tmp_product.id
        product_in_shopping_cart.quantity = 1
        tmp_cart.products.append(product_in_shopping_cart)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().post(
            f'/shoppingcarts/{tmp_cart.id}/clear',
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert len(data['items']) == 0

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == data['id']).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == data['id']).delete()
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_return_404_when_clear_not_exists_cart(self):
        response = app.test_client().post(
            f'/shoppingcarts/{str(uuid.uuid4())}/clear',
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 404
        assert data['message'] == 'Carrinho não encontrado'
