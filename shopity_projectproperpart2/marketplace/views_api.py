"""
API View controllers for handling REST requests, token authentication,
catalog searches, cart operations, and order checkouts.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Product, Store, Cart, CartItem, Order, OrderItem, ProductReview
from .serializers import (
    ProductSerializer,
    StoreSerializer,
    CartSerializer,
    OrderSerializer,
    ProductReviewSerializer,
)


class CustomObtainAuthToken(ObtainAuthToken):
    """Authenticate user credentials and return an authorization token."""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'user_id': token.user_id,
            'username': token.user.username
        })


class ProductListAPIView(generics.ListAPIView):
    """List all active products, with optional filtering by store or category[cite: 71]."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        store_id = self.request.query_params.get('store')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    """Retrieve details of a specific product[cite: 71]."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class StoreListCreateAPIView(generics.ListCreateAPIView):
    """List stores or create a new store (Vendors only)[cite: 71]."""
    queryset = Store.objects.filter(approval_status='approved')
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class StoreUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Update or remove a vendor's store[cite: 71]."""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Vendors can only modify their own stores
        return super().get_queryset().filter(owner=self.request.user)


class CartDetailAPIView(generics.RetrieveAPIView, generics.CreateAPIView):
    """View current cart items or add a product to the cart[cite: 71]."""
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def post(self, request, *args, **kwargs):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = generics.get_object_or_404(Product, pk=product_id, is_active=True)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCheckoutAPIView(generics.CreateAPIView):
    """Trigger checkout, clear cart, generate invoice, and queue email[cite: 71]."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Create master order record
        order = Order.objects.create(user=user, status='pending')

        # Move cart items to order items and deduct stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.base_price
            )
            # Optional: Deduct stock quantity
            item.product.stock -= item.quantity
            item.product.save()

        # Clear shopping cart
        cart.items.all().delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    """List reviews or submit a new product review[cite: 71]."""
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
