#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

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


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    date_parts_count = 3
    day_digits = 2
    year_digits = 4
    months_in_year = 12
    feb_index = 2
    feb_leap_days = 29

    parts = maybe_dt.split("-")
    if len(parts) != date_parts_count:
        return None

    if not all(part.isdigit() for part in parts):
        return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if (len(parts[0]) != day_digits or
            len(parts[1]) != day_digits or
            len(parts[2]) != year_digits):
        return None

    if day < 1 or month < 1 or month > months_in_year or year < 1:
        return None

    days_in_month = [
        0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ]
    if is_leap_year(year):
        days_in_month[feb_index] = feb_leap_days

    if day > days_in_month[month]:
        return None

    return (day, month, year)


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append(
        {"type": "income", "amount": amount, "date": date}
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    category_parts_count = 2
    parts = category_name.split("::")
    if len(parts) != category_parts_count:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    common, target = parts
    if common not in EXPENSE_CATEGORIES:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    if target not in EXPENSE_CATEGORIES[common]:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {"type": "cost", "category": category_name, "amount": amount, "date": date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines: list[str] = []
    for common, targets in EXPENSE_CATEGORIES.items():
        lines.extend(f"{common}::{target}" for target in targets)
    return "\n".join(lines)


def _calculate_capital(query_date: tuple[int, int, int]) -> float:
    capital = 0
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        day, month, year = transaction["date"]
        if (year, month, day) > (query_date[2], query_date[1], query_date[0]):
            continue
        if transaction["type"] == "income":
            capital += transaction["amount"]
        else:
            capital -= transaction["amount"]
    return capital


def _calculate_month_income(query_date: tuple[int, int, int]) -> float:
    month_income = 0
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        _, month, year = transaction["date"]
        if transaction["type"] != "income":
            continue
        if year == query_date[2] and month == query_date[1]:
            month_income += transaction["amount"]
    return month_income


def _calculate_month_cost(query_date: tuple[int, int, int]) -> tuple[float, dict[str, float]]:
    month_cost = 0
    costs: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        _, month, year = transaction["date"]
        if transaction["type"] != "cost":
            continue
        if year == query_date[2] and month == query_date[1]:
            amount = transaction["amount"]
            month_cost += amount
            category = transaction["category"]
            costs[category] = costs.get(category, 0) + amount
    return month_cost, costs


def stats_handler(report_date: str) -> str:
    query_date = extract_date(report_date)
    if query_date is None:
        return INCORRECT_DATE_MSG

    capital = _calculate_capital(query_date)
    month_income = _calculate_month_income(query_date)
    month_cost, costs = _calculate_month_cost(query_date)

    budget = month_income - month_cost
    direction = "loss" if budget < 0 else "profit"

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {capital:.2f} rubles",
        f"This month, the {direction} amounted to {abs(budget):.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_cost:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    if costs:
        sorted_items = sorted(costs.items(), key=lambda x: x[0])
        for idx, (category, value) in enumerate(sorted_items, 1):
            if value == int(value):
                lines.append(f"{idx}. {category}: {int(value)}")
            else:
                lines.append(f"{idx}. {category}: {value}")

    return "\n".join(lines)


def _handle_income(parts: list[str]) -> None:
    income_args = 3
    if len(parts) != income_args:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount = float(parts[1].replace(",", "."))
    result = income_handler(amount, parts[2])
    print(result)


def _handle_cost(parts: list[str]) -> None:
    cost_categories_args = 2
    cost_args = 4
    if len(parts) == cost_categories_args and parts[1] == "categories":
        print(cost_categories_handler())
        return
    if len(parts) != cost_args:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount = float(parts[2].replace(",", "."))
    result = cost_handler(parts[1], amount, parts[3])
    print(result)
    if result == NOT_EXISTS_CATEGORY:
        print(cost_categories_handler())


def _handle_stats(parts: list[str]) -> None:
    stats_args = 2
    if len(parts) != stats_args:
        print(UNKNOWN_COMMAND_MSG)
        return
    result = stats_handler(parts[1])
    print(result)


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
