from tools.databaseconnector import DataBaseConnector
from tools.reportbuilder import ReportBuilder

con = DataBaseConnector()
con.set_ssh_tunnel()
con.set_database_connection()
connection = con.get_database_connection()

#df1 = ReportBuilder(connection, '2021-10-01', '2021-10-31')
#df1.quick_report()

#df2 = ReportBuilder(connection, '2021-10-01', '2021-10-31')
#df2.quick_summary()

df3 = ReportBuilder(connection, '2021-10-01', '2021-10-31')
df3.tickets_report_actualtime()
df3.export_excel('actualtime')
