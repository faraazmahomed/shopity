"""Views for the Marketplace application."""

import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LoginView
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
from .forms import ProductReviewForm, RegisterForm
from .models import (
    Order,
    OrderItem,
    Product,
    ProductReview,
    ResetToken,
    Store,
)
from .services import InsufficientStockError, process_checkout


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
        cart_data = [
            {
                "product_id": item["product"].pk,
                "quantity": item["quantity"],
            }
            for item in cart_obj
        ]

        try:
            order = process_checkout(
                buyer=request.user,
                cart_data=cart_data,
            )
        except InsufficientStockError as exc:
            messages.error(request, str(exc))
            return redirect("cart_detail")

        invoice_lines = []
        for order_item in order.items.select_related(
            "product"
        ):
            line_total = (
                order_item.price * order_item.quantity
            )
            invoice_lines.append(
                f"- {order_item.product.name} x "
                f"{order_item.quantity} "
                f"@ R{order_item.price} = R{line_total}"
            )

        invoice_body = (
            f"Dear {request.user.username},\n\n"
            f"Thank you for your order! Here is your "
            f"invoice for Order #{order.id}:\n\n"
            + "\n".join(invoice_lines)
            + f"\n\nTotal Amount: R{order.total_amount}\n\n"
            f"Status: Pending Processing\n\n"
            f"Thank you for shopping with Shopity!"
        )

        if request.user.email:
            send_mail(
                subject=(
                    f"Your Shopity Invoice - "
                    f"Order #{order.id}"
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
                f"You requested a password reset for "
                f"Shopity. Click the link below (valid for "
                f"1 hour):\n\n"
                f"{reset_url}\n\n"
                f"If you didn't request this, ignore this "
                f"email."
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
