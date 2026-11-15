"""
Forms for the Marketplace application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Product, ProductReview, Store, OrderItem


class RegisterForm(UserCreationForm):
    """User registration form supporting role selection for Buyers and Vendors."""

    role = forms.ChoiceField(
        choices=[("buyer", "Buyer"), ("vendor", "Vendor")],
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "role")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            role = self.cleaned_data.get("role")
            group_name = "Vendors" if role == "vendor" else "Buyers"
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
        return user


class StoreForm(forms.ModelForm):
    """Form for creating and updating vendor stores."""

    class Meta:
        model = Store
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class ProductForm(forms.ModelForm):
    """Form for creating and updating store products."""

    class Meta:
        model = Product
        fields = (
            "store",
            "name",
            "description",
            "base_price",
            "stock",
            "image",
            "is_active",
        )
        widgets = {
            "store": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "base_price": forms.NumberInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProductReviewForm(forms.ModelForm):
    """Form for submitting product ratings and review comments."""

    class Meta:
        model = ProductReview
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class TrackingForm(forms.ModelForm):
    """Form for updating order item fulfillment status and carrier information."""

    class Meta:
        model = OrderItem
        fields = ("item_status", "carrier_name", "tracking_number")
        widgets = {
            "item_status": forms.Select(attrs={"class": "form-control"}),
            "carrier_name": forms.TextInput(attrs={"class": "form-control"}),
            "tracking_number": forms.TextInput(attrs={"class": "form-control"}),
        }
