"""
Marketplace URL routing configurations for Shopity Marketplace.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views, views_admin, views_vendor

urlpatterns = [
    # Vendor Product Management Routes (Using views_vendor)
    path(
        'vendor/products/',
        views_vendor.vendor_product_list,
        name='vendor_product_list',
    ),
    path(
        'vendor/products/add/',
        views_vendor.vendor_product_add,
        name='vendor_product_add',
    ),
    path(
        'vendor/products/<int:product_id>/edit/',
        views_vendor.vendor_product_edit,
        name='vendor_product_edit',
    ),
    path(
        'vendor/products/<int:product_id>/delete/',
        views_vendor.vendor_product_delete,
        name='vendor_product_delete',
    ),
    
    # Vendor Order Processing Routes
    path(
        'vendor/orders/',
        views_vendor.vendor_order_list,
        name='vendor_order_list',
    ),
    path(
        'vendor/orders/<int:pk>/',
        views_vendor.vendor_order_detail,
        name='vendor_order_detail',
    ),
    path(
        'vendor/order-item/<int:item_id>/update/',
        views_vendor.update_order_item_status,
        name='update_order_item_status',
    ),
    
    # Admin & Governance Routes
    path(
        'management/vendors/',
        views_admin.admin_vendor_list,
        name='admin_vendor_list',
    ),
    path(
        'management/vendor/<int:store_id>/approve/',
        views_admin.admin_approve_vendor,
        name='admin_approve_vendor',
    ),
    path(
        'management/vendor/<int:store_id>/reject/',
        views_admin.admin_reject_vendor,
        name='admin_reject_vendor',
    ),
    path(
        'management/moderation/',
        views_admin.admin_moderation_queue,
        name='admin_moderation_queue',
    ),
    path(
        'management/moderation/<int:pk>/dismiss/',
        views_admin.admin_dismiss_flag,
        name='admin_dismiss_flag',
    ),
    path(
        'management/moderation/<int:pk>/delist/',
        views_admin.admin_delist_product,
        name='admin_delist_product',
    ),
    
    # Authentication Routes (Using Custom Login View)
    path(
        'login/',
        views.RoleBasedLoginView.as_view(),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path('register/', views.register, name='register'),
    
    # Password Reset Routes
    path(
        'password-reset/',
        views.password_reset_request,
        name='password_reset_request',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='marketplace/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='marketplace/password_reset_confirm.html'
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='marketplace/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
    
    # Catalog & Public Routes
    path('', views.home, name='home'),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('reddit/', views.reddit_feed, name='reddit_feed'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path(
        'product/<int:product_id>/review/',
        views.add_product_review,
        name='add_product_review',
    ),
    
    # Shopping Cart & Checkout Routes
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/', views.cart_detail, name='cart'),  
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Product CRUD Routes
    path(
        'vendor/product/create/',
        views.product_create,
        name='product_create',
    ),
    path(
        'vendor/product/<int:pk>/edit/',
        views.product_edit,
        name='product_edit',
    ),
    path(
        'vendor/product/<int:pk>/delete/',
        views.product_delete,
        name='product_delete',
    ),
    
    # Dashboard & Store Management Routes
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/orders/', views.buyer_orders, name='buyer_orders'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/store/create/', views.store_create, name='store_create'),
    path('vendor/store/<int:pk>/', views.store_detail, name='store_detail'),
    path(
        'vendor/store/<int:pk>/edit/',
        views.store_edit,
        name='store_edit',
    ),
    path(
        'vendor/store/<int:pk>/delete/',
        views.store_delete,
        name='store_delete',
    ),
]
