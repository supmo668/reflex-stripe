"""EmbeddedCheckout components for Stripe-hosted checkout in an iframe."""

import reflex as rx

from .base import StripeBase


class EmbeddedCheckoutProvider(StripeBase):
    """Wraps Stripe's <EmbeddedCheckoutProvider>.

    Provides the Embedded Checkout context to child components.
    Requires either a client_secret or fetchClientSecret callback,
    which will be handled via JS bridge in Phase 4.

    Must be used with a Stripe instance (from loadStripe).

    See: https://docs.stripe.com/checkout/embedded/quickstart
    """

    tag = "EmbeddedCheckoutProvider"

    # The stripe prop is injected as raw JS via add_custom_code, similar to StripeProvider.
    # The options (clientSecret or fetchClientSecret) will be handled in Phase 4.

    _publishable_key: str = ""

    def add_imports(self) -> rx.ImportDict:
        return {"@stripe/stripe-js": ["loadStripe"]}

    def add_custom_code(self) -> list[str]:
        if not self._publishable_key:
            return []
        return [
            f'const stripePromise = loadStripe("{self._publishable_key}");'
        ]

    @classmethod
    def create(cls, *children, publishable_key: str = "", **props) -> "EmbeddedCheckoutProvider":
        """Create an EmbeddedCheckoutProvider.

        Args:
            children: Child components (must include EmbeddedCheckout).
            publishable_key: Stripe publishable key.
            **props: Additional props.
        """
        component = super().create(*children, **props)
        component._publishable_key = publishable_key
        return component

    def _render(self):
        """Override render to inject stripe={stripePromise} as raw JS reference."""
        tag = super()._render()
        if self._publishable_key:
            tag.add_props(stripe=rx.Var("stripePromise"))
        return tag


class EmbeddedCheckout(StripeBase):
    """Wraps Stripe's <EmbeddedCheckout> mount point.

    Must be a child of EmbeddedCheckoutProvider. Renders the Stripe-hosted
    checkout form inside an iframe.

    See: https://docs.stripe.com/checkout/embedded/quickstart
    """

    tag = "EmbeddedCheckout"


embedded_checkout_provider = EmbeddedCheckoutProvider.create
embedded_checkout = EmbeddedCheckout.create
