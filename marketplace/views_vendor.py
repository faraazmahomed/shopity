"""Vendor views for managing store products, orders, and tracking."""

from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import ProductForm, TrackingForm
from .models import OrderItem, Product, Store
from .utils import ensure_vendor_group_permissions


@login_required
def vendor_product_list(request):
    """Display all products across the vendor's stores."""
    stores = Store.objects.filter(owner=request.user)
    products = Product.objects.filter(store__in=stores)
    return render(
        request,
        "marketplace/vendor_product_list.html",
        {"products": products, "stores": stores},
    )


@login_required
@permission_required(
    "marketplace.add_product", raise_exception=True
)
def vendor_product_add(request):
    """Create a new product within a vendor-owned store."""
    owned_stores = Store.objects.filter(owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if "store" in form.fields:
            form.fields["store"].queryset = owned_stores
        if form.is_valid():
            product = form.save(commit=False)
            if product.store.owner == request.user:
                product.save()
                return redirect("vendor_product_list")
            raise PermissionDenied(
                "You do not own this store."
            )
    else:
        form = ProductForm()
        if "store" in form.fields:
            form.fields["store"].queryset = owned_stores

    return render(
        request,
        "marketplace/vendor_product_form.html",
        {"form": form},
    )


@login_required
@permission_required(
    "marketplace.change_product", raise_exception=True
)
def vendor_product_edit(request, pk):
    """Edit an existing product within a vendor's store."""
    product = get_object_or_404(Product, pk=pk)

    if product.store.owner != request.user:
        raise PermissionDenied(
            "You do not have permission to edit this product."
        )

    owned_stores = Store.objects.filter(owner=request.user)
    if request.method == "POST":
        form = ProductForm(
            request.POST, request.FILES, instance=product
        )
        if "store" in form.fields:
            form.fields["store"].queryset = owned_stores
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.store.owner != request.user:
                raise PermissionDenied(
                    "You do not own this store."
                )
            updated.save()
            return redirect("vendor_product_list")
    else:
        form = ProductForm(instance=product)
        if "store" in form.fields:
            form.fields["store"].queryset = owned_stores

    return render(
        request,
        "marketplace/vendor_product_form.html",
        {"form": form, "product": product},
    )


@login_required
@permission_required(
    "marketplace.delete_product", raise_exception=True
)
def vendor_product_delete(request, pk):
    """Delete an existing product within a vendor's store."""
    product = get_object_or_404(Product, pk=pk)

    if product.store.owner != request.user:
        raise PermissionDenied(
            "You do not have permission to delete this product."
        )

    if request.method == "POST":
        product.delete()
        return redirect("vendor_product_list")

    return render(
        request,
        "marketplace/vendor_product_confirm_delete.html",
        {"product": product},
    )


@login_required
def vendor_order_list(request):
    """Display order items for the logged-in vendor's stores."""
    stores = Store.objects.filter(owner=request.user)
    order_items = OrderItem.objects.filter(
        product__store__in=stores
    ).select_related("order", "product", "product__store")
    return render(
        request,
        "marketplace/vendor_order_list.html",
        {"order_items": order_items, "stores": stores},
    )


@login_required
def vendor_order_detail(request, pk):
    """Display details for a specific vendor order item."""
    stores = Store.objects.filter(owner=request.user)
    order_item = get_object_or_404(
        OrderItem, pk=pk, product__store__in=stores
    )
    return render(
        request,
        "marketplace/vendor_order_detail.html",
        {"order_item": order_item},
    )


@login_required
def update_order_item_status(request, pk):
    """Update status and tracking for a specific order item."""
    stores = Store.objects.filter(owner=request.user)
    item = get_object_or_404(
        OrderItem, pk=pk, product__store__in=stores
    )

    if request.method == "POST":
        form = TrackingForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("vendor_order_list")
    else:
        form = TrackingForm(instance=item)

    return render(
        request,
        "marketplace/update_tracking.html",
        {"form": form, "item": item},
    )


@login_required
def vendor_dashboard(request):
    """Display vendor overview with stores, products, and orders."""
    ensure_vendor_group_permissions()
    stores = Store.objects.filter(
        owner=request.user
    ).order_by("id")
    products = (
        Product.objects.filter(store__in=stores)
        .select_related("store")
        .prefetch_related("orderitem_set__order")
    )
    order_items = OrderItem.objects.filter(
        product__store__in=stores
    ).select_related("order", "product")
    return render(
        request,
        "marketplace/vendor_dashboard.html",
        {
            "stores": stores,
            "products": products,
            "order_items": order_items,
        },
    )


@login_required
def update_shipment_tracking(request, item_id):
    """Update tracking details and mark an order item shipped."""
    stores = Store.objects.filter(owner=request.user)
    item = get_object_or_404(
        OrderItem, id=item_id, product__store__in=stores
    )

    if request.method == "POST":
        form = TrackingForm(request.POST, instance=item)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.item_status = "SHIPPED"
            shipment.save()
            return redirect("vendor_dashboard")
    else:
        form = TrackingForm(instance=item)

    return render(
        request,
        "marketplace/update_tracking.html",
        {"form": form, "item": item},
    )
