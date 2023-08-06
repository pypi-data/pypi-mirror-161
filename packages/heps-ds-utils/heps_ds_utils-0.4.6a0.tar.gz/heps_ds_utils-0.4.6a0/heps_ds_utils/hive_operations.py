""" This Module is created to enable Hepsiburada Data Science to communicate with Hive """

import os
import time
from random import randint

from colorama import Fore, init ##Style
from pyhive import hive
import pandas as pd
import numpy as np
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

init(autoreset=True)

class HiveOperations:
    """ This class is created to enable Hepsiburada Data Science to communicate with Hive """
    _implemented_returns = ['dataframe', 'numpy', 'list', 'dict']

    def __init__(self, **kwargs):
        """ Initialize the class
        :param HIVE_HOST: Hive Server 2 host
        :param HIVE_PORT: Hive Server 2 port
        :param APP_USER_USERNAME: Hive Server 2 username
        :param APP_USER_PASS: Hive Server 2 password
        """
        self.hive_host = kwargs.get("HIVE_HOST")
        self.hive_port = kwargs.get("HIVE_PORT")
        self.hive_username = kwargs.get("HIVE_USER")
        self.hive_password = kwargs.get("HIVE_PASS")
        self.hadoop_edge_host = kwargs.get("HADOOP_EDGE_HOST")
        self.hive_connection = None

    def __repr__(self):
        return f'HiveOperations(HIVE_HOST={self.hive_host}, HIVE_PORT={self.hive_port}, ' \
               f'HIVE_USER={self.hive_username}, HIVE_PASS="XXXXXXXX")'

    def connect_to_hive(self):
        """
        This function is used to connect to Hive Server 2 and return the connection object.
        :return: Hive Server 2 connection object
        """
        try:
            self.hive_connection = hive.connect(
                                    host=self.hive_host,
                                    port=self.hive_port,
                                    username=self.hive_username,
                                    password=self.hive_password,
                                    auth='LDAP')
        except TypeError:
            raise TypeError(Fore.RED + "Failed to connect to Hive Server 2: "
                            "VPN is possibly not connected") from None

        except ValueError:
            raise ValueError(Fore.RED + "Failed to connect to Hive Server 2: "
                            "Credentials are incorrect or missing ") from None
        print(Fore.GREEN + "Connection Succeded !!")

    def disconnect_from_hive(self):
        """
        This function is used to disconnect from Hive Server 2.
        :param hive_connection: Hive Server 2 connection object
        :return: None
        """
        self.hive_connection.close()
        print(Fore.GREEN + "Connection Closed! ")

    def execute_query(self, query, return_type='dataframe', **kwargs):
        """
        This function is used to execute the query and return data in different types.
        :param hive_connection: Hive Server 2 connection object
        :param query: Hive query
        :param return_type: Type of return data
        :param kwargs return_colums: Return Columns for numpy array and list types.
        :return: Data frame
        """
        if return_type not in HiveOperations._implemented_returns:
            raise NotImplementedError(Fore.RED + f'Return type {return_type} not implemented !!')

        cursor = self.hive_connection.cursor()
        execution_start = time.time()
        cursor.execute(query)
        execution_duration = time.time() - execution_start
        print(Fore.YELLOW + f'Query executed in {execution_duration:.2f} seconds !')
        columns = HiveOperations._rename_columns(cursor)

        if return_type == 'dataframe':
            data = pd.DataFrame(cursor.fetchall(), columns=columns)
        elif return_type == 'numpy':
            data = np.array(cursor.fetchall())
        elif return_type == 'list':
            data = cursor.fetchall()
        elif return_type == 'dict':
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        if kwargs.get('return_columns'):
            return data, columns
        return data, None

    def create_insert_table(self, query) -> None:
        """
        This function is used to create the table and insert data into the table.
        :param query: Hive query
        :param hive_connection: Hive Server 2 connection object
        :return: None
        """
        cursor = self.hive_connection.cursor()
        cursor.execute(query)
        cursor.close()

    def send_files_to_hive(self, target_table, source_data, columns=None):
        """
        This function is used to send files to Hive Server 2.
        :param target_table: Target Hive table
        :param source_data: Source data
        :param columns: Columns of the source data
        :return: None
        """
        unique_filename = str(randint(0, 100000))
        transfer_start = time.time()
        ssh_client = self._set_ssh_client()

        csv_created= False
        edge_node_path = f"/home/{self.hive_username}/Python_CSV"
        hdfs_path = f"/user/{self.hive_username}/projects/Python_CSV"

        # Check if Edge Node & HDFS Path exist
        edge_node_dir_check_cmd = f"ls -d {edge_node_path}"
        hdfs_dir_check_cmd = f"hdfs dfs -test -d {hdfs_path}"

        _, stdout, _ = ssh_client.exec_command(edge_node_dir_check_cmd)
        if stdout.channel.recv_exit_status() != 0:
            print(Fore.RED + f"Edge Node Path {edge_node_path} does not exist")
            print(Fore.YELLOW + f"Creating Edge Node Path {edge_node_path}")
            ssh_client.exec_command(f"mkdir {edge_node_path}")

        _, stdout, _ = ssh_client.exec_command(hdfs_dir_check_cmd)
        if stdout.channel.recv_exit_status() != 0:
            print(Fore.RED + f"HDFS Path {hdfs_path} does not exist")
            print(Fore.YELLOW + f"Creating HDFS Path {hdfs_path}")
            ssh_client.exec_command(f"hdfs dfs -mkdir {hdfs_path}")

        try:
            # Creating a csv file
            if str(type(source_data)) ==  "<class 'numpy.ndarray'>":
                np.savetxt(unique_filename + ".csv", source_data,
                                    delimiter="\t",header='\t'.join(columns),comments='')
                source_data = unique_filename + ".csv"
                csv_created = True
                # print("Temporary csv file '" + unique_filename +".csv' created.")

            elif str(type(source_data)) ==  "<class 'pandas.core.frame.DataFrame'>":
                source_data.to_csv(unique_filename + ".csv",index=False,sep="\t")
                source_data = unique_filename + ".csv"
                csv_created = True
                # print("Temporary csv file '" + unique_filename +".csv' created.")


            _, stdout, _ = ssh_client.exec_command(f"mkdir {edge_node_path}/{unique_filename};")
            if stdout.channel.recv_exit_status() != 0:
                raise RuntimeError(Fore.RED + "Failed to create directory on edge node")

            with SCPClient(ssh_client.get_transport()) as scp:
                # uploads target CSV to edgenode
                scp.put(source_data, recursive=True, remote_path=f"{edge_node_path}/{unique_filename}/")
            print(Fore.GREEN + "Files sent to EdgeNode succesfully!")

            edge_node_to_hdfs_command_list = [
                f"hadoop fs -rm -r {hdfs_path}/{unique_filename};",
                f"hadoop fs -mkdir {hdfs_path}/{unique_filename}/;",
                f"hadoop fs -put {edge_node_path}/{unique_filename}/*.csv {hdfs_path}/{unique_filename};",
                f"rm -r {edge_node_path}/{unique_filename};"
                ]

            for command in edge_node_to_hdfs_command_list:
                _, stdout, _ = ssh_client.exec_command(command)
                if stdout.channel.recv_exit_status() == 0:
                    print(Fore.GREEN + f"Command executed: {command}")
                else:
                    print(Fore.RED + f"Command failed: {command}")

            print(Fore.GREEN + "EdgeNode - HDFS transfer completed! \nEdgeNode is clean again!")

            # reading csv file's column types and make column types suitable for hql
            dataframe = pd.read_csv(source_data, sep='\t')
            column_name = dataframe.columns
            dtype_dict = {
                "object": "STRING",
                "int64": "INT",
                "float64": "FLOAT",
                "bool": "BOOLEAN"
                }
            column_type = [dtype_dict[str(item)] for item in dataframe.dtypes]
            columns = []

            for item in zip(column_name, column_type):
                columns.append(" ".join(item))
            column_details = ",".join(columns)

            # numpy,pandas csvleri siliniyor
            if csv_created:
                os.remove(source_data)
                csv_created = False

            # creating external table
            print(Fore.GREEN + "Creating external table...")
            self.create_insert_table(f"DROP TABLE IF EXISTS {target_table}_ext")
            self.create_insert_table(f"CREATE EXTERNAL TABLE {target_table}_ext"
                                    f"({column_details}) "
                                    f'ROW FORMAT DELIMITED FIELDS TERMINATED BY "\t" '
                                    f'LOCATION "{hdfs_path}/{unique_filename}/" '
                                    f'TBLPROPERTIES("skip.header.line.count"="1")')

            self.create_insert_table(f"DROP TABLE IF EXISTS {target_table}")
            self.create_insert_table("SET hive.auto.convert.join=false")
            self.create_insert_table("SET hive.tez.container.size=16384")
            self.create_insert_table("SET hive.tez.java.opts=-Xmx13108m")
            self.create_insert_table(f"CREATE TABLE {target_table} AS "
                                    f"SELECT * FROM {target_table}_ext")
            self.create_insert_table(f"DROP TABLE IF EXISTS {target_table}_ext")

            print(Fore.GREEN + "Table creation Success!")
            transfer_end = time.time()
            print(Fore.YELLOW +
                    f"Table Creation took: {transfer_end - transfer_start:.2f} seconds!")

            ssh_client.exec_command(f"hadoop fs -rm -r {hdfs_path}/{unique_filename};")
            print(Fore.GREEN + "HDFS is clean again!")

        except Exception as exc:
            ssh_client.exec_command(f"hadoop fs -rm -r {hdfs_path}/{unique_filename};")
            print(Fore.GREEN + "HDFS is clean!")
            ssh_client.exec_command(f"rm -r {edge_node_path}/{unique_filename};")
            print(Fore.GREEN + "EdgeNode is clean!")
            raise exc

    def _set_ssh_client(self):
        ssh_client = SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=self.hadoop_edge_host,
                            username=self.hive_username,
                            password=self.hive_password, look_for_keys=False)
        return ssh_client

    @staticmethod
    def _rename_columns(cursor) -> list:
        """
        This function takes cursor description and rename the columns of the data frame.
        :param column_names: Column names
        :return: List of column names
        """
        columns = [column[0].split('.')[-1] for column in cursor.description]
        return columns

    @staticmethod
    def _parse_sql_query(query):
        """
        This function is used to parse the sql query and return the query with the table name.
        :param query: Hive query
        :return: Hive query with table name
        """

        ## TO BE WRITTEN !!

        query_list = query.split(' ')
        table_name = query_list[2]
        return table_name

    @staticmethod
    def _execute_sql_from_file(query_file, hive_connection):
        """
        This function is used to execute the sql query from file and return the data frame.
        :param query_file: Hive query file
        :param hive_connection: Hive Server 2 connection object
        :return: Data frame
        """

        ## TO BE WRITTEN !!

        with open(query_file, 'r', encoding='utf-8') as hiveql_file:
            query = hiveql_file.read()
        return HiveOperations.execute_query(hive_connection, query)

    @property
    def hive_host(self):
        """Hive Server 2 host"""
        return self._hive_host

    @hive_host.setter
    def hive_host(self, provided_hive_host):
        """Hive Server 2 host setter"""
        if provided_hive_host is not None:
            self._hive_host = str(provided_hive_host)
        elif os.environ.get("HIVE_HOST"):
            self._hive_host = os.environ.get("HIVE_HOST")
        else:
            self._hive_host = None
            print(Fore.RED + "Warning!! Hive host is not specified")

    @property
    def hive_port(self):
        """Hive Server 2 port"""
        return self._hive_port

    @hive_port.setter
    def hive_port(self, provided_hive_port):
        """Hive Server 2 port setter"""
        if provided_hive_port is not None:
            self._hive_port = str(provided_hive_port)
        elif os.environ.get("HIVE_PORT"):
            self._hive_port = os.environ.get("HIVE_PORT")
        else:
            self._hive_port = None
            print(Fore.RED + "Warning!! Hive port is not specified")

    @property
    def hive_username(self):
        """Hive Server 2 username"""
        return self._hive_username

    @hive_username.setter
    def hive_username(self, provided_hive_username):
        """Hive Server 2 username setter"""
        if provided_hive_username is not None:
            self._hive_username = str(provided_hive_username)
        elif os.environ.get("HIVE_USERNAME"):
            self._hive_username = os.environ.get("HIVE_USERNAME")
        else:
            self._hive_username = None
            print(Fore.RED + "Warning!! Hive username is not specified")

    @property
    def hive_password(self):
        """Hive Server 2 password"""
        return self._hive_password

    @hive_password.setter
    def hive_password(self, provided_hive_password):
        """Hive Server 2 password setter"""
        if provided_hive_password is not None:
            self._hive_password = str(provided_hive_password)
        elif os.environ.get("HIVE_PASSWORD"):
            self._hive_password = os.environ.get("HIVE_PASSWORD")
        else:
            self._hive_password = None
            print(Fore.RED + "Warning!! Hive password is not specified")

    @property
    def hadoop_edge_host(self):
        """Hadoop Edge host"""
        return self._hadoop_edge_host

    @hadoop_edge_host.setter
    def hadoop_edge_host(self, provided_hadoop_edge_host):
        """Hadoop Edge host setter"""
        if provided_hadoop_edge_host is not None:
            self._hadoop_edge_host = str(provided_hadoop_edge_host)
        elif os.environ.get("HADOOP_EDGE_HOST"):
            self._hadoop_edge_host = os.environ.get("HADOOP_EDGE_HOST")
        else:
            self._hadoop_edge_host = None
            print(Fore.RED + "Warning!! Hadoop Edge Host is not specified")
