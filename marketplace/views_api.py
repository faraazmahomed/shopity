from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Store, Product, ProductReview
from .serializers import StoreSerializer, ProductSerializer, ProductReviewSerializer

class IsVendorAndOwner(permissions.BasePermission):
    """
    Custom permission to ensure:
    - Only users in the 'Vendors' group (or staff) can create/edit resources.
    - Vendors can only modify stores and products they personally own.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.groups.filter(name='Vendors').exists() or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Staff can modify anything, but vendors can only modify their own store/products
        if request.user.is_staff:
            return True
            
        if isinstance(obj, Store):
            return obj.owner == request.user
        elif isinstance(obj, Product):
            return obj.store.owner == request.user
            
        return False

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsVendorAndOwner]

    def get_queryset(self):
        queryset = Store.objects.all()
        vendor_id = self.request.query_params.get('vendor_id')
        if vendor_id:
            queryset = queryset.filter(owner_id=vendor_id)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if Store.objects.filter(owner=user).exists():
            raise PermissionDenied("You already own a store.")
        serializer.save(owner=user, approval_status='pending')

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(store__approval_status='approved')
    serializer_class = ProductSerializer
    permission_classes = [IsVendorAndOwner]

    def get_queryset(self):
        queryset = Product.objects.all()
        store_id = self.request.query_params.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id, store__approval_status='approved')
        else:
            queryset = queryset.filter(store__approval_status='approved')
        return queryset

    def perform_create(self, serializer):
        store = Store.objects.filter(owner=self.request.user).first()
        if not store:
            raise PermissionDenied("You must create a store before adding products.")
        serializer.save(store=store)

class ProductReviewViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        return ProductReview.objects.filter(product_id=product_id)

class VendorListViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint to list vendors and the stores listed under each vendor."""
    queryset = Store.objects.filter(approval_status='approved')
    serializer_class = StoreSerializer
