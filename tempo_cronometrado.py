from tools.reportbuilder import ActualtimeReportBuilder

df = ActualtimeReportBuilder('2021-12-13', '2021-12-13')
df.gerar_relatorio(gerar_resumo=True, excluir_discrepantes=False)
df.exportar_dataframe('actualtime1')