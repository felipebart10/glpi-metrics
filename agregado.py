from tools.reportbuilder import TicketReportBuilder
from tools.reportbuilder import ActualtimeReportBuilder

df1 = TicketReportBuilder('2021-10-01', '2021-10-31')
df1.gerar_notas_periodo(solucao=1)
df_tickets = df1.get_dataframe()

df2 = ActualtimeReportBuilder('2021-10-01', '2021-10-31')
df2.gerar_relatorio(excluir_discrepantes=False)
df_actualtime = df2.get_dataframe()
df3 = df_tickets.merge(df_actualtime[['id', 'tecnico_das_tarefas', 'tempo_eleito']], on='id', how='right')

df3.to_excel(excel_writer="09-12.xlsx", sheet_name="agregado", header=True, index=False)