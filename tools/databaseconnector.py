from pymysql import connect
from sshtunnel import SSHTunnelForwarder
import configparser as cp

parser = cp.ConfigParser()
parser.read('setup/config.ini')

# CRIE UM ARQUIVO CONFIG.INI PARA DEFINIR OS PARÂMETROS
ssh_host = str(parser['CONNECTION PARAMETERS']['ssh_host'])
ssh_username = str(parser['CONNECTION PARAMETERS']['ssh_username'])
ssh_password = str(parser['CONNECTION PARAMETERS']['ssh_password'])
database_username = str(parser['CONNECTION PARAMETERS']['database_username'])
database_password = str(parser['CONNECTION PARAMETERS']['database_password'])
database_name = str(parser['CONNECTION PARAMETERS']['database_name'])
localhost = str(parser['CONNECTION PARAMETERS']['localhost'])

class DataBaseConnector:
    """Classe para conexão remota ao banco de dados

    Contém métodos para serem utilizados na conexão remota em um banco dados desejado. Os métodos envolvem
    estabelecimento da conexão, criação de um cursor e desconexão quando concluídos os serviços.
    """
    def __init__(self):
        pass

    def set_ssh_tunnel(self):
        """Conecta via SSH ao servidor remoto de destivno
        """
        self.tunnel = SSHTunnelForwarder(
            (ssh_host, 22),
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=('127.0.0.1', 3306)
        )
        self.tunnel.start()
    
    def close_ssh_tunnel(self):
        """Fecha a conexão SSH após utiizaçção"""
        self.tunnel.close()

    def set_database_connection(self):
        """Conecta ao banco de dados contido no servidor acessado remotamente"""
        self.connection = connect(
            host='127.0.0.1',
            user=database_username,
            passwd=database_password,
            db=database_name,
            port=self.tunnel.local_bind_port,
        )

    def get_database_connection(self):
        """Retorna o objeto connection par auso em outros aplicativos"""
        return self.connection

    def close_database_connection(self):
        """Fecha a conexão do banco de dados"""
        self.connection.close()

    def set_cursor(self):
        """Abre um cursor para execturar queries através da conexão """
        self.db_cursor = self.connection.cursor()

    def close_cursor(self):
        """Fecha o cursor"""
        self.db_cursor.close()
