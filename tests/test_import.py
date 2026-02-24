"""Smoke test: verify the package is importable and all exports exist."""


def test_import():
    import reflex_stripe

    assert hasattr(reflex_stripe, "__version__")
    assert reflex_stripe.__version__ == "0.1.0"


def test_base_class():
    from reflex_stripe.base import StripeBase

    assert StripeBase.library == "@stripe/react-stripe-js@^5.6.0"


def test_all_exports():
    import reflex_stripe

    expected = [
        "Appearance",
        "ButtonTheme",
        "ButtonType",
        "EmbeddedCheckout",
        "EmbeddedCheckoutProvider",
        "ExpressCheckoutElement",
        "ExpressCheckoutLayout",
        "ExpressCheckoutOptions",
        "PaymentMethods",
        "StripeBase",
        "StripeProvider",
        "Variables",
        "embedded_checkout",
        "embedded_checkout_provider",
        "express_checkout",
        "stripe_provider",
    ]
    for name in expected:
        assert hasattr(reflex_stripe, name), f"Missing export: {name}"


def test_stripe_provider_class():
    from reflex_stripe.stripe_provider import StripeProvider

    assert StripeProvider.tag == "Elements"


def test_express_checkout_class():
    from reflex_stripe.express_checkout import ExpressCheckoutElement

    assert ExpressCheckoutElement.tag == "ExpressCheckoutElement"


def test_embedded_checkout_classes():
    from reflex_stripe.embedded_checkout import (
        EmbeddedCheckout,
        EmbeddedCheckoutProvider,
    )

    assert EmbeddedCheckoutProvider.tag == "EmbeddedCheckoutProvider"
    assert EmbeddedCheckout.tag == "EmbeddedCheckout"
