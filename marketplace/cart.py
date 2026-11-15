"""
Session-based shopping cart implementation for the Marketplace application.
"""

from decimal import Decimal
from .models import Product


class Cart:
    """Manage session-based shopping cart items, quantities, and totals."""

    def __init__(self, request):
        """Initialize the shopping cart from the active HTTP session.

        Args:
            request (HttpRequest): The incoming request containing the session.
        """
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """Add a product to the cart or update its existing quantity.

        Args:
            product (Product): The product instance to add or update.
            quantity (int): Number of units to add or set. Defaults to 1.
            update_quantity (bool): If True, overwrite existing quantity
                instead of incrementing it. Defaults to False.
        """
        product_id = str(product.pk)
        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "price": str(product.base_price),
            }
        if update_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self):
        """Mark the HTTP session as modified to persist cart changes."""
        self.session.modified = True

    def remove(self, product):
        """Remove a specific product entry from the shopping cart.

        Args:
            product (Product): The product instance to remove.
        """
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Iterate over cart items and attach live Product instances.

        Yields:
            dict: Cart item dictionary with product, price, quantity,
                and total_price keys.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(pk__in=product_ids)
        cart_copy = self.cart.copy()
        for product in products:
            cart_copy[str(product.pk)]["product"] = product
        for item in cart_copy.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        """Calculate the total number of individual units in the cart.

        Returns:
            int: Total item quantity across all products in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        """Calculate the cumulative monetary total of all items in the cart.

        Returns:
            Decimal: Total cost of all items in the cart.
        """
        return sum(
            Decimal(item["price"]) * item["quantity"]
            for item in self.cart.values()
        )

    def clear(self):
        """Remove the shopping cart dictionary from the user session."""
        if "cart" in self.session:
            del self.session["cart"]
            self.save()
