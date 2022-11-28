from flask import json

from app import app
from src.shared.global_db import GlobalDB
from src.shared.models import Product


def test_should_return_success_with_an_existing_product_id():
    tmp_product = Product(name="PRODUTO X", stock=5, price=12.99)
    GlobalDB.instance().db.session.add(tmp_product)
    GlobalDB.instance().db.session.commit()
    response = app.test_client().get(
        f'/products/{tmp_product.id}',
        content_type='application/json',
    )

    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data['id'] == tmp_product.id
    assert data['name'] == tmp_product.name
    assert data['stock'] == tmp_product.stock
    assert data['price'] == str(tmp_product.price)

    GlobalDB.instance().db.session.delete(tmp_product)
    GlobalDB.instance().db.session.commit()
    GlobalDB.instance().db.session.close()


def test_should_return_404_with_product_not_exists():
    response = app.test_client().get(
        f'/products/GHOST',
        content_type='application/json',
    )

    assert response.status_code == 404


def test_should_return_list_of_products():
    response = app.test_client().get(
        '/products',
        content_type='application/json',
    )

    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert type(data['products']) is list
