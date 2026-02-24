# reflex-stripe

A Reflex custom component library for Stripe payment integration.

## Overview

`reflex-stripe` wraps `@stripe/react-stripe-js` to provide Pythonic Stripe
checkout components for Reflex applications.

## Features

- **Express Checkout** -- Apple Pay, Google Pay, Link, PayPal buttons
- **Embedded Checkout** -- Full Stripe-hosted checkout form
- **One-liner page helpers** -- `add_checkout_page(app)` and `add_express_checkout_page(app)`
- **Typed configuration** -- Python dataclasses for all Stripe options
- **Backend state management** -- `StripeState` for PaymentIntent/Session creation
