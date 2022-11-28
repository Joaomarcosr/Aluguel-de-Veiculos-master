import decimal
import json
import unittest
import uuid

from app import app
from src.shared.global_db import GlobalDB
from src.shared.models import ShoppingCart, ProductsInShoppingCart, Product, Coupon


class TestShowCart(unittest.TestCase):

    def test_show_cart_with_correct_values(self):
        # PREPARE TEMP DATA
        tmp_cart = ShoppingCart(id=uuid.uuid4())
        GlobalDB.instance().db.session.add(tmp_cart)
        product_id = uuid.uuid4()
        tmp_product = Product(id=product_id, name="PRODUTO X", stock=5, price=17)
        GlobalDB.instance().db.session.add(tmp_product)
        product_in_shopping_cart = ProductsInShoppingCart()
        product_in_shopping_cart.product_id = tmp_product.id
        product_in_shopping_cart.quantity = 2
        tmp_cart.products.append(product_in_shopping_cart)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().get(
            f'/shoppingcarts/{tmp_cart.id}',
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert len(data['items']) == 1
        assert data['id'] == tmp_cart.id
        assert data['items'][0]['product_id'] == str(product_id)
        assert data['items'][0]['name'] == 'PRODUTO X'
        assert data['items'][0]['quantity'] == 2
        assert data['items'][0]['price'] == '17.00'
        assert data['items'][0]['subtotal'] == \
               str(decimal.Decimal(2 * 17).quantize(decimal.Decimal('0.01')))

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == data['id']).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == data['id']).delete()
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_return_404_when_show_not_exists_cart(self):
        response = app.test_client().get(
            f'/shoppingcarts/{str(uuid.uuid4())}',
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 404
        assert data['message'] == 'Carrinho não encontrado'

    def test_show_cart_with_correct_total_value(self):
        # PREPARE TEMP DATA
        tmp_cart = ShoppingCart(id=uuid.uuid4())
        GlobalDB.instance().db.session.add(tmp_cart)
        product_id = uuid.uuid4()
        product2_id = uuid.uuid4()
        tmp_product = Product(id=product_id, name="PRODUTO X", stock=5, price=17)
        tmp_product2 = Product(id=product2_id, name="PRODUTO Y", stock=5, price=5.97)
        GlobalDB.instance().db.session.add(tmp_product)
        GlobalDB.instance().db.session.add(tmp_product2)
        product_in_shopping_cart = ProductsInShoppingCart()
        product_in_shopping_cart.product_id = tmp_product.id
        product_in_shopping_cart.quantity = 2
        tmp_cart.products.append(product_in_shopping_cart)
        product_in_shopping_cart2 = ProductsInShoppingCart()
        product_in_shopping_cart2.product_id = tmp_product2.id
        product_in_shopping_cart2.quantity = 3
        tmp_cart.products.append(product_in_shopping_cart2)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().get(
            f'/shoppingcarts/{tmp_cart.id}',
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert len(data['items']) == 2
        assert data['id'] == tmp_cart.id
        assert data['total'] == \
               str(decimal.Decimal((2 * 17) + (3 * 5.97)).quantize(decimal.Decimal('0.01')))

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == data['id']).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.delete(tmp_product2)
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == data['id']).delete()
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_show_cart_with_correct_total_value_with_coupon(self):
        # PREPARE TEMP DATA
        tmp_cart = ShoppingCart(id=uuid.uuid4())
        GlobalDB.instance().db.session.add(tmp_cart)
        product_id = uuid.uuid4()
        product2_id = uuid.uuid4()
        tmp_product = Product(id=product_id, name="PRODUTO X", stock=5, price=17)
        tmp_product2 = Product(id=product2_id, name="PRODUTO Y", stock=5, price=5.97)
        GlobalDB.instance().db.session.add(tmp_product)
        GlobalDB.instance().db.session.add(tmp_product2)
        product_in_shopping_cart = ProductsInShoppingCart()
        product_in_shopping_cart.product_id = tmp_product.id
        product_in_shopping_cart.quantity = 2
        tmp_cart.products.append(product_in_shopping_cart)
        product_in_shopping_cart2 = ProductsInShoppingCart()
        product_in_shopping_cart2.product_id = tmp_product2.id
        product_in_shopping_cart2.quantity = 3
        tmp_cart.products.append(product_in_shopping_cart2)
        coupon_code = str(uuid.uuid4())
        tmp_coupon = Coupon(code=coupon_code, discount_percentage=5, is_valid=False)
        GlobalDB.instance().db.session.add(tmp_coupon)
        GlobalDB.instance().db.session.commit()
        tmp_cart.coupon_id = tmp_coupon.id
        total = decimal.Decimal((2 * 17) + (3 * 5.97)).quantize(decimal.Decimal('0.01'))

        response = app.test_client().get(
            f'/shoppingcarts/{tmp_cart.id}',
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert len(data['items']) == 2
        assert data['id'] == tmp_cart.id
        assert data['subtotal'] == str(total)
        assert data['total'] == str((total - (total*5)/100).quantize(decimal.Decimal('0.01')))

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == data['id']).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.delete(tmp_product2)
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == data['id']).delete()
        GlobalDB.instance().db.session.delete(tmp_coupon)
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()
