#!/usr/bin/env python

from typing import Any

MonthCostResult = tuple[float, dict[str, float]]

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


def _check_date_format(parts: list[str]) -> bool:
    expected_parts = 3
    if len(parts) != expected_parts:
        return False
    return all(part.isdigit() for part in parts)


def _check_date_lengths(parts: list[str]) -> bool:
    day_digits = 2
    year_digits = 4
    if len(parts[0]) != day_digits:
        return False
    if len(parts[1]) != day_digits:
        return False
    return len(parts[2]) == year_digits


def _check_date_range(day: int, month: int, year: int) -> bool:
    months_in_year = 12
    if day < 1:
        return False
    if month < 1:
        return False
    if month > months_in_year:
        return False
    return not year < 1


def _check_day_in_month(day: int, month: int, year: int) -> bool:
    days_in_month = [
        0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ]
    if is_leap_year(year):
        days_in_month[2] = 29
    return not day > days_in_month[month]


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if not _check_date_format(parts):
        return None
    if not _check_date_lengths(parts):
        return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if not _check_date_range(day, month, year):
        return None
    if not _check_day_in_month(day, month, year):
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
    transaction = {
        "type": "income",
        "amount": amount,
        "date": date
    }
    financial_transactions_storage.append(transaction)
    return OP_SUCCESS_MSG


def _check_category(category_name: str) -> bool:
    category_parts = 2
    parts = category_name.split("::")
    if len(parts) != category_parts:
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
    transaction = {
        "type": "cost",
        "category": category_name,
        "amount": amount,
        "date": date
    }
    financial_transactions_storage.append(transaction)
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines: list[str] = []
    for common, targets in EXPENSE_CATEGORIES.items():
        lines.extend(f"{common}::{target}" for target in targets)
    return "\n".join(lines)


def _compare_years(t_year: int, q_year: int) -> int:
    if t_year < q_year:
        return -1
    if t_year > q_year:
        return 1
    return 0


def _compare_months(t_month: int, q_month: int) -> int:
    if t_month < q_month:
        return -1
    if t_month > q_month:
        return 1
    return 0


def _compare_dates(t_date: tuple[int, int, int], q_date: tuple[int, int, int]) -> bool:
    if t_date[2] < q_date[2]:
        return True
    if t_date[2] > q_date[2]:
        return False
    if t_date[1] < q_date[1]:
        return True
    if t_date[1] > q_date[1]:
        return False
    return t_date[0] <= q_date[0]


def _calculate_capital(query_date: tuple[int, int, int]) -> float:
    capital = 0
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        if not _compare_dates(transaction["date"], query_date):
            continue
        if transaction["type"] == "income":
            capital = capital + transaction["amount"]
        else:
            capital = capital - transaction["amount"]
    return capital


def _is_month_match(transaction: dict[str, Any], target_year: int, target_month: int) -> bool:
    _, month, year = transaction["date"]
    if year != target_year:
        return False
    return month == target_month


def _calculate_month_income(query_date: tuple[int, int, int]) -> float:
    target_year = query_date[2]
    target_month = query_date[1]
    month_income = 0
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        if transaction["type"] != "income":
            continue
        if _is_month_match(transaction, target_year, target_month):
            month_income = month_income + transaction["amount"]
    return month_income


def _add_cost_to_stats(month_cost: float, costs: dict[str, float],
                       amount: float, category: str) -> tuple[float, dict[str, float]]:
    new_cost = month_cost + amount
    new_costs = costs.copy()
    new_costs[category] = new_costs.get(category, 0) + amount
    return new_cost, new_costs


def _process_cost(transaction: dict[str, Any], target_year: int, target_month: int,
                  month_cost: float, costs: dict[str, float]) -> tuple[float, dict[str, float]]:
    if not _is_month_match(transaction, target_year, target_month):
        return month_cost, costs
    if transaction["type"] != "cost":
        return month_cost, costs
    return _add_cost_to_stats(month_cost, costs, transaction["amount"], transaction["category"])


def _calculate_month_cost(query_date: tuple[int, int, int]) -> tuple[float, dict[str, float]]:
    target_year = query_date[2]
    target_month = query_date[1]
    month_cost = 0
    costs: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        month_cost, costs = _process_cost(transaction, target_year, target_month, month_cost, costs)
    return month_cost, costs


def _format_category_line(idx: int, category: str, value: float) -> str:
    if value == int(value):
        return f"{idx}. {category}: {int(value)}"
    return f"{idx}. {category}: {value}"


def _build_stats_lines(stats: tuple[float, float, float, dict[str, float]], report_date: str) -> list[str]:
    capital, month_income, month_cost, costs = stats
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {capital:.2f} rubles",
        f"This month, the {'loss' if month_income - month_cost < 0 else 'profit'} "
        f"amounted to {abs(month_income - month_cost):.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_cost:.2f} rubles",
        "",
        "Details (category: amount):",
    ]
    for idx, (category, value) in enumerate(sorted(costs.items()), 1):
        lines.append(_format_category_line(idx, category, value))
    return lines


def stats_handler(report_date: str) -> str:
    query_date = extract_date(report_date)
    if query_date is None:
        return INCORRECT_DATE_MSG
    stats = (
        _calculate_capital(query_date),
        _calculate_month_income(query_date),
        *_calculate_month_cost(query_date)
    )
    return "\n".join(_build_stats_lines(stats, report_date))


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
