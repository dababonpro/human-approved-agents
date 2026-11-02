"""Order pricing. Amounts are in pence to avoid float rounding."""

DISCOUNT_CODES = {
    "SPRING10": 10,
    "TRADE15": 15,
}

FREE_SHIPPING_THRESHOLD = 5000  # pence
SHIPPING = 495


def apply_discount(subtotal: int, code: str | None) -> int:
    """Return the subtotal after the percentage discount for `code`."""
    if not code:
        return subtotal
    percent = DISCOUNT_CODES.get(code.upper(), 0)
    return subtotal - (subtotal * percent) // 100


def shipping_for(subtotal: int) -> int:
    """Free shipping at or above the threshold."""
    if subtotal > FREE_SHIPPING_THRESHOLD:
        return 0
    return SHIPPING


def calc_total(lines: list[tuple[int, int]], code: str | None = None) -> int:
    """lines are (unit_price_pence, quantity). Returns the order total in pence."""
    subtotal = sum(price * qty for price, qty in lines)
    discounted = apply_discount(subtotal, code)
    if code:
        discounted = apply_discount(discounted, code)
    return discounted + shipping_for(discounted)
