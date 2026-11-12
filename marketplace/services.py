from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, EmailQueue, Product


def process_checkout(buyer, cart_data):
    """
    Executes transaction with atomic locks to handle inventory deduction safely
    and enqueue background receipts.
    """
    with transaction.atomic():
        total = 0
        items_to_create = []

        # Lock products to prevent race conditions during checkout
        product_ids = [item['product_id'] for item in cart_data]
        products = Product.objects.select_for_update().filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        for item in cart_data:
            product = product_map.get(item['product_id'])
            qty = item['quantity']

            if not product or product.stock < qty or not product.is_published:
                raise ValueError(
                    f"Product {
                        product.title if product else ''} unavailable or out of stock.")

            product.stock -= qty
            product.save()

            line_total = product.price * qty
            total += line_total
            items_to_create.append((product, qty, product.price))

        order = Order.objects.create(buyer=buyer, total_amount=total)

        for product, qty, price in items_to_create:
            OrderItem.objects.create(
                order=order,
                product=product,
                store=product.store,
                quantity=qty,
                unit_price=price,
                item_status='PROCESSING'
            )

        # Enqueue Email Receipt (Failure Recovery Strategy)
        EmailQueue.objects.create(
            to_email=buyer.email,
            subject=f"Order Confirmation #{order.id}",
            message=f"Thank you for your purchase! Order total: ${order.total_amount}"
        )

    return order
