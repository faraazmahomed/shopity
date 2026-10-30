from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Store, Cart, CartItem, Order, OrderItem, ProductReview
from .forms import RegisterForm, StoreForm, ProductForm, ProductReviewForm
from .functions.reddit import fetch_reddit_posts
import requests
from django.shortcuts import render

def home(request):
    products = Product.objects.filter(is_active=True)[:8] if hasattr(Product, 'is_active') else Product.objects.all()[:8]
    reddit_posts = fetch_reddit_posts(subreddit_name='django', limit=4)
    return render(request, 'marketplace/home.html', {
        'products': products,
        'reddit_posts': reddit_posts
    })

def reddit_feed(request):
    """
    Fetches hot posts from the r/django subreddit with a custom User-Agent header 
    to prevent Reddit 403 blocks, with built-in fallback data.
    """
    url = "https://www.reddit.com/r/django/hot.json?limit=4"
    
    # Custom headers are REQUIRED by Reddit to prevent 403 Forbidden blocks
    headers = {'User-Agent': 'ShopityMarketplaceBot/1.0 (by u/Faraaz)'}
    
    posts = []
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Extract post details from Reddit's JSON structure
            for child in data.get('data', {}).get('children', []):
                post_data = child.get('data', {})
                posts.append({
                    'title': post_data.get('title'),
                    'url': post_data.get('url'),
                    'score': post_data.get('score'),
                    'author': post_data.get('author'),
                    'subreddit': post_data.get('subreddit'),
                    'num_comments': post_data.get('num_comments'),
                })
        else:
            # Fallback if Reddit returns a non-200 status code
            posts = get_default_reddit_posts()
    except Exception as e:
        print(f"Live Reddit fetch failed: {e}")
        posts = get_default_reddit_posts()

    return render(request, 'marketplace/reddit_feed.html', {'posts': posts})

def get_default_reddit_posts():
    """Provides fallback mock posts if the live Reddit API is unreachable."""
    return [
        {
            'title': 'Welcome to Django 6.1! Here is what you need to know.',
            'url': 'https://www.reddit.com/r/django/',
            'score': 342,
            'author': 'django_dev_lead',
            'subreddit': 'django',
            'num_comments': 58
        },
        {
            'title': 'Best practices for organizing large Django e-commerce projects',
            'url': 'https://www.reddit.com/r/django/',
            'score': 215,
            'author': 'fullstack_coder',
            'subreddit': 'django',
            'num_comments': 24
        },
        {
            'title': 'How to handle custom user authentication and store ownership cleanly',
            'url': 'https://www.reddit.com/r/django/',
            'score': 189,
            'author': 'python_enthusiast',
            'subreddit': 'django',
            'num_comments': 19
        }
    ]


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
