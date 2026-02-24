"""Smoke test: verify the package is importable."""


def test_import():
    import reflex_stripe

    assert hasattr(reflex_stripe, "__version__")
    assert reflex_stripe.__version__ == "0.1.0"


def test_base_class():
    from reflex_stripe.base import StripeBase

    assert StripeBase.library == "@stripe/react-stripe-js@^5.6.0"
