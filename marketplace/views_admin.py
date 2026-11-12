from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from .models import Store, Product, OrderItem


@staff_member_required
@permission_required('marketplace.change_store', raise_exception=True)
def admin_vendor_list(request):
    """Display a list of pending vendor stores for administrative review and approval."""
    pending_stores = Store.objects.filter(
        Q(approval_status__iexact='pending') | 
        Q(approval_status__isnull=True) | 
        Q(approval_status='')
    ).select_related('owner')
    return render(request, 'marketplace/admin_vendor_list.html', {'pending_stores': pending_stores})


@staff_member_required
@permission_required('marketplace.change_store', raise_exception=True)
def admin_approve_vendor(request, store_id):
    """Approve a vendor store application."""
    store = get_object_or_404(Store, id=store_id)
    store.approval_status = 'approved'
    store.save()
    return redirect('admin_vendor_list')


@staff_member_required
@permission_required('marketplace.change_store', raise_exception=True)
def admin_reject_vendor(request, store_id):
    """Reject a vendor store application."""
    store = get_object_or_404(Store, id=store_id)
    store.approval_status = 'rejected'
    store.save()
    return redirect('admin_vendor_list')


@staff_member_required
def admin_moderation_queue(request):
    pending_stores = Store.objects.filter(
        Q(approval_status__iexact='pending') | 
        Q(approval_status__isnull=True) | 
        Q(approval_status='')
    )
    disputed_items = OrderItem.objects.filter(item_status='DISPUTED')
    return render(request, 'marketplace/admin_moderation_queue.html', {
        'pending_stores': pending_stores,
        'disputed_items': disputed_items
    })


@staff_member_required
@permission_required('marketplace.change_orderitem', raise_exception=True)
def admin_dismiss_flag(request, pk):
    """Dismiss a flag or dispute on an item, returning it to standard processing."""
    item = get_object_or_404(OrderItem, pk=pk)
    item.item_status = 'PROCESSING'
    item.save()
    return redirect('admin_moderation_queue')


@staff_member_required
@permission_required('marketplace.delete_product', raise_exception=True)
def admin_delist_product(request, pk):
    """Delist or deactivate a specific product violating marketplace policy."""
    product = get_object_or_404(Product, pk=pk)
    if hasattr(product, 'is_active'):
        product.is_active = False
        product.save()
    else:
        product.delete()
    return redirect('admin_moderation_queue')


@staff_member_required
@permission_required('marketplace.change_store', raise_exception=True)
def approve_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    store.approval_status = 'approved'
    store.save()
    return redirect('admin_moderation_queue')


@staff_member_required
@permission_required('marketplace.change_orderitem', raise_exception=True)
def resolve_dispute(request, item_id, action):
    item = get_object_or_404(OrderItem, id=item_id)
    if action == 'refund':
        item.item_status = 'CANCELLED'
        if item.product and hasattr(item.product, 'stock'):
            item.product.stock += item.quantity
            item.product.save()
    elif action == 'release':
        item.item_status = 'DELIVERED'
    item.save()
    return redirect('admin_moderation_queue')
