<p align="center">
  <h1 align="center">reflex-stripe</h1>
</p>

<p align="center">
  <strong>Stripe payment components for Reflex applications</strong>
</p>

<p align="center">
  <a href="https://github.com/supmo668/reflex-stripe/actions/workflows/ci.yml">
    <img src="https://github.com/supmo668/reflex-stripe/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://pypi.org/project/reflex-stripe/">
    <img src="https://img.shields.io/pypi/v/reflex-stripe?color=blue" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/reflex-stripe/">
    <img src="https://img.shields.io/pypi/pyversions/reflex-stripe" alt="Python Versions">
  </a>
  <a href="https://github.com/supmo668/reflex-stripe/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="License">
  </a>
  <a href="https://github.com/supmo668/reflex-stripe/actions/workflows/publish.yml">
    <img src="https://github.com/supmo668/reflex-stripe/actions/workflows/publish.yml/badge.svg" alt="Publish">
  </a>
</p>

---

A [Reflex](https://reflex.dev) custom component library wrapping [`@stripe/react-stripe-js`](https://docs.stripe.com/stripe-js/react) for seamless Stripe payment integration in Python.

## Features

- **Express Checkout** — Apple Pay, Google Pay, and Link via `ExpressCheckoutElement`
- **Embedded Checkout** — Full Stripe-hosted checkout form in an iframe
- **Backend State Management** — `StripeState` handles PaymentIntents and Checkout Sessions
- **API Routes** — Auto-registered FastAPI endpoints for client-server communication
- **Type-Safe Config** — Pydantic-style `Appearance`, `ExpressCheckoutOptions`, and more

## Installation

```bash
pip install reflex-stripe
```

```bash
uv add reflex-stripe
```

## Quick Start

### Express Checkout

Drop in a complete Express Checkout (Apple Pay / Google Pay) with a single provider:

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
```

### Embedded Checkout

Render a full Stripe Checkout form as an embedded iframe:

```python
import os
import reflex as rx
import reflex_stripe as stripe

def checkout_page() -> rx.Component:
    return stripe.embedded_checkout_session(
        publishable_key=os.environ["STRIPE_PUBLISHABLE_KEY"],
        secret_key=os.environ["STRIPE_SECRET_KEY"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Pro Plan"},
                "unit_amount": 2000,
            },
            "quantity": 1,
        }],
        return_url="/checkout/complete",
    )
```

### Register API Routes

Register the Stripe backend endpoints on your Reflex app:

```python
app = rx.App()
stripe.register_stripe_api(app)
```

## Architecture

```
reflex_stripe/
├── base.py              # StripeBase — shared component base class
├── models.py            # Appearance, ExpressCheckoutOptions, ButtonType, etc.
├── stripe_provider.py   # StripeProvider wrapping <Elements> + loadStripe
├── stripe_state.py      # StripeState — PaymentIntent & Checkout Session management
├── express_checkout.py  # ExpressCheckoutElement + JS bridge
└── embedded_checkout.py # EmbeddedCheckoutProvider + EmbeddedCheckout + bridge
```

| Layer | Component | Purpose |
|-------|-----------|---------|
| Provider | `StripeProvider` | Wraps `<Elements>` with `loadStripe()` |
| Elements | `ExpressCheckoutElement`, `EmbeddedCheckout` | Stripe UI components |
| Bridges | `ExpressCheckoutBridge`, `EmbeddedCheckoutBridge` | JS glue for event handling |
| State | `StripeState` | Backend payment logic (PaymentIntents, Sessions) |
| API | `register_stripe_api()` | Auto-registers `/api/stripe/*` endpoints |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_PUBLISHABLE_KEY` | Yes | Stripe publishable key (`pk_test_...` or `pk_live_...`) |
| `STRIPE_SECRET_KEY` | Yes | Stripe secret key (`sk_test_...` or `sk_live_...`) |

## Development

```bash
task install    # Install dev deps + pre-commit hooks
task lint       # Run ruff linter
task typecheck  # Run pyright type checker
task test       # Run full test suite
task run        # Run demo app
task run-docs   # Run docs locally
```

## Requirements

- Python 3.11+
- Reflex >= 0.8.0
- Stripe Python SDK >= 12.0.0

## Contributing

Contributions welcome. Please run `task lint` and `task test` before submitting a PR.

## License

[Apache-2.0](LICENSE)
