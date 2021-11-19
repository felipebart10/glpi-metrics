from pymysql import connect
from sshtunnel import SSHTunnelForwarder
import configparser as cp

parser = cp.ConfigParser()
parser.read('config.ini')

ssh_host = str(parser['CONNECTION PARAMETERS']['ssh_host'])
ssh_username = str(parser['CONNECTION PARAMETERS']['ssh_username'])
ssh_password = str(parser['CONNECTION PARAMETERS']['ssh_password'])
database_username = str(parser['CONNECTION PARAMETERS']['database_username'])
database_password = str(parser['CONNECTION PARAMETERS']['database_password'])
database_name = str(parser['CONNECTION PARAMETERS']['database_name'])
localhost = str(parser['CONNECTION PARAMETERS']['localhost'])

class DataBaseConnector:
    def __init__(self):
        pass

    def set_ssh_tunnel(self):
        self.tunnel = SSHTunnelForwarder(
            (ssh_host, 22),
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=('127.0.0.1', 3306)
        )
        self.tunnel.start()
    
    def close_ssh_tunnel(self):
        self.tunnel.close()

    def set_database_connection(self):
        self.connection = connect(
            host='127.0.0.1',
            user=database_username,
            passwd=database_password,
            db=database_name,
            port=self.tunnel.local_bind_port,
        )

    def get_database_connection(self):
        return self.connection

    def close_database_connection(self):
        self.connection.close()

    def set_cursor(self):
        self.db_cursor = self.connection.cursor()

    def close_cursor(self):
        self.db_cursor.close()
