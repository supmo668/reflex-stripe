"""EmbeddedCheckout components for Stripe-hosted checkout in an iframe."""

import reflex as rx

from .base import StripeBase


class EmbeddedCheckoutProvider(rx.Component):
    """Guarded Embedded Checkout for a STATIC (reactive) client_secret.

    NOTE — inherits ``rx.Component`` (NOT ``StripeBase``) on purpose. This is
    a custom-code component: its ``tag`` (``GuardedEmbeddedCheckout``) is a
    function defined in ``add_custom_code``, not a real export of
    ``@stripe/react-stripe-js``. If it inherited ``StripeBase`` (which sets
    ``library = "@stripe/react-stripe-js"``), Reflex would auto-emit
    ``import {GuardedEmbeddedCheckout} from "@stripe/react-stripe-js"`` AND
    the local ``function GuardedEmbeddedCheckout(...)`` → "Identifier
    already declared" build error. The bridges (ExpressCheckoutBridge,
    EmbeddedCheckoutBridge) inherit ``rx.Component`` for the same reason;
    the real Stripe components are pulled in via ``add_imports``.

    Renders Stripe's ``<EmbeddedCheckoutProvider options={{clientSecret}}>``
    + ``<EmbeddedCheckout/>`` ONLY when ``client_secret`` is non-empty.

    2026-06-09 fix — this component previously emitted a bare
    ``<EmbeddedCheckoutProvider stripe={stripePromise}>`` with NO ``options``
    prop (the "Phase 4" options wiring was never done for the static-secret
    path; only ``EmbeddedCheckoutBridge``'s fetchClientSecret path got it).
    Stripe's React lib then destructured ``options.clientSecret`` on
    ``undefined`` → ``TypeError: Cannot read properties of undefined
    (reading 'clientSecret')`` on every mount.

    Two parts of the fix:
      1. Map ``client_secret`` → Stripe's required
         ``options={{ clientSecret }}``.
      2. GUARD: render nothing while ``client_secret`` is empty. Required
         because hosts mount this unconditionally (visibility toggled by a
         parent ``class_name`` per the Reflex rx.cond-reactivity gotcha),
         and Stripe THROWS if mounted with neither clientSecret nor
         fetchClientSecret. When the reactive ``client_secret`` later
         populates, React re-renders and mounts the real checkout.

    The Stripe instance (loadStripe) is injected via ``add_custom_code``,
    same as the other bridges.

    See: https://docs.stripe.com/checkout/embedded/quickstart
    """

    tag = "GuardedEmbeddedCheckout"

    # Reactive client secret from host state (e.g. a pre-created Checkout
    # Session's client_secret). Empty string => render nothing.
    client_secret: rx.Var[str]

    _publishable_key: str = ""

    def add_imports(self) -> rx.ImportDict:
        return {
            "@stripe/stripe-js": ["loadStripe"],
            "@stripe/react-stripe-js": [
                "EmbeddedCheckoutProvider",
                "EmbeddedCheckout",
            ],
        }

    def add_custom_code(self) -> list[str]:
        if not self._publishable_key:
            # Still define the symbol so JSX <GuardedEmbeddedCheckout/> resolves.
            return [
                """
function GuardedEmbeddedCheckout({ clientSecret }) {
  return (<div data-stripe-error="Missing publishable key" />);
}
"""
            ]
        return [
            f'const stripePromise = loadStripe("{self._publishable_key}");',
            """
function GuardedEmbeddedCheckout({ clientSecret }) {
  // GUARD: don't mount Stripe's EmbeddedCheckoutProvider until we have a
  // non-empty clientSecret — Stripe throws if given neither clientSecret
  // nor fetchClientSecret. The host mounts this unconditionally, so the
  // initial render has clientSecret="".
  //
  // 2026-06-09 fix #2 — the prop arrives as ``clientSecret`` (camelCase),
  // NOT ``client_secret``. Reflex serializes the Python ``client_secret:
  // rx.Var[str]`` field to a camelCase JSX prop by default (React
  // convention). Destructuring ``client_secret`` here read ``undefined``
  // every render, so ``!client_secret`` was permanently true and the
  // checkout never mounted ("no stripe page loads" on the CTA click). The
  // session was created fine; the guard silently swallowed it.
  if (!clientSecret) {
    return null;
  }
  return (
    <EmbeddedCheckoutProvider
      stripe={stripePromise}
      options={{ clientSecret }}
    >
      <EmbeddedCheckout />
    </EmbeddedCheckoutProvider>
  );
}
""",
        ]

    @classmethod
    def create(
        cls, *children, publishable_key: str = "", client_secret: str = "", **props
    ) -> "EmbeddedCheckoutProvider":
        """Create a guarded Embedded Checkout.

        Args:
            children: IGNORED for backward-compat with the old
                ``embedded_checkout_provider(embedded_checkout(), ...)``
                call shape — the guarded wrapper renders its own
                ``<EmbeddedCheckout/>`` internally, so a passed-in
                ``embedded_checkout()`` child would double-mount. Drop it.
            publishable_key: Stripe publishable key.
            client_secret: Reactive client secret (Var or str). Empty =>
                the wrapper renders nothing until it populates.
            **props: Additional props.
        """
        # Note: *children intentionally dropped (see docstring).
        component = super().create(client_secret=client_secret, **props)
        component._publishable_key = publishable_key
        return component


class EmbeddedCheckout(StripeBase):
    """Wraps Stripe's <EmbeddedCheckout> mount point.

    NOTE (2026-06-09): with the guarded ``EmbeddedCheckoutProvider`` above
    rendering its own ``<EmbeddedCheckout/>`` internally, passing this as a
    child is a no-op (the provider drops children). Retained for API
    back-compat and for advanced callers composing the raw Stripe tags
    directly.

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
            "$/utils/state": ["ReflexEvent", "getBackendURL"],
        }

    def add_custom_code(self) -> list[str]:
        from .stripe_state import StripeState

        state_name = StripeState.get_full_name()

        if not self._publishable_key:
            # Must still define the component so JSX <EmbeddedCheckoutBridge /> resolves
            return [
                """
function EmbeddedCheckoutBridge({ children, ...props }) {
  return (<div data-stripe-error="Missing publishable key">{children}</div>);
}
"""
            ]

        return [
            f'const stripePromise = loadStripe("{self._publishable_key}");',
            f"""
function EmbeddedCheckoutBridge({{ children, ...props }}) {{
  const [ addEvents ] = useContext(EventLoopContext);

  const fetchClientSecret = useCallback(async () => {{
    const apiUrl = getBackendURL().href.replace("/ping", "{self._api_url}");
    const res = await fetch(apiUrl, {{
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
    mode: str = "payment",
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
        mode: Checkout Session mode: 'payment', 'subscription', or 'setup'.
            Use 'subscription' for recurring Price IDs.
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
            mode=mode,
        )

    return EmbeddedCheckoutBridge.create(
        *children,
        publishable_key=publishable_key,
        **props,
    )
