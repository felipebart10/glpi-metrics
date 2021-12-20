from tools.reportbuilder import ActualtimeReportBuilder

df = ActualtimeReportBuilder('2021-01-01', '2021-12-31')
df.gerar_relatorio(gerar_resumo=False, excluir_discrepantes=True, excluir_pedro=False)
df.exportar_dataframe('actualtime', iniciar_arquivo=False)

