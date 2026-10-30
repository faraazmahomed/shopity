from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Store, Cart, CartItem, Order, OrderItem, ProductReview
from .forms import RegisterForm, StoreForm, ProductForm, ProductReviewForm

def home(request):
    products = Product.objects.filter(is_active=True)[:8] if hasattr(Product, 'is_active') else Product.objects.all()[:8]
    return render(request, 'marketplace/home.html', {'products': products})

def product_catalog(request):
    products = Product.objects.all()
    return render(request, 'marketplace/product_catalog.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = ProductReview.objects.filter(product=product) if 'ProductReview' in globals() else []
    form = ProductReviewForm() if 'ProductReviewForm' in globals() else None
    return render(request, 'marketplace/product_detail.html', {'product': product, 'reviews': reviews, 'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'marketplace/register.html', {'form': form})

@login_required(login_url='login')
def buyer_dashboard(request):
    return render(request, 'marketplace/buyer_dashboard.html')

@login_required(login_url='login')
def vendor_dashboard(request):
    store = Store.objects.filter(owner=request.user).first()
    products = Product.objects.filter(store=store) if store else []
    return render(request, 'marketplace/vendor_dashboard.html', {'store': store, 'products': products})

@login_required(login_url='login')
def store_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            messages.success(request, "Store created successfully.")
            return redirect('vendor_dashboard')
    else:
        form = StoreForm()
    return render(request, 'marketplace/store_form.html', {'form': form})

@login_required(login_url='login')
def store_detail(request, pk):
    """
    Display details and products for a specific vendor store.
    """
    store = get_object_or_404(Store, pk=pk)
    products = Product.objects.filter(store=store)
    return render(request, 'marketplace/store_detail.html', {'store': store, 'products': products})

@login_required(login_url='login')
def store_edit(request):
    store = get_object_or_404(Store, owner=request.user)
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, "Store updated successfully.")
            return redirect('vendor_dashboard')
    else:
        form = StoreForm(instance=store)
    return render(request, 'marketplace/store_form.html', {'form': form, 'store': store})

@login_required(login_url='login')
def store_delete(request):
    store = get_object_or_404(Store, owner=request.user)
    if request.method == 'POST':
        store.delete()
        messages.success(request, "Store deleted successfully.")
        return redirect('vendor_dashboard')
    return render(request, 'marketplace/store_confirm_delete.html', {'store': store})

@login_required(login_url='login')
def product_create(request):
    store = get_object_or_404(Store, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            messages.success(request, "Product created successfully.")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
    return render(request, 'marketplace/product_form.html', {'form': form})

@login_required(login_url='login')
def product_edit(request, pk):
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, pk=pk, store=store)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/product_form.html', {'form': form, 'product': product})

def store_context(request):
    """Adds a global user_has_store boolean to all templates."""
    if request.user.is_authenticated:
        has_store = Store.objects.filter(owner=request.user).exists()
        return {'user_has_store': has_store}
    return {'user_has_store': False}

@login_required(login_url='login')
def product_delete(request, pk):
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, pk=pk, store=store)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('vendor_dashboard')
    return render(request, 'marketplace/product_confirm_delete.html', {'product': product})

@login_required(login_url='login')
def cart_view(request):
    """
    Display the contents of the user's shopping cart.
    """
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'marketplace/cart_detail.html', {'cart': cart})

@login_required(login_url='login')
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'marketplace/cart_detail.html', {'cart': cart})

@login_required(login_url='login')
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, "Added to cart.")
    return redirect('cart_detail')

@login_required(login_url='login')
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Removed from cart.")
    return redirect('cart_detail')

@login_required(login_url='login')
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_price=cart.total_price if hasattr(cart, 'total_price') else 0)
        for item in cart.items.all() if hasattr(cart, 'items') else []:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        cart.items.all().delete()
        messages.success(request, "Order placed successfully.")
        return redirect('buyer_orders')
    return render(request, 'marketplace/checkout.html', {'cart': cart})

@login_required(login_url='login')
def buyer_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'marketplace/buyer_orders.html', {'orders': orders})

@login_required(login_url='login')
def vendor_orders(request):
    store = get_object_or_404(Store, owner=request.user)
    order_items = OrderItem.objects.filter(product__store=store)
    return render(request, 'marketplace/vendor_orders.html', {'order_items': order_items})

@login_required(login_url='login')
def update_order_item_status(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id, product__store__owner=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status and hasattr(item, 'status'):
            item.status = status
            item.save()
            messages.success(request, "Order item status updated.")
    return redirect('vendor_orders')

@login_required(login_url='login')
def add_product_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Review added successfully.")
    return redirect('product_detail', pk=pk)
