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
    """
    Lists all products belonging to the logged-in vendor's store.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered vendor product list template with store and products context.
    """
    store = get_object_or_404(Store, owner=request.user)
    products = store.products.all().order_by('-created_at')
    return render(request, 'marketplace/vendor_product_list.html', {
        'store': store,
        'products': products
    })

@login_required(login_url='login')
def vendor_product_add(request):
    """
    Allows an authenticated vendor to create and add a new product to their store inventory.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered product form template or redirect on successful creation.
    """
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
    """
    Allows a vendor to modify an existing product within their store catalog.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The primary key of the product being edited.

    Returns:
        HttpResponse: Rendered product form template with existing instance data or redirect on save.
    """
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
    """
    Allows a vendor to remove a product from their store inventory.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The primary key of the product to delete.

    Returns:
        HttpResponse: Rendered deletion confirmation template or redirect on deletion.
    """
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
    """
    Displays all order items purchased from the logged-in vendor's store.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered vendor order list template with order items context.
    """
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
    """
    Displays granular details for a specific order item and processes fulfillment status changes.

    Args:
        request (HttpRequest): The HTTP request object.
        order_item_id (int): The primary key of the target order item.

    Returns:
        HttpResponse: Rendered order detail template or redirect after status modification.
    """
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


# ==========================================
# CONTEXT PROCESSORS
# ==========================================

def store_context(request):
    """
    Global template context processor to inject the authenticated user's store instance.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary mapping 'user_store' to the user's Store instance or None.
    """
    context = {}
    if request.user.is_authenticated:
        context['user_store'] = Store.objects.filter(owner=request.user).first()
    return context