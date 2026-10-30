from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Store, Product
from .forms import ProductForm

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
            messages.success(request, f"Product '{product.title}' created successfully!")
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
            messages.success(request, f"Product '{product.title}' updated successfully!")
            return redirect('vendor_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'marketplace/vendor_product_form.html', {
        'form': form,
        'product': product,
        'title': f"Edit Product: {product.title}"
    })

@login_required(login_url='login')
def vendor_product_delete(request, product_id):
    """Allows a vendor to delete a product from their store."""
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)

    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f"Product '{title}' was deleted.")
        return redirect('vendor_product_list')

    return render(request, 'marketplace/vendor_product_confirm_delete.html', {
        'product': product
    })
