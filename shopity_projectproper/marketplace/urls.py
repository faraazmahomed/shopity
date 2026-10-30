from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, views_admin
from . import views_vendor

urlpatterns = [
    # Custom Admin & Moderation Routes (Placed at the top with a safe prefix to avoid /admin/ collisions)
    path('vendor/products/', views_vendor.vendor_product_list, name='vendor_product_list'),
    path('vendor/products/add/', views_vendor.vendor_product_add, name='vendor_product_add'),
    path('vendor/products/<int:product_id>/edit/', views_vendor.vendor_product_edit, name='vendor_product_edit'),
    path('vendor/products/<int:product_id>/delete/', views_vendor.vendor_product_delete, name='vendor_product_delete'),

    # Vendor Order Processing Routes
    path('vendor/orders/', views_vendor.vendor_order_list, name='vendor_order_list'),
    path('vendor/orders/<int:order_item_id>/', views_vendor.vendor_order_detail, name='vendor_order_detail'),

    path('management/vendors/', views_admin.admin_vendor_list, name='admin_vendor_list'),
    path('management/vendor/<int:store_id>/approve/', views_admin.admin_approve_vendor, name='admin_approve_vendor'),
    path('management/vendor/<int:store_id>/reject/', views_admin.admin_reject_vendor, name='admin_reject_vendor'),
    path('management/moderation/', views_admin.admin_moderation_queue, name='admin_moderation_queue'),
    path('management/moderation/<int:product_id>/dismiss/', views_admin.admin_dismiss_flag, name='admin_dismiss_flag'),
    path('management/moderation/<int:product_id>/delist/', views_admin.admin_delist_product, name='admin_delist_product'),
# Vendor Inventory Management Routes
    path('vendor/products/', views_vendor.vendor_product_list, name='vendor_product_list'),
    path('vendor/products/add/', views_vendor.vendor_product_add, name='vendor_product_add'),
    path('vendor/products/<int:product_id>/edit/', views_vendor.vendor_product_edit, name='vendor_product_edit'),
    path('vendor/products/<int:product_id>/delete/', views_vendor.vendor_product_delete, name='vendor_product_delete'),

    # Built-in Authentication & Fallback Login Routes
    path('login/', auth_views.LoginView.as_view(template_name='marketplace/login.html'), name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='marketplace/login.html')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Public & Catalog Routes
    path('', views.home, name='home'),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),

    # Shopping Cart & Checkout Routes
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),

    # Dashboards & Store Management
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/store/create/', views.store_create, name='store_create'),
    path('vendor/store/<int:pk>/', views.store_detail, name='store_detail'),
    path('vendor/store/<int:pk>/edit/', views.store_edit, name='store_edit'),
    path('vendor/store/<int:pk>/delete/', views.store_delete, name='store_delete'),

    # Product CRUD
    path('vendor/product/create/', views.product_create, name='product_create'),
    path('vendor/product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('vendor/product/<int:pk>/delete/', views.product_delete, name='product_delete'),

# Vendor Product Management Routes...

    path('vendor/products/', views_vendor.vendor_order_list, name='vendor_product_list'), # (Keep existing product URLs)

    # Vendor Order Processing Routes
    path('vendor/orders/', views_vendor.vendor_order_list, name='vendor_order_list'),
    path('vendor/orders/<int:order_item_id>/', views_vendor.vendor_order_detail, name='vendor_order_detail'),

    # Reviews & Order Status
    path('product/<int:product_id>/review/', views.add_product_review, name='add_product_review'),
    path('vendor/order-item/<int:item_id>/update/', views.update_order_item_status, name='update_order_item_status'),
]
