# CLAUDE.md — reflex-stripe

## Overview

`reflex-stripe` is a Reflex custom component library wrapping `@stripe/react-stripe-js`. It follows the same architecture as `reflex-clerk-api` — React library wrapping with Python state management.

## Package Structure

```
custom_components/reflex_stripe/
├── __init__.py          # Public API exports
├── base.py              # StripeBase(rx.Component), library = "@stripe/react-stripe-js"
├── models.py            # Appearance, ExpressCheckoutOptions, ButtonType, etc.
├── stripe_provider.py   # StripeProvider wrapping <Elements> + loadStripe
├── stripe_state.py      # StripeState — backend PaymentIntent/Session management
├── express_checkout.py  # ExpressCheckoutElement + JS bridge
├── embedded_checkout.py # EmbeddedCheckoutProvider + EmbeddedCheckout
└── pages.py             # add_checkout_page(), add_express_checkout_page(), checkout_return_page()
```

## Commands

```bash
# Install deps
uv sync

# Run demo app
cd stripe_demo && uv run reflex run

# Tests
uv run pytest tests/ -v

# Lint
uv run ruff check custom_components/ tests/
uv run ruff format custom_components/ tests/
```

## Implementation Status

See `.claude/PRPs/prds/reflex-stripe.prd.md` for full PRD.

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project scaffold | COMPLETE |
| 2 | Core components (StripeBase, Provider, models) | COMPLETE |
| 3 | StripeState + Express Checkout | COMPLETE |
| 4 | Embedded Checkout | COMPLETE |
| 5 | Page helpers + Return page | COMPLETE |
| 6 | Demo app | PENDING |
| 7 | Documentation + CI/CD | PENDING |
| 8 | Testing + PyPI publish | PENDING |

## Key Conventions

- Package manager: **uv**
- Build backend: **hatchling** (updated from setuptools)
- Component base class: `StripeBase(rx.Component)` in `base.py`
- State management: `StripeState(rx.State)` — `_secret_key: ClassVar[str]`
- React library: `@stripe/react-stripe-js` + `@stripe/stripe-js`
- Python SDK: `stripe>=12.0.0`
- Pattern reference: `reflex-clerk-api` (same Provider → Element → State architecture)

## Architecture Notes

- `loadStripe()` is async — handled via `add_custom_code` in StripeProvider
- Express Checkout `onConfirm` needs multi-step JS flow → custom bridge component
- Embedded Checkout uses `fetchClientSecret` callback → needs FastAPI endpoint
- Config models use `PropsBase` dataclasses (like clerk-api's `Appearance`)
