"""Page helpers for one-liner checkout page creation.

Provides ``add_checkout_page()`` and ``add_express_checkout_page()`` functions
that compose checkout components, register API routes, and add return pages --
matching the ``add_sign_in_page()`` pattern from reflex-clerk-api.
"""

import os

import reflex as rx

from .embedded_checkout import embedded_checkout_session
from .express_checkout import ExpressCheckoutBridge
from .stripe_provider import stripe_provider
from .stripe_state import StripeState, register_stripe_api


def _register_api_safe(app) -> None:
    """Register Stripe API routes, ignoring if already registered."""
    try:
        register_stripe_api(app)
    except Exception:
        pass  # Routes already registered or app not ready


def checkout_return_page() -> rx.Component:
    """Return page component for Stripe payment completion.

    Displays payment status based on ``StripeState`` values populated by
    ``get_session_status`` or ``get_payment_status`` on_load handlers.

    Returns:
        An rx.Component showing payment result.
    """
    return rx.center(
        rx.vstack(
            rx.cond(
                StripeState.payment_status == "succeeded",
                rx.vstack(
                    rx.heading("Payment Successful!", size="6"),
                    rx.cond(
                        StripeState.customer_email != "",
                        rx.text(
                            "A confirmation email will be sent to ",
                            rx.text(
                                StripeState.customer_email,
                                weight="bold",
                                as_="span",
                            ),
                            ".",
                        ),
                        rx.text("Thank you for your purchase."),
                    ),
                    rx.link(
                        rx.button("Back to Home", size="3"),
                        href="/",
                    ),
                    align="center",
                    spacing="4",
                ),
                rx.cond(
                    StripeState.payment_status == "failed",
                    rx.vstack(
                        rx.heading("Payment Issue", size="6", color="red"),
                        rx.text(StripeState.error_message),
                        rx.link(
                            rx.button("Try Again", size="3"),
                            href="/checkout",
                        ),
                        align="center",
                        spacing="4",
                    ),
                    # Loading / idle state
                    rx.vstack(
                        rx.spinner(size="3"),
                        rx.text("Checking payment status..."),
                        align="center",
                        spacing="4",
                    ),
                ),
            ),
            align="center",
            spacing="4",
            width="100%",
            max_width="600px",
            padding="8",
        ),
        height="100vh",
    )


def add_checkout_page(
    app: rx.App,
    publishable_key: str | None = None,
    secret_key: str | None = None,
    line_items: list[dict] | None = None,
    route: str = "/checkout",
    return_route: str = "/checkout/return",
) -> None:
    """Add an Embedded Checkout page and return page to the app.

    This is the simplest way to add Stripe checkout to a Reflex app::

        import reflex_stripe as stripe

        app = rx.App()
        stripe.add_checkout_page(
            app,
            line_items=[{"price": "price_xxx", "quantity": 1}],
        )

    Args:
        app: The Reflex app instance.
        publishable_key: Stripe publishable key. Reads from
            ``STRIPE_PUBLISHABLE_KEY`` env var if not provided.
        secret_key: Stripe secret key. Reads from
            ``STRIPE_SECRET_KEY`` env var if not provided.
        line_items: List of Stripe line item dicts for the Checkout Session.
        route: Route for the checkout page.
        return_route: Route for the return/success page.
    """
    assert route.startswith("/"), f"route must start with '/': {route}"
    assert return_route.startswith("/"), f"return_route must start with '/': {return_route}"

    publishable_key = publishable_key or os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    secret_key = secret_key or os.environ.get("STRIPE_SECRET_KEY", "")

    _register_api_safe(app)

    checkout_component = rx.center(
        rx.vstack(
            embedded_checkout_session(
                publishable_key=publishable_key,
                secret_key=secret_key,
                line_items=line_items,
                return_url=return_route,
            ),
            align="center",
            spacing="4",
            width="100%",
            max_width="600px",
            padding="8",
        ),
        height="100vh",
    )
    app.add_page(checkout_component, route=route)
    app.add_page(
        checkout_return_page,
        route=return_route,
        on_load=StripeState.get_session_status,
    )


def add_express_checkout_page(
    app: rx.App,
    publishable_key: str | None = None,
    secret_key: str | None = None,
    amount: int = 1099,
    currency: str = "usd",
    route: str = "/express-checkout",
    return_route: str = "/express-checkout/complete",
) -> None:
    """Add an Express Checkout page and return page to the app.

    This creates a page with Apple Pay, Google Pay, and Link buttons::

        import reflex_stripe as stripe

        app = rx.App()
        stripe.add_express_checkout_page(app, amount=2000)

    Args:
        app: The Reflex app instance.
        publishable_key: Stripe publishable key. Reads from
            ``STRIPE_PUBLISHABLE_KEY`` env var if not provided.
        secret_key: Stripe secret key. Reads from
            ``STRIPE_SECRET_KEY`` env var if not provided.
        amount: Amount in smallest currency unit (e.g. cents).
        currency: Three-letter ISO currency code.
        route: Route for the checkout page.
        return_route: Route for the return/success page.
    """
    assert route.startswith("/"), f"route must start with '/': {route}"
    assert return_route.startswith("/"), f"return_route must start with '/': {return_route}"

    publishable_key = publishable_key or os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    secret_key = secret_key or os.environ.get("STRIPE_SECRET_KEY", "")

    _register_api_safe(app)

    checkout_component = rx.center(
        rx.vstack(
            stripe_provider(
                ExpressCheckoutBridge.create(return_url=return_route),
                publishable_key=publishable_key,
                secret_key=secret_key,
                mode="payment",
                amount=amount,
                currency=currency,
            ),
            align="center",
            spacing="4",
            width="100%",
            max_width="600px",
            padding="8",
        ),
        height="100vh",
    )
    app.add_page(checkout_component, route=route)
    app.add_page(
        checkout_return_page,
        route=return_route,
        on_load=StripeState.get_payment_status,
    )
