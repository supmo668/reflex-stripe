# reflex-stripe

## Problem Statement

Reflex (Python) developers who need Stripe payment integration have no proper component library. The only existing example (`joyhchen/reflex-embedded-checkout`) uses raw `rx.call_script` with inline JS strings — no proper React component wrapping, no state management, no type safety, and hardcoded price IDs. Developers must write fragile JS interop code to accept payments, a task that should be a one-liner.

## Evidence

- `joyhchen/reflex-embedded-checkout` has 0 abstraction — raw Stripe.js loaded via `rx.script`, checkout mounted via `rx.call_script` with string interpolation of client secrets
- No `reflex-stripe` package exists on PyPI (searched Feb 2026)
- `reflex-clerk-api` proves the pattern works — wrapping `@clerk/clerk-react` into Reflex components with 55+ exports, full state management, and `add_sign_in_page()` one-liners
- Stripe's `@stripe/react-stripe-js` provides React components (`Elements`, `ExpressCheckoutElement`, `EmbeddedCheckoutProvider`, `EmbeddedCheckout`) that are ideal candidates for Reflex wrapping

## Proposed Solution

Build `reflex-stripe` — a Reflex custom component library that wraps `@stripe/react-stripe-js` using the same architecture as `reflex-clerk-api`. V1 focuses on two checkout flows: **Express Checkout** (Apple Pay, Google Pay, Link, PayPal) and **Embedded Checkout** (Stripe-hosted form embedded in an iframe). The library provides a `StripeState` for backend PaymentIntent/Session management, typed configuration models, and `add_checkout_page()`/`add_express_checkout_page()` helpers for zero-config page creation.

## Key Hypothesis

We believe a Pythonic Stripe component library with `add_checkout_page()` one-liners and typed configuration will enable Reflex developers to accept payments in <10 lines of Python.
We'll know we're right when the library can reproduce the full `joyhchen/reflex-embedded-checkout` functionality in 5 lines and the Express Checkout Element in 3 lines.

## What We're NOT Building

- **Subscription management UI** — complex billing portal is a separate concern, deferred
- **Stripe Connect / marketplace flows** — multi-party payments are out of scope
- **Custom Payment Element** — the full card/bank/BNPL form; Express + Embedded cover v1 needs
- **Webhook handling** — server-side webhook verification is important but orthogonal to components
- **Stripe Customer portal** — Stripe's hosted billing portal is a redirect, not a component
- **Invoice/receipt rendering** — PDF/email generation is backend-only

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Lines to checkout page | ≤5 lines (via `add_checkout_page()`) | Code measurement |
| Express checkout setup | ≤10 lines with full config | Code measurement |
| Component parity with clerk-api | Same structure: base, models, provider, state, pages, demo, docs | File structure comparison |
| PyPI installable | `uv add reflex-stripe` works | PyPI listing |
| Demo app functional | End-to-end payment in test mode | Manual + Playwright test |

## Open Questions

- [ ] Should `StripeState` handle PaymentIntent creation server-side, or should it only manage client_secret forwarding (letting users create intents in their own backend)?
- [ ] How to handle domain registration requirement for Apple Pay/Google Pay in dev vs prod?
- [ ] Should the library include a return/success page component, or just a helper?
- [ ] What Reflex version minimum? (0.8.0 to match clerk-api, or newer?)
- [ ] Should we support `mode='subscription'` in v1, or strictly `mode='payment'`?

---

## Users & Context

**Primary User**
- **Who**: Python/Reflex developers building SaaS, e-commerce, or donation apps who need payment collection
- **Current behavior**: Either (a) don't have payments, (b) redirect to Stripe hosted checkout via URL, or (c) write fragile `rx.call_script` JS interop like `joyhchen/reflex-embedded-checkout`
- **Trigger**: "I need to accept a payment in my Reflex app"
- **Success state**: `import reflex_stripe as stripe` → configure keys → `stripe.add_checkout_page(app)` → working checkout at `/checkout`

**Job to Be Done**
When building a Reflex app that needs to accept payments, I want to drop in a Stripe checkout component with Python configuration, so I can accept payments without writing JavaScript or managing React interop.

**Non-Users**
- Developers who need full Stripe Elements customization (custom card inputs, split fields) — they should use Stripe.js directly
- Developers building mobile apps — this is web-only via Reflex
- Developers who only need Stripe hosted checkout (redirect) — they just need a URL, no component

---

## Solution Detail

### Core Capabilities (MoSCoW)

| Priority | Capability | Rationale |
|----------|------------|-----------|
| Must | **StripeProvider** — `Elements` wrapper with `loadStripe` | Foundation: all Stripe components need this context |
| Must | **ExpressCheckoutElement** — Apple Pay, Google Pay, Link, PayPal buttons | Primary Express Checkout flow |
| Must | **EmbeddedCheckout** — Full Stripe-hosted checkout form in iframe | Primary Embedded Checkout flow |
| Must | **StripeState** — Backend state for creating PaymentIntents/Sessions, tracking status | Server-side integration (equivalent to ClerkState) |
| Must | **`add_checkout_page(app)`** — One-liner to add `/checkout` embedded checkout page | Parity with `add_sign_in_page()` pattern |
| Must | **`add_express_checkout_page(app)`** — One-liner for express checkout page | Parity with `add_sign_in_page()` pattern |
| Must | **Configuration models** — Appearance, ButtonType, ButtonTheme, Layout typed dataclasses | Type-safe Python configuration |
| Must | **Demo app** — Working demo with test keys | Proves the library works, serves as documentation |
| Must | **Documentation** — MkDocs with getting started + component reference | Publishable docs |
| Should | **CheckoutReturnPage** — Component/helper for post-payment return URL handling | Common need after checkout |
| Should | **`on_payment_complete` callback** — Event handler for payment success | State management convenience |
| Should | **Appearance API** — Theme, variables, borderRadius config | Stripe Elements styling |
| Could | **PaymentElement** — Full card/bank/BNPL input form | More flexible than Express, but complex |
| Could | **`mode='subscription'`** — Recurring payment support | Common but adds scope |
| Won't | **Webhook endpoint** — Server-side webhook handler | Orthogonal; users should implement with FastAPI directly |
| Won't | **Stripe Connect** — Multi-party payments | Too complex for v1 |
| Won't | **Customer portal** — Billing management | Stripe-hosted redirect, not a component |

### MVP Scope

1. `stripe_provider()` wrapping `<Elements>` with `loadStripe`
2. `express_checkout()` wrapping `<ExpressCheckoutElement>` with `onConfirm`, `onClick`, `onReady` events
3. `embedded_checkout()` wrapping `<EmbeddedCheckoutProvider>` + `<EmbeddedCheckout>`
4. `StripeState` with `create_checkout_session()` and `create_payment_intent()` backend methods
5. `add_checkout_page(app)` and `add_express_checkout_page(app)` helpers
6. Typed models for configuration (Appearance, ExpressCheckoutOptions)
7. Demo app with both flows working in test mode
8. MkDocs documentation

### User Flow

**Express Checkout (shortest path):**
```python
import reflex_stripe as stripe

# In app setup:
stripe.add_express_checkout_page(
    app,
    secret_key=os.environ["STRIPE_SECRET_KEY"],
    publishable_key=os.environ["STRIPE_PUBLISHABLE_KEY"],
    amount=1099,  # $10.99
    currency="usd",
)
# → Express checkout buttons at /express-checkout
```

**Embedded Checkout (shortest path):**
```python
import reflex_stripe as stripe

stripe.add_checkout_page(
    app,
    secret_key=os.environ["STRIPE_SECRET_KEY"],
    publishable_key=os.environ["STRIPE_PUBLISHABLE_KEY"],
    line_items=[{"price": "price_xxx", "quantity": 1}],
)
# → Full Stripe checkout form at /checkout
```

**Custom integration (explicit):**
```python
import reflex_stripe as stripe

def checkout_page():
    return stripe.stripe_provider(
        stripe.express_checkout(
            on_confirm=StripeState.handle_confirm,
            options=stripe.ExpressCheckoutOptions(
                button_height=50,
                button_theme=stripe.ButtonTheme(apple_pay="white-outline"),
                layout=stripe.ExpressCheckoutLayout(max_rows=2, overflow="auto"),
            ),
        ),
        publishable_key=os.environ["STRIPE_PUBLISHABLE_KEY"],
        mode="payment",
        amount=1099,
        currency="usd",
    )
```

---

## Technical Approach

**Feasibility**: HIGH

The pattern is proven by `reflex-clerk-api` — wrapping React component libraries (`@clerk/clerk-react`) into Reflex custom components with state management. The Stripe equivalent (`@stripe/react-stripe-js`) follows the same Provider → Element pattern.

**Architecture Notes**

- **React library**: `@stripe/react-stripe-js` (wraps `@stripe/stripe-js`)
- **Base class**: `StripeBase(rx.Component)` with `library = "@stripe/react-stripe-js"`
- **Provider pattern**: `StripeProvider` wraps `<Elements>` — needs `loadStripe()` via custom JS import from `@stripe/stripe-js`
- **State pattern**: `StripeState(rx.State)` handles backend Stripe API calls (create sessions/intents) and stores `client_secret`, `payment_status`
- **Session synchronizer**: Custom React component (like `ClerkSessionSynchronizer`) that bridges frontend Stripe events to backend state
- **Backend SDK**: `stripe` Python package for server-side PaymentIntent/Session creation
- **Key difference from Clerk**: Clerk has a persistent auth session; Stripe has per-transaction sessions. `StripeState` manages transient checkout state, not persistent auth

**Key Technical Decisions**

| Decision | Choice | Why |
|----------|--------|-----|
| React library | `@stripe/react-stripe-js` | Official React wrapper, maintained by Stripe |
| Backend SDK | `stripe` Python package | Official, well-maintained, async support |
| State approach | Create PaymentIntent/Session in StripeState event handlers | Keeps secret_key server-side, mirrors clerk_provider pattern |
| loadStripe | Custom JS import in component | `loadStripe()` must be called client-side; handle via `add_imports` + `add_custom_code` |
| Embedded Checkout | Separate component tree (EmbeddedCheckoutProvider → EmbeddedCheckout) | Stripe requires different provider for embedded vs Elements checkout |
| Express Checkout | Elements → ExpressCheckoutElement | Standard Stripe Elements flow with onConfirm → confirmPayment |

**Technical Risks**

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `loadStripe()` async initialization in Reflex | M | Study how clerk_provider handles `ClerkProvider` initialization; may need `add_custom_code` for async JS |
| Express Checkout `onConfirm` requires `elements.submit()` + `stripe.confirmPayment()` chain in JS | M | Implement as custom React component (like ClerkSessionSynchronizer) that handles the full JS flow |
| Apple Pay / Google Pay require HTTPS + domain registration | L | Document clearly; works in Stripe test mode without registration |
| Reflex `rx.Var` serialization of Stripe config objects | L | Use PropsBase dataclasses (proven in clerk models.py) |
| EmbeddedCheckout uses `fetchClientSecret` callback (not static prop) | M | Need custom JS component that calls backend API endpoint, not just state variable |

---

## Implementation Phases

<!--
  STATUS: pending | in-progress | complete
  PARALLEL: phases that can run concurrently (e.g., "with 3" or "-")
  DEPENDS: phases that must complete first (e.g., "1, 2" or "-")
  PRP: link to generated plan file once created
-->

| # | Phase | Description | Status | Parallel | Depends | PRP Plan |
|---|-------|-------------|--------|----------|---------|----------|
| 1 | Project scaffold | Fork repo, setup package structure mirroring reflex-clerk-api (pyproject.toml, Taskfile, mkdocs, CI, .gitmodules update) | complete | - | - | [plan](../plans/reflex-stripe-phase-1-scaffold.plan.md) |
| 2 | Core components | StripeBase, StripeProvider (Elements wrapper), loadStripe integration, models (Appearance, ExpressCheckoutOptions) | complete | - | 1 | [plan](../plans/reflex-stripe-phase-2-core-components.plan.md) |
| 3 | StripeState + Express Checkout | StripeState with create_payment_intent(), ExpressCheckoutElement component with onConfirm/onClick/onReady, JS bridge for confirmPayment flow | complete | - | 2 | [plan](../plans/reflex-stripe-phase-3-stripe-state-express.plan.md) |
| 4 | Embedded Checkout | EmbeddedCheckoutProvider + EmbeddedCheckout components, StripeState.create_checkout_session(), fetchClientSecret bridge | complete | with 3 | 2 | [plan](../plans/completed/reflex-stripe-phase-4-embedded-checkout.plan.md) |
| 5 | Page helpers + Return page | add_checkout_page(), add_express_checkout_page(), CheckoutReturn component, session status retrieval | complete | - | 3, 4 | [plan](../plans/completed/reflex-stripe-phase-5-page-helpers.plan.md) |
| 6 | Demo app | Full demo app with both Express and Embedded checkout flows, test mode, interactive examples | complete | with 7 | 5 | - |
| 7 | Documentation + CI/CD | MkDocs docs (getting started, component reference), GitHub Actions (CI, publish, deploy), Taskfile tasks | complete | with 6 | 5 | - |
| 8 | Testing + publish | Playwright E2E tests, PyPI publishing, README, final validation | complete | - | 6, 7 | - |

### Phase Details

**Phase 1: Project scaffold**
- **Goal**: Establish the package structure matching reflex-clerk-api conventions
- **Scope**:
  - Fork `joyhchen/reflex-embedded-checkout` to `supmo668/reflex-embedded-checkout` (reference)
  - Reset `supmo668/reflex-stripe` repo with new structure:
    ```
    reflex-stripe/
    ├── custom_components/
    │   └── reflex_stripe/
    │       ├── __init__.py
    │       ├── base.py
    │       ├── models.py
    │       └── ...
    ├── stripe_demo/
    │   ├── stripe_demo/
    │   │   └── stripe_demo.py
    │   ├── rxconfig.py
    │   └── assets/
    ├── docs/
    ├── tests/
    ├── pyproject.toml
    ├── Taskfile.yml
    ├── mkdocs.yml
    ├── .pre-commit-config.yaml
    ├── .github/workflows/
    └── README.md
    ```
  - Update `.gitmodules` to point to new remote if needed
  - pyproject.toml with `stripe>=12.0.0`, `reflex>=0.8.0` deps
- **Success signal**: `uv sync` works, package importable, ruff/pyright pass on empty scaffold

**Phase 2: Core components**
- **Goal**: Foundation components that all checkout flows depend on
- **Scope**:
  - `base.py`: `StripeBase(rx.Component)` with `library = "@stripe/react-stripe-js"`
  - `models.py`: `Appearance`, `Variables`, `ExpressCheckoutOptions`, `ExpressCheckoutLayout`, `ButtonType`, `ButtonTheme` dataclasses using `PropsBase`
  - `stripe_provider.py`: `StripeProvider` wrapping `<Elements>` component, `loadStripe` import handling via `add_imports` + `add_custom_code`, `stripe_provider()` factory function
- **Success signal**: `stripe.stripe_provider(rx.text("hello"), publishable_key="pk_test_xxx", mode="payment", amount=100, currency="usd")` renders without JS errors

**Phase 3: StripeState + Express Checkout**
- **Goal**: Working Express Checkout with backend payment creation
- **Scope**:
  - `StripeState(rx.State)` with:
    - `client_secret: str` — current transaction's client secret
    - `payment_status: str` — "idle" | "processing" | "succeeded" | "failed"
    - `error_message: str` — last error
    - `create_payment_intent(amount, currency)` — server-side PaymentIntent creation
    - `_secret_key: ClassVar[str]` — Stripe secret key (server-only)
  - `ExpressCheckoutElement` component wrapping `<ExpressCheckoutElement>`
  - `ExpressCheckoutBridge` custom JS component (like `ClerkSessionSynchronizer`) that:
    - Calls `elements.submit()` on confirm
    - Fetches client_secret from StripeState
    - Calls `stripe.confirmPayment()` with return_url
    - Reports success/error back to StripeState
  - Event handlers: `on_confirm`, `on_click`, `on_ready`, `on_cancel`
  - Express checkout options: `button_height`, `button_type`, `button_theme`, `layout`
- **Success signal**: Express Checkout buttons render, clicking Google Pay (test mode) completes a payment

**Phase 4: Embedded Checkout**
- **Goal**: Working Embedded Checkout (Stripe-hosted form in iframe)
- **Scope**:
  - `EmbeddedCheckoutProvider` wrapping `<EmbeddedCheckoutProvider>`
  - `EmbeddedCheckout` wrapping `<EmbeddedCheckout>`
  - `StripeState.create_checkout_session(line_items, mode, return_url)` — server-side Session creation with `ui_mode='embedded'`
  - `fetchClientSecret` JS bridge (callback-based, not static prop)
  - `embedded_checkout()` factory function
- **Success signal**: Embedded checkout form renders with Stripe card input, test payment succeeds

**Phase 5: Page helpers + Return page**
- **Goal**: One-liner page creation matching `add_sign_in_page()` pattern
- **Scope**:
  - `pages.py`:
    - `add_checkout_page(app, secret_key, publishable_key, line_items, route="/checkout", return_route="/checkout/return")`
    - `add_express_checkout_page(app, secret_key, publishable_key, amount, currency, route="/express-checkout")`
  - `CheckoutReturn` component or helper for `/checkout/return` page (shows success/status)
  - `StripeState.get_session_status(session_id)` for return page
- **Success signal**: `stripe.add_checkout_page(app, ...)` creates working checkout at `/checkout` with return page

**Phase 6: Demo app**
- **Goal**: Interactive demo proving all capabilities
- **Scope**:
  - `stripe_demo/` app with:
    - Home page with overview and setup instructions
    - Express Checkout demo with configurable options
    - Embedded Checkout demo
    - Return/success page
    - State display (payment status, errors)
  - Test mode with Stripe test keys
  - Dockerfile for deployment
- **Success signal**: `task run` starts demo, both checkout flows complete in test mode

**Phase 7: Documentation + CI/CD**
- **Goal**: Publishable documentation and automated pipelines
- **Scope**:
  - MkDocs docs: about, getting_started, component reference (stripe_provider, express_checkout, embedded_checkout, pages, models)
  - GitHub Actions: CI (lint + typecheck + test), publish (PyPI), deploy (demo + docs)
  - Taskfile: install, run, test, lint, typecheck, bump-*, publish, run-docs
  - .pre-commit-config.yaml (ruff)
  - README.md with quickstart examples
- **Success signal**: `task test` passes, docs render at localhost:9000

**Phase 8: Testing + publish**
- **Goal**: Validated, published package
- **Scope**:
  - Playwright E2E tests (render, express checkout flow, embedded checkout flow)
  - Unit tests for StripeState, models
  - First PyPI publish
  - Update parent repo `.gitmodules` if needed
- **Success signal**: `uv add reflex-stripe` installs from PyPI, demo app works

### Parallelism Notes

- **Phases 3 and 4** can run in parallel in separate worktrees — Express Checkout and Embedded Checkout are independent component trees with separate React providers. Both depend on Phase 2 (core components) being complete.
- **Phases 6 and 7** can run in parallel — demo app development and documentation are independent writing tasks.
- All other phases are sequential due to dependencies.

---

## Decisions Log

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Package structure | `custom_components/reflex_stripe/` (setuptools find) | Flat `reflex_stripe/` | Match reflex-clerk-api exactly for consistency across our libs |
| React library | `@stripe/react-stripe-js` | Raw `@stripe/stripe-js` via rx.call_script | React wrapper provides proper component lifecycle, props, events — essential for Reflex wrapping |
| Backend integration | `stripe` Python SDK in StripeState | FastAPI endpoint separate from state | Keep server-side logic in State (like ClerkState) for single-package simplicity |
| Express Checkout confirm flow | Custom JS bridge component | Direct event handler mapping | `onConfirm` requires `elements.submit()` → fetch client_secret → `stripe.confirmPayment()` chain that must execute client-side |
| Embedded Checkout client_secret | `fetchClientSecret` callback via API endpoint | Static client_secret prop | Stripe requires callback pattern for embedded checkout; need FastAPI endpoint |
| Build backend | setuptools (match clerk-api) | hatchling | Consistency with existing libs in monorepo |
| Config models | PropsBase dataclasses | Plain dicts | Type safety, IDE autocomplete, matches clerk-api Appearance pattern |
| Hosting reference repo | Fork joyhchen/reflex-embedded-checkout | Copy code only | Maintain attribution, easy to pull upstream changes |

---

## Research Summary

**Market Context**
- No existing `reflex-stripe` package on PyPI (Feb 2026)
- `joyhchen/reflex-embedded-checkout` is the only Reflex+Stripe example — uses raw JS interop, Reflex 0.4.4, hardcoded price IDs, no abstraction
- `reflex-clerk-api` v1.1.3 is the gold standard for Reflex custom component libraries — well-structured, 55+ exports, full docs/tests/CI
- Stripe's `@stripe/react-stripe-js` provides clean React components ready for wrapping: `Elements`, `ExpressCheckoutElement`, `EmbeddedCheckoutProvider`, `EmbeddedCheckout`
- Express Checkout Element supports: Apple Pay, Google Pay, Link, PayPal, Klarna, Amazon Pay
- Stripe requires HTTPS for production payment methods; test mode works on localhost

**Technical Context**
- **Existing scaffold**: `supmo668/reflex-stripe` exists with empty `__init__.py` + minimal pyproject.toml (2 commits)
- **Reference code**: `joyhchen/reflex-embedded-checkout` demonstrates the core pattern: `CheckoutState` creates a `stripe.checkout.Session` with `ui_mode='embedded'`, stores `client_secret`, mounts checkout via raw JS `stripe.initEmbeddedCheckout({clientSecret})`
- **Proven pattern**: `reflex-clerk-api` shows how to wrap React libraries: `ClerkBase(rx.Component)` → `library = "@clerk/clerk-react"`, `ClerkProvider` with `add_custom_code()` for JS bridge, `ClerkState` for backend sync
- **Key challenge**: Stripe's `loadStripe()` is async and returns a Promise — need careful handling in component initialization. The `Elements` provider takes `stripe={stripePromise}` not a resolved value
- **Key challenge**: Express Checkout `onConfirm` is a multi-step JS flow (`elements.submit()` → fetch intent → `stripe.confirmPayment()`) that needs a custom bridge component
- **Key challenge**: Embedded Checkout uses `fetchClientSecret` callback that must call a server endpoint — needs FastAPI route registration similar to health endpoint pattern

---

*Generated: 2026-02-23*
*Status: DRAFT - needs validation*
