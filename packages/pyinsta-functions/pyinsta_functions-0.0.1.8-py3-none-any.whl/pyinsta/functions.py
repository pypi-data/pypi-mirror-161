from datetime import datetime
import os
import sys
import pandas as pd
import numpy as np
import requests
import json
import pytz
from google.cloud import bigquery, storage
from google.oauth2 import service_account
from google.api_core.exceptions import AlreadyExists, NotFound, BadRequest
from google.cloud import error_reporting
from google.cloud import secretmanager
import hashlib

class google_data():

    def __init__(self, bigquery_client):
        self.bigquery_client = bigquery_client

    def get_data(self, query: str):
        """
            Função para a captura de dados do Google Cloud

            Args:
            query: query a ser executada

            Returns:
            data: dados capturados
            """
        try:
            data = self.bigquery_client.query(query).to_dataframe()
        except:
            return "Erro em capturar os dados da BigQuery"
        return data



    def load_into_bigquery(self, input, table, bigquery_client):


        """
        Função para subir arquivos na BigQuery
        """

        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = True
        # job_config.schema = schema
        job_config.ignore_unknown_values = True
        job_config.schema_update_options = 'ALLOW_FIELD_RELAXATION'
        job_config.max_bad_records = 10
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
        job = bigquery_client.load_table_from_dataframe(input,
                                                        table,
                                                        job_config=job_config)

        print("Starting job {}".format(job.job_id))

        # Waits for table load to complete.
        try:
            job.result()
        except BadRequest as e:
            for e in job.errors:
                print('ERROR: {}'.format(e['message']))
        assert job.job_type == 'load'
        assert job.state == 'DONE'

        destination_table = bigquery_client.get_table(table)
        print("Loaded {} rows.".format(destination_table.num_rows))


    def load_into_bigquery_stream(self, input, table):

        # Make an API request.
        errors = bigquery_client.insert_rows_json(table, input)

        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))


def clean_columns(input):

    #### rename para tirar caracteres especiais####

    input.columns = input.columns.str.replace('ç', 'c', regex=True)
    input.columns = input.columns.str.replace('ã|â|á', 'a', regex=True)
    input.columns = input.columns.str.replace('í', 'i', regex=True)
    input.columns = input.columns.str.replace('õ|ó', 'o', regex=True)
    input.columns = input.columns.str.replace('é', 'e', regex=True)
    input.columns = input.columns.str.replace('-', '_', regex=True)
    input.columns = input.columns.str.replace(' ', '_', regex=True)
    input.columns = input.columns.str.replace('.', '_', regex=True)
    input.columns = input.columns.str.replace('&', '', regex=True)
    input.columns = input.columns.str.replace(r'[/]', '_', regex=True)

    ## drop columns que com ( no DDD e não fazem sentido para o modelo
    input = input.loc[:, ~input.columns.str.contains("\(|\+")]

    return input


def check_columns(dataframe, list_columns):

    dataframe_columns = list(dataframe.columns)
    list_results = list(set(list_columns) & set(dataframe_columns))

    return list_results


def astype_columns(input):

    if input == 'FLOAT':
        return "float64"
    elif input == 'INTEGER':
        return "int64"
    elif input == 'STRING':
        return "str"
    elif input == 'BOOLEAN':
        return "bool"


def bq_schema(input, schema):

    schema_df = pd.DataFrame(schema)
    del schema_df['mode']

    schema_df['astype'] = schema_df.apply(
        lambda row: astype_columns(str(row['type'])), axis=1)
    columns = check_columns(input, list(schema_df.name.unique()))
    input = input[columns].fillna(method='ffill')

    for col in input.columns:
        astype_value = schema_df['astype'][schema_df['name'] == str(
            col)].iloc[0]
        type = schema_df['type'][schema_df['name'] == str(col)].iloc[0]

        if type == 'TIMESTAMP':
            try:
                input[col] = pd.to_datetime(
                    input[col].replace(np.nan, "2022-01-31"), utc=True)
            except:
                None
        elif type == 'DATE':
            input[col] = pd.to_datetime(input[col], utc=True)
        elif type == 'FLOAT':
            input[col] = input[col].fillna(0).astype('float64')
        elif type == 'INTEGER':
            input[col] = input[col].fillna(0).astype('int64')
        elif type == 'STRING':
            input[col] = input[col].fillna("None").astype('str')
        elif type == 'BOOLEAN':
            input[col] = input[col].fillna("true").astype('bool')
        else:
            input[col] = input[col].fillna("None").astype(
                str(astype_value), errors='ignore')

    return input

##function to upload the results in the google storage (data lake)##


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(
            source_file_name, content_type='application/json')

    except Exception as e:
        print(e)
    return("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def access_secret(project_id,secret_id, version_id="latest"):
    """
    Accesses the secret version identified by secret_id and version_id.
    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response


def secret_hash(secret_value):
  """
  return the sha224 hash of the secret value
  """
  return hashlib.sha224(bytes(secret_value, "utf-8")).hexdigest()
