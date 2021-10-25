import pandas as pd
import numpy as np
from report_tools.query_builder import tickets_report


def grade_calculator(initial_date, final_date):
    df = tickets_report(initial_date, final_date,
                        start_file=False, save_file=False)
    df = df[df.nome_tecnico != 'Pedro Borges']
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime('%Y-%m')

    return df


def compute_partial_grade(data_frame, col, inversed_proportion=False, reduction_constant=0.25, agg_method='mean'):
    """Calcula a pré-nota da coluna passada, já calculando a média, o desvio padrão, 
    o coeficiente de achatamento e a nota parcial obtida.

    : col (string): coluna da qual será calculada a média

    : inversed_proportion (boolean): define se a nota será diretamente/inversamente proporcional ao valor de referência

    : reducion_constant (float): constante de redução do coeficiente de achatameneto.
    """
    proportion_inverter = 1
    if inversed_proportion:
        proportion_inverter = -1
    col_name = f'temp_{agg_method}_{col}'

    data_frame[col_name] = (data_frame.groupby(['date', 'nome_tecnico'])[
                            col].transform(agg_method))  # Agregação mensal por funcionário
    mean_col = np.mean(data_frame[col_name].unique())
    std_col = np.std(data_frame[col_name].unique())

    if reduction_constant * (std_col / mean_col) >= 0.25:
        coef_achatamento = 0.25
    else:
        coef_achatamento = reduction_constant * (std_col / mean_col)

    data_frame[f'nota_{col}'] = ((data_frame[col_name] / mean_col)**proportion_inverter +
                                 coef_achatamento*(1 - ((data_frame[col_name] / mean_col)**proportion_inverter)))
    data_frame[f'nota_final_{col}'] = (data_frame[f'nota_{col}'] / (1.05*data_frame[f'nota_{col}'].max())) / (
        data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count'))

    data_frame.drop(columns=col_name, inplace=True)

    #print(f'média: {mean_col} / desvio padrão: {std_col}')
