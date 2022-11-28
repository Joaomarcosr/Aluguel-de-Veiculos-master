from flask import jsonify

from src.coupons.response_dto import ResponseDto
from src.shared.models import Coupon


class CouponsController:

    @staticmethod
    def get_coupons():
        coupons = Coupon.query.all()
        return jsonify([ResponseDto.to_listing(p) for p in coupons])
