# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-28

### Added

- `StripeProvider` wrapping `<Elements>` with async `loadStripe` initialization
- `ExpressCheckoutElement` and `ExpressCheckoutBridge` for Apple Pay, Google Pay, Link
- `EmbeddedCheckoutProvider`, `EmbeddedCheckout`, and `EmbeddedCheckoutBridge` for Stripe-hosted checkout
- `StripeState` backend state with `create_payment_intent()`, `create_checkout_session()`, `get_session_status()`, `get_payment_status()`
- `add_checkout_page()` one-liner for Embedded Checkout page creation
- `add_express_checkout_page()` one-liner for Express Checkout page creation
- `checkout_return_page()` component for post-payment status display
- Typed configuration models: `Appearance`, `Variables`, `ExpressCheckoutOptions`, `ExpressCheckoutLayout`, `ButtonTheme`, `ButtonType`, `PaymentMethods`
- API endpoints: `/api/stripe/create-payment-intent`, `/api/stripe/create-checkout-session`, `/api/stripe/session-status`
- Demo app with both Express and Embedded checkout flows
- MkDocs documentation with Getting Started, API Reference
- CI/CD with GitHub Actions (lint, pyright, pytest across Python 3.11-3.13)
- PyPI publish workflow
