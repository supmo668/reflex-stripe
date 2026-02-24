"""Typed configuration models for Stripe Elements components."""

from typing import Literal

from reflex.components.props import PropsBase

LiteralTheme = Literal["stripe", "night", "flat"]


class Variables(PropsBase):
    """Stripe Elements appearance variables.

    See: https://docs.stripe.com/elements/appearance-api?platform=web#variables
    """

    font_family: str = ""
    font_size_base: str = ""
    spacing_unit: str = ""
    border_radius: str = ""
    color_primary: str = ""
    color_background: str = ""
    color_text: str = ""
    color_danger: str = ""
    color_success: str = ""
    color_warning: str = ""
    color_text_secondary: str = ""
    color_text_placeholder: str = ""
    color_icon: str = ""
    color_icon_tab: str = ""
    color_icon_tab_selected: str = ""
    focus_box_shadow: str = ""
    focus_outline: str = ""


class Appearance(PropsBase):
    """Stripe Elements appearance configuration.

    See: https://docs.stripe.com/elements/appearance-api
    """

    theme: LiteralTheme | None = None
    variables: Variables | None = None
    rules: dict[str, dict[str, str]] | None = None
    labels: Literal["above", "floating"] | None = None
    disable_animations: bool | None = None


class ExpressCheckoutLayout(PropsBase):
    """Layout options for Express Checkout Element."""

    max_columns: int | None = None
    max_rows: int | None = None
    overflow: Literal["auto", "never"] | None = None


class ButtonTheme(PropsBase):
    """Button theme options per payment method."""

    apple_pay: Literal["black", "white", "white-outline"] | None = None
    google_pay: Literal["black", "white"] | None = None
    paypal: Literal["gold", "blue", "silver", "white", "black"] | None = None


class ButtonType(PropsBase):
    """Button type/label options per payment method."""

    apple_pay: (
        Literal[
            "add-money",
            "book",
            "buy",
            "check-out",
            "contribute",
            "donate",
            "order",
            "plain",
            "reload",
            "rent",
            "subscribe",
            "support",
            "tip",
            "top-up",
        ]
        | None
    ) = None
    google_pay: (
        Literal[
            "book",
            "buy",
            "checkout",
            "donate",
            "order",
            "pay",
            "plain",
            "subscribe",
        ]
        | None
    ) = None
    paypal: Literal["paypal", "buynow", "checkout", "pay"] | None = None


class PaymentMethods(PropsBase):
    """Payment method visibility options."""

    apple_pay: Literal["always", "auto", "never"] | None = None
    google_pay: Literal["always", "auto", "never"] | None = None
    link: Literal["auto", "never"] | None = None
    paypal: Literal["auto", "never"] | None = None


class ExpressCheckoutOptions(PropsBase):
    """Options for ExpressCheckoutElement.

    See: https://docs.stripe.com/elements/express-checkout-element
    """

    button_height: int | None = None
    button_theme: ButtonTheme | None = None
    button_type: ButtonType | None = None
    layout: ExpressCheckoutLayout | None = None
    payment_methods: PaymentMethods | None = None
    payment_method_order: list[str] | None = None
    email_required: bool | None = None
    phone_number_required: bool | None = None
