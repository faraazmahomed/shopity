from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Store, Product, OrderItem
from .forms import ProductForm

# ==========================================
# PRODUCT INVENTORY MANAGEMENT VIEWS
# ==========================================

@login_required(login_url='login')
def vendor_product_list(request):
    """Lists all products for the logged-in vendor's store."""
    store = get_object_or_404(Store, owner=request.user)
    products = store.products.all().order_by('-created_at')
    return render(request, 'marketplace/vendor_product_list.html', {
        'store': store,
        'products': products
    })

@login_required(login_url='login')
def vendor_product_add(request):
    """Allows a vendor to add a new product to their store."""
    store = get_object_or_404(Store, owner=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            messages.success(request, f"Product '{product.name}' created successfully!")
            return redirect('vendor_product_list')
    else:
        form = ProductForm()

    return render(request, 'marketplace/vendor_product_form.html', {
        'form': form,
        'title': 'Add New Product'
    })

@login_required(login_url='login')
def vendor_product_edit(request, product_id):
    """Allows a vendor to edit an existing product in their store."""
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('vendor_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'marketplace/vendor_product_form.html', {
        'form': form,
        'product': product,
        'title': f"Edit Product: {product.name}"
    })

@login_required(login_url='login')
def vendor_product_delete(request, product_id):
    """Allows a vendor to delete a product from their store."""
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)

    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' was deleted.")
        return redirect('vendor_product_list')

    return render(request, 'marketplace/vendor_product_confirm_delete.html', {
        'product': product
    })


# ==========================================
# ORDER PROCESSING VIEWS
# ==========================================

@login_required(login_url='login')
def vendor_order_list(request):
    """Lists all order items purchased from the logged-in vendor's store."""
    store = get_object_or_404(Store, owner=request.user)
    
    # Fetch all order items linked to products belonging to this vendor's store
    order_items = OrderItem.objects.filter(product__store=store).select_related(
        'order', 'product', 'order__user'
    ).order_by('-order__created_at')
    
    return render(request, 'marketplace/vendor_order_list.html', {
        'store': store,
        'order_items': order_items
    })

@login_required(login_url='login')
def vendor_order_detail(request, order_item_id):
    """Displays detailed information for a specific vendor order item and allows status updates."""
    store = get_object_or_404(Store, owner=request.user)
    order_item = get_object_or_404(OrderItem, id=order_item_id, product__store=store)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
        if new_status in valid_statuses:
            order_item.order.status = new_status
            order_item.order.save()
            messages.success(request, f"Order #{order_item.order.pk} status updated to {new_status.capitalize()}.")
            return redirect('vendor_order_list')
            
    return render(request, 'marketplace/vendor_order_detail.html', {
        'store': store,
        'order_item': order_item
    })
