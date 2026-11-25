"""Administrative views for vendor approvals and moderation."""

from django.contrib.admin.views.decorators import (
    staff_member_required,
)
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .models import OrderItem, Product, Store


def _pending_stores_queryset():
    """Return pending stores if approval_status exists."""
    if hasattr(Store, "approval_status"):
        return Store.objects.filter(
            Q(approval_status__iexact="pending")
            | Q(approval_status__isnull=True)
            | Q(approval_status="")
        )
    return Store.objects.none()


@staff_member_required
@permission_required(
    "marketplace.change_store", raise_exception=True
)
def admin_vendor_list(request):
    """Display pending vendor stores for review and approval."""
    pending_stores = _pending_stores_queryset().select_related(
        "owner"
    )
    return render(
        request,
        "marketplace/admin_vendor_list.html",
        {"pending_stores": pending_stores},
    )


@staff_member_required
@permission_required(
    "marketplace.change_store", raise_exception=True
)
def admin_approve_vendor(request, store_id):
    """Approve a pending vendor store application."""
    store = get_object_or_404(Store, id=store_id)
    if hasattr(store, "approval_status"):
        store.approval_status = "approved"
        store.save()
    return redirect("admin_vendor_list")


@staff_member_required
@permission_required(
    "marketplace.change_store", raise_exception=True
)
def admin_reject_vendor(request, store_id):
    """Reject a pending vendor store application."""
    store = get_object_or_404(Store, id=store_id)
    if hasattr(store, "approval_status"):
        store.approval_status = "rejected"
        store.save()
    return redirect("admin_vendor_list")


@staff_member_required
def admin_moderation_queue(request):
    """Display pending stores and disputed order items."""
    pending_stores = _pending_stores_queryset()
    disputed_items = OrderItem.objects.filter(
        item_status="DISPUTED"
    )
    return render(
        request,
        "marketplace/admin_moderation_queue.html",
        {
            "pending_stores": pending_stores,
            "disputed_items": disputed_items,
        },
    )


@staff_member_required
@permission_required(
    "marketplace.change_orderitem", raise_exception=True
)
def admin_dismiss_flag(request, pk):
    """Dismiss a dispute flag on an order item."""
    item = get_object_or_404(OrderItem, pk=pk)
    item.item_status = "PROCESSING"
    item.save()
    return redirect("admin_moderation_queue")


@staff_member_required
@permission_required(
    "marketplace.delete_product", raise_exception=True
)
def admin_delist_product(request, pk):
    """Deactivate or delete a policy-violating product."""
    product = get_object_or_404(Product, pk=pk)
    if hasattr(product, "is_active"):
        product.is_active = False
        product.save()
    else:
        product.delete()
    return redirect("admin_moderation_queue")


@staff_member_required
@permission_required(
    "marketplace.change_store", raise_exception=True
)
def approve_store(request, store_id):
    """Approve a store from the moderation queue."""
    store = get_object_or_404(Store, id=store_id)
    if hasattr(store, "approval_status"):
        store.approval_status = "approved"
        store.save()
    return redirect("admin_moderation_queue")


@staff_member_required
@permission_required(
    "marketplace.change_orderitem", raise_exception=True
)
def resolve_dispute(request, item_id, action):
    """Resolve a disputed order item by refund or release."""
    item = get_object_or_404(OrderItem, id=item_id)
    if action == "refund":
        item.item_status = "CANCELLED"
        if item.product and hasattr(item.product, "stock"):
            item.product.stock += item.quantity
            item.product.save()
    elif action == "release":
        item.item_status = "DELIVERED"
    item.save()
    return redirect("admin_moderation_queue")
