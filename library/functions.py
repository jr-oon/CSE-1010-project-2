def calc_balance(income: float, expenses_total: float) -> float:
    return float(income) - float(expenses_total)


def financial_status_msg(balance: float) -> str:
    if balance > 0:
        return "Great! You are saving money."
    if balance == 0:
        return "You are breaking even."
    return "WARNING: You are overspending."


def parse_float(s: str) -> tuple[bool, float]:
    try:
        return True, float(s)
    except (TypeError, ValueError):
        return False, 0.0


def format_currency(x: float, symbol: str = "$") -> str:
    return f"{symbol}{x:,.2f}"
