"""Views for the Marketplace application."""

import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .cart import Cart
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


def _user_is_vendor(user):
    """Return True if the user is a vendor or store owner."""
    if not user.is_authenticated:
        return False
    return (
        user.groups.filter(name="Vendors").exists()
        or Store.objects.filter(owner=user).exists()
    )


class RoleBasedLoginView(LoginView):
    """Route authenticated users by role and store state."""

    template_name = "marketplace/login.html"

    def get_success_url(self):
        """Return redirect URL based on user role."""
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return "/management/vendors/"

        if user.groups.filter(name="Vendors").exists():
            if not Store.objects.filter(owner=user).exists():
                return "/vendor/store/create/"
            return "/vendor/dashboard/"

        return "/buyer/dashboard/"


def home(request):
    """Render the homepage with active products."""
    if hasattr(Product, "is_active"):
        products = Product.objects.filter(is_active=True)[:8]
    else:
        products = Product.objects.all()[:8]
    return render(
        request,
        "marketplace/home.html",
        {"products": products},
    )


def product_catalog(request):
    """Display the full product catalog."""
    products = Product.objects.all()
    return render(
        request,
        "marketplace/product_catalog.html",
        {"products": products},
    )


def product_detail(request, pk):
    """Display detailed information for a single product."""
    product = get_object_or_404(Product, pk=pk)
    reviews = ProductReview.objects.filter(product=product)
    review_form = ProductReviewForm()

    is_vendor = _user_is_vendor(request.user)
    is_store_owner = (
        request.user.is_authenticated
        and product.store.owner == request.user
    )
    has_reviewed = (
        request.user.is_authenticated
        and reviews.filter(user=request.user).exists()
    )
    can_review = (
        request.user.is_authenticated
        and not is_vendor
        and not is_store_owner
        and not has_reviewed
    )

    return render(
        request,
        "marketplace/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "form": review_form,
            "review_form": review_form,
            "can_review": can_review,
            "has_reviewed": has_reviewed,
        },
    )


@login_required(login_url="login")
def add_product_review(request, product_id):
    """Create a product review and verify purchase."""
    product = get_object_or_404(Product, pk=product_id)

    if _user_is_vendor(
        request.user
    ) or product.store.owner == request.user:
        messages.error(
            request,
            "Vendors cannot submit customer reviews.",
        )
        return redirect("product_detail", pk=product.pk)

    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user

            if hasattr(review, "is_verified"):
                review.is_verified = OrderItem.objects.filter(
                    order__user=request.user,
                    product=product,
                ).exists()

            review.save()
            messages.success(
                request, "Review added successfully."
            )
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductReviewForm()
    return render(
        request,
        "marketplace/product_review_form.html",
        {"form": form, "product": product},
    )


@login_required(login_url="login")
def cart_detail(request):
    """Display the contents of the session cart."""
    cart_obj = Cart(request)
    return render(
        request,
        "marketplace/cart_detail.html",
        {"cart": cart_obj},
    )


@login_required(login_url="login")
def cart(request):
    """Alias for cart_detail URL reversal."""
    return redirect("cart_detail")


@require_POST
@login_required(login_url="login")
def cart_add(request, product_id):
    """Add a product item to the session cart."""
    cart_obj = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get("quantity", 1))
    update_quantity = (
        request.POST.get("update", False) == "True"
    )

    cart_obj.add(
        product=product,
        quantity=quantity,
        update_quantity=update_quantity,
    )
    messages.success(
        request, f"Added {product.name} to your cart."
    )
    return redirect("cart_detail")


@login_required(login_url="login")
def cart_remove(request, product_id):
    """Remove a product item from the session cart."""
    cart_obj = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart_obj.remove(product)
    messages.success(
        request, "Item removed from your cart."
    )
    return redirect("cart_detail")


@login_required(login_url="login")
def checkout(request):
    """Convert cart items into an order and email invoice."""
    cart_obj = Cart(request)

    if not len(cart_obj):
        messages.warning(request, "Your cart is empty.")
        return redirect("cart_detail")

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user, status="PENDING"
        )

        invoice_lines = []
        total_amount = 0

        for item in cart_obj:
            product = item["product"]
            quantity = item["quantity"]
            item_price = (
                product.base_price
                if hasattr(product, "base_price")
                else item["price"]
            )
            item_total = item_price * quantity
            total_amount += item_total

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item_price,
                item_status="PROCESSING",
            )
            invoice_lines.append(
                f"- {product.name} x {quantity} "
                f"@ R{item_price} = R{item_total}"
            )

        invoice_body = (
            f"Dear {request.user.username},\n\n"
            f"Thank you for your order! Here is your invoice "
            f"for Order #{order.id}:\n\n"
            + "\n".join(invoice_lines)
            + f"\n\nTotal Amount: R{total_amount}\n\n"
            f"Status: Pending Processing\n\n"
            f"Thank you for shopping with Shopity!"
        )

        if request.user.email:
            send_mail(
                subject=(
                    f"Your Shopity Invoice - Order #{order.id}"
                ),
                message=invoice_body,
                from_email=getattr(
                    settings,
                    "DEFAULT_FROM_EMAIL",
                    "noreply@shopity.com",
                ),
                recipient_list=[request.user.email],
                fail_silently=True,
            )

        cart_obj.clear()
        messages.success(
            request,
            "Order placed! An invoice has been emailed.",
        )
        return redirect("buyer_orders")

    return render(
        request,
        "marketplace/checkout.html",
        {"cart": cart_obj},
    )


@login_required(login_url="login")
def buyer_orders(request):
    """Display all orders placed by the current buyer."""
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related("items__product")
    return render(
        request,
        "marketplace/buyer_orders.html",
        {"orders": orders},
    )


def register(request):
    """Handle new user registration and automatic login."""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Registration successful!"
            )

            if (
                user.groups.filter(name="Vendors").exists()
                and not Store.objects.filter(
                    owner=user
                ).exists()
            ):
                return redirect("store_create")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(
        request,
        "marketplace/register.html",
        {"form": form},
    )


def password_reset_request(request):
    """Generate and send a password reset token email."""
    if request.method == "POST":
        email = request.POST.get("email")
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
            raw_token = ResetToken.generate_token(user)
            reset_path = reverse(
                "password_reset_confirm",
                kwargs={"token": raw_token},
            )
            reset_url = request.build_absolute_uri(reset_path)

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
                    "DEFAULT_FROM_EMAIL",
                    "noreply@shopity.com",
                ),
                recipient_list=[email],
                fail_silently=True,
            )
        except user_model.DoesNotExist:
            pass

        return render(
            request, "marketplace/password_reset_done.html"
        )

    return render(
        request, "marketplace/password_reset_form.html"
    )


def password_reset_confirm(request, token):
    """Validate password reset token and update password."""
    token_hash = hashlib.sha256(
        token.encode("utf-8")
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
            "This reset link is invalid or expired.",
        )
        return redirect("password_reset_request")

    user = reset_obj.user

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            reset_obj.is_used = True
            reset_obj.save()
            return render(
                request,
                "marketplace/password_reset_complete.html",
            )
    else:
        form = SetPasswordForm(user)

    return render(
        request,
        "marketplace/password_reset_confirm.html",
        {"form": form},
    )


@login_required(login_url="login")
def buyer_dashboard(request):
    """Display recent orders for the buyer dashboard."""
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]
    return render(
        request,
        "marketplace/buyer_dashboard.html",
        {"orders": orders},
    )


@login_required(login_url="login")
def vendor_dashboard(request):
    """Display all vendor stores, products, and orders."""
    stores = Store.objects.filter(
        owner=request.user
    ).order_by("id")
    selected_store_id = request.GET.get("store")
    active_store = None
    if selected_store_id:
        active_store = stores.filter(
            pk=selected_store_id
        ).first()
    if active_store is None:
        active_store = stores.first()

    products = Product.objects.filter(
        store__in=stores
    ).select_related("store")
    order_items = OrderItem.objects.filter(
        product__store__in=stores
    ).select_related("order", "product", "product__store")

    return render(
        request,
        "marketplace/vendor_dashboard.html",
        {
            "stores": stores,
            "active_store": active_store,
            "store": active_store,
            "products": products,
            "order_items": order_items,
        },
    )


@login_required(login_url="login")
@permission_required(
    "marketplace.add_store", raise_exception=True
)
def store_create(request):
    """Handle creation of a new vendor store."""
    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            messages.success(
                request, "Store created successfully."
            )
            return redirect("vendor_dashboard")
    else:
        form = StoreForm()
    return render(
        request,
        "marketplace/store_form.html",
        {"form": form},
    )


@login_required(login_url="login")
def store_detail(request, pk):
    """Display details and products of a specific store."""
    store = get_object_or_404(Store, pk=pk)
    products = Product.objects.filter(store=store)
    return render(
        request,
        "marketplace/store_detail.html",
        {"store": store, "products": products},
    )


@login_required(login_url="login")
@permission_required(
    "marketplace.change_store", raise_exception=True
)
def store_edit(request, pk):
    """Handle editing one of the vendor's own stores."""
    store = get_object_or_404(
        Store, pk=pk, owner=request.user
    )
    if request.method == "POST":
        form = StoreForm(
            request.POST, request.FILES, instance=store
        )
        if form.is_valid():
            form.save()
            messages.success(
                request, "Store updated successfully."
            )
            return redirect("vendor_dashboard")
    else:
        form = StoreForm(instance=store)
    return render(
        request,
        "marketplace/store_form.html",
        {"form": form, "store": store},
    )


@login_required(login_url="login")
@permission_required(
    "marketplace.delete_store", raise_exception=True
)
def store_delete(request, pk):
    """Handle deletion of one of the vendor's stores."""
    store = get_object_or_404(
        Store, pk=pk, owner=request.user
    )
    if request.method == "POST":
        store.delete()
        messages.success(
            request, "Store deleted successfully."
        )
        return redirect("vendor_dashboard")
    return render(
        request,
        "marketplace/store_confirm_delete.html",
        {"store": store},
    )


@login_required(login_url="login")
@permission_required(
    "marketplace.add_product", raise_exception=True
)
def product_create(request):
    """Create a product under one of the vendor's stores."""
    vendor_stores = Store.objects.filter(
        owner=request.user
    ).order_by("id")
    if not vendor_stores.exists():
        messages.warning(
            request, "You must create a store first."
        )
        return redirect("store_create")

    requested_store_id = (
        request.POST.get("store")
        or request.GET.get("store")
        or request.POST.get("store_id")
        or request.GET.get("store_id")
    )
    default_store = (
        vendor_stores.filter(pk=requested_store_id).first()
        if requested_store_id
        else vendor_stores.first()
    )

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if "store" in form.fields:
            form.fields["store"].queryset = vendor_stores
        if form.is_valid():
            product = form.save(commit=False)
            if not getattr(product, "store_id", None):
                product.store = default_store
            if product.store.owner != request.user:
                raise PermissionDenied(
                    "You do not own this store."
                )
            product.save()
            messages.success(
                request, "Product created successfully."
            )
            return redirect("vendor_dashboard")
    else:
        initial = (
            {"store": default_store} if default_store else {}
        )
        form = ProductForm(initial=initial)
        if "store" in form.fields:
            form.fields["store"].queryset = vendor_stores
            form.fields["store"].initial = default_store

    return render(
        request,
        "marketplace/product_form.html",
        {
            "form": form,
            "stores": vendor_stores,
            "selected_store": default_store,
        },
    )


@login_required(login_url="login")
@permission_required(
    "marketplace.change_product", raise_exception=True
)
def product_edit(request, pk):
    """Edit a product belonging to any of vendor's stores."""
    stores = Store.objects.filter(owner=request.user)
    product = get_object_or_404(
        Product, pk=pk, store__in=stores
    )
    if request.method == "POST":
        form = ProductForm(
            request.POST, request.FILES, instance=product
        )
        if "store" in form.fields:
            form.fields["store"].queryset = stores
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.store.owner != request.user:
                raise PermissionDenied(
                    "You do not own this store."
                )
            updated.save()
            messages.success(
                request, "Product updated successfully."
            )
            return redirect("vendor_dashboard")
    else:
        form = ProductForm(instance=product)
        if "store" in form.fields:
            form.fields["store"].queryset = stores
    return render(
        request,
        "marketplace/product_form.html",
        {"form": form, "product": product},
    )


@login_required(login_url="login")
@permission_required(
    "marketplace.delete_product", raise_exception=True
)
def product_delete(request, pk):
    """Delete a product belonging to any of vendor's stores."""
    stores = Store.objects.filter(owner=request.user)
    product = get_object_or_404(
        Product, pk=pk, store__in=stores
    )
    if request.method == "POST":
        product.delete()
        messages.success(
            request, "Product deleted successfully."
        )
        return redirect("vendor_dashboard")
    return render(
        request,
        "marketplace/product_confirm_delete.html",
        {"product": product},
    )


@login_required(login_url="login")
def vendor_order_list(request):
    """Display incoming orders for all vendor stores."""
    stores = Store.objects.filter(owner=request.user)
    order_items = OrderItem.objects.filter(
        product__store__in=stores
    ).select_related("order", "product", "product__store")
    return render(
        request,
        "marketplace/vendor_order_list.html",
        {"order_items": order_items, "stores": stores},
    )


@login_required(login_url="login")
def vendor_order_detail(request, pk):
    """Display detailed view of a vendor order item."""
    stores = Store.objects.filter(owner=request.user)
    order_item = get_object_or_404(
        OrderItem, pk=pk, product__store__in=stores
    )
    return render(
        request,
        "marketplace/vendor_order_detail.html",
        {"order_item": order_item},
    )


@login_required(login_url="login")
def update_order_item_status(request, pk):
    """Handle tracking and status updates for order items."""
    stores = Store.objects.filter(owner=request.user)
    item = get_object_or_404(
        OrderItem, pk=pk, product__store__in=stores
    )

    if request.method == "POST":
        form = TrackingForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Tracking updated successfully."
            )
            return redirect("vendor_order_list")
    else:
        form = TrackingForm(instance=item)

    return render(
        request,
        "marketplace/update_tracking.html",
        {"form": form, "item": item},
    )


