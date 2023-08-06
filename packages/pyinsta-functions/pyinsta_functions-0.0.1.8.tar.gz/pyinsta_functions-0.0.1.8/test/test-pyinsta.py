import pytest
import os
from pytest import mark
from os.path import dirname, join
import sys
pyinsta_dir = dirname(dirname(__file__))  # This is your Project Root
root_dir = os.path.realpath(os.path.join(dirname(dirname(__file__)), '..'))
sys.path.append(pyinsta_dir+'/src/pyinsta/')
# sys.path.append('./pyinsta/src/pyinsta/')

import connectors as con
import functions as func

credentials_file = root_dir+'/functions/producer/facebook/credentials/data-science-279809-3a77dceb5e8e.json'


@pytest.mark.bq_connection
def bigquery_connections():
    bigquery_client = con.google_connection(credentials_file).bq_connection()
    assert bigquery_client is not None

@pytest.mark.bq_data
def bigquery_data():
    bigquery_client = con.google_connection(credentials_file).bq_connection()
    query = 'SELECT * FROM `data-science-279809.tables_fields.experience` LIMIT 1'
    data = func.google_data(bigquery_client).get_data(query)
    assert data is not None

