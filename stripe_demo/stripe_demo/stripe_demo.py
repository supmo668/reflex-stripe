"""reflex-stripe demo application."""

import os

import reflex as rx
import reflex_stripe as stripe


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("reflex-stripe Demo", size="8"),
            rx.text("Test Express Checkout and Embedded Checkout below."),
            rx.divider(),
            rx.heading("Express Checkout", size="5"),
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


def checkout_complete() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Payment Complete!", size="8"),
            rx.text("Thank you for your purchase."),
            rx.link("Back to home", href="/"),
            align="center",
            spacing="4",
        ),
        height="100vh",
    )


app = rx.App()
stripe.register_stripe_api(app)
app.add_page(index, route="/")
app.add_page(checkout_complete, route="/checkout/complete")
