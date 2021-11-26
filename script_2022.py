from tools.reportbuilder import TicketReportBuilder

df1 = TicketReportBuilder('2021-11-01', '2021-11-26', relatorio_limpo=False)
df1.relatorio_tickets()
df1.media_notas_tempo(solucao=1, fechamento=0)
df1.calcular_bonus_quantidade()
df1.exportar_dataframe('tickets')
df1.notas_finais()
df1.exportar_dataframe('resumo')