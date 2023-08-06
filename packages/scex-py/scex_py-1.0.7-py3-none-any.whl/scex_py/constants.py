"""Module for storing constants for the SCEX Client package"""

from enum import Enum
from pathlib import Path

API_KEY_HEADER = "x-sce-apikey"

BASE_DIR = Path(__file__).resolve().parent
EQUAL_PAYMENT_INPUT_XML = BASE_DIR.joinpath("input_xml", "equal_payment_loan.xml")
MULTI_TERM_PAYMENT_INPUT_XML = BASE_DIR.joinpath("input_xml", "multi_term_payment_loan.xml")
BALLOON_PAYMENT_REGULAR_INPUT_XML = BASE_DIR.joinpath("input_xml", "balloon_payment", "regular.xml")
BALLOON_PAYMENT_FINAL_INPUT_XML = BASE_DIR.joinpath("input_xml", "balloon_payment", "final.xml")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "development": {
            "format": (
                "%(process)d  %(thread)d  %(asctime)-25s %(module)-15s %(funcName)-30s %(levelname)-10s -  %(message)s"
            ),
        },
    },
    "handlers": {
        "development": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "development",
        },
    },
    "loggers": {
        "scex_py": {
            "handlers": ["development"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


class AccrualCode(Enum):
    ACTUAL_360_SIMPLE = 210
    ACTUAL_365_SIMPLE = 220
    ACTUAL_360_US_RULE = 310
    ACTUAL_365_US_RULE = 320
    UNIT_PERIOD_SIMPLE_WITH_360_DAY_DIVISOR = 201
    UNIT_PERIOD_SIMPLE_WITH_365_DAY_DIVISOR = 202
    UNIT_PERIOD_SIMPLE_WITH_360_CALENDAR_360_DAY_DIVISOR = 204
    UNIT_PERIOD_SIMPLE_WITH_360_CALENDAR_365_DAY_DIVISOR = 205


class PaymentsPerYear(Enum):
    ANNUAL = "annual"
    SEMI_ANNUAL = "semiannual"
    QUATERLY = "quarterly"
    BI_MONTHLY = "bimonthly"
    MONTHLY = "monthly"
    SEMI_MONTHLY = "semimonthly"
    BI_WEEKLY = "biweekly"
    WEEKLY = "weekly"
