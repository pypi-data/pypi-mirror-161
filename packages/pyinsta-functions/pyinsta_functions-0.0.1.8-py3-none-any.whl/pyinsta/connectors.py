import os
import json
from mysql.connector import errorcode
import mysql.connector
import psycopg2
from sqlalchemy import create_engine
import copy
from psycopg2 import Error
from google.cloud import bigquery
from google.api_core.exceptions import AlreadyExists, NotFound,BadRequest


class google_connection():
    """
    Função para a conexão com o Google Cloud
    
    Args:
    
    Returns:
    
    bigquery_client: objeto do tipo bigquery
    storage_client: objeto do tipo storage

    """

    def __init__(self, credentials_file:json):
        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
            ##create connection##
            self.bigquery_client = bigquery.Client()
        except:
            raise ValueError("Erro em capturar os dados da BigQuery")


    def bq_connection(self) -> bigquery.Client:
        """
        Função para a conexão com a BigQuery
        
        Args:
        credentials_file: arquivo de credenciais
        
        Returns:
        
        bigquery_client: objeto do tipo bigquery

        """
        try:
            ##create connection##
            bigquery_client = self.bigquery_client

        except BadRequest as e:
            for e in bigquery_client.errors:
                print('ERROR: {}'.format(e['message']))

        return bigquery_client

class postgres_connection():
    """
    Função para a conexão com o PostgreSQL
    
    Args:
    
    Returns:
    
    postgres_con: objeto do tipo postgres

    """

    def __init__(self, port:int, host:str, user:str, password:str, database:str):
        self.port = port
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        try:
            params = {
                "host": host,
                "port": port,
                "database": database,
                "user": user,
                "password": password}
            # construct an engine connection string
            engine_string = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
                user=params['user'],
                password=params['password'],
                host=params['host'],
                port=params['port'],
                database=params['database'],
            )

            # create sqlalchemy engine
            engine = create_engine(engine_string)
        except:
            print("Error")

        return engine

class mysql_connection():
    """
    Função para a conexão com o MySQL
    
    Args:
    
    Returns:
    
    mysql_con: objeto do tipo mysql

    """

    def __init__(self, port: int, host: str, user: str, password: str, database: str):
        self.port = port
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
        try:
            params = {
                "host": host,
                "port": port,
                "database": database,
                "user": user,
                "password": password}
            # construct an engine connection string
            engine_string = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(
                user=params['user'],
                password=params['password'],
                host=params['host'],
                port=params['port'],
                database=params['database'],
            )

            # create sqlalchemy engine
            engine = create_engine(engine_string)
        except:
            print("Error")

        return engine

    def get_rds_data(self, query: str) -> DataFrame:

        config = {
            'user': self.user,
            'password': self.password,
            'host': self.host,  # replica
            'database': self.database,
            'raise_on_warnings': False,
        }
        try:
            mysql_con = mysql.connector.connect(**config)
        except:
            return "Erro ao conectar no banco de dados"

        try:

            results_mysql = pd.read_sql(query, mysql_con)

        except:
            return "Não existe leads para classificar"

        mysql_con.close()

        return results_mysql
