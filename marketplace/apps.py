"""Application configuration for the Marketplace app."""

from django.apps import AppConfig
from django.db.models.signals import post_migrate


def setup_group_permissions(sender, **kwargs):
    """Assign model permissions to Vendors and Buyers groups."""
    from django.contrib.auth.models import (
        Group,
        Permission,
    )
    from django.contrib.contenttypes.models import (
        ContentType,
    )

    Product = sender.get_model("Product")
    Store = sender.get_model("Store")
    if Product is None or Store is None:
        return

    product_ct = ContentType.objects.get_for_model(Product)
    store_ct = ContentType.objects.get_for_model(Store)

    vendor_group, _ = Group.objects.get_or_create(
        name="Vendors"
    )
    vendor_perms = [
        Permission.objects.get(
            content_type=product_ct, codename="add_product"
        ),
        Permission.objects.get(
            content_type=product_ct, codename="change_product"
        ),
        Permission.objects.get(
            content_type=product_ct, codename="delete_product"
        ),
        Permission.objects.get(
            content_type=product_ct, codename="view_product"
        ),
        Permission.objects.get(
            content_type=store_ct, codename="add_store"
        ),
        Permission.objects.get(
            content_type=store_ct, codename="change_store"
        ),
        Permission.objects.get(
            content_type=store_ct, codename="delete_store"
        ),
        Permission.objects.get(
            content_type=store_ct, codename="view_store"
        ),
    ]
    vendor_group.permissions.add(*vendor_perms)

    buyer_group, _ = Group.objects.get_or_create(
        name="Buyers"
    )
    buyer_perms = [
        Permission.objects.get(
            content_type=product_ct, codename="view_product"
        ),
        Permission.objects.get(
            content_type=store_ct, codename="view_store"
        ),
    ]
    Order = sender.get_model("Order")
    OrderItem = sender.get_model("OrderItem")
    ProductReview = sender.get_model("ProductReview")
    if Order is not None:
        order_ct = ContentType.objects.get_for_model(Order)
        for code in ("add_order", "view_order"):
            buyer_perms.append(
                Permission.objects.get(
                    content_type=order_ct, codename=code
                )
            )
    if OrderItem is not None:
        item_ct = ContentType.objects.get_for_model(OrderItem)
        buyer_perms.append(
            Permission.objects.get(
                content_type=item_ct, codename="view_orderitem"
            )
        )
    if ProductReview is not None:
        rev_ct = ContentType.objects.get_for_model(
            ProductReview
        )
        for code in ("add_productreview", "view_productreview"):
            buyer_perms.append(
                Permission.objects.get(
                    content_type=rev_ct, codename=code
                )
            )
    buyer_group.permissions.add(*buyer_perms)


class MarketplaceConfig(AppConfig):
    """Configuration class for the marketplace application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "marketplace"

    def ready(self):
        """Connect post_migrate signal for group permissions."""
        post_migrate.connect(
            setup_group_permissions, sender=self
        )
