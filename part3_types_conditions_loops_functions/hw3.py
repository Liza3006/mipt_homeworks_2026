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

TYPE = "type"
AMOUNT = "amount"
DATE = "date"
CATEGORY = "category"
INCOME = "income"
COST = "cost"

CONST2 = 2
CONST3 = 3
CONST4 = 4
CONST12 = 12


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return not (year % 100 == 0 and year % 400 != 0)


def _is_valid_values(parts: list[str]) -> bool:
    if int(parts[0]) < 1:
        return False
    if int(parts[1]) < 1:
        return False
    if int(parts[1]) > CONST12:
        return False
    return not int(parts[2]) < 1


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    flag = 0

    if len(parts) != CONST3:
        flag = 1
    if not all(part.isdigit() for part in parts):
        flag = 1

    if (len(parts[0]) != CONST2 or
            len(parts[1]) != CONST2 or
            len(parts[2]) != CONST4):
        flag = 1

    if flag:
        return None

    if not _is_valid_values(parts):
        flag = 1

    days_in_month = [
        0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ]
    if is_leap_year(int(parts[2])):
        days_in_month[2] = 29

    if int(parts[0]) > days_in_month[int(parts[1])]:
        flag = 1

    if flag:
        return None

    ans1 = int(parts[0])
    return ans1, int(parts[1]), int(parts[2])


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append(
        {TYPE: INCOME, AMOUNT: amount, DATE: date}
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
    if (common not in EXPENSE_CATEGORIES) or target not in EXPENSE_CATEGORIES[common]:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {TYPE: COST, CATEGORY: category_name, AMOUNT: amount, DATE: date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines: list[str] = []
    for common, targets in EXPENSE_CATEGORIES.items():
        lines.extend(f"{common}::{target}" for target in targets)
    return "\n".join(lines)


def _is_date_after(date1: tuple[int, int, int],
                   date2: tuple[int, int, int]) -> bool:
    if date1[2] > date2[2]:
        return True
    if date1[2] < date2[2]:
        return False

    if date1[1] > date2[1]:
        return True
    if date1[1] < date2[1]:
        return False

    return date1[0] > date2[0]


def _calculate_capital(query_date: tuple[int, int, int]) -> float:
    capital = 0
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        day, month, year = transaction[DATE]
        if _is_date_after((day, month, year), query_date):
            continue
        if transaction[TYPE] == INCOME:
            capital += transaction[AMOUNT]
        else:
            capital -= transaction[AMOUNT]
    return capital


def _calculate_month_income(query_date: tuple[int, int, int]) -> float:
    month_income = 0
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        _, month, year = transaction[DATE]
        if (transaction[TYPE] == INCOME
                and year == query_date[2]
                and month == query_date[1]):
            month_income += transaction[AMOUNT]
    return month_income


def _is_same_month(
        date: tuple[int, int, int],
        query: tuple[int, int, int]
) -> bool:
    month = date[1]
    year = date[2]
    q_month = query[1]
    q_year = query[2]
    return month == q_month and year == q_year


def _calculate_month_cost(
        query_date: tuple[int, int, int]
) -> tuple[float, dict[str, float]]:
    month_cost = 0
    costs: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        if transaction["type"] != "cost":
            continue
        if _is_same_month(transaction[DATE], query_date):
            month_cost += transaction[AMOUNT]
            category = transaction["category"]
            costs[category] = (costs.get(category, 0) + transaction[AMOUNT])
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
        INCOME: _handle_income,
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
