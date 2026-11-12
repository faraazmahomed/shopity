from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Store, Product, ProductReview

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class StoreSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    approval_status = serializers.CharField(read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'logo', 'approval_status', 'owner', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'store', 'store_name', 'name', 'description', 'base_price', 'stock', 'is_active', 'created_at']
        read_only_fields = ['store']

class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'comment', 'is_verified', 'created_at']
        read_only_fields = ['user', 'is_verified']
