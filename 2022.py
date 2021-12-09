from tools.reportbuilder import TicketReportBuilder
import pandas as pd

df1 = TicketReportBuilder('2021-10-01', '2021-10-31', relatorio_limpo=False)

i = 0.005

df1.gerar_notas_periodo(gerar_resumo=True, menor_nota=3, maior_nota=8.5, coef_quantidade=0.15, coef_dificuldade=i, solucao=1, fechamento=0)
df = df1.get_dataframe()
df = df[['Técnico', 'Nota final']]
while i < 0.3:
    df1.gerar_notas_periodo(gerar_resumo=True, menor_nota=3, maior_nota=8.5, coef_quantidade=0.15, coef_dificuldade=i, solucao=1, fechamento=0)
    df_aux = df1.get_dataframe()
    df = df.merge(df_aux[['Técnico', 'Nota final']], 'left', on='Técnico')
    i += 0.005
    print(i)

df.to_excel('graph.xlsx', index=False)
