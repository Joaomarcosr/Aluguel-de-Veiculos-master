from src.shared.models import ShoppingCart


class ResponseDto:

    @staticmethod
    def to_creating(cart: ShoppingCart):
        return {"id": cart.id}

    @staticmethod
    def show_cart_with_items(cart: ShoppingCart):
        return {
            "id": cart.id,
            "items": cart.show_items(),
            "total": cart.total()
        }

    @staticmethod
    def show_complete_cart(cart: ShoppingCart):
        return {
            "id": cart.id,
            "items": cart.show_items(),
            "subtotal": cart.subtotal(),
            "discount": cart.discount(),
            "total": cart.total()
        }
