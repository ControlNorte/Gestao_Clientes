from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def _to_decimal(value) -> Decimal:
    if value in (None, "", "-"):
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


@register.filter
def currency(value) -> str:
    number = _to_decimal(value).quantize(Decimal("0.01"))
    formatted = f"{number:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


@register.filter
def currency_value(value) -> str:
    number = _to_decimal(value).quantize(Decimal("0.01"))
    formatted = f"{number:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


@register.filter
def currency_value_or_dash(value) -> str:
    number = _to_decimal(value).quantize(Decimal("0.01"))
    if number == 0:
        return "-"
    formatted = f"{number:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


@register.filter
def dash_number(value) -> str:
    number = _to_decimal(value)
    if number == 0:
        return "-"
    if number == int(number):
        return str(int(number))
    return str(number)


@register.filter
def number_format(value) -> str:
    if value in (None, "", "-"):
        return "0"
    try:
        if isinstance(value, float):
            number = int(value)
        else:
            number = int(value)
    except (ValueError, TypeError):
        try:
            number = int(float(value))
        except (ValueError, TypeError):
            return str(value)
    formatted = f"{number:,}".replace(",", ".")
    return formatted


@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
