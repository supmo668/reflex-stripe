# Getting Started

## Installation

```bash
pip install reflex-stripe
```

Or with uv:

```bash
uv add reflex-stripe
```

## Environment Variables

Set your Stripe keys as environment variables:

```bash
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_SECRET_KEY="sk_test_..."
```

!!! tip
    Get your test keys from the [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys).

## Quick Start

### Embedded Checkout (simplest)

Add a full Stripe checkout page to your app in 5 lines:

```python
import reflex as rx
import reflex_stripe as stripe

app = rx.App()
stripe.add_checkout_page(
    app,
    line_items=[{"price": "price_xxx", "quantity": 1}],
)
```

This creates:

- `/checkout` — Embedded Stripe checkout form
- `/checkout/return` — Return page with payment status

### Express Checkout (Apple Pay / Google Pay)

```python
import reflex as rx
import reflex_stripe as stripe

app = rx.App()
stripe.add_express_checkout_page(app, amount=2000, currency="usd")
```

This creates:

- `/express-checkout` — Express wallet buttons (Apple Pay, Google Pay, Link)
- `/express-checkout/complete` — Return page with payment status

### Custom Integration

For more control, compose components explicitly:

```python
import os
import reflex as rx
import reflex_stripe as stripe


def checkout_page() -> rx.Component:
    return stripe.stripe_provider(
        stripe.ExpressCheckoutBridge.create(
            return_url="/checkout/complete",
        ),
        publishable_key=os.environ["STRIPE_PUBLISHABLE_KEY"],
        secret_key=os.environ["STRIPE_SECRET_KEY"],
        mode="payment",
        amount=1099,
        currency="usd",
    )


app = rx.App()
stripe.register_stripe_api(app)
app.add_page(checkout_page, route="/checkout")
```

## API Routes

The library registers three API endpoints on your Reflex app:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/stripe/create-payment-intent` | POST | Creates a PaymentIntent (Express Checkout) |
| `/api/stripe/create-checkout-session` | POST | Creates a Checkout Session (Embedded Checkout) |
| `/api/stripe/session-status` | GET | Retrieves session status (return pages) |

Routes are auto-registered when you use `add_checkout_page()` or `add_express_checkout_page()`.
For manual composition, call `stripe.register_stripe_api(app)`.

## Components Reference

### Page Helpers

- **`add_checkout_page(app, ...)`** — Adds Embedded Checkout page + return page
- **`add_express_checkout_page(app, ...)`** — Adds Express Checkout page + return page
- **`checkout_return_page()`** — Standalone return page component

### Provider & Elements

- **`stripe_provider(*children, publishable_key, ...)`** — Wraps children in `<Elements>` with `loadStripe()`
- **`ExpressCheckoutBridge.create(return_url, ...)`** — Express wallet buttons with auto payment flow
- **`embedded_checkout_session(publishable_key, secret_key, line_items, ...)`** — Embedded checkout form

### State

- **`StripeState`** — Backend state managing `payment_status`, `error_message`, `customer_email`
- **`StripeState.get_session_status`** — `on_load` handler for Embedded Checkout return pages
- **`StripeState.get_payment_status`** — `on_load` handler for Express Checkout return pages

### Configuration Models

- **`Appearance`** — Stripe Elements appearance configuration
- **`ExpressCheckoutOptions`** — Express Checkout button options
- **`ButtonTheme`**, **`ButtonType`** — Button styling
- **`ExpressCheckoutLayout`** — Layout options (maxRows, overflow)
- **`Variables`** — CSS variables for theming
