# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['heps_ds_utils']

package_data = \
{'': ['*']}

install_requires = \
['PyHive>=0.6.5,<0.7.0',
 'colorama>=0.4.4,<0.5.0',
 'google-cloud-bigquery[bqstorage,pandas]>=3.0.1,<4.0.0',
 'google-cloud-logging>=3.0.0,<4.0.0',
 'pandas>=1.4.1,<2.0.0',
 'paramiko>=2.10.3,<3.0.0',
 'protobuf==3.20.0',
 'scp>=0.14.4,<0.15.0',
 'thrift-sasl>=0.4.3,<0.5.0',
 'thrift>=0.15.0,<0.16.0',
 'tqdm>=4.64.0,<5.0.0']

extras_require = \
{':sys_platform == "linux" or sys_platform == "darwin"': ['sasl>=0.3.1,<0.4.0']}

setup_kwargs = {
    'name': 'heps-ds-utils',
    'version': '0.4.6a1',
    'description': 'A Module to enable Hepsiburada Data Science Team to utilize different tools.',
    'long_description': '# Hepsiburada Data Science Utilities\n\nThis module includes utilities for Hepsiburada Data Science Team.\n\n- Library is available via PyPi. \n- Library can be downloaded using pip as follows: `pip install heps-ds-utils`\n- Existing library can be upgraded using pip as follows: `pip install heps-ds-utils --upgrade`\n\n***\n## Available Modules\n\n1. Hive Operations\n\n```python\nfrom heps_ds_utils import HiveOperations\n\n# A connection is needed to be generated in a specific runtime.\n# There are 3 ways to set credentials for connection.\n\n# 1) Instance try to set default credentials from Environment Variables.\nhive_ds = HiveOperations()\nhive_ds.connect_to_hive()\n\n# 2) One can pass credentials to instance initiation to override default.\nhive_ds = HiveOperations(HIVE_HOST="XXX", HIVE_PORT="YYY", HIVE_USER="ZZZ", HIVE_PASS="WWW", HADOOP_EDGE_HOST="QQQ")\nhive_ds = HiveOperations(HIVE_USER="ZZZ", HIVE_PASS="WWW")\nhive_ds.connect_to_hive()\n\n# 3) One can change any of the credentials after initiation using appropriate attribute.\nhive_ds = HiveOperations()\nhive_ds.hive_username = \'XXX\'\nhive_ds.hive_password = \'YYY\'\nhive_ds.connect_to_hive()\n\n#\xa0Execute an SQL query to retrieve data.\n# Currently Implemented Types: DataFrame, Numpy Array, Dictionary, List.\nSQL_QUERY = "SELECT * FROM {db}.{table}"\ndata, columns = hive_ds.execute_query(SQL_QUERY, return_type="dataframe", return_columns=False)\n\n# Execute an SQL query to create and insert data into table.\nSQL_QUERY = "INSERT INTO .."\nhive_ds.create_insert_table(SQL_QUERY)\n\n# Send Files to Hive and Create a Table with the Data.\n# Currently DataFrame or Numpy Array can be sent to Hive.\n# While sending Numpy Array columns have to be provided.\nSQL_QUERY = "INSERT INTO .."\nhive_ds.send_files_to_hive("{db}.{table}", data, columns=None)\n\n# Close the connection at the end of the runtime.\n\nhive_ds.disconnect_from_hive()\n\n```\n\n2. BigQuery Operations\n\n```python\nfrom heps_ds_utils import BigQueryOperations, execute_from_bq_file\n\n# A connection is needed to be generated in a specific runtime.\n# There are 3 ways to set credentials for connection.\n\n# 1) Instance try to set default credentials from Environment Variables.\nbq_ds = BigQueryOperations()\n\n# 2) One can pass credentials to instance initiation to override default.\nbq_ds = BigQueryOperations(gcp_key_path="/tmp/keys/ds_qos.json")\n\n# Unlike HiveOperations, initiation creates a direct connection. Absence of\n# credentials will throw an error.\n\n#\xa0Execute an SQL query to retrieve data.\n# Currently Implemented Types: DataFrame.\nQUERY_STRING = """SELECT * FROM `[project_name].[dataset_name].[table_name]` LIMIT 20"""\ndata = bq_ds.execute_query(QUERY_STRING, return_type=\'dataframe\')\n\n#\xa0Create a Dataset in BigQuery.\nbq_ds.create_new_dataset("example_dataset")\n\n# Create a Table under a Dataset in BigQuery.\nschema = [\n    {"field_name": "id", "field_type": "INTEGER", "field_mode": "REQUIRED"},\n    {"field_name": "first_name", "field_type": "STRING", "field_mode": "REQUIRED"},\n    {"field_name": "last_name", "field_type": "STRING", "field_mode": "REQUIRED"},\n    {"field_name": "email", "field_type": "STRING", "field_mode": "REQUIRED"},\n    {"field_name": "gender", "field_type": "STRING", "field_mode": "REQUIRED"},\n    {"field_name": "ip_address", "field_type": "STRING", "field_mode": "REQUIRED"}]\n\nbq_ds.create_new_table(dataset=\'example_dataset\', table_name=\'mock_data\', schema=schema)\n\n# Insert into an existing Table from Dataframe.\n# Don\'t create and insert in the same runtime.\n# Google throws an error when creation and insertion time is close.\nbq_ds.insert_rows_into_existing_table(dataset=\'example_dataset\', table=\'mock_data\', data=df)\n\n# Delete a Table.\nbq_ds.delete_existing_table(\'example_dataset\', \'mock_data\')\n\n# Delete a Dataset.\n# Trying to delete a dataset consisting of tables will throw an error.\nbq_ds.delete_existing_dataset(\'example_dataset\')\n\n# Load Dataframe As a Table. BigQuery will infer the data types.\nbq_ds.load_data_to_table(\'example_dataset\', \'mock_data\', df, overwrite=False)\n\n# To execute BQ commands sequentially from a BigQuery Script without a return statement !\nexecute_from_bq_file(bq_client=bq_ds, bq_file_path="tests/test_data/test_case_2.bq", verbose=True)\n\n```\n\n3. Logging Operations\n\n```python\nfrom heps_ds_utils import LoggingOperations\n\n# A connection is needed to be generated in a specific runtime.\n# There are 3 ways to set credentials for connection.\n\n# 1) Instance try to set default credentials from Environment Variables.\nlogger_ds = LoggingOperations()\n\n# 2) One can pass credentials to instance initiation to override default.\nlogger_ds = LoggingOperations(gcp_key_path="/tmp/keys/ds_qos.json")\n\n# Unlike HiveOperations, initiation creates a direct connection. Absence of\n# credentials will throw an error.\n\n\n```\n\nRelease Notes:\n\n0.4.4:\n- BigQueryOperations:\n    - insert_rows_into_existing_table: insertion exception handling added.\n    - insert_rows_into_existing_table: retry added. \n        - Put time between table creation and insertion.\n    - execute_query: total_bytes_processed info added.\n    - execute_query: max allowed total_bytes_processed set to 100GB.\n    - execute_query: return_type=None for Queries w/o any return.\n    - load_data_to_table: kwargs[\'overwrite\'] is added.\n        - load_data_to_table(..., overwrite=True) to overwrite to table.\n        - load_data_to_table(..., overwrite=False) to append to table.\n        - not passing overwrite kwarg will print a DeprecationWarning.\n    - execute_from_bq_file: sequential execution of BigQuery commands from\n    a file. It has its own parser. \n        - execute_from_bq_file(..., verbose=True) to print BigQuery commands to console.\n        - execute_from_bq_file(..., verbose=False) not to print BigQuery commands to console.\n\n0.4.5:\n- LoggingOperations\n    - Bug Fix in Authentication to GCP Logging !\n- BigQueryOperations\n    - Executing BQ files for different environments !\n\n0.4.6:\n- BigQueryOperations\n    - BQ Parser bug fix !\n    - BQ File Execution dependent queries\n        - Some of the queries depends on the previous command executions. For these cases:\n        dependent_queries is needed to be set to True !\n        execute_from_bq_file(\n            bq_ds,\n            "tests/test_data/test_case_4.bq",\n            verbose=True,\n            config=configs,\n            dependent_queries=True)',
    'author': 'FarukBuldur',
    'author_email': 'faruk.buldur@hepsiburada.com',
    'maintainer': 'FıratÖncü',
    'maintainer_email': 'firat.oncu@hepsiburada.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
