import logging

import requests

from .constants import API_KEY_HEADER

LOGGER = logging.getLogger("root")


class ApiHandler:
    """Base class for calling any external APIs"""

    REQUEST_TIMEOUT = 30

    def __init__(self, url: str, api_key: str, logging: bool = True):
        self._url = url
        self.__api_key = api_key
        self.__logging = logging

    @property
    def url(self):
        return self._url

    def get_headers(self, **kwargs):
        """Builds and return headers for each request"""
        kwargs.setdefault("Content-Type", "application/xml")
        kwargs.setdefault(API_KEY_HEADER, self.__api_key)
        return kwargs

    def send_request(
        self,
        method,
        params=None,
        payload=None,
        log_config: dict = None,
        headers: dict = None,
    ):
        """Send API request for the given URL with the specified method, params and payload"""
        if not headers:
            headers = self.get_headers()

        if self.__logging:
            LOGGER.info("[SCEX] - [%s: %s]", method, self.url)

        log_entry = None

        if log_config:
            if (
                "model" not in log_config
                or "user" not in log_config
                or "loan" not in log_config
                or "timezone" not in log_config
            ):
                raise Exception("Invalid log dict")

        try:
            if log_config:
                log_entry = log_config["model"](
                    loan=log_config["loan"],
                    requested_by=log_config["user"],
                    request_url=f"{method}: {self.url}",
                    request_headers=headers,
                    request_body=payload,
                    request_time=log_config["timezone"].now(),
                )

            response = requests.request(
                method,
                self.url,
                timeout=self.REQUEST_TIMEOUT,
                headers=headers,
                params=params,
                data=payload,
            )

            if self.__logging:
                LOGGER.info(
                    "Received [%s] response for [%s: %s]",
                    response.status_code,
                    method,
                    self.url,
                )

            if log_entry:
                log_entry.response_code = response.status_code
                log_entry.response_body = response.text
                log_entry.response_time = log_entry.request_time + response.elapsed
                log_entry.save()

            response.raise_for_status()
            return response
        except requests.HTTPError as excp:
            if self.__logging:
                LOGGER.error(
                    "SCEX API Failed. Received [%s] response for [%s: %s]",
                    response.status_code,
                    method,
                    self.url,
                )

            raise Exception(f"Failed to get success response from SCEX. Response: [{response.text}]") from excp
