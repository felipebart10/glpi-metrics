from tools.reportbuilder import ActualtimeReportBuilder

df = ActualtimeReportBuilder('2021-10-01', '2021-10-31')
df.gerar_relatorio(excluir_discrepantes=False)
df.exportar_dataframe('actualtime')