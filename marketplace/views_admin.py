"""
Administrative views for managing vendor approvals and marketplace moderation.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from .models import Store, Product, OrderItem


@staff_member_required
@permission_required("marketplace.change_store", raise_exception=True)
def admin_vendor_list(request):
    """Display pending vendor stores for administrative review and approval.

    Args:
        request (HttpRequest): The incoming administrative HTTP request.

    Returns:
        HttpResponse: Rendered vendor approval list template.
    """
    pending_stores = Store.objects.filter(
        Q(approval_status__iexact="pending")
        | Q(approval_status__isnull=True)
        | Q(approval_status="")
    ).select_related("owner")
    return render(
        request,
        "marketplace/admin_vendor_list.html",
        {"pending_stores": pending_stores},
    )


@staff_member_required
@permission_required("marketplace.change_store", raise_exception=True)
def admin_approve_vendor(request, store_id):
    """Approve a pending vendor store application.

    Args:
        request (HttpRequest): The incoming HTTP request.
        store_id (int): Primary key of the Store to approve.

    Returns:
        HttpResponseRedirect: Redirect to the admin vendor list view.
    """
    store = get_object_or_404(Store, id=store_id)
    store.approval_status = "approved"
    store.save()
    return redirect("admin_vendor_list")


@staff_member_required
@permission_required("marketplace.change_store", raise_exception=True)
def admin_reject_vendor(request, store_id):
    """Reject a pending vendor store application.

    Args:
        request (HttpRequest): The incoming HTTP request.
        store_id (int): Primary key of the Store to reject.

    Returns:
        HttpResponseRedirect: Redirect to the admin vendor list view.
    """
    store = get_object_or_404(Store, id=store_id)
    store.approval_status = "rejected"
    store.save()
    return redirect("admin_vendor_list")


@staff_member_required
def admin_moderation_queue(request):
    """Display pending store applications and disputed order items for review.

    Args:
        request (HttpRequest): The incoming administrative HTTP request.

    Returns:
        HttpResponse: Rendered moderation queue template with pending items.
    """
    pending_stores = Store.objects.filter(
        Q(approval_status__iexact="pending")
        | Q(approval_status__isnull=True)
        | Q(approval_status="")
    )
    disputed_items = OrderItem.objects.filter(item_status="DISPUTED")
    return render(
        request,
        "marketplace/admin_moderation_queue.html",
        {"pending_stores": pending_stores, "disputed_items": disputed_items},
    )


@staff_member_required
@permission_required("marketplace.change_orderitem", raise_exception=True)
def admin_dismiss_flag(request, pk):
    """Dismiss a dispute flag on an order item and return it to processing.

    Args:
        request (HttpRequest): The incoming HTTP request.
        pk (int): Primary key of the OrderItem to update.

    Returns:
        HttpResponseRedirect: Redirect to the admin moderation queue.
    """
    item = get_object_or_404(OrderItem, pk=pk)
    item.item_status = "PROCESSING"
    item.save()
    return redirect("admin_moderation_queue")


@staff_member_required
@permission_required("marketplace.delete_product", raise_exception=True)
def admin_delist_product(request, pk):
    """Deactivate or delete a product that violates marketplace policies.

    Args:
        request (HttpRequest): The incoming HTTP request.
        pk (int): Primary key of the Product to delist.

    Returns:
        HttpResponseRedirect: Redirect to the admin moderation queue.
    """
    product = get_object_or_404(Product, pk=pk)
    if hasattr(product, "is_active"):
        product.is_active = False
        product.save()
    else:
        product.delete()
    return redirect("admin_moderation_queue")


@staff_member_required
@permission_required("marketplace.change_store", raise_exception=True)
def approve_store(request, store_id):
    """Approve a store directly from the administrative moderation queue.

    Args:
        request (HttpRequest): The incoming HTTP request.
        store_id (int): Primary key of the Store to approve.

    Returns:
        HttpResponseRedirect: Redirect to the admin moderation queue.
    """
    store = get_object_or_404(Store, id=store_id)
    store.approval_status = "approved"
    store.save()
    return redirect("admin_moderation_queue")


@staff_member_required
@permission_required("marketplace.change_orderitem", raise_exception=True)
def resolve_dispute(request, item_id, action):
    """Resolve a disputed order item by issuing a refund or releasing funds.

    Args:
        request (HttpRequest): The incoming HTTP request.
        item_id (int): Primary key of the disputed OrderItem.
        action (str): Resolution action ('refund' or 'release').

    Returns:
        HttpResponseRedirect: Redirect to the admin moderation queue.
    """
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
