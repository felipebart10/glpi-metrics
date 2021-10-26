import pymysql
import logging
from pymysql.constants import CLIENT
import sshtunnel
from sshtunnel import SSHTunnelForwarder
import pandas as pd
import configparser as cp

parser = cp.ConfigParser()
parser.read('config.ini')

### PARÂMETROS ###

ssh_host = str(parser['CONNECTION PARAMETERS']['ssh_host'])
ssh_username = str(parser['CONNECTION PARAMETERS']['ssh_username'])
ssh_password = str(parser['CONNECTION PARAMETERS']['ssh_password'])
database_username = str(parser['CONNECTION PARAMETERS']['database_username'])
database_password = str(parser['CONNECTION PARAMETERS']['database_password'])
database_name = str(parser['CONNECTION PARAMETERS']['database_name'])
localhost = str(parser['CONNECTION PARAMETERS']['localhost'])

def open_ssh_tunnel(verbose=False):
    """Open an SSH tunnel and connect using a username and password.
    
    :param verbose: Set to True to show logging
    :return tunnel: Global SSH tunnel connection
    """
    
    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG
    
    global tunnel
    tunnel = SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username = ssh_username,
        ssh_password = ssh_password,
        remote_bind_address = ('127.0.0.1', 3306)
    )
    
    tunnel.start()

def mysql_connect():
    """Connect to a MySQL server using the SSH tunnel connection
    
    :return connection: Global MySQL database connection
    """
    
    global connection
    
    connection = pymysql.connect(
        host='127.0.0.1',
        user=database_username,
        passwd=database_password,
        db=database_name,
        port=tunnel.local_bind_port,
        client_flag=CLIENT.MULTI_STATEMENTS
    )
    print("Conectado ao banco com sucesso!")
    return connection

def run_select_query(sql):

    """Runs a given SQL query via the global database connection.
    
    :param sql: MySQL query
    :return: Pandas dataframe containing results
    """
    
    return pd.read_sql(sql, connection)

def run_query(sql):
    cur = connection.cursor()
    cur.execute(sql)
    print(f'Linhas a serem modificadas: {cur.rowcount}')
    opcao = input("Prosseguir? (Y/n): ")
    if opcao == 'Y':
        connection.commit()
        print("Query concluída")
    else:
        print("Operação cancelada")
    cur.close()

def close_connection():
    connection.close()
    