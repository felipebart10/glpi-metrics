from tools.reportbuilder import ActualtimeReportBuilder

df = ActualtimeReportBuilder('2021-12-09', '2021-12-09')
df.gerar_relatorio(excluir_discrepantes=False)
df.exportar_dataframe('actualtime2')