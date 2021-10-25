import pandas as pd
import numpy as np
from report_tools.query_builder import tickets_report


def grade_calculator(initial_date, final_date):
    """
        Prepara o relatório para cálculo dos diversos parâmetros necessários na definição da nota

        :param initial_date str: Data inicial
        :param final_date str: Data final
        :returns: retorna um dataframe do pandas  

    """
    df = tickets_report(initial_date, final_date)
    df = df[df.nome_tecnico != 'Pedro']
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime('%Y-%m')

    return df


def compute_time_grades(data_frame, col_name, excluir_coluna=True):
    """Calcula a nota dos valores de tempo desejados

    A fórmula retorna a nota diretamente no data_frame repassado a ela, sendo
    assim sem return. Neste caso é retornada a nota normalizada, ou seja, um valor
    que irá variar de 0 a 1.  

    :param data_frame: dataframe usado no cálculo
    :param col_name: nome da coluna cuja nota será calculada
    :param excluir_coluna: exclui as colunas complementares que foram criadas apenas para serem usadas no cálculo
    """
    data_frame[f'delta_tempo_{col_name}'] = data_frame[f'tempo_medio_{col_name}'] - \
        data_frame[f'tempo_{col_name}']
    data_frame[f'delta_tempo_{col_name}_normalized'] = (data_frame[f'delta_tempo_{col_name}'] - data_frame[f'delta_tempo_{col_name}'].min()) / (
        data_frame[f'delta_tempo_{col_name}'].max() - data_frame[f'delta_tempo_{col_name}'].min())
    if excluir_coluna:
        data_frame.drop(columns=f'delta_tempo_{col_name}', inplace=True)


def average_grade(data_frame, peso_fechamento=1, peso_solucao=1, excluir_coluna=True):
    """Calcula a média das notas dos tempos de acordo com os pesos repassados)
    
    :param data_frame: dataFrame a ser utilizado
    :param peso_fechamento: peso atribuiído a nota do tempo de fechamento chamado (padrão=1)
    :param peso_solucao: peso atribuído a nota de solução do chamado (padrão=1)
    :param ecluir_conta =  opção de if a camera do celular
    """

    data_frame['nota_final_tempos'] = (data_frame['delta_tempo_fechamento_normalized'] * peso_fechamento +
                                       data_frame['delta_tempo_solucao_normalized'] * peso_solucao) / (peso_fechamento+peso_solucao)
    
    if excluir_coluna:
        data_frame.drop(columns=['delta_tempo_fechamento_normalized',
                        'delta_tempo_solucao_normalized'], inplace=True)


def get_monthly_quantity_bonus(data_frame, bonus_percentual=0.2, excluir_coluna=True):
    """Calcula o bônus devido a quantidade.
    
    A fórmula encontra a quantidade de chamados mensais por técnico, atribuindo uma bonificação percentual que varia de 0 a 20%, sendo o técnico
    com a maior quantidade de chamados a pessoa que irá receber a maior bonificação. Note que as notas serão geradas já de forma normalizada.

    :param data_frame: data frame onde os bônus serão calculados.
    :param excluir_coluna: define se a coluna dos valores de bonificação será excluída ou não do relatório final"""

    data_frame['bonus'] = 1+bonus_percentual*(data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count') - data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count').min()) / (
        data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count').max(
        ) - data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count').min()
    )
    data_frame['nota_final_tempos'] = data_frame['nota_final_tempos'] * data_frame['bonus']
    #data_frame['nota_final_tempos'] = data_frame['nota_final_tempos'].clip(upper=1)
    data_frame['nota_final_tempos'] = (
        data_frame['nota_final_tempos'] / data_frame['nota_final_tempos'].max())
    
    if excluir_coluna:
        data_frame.drop(columns='bonus', inplace=True)


def grade_summary(data_frame):
    """Gera o sumário das notas por mês
    
    Esta função irá gerar uma pivot_table do pandas com o intuito de gerar os dados de forma previamente resumida, sem a necessidade
    de manipulação de tabelas dinâmicas do excel. O objetivo é criar uma base de dados padronizada para no futuro apenas atualizarmos essa base
    e recebermos a nota automaticamente através de uma outra planilha de fórmulas.
    
    :param data_frame: data frame base para formatação das notas resumidas mensalmente."""
    pivot_df = data_frame.pivot_table(['id', 'tempo_fechamento', 'tempo_solucao', 'atraso', 'nota_final_tempos'], index=['nome_tecnico', 'date'],
                                      aggfunc={'id': 'count',
                                               'tempo_fechamento': np.mean,
                                               'tempo_solucao': np.mean,
                                               'atraso': 'sum',
                                               'nota_final_tempos': np.mean
                                               })
    
    col_order = ['id', 'atraso', 'tempo_fechamento', 'tempo_solucao', 'nota_final_tempos']
    pivot_df.reset_index()
    pivot_df = pivot_df.reindex(col_order, axis=1)
    pivot_df = pivot_df.reset_index()
    return pivot_df
