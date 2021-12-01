from tools.reportbuilder import TicketReportBuilder

df1 = TicketReportBuilder('2021-11-01', '2021-11-30')
df1.gerar_relatorio()
df1.media_notas_tempo(menor_nota=3, maior_nota= 8.5, solucao=1, fechamento=0)
df1.calcular_bonus_quantidade(0.15)
#df1.exportar_dataframe('tickets_anual')
df1.notas_finais()
df1.exportar_dataframe('resumo')