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


class EmbeddedCheckoutBridge(rx.Component):
    """JS bridge that handles the Embedded Checkout fetchClientSecret flow.

    Like ExpressCheckoutBridge, this is a custom React component that:
    1. Initializes loadStripe with the publishable key
    2. Defines fetchClientSecret callback calling /api/stripe/create-checkout-session
    3. Renders <EmbeddedCheckoutProvider> + <EmbeddedCheckout> with the callback
    4. Dispatches onComplete to StripeState.handle_payment_success

    Usage::

        stripe.embedded_checkout_session(
            publishable_key="pk_test_...",
            secret_key="sk_test_...",
            line_items=[{"price": "price_xxx", "quantity": 1}],
            return_url="/checkout/return",
        )
    """

    tag = "EmbeddedCheckoutBridge"

    # Internal configuration (not React props)
    _publishable_key: str = ""
    _api_url: str = "/api/stripe/create-checkout-session"

    def add_imports(self) -> rx.ImportDict:
        return {
            "@stripe/stripe-js": ["loadStripe"],
            "@stripe/react-stripe-js": [
                "EmbeddedCheckoutProvider",
                "EmbeddedCheckout",
            ],
            "react": ["useCallback", "useContext"],
            "$/utils/context": ["EventLoopContext"],
            "$/utils/state": ["ReflexEvent"],
        }

    def add_custom_code(self) -> list[str]:
        from .stripe_state import StripeState

        state_name = StripeState.get_full_name()

        if not self._publishable_key:
            return []

        return [
            f'const stripePromise = loadStripe("{self._publishable_key}");',
            f"""
function EmbeddedCheckoutBridge({{ children, ...props }}) {{
  const [ addEvents ] = useContext(EventLoopContext);

  const fetchClientSecret = useCallback(async () => {{
    const res = await fetch("{self._api_url}", {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
    }});
    const data = await res.json();
    if (data.error) {{
      if (addEvents) {{
        addEvents([ReflexEvent("{state_name}.handle_payment_error",
          {{error_message: data.error}})]);
      }}
      throw new Error(data.error);
    }}
    return data.client_secret;
  }}, [addEvents]);

  const onComplete = useCallback(() => {{
    if (addEvents) {{
      addEvents([ReflexEvent("{state_name}.handle_payment_success",
        {{}})]);
    }}
  }}, [addEvents]);

  return (
    <EmbeddedCheckoutProvider
      stripe={{stripePromise}}
      options={{{{ fetchClientSecret, onComplete }}}}
    >
      <EmbeddedCheckout />
      {{children}}
    </EmbeddedCheckoutProvider>
  );
}}
""",
        ]

    @classmethod
    def create(
        cls,
        *children,
        publishable_key: str = "",
        api_url: str = "/api/stripe/create-checkout-session",
        **props,
    ) -> "EmbeddedCheckoutBridge":
        """Create an EmbeddedCheckoutBridge component.

        Args:
            children: Optional child components.
            publishable_key: Stripe publishable key (pk_test_... or pk_live_...).
            api_url: Backend API URL for Checkout Session creation.
                Defaults to /api/stripe/create-checkout-session.
            **props: Additional props.
        """
        component = super().create(*children, **props)
        component._publishable_key = publishable_key
        component._api_url = api_url
        return component


embedded_checkout_bridge = EmbeddedCheckoutBridge.create


def embedded_checkout_session(
    *children,
    publishable_key: str,
    secret_key: str | None = None,
    line_items: list[dict] | None = None,
    return_url: str = "/checkout/return",
    **props,
) -> rx.Component:
    """Create an Embedded Checkout component (factory function).

    This is the recommended way to add Stripe Embedded Checkout to your app.
    It handles loadStripe initialization, StripeState configuration, and
    wraps the checkout form in EmbeddedCheckoutBridge.

    Args:
        children: Optional child components rendered inside the provider.
        publishable_key: Stripe publishable key (pk_test_... or pk_live_...).
        secret_key: Stripe secret key for backend API calls (sk_test_... or sk_live_...).
            Stored server-side only in StripeState._secret_key (ClassVar).
        line_items: List of Stripe line item dicts for the Checkout Session.
            Example: [{"price": "price_xxx", "quantity": 1}]
            or [{"price_data": {"currency": "usd", "product_data": {"name": "T-shirt"},
                "unit_amount": 2000}, "quantity": 1}]
        return_url: Path to redirect to after payment (e.g. "/checkout/return").
        **props: Additional props passed to EmbeddedCheckoutBridge.
    """
    from .stripe_state import StripeState

    if secret_key:
        StripeState._set_secret_key(secret_key)

    if line_items is not None:
        StripeState._set_checkout_defaults(
            line_items=line_items,
            return_url=return_url,
        )

    return EmbeddedCheckoutBridge.create(
        *children,
        publishable_key=publishable_key,
        **props,
    )
