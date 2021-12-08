from tools.reportbuilder import ActualtimeReportBuilder

df = ActualtimeReportBuilder('2021-01-01', '2021-11-30')
df.gerar_relatorio(excluir_discrepantes=False)
df.exportar_dataframe('actualtime')