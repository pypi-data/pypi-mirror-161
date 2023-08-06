"""SCEX Client for making requests to the SCE Server"""

import logging

from .api_handler import ApiHandler
from .constants import (
    BALLOON_PAYMENT_FINAL_INPUT_XML,
    BALLOON_PAYMENT_REGULAR_INPUT_XML,
    EQUAL_PAYMENT_INPUT_XML,
    MULTI_TERM_PAYMENT_INPUT_XML,
    AccrualCode,
    PaymentsPerYear,
)
from .utils import ValidationError, validate_inputs

LOGGER = logging.getLogger("root")


class ScexClient:
    def __init__(self, host: str, api_key: str):
        self.__request_url = f"{host}/scex/api/v1/request"
        self._api_handler = ApiHandler(self.__request_url, api_key)

    @property
    def url(self):
        return self.__request_url

    def __initialize_defaults(self, options: dict):
        LOGGER.info("Setting default values")

        options.setdefault("Account", 1)
        options.setdefault("DataDirPath", "/etc/sce/*")
        options.setdefault("AccrualCode", AccrualCode.ACTUAL_360_US_RULE.value)
        options.setdefault("AprType", "default")
        options.setdefault("UseMAPR", "false")
        options.setdefault("HideAmort", "false")
        options.setdefault("Lastday", "false")
        options.setdefault("OddFinal", "true")
        options.setdefault("ValidateInput", "true")
        options.setdefault("ValidateOutput", "true")
        options.setdefault("TotalDown", 0)

        if "PPY" not in options:
            options["PPY"] = PaymentsPerYear.MONTHLY.value[0]
        else:
            try:
                PaymentsPerYear(options["PPY"])
            except ValueError:
                raise ValidationError("Invalid payment schedule")

        options["TilaRespa"] = "<TILARESPA2015/>" if "TilaRespa" in options else ""

        LOGGER.info("Validating equal payment loan input")
        validate_inputs(options)

        return options

    # def load_logger(self, logging_config=LOGGING_CONFIG):
    #     logging.config.dictConfig(LOGGING_CONFIG)
    #     LOGGER = logging.getLogger("scex_py")

    def process_equal_payment_loan(self, options: dict, log_config: dict = None):
        options = self.__initialize_defaults(options)
        LOGGER.info("Loading raw XML for Equal Payment Loan")

        with open(EQUAL_PAYMENT_INPUT_XML) as equal_payment_input_file:
            equal_payment_input = equal_payment_input_file.read()

        equal_payment_input = equal_payment_input.format(**options)

        LOGGER.info("Calculating Equal Payment loan")
        return self._api_handler.send_request("POST", payload=equal_payment_input, log_config=log_config)

    def process_multi_term_payment_loan(self, options: dict, log_config: dict = None):
        options = self.__initialize_defaults(options)
        LOGGER.info("Loading raw XML for Multi Term Payment Loan")

        with open(MULTI_TERM_PAYMENT_INPUT_XML) as multi_term_payment_input_file:
            multi_term_payment_input = multi_term_payment_input_file.read()

        multi_term_payment_input = multi_term_payment_input.format(**options)

        LOGGER.info("Calculating Multi Term Payment loan")
        return self._api_handler.send_request("POST", payload=multi_term_payment_input, log_config=log_config)

    def process_balloon_payment_loan_regular(self, options: dict, log_config: dict = None):
        options = self.__initialize_defaults(options)

        if "RegPmt" not in options:
            raise ValidationError("Regular Payment value is required")

        LOGGER.info("Loading raw XML for Balloon Payment Loan with Regular Payment")

        with open(BALLOON_PAYMENT_REGULAR_INPUT_XML) as balloon_regular_payment_input_file:
            balloon_regular_payment_input = balloon_regular_payment_input_file.read()

        balloon_regular_payment_input = balloon_regular_payment_input.format(**options)

        LOGGER.info("Calculating Balloon Payment loan with Regular Payment")
        return self._api_handler.send_request("POST", payload=balloon_regular_payment_input, log_config=log_config)

    def process_balloon_payment_loan_final(self, options: dict, log_config: dict = None):
        options = self.__initialize_defaults(options)

        if "FinalPmt" not in options:
            raise ValidationError("Final Payment value is required")

        LOGGER.info("Loading raw XML for Balloon Payment Loan with Final Payment")

        with open(BALLOON_PAYMENT_FINAL_INPUT_XML) as balloon_final_payment_input_file:
            balloon_final_payment_input = balloon_final_payment_input_file.read()

        balloon_final_payment_input = balloon_final_payment_input.format(**options)

        LOGGER.info("Calculating Balloon Payment loan with Final Payment")
        return self._api_handler.send_request("POST", payload=balloon_final_payment_input, log_config=log_config)
