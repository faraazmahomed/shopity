"""
Administrative views for managing vendor approvals, store statuses,
and product content moderation queue.
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from .models import Store, Product


def is_admin(user):
    """Check if the given user is authenticated and holds administrator privileges."""
    return user.is_authenticated and (user.is_superuser or getattr(user, "role", None) == "ADMIN")


@login_required
@user_passes_test(is_admin)
def admin_vendor_list(request):
    """Display a list of all vendor stores currently pending administrative approval."""
    pending_stores = Store.objects.filter(approval_status='pending')
    return render(request, "marketplace/admin_vendor_list.html", {"pending_stores": pending_stores})


@login_required
@user_passes_test(is_admin)
def admin_approve_vendor(request, store_id):
    """Approve a specific vendor store application by its unique ID."""
    store = get_object_or_404(Store, pk=store_id)
    store.approval_status = 'approved'
    store.save()
    return redirect("admin_vendor_list")


@login_required
@user_passes_test(is_admin)
def admin_reject_vendor(request, store_id):
    """Reject a vendor store application."""
    store = get_object_or_404(Store, pk=store_id)
    store.approval_status = 'rejected'
    store.save()
    return redirect("admin_vendor_list")


@login_required
@user_passes_test(is_admin)
def admin_moderation_queue(request):
    """Display a moderation queue containing flagged marketplace products."""
    flagged_products = Product.objects.filter(is_active=False)
    return render(request, "marketplace/admin_moderation_queue.html", {"flagged_products": flagged_products})


@login_required
@user_passes_test(is_admin)
def admin_delist_product(request, product_id):
    """Unpublish a specific product flagged in the moderation queue."""
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = False
    product.save()
    return redirect("admin_moderation_queue")


@login_required
@user_passes_test(is_admin)
def admin_dismiss_flag(request, product_id):
    """Dismiss the flag on a product and activate it."""
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = True
    product.save()
    return redirect("admin_moderation_queue")
