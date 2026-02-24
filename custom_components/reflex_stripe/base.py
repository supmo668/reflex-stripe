import reflex as rx


class StripeBase(rx.Component):
    """Base component for all Stripe React component wrappers."""

    # The React library to wrap.
    library = "@stripe/react-stripe-js@^5.6.0"

    # Additional npm packages required.
    lib_dependencies: list[str] = ["@stripe/stripe-js@^8.8.0"]
