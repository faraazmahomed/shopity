"""Forms for the Marketplace application."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User

from .models import (
    Order,
    OrderItem,
    Product,
    ProductReview,
    Store,
)


class RegisterForm(UserCreationForm):
    """Registration form supporting Buyer and Vendor roles."""

    role = forms.ChoiceField(
        choices=[("buyer", "Buyer"), ("vendor", "Vendor")],
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(required=True)

    class Meta:
        """Metadata configuration for RegisterForm."""

        model = User
        fields = ("username", "email", "role")

    def save(self, commit=True):
        """Save user and assign to Buyers or Vendors group."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            role = self.cleaned_data.get("role")
            group_name = (
                "Vendors" if role == "vendor" else "Buyers"
            )
            group, _ = Group.objects.get_or_create(
                name=group_name
            )
            user.groups.add(group)
        return user


class StoreForm(forms.ModelForm):
    """Form for creating and updating vendor stores."""

    class Meta:
        """Metadata configuration for StoreForm."""

        model = Store
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }


class ProductForm(forms.ModelForm):
    """Form for creating and updating store products."""

    class Meta:
        """Metadata configuration for ProductForm."""

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
            "store": forms.Select(
                attrs={"class": "form-control"}
            ),
            "name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "base_price": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "stock": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control-file"}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }


class ProductReviewForm(forms.ModelForm):
    """Form for submitting product ratings and reviews."""

    class Meta:
        """Metadata configuration for ProductReviewForm."""

        model = ProductReview
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(
                attrs={"class": "form-control"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


class TrackingForm(forms.ModelForm):
    """Form for updating item fulfillment and tracking details."""

    class Meta:
        """Metadata configuration for TrackingForm."""

        model = OrderItem
        fields = (
            "item_status",
            "carrier_name",
            "tracking_number",
        )
        widgets = {
            "item_status": forms.Select(
                attrs={"class": "form-select"}
            ),
            "carrier_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "tracking_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }


class OrderStatusForm(forms.ModelForm):
    """Form for updating the parent Order status."""

    class Meta:
        """Metadata configuration for OrderStatusForm."""

        model = Order
        fields = ("status",)
        widgets = {
            "status": forms.Select(
                attrs={"class": "form-select"}
            ),
        }
