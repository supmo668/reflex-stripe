# reflex-stripe

A Reflex custom component library for Stripe payment integration.

Wraps `@stripe/react-stripe-js` to provide Express Checkout and Embedded Checkout
components for Reflex applications.

## Installation

```bash
uv add reflex-stripe

pip install reflex-stripe
```

## Quick Start

### Express Checkout (one-liner)

```python
import reflex_stripe as stripe

stripe.add_express_checkout_page(
    app,
    publishable_key=os.environ["STRIPE_PUBLISHABLE_KEY"],
    secret_key=os.environ["STRIPE_SECRET_KEY"],
    amount=1099,
    currency="usd",
)
```

### Embedded Checkout (one-liner)

```python
import reflex_stripe as stripe

stripe.add_checkout_page(
    app,
    publishable_key=os.environ["STRIPE_PUBLISHABLE_KEY"],
    secret_key=os.environ["STRIPE_SECRET_KEY"],
    line_items=[{"price": "price_xxx", "quantity": 1}],
)
```

## Development

```bash
task install    # Install dev deps + pre-commit
task run        # Run demo app
task lint       # Run ruff linter
task typecheck  # Run pyright
task test       # Run full test suite
task run-docs   # Run docs locally
```

## Contributing

See the development section above. PRs welcome.

## License

Apache-2.0
