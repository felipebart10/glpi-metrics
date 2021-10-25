from report_tools.gradescalculator3 import grade_calculator, compute_time_grades, get_monthly_quantity_bonus, average_grade, grade_summary
from report_tools.query_builder import export_excel

# # # # # # # # SCRIPT PARA GERAÇÃO DE RELATÓRIOS E NOTAS # # # # # # # #

# Parâmetros
data_inicial = '2021-08-01'
data_final = '2021-08-31'
peso_fechamento = 1
peso_solucao = 2
bonus_por_quantidade = 0.5
excluir_colunas_aux = False
nome_relatorio_dados = 'dados'
nome_sumario = 'resumo notas'
gerar_sumario = False
abrir_excel = True

# Geração do relatório
df = grade_calculator(data_inicial, data_final)

# Cálculo da nota dos tempos
compute_time_grades(df, 'fechamento', excluir_colunas_aux)
compute_time_grades(df, 'solucao', excluir_colunas_aux)
average_grade(df, peso_fechamento, peso_solucao, excluir_colunas_aux)

# Cálculo do bônus
get_monthly_quantity_bonus(df, bonus_por_quantidade,  excluir_colunas_aux)

# Geração de dados
export_excel(df, nome_relatorio_dados, start_file=abrir_excel)

# Geração do sumário
if gerar_sumario:
    pivot_df = grade_summary(df)
    export_excel(pivot_df, nome_sumario, start_file=abrir_excel)

