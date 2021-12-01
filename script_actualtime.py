from tools.reportbuilder import ActualtimeReportBuilder

df = ActualtimeReportBuilder('2021-11-01', '2021-11-30')
df.gerar_relatorio()
df.exportar_dataframe('actualtime')