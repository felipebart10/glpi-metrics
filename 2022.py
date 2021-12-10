from tools.reportbuilder import TicketReportBuilder
import pandas as pd

df1 = TicketReportBuilder('2021-01-01', '2021-12-31', relatorio_limpo=False)

df1.gerar_notas_periodo()

df1.exportar_dataframe('relatório anual')