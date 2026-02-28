"""reflex-stripe demo application."""

import os

import reflex as rx
import reflex_stripe as stripe


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
            rx.divider(),
            rx.heading("Express Checkout (manual)", size="5"),
            rx.text(
                "Requires STRIPE_PUBLISHABLE_KEY and STRIPE_SECRET_KEY env vars.",
                color="gray",
            ),
            stripe.stripe_provider(
                stripe.ExpressCheckoutBridge.create(
                    return_url="/checkout/complete",
                ),
                publishable_key=os.environ.get("STRIPE_PUBLISHABLE_KEY", ""),
                secret_key=os.environ.get("STRIPE_SECRET_KEY", ""),
                mode="payment",
                amount=1099,
                currency="usd",
            ),
            rx.divider(),
            rx.heading("Embedded Checkout (manual)", size="5"),
            rx.text(
                "Stripe-hosted checkout form in an iframe.",
                color="gray",
            ),
            stripe.embedded_checkout_session(
                publishable_key=os.environ.get("STRIPE_PUBLISHABLE_KEY", ""),
                secret_key=os.environ.get("STRIPE_SECRET_KEY", ""),
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Demo Product"},
                        "unit_amount": 2000,
                    },
                    "quantity": 1,
                }],
                return_url="/checkout/complete",
            ),
            rx.divider(),
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
    on_load=stripe.StripeState.get_payment_status,
)

# Page-helper one-liners (creates /embedded + /embedded/return)
stripe.add_checkout_page(
    app,
    route="/embedded",
    return_route="/embedded/return",
    line_items=[{
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Demo Product (Page Helper)"},
            "unit_amount": 2000,
        },
        "quantity": 1,
    }],
)

# Creates /express + /express/complete
stripe.add_express_checkout_page(
    app,
    route="/express",
    return_route="/express/complete",
    amount=1099,
)
