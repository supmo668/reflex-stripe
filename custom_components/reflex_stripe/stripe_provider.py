"""StripeProvider component wrapping Stripe's <Elements> provider."""

import reflex as rx

from .base import StripeBase
from .models import Appearance


class StripeProvider(StripeBase):
    """Wraps Stripe's <Elements> provider component.

    The Elements provider makes Stripe.js and Elements available to child components.
    It requires a `publishable_key` for Stripe initialization and accepts either
    deferred-intent mode props (mode, amount, currency) or a client_secret.

    See: https://docs.stripe.com/sdks/stripejs-react#elements-provider
    """

    tag = "Elements"

    # The stripe prop is injected as a raw JS variable reference via add_custom_code.
    # It is NOT a regular Python prop — loadStripe returns a Promise<Stripe>.

    # Options props (passed as `options` to Elements)
    # For deferred intent mode:
    mode: str | None = None
    """Payment mode: 'payment', 'subscription', or 'setup'."""

    amount: int | None = None
    """Amount in the smallest currency unit (e.g. cents). Required for deferred intent."""

    currency: str | None = None
    """Three-letter ISO currency code (e.g. 'usd'). Required for deferred intent."""

    # For client_secret mode:
    client_secret: str | None = None
    """The client_secret from a PaymentIntent or SetupIntent."""

    appearance: Appearance | None = None
    """Stripe Appearance API configuration for theming Elements."""

    locale: str | None = None
    """Locale for Elements (e.g. 'en', 'fr', 'auto')."""

    loader: str | None = None
    """Loading indicator: 'auto', 'always', or 'never'."""

    # Internal: publishable key stored for JS code generation
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
    def create(cls, *children, publishable_key: str = "", **props) -> "StripeProvider":
        """Create a StripeProvider component.

        Args:
            children: Child components (Elements, ExpressCheckout, etc.).
            publishable_key: Stripe publishable key (pk_test_... or pk_live_...).
            **props: Additional props passed to the Elements component.
        """
        component = super().create(*children, **props)
        component._publishable_key = publishable_key
        return component

    def _render(self, props=None):
        """Override render to inject stripe={stripePromise} as raw JS reference."""
        tag = super()._render(props)
        if self._publishable_key:
            tag.add_props(stripe=rx.Var("stripePromise"))
        # Build options object from individual props
        options = {}
        if self.mode is not None:
            options["mode"] = self.mode
        if self.amount is not None:
            options["amount"] = self.amount
        if self.currency is not None:
            options["currency"] = self.currency
        if self.client_secret is not None:
            options["clientSecret"] = self.client_secret
        if self.appearance is not None:
            options["appearance"] = self.appearance
        if self.locale is not None:
            options["locale"] = self.locale
        if self.loader is not None:
            options["loader"] = self.loader
        if options:
            tag.add_props(options=options)
        # Remove individual props that were merged into options
        tag.remove_props("mode", "amount", "currency", "client_secret",
                         "appearance", "locale", "loader")
        return tag


def stripe_provider(
    *children,
    publishable_key: str,
    secret_key: str | None = None,
    mode: str | None = None,
    amount: int | None = None,
    currency: str | None = None,
    client_secret: str | None = None,
    appearance: Appearance | None = None,
    return_url: str = "",
    **props,
) -> rx.Component:
    """Create a StripeProvider component (factory function).

    This is the recommended way to create a StripeProvider. It handles
    loadStripe initialization, StripeState configuration, and wraps
    children in the Elements provider.

    Args:
        children: Child components to render inside the provider.
        publishable_key: Stripe publishable key (pk_test_... or pk_live_...).
        secret_key: Stripe secret key for backend API calls (sk_test_... or sk_live_...).
            Stored server-side only in StripeState._secret_key (ClassVar).
        mode: Payment mode ('payment', 'subscription', 'setup').
        amount: Amount in smallest currency unit (cents).
        currency: Three-letter ISO currency code.
        client_secret: Client secret from PaymentIntent/SetupIntent.
        appearance: Stripe Appearance API configuration.
        return_url: URL to redirect to after payment. Used by ExpressCheckoutBridge.
        **props: Additional props passed to Elements.
    """
    from .stripe_state import StripeState

    if secret_key:
        StripeState._set_secret_key(secret_key)

    if mode and amount and currency:
        StripeState._set_defaults(
            amount=amount, currency=currency, return_url=return_url
        )

    return StripeProvider.create(
        *children,
        publishable_key=publishable_key,
        mode=mode,
        amount=amount,
        currency=currency,
        client_secret=client_secret,
        appearance=appearance,
        **props,
    )
