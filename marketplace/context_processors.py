"""Context processors for the Shopity Marketplace app."""

from .cart import Cart
from .models import Store


def cart_context(request):
    """Add the session shopping cart to template context."""
    return {"cart": Cart(request)}


def store_context(request):
    """Add vendor store info and role flags to context."""
    context = {
        "user_stores": Store.objects.none(),
        "user_store": None,
        "is_vendor": False,
    }
    if request.user.is_authenticated:
        stores = Store.objects.filter(
            owner=request.user
        ).order_by("id")
        context["user_stores"] = stores
        context["user_store"] = stores.first()
        context["is_vendor"] = (
            request.user.groups.filter(
                name="Vendors"
            ).exists()
            or request.user.is_staff
            or stores.exists()
        )
    return context
