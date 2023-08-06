""" This Module is created to enable Hepsiburada Data Science team to log Python Applications. """

import os
import logging

# from logging.handlers import RotatingFileHandler
# from pathlib import Path


from colorama import Fore, init
from google.oauth2 import service_account
import google.cloud.logging as gcp_logging
from google.cloud.logging_v2.handlers import CloudLoggingHandler

init(autoreset=True)


class LoggingOperations:
    """This class is created to enable Hepsiburada Data Science team to log Python Applications."""

    def __init__(self, **kwargs) -> None:
        self.gcp_key = kwargs.get("gcp_key_path")
        self.logger_name = kwargs.get("logger_name")
        self.project = kwargs.get("project")
        self.submodule = kwargs.get("submodule")
        self.credentials = kwargs.get("gcp_key_path")
        self.logger = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(Project ID: {self.credentials.project_id}, "
            f"Service Account: {self.credentials._service_account_email.split('@')[0]}, "
            f"Logger Name: {self.logger_name}, "
            f"Project: {self.project}, Submodule: {self.submodule})"
        )

    def set_logger(self):
        """This function is to set logger."""
        # root_dir = Path(__file__).parent.parent
        # log_file = f"reports/logs/{self.project}_{self.submodule}.log"
        # log_file_path = root_dir.joinpath(log_file)
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.DEBUG)

        # file_handler = RotatingFileHandler(
        #     log_file_path, "a", 10 * 1024 * 1024, 5, "utf-8"
        # )
        # file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)2s() - %(message)s"
        )

        gcloud_logging_client = gcp_logging.Client(
            project=self.credentials.project_id, credentials=self.credentials
        )
        gcloud_logging_handler = CloudLoggingHandler(
            gcloud_logging_client, name=self.logger_name
        )
        # file_handler.setFormatter(formatter)
        gcloud_logging_handler.setFormatter(formatter)
        gcloud_logging_handler.setLevel(logging.DEBUG)

        # self.logger.addHandler(file_handler)
        self.logger.addHandler(gcloud_logging_handler)
        self.logger.info(msg="Logger has been initiated! ")

    @property
    def gcp_key(self):
        """This function is to get GCP key."""
        return self._gcp_key

    @gcp_key.setter
    def gcp_key(self, provided_gcp_key):
        """This function is to set GCP key."""
        if provided_gcp_key is not None:
            self._gcp_key = str(provided_gcp_key)
            self.credentials = str(provided_gcp_key)
        elif os.environ.get("SERVICE_ACCOUNT_KEY_PATH"):
            self._gcp_key = os.environ.get("SERVICE_ACCOUNT_KEY_PATH")
        else:
            self._gcp_key = None
            print(
                Fore.RED + "Warning!! GCP Key Path for Service Account is not specified"
            )

    @property
    def credentials(self):
        """This function is to get credentials."""
        return self._credentials

    @credentials.setter
    def credentials(self, provided_credentials):
        """This function is to set credentials."""
        if provided_credentials is not None:
            self._credentials = service_account.Credentials.from_service_account_file(
                self.gcp_key,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        elif os.environ.get("SERVICE_ACCOUNT_KEY_PATH"):
            self._credentials = service_account.Credentials.from_service_account_file(
                self.gcp_key,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        else:
            self._credentials = None
            print(
                Fore.RED + "Warning!! Credentials for Service Account is not specified"
            )
