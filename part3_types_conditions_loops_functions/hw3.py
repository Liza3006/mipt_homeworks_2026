#!/usr/bin/env python

from typing import Any

MonthCostResult = tuple[float, dict[str, float]]

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

# Date constants
DATE_PARTS_COUNT = 3
DAY_DIGITS = 2
MONTH_DIGITS = 2
YEAR_DIGITS = 4
MONTHS_IN_YEAR = 12

# Category constants
CATEGORY_PARTS_COUNT = 2

# Command argument counts
INCOME_ARGS = 3
COST_ARGS = 4
COST_CATEGORIES_ARGS = 2
STATS_ARGS = 2

# Transaction keys
KEY_TYPE = "type"
KEY_AMOUNT = "amount"
KEY_DATE = "date"
KEY_CATEGORY = "category"

# Transaction types
TYPE_INCOME = "income"
TYPE_COST = "cost"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return not (year % 100 == 0 and year % 400 != 0)


def _check_date_format(parts: list[str]) -> bool:
    if len(parts) != DATE_PARTS_COUNT:
        return False
    return all(part.isdigit() for part in parts)


def _check_date_lengths(parts: list[str]) -> bool:
    if len(parts[0]) != DAY_DIGITS:
        return False
    if len(parts[1]) != MONTH_DIGITS:
        return False
    return len(parts[2]) == YEAR_DIGITS


def _check_date_range(day: int, month: int, year: int) -> bool:
    if day < 1:
        return False
    if month < 1:
        return False
    if month > MONTHS_IN_YEAR:
        return False
    return year >= 1


def _check_day_in_month(day: int, month: int, year: int) -> bool:
    days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if is_leap_year(year):
        days[2] = 29
    return day <= days[month]


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if not _check_date_format(parts):
        return None
    if not _check_date_lengths(parts):
        return None

    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])

    if not _check_date_range(day, month, year):
        return None
    if not _check_day_in_month(day, month, year):
        return None

    return (day, month, year)


def _create_transaction(trans_type: str, amount: float, date: tuple[int, int, int],
                        category: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        KEY_TYPE: trans_type,
        KEY_AMOUNT: amount,
        KEY_DATE: date,
    }
    if category:
        result[KEY_CATEGORY] = category
    return result


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append(
        _create_transaction(TYPE_INCOME, amount, date)
    )
    return OP_SUCCESS_MSG


def _check_category(category_name: str) -> bool:
    parts = category_name.split("::")
    if len(parts) != CATEGORY_PARTS_COUNT:
        return False
    common, target = parts
    if common not in EXPENSE_CATEGORIES:
        return False
    return target in EXPENSE_CATEGORIES[common]


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    if not _check_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    financial_transactions_storage.append(
        _create_transaction(TYPE_COST, amount, date, category_name)
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines: list[str] = []
    for common, targets in EXPENSE_CATEGORIES.items():
        lines.extend(f"{common}::{target}" for target in targets)
    return "\n".join(lines)


def _compare_dates(t_date: tuple[int, int, int], q_date: tuple[int, int, int]) -> bool:
    t_year, t_month, t_day = t_date[2], t_date[1], t_date[0]
    q_year, q_month, q_day = q_date[2], q_date[1], q_date[0]
    if t_year != q_year:
        return t_year < q_year
    if t_month != q_month:
        return t_month < q_month
    return t_day <= q_day


def _calculate_capital(query_date: tuple[int, int, int]) -> float:
    capital = 0.0
    for trans in financial_transactions_storage:
        if not trans:
            continue
        if not _compare_dates(trans[KEY_DATE], query_date):
            continue
        sign = 1 if trans[KEY_TYPE] == TYPE_INCOME else -1
        capital += sign * trans[KEY_AMOUNT]
    return capital


def _is_month_match(transaction: dict[str, Any], target_year: int, target_month: int) -> bool:
    _, month, year = transaction[KEY_DATE]
    return year == target_year and month == target_month


def _calculate_month_income(query_date: tuple[int, int, int]) -> float:
    target_year, target_month = query_date[2], query_date[1]
    month_income = 0.0
    for trans in financial_transactions_storage:
        if not trans:
            continue
        if trans[KEY_TYPE] != TYPE_INCOME:
            continue
        if _is_month_match(trans, target_year, target_month):
            month_income += trans[KEY_AMOUNT]
    return month_income


def _calculate_month_cost(query_date: tuple[int, int, int]) -> MonthCostResult:
    target_year, target_month = query_date[2], query_date[1]
    month_cost = 0.0
    costs: dict[str, float] = {}
    for trans in financial_transactions_storage:
        if not trans:
            continue
        if trans[KEY_TYPE] != TYPE_COST:
            continue
        if not _is_month_match(trans, target_year, target_month):
            continue
        month_cost += trans[KEY_AMOUNT]
        cat = trans[KEY_CATEGORY]
        costs[cat] = costs.get(cat, 0) + trans[KEY_AMOUNT]
    return month_cost, costs


def _format_category_line(idx: int, category: str, value: float) -> str:
    if value == int(value):
        return f"{idx}. {category}: {int(value)}"
    return f"{idx}. {category}: {value}"


def _get_budget_info(income: float, cost: float) -> tuple[str, float]:
    diff = income - cost
    direction = "loss" if diff < 0 else "profit"
    return direction, abs(diff)


def _build_stats_header(capital: float, report_date: str) -> list[str]:
    return [
        f"Your statistics as of {report_date}:",
        f"Total capital: {capital:.2f} rubles",
    ]


def _build_stats_budget(income: float, cost: float) -> list[str]:
    direction, amount = _get_budget_info(income, cost)
    return [
        f"This month, the {direction} amounted to {amount:.2f} rubles.",
        f"Income: {income:.2f} rubles",
        f"Expenses: {cost:.2f} rubles",
    ]


def _build_stats_details(costs: dict[str, float]) -> list[str]:
    lines = ["", "Details (category: amount):"]
    for idx, (category, value) in enumerate(sorted(costs.items()), 1):
        lines.append(_format_category_line(idx, category, value))
    return lines


def _build_stats_lines(stats: tuple[float, float, float, dict[str, float]],
                       report_date: str) -> list[str]:
    capital, month_income, month_cost, costs = stats
    result = _build_stats_header(capital, report_date)
    result.extend(_build_stats_budget(month_income, month_cost))
    result.extend(_build_stats_details(costs))
    return result


def stats_handler(report_date: str) -> str:
    query_date = extract_date(report_date)
    if query_date is None:
        return INCORRECT_DATE_MSG
    capital = _calculate_capital(query_date)
    month_income = _calculate_month_income(query_date)
    month_cost, costs = _calculate_month_cost(query_date)
    stats = (capital, month_income, month_cost, costs)
    return "\n".join(_build_stats_lines(stats, report_date))


def _handle_income(parts: list[str]) -> None:
    if len(parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount = float(parts[1].replace(",", "."))
    print(income_handler(amount, parts[2]))


def _handle_cost(parts: list[str]) -> None:
    if len(parts) == COST_CATEGORIES_ARGS and parts[1] == "categories":
        print(cost_categories_handler())
        return
    if len(parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount = float(parts[2].replace(",", "."))
    result = cost_handler(parts[1], amount, parts[3])
    print(result)
    if result == NOT_EXISTS_CATEGORY:
        print(cost_categories_handler())


def _handle_stats(parts: list[str]) -> None:
    if len(parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return
    print(stats_handler(parts[1]))


def main() -> None:
    handlers = {
        "income": _handle_income,
        "cost": _handle_cost,
        "stats": _handle_stats,
    }
    line = input()
    while line:
        parts = line.split()
        if parts:
            handler = handlers.get(parts[0])
            if handler:
                handler(parts)
            else:
                print(UNKNOWN_COMMAND_MSG)
        line = input()


if __name__ == "__main__":
    main()
