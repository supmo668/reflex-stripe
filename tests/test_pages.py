"""Tests for page helper functions."""

import pytest


def test_add_checkout_page_callable():
    """add_checkout_page is importable and callable."""
    from reflex_stripe.pages import add_checkout_page

    assert callable(add_checkout_page)


def test_add_express_checkout_page_callable():
    """add_express_checkout_page is importable and callable."""
    from reflex_stripe.pages import add_express_checkout_page

    assert callable(add_express_checkout_page)


def test_checkout_return_page_callable():
    """checkout_return_page is importable and callable."""
    from reflex_stripe.pages import checkout_return_page

    assert callable(checkout_return_page)


def test_checkout_return_page_returns_component():
    """checkout_return_page() returns an rx.Component."""
    import reflex as rx
    from reflex_stripe.pages import checkout_return_page

    component = checkout_return_page()
    assert isinstance(component, rx.Component)


def test_add_checkout_page_asserts_route():
    """add_checkout_page raises AssertionError for invalid route."""
    from reflex_stripe.pages import add_checkout_page

    with pytest.raises(AssertionError, match="route must start with"):
        add_checkout_page(None, route="bad-route")  # type: ignore[arg-type]


def test_add_express_checkout_page_asserts_route():
    """add_express_checkout_page raises AssertionError for invalid route."""
    from reflex_stripe.pages import add_express_checkout_page

    with pytest.raises(AssertionError, match="route must start with"):
        add_express_checkout_page(None, route="bad-route")  # type: ignore[arg-type]
