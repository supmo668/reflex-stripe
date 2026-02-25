"""ExpressCheckoutElement component and ExpressCheckoutBridge JS bridge."""

import reflex as rx

from .base import StripeBase
from .models import ExpressCheckoutOptions


class ExpressCheckoutElement(StripeBase):
    """Wraps Stripe's <ExpressCheckoutElement>.

    Renders wallet-based payment buttons (Apple Pay, Google Pay, Link, PayPal)
    inside a StripeProvider. Must be a child of StripeProvider.

    For automatic payment flow handling, use ExpressCheckoutBridge instead,
    which wraps this component with the full onConfirm → confirmPayment flow.

    See: https://docs.stripe.com/elements/express-checkout-element
    """

    tag = "ExpressCheckoutElement"

    options: ExpressCheckoutOptions | None = None
    """Configuration options for button appearance and behavior."""

    # Event handlers — these receive complex JS event objects.
    # For the full automated flow, use ExpressCheckoutBridge instead.
    on_confirm: rx.EventHandler[lambda: []]
    on_click: rx.EventHandler[lambda: []]
    on_cancel: rx.EventHandler[lambda: []]
    on_ready: rx.EventHandler[lambda: []]
    on_shipping_address_change: rx.EventHandler[lambda: []]
    on_shipping_rate_change: rx.EventHandler[lambda: []]


express_checkout = ExpressCheckoutElement.create


class ExpressCheckoutBridge(rx.Component):
    """JS bridge that handles the Express Checkout onConfirm payment flow.

    Like ClerkSessionSynchronizer in reflex-clerk-api, this is a custom React
    component that uses hooks (useStripe, useElements) to orchestrate the
    deferred-intent payment confirmation and dispatches events to StripeState
    via ReflexEvent.

    The flow:
    1. Renders <ExpressCheckoutElement> with an automatic onConfirm handler
    2. onConfirm: elements.submit() validates payment data
    3. fetch(/api/stripe/create-payment-intent) gets client_secret from backend
    4. stripe.confirmPayment({elements, clientSecret}) confirms with Stripe
    5. On success: user redirects to return_url
    6. On error: event.paymentFailed() dismisses wallet + dispatches to StripeState

    Usage::

        stripe.stripe_provider(
            stripe.ExpressCheckoutBridge.create(return_url="/checkout/complete"),
            publishable_key="pk_test_...",
            secret_key="sk_test_...",
            mode="payment", amount=1099, currency="usd",
        )
    """

    tag = "ExpressCheckoutBridge"

    # Internal configuration (not React props)
    _return_url: str = ""
    _api_url: str = "/api/stripe/create-payment-intent"

    def add_imports(self) -> rx.ImportDict:
        return {
            "@stripe/react-stripe-js": [
                "useStripe",
                "useElements",
                "ExpressCheckoutElement",
            ],
            "react": ["useCallback", "useContext"],
            "$/utils/context": ["EventLoopContext"],
            "$/utils/state": ["ReflexEvent"],
        }

    def add_custom_code(self) -> list[str]:
        from .stripe_state import StripeState

        state_name = StripeState.get_full_name()

        # Build return_url JS expression
        if self._return_url and not self._return_url.startswith("window."):
            return_url_js = f'"{self._return_url}"'
        else:
            return_url_js = 'window.location.origin + "/checkout/complete"'

        return [
            f"""
function ExpressCheckoutBridge({{ children, ...props }}) {{
  const stripe = useStripe();
  const elements = useElements();
  const [ addEvents ] = useContext(EventLoopContext);

  const onConfirm = useCallback(async (event) => {{
    if (!stripe || !elements) return;

    // Step 1: Validate and collect payment data
    const {{error: submitError}} = await elements.submit();
    if (submitError) {{
      event.paymentFailed({{reason: "fail", message: submitError.message}});
      if (addEvents) {{
        addEvents([ReflexEvent("{state_name}.handle_payment_error",
          {{error_message: submitError.message}})]);
      }}
      return;
    }}

    // Step 2: Create PaymentIntent on server (synchronous fetch)
    let clientSecret;
    try {{
      const res = await fetch("{self._api_url}", {{method: "POST"}});
      const data = await res.json();
      if (data.error) {{
        event.paymentFailed({{reason: "fail", message: data.error}});
        if (addEvents) {{
          addEvents([ReflexEvent("{state_name}.handle_payment_error",
            {{error_message: data.error}})]);
        }}
        return;
      }}
      clientSecret = data.client_secret;
    }} catch (fetchErr) {{
      event.paymentFailed({{reason: "fail", message: fetchErr.message}});
      if (addEvents) {{
        addEvents([ReflexEvent("{state_name}.handle_payment_error",
          {{error_message: fetchErr.message}})]);
      }}
      return;
    }}

    // Step 3: Confirm payment with Stripe
    const {{error}} = await stripe.confirmPayment({{
      elements,
      clientSecret,
      confirmParams: {{
        return_url: {return_url_js},
      }},
    }});

    if (error) {{
      event.paymentFailed({{reason: "fail", message: error.message}});
      if (addEvents) {{
        addEvents([ReflexEvent("{state_name}.handle_payment_error",
          {{error_message: error.message}})]);
      }}
    }}
    // If no error, Stripe redirects to return_url automatically
  }}, [stripe, elements, addEvents]);

  return (
    <ExpressCheckoutElement onConfirm={{onConfirm}} {{...props}}>
      {{children}}
    </ExpressCheckoutElement>
  );
}}
"""
        ]

    @classmethod
    def create(
        cls,
        *children,
        return_url: str = "",
        api_url: str = "/api/stripe/create-payment-intent",
        **props,
    ) -> "ExpressCheckoutBridge":
        """Create an ExpressCheckoutBridge component.

        Args:
            children: Optional child components.
            return_url: URL to redirect to after successful payment.
                Defaults to window.location.origin + "/checkout/complete".
            api_url: Backend API URL for PaymentIntent creation.
                Defaults to /api/stripe/create-payment-intent.
            **props: Additional props passed to ExpressCheckoutElement.
        """
        component = super().create(*children, **props)
        component._return_url = return_url
        component._api_url = api_url
        return component


express_checkout_bridge = ExpressCheckoutBridge.create
