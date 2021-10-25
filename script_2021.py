import numpy as np
from report_tools.query_builder import tickets_report
from report_tools.query_builder import export_excel

# # # # # # # # # # # # # # # # SCRIPT PARA GERAÇÃO DE NOTAS - 2021 # # # # # # # # # # # # # # # # #

# Parâmetros
data_inicial = '2021-08-01'
data_final = '2021-08-31'

# Geração de relatório
df = tickets_report(data_inicial, data_final)

df['date'] = df['date'].dt.strftime('%Y-%m')

pivot_df = df.pivot_table(['id', 'tempo_fechamento', 'tempo_solucao', 'tempo_medio_solucao', 'atraso'], index=['nome_tecnico', 'date'],
                            aggfunc={'id': 'count',
                                    'tempo_fechamento': np.mean,
                                    'tempo_solucao': np.mean,
                                    'tempo_medio_solucao': np.mean,
                                    'atraso': 'sum'
                                    })

col_order = ['id', 'atraso', 'tempo_fechamento', 'tempo_solucao']
pivot_df = pivot_df.reindex(col_order, axis=1)
pivot_df = pivot_df.drop(index="Pedro")

def computePartialGrade(col, inversed_proportion=False, reduction_constant=0.25):
    """Calcula a pré-nota da coluna passada, já calculando a média, o desvio padrão, 
    o coeficiente de achatamento e a nota parcial obtida.

    : col (string): coluna da qual será calculada a média

    : inversed_proportion (boolean): define se a nota será diretamente/inversamente proporcional ao valor de referência

    : reducion_constant (float): constante de redução do coeficiente de achatameneto.
    """
    coef_achatamento = 0.25 if reduction_constant * (np.std(pivot_df[col] / np.mean(pivot_df[col]))) >= 0.25 else reduction_constant * (np.std(pivot_df[col] / np.mean(pivot_df[col])))
    if inversed_proportion:
        pivot_df[f'nota_{col}'] = 1/(pivot_df[col] / np.mean(pivot_df[col])) + coef_achatamento*(1 - 1/(pivot_df[col] / np.mean(pivot_df[col])))        
    else:
        pivot_df[f'nota_{col}'] = pivot_df[col] / np.mean(pivot_df[col]) + coef_achatamento*(1- (pivot_df[col] / np.mean(pivot_df[col])))
    pivot_df[f'nota_final_{col}'] = pivot_df[f'nota_{col}'] / (1.05*pivot_df[f'nota_{col}'].max())

# Calcular as notas de cada um dos critérios
computePartialGrade('id', reduction_constant=0.5)
computePartialGrade('tempo_fechamento', True)
computePartialGrade('tempo_solucao', True)
computePartialGrade('id', reduction_constant=0.5)
computePartialGrade('tempo_fechamento', True)
computePartialGrade('tempo_solucao', True)

export_excel(pivot_df.reset_index(), 'grades report')

