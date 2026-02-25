"""Tests for StripeState backend state and API routes."""

import os

import pytest


def test_stripe_state_defaults():
    """StripeState has correct default values."""
    from reflex_stripe.stripe_state import StripeState

    assert isinstance(StripeState._default_amount, int)
    assert isinstance(StripeState._default_currency, str)


def test_set_secret_key():
    """_set_secret_key stores key and resets client."""
    from reflex_stripe.stripe_state import StripeState

    StripeState._stripe_client = "dummy"  # type: ignore[assignment]
    StripeState._set_secret_key("sk_test_123")
    assert StripeState._secret_key == "sk_test_123"
    assert StripeState._stripe_client is None  # Forces re-init


def test_set_secret_key_empty_raises():
    """Empty secret_key raises ValueError."""
    from reflex_stripe.stripe_state import StripeState

    with pytest.raises(ValueError, match="must not be empty"):
        StripeState._set_secret_key("")


def test_set_defaults():
    """_set_defaults stores amount, currency, return_url."""
    from reflex_stripe.stripe_state import StripeState

    StripeState._set_defaults(amount=2000, currency="eur", return_url="/done")
    assert StripeState._default_amount == 2000
    assert StripeState._default_currency == "eur"
    assert StripeState._return_url == "/done"


def test_get_client_no_key_raises():
    """_get_client without key or env var raises ValueError."""
    from reflex_stripe.stripe_state import StripeState

    StripeState._secret_key = None
    StripeState._stripe_client = None
    env_backup = os.environ.pop("STRIPE_SECRET_KEY", None)
    try:
        with pytest.raises(ValueError, match="STRIPE_SECRET_KEY"):
            StripeState._get_client()
    finally:
        if env_backup:
            os.environ["STRIPE_SECRET_KEY"] = env_backup


def test_get_client_with_key():
    """_get_client creates a StripeClient when secret_key is set."""
    import stripe as stripe_lib
    from reflex_stripe.stripe_state import StripeState

    StripeState._stripe_client = None
    StripeState._set_secret_key("sk_test_456")
    client = StripeState._get_client()
    assert isinstance(client, stripe_lib.StripeClient)
    # Cleanup
    StripeState._stripe_client = None


def test_api_routes_exist():
    """get_stripe_api_routes returns routes with correct paths."""
    from reflex_stripe.stripe_state import get_stripe_api_routes

    routes = get_stripe_api_routes()
    assert len(routes) >= 1
    paths = [r.path for r in routes]
    assert "/api/stripe/create-payment-intent" in paths


def test_register_stripe_api_callable():
    """register_stripe_api is importable and callable."""
    from reflex_stripe.stripe_state import register_stripe_api

    assert callable(register_stripe_api)


def test_stripe_state_event_handlers():
    """StripeState has the expected event handler methods."""
    from reflex_stripe.stripe_state import StripeState

    assert hasattr(StripeState, "create_payment_intent")
    assert hasattr(StripeState, "handle_payment_success")
    assert hasattr(StripeState, "handle_payment_error")
    assert hasattr(StripeState, "reset_payment")
