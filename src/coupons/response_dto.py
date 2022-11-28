from src.shared.models import Coupon


class ResponseDto:

    @staticmethod
    def to_listing(coupon: Coupon):
        return {
            "code": coupon.code,
            "discount_percentage": coupon.discount_percentage,
            "is_valid": coupon.is_valid
        }
