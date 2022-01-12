from tools.reportbuilder import ActualtimeReportBuilder, TicketReportBuilder

df1 = TicketReportBuilder('2021-12-01', '2021-12-31')

df1.gerar_notas_periodo(gerar_resumo=True,solucao=1, excluir_pedro=True, relatorio_limpo=False)
df1.exportar_dataframe('relatorio2', iniciar_arquivo=True)

df2 = ActualtimeReportBuilder('2021-12-01', '2021-12-31')
df2.gerar_relatorio(gerar_resumo=True)
df2.exportar_dataframe('actualtime')