"""Transaction and checkout service utilities."""

from django.db import transaction

from .models import EmailQueue, Order, OrderItem, Product


class InsufficientStockError(Exception):
    """Raised when requested stock exceeds available quantity."""


def process_checkout(buyer, cart_data):
    """Execute atomic checkout and inventory deduction.

    Args:
        buyer: User completing the purchase.
        cart_data: Iterable of dicts with product_id and quantity.

    Returns:
        Order: Newly created order instance.
    """
    with transaction.atomic():
        total = 0
        items_to_create = []

        product_ids = [item["product_id"] for item in cart_data]
        products = (
            Product.objects.select_for_update()
            .select_related("store")
            .filter(id__in=product_ids)
        )
        product_map = {p.id: p for p in products}

        for item in cart_data:
            product = product_map.get(item["product_id"])
            qty = int(item["quantity"])

            if (
                not product
                or qty <= 0
                or product.stock < qty
                or not product.is_active
                or not product.is_published
            ):
                prod_name = product.name if product else ""
                raise InsufficientStockError(
                    f"Product {prod_name} unavailable or "
                    "out of stock."
                )

            product.stock -= qty
            product.save(update_fields=["stock"])

            line_total = product.base_price * qty
            total += line_total
            items_to_create.append(
                (product, qty, product.base_price)
            )

        order = Order.objects.create(
            user=buyer,
            total_amount=total,
            status="pending",
        )

        for product, qty, price in items_to_create:
            OrderItem.objects.create(
                order=order,
                product=product,
                store=product.store,
                quantity=qty,
                price=price,
                unit_price=price,
                item_status="PROCESSING",
            )

        if buyer.email:
            EmailQueue.objects.create(
                to_email=buyer.email,
                subject=f"Order Confirmation #{order.id}",
                message=(
                    f"Thank you for your purchase! "
                    f"Order total: R{order.total_amount}"
                ),
            )

    return order
