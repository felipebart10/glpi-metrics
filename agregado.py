from tools.reportbuilder import TicketReportBuilder
from tools.reportbuilder import ActualtimeReportBuilder
import pandas as pd

df1 = TicketReportBuilder('2021-11-01', '2021-11-30')
df1.__calcular_relatorio()
df1.__media_notas_tempo(menor_nota=3, maior_nota= 8.5, solucao=1, fechamento=0)
df1.__calcular_bonus(0.15)
df_tickets = df1.get_dataframe()

df2 = ActualtimeReportBuilder('2021-11-01', '2021-11-30')
df2.gerar_relatorio(excluir_discrepantes=False)
df_actualtime = df2.get_dataframe()
df3 = df_tickets.merge(df_actualtime[['id', 'tecnico_das_tarefas', 'tempo_eleito']], on='id', how='outer')

df3.to_excel(excel_writer="agregado.xlsx", sheet_name="agregado", header=True, index=False)