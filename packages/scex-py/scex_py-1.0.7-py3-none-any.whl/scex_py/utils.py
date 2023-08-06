"""Module for defining utilities"""

from datetime import datetime

from .constants import AccrualCode


class ValidationError(Exception):
    pass


def validate_date_input(options: dict, key: str):
    try:
        datetime.strptime(options[key], "%Y-%m-%d")
    except KeyError:
        raise ValidationError(f"{key} is required")
    except ValueError:
        raise ValidationError("Date should be in `%Y-%m-%d` format")


def validate_inputs(options: dict):
    validate_date_input(options, "LoanDate")
    validate_date_input(options, "PmtDate")
    validate_date_input(options, "IntStartDate")

    if "Proceeds" not in options:
        raise ValidationError("Proceeds is required")

    if "Term" not in options:
        raise ValidationError("Term is required")

    if "IntRate" not in options or "FirstTermRate" not in options:
        raise ValidationError("IntRate or FirstTermRate is required")

    try:
        AccrualCode(options["AccrualCode"])
    except ValueError:
        raise ValidationError("Accural code not supported")
