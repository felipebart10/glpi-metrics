import pandas as pd
from tools.reportbuilder import TicketReportBuilder, ChangeReportBuilder, ProblemReportBuilder, ActualtimeReportBuilder, GenericBuilder

# Intervalo de tempo desejado:
data_inicial = '2021-01-01'
data_final = '2022-01-11'

# Agrega funções de script num arquivo só. Altere parâmetros internos para personalizar o relatório.

def salvar_relatorio_tickets(data_inicial, data_final):
    df = TicketReportBuilder(data_inicial, data_final)
    df.gerar_notas_periodo(gerar_resumo=False,solucao=1, excluir_pedro=False, relatorio_limpo=False)
    df.exportar_dataframe('base_powerbi', iniciar_arquivo=False)

def salvar_relatorio_problemas(data_inicial, data_final):
    df = ProblemReportBuilder(data_inicial, data_final)
    df.gerar_relatorio()
    df.exportar_dataframe('base_problemas', iniciar_arquivo=False)

def salvar_relatorio_mudancas(data_inicial, data_final):
    df = ChangeReportBuilder(data_inicial, data_final)
    df.gerar_relatorio()
    df.exportar_dataframe('base_mudanças', iniciar_arquivo=False)

def salvar_relatorio_actualtime(data_inicial, data_final):
    df = ActualtimeReportBuilder(data_inicial, data_final)
    df.gerar_relatorio(gerar_resumo=False, excluir_discrepantes=True, excluir_pedro=False)
    df.exportar_dataframe('actualtime', iniciar_arquivo=False)

def salvar_relatorio_usuarios():
    df = GenericBuilder('users_count')
    df.ler_query()
    df.exportar_dataframe('quantidade_usuarios', iniciar_arquivo=False)

def salvar_relatorio_combinado(data_inicial, data_final):
    df1 = TicketReportBuilder(data_inicial, data_final)
    df1.gerar_relatorio_combinado(gerar_resumo=False,solucao=1, excluir_pedro=False, relatorio_limpo=False)
    df_tickets = df1.get_dataframe()
    df2 = ProblemReportBuilder(data_inicial, data_final)
    df2.gerar_relatorio()
    df_problemas = df2.get_dataframe()
    df3 = ChangeReportBuilder(data_inicial, data_final)
    df3.gerar_relatorio()
    df_mudancas = df3.get_dataframe()
    new_df = pd.concat([df_tickets, df_mudancas, df_problemas])
    df = GenericBuilder('actualtime')
    df.set_dataframe(new_df)
    df.exportar_dataframe('relatório combinado')

salvar_relatorio_tickets(data_inicial, data_final)
salvar_relatorio_mudancas(data_inicial, data_final)
salvar_relatorio_problemas(data_inicial, data_final)
salvar_relatorio_actualtime(data_inicial, data_final)
salvar_relatorio_usuarios()
#salvar_relatorio_combinado(data_inicial, data_final)