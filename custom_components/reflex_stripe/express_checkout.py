"""ExpressCheckoutElement component for Apple Pay, Google Pay, Link, PayPal."""

import reflex as rx

from .base import StripeBase
from .models import ExpressCheckoutOptions


class ExpressCheckoutElement(StripeBase):
    """Wraps Stripe's <ExpressCheckoutElement>.

    Renders wallet-based payment buttons (Apple Pay, Google Pay, Link, PayPal)
    inside a StripeProvider. Must be a child of StripeProvider.

    See: https://docs.stripe.com/elements/express-checkout-element
    """

    tag = "ExpressCheckoutElement"

    options: ExpressCheckoutOptions | None = None
    """Configuration options for button appearance and behavior."""

    # Event handlers — these receive complex JS event objects.
    # The full JS bridge for elements.submit() + stripe.confirmPayment()
    # is implemented in Phase 3 (StripeState). For now, users can pass
    # custom event handlers.
    on_confirm: rx.EventHandler[lambda: []]
    on_click: rx.EventHandler[lambda: []]
    on_cancel: rx.EventHandler[lambda: []]
    on_ready: rx.EventHandler[lambda: []]
    on_shipping_address_change: rx.EventHandler[lambda: []]
    on_shipping_rate_change: rx.EventHandler[lambda: []]


express_checkout = ExpressCheckoutElement.create
