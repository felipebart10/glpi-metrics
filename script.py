from tools.reportbuilder import TicketReportBuilder, ChangeReportBuilder, ProblemReportBuilder, ActualtimeReportBuilder, GenericBuilder

# Intervalo de tempo desejado:
data_inicial = '2021-12-01'
data_final = '2021-12-31'

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


salvar_relatorio_mudancas(data_inicial, data_final)
salvar_relatorio_problemas(data_inicial, data_final)