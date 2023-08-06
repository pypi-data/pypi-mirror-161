""" This Module is created to enable Hepsiburada Data Science to communicate with BigQuery. """

import os
import sys
import time
import warnings

from colorama import Fore, init  ##Style
from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound, BadRequest

from .read_from_bq_file import bq_command_parser

init(autoreset=True)


class BigQueryOperations(bigquery.Client):
    """This class is created to enable Hepsiburada Data Science to communicate with BigQuery"""

    _implemented_returns = ["dataframe", None]

    def __init__(self, **kwargs) -> None:
        self.gcp_key = kwargs.get("gcp_key_path")
        self.credentials = kwargs.get("gcp_key_path")
        super().__init__(
            project=self.credentials.project_id,
            credentials=self.credentials,
            location="EU",
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(Project ID: {self.credentials.project_id}, "
            f"Service Account: {self.credentials._service_account_email.split('@')[0]})"
        )

    def get_bq_table(self, table_name):
        """This function is to get BQ table."""
        return self.get_table(table_name)

    def execute_query(self, query_string, return_type="dataframe", **kwargs):
        """This function is to query BQ."""
        if return_type not in BigQueryOperations._implemented_returns:
            raise NotImplementedError(
                Fore.RED + f"Return type {return_type} not implemented !!"
            )

        job_config = bigquery.QueryJobConfig()
        job_config.dry_run = True
        try:
            job_result = self.query(query_string, job_config=job_config, **kwargs)
        except BadRequest as bad_request_message:
            raise RuntimeError(
                Fore.RED + f"Query failed with error: {bad_request_message}"
            ) from bad_request_message

        if job_result.total_bytes_processed / (1024 * 1024 * 1024) > 100:
            raise ValueError(
                Fore.RED
                + "Query is trying to process "
                + f"{(job_result.total_bytes_processed)/(1024*1024*1024):.2f} GB of data!"
            )

        job_config.dry_run = False
        execution_start = time.time()
        job_result = self.query(query_string, job_config=job_config, **kwargs)
        query_result = job_result.result()
        execution_duration = time.time() - execution_start
        print(Fore.YELLOW + f"Query executed in {execution_duration:.2f} seconds !")
        print(
            Fore.YELLOW
            + "Query processed "
            + f"{(job_result.total_bytes_processed)/(1024*1024):.2f} MB !"
        )

        if return_type == "dataframe":
            return query_result.to_dataframe(progress_bar_type="tqdm")
        elif return_type is None:
            return None

        # return self.query(query_string)

    def create_new_dataset(self, dataset_name):
        """This function is to create dataset."""
        _ = self.create_dataset(dataset_name)

    def delete_existing_dataset(self, dataset_name):
        """This function is to delete dataset.
        Note: This function will not delete the dataset if there are tables in it."""
        self.delete_dataset(dataset_name)

    def delete_existing_table(self, dataset, table):
        """This function is to delete table."""
        self.delete_table(f"{self.project}.{dataset}.{table}")

    def create_new_table(self, dataset, table_name, schema, **kwargs):
        """This function is to create table."""
        provided_schema = [
            bigquery.SchemaField(
                field["field_name"], field["field_type"], field["field_mode"]
            )
            for field in schema
        ]

        table_reference = bigquery.Table(
            f"{self.project}.{dataset}.{table_name}", schema=provided_schema
        )
        self.create_table(table_reference, provided_schema, **kwargs)

    def load_data_to_table(self, dataset, table_name, data_frame, **kwargs):
        """This function is to create a table and load data from dataframe into it."""
        if dataset in [dataset.dataset_id for dataset in self.list_datasets()]:
            job_config = bigquery.job.LoadJobConfig()
            if kwargs.get("overwrite"):
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
                # overwrite asıl class'ta yok o yüzden asıl class'a paslamamak için kaldırıldı.
                # sonraki sürümlerde overwrite parametreye alınınca buna gerek kalmayacak.
                kwargs.pop("overwrite")
            else:
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
                if kwargs.get("overwrite") is None:
                    warnings.showwarning(
                        message="""Overwrite is not provided. Default is False. """
                        """Please provide overwrite parameter since it will be required in future releases.""",
                        category=DeprecationWarning,
                        filename=__name__ + ".py",
                        lineno=4,
                        file=sys.stdout,
                    )
                # overwrite asıl class'ta yok o yüzden asıl class'a paslamamak için kaldırıldı.
                # sonraki sürümlerde overwrite parametreye alınınca buna gerek kalmayacak.
                else:
                    kwargs.pop("overwrite")
            job = self.load_table_from_dataframe(
                data_frame,
                f"{self.project}.{dataset}.{table_name}",
                job_config=job_config,
                **kwargs,
            )
            job.result()
        else:
            raise ValueError(Fore.RED + f"Dataset {dataset} does not exist !")

    def insert_rows_into_existing_table(self, dataset, table, data):
        """This function is to insert rows into existing table."""
        table_reference = self.get_bq_table(f"{self.project}.{dataset}.{table}")
        try:
            insert_result = self.insert_rows_from_dataframe(table_reference, data)
        except NotFound:
            insert_result = self.insert_rows_from_dataframe(table_reference, data)
        if len(insert_result[0]) > 0:
            print(Fore.RED + f"Insertion failed for {insert_result[0]} !")

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


def execute_from_bq_file(bq_client, bq_file_path, **kwargs):
    """This function is to execute bq file in designated environment."""
    bq_commands = bq_command_parser(bq_file_path)
    transformed_bq_commands = []

    for bq_command in bq_commands:
        if kwargs.get("config") is not None:
            environ = kwargs.get("config")["env_identifier"]
            target_db_prefix = kwargs.get("config")["db_prefix"]
            if environ == "qa":
                source_db_prefix = target_db_prefix.replace("qa", "dev")
                bq_command = bq_command.replace(source_db_prefix, target_db_prefix)
            elif environ == "prod":
                source_db_prefix = target_db_prefix.replace("prod", "dev")
                bq_command = bq_command.replace(source_db_prefix, target_db_prefix)
        else:
            print(Fore.YELLOW + "Default Env is DEV")

        if kwargs.get("verbose"):
            print(Fore.GREEN + f"Executing: {bq_command}")
        if not kwargs.get("dependent_queries"):
            bq_client.execute_query(bq_command, return_type=None)
        else:
            transformed_bq_commands.append(bq_command)
    if kwargs.get("dependent_queries"):
        multi_query = ";".join(transformed_bq_commands)
        bq_client.execute_query(multi_query, return_type=None)
