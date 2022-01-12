from tools.reportbuilder import TicketReportBuilder

df1 = TicketReportBuilder('2021-12-26', '2022-01-02')

df1.gerar_notas_periodo(relatorio_limpo=False,gerar_resumo=True,solucao=1, excluir_pedro=False)
df1.exportar_dataframe('base_powerbi')