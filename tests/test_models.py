"""Tests for PropsBase configuration models."""

from reflex_stripe.models import (
    Appearance,
    ButtonTheme,
    ButtonType,
    ExpressCheckoutLayout,
    ExpressCheckoutOptions,
    PaymentMethods,
    Variables,
)


def test_variables_defaults():
    v = Variables()
    assert v.color_primary == ""
    assert v.font_family == ""
    assert v.border_radius == ""


def test_variables_custom():
    v = Variables(color_primary="#6772e5", border_radius="8px", font_family="Roboto")
    assert v.color_primary == "#6772e5"
    assert v.border_radius == "8px"
    assert v.font_family == "Roboto"


def test_appearance_defaults():
    a = Appearance()
    assert a.theme is None
    assert a.variables is None
    assert a.rules is None
    assert a.labels is None
    assert a.disable_animations is None


def test_appearance_with_theme():
    a = Appearance(theme="night")
    assert a.theme == "night"


def test_appearance_with_variables():
    v = Variables(color_primary="#6772e5")
    a = Appearance(theme="stripe", variables=v)
    assert a.theme == "stripe"
    assert a.variables is not None
    assert a.variables.color_primary == "#6772e5"


def test_appearance_with_rules():
    a = Appearance(
        rules={".Input": {"border": "1px solid #e0e0e0", "fontSize": "14px"}}
    )
    assert a.rules is not None
    assert ".Input" in a.rules


def test_express_checkout_layout():
    layout = ExpressCheckoutLayout(max_columns=2, max_rows=3, overflow="auto")
    assert layout.max_columns == 2
    assert layout.max_rows == 3
    assert layout.overflow == "auto"


def test_button_theme():
    bt = ButtonTheme(apple_pay="white-outline", google_pay="black")
    assert bt.apple_pay == "white-outline"
    assert bt.google_pay == "black"
    assert bt.paypal is None


def test_button_type():
    bt = ButtonType(apple_pay="buy", google_pay="checkout", paypal="buynow")
    assert bt.apple_pay == "buy"
    assert bt.google_pay == "checkout"
    assert bt.paypal == "buynow"


def test_payment_methods():
    pm = PaymentMethods(apple_pay="always", google_pay="auto", link="never")
    assert pm.apple_pay == "always"
    assert pm.google_pay == "auto"
    assert pm.link == "never"
    assert pm.paypal is None


def test_express_checkout_options_defaults():
    opts = ExpressCheckoutOptions()
    assert opts.button_height is None
    assert opts.button_theme is None
    assert opts.button_type is None
    assert opts.layout is None
    assert opts.payment_methods is None
    assert opts.payment_method_order is None


def test_express_checkout_options_full():
    opts = ExpressCheckoutOptions(
        button_height=50,
        button_theme=ButtonTheme(apple_pay="black"),
        button_type=ButtonType(google_pay="pay"),
        layout=ExpressCheckoutLayout(max_rows=2, overflow="auto"),
        payment_methods=PaymentMethods(link="auto"),
        payment_method_order=["apple_pay", "google_pay"],
        email_required=True,
        phone_number_required=False,
    )
    assert opts.button_height == 50
    assert opts.button_theme.apple_pay == "black"
    assert opts.button_type.google_pay == "pay"
    assert opts.layout.max_rows == 2
    assert opts.payment_methods.link == "auto"
    assert opts.payment_method_order == ["apple_pay", "google_pay"]
    assert opts.email_required is True
    assert opts.phone_number_required is False
