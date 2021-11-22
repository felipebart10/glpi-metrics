from tools.databaseconnector import DataBaseConnector
from tools.reportbuilder import ReportBuilder

con = DataBaseConnector()
con.set_ssh_tunnel()
con.set_database_connection()
connection = con.get_database_connection()

df1 = ReportBuilder(connection, '2021-10-01', '2021-10-31', 'actualtime')

df1.tickets_report()
df1.grade_calculator()
df1.compute_time_grades('fechamento')
df1.compute_time_grades('solucao')
df1.average_grade()
df1.get_monthly_quantity_bonus()
df1.export_excel()

con.close_database_connection()
con.close_ssh_tunnel()
