from flask import make_response, jsonify

from src.shared.global_db import GlobalDB
from src.shared.models import Product, ShoppingCart, ProductsInShoppingCart, Coupon
from src.shopping_carts.response_dto import ResponseDto


class ShoppingCartsController:

    @staticmethod
    def create(data):
        if data.get('items') is None:
            return make_response(jsonify({
                'message': 'Deve informar uma lista de items'
            }), 422)

        items = data['items']
        new_shopping_cart = ShoppingCart()
        try:
            for i in items:
                product = GlobalDB.instance().db.session.query(Product) \
                    .filter(Product.id == i['product_id']).first()
                if product is not None:
                    if product.stock < i['quantity']:
                        return make_response(jsonify({
                            'message': f'Estoque não é suficiente para o produto: {product.id}'
                        }), 422)

                    product_in_shopping_cart = ProductsInShoppingCart()
                    product_in_shopping_cart.product_id = product.id
                    product_in_shopping_cart.quantity = i['quantity']
                    new_shopping_cart.products.append(product_in_shopping_cart)
            GlobalDB.instance().db.session.add(new_shopping_cart)
            GlobalDB.instance().db.session.commit()
            return make_response(jsonify(ResponseDto.to_creating(new_shopping_cart)), 201)
        except KeyError as k:
            return make_response(jsonify({
                'message': f'Atributo: {k.args[0]} não informado. Verifique se o item contem product_id e quantity'
            }), 422)

    @staticmethod
    def add_item(cart_id, data):
        product_id = data['product_id']
        quantity = data['quantity']
        if quantity <= 0:
            return make_response(jsonify({
                'message': f'Quantidade deve ser maior que zero'
            }), 422)

        cart = GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == cart_id).first()
        if cart is None:
            return make_response(jsonify({'message': 'Carrinho não encontrado'}), 404)

        product = GlobalDB.instance().db.session.query(Product) \
            .filter(Product.id == product_id).first()
        if product is None:
            return make_response(jsonify({
                'message': f'Não foi encontrado o produto com id: {product_id}'
            }), 422)

        product_already_exists = GlobalDB.instance().db.session.query(ProductsInShoppingCart). \
            filter(ProductsInShoppingCart.product_id == product_id,
                   ProductsInShoppingCart.shopping_cart_id == cart_id).first()
        quantity_wanted = quantity if product_already_exists is None else quantity + product_already_exists.quantity
        if product.stock < quantity_wanted:
            return make_response(jsonify({
                'message': f'Estoque não é suficiente para o produto: {product.id}'
            }), 422)
        if product_already_exists is not None:
            product_already_exists.quantity += quantity
        else:
            product_in_shopping_cart = ProductsInShoppingCart()
            product_in_shopping_cart.product_id = product.id
            product_in_shopping_cart.quantity = quantity
            cart.products.append(product_in_shopping_cart)
            GlobalDB.instance().db.session.add(cart)
        GlobalDB.instance().db.session.commit()
        return make_response(jsonify(ResponseDto.show_cart_with_items(cart)), 200)

    @staticmethod
    def remove_item(cart_id, product_id):
        cart = GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == cart_id).first()
        if cart is None:
            return make_response(jsonify({'message': 'Carrinho não encontrado'}), 404)

        product_exists = GlobalDB.instance().db.session.query(ProductsInShoppingCart). \
            filter(ProductsInShoppingCart.product_id == product_id,
                   ProductsInShoppingCart.shopping_cart_id == cart_id).first()
        if product_exists is None:
            return make_response(jsonify({
                'message': f'Produto de id {product_id} não foi encontrado no carrinho'
            }), 422)

        GlobalDB.instance().db.session.delete(product_exists)
        GlobalDB.instance().db.session.add(cart)
        GlobalDB.instance().db.session.commit()
        return make_response(jsonify(ResponseDto.show_cart_with_items(cart)), 200)

    @staticmethod
    def update_item(cart_id, data):
        product_id = data['product_id']
        quantity = data['quantity']
        if quantity <= 0:
            return make_response(jsonify({
                'message': f'Quantidade deve ser maior que zero'
            }), 422)

        cart = GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == cart_id).first()
        if cart is None:
            return make_response(jsonify({'message': 'Carrinho não encontrado'}), 404)

        product_in_cart = GlobalDB.instance().db.session.query(ProductsInShoppingCart). \
            filter(ProductsInShoppingCart.product_id == product_id,
                   ProductsInShoppingCart.shopping_cart_id == cart_id).first()
        if product_in_cart is None:
            return make_response(jsonify({
                'message': f'Produto de id {product_id} não foi encontrado no carrinho'
            }), 422)

        product = GlobalDB.instance().db.session.query(Product) \
            .filter(Product.id == product_id).first()
        if product.stock < quantity:
            return make_response(jsonify({
                'message': f'Estoque não é suficiente para o produto: {product.id}'
            }), 422)

        product_in_cart.quantity = quantity
        GlobalDB.instance().db.session.commit()
        return make_response(jsonify(ResponseDto.show_cart_with_items(cart)), 200)

    @staticmethod
    def clear_cart(cart_id):
        cart = GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == cart_id).first()
        if cart is None:
            return make_response(jsonify({'message': 'Carrinho não encontrado'}), 404)

        GlobalDB.instance().db.session.query(ProductsInShoppingCart) \
            .filter(ProductsInShoppingCart.shopping_cart_id == cart_id).delete()
        GlobalDB.instance().db.session.commit()
        return make_response(jsonify(ResponseDto.show_cart_with_items(cart)), 200)

    @staticmethod
    def show_cart(cart_id):
        cart = GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == cart_id).first()
        if cart is None:
            return make_response(jsonify({'message': 'Carrinho não encontrado'}), 404)

        return make_response(jsonify(ResponseDto.show_complete_cart(cart)), 200)

    @staticmethod
    def add_coupon(cart_id, data):
        cart = GlobalDB.instance().db.session.query(ShoppingCart) \
            .filter(ShoppingCart.id == cart_id).first()
        if cart is None:
            return make_response(jsonify({'message': 'Carrinho não encontrado'}), 404)

        coupon = GlobalDB.instance().db.session.query(Coupon) \
            .filter(Coupon.code == data['code']).first()
        if coupon is None:
            return make_response(jsonify({'message': 'Cupom não encontrado'}), 404)

        if not coupon.is_valid:
            return make_response(jsonify({'message': 'Cupom inválido'}), 422)

        cart.coupon_id = coupon.id
        GlobalDB.instance().db.session.commit()

        return make_response(jsonify({}), 200)
