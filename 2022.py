from tools.reportbuilder import TicketReportBuilder

df1 = TicketReportBuilder('2021-11-01', '2021-11-30')


df1.gerar_notas_periodo(gerar_resumo=False,solucao=1, excluir_pedro=False, relatorio_limpo=False)
df1.exportar_dataframe('relatorio', iniciar_arquivo=True)

df1.gerar_notas_periodo(gerar_resumo=True,solucao=1, excluir_pedro=False, relatorio_limpo=False)
df1.exportar_dataframe('relatorio2', iniciar_arquivo=True)
