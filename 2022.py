from tools.reportbuilder import TicketReportBuilder
import pandas as pd

df1 = TicketReportBuilder('2021-10-01', '2021-10-31')

df1.gerar_notas_periodo(gerar_resumo=True,solucao=1)
df1.exportar_dataframe('dia 09')