"""
Forms for the Marketplace application.

This module provides Django ModelForms and Forms for user registration,
vendor store creation, product management, and product reviews.
"""

from django import forms
from django.contrib.auth.models import User
from .models import Store, Product, ProductReview


class RegisterForm(forms.ModelForm):
    """
    Form for registering new users, allowing them to choose between
    a Buyer account or a Vendor account profile.
    """

    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
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
        """
        Ensure the provided email address is unique across the user base.

        Raises:
            ValidationError: If an account with this email already exists.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        """
        Validate that the password and confirmation password fields match.

        Raises:
            ValidationError: If passwords do not match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "The two password fields didn't match.")
        return cleaned_data


class StoreForm(forms.ModelForm):
    """
    Form for creating and editing vendor stores.
    """

    class Meta:
        model = Store
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    """
    Form for adding and editing products within a vendor store.
    """

    class Meta:
        model = Product
        fields = ['store', 'name', 'description', 'base_price', 'stock', 'image']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ProductReviewForm(forms.ModelForm):
    """
    Form for submitting product ratings and reviews.
    """

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
