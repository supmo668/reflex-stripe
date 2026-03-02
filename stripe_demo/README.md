# reflex-stripe Demo

A minimal Reflex app demonstrating `reflex-stripe` components.

## Quick Start

```bash
# 1. Install dependencies (from stripe_demo/)
uv sync

# 2. Configure Stripe keys
cp .env.example .env
# Edit .env with your test keys from https://dashboard.stripe.com/test/apikeys

# 3. Start the app
source .env && uv run reflex run
```

Visit **http://localhost:3000**.

## What's in the Demo

| Route | Description |
|-------|-------------|
| `/` | Home page with manual Express + Embedded checkout (composable API) |
| `/embedded` | Page-helper one-liner: `add_checkout_page()` |
| `/express` | Page-helper one-liner: `add_express_checkout_page()` |
| `/checkout/complete` | Return page after payment |

## Using Your Own Products

Open `stripe_demo/stripe_demo.py` and look for the section marked:

```
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURE YOUR PRODUCTS / PRICES HERE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Option A — Stripe Price IDs (recommended)

Create products in the [Stripe Dashboard](https://dashboard.stripe.com/test/products),
then reference their Price IDs:

```python
EMBEDDED_LINE_ITEMS = [
    {"price": "price_1AbCdEfGhIjKlMnO", "quantity": 1},
]
```

### Option B — Inline price_data (no dashboard setup)

Define products entirely in code — useful for prototyping:

```python
EMBEDDED_LINE_ITEMS = [
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "My Product"},
            "unit_amount": 2000,  # $20.00 in cents
        },
        "quantity": 1,
    },
]
```

## Test Products (pre-configured)

The demo ships with example test price IDs. Replace them with your own from the
[Stripe Dashboard](https://dashboard.stripe.com/test/products):

| Line Item | Price ID | Amount |
|-----------|----------|--------|
| Plan 1 (monthly) | `price_1T6JxJRvKiLEj1vUElhnpdiM` | $9.99/mo |
| Plan 2 (monthly) | `price_1T6JxWRvKiLEj1vURqP6u3OZ` | $29.99/mo |

To use your own, replace the price IDs in `EMBEDDED_LINE_ITEMS` and `EXPRESS_AMOUNT`.

## Stripe Test Cards

| Card | Number | Behavior |
|------|--------|----------|
| Visa | `4242 4242 4242 4242` | Succeeds |
| Visa (3DS) | `4000 0025 0000 3155` | Requires authentication |
| Declined | `4000 0000 0000 0002` | Always declined |

Use any future expiry (e.g. `12/34`), any CVC, and any ZIP code.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `STRIPE_PUBLISHABLE_KEY` | Public key (`pk_test_...` or `pk_live_...`) |
| `STRIPE_SECRET_KEY` | Secret key (`sk_test_...` or `sk_live_...`) |
