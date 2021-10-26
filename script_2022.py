from report_tools.gradescalculator3 import grade_calculator, compute_time_grades, get_monthly_quantity_bonus, average_grade, grade_summary
from report_tools.query_builder import export_excel
import configparser as cp

parser = cp.ConfigParser()
parser.read('config.ini')

# # # # # # # # SCRIPT PARA GERAÇÃO DE RELATÓRIOS E NOTAS # # # # # # # #

# Parâmetros
data_inicial = parser['REPORT PARAMETERS']['data_inicial']
data_final = parser['REPORT PARAMETERS']['data_final']
peso_fechamento = float(parser['REPORT PARAMETERS']['peso_fechamento'])
peso_solucao = float(parser['REPORT PARAMETERS']['peso_solucao'])
bonus_por_quantidade = float(parser['REPORT PARAMETERS']['bonus_por_quantidade'])
nome_relatorio_dados = parser['REPORT PARAMETERS']['nome_relatorio_dados']
nome_sumario = parser['REPORT PARAMETERS']['nome_sumario']
excluir_colunas_aux = parser.getboolean('REPORT PARAMETERS', 'excluir_colunas_aux')
gerar_sumario = parser.getboolean('REPORT PARAMETERS', 'gerar_sumario')
abrir_excel = parser.getboolean('REPORT PARAMETERS', 'abrir_excel')

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

