# reflex-stripe

A Reflex custom component library for Stripe payment integration.

## Overview

`reflex-stripe` wraps [`@stripe/react-stripe-js`](https://docs.stripe.com/stripe-js/react) to provide Pythonic Stripe
checkout components for [Reflex](https://reflex.dev) applications. It follows the same architecture
as `reflex-clerk-api` — React library wrapping with Python state management.

## Features

- **Express Checkout** — Apple Pay, Google Pay, Link via `ExpressCheckoutElement`
- **Embedded Checkout** — Full Stripe-hosted checkout form in an iframe
- **One-liner page helpers** — `add_checkout_page(app)` and `add_express_checkout_page(app)`
- **Return page component** — `checkout_return_page()` with automatic payment status display
- **Backend state management** — `StripeState` handles PaymentIntents and Checkout Sessions
- **API routes** — Auto-registered `/api/stripe/*` endpoints for client-server communication
- **Typed configuration** — `Appearance`, `ExpressCheckoutOptions`, and more via `PropsBase` dataclasses

## Architecture

```
reflex_stripe/
├── base.py              # StripeBase — shared component base class
├── models.py            # Appearance, ExpressCheckoutOptions, ButtonType, etc.
├── stripe_provider.py   # StripeProvider wrapping <Elements> + loadStripe
├── stripe_state.py      # StripeState — PaymentIntent & Checkout Session management
├── express_checkout.py  # ExpressCheckoutElement + JS bridge
├── embedded_checkout.py # EmbeddedCheckoutProvider + EmbeddedCheckout + bridge
└── pages.py             # Page helpers + checkout return page
```

| Layer | Component | Purpose |
|-------|-----------|---------|
| Provider | `StripeProvider` | Wraps `<Elements>` with `loadStripe()` |
| Elements | `ExpressCheckoutElement`, `EmbeddedCheckout` | Stripe UI components |
| Bridges | `ExpressCheckoutBridge`, `EmbeddedCheckoutBridge` | JS glue for payment event handling |
| State | `StripeState` | Backend payment logic (PaymentIntents, Sessions) |
| API | `register_stripe_api()` | Auto-registers `/api/stripe/*` endpoints |
| Pages | `add_checkout_page()`, `add_express_checkout_page()` | One-liner page creation |

## Requirements

- Python 3.11+
- Reflex >= 0.8.0
- Stripe Python SDK >= 12.0.0

## License

Apache-2.0
