import decimal
import json
import unittest
import uuid

from app import app
from src.shared.global_db import GlobalDB
from src.shared.models import ShoppingCart, Product, ProductsInShoppingCart, Coupon


class TestAddCoupon(unittest.TestCase):

    def test_should_add_coupon_with_success(self):
        # PREPARE TEMP DATA
        cart_id = uuid.uuid4()
        tmp_cart = ShoppingCart(id=cart_id)
        GlobalDB.instance().db.session.add(tmp_cart)
        product_id = uuid.uuid4()
        tmp_product = Product(id=product_id, name="PRODUTO X", stock=5, price=17)
        GlobalDB.instance().db.session.add(tmp_product)
        product_in_shopping_cart = ProductsInShoppingCart()
        product_in_shopping_cart.product_id = tmp_product.id
        product_in_shopping_cart.quantity = 2
        tmp_cart.products.append(product_in_shopping_cart)
        coupon_code = str(uuid.uuid4())
        tmp_coupon = Coupon(code=coupon_code, discount_percentage=5, is_valid=True)
        GlobalDB.instance().db.session.add(tmp_coupon)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().post(
            f'/shoppingcarts/{tmp_cart.id}/add-coupon',
            data=json.dumps({'code': coupon_code}),
            content_type='application/json',
        )

        assert response.status_code == 200

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == str(cart_id)).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == str(cart_id)).delete()
        GlobalDB.instance().db.session.delete(tmp_coupon)
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_return_404_when_add_coupon_in_not_exists_cart(self):
        response = app.test_client().post(
            f'/shoppingcarts/{str(uuid.uuid4())}/add-coupon',
            data=json.dumps({'code': 'TESTCOUPON'}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 404
        assert data['message'] == 'Carrinho não encontrado'

    def test_should_return_404_when_add_not_exists_coupon(self):
        # PREPARE TEMP DATA
        cart_id = uuid.uuid4()
        tmp_cart = ShoppingCart(id=cart_id)
        GlobalDB.instance().db.session.add(tmp_cart)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().post(
            f'/shoppingcarts/{cart_id}/add-coupon',
            data=json.dumps({'code': 'GHOSTC'}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 404
        assert data['message'] == 'Cupom não encontrado'

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == str(cart_id)).delete()
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_not_add_coupon_invalid(self):
        # PREPARE TEMP DATA
        cart_id = uuid.uuid4()
        tmp_cart = ShoppingCart(id=cart_id)
        GlobalDB.instance().db.session.add(tmp_cart)
        product_id = uuid.uuid4()
        tmp_product = Product(id=product_id, name="PRODUTO X", stock=5, price=17)
        GlobalDB.instance().db.session.add(tmp_product)
        product_in_shopping_cart = ProductsInShoppingCart()
        product_in_shopping_cart.product_id = tmp_product.id
        product_in_shopping_cart.quantity = 2
        tmp_cart.products.append(product_in_shopping_cart)
        coupon_code = str(uuid.uuid4())
        tmp_coupon = Coupon(code=coupon_code, discount_percentage=5, is_valid=False)
        GlobalDB.instance().db.session.add(tmp_coupon)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().post(
            f'/shoppingcarts/{tmp_cart.id}/add-coupon',
            data=json.dumps({'code': coupon_code}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 422
        assert data['message'] == 'Cupom inválido'

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == str(cart_id)).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == str(cart_id)).delete()
        GlobalDB.instance().db.session.delete(tmp_coupon)
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()
