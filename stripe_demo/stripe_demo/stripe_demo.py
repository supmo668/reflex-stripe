"""reflex-stripe demo application.

Setup
-----
1. Copy ``.env.example`` to ``.env`` and fill in your Stripe test keys::

       STRIPE_PUBLISHABLE_KEY=pk_test_...
       STRIPE_SECRET_KEY=sk_test_...

2. Load the env vars and start the app::

       source .env && uv run reflex run

3. Visit http://localhost:3000

The demo shows two checkout patterns:
- **Express Checkout** — Apple Pay / Google Pay / Link buttons (deferred-intent)
- **Embedded Checkout** — Stripe-hosted checkout form in an iframe (Checkout Session)

Both patterns are shown in "manual" (composable) and "page helper" (one-liner) modes.
"""

import os

import reflex as rx
import reflex_stripe as stripe

# ── Read keys from environment ──────────────────────────────────────
PK = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
SK = os.environ.get("STRIPE_SECRET_KEY", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURE YOUR PRODUCTS / PRICES HERE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Replace the price IDs below with your own from the Stripe Dashboard:
#   https://dashboard.stripe.com/test/products
#
# Option A — Use existing Stripe Price IDs (recommended):
#   {"price": "price_1AbCdEfGhIjKlMnO", "quantity": 1}
#
# Option B — Inline price_data (no dashboard setup needed):
#   {"price_data": {"currency": "usd", "product_data": {"name": "T-shirt"},
#                   "unit_amount": 2000}, "quantity": 1}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Embedded Checkout line items (Checkout Session mode)
EMBEDDED_LINE_ITEMS: list[dict] = [
    # Plan 1 — $9.99/mo (replace with your own price IDs)
    {"price": "price_1T6JxJRvKiLEj1vUElhnpdiM", "quantity": 1},
    # Plan 2 — $29.99/mo
    {"price": "price_1T6JxWRvKiLEj1vURqP6u3OZ", "quantity": 1},
]

# Express Checkout amount (deferred-intent mode — amount in cents)
EXPRESS_AMOUNT = 999  # $9.99


def _env_hint() -> rx.Component:
    """Show a hint when Stripe keys are missing."""
    if PK and SK:
        return rx.fragment()
    return rx.callout(
        rx.text(
            "Set ",
            rx.code("STRIPE_PUBLISHABLE_KEY"),
            " and ",
            rx.code("STRIPE_SECRET_KEY"),
            " env vars to enable checkout. See ",
            rx.code(".env.example"),
            ".",
        ),
        icon="triangle_alert",
        color_scheme="orange",
        width="100%",
    )


def index() -> rx.Component:
    """Home page with manual component composition (advanced usage)."""
    return rx.center(
        rx.vstack(
            rx.heading("reflex-stripe Demo", size="8"),
            rx.text("Test Express Checkout and Embedded Checkout below."),
            rx.text(
                "Also try ",
                rx.link("/embedded", href="/embedded"),
                " and ",
                rx.link("/express", href="/express"),
                " (page-helper one-liners).",
                color="gray",
            ),
            _env_hint(),
            rx.divider(),
            # ── Express Checkout (manual) ──
            rx.heading("Express Checkout (manual)", size="5"),
            rx.text(
                f"Apple Pay, Google Pay, and Link buttons. Amount: ${EXPRESS_AMOUNT / 100:.2f}.",
                color="gray",
            ),
            stripe.stripe_provider(
                stripe.ExpressCheckoutBridge.create(
                    return_url="/checkout/complete",
                ),
                publishable_key=PK,
                secret_key=SK,
                mode="payment",
                amount=EXPRESS_AMOUNT,
                currency="usd",
            ),
            rx.divider(),
            # ── Embedded Checkout (manual) ──
            rx.heading("Embedded Checkout (manual)", size="5"),
            rx.text(
                "Stripe-hosted checkout form in an iframe.",
                color="gray",
            ),
            stripe.embedded_checkout_session(
                publishable_key=PK,
                secret_key=SK,
                line_items=EMBEDDED_LINE_ITEMS,
                mode="subscription",  # Use "subscription" for recurring prices
                return_url="/checkout/complete",
            ),
            rx.divider(),
            # ── Payment Status ──
            rx.heading("Payment Status", size="5"),
            rx.text(f"Status: {stripe.StripeState.payment_status}"),
            rx.text(f"Error: {stripe.StripeState.error_message}"),
            align="center",
            spacing="4",
            width="100%",
            max_width="600px",
            padding="8",
        ),
        height="100vh",
    )


app = rx.App()
stripe.register_stripe_api(app)
app.add_page(index, route="/")
app.add_page(
    stripe.checkout_return_page,
    route="/checkout/complete",
    on_load=stripe.StripeState.get_session_status,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE-HELPER ONE-LINERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# These create full checkout pages + return pages with a single call.
# Replace line_items / amount with your own product prices.

# Creates /embedded + /embedded/return
stripe.add_checkout_page(
    app,
    route="/embedded",
    return_route="/embedded/return",
    line_items=EMBEDDED_LINE_ITEMS,
    mode="subscription",  # Use "subscription" for recurring prices
)

# Creates /express + /express/complete
stripe.add_express_checkout_page(
    app,
    route="/express",
    return_route="/express/complete",
    amount=EXPRESS_AMOUNT,
)
