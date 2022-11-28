import json
import unittest
import uuid

from app import app
from src.shared.global_db import GlobalDB
from src.shared.models import ShoppingCart, Product, ProductsInShoppingCart


class TestUpdateItem(unittest.TestCase):

    def test_should_update_item_in_shopping_cart(self):
        # PREPARE TEMP DATA
        tmp_cart = ShoppingCart(id=uuid.uuid4())
        GlobalDB.instance().db.session.add(tmp_cart)
        product_id = uuid.uuid4()
        product_name = "PRODUTO X"
        tmp_product = Product(id=product_id, name=product_name, stock=5, price=12.99)
        GlobalDB.instance().db.session.add(tmp_product)
        product_in_shopping_cart = ProductsInShoppingCart()
        product_in_shopping_cart.product_id = tmp_product.id
        product_in_shopping_cart.quantity = 1
        tmp_cart.products.append(product_in_shopping_cart)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().patch(
            f'/shoppingcarts/{tmp_cart.id}',
            data=json.dumps({'product_id': tmp_product.id, 'quantity': 3}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert len(data['items']) > 0
        assert data['items'][0]['product_id'] == str(product_id)
        assert data['items'][0]['name'] == product_name
        assert data['items'][0]['quantity'] == 3
        assert data['items'][0]['price'] == '12.99'
        assert data['items'][0]['subtotal'] == str(3 * 12.99)

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == data['id']).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == data['id']).delete()
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_return_404_if_update_item_from_not_exists_cart(self):
        response = app.test_client().patch(
            f'/shoppingcarts/{str(uuid.uuid4())}',
            data=json.dumps({'product_id': str(uuid.uuid4()), 'quantity': 3}),
            content_type='application/json'
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 404
        assert data['message'] == 'Carrinho não encontrado'

    def test_should_not_update_item_in_cart_with_stock_insufficient(self):
        # PREPARE TEMP DATA
        tmp_cart = ShoppingCart(id=uuid.uuid4())
        GlobalDB.instance().db.session.add(tmp_cart)
        tmp_product = Product(id=uuid.uuid4(), name="PRODUTO X", stock=5, price=7)
        GlobalDB.instance().db.session.add(tmp_product)
        product_in_shopping_cart = ProductsInShoppingCart()
        product_in_shopping_cart.product_id = tmp_product.id
        product_in_shopping_cart.quantity = 1
        tmp_cart.products.append(product_in_shopping_cart)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().patch(
            f'/shoppingcarts/{tmp_cart.id}',
            data=json.dumps({'product_id': tmp_product.id, 'quantity': 6}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 422
        assert data['message'] == f'Estoque não é suficiente para o produto: {tmp_product.id}'

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == tmp_cart.id).delete()
        GlobalDB.instance().db.session.delete(tmp_product)
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == tmp_cart.id).delete()
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_return_422_if_product_not_found_in_cart(self):
        # PREPARE TEMP DATA
        product_id = str(uuid.uuid4())
        tmp_cart = ShoppingCart(id=uuid.uuid4())
        GlobalDB.instance().db.session.add(tmp_cart)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().patch(
            f'/shoppingcarts/{tmp_cart.id}',
            data=json.dumps({'product_id': product_id, 'quantity': 6}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 422
        assert data['message'] == f'Produto de id {product_id} não foi encontrado no carrinho'

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == tmp_cart.id).delete()
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()

    def test_should_return_error_when_update_item_and_quantity_is_smaller_then_0(self):
        # PREPARE TEMP DATA
        tmp_cart = ShoppingCart()
        GlobalDB.instance().db.session.add(tmp_cart)
        GlobalDB.instance().db.session.commit()

        response = app.test_client().patch(
            f'/shoppingcarts/{tmp_cart.id}',
            data=json.dumps({'product_id': str(uuid.uuid4()), 'quantity': 0}),
            content_type='application/json',
        )

        data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 422
        assert data['message'] == f'Quantidade deve ser maior que zero'

        # CLEAR TESTS DB
        GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == tmp_cart.id).delete()
        GlobalDB.instance().db.session.commit()
        GlobalDB.instance().db.session.close()
