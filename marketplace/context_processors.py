"""
Module: context_processors.py
Description: Module-level docstring.
"""

# context_processors.py
from .cart import Cart


def cart_context(request):
    return {"cart": Cart(request)}
