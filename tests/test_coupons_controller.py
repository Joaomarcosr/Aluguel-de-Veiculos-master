import json

from app import app


def test_should_return_list_of_coupons():
    response = app.test_client().get(
        '/coupons',
        content_type='application/json',
    )

    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert type(data) is list
