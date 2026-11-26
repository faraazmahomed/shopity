"""Consolidated vendor views for stores, products, and orders."""

from django.contrib import messages
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

from .forms import (
    OrderStatusForm,
    ProductForm,
    StoreForm,
    TrackingForm,
)
from .models import OrderItem, Product, Store
from .utils import ensure_vendor_group_permissions


@login_required(login_url="login")
def vendor_dashboard(request):
    """Display vendor stores, active store, products, and orders."""
    ensure_vendor_group_permissions()
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

    products = (
        Product.objects.filter(store__in=stores)
        .select_related("store")
        .prefetch_related("orderitem_set__order")
    )
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
def vendor_product_list(request):
    """Display all products across the vendor's stores."""
    stores = Store.objects.filter(
        owner=request.user
    ).order_by("id")
    products = Product.objects.filter(
        store__in=stores
    ).select_related("store")
    return render(
        request,
        "marketplace/vendor_product_list.html",
        {"products": products, "stores": stores},
    )


@login_required(login_url="login")
@permission_required(
    "marketplace.add_product", raise_exception=True
)
def vendor_product_add(request):
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
            return redirect("vendor_product_list")
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
        "marketplace/vendor_product_form.html",
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
def vendor_product_edit(request, pk):
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
            return redirect("vendor_product_list")
    else:
        form = ProductForm(instance=product)
        if "store" in form.fields:
            form.fields["store"].queryset = stores

    return render(
        request,
        "marketplace/vendor_product_form.html",
        {"form": form, "product": product},
    )


@login_required(login_url="login")
@permission_required(
    "marketplace.delete_product", raise_exception=True
)
def vendor_product_delete(request, pk):
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
        return redirect("vendor_product_list")

    return render(
        request,
        "marketplace/vendor_product_confirm_delete.html",
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
    """Display and update status for a vendor order item."""
    stores = Store.objects.filter(owner=request.user)
    order_item = get_object_or_404(
        OrderItem, pk=pk, product__store__in=stores
    )
    order = order_item.order

    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Order status updated successfully."
            )
            return redirect(
                "vendor_order_detail", pk=order_item.pk
            )
    else:
        form = OrderStatusForm(instance=order)

    return render(
        request,
        "marketplace/vendor_order_detail.html",
        {
            "order_item": order_item,
            "order": order,
            "form": form,
        },
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


@login_required(login_url="login")
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
            messages.success(
                request, "Shipment marked as shipped."
            )
            return redirect("vendor_dashboard")
    else:
        form = TrackingForm(instance=item)

    return render(
        request,
        "marketplace/update_tracking.html",
        {"form": form, "item": item},
    )
