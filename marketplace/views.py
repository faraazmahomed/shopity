"""Views for the Marketplace application."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    login,
)
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
import hashlib

from .forms import (
    ProductForm,
    ProductReviewForm,
    RegisterForm,
    StoreForm,
    TrackingForm,
)
from .models import (
    Order,
    OrderItem,
    Product,
    ProductReview,
    ResetToken,
    Store,
)
from .cart import Cart
from functions.reddit import fetch_subreddit_posts


class RoleBasedLoginView(LoginView):
    """Custom login view routing users by group and store status."""
    template_name = 'marketplace/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return '/management/vendors/'
        
        if user.groups.filter(name='Vendors').exists():
            if not Store.objects.filter(
                owner=user
            ).exists():
                return '/store/create/'
            return '/vendor/dashboard/'
            
        return '/buyer/dashboard/'


def home(request):
    """Render the homepage with active products."""
    if hasattr(Product, 'is_active'):
        products = Product.objects.filter(
            is_active=True
        )[:8]
    else:
        products = Product.objects.all()[:8]
    return render(
        request, 'marketplace/home.html', {'products': products}
    )


def store_context(request):
    """Provide store and vendor context for templates."""
    context = {}
    if request.user.is_authenticated:
        context['user_store'] = Store.objects.filter(
            owner=request.user
        ).first()
        context['is_vendor'] = (
            request.user.groups.filter(
                name='Vendors'
            ).exists()
            or request.user.is_staff
        )
    return context


def product_catalog(request):
    """Display the full product catalog."""
    products = Product.objects.all()
    return render(
        request,
        'marketplace/product_catalog.html',
        {'products': products},
    )


def product_detail(request, pk):
    """Display detailed information for a single product."""
    product = get_object_or_404(Product, pk=pk)
    reviews = (
        ProductReview.objects.filter(product=product)
        if 'ProductReview' in globals()
        else []
    )
    form = (
        ProductReviewForm()
        if 'ProductReviewForm' in globals()
        else None
    )
    return render(
        request,
        'marketplace/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'form': form,
        },
    )


@login_required(login_url='login')
def add_product_review(request, product_id):
    """Handle product review creation and check verified purchase."""
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            
            if hasattr(review, 'is_verified'):
                review.is_verified = OrderItem.objects.filter(
                    order__user=request.user,
                    product=product
                ).exists()
                
            review.save()
            messages.success(
                request, "Review added successfully."
            )
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductReviewForm()
    return render(
        request,
        'marketplace/product_review_form.html',
        {'form': form, 'product': product},
    )


@login_required(login_url='login')
def cart_detail(request):
    """Display the contents of the session cart."""
    cart_obj = Cart(request)
    return render(
        request,
        'marketplace/cart_detail.html',
        {'cart': cart_obj},
    )


@login_required(login_url='login')
def cart(request):
    """Alias for cart_detail URL reversal."""
    return redirect('cart_detail')


@require_POST
@login_required(login_url='login')
def cart_add(request, product_id):
    """Add a product item to the session cart."""
    cart_obj = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    update_quantity = (
        request.POST.get('update', False) == 'True'
    )
    
    cart_obj.add(
        product=product,
        quantity=quantity,
        update_quantity=update_quantity,
    )
    messages.success(
        request, f"Added {product.name} to your cart."
    )
    return redirect('cart_detail')


@login_required(login_url='login')
def cart_remove(request, product_id):
    """Remove a product item from the session cart."""
    cart_obj = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart_obj.remove(product)
    messages.success(
        request, "Item removed from your cart."
    )
    return redirect('cart_detail')


@login_required(login_url='login')
def checkout(request):
    """Process cart items into an order and send an email invoice."""
    cart_obj = Cart(request)
    
    if not len(cart_obj):
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_detail')

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user, status='PENDING'
        )
        
        invoice_lines = []
        total_amount = 0
        
        for item in cart_obj:
            product = item['product']
            quantity = item['quantity']
            item_price = (
                product.base_price
                if hasattr(product, 'base_price')
                else item['price']
            )
            item_total = item_price * quantity
            total_amount += item_total
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item_price,
                item_status='PROCESSING',
            )
            invoice_lines.append(
                f"- {product.name} x {quantity} "
                f"@ R{item_price} = R{item_total}"
            )
        
        invoice_body = (
            f"Dear {request.user.username},\n\n"
            f"Thank you for your order! Here is your invoice "
            f"for Order #{order.id}:\n\n"
            + "\n".join(invoice_lines) +
            f"\n\nTotal Amount: R{total_amount}\n\n"
            f"Status: Pending Processing\n\n"
            f"Thank you for shopping with Shopity!"
        )
        
        if request.user.email:
            send_mail(
                subject=f"Your Shopity Invoice - Order #{order.id}",
                message=invoice_body,
                from_email=getattr(
                    settings,
                    'DEFAULT_FROM_EMAIL',
                    'noreply@shopity.com',
                ),
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        
        cart_obj.clear()
        messages.success(
            request,
            "Order placed successfully! An invoice has been emailed.",
        )
        return redirect('buyer_orders')

    return render(
        request,
        'marketplace/checkout.html',
        {'cart': cart_obj},
    )


@login_required(login_url='login')
def buyer_orders(request):
    """Display all orders placed by the current buyer."""
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items__product')
    return render(
        request,
        'marketplace/buyer_orders.html',
        {'orders': orders},
    )


def register(request):
    """Handle new user registration and automatic login."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            
            if (
                user.groups.filter(name='Vendors').exists()
                and not Store.objects.filter(
                    owner=user
                ).exists()
            ):
                return redirect('store_create')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(
        request,
        'marketplace/register.html',
        {'form': form},
    )


def password_reset_request(request):
    """Handle generation of password reset requests and tokens."""
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            raw_token = ResetToken.generate_token(user)
            reset_url = request.build_absolute_uri(
                f'/password-reset/confirm/{raw_token}/'
            )
            
            message = (
                f"Hi {user.username},\n\n"
                f"You requested a password reset for Shopity. "
                f"Click the link below (valid for 1 hour):\n\n"
                f"{reset_url}\n\n"
                f"If you didn't request this, ignore this email."
            )
            
            send_mail(
                subject="Password Reset - Shopity",
                message=message,
                from_email=getattr(
                    settings,
                    'DEFAULT_FROM_EMAIL',
                    'noreply@shopity.com',
                ),
                recipient_list=[email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass
            
        return render(
            request, 'marketplace/password_reset_done.html'
        )
        
    return render(
        request, 'marketplace/password_reset_form.html'
    )


def password_reset_confirm(request, token):
    """Validate password reset token and update user password."""
    token_hash = hashlib.sha256(
        token.encode('utf-8')
    ).hexdigest()
    reset_obj = ResetToken.objects.filter(
        token_hash=token_hash, is_used=False
    ).first()
    
    if (
        not reset_obj
        or reset_obj.expiry_at < timezone.now()
    ):
        messages.error(
            request,
            "This password reset link is invalid or expired.",
        )
        return redirect('password_reset_request')
        
    user = reset_obj.user
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            reset_obj.is_used = True
            reset_obj.save()
            return render(
                request,
                'marketplace/password_reset_complete.html',
            )
    else:
        form = SetPasswordForm(user)
        
    return render(
        request,
        'marketplace/password_reset_confirm.html',
        {'form': form},
    )


@login_required(login_url='login')
def buyer_dashboard(request):
    """Display recent orders for the buyer dashboard."""
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    return render(
        request,
        'marketplace/buyer_dashboard.html',
        {'orders': orders},
    )


@login_required(login_url='login')
def vendor_dashboard(request):
    """Display vendor store stats, products, and order items."""
    store = Store.objects.filter(owner=request.user).first()
    products = (
        Product.objects.filter(store=store) if store else []
    )
    order_items = (
        OrderItem.objects.filter(
            product__store=store
        ).select_related('order', 'product')
        if store
        else []
    )
    return render(
        request,
        'marketplace/vendor_dashboard.html',
        {
            'store': store,
            'products': products,
            'order_items': order_items,
        },
    )


@login_required(login_url='login')
def store_create(request):
    """Handle vendor store profile creation."""
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            messages.success(
                request,
                "Store created successfully.",
            )
            return redirect('vendor_dashboard')
    else:
        form = StoreForm()
    return render(
        request,
        'marketplace/store_form.html',
        {'form': form},
    )


@login_required(login_url='login')
def store_detail(request, pk):
    """Display public details and products of a store."""
    store = get_object_or_404(Store, pk=pk)
    products = Product.objects.filter(store=store)
    return render(
        request,
        'marketplace/store_detail.html',
        {'store': store, 'products': products},
    )


@login_required(login_url='login')
def store_edit(request):
    """Handle editing of the vendor's own store."""
    store = get_object_or_404(Store, owner=request.user)
    if request.method == 'POST':
        form = StoreForm(
            request.POST, request.FILES, instance=store
        )
        if form.is_valid():
            form.save()
            messages.success(
                request, "Store updated successfully."
            )
            return redirect('vendor_dashboard')
    else:
        form = StoreForm(instance=store)
    return render(
        request,
        'marketplace/store_form.html',
        {'form': form, 'store': store},
    )


@login_required(login_url='login')
def store_delete(request):
    """Handle deletion of the vendor's store."""
    store = get_object_or_404(Store, owner=request.user)
    if request.method == 'POST':
        store.delete()
        messages.success(
            request, "Store deleted successfully."
        )
        return redirect('home')
    return render(
        request,
        'marketplace/store_confirm_delete.html',
        {'store': store},
    )


@login_required(login_url='login')
@permission_required(
    'marketplace.add_product', raise_exception=True
)
def product_create(request):
    """Handle creation of a new product by a vendor."""
    store = Store.objects.filter(owner=request.user).first()
    if not store:
        messages.warning(
            request, "You must create a store first."
        )
        return redirect('store_create')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            if product.store.owner != request.user:
                raise PermissionDenied(
                    "You do not own this store."
                )
            product.save()
            messages.success(
                request, "Product created successfully."
            )
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
        if 'store' in form.fields:
            form.fields['store'].queryset = (
                Store.objects.filter(owner=request.user)
            )
            form.fields['store'].initial = store
            
    return render(
        request,
        'marketplace/product_form.html',
        {'form': form},
    )


@login_required(login_url='login')
@permission_required(
    'marketplace.change_product', raise_exception=True
)
def product_edit(request, pk):
    """Handle editing an existing store product."""
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, pk=pk, store=store)
    if request.method == 'POST':
        form = ProductForm(
            request.POST, request.FILES, instance=product
        )
        if form.is_valid():
            form.save()
            messages.success(
                request, "Product updated successfully."
            )
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(
        request,
        'marketplace/product_form.html',
        {'form': form, 'product': product},
    )


@login_required(login_url='login')
@permission_required(
    'marketplace.delete_product', raise_exception=True
)
def product_delete(request, pk):
    """Handle deletion of a store product."""
    store = get_object_or_404(Store, owner=request.user)
    product = get_object_or_404(Product, pk=pk, store=store)
    if request.method == 'POST':
        product.delete()
        messages.success(
            request, "Product deleted successfully."
        )
        return redirect('vendor_dashboard')
    return render(
        request,
        'marketplace/product_confirm_delete.html',
        {'product': product},
    )


@login_required(login_url='login')
def vendor_order_list(request):
    """Display incoming orders and items for vendor stores."""
    stores = Store.objects.filter(owner=request.user)
    order_items = OrderItem.objects.filter(
        product__store__in=stores
    ).select_related('order', 'product', 'product__store')
    return render(
        request,
        'marketplace/vendor_order_list.html',
        {'order_items': order_items, 'stores': stores},
    )


@login_required(login_url='login')
def vendor_order_detail(request, pk):
    """Display detailed view of a specific vendor order item."""
    stores = Store.objects.filter(owner=request.user)
    order_item = get_object_or_404(
        OrderItem, pk=pk, product__store__in=stores
    )
    return render(
        request,
        'marketplace/vendor_order_detail.html',
        {'order_item': order_item},
    )


@login_required(login_url='login')
def update_order_item_status(request, pk):
    """Handle tracking and status updates for order items."""
    stores = Store.objects.filter(owner=request.user)
    item = get_object_or_404(
        OrderItem, pk=pk, product__store__in=stores
    )

    if request.method == 'POST':
        form = TrackingForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Tracking updated successfully."
            )
            return redirect('vendor_order_list')
    else:
        form = TrackingForm(instance=item)

    return render(
        request,
        'marketplace/update_tracking.html',
        {'form': form, 'item': item},
    )


def reddit_feed(request):
    """Fetch posts from the Reddit subreddit and render them."""
    posts = []
    try:
        posts = fetch_subreddit_posts(
            subreddit_name="django", limit=10
        )
    except Exception as e:
        messages.error(
            request, f"Could not load Reddit feed: {e}"
        )
        
    return render(
        request,
        'marketplace/reddit_feed.html',
        {'posts': posts},
    )
