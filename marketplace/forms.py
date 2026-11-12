"""
Forms for the Marketplace application.

This module provides Django ModelForms and Forms for user registration,
vendor store creation, product management, and product reviews.
"""

from django import forms
from django.contrib.auth.models import Group, Permission, User
from .models import Product, ProductReview, Store, OrderItem


class RegisterForm(forms.ModelForm):
    """
    Form for registering new users, allowing them to choose between
    a Buyer account or a Vendor account profile, assigning groups and permissions.
    """

    ROLE_CHOICES = (
        ('Vendor', 'Vendor'),
        ('Buyer', 'Buyer'),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter a secure password.",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password",
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label="Register as",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Choose whether you want to buy items or manage your own store as a vendor.",
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        """Ensure the provided email address is unique across the user base."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists.")
        return email

    def clean(self):
        """Validate that password and confirm_password match."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "The two password fields didn't match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        role = self.cleaned_data.get("role")

        if commit:
            user.save()
            if role == 'Vendor':
                vendor_group, _ = Group.objects.get_or_create(name='Vendors')
                user.groups.add(vendor_group)
                for perm_code in ['add_product', 'change_product', 'delete_product']:
                    try:
                        perm = Permission.objects.get(
                            codename=perm_code, content_type__app_label='marketplace')
                        user.user_permissions.add(perm)
                    except Permission.DoesNotExist:
                        pass
            else:
                buyer_group, _ = Group.objects.get_or_create(name='Buyers')
                user.groups.add(buyer_group)
        return user


class StoreForm(forms.ModelForm):
    """Form for creating and editing vendor stores."""

    class Meta:
        model = Store
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ProductForm(forms.ModelForm):
    """Form for adding and editing products within a vendor store."""

    class Meta:
        model = Product
        fields = ['store', 'name', 'description', 'base_price', 'stock', 'image', 'is_active']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductReviewForm(forms.ModelForm):
    """Form for submitting product ratings and reviews."""

    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, str(i)) for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TrackingForm(forms.ModelForm):
    """Form for updating fulfillment status and tracking information."""

    class Meta:
        model = OrderItem
        fields = ['item_status', 'carrier_name', 'tracking_number']
        widgets = {
            'item_status': forms.Select(attrs={'class': 'form-select'}),
            'carrier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., DHL, FedEx'}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tracking number'}),
        }
