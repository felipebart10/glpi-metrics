from tools.databaseconnector import DataBaseConnector
from tools.dataframebuilder import DataFrameBuilder

con = DataBaseConnector()
con.set_ssh_tunnel()
con.set_database_connection()
connection = con.get_database_connection()

dfb = DataFrameBuilder(connection, '2021-10-01', '2021-10-31', 'outubro')

dfb.tickets_report()
dfb.grade_calculator()
dfb.export_excel()


con.close_database_connection()
con.close_ssh_tunnel()