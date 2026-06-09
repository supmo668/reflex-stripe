"""Smoke test: verify the package is importable and all exports exist."""


def test_import():
    import reflex_stripe

    assert hasattr(reflex_stripe, "__version__")
    assert reflex_stripe.__version__  # non-empty version string


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
        "EmbeddedCheckoutBridge",
        "EmbeddedCheckoutProvider",
        "ExpressCheckoutBridge",
        "ExpressCheckoutElement",
        "ExpressCheckoutLayout",
        "ExpressCheckoutOptions",
        "PaymentMethods",
        "StripeBase",
        "StripeProvider",
        "StripeState",
        "Variables",
        "add_checkout_page",
        "add_express_checkout_page",
        "checkout_return_page",
        "embedded_checkout",
        "embedded_checkout_bridge",
        "embedded_checkout_provider",
        "embedded_checkout_session",
        "express_checkout",
        "express_checkout_bridge",
        "get_stripe_api_routes",
        "register_stripe_api",
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

    # 2026-06-09: EmbeddedCheckoutProvider is now a guarded custom wrapper
    # (tag "GuardedEmbeddedCheckout") that maps client_secret →
    # options={{clientSecret}} and refuses to mount Stripe's provider with
    # an empty secret. Previously it was a bare passthrough to Stripe's
    # <EmbeddedCheckoutProvider> with NO options wiring, which crashed with
    # "Cannot read properties of undefined (reading 'clientSecret')".
    assert EmbeddedCheckoutProvider.tag == "GuardedEmbeddedCheckout"
    assert EmbeddedCheckout.tag == "EmbeddedCheckout"


def test_embedded_checkout_provider_has_client_secret_var():
    """The guarded provider must expose a reactive client_secret Var so the
    host can bind state (e.g. BillingState.embedded_client_secret) and the
    wrapper can gate mounting + build options={{clientSecret}}."""
    from reflex_stripe.embedded_checkout import EmbeddedCheckoutProvider

    assert "client_secret" in EmbeddedCheckoutProvider.get_fields()


def test_guarded_checkout_destructures_camelcase_prop():
    """The custom-code wrapper MUST destructure ``clientSecret`` (camelCase),
    NOT ``client_secret``.

    2026-06-09 regression: Reflex serializes the Python ``client_secret:
    rx.Var[str]`` field to a camelCase ``clientSecret`` JSX prop (React
    convention). The wrapper originally destructured ``client_secret``, so it
    read ``undefined`` every render → the ``if (!clientSecret) return null``
    guard was permanently true → Stripe's EmbeddedCheckoutProvider never
    mounted ("no stripe page loads" on the upgrade CTA). The session was
    created fine; the prop-name mismatch silently swallowed it.
    """
    from reflex_stripe.embedded_checkout import EmbeddedCheckoutProvider

    comp = EmbeddedCheckoutProvider.create(
        publishable_key="pk_test_dummy", client_secret=""
    )
    code = "\n".join(comp.add_custom_code())
    assert "function GuardedEmbeddedCheckout({ clientSecret })" in code
    assert "{ client_secret }" not in code
    assert "if (!clientSecret)" in code
    assert "options={{ clientSecret }}" in code


def test_express_checkout_bridge_class():
    from reflex_stripe.express_checkout import ExpressCheckoutBridge

    assert ExpressCheckoutBridge.tag == "ExpressCheckoutBridge"


def test_embedded_checkout_bridge_class():
    from reflex_stripe.embedded_checkout import EmbeddedCheckoutBridge

    assert EmbeddedCheckoutBridge.tag == "EmbeddedCheckoutBridge"


def test_embedded_checkout_session_factory():
    from reflex_stripe.embedded_checkout import embedded_checkout_session

    assert callable(embedded_checkout_session)


def test_stripe_state_class():
    from reflex_stripe.stripe_state import StripeState

    assert issubclass(StripeState, __import__("reflex").State)
