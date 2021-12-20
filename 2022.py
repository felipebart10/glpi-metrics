from tools.reportbuilder import TicketReportBuilder

df1 = TicketReportBuilder('2021-01-01', '2021-12-31')

df1.gerar_notas_periodo(gerar_resumo=False,solucao=1, excluir_pedro=False, relatorio_limpo=False)
df1.exportar_dataframe('base_powerbi', iniciar_arquivo=False)
