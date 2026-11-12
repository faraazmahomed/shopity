from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Store, Product, OrderItem
from .forms import ProductForm, TrackingForm


@login_required
def vendor_product_list(request):
    """Display a list of products belonging to the logged-in vendor's stores."""
    stores = Store.objects.filter(owner=request.user)
    products = Product.objects.filter(store__in=stores)
    return render(request, 'marketplace/vendor_product_list.html', {'products': products, 'stores': stores})


@login_required
@permission_required('marketplace.add_product', raise_exception=True)
def vendor_product_add(request):
    """Handle creation of a new product by a vendor."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if product.store.owner == request.user:
                product.save()
                return redirect('vendor_product_list')
            else:
                raise PermissionDenied("You do not own this store.")
    else:
        form = ProductForm()
        form.fields['store'].queryset = Store.objects.filter(owner=request.user)

    return render(request, 'marketplace/vendor_product_form.html', {'form': form})


@login_required
@permission_required('marketplace.change_product', raise_exception=True)
def vendor_product_edit(request, pk):
    """Handle editing an existing product within a vendor's store."""
    product = get_object_or_404(Product, pk=pk)
    
    if product.store.owner != request.user:
        raise PermissionDenied("You do not have permission to edit this product.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_product_list')
    else:
        form = ProductForm(instance=product)
        form.fields['store'].queryset = Store.objects.filter(owner=request.user)

    return render(request, 'marketplace/vendor_product_form.html', {'form': form, 'product': product})


@login_required
@permission_required('marketplace.delete_product', raise_exception=True)
def vendor_product_delete(request, pk):
    """Handle deletion of an existing product within a vendor's store."""
    product = get_object_or_404(Product, pk=pk)

    if product.store.owner != request.user:
        raise PermissionDenied("You do not have permission to delete this product.")

    if request.method == 'POST':
        product.delete()
        return redirect('vendor_product_list')

    return render(request, 'marketplace/vendor_product_confirm_delete.html', {'product': product})


@login_required
def vendor_order_list(request):
    """Display a list of orders/order items associated with the logged-in vendor's stores."""
    stores = Store.objects.filter(owner=request.user)
    order_items = OrderItem.objects.filter(product__store__in=stores).select_related('order', 'product', 'product__store')
    return render(request, 'marketplace/vendor_order_list.html', {'order_items': order_items, 'stores': stores})


@login_required
def vendor_order_detail(request, pk):
    """Display detailed view for a specific order item belonging to the vendor's store."""
    stores = Store.objects.filter(owner=request.user)
    order_item = get_object_or_404(OrderItem, pk=pk, product__store__in=stores)
    return render(request, 'marketplace/vendor_order_detail.html', {'order_item': order_item})


@login_required
def update_order_item_status(request, pk):
    """Handle quick status or tracking updates for a specific order item."""
    stores = Store.objects.filter(owner=request.user)
    item = get_object_or_404(OrderItem, pk=pk, product__store__in=stores)

    if request.method == 'POST':
        form = TrackingForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('vendor_order_list')
    else:
        form = TrackingForm(instance=item)

    return render(request, 'marketplace/update_tracking.html', {'form': form, 'item': item})


@login_required
def vendor_dashboard(request):
    stores = Store.objects.filter(owner=request.user)
    products = Product.objects.filter(store__in=stores)
    order_items = OrderItem.objects.filter(product__store__in=stores).select_related('order', 'product')
    return render(request, 'marketplace/vendor_dashboard.html', {
        'stores': stores,
        'products': products,
        'order_items': order_items
    })


@login_required
def update_shipment_tracking(request, item_id):
    stores = Store.objects.filter(owner=request.user)
    item = get_object_or_404(OrderItem, id=item_id, product__store__in=stores)

    if request.method == 'POST':
        form = TrackingForm(request.POST, instance=item)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.item_status = 'SHIPPED'
            shipment.save()
            return redirect('vendor_dashboard')
    else:
        form = TrackingForm(instance=item)

    return render(request, 'marketplace/update_tracking.html',
                  {'form': form, 'item': item})
