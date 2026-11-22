# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-11-22

### Changed

- Stripe.js is now loaded on first render of a Stripe component instead of when
  a page module is imported. `loadStripe` is imported from the side-effect-free
  entry of the pinned `@stripe/stripe-js` (`pure`), and the module-level
  `const stripePromise = loadStripe(key)` is replaced by a memoised
  `getStripePromise(key)` called at render (for `EmbeddedCheckoutProvider`, only
  once a client secret is present). One `loadStripe` call per publishable key
  per module; providers receive the same promise object on every render.
  Pages that never render a Stripe component no longer request Stripe.js.
  No Python API, prop or option changed. See "Loading Stripe.js" in the README
  for the fraud-signal trade-off and how to keep loading it on every page.
- The emitted module-level identifier `stripePromise` no longer exists; custom
  JS that referenced it should call `getStripePromise("<publishable key>")`.

### Included (on `main` since 0.1.1, not previously published)

- Exact npm versions: `@stripe/react-stripe-js@7.0.0`, `@stripe/stripe-js@10.0.0`
- Guarded `EmbeddedCheckoutProvider` that maps `client_secret` to
  `options.clientSecret` and renders nothing until the secret is set

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
