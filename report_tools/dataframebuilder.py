import datetime
import numpy as np
import pandas as pd
from inc.sshcon import mysql_connect, open_ssh_tunnel
from os import startfile


class DataFrameBuilder:
    def __init__(self, initial_date: str, final_date: str, label: str, relatorio_limpo: bool = True):
        self.initial_date = initial_date
        self.final_date = final_date
        self.label = f"{label.replace(' ','_')}_{datetime.date.today()}.xlsx"
        self.relatorio_limpo = relatorio_limpo

    def tickets_report(self, convert_seconds=True):
        """Gera relatório de chamados do período desejado

        :param initial_date: data inicial na forma yyyy-mm-dd
        :param final_date: data final na forma yyyy-mm-dd
        :param clean_report: opção de limpar ou não o relatório, removento colunas inutilizadas.
        :param convert_seconds: opção para converter os segundos em número de série de data/hora usados no excel"""

        open_ssh_tunnel()
        connection = mysql_connect()

        first_day = f'{self.initial_date[:4]}-01-01'

        df = pd.read_sql(f"""
        SELECT t.*, ic.name AS nome_categoria, rt.name AS origem, u.firstname AS nome_tecnico, o.nome_observador, c.avg_time AS tempo_medio_fechamento, d.avg_time AS tempo_medio_solucao  
        FROM glpi_tickets t

        LEFT JOIN glpi_itilcategories ic
        ON t.itilcategories_id = ic.id

        LEFT JOIN glpi_tickets_users tu
        ON t.id = tu.tickets_id AND
        tu.type = 2

        LEFT JOIN glpi_requesttypes rt
        ON t.requesttypes_id = rt.id

        LEFT JOIN glpi_users u
        ON u.id = tu.users_id

        LEFT JOIN (
            SELECT ic.id, ic.completename, avg(t.close_delay_stat) AS avg_time FROM glpi_tickets t 
            LEFT JOIN glpi_itilcategories ic 
            ON t.itilcategories_id = ic.id 
            WHERE (DATE(t.date) BETWEEN %s AND %s)
            GROUP BY t.itilcategories_id
            ) c
        ON t.itilcategories_id = c.id    

        LEFT JOIN (
            SELECT ic.id, ic.completename, avg(t.solve_delay_stat) AS avg_time FROM glpi_tickets t 
            LEFT JOIN glpi_itilcategories ic 
            ON t.itilcategories_id = ic.id 
            WHERE (DATE(t.date) BETWEEN %s AND %s)
            GROUP BY t.itilcategories_id
            ) d
        ON t.itilcategories_id = d.id

        LEFT JOIN (
            SELECT DISTINCT t.id, u2.firstname AS nome_observador FROM glpi_tickets t 
            LEFT JOIN glpi_tickets_users tu2
            ON t.id = tu2.tickets_id AND
            tu2.type = 3
            LEFT JOIN glpi_users u2
            ON u2.id = tu2.users_id AND
            (u2.groups_id = 1 OR u2.groups_id = 2) AND
            u2.id <> 6
            WHERE (DATE(t.date) BETWEEN %s AND %s)
            ) o
        ON t.id = o.id AND o.nome_observador IS NOT NULL

        WHERE (DATE(t.date) BETWEEN %s AND %s) AND
        t.status = 6 

        """, connection, params=[first_day, self.final_date, first_day, self.final_date, self.initial_date, self.final_date, self.initial_date, self.final_date])

        # Coluna auxiliar para criar valor de tempo interpretado pelo excel
        df['tempo_fechamento'] = df['close_delay_stat'] / (24*60*60)
        # Coluna auxiliar para criar valor de tempo interpretado pelo excel
        df['tempo_solucao'] = df['solve_delay_stat'] / (24*60*60)
        df['tempo_medio_solucao'] = df['tempo_medio_solucao'] / (24*60*60)
        df['tempo_medio_fechamento'] = df['tempo_medio_fechamento'] / \
            (24*60*60)
        # Retorna apenas a data, removendo o horário da data do chamado
        #df['date'] = df['date'].dt.date
        if convert_seconds:
            df['close_delay_stat'] = pd.to_datetime(df["close_delay_stat"], unit='s').dt.strftime(
                "%H:%M:%S")  # transforma o tempo de fechamento de segundos para formato de horário
            df['solve_delay_stat'] = pd.to_datetime(df["solve_delay_stat"], unit='s').dt.strftime(
                "%H:%M:%S")  # transforma o tempo de fechamento de segundos para formato de horário
        # substitui '1' por 'Incidente' e '2' por 'Requisição'
        df['type'].replace({1: 'Incidente', 2: 'Requisição'}, inplace=True)
        # Coluna tipo booleana que retorna VERDADEIRO caso o ticket tenha atraso
        df['atraso'] = np.logical_or(
            df['solvedate'] > df['time_to_resolve'], df['time_to_resolve'] == "")
        # relatório limpo (coloque o parâmetro clean_report=False caso queira o relatório completo)
        if self.relatorio_limpo:
            df.drop(labels=['name', 'date_mod', 'users_id_lastupdater', 'content', 'global_validation', 'ola_waiting_duration', 'olas_id_tto', 'olas_id_ttr', 'olalevels_id_ttr',
                            'internal_time_to_resolve', 'internal_time_to_own', 'validation_percent', 'requesttypes_id'], axis=1, inplace=True)

        self.df = df

    def export_excel(self, start_file=True):
        """Exporta um dataframe do pandas para arquivo em excel.

        :param data_frame: data_frame que se deseja exportar
        :param label: nome base do arquivo para salvamento. A função automaticamente remove espaços vazios e os substitui por '_', além de inserir a data no final
        :param star_file: opção de iniciar o arquivo no excel ou apenas salvá-lo sem abrir a aplicação.
        """
        file_name = f".\\reports\\{self.label}"
        self.df.to_excel(file_name, index=False)
        print(f'Arquivo salvo em: {file_name}')
        if start_file:
            startfile(file_name)

    def grade_calculator(self):
        """
            Prepara o relatório para cálculo dos diversos parâmetros necessários na definição da nota

            :param initial_date str: Data inicial
            :param final_date str: Data final
            :returns: retorna um dataframe do pandas  

        """
        self.df = self.df[self.df.nome_tecnico != 'Pedro']
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['date'] = self.df['date'].dt.strftime('%Y-%m')

        return self.df

    def compute_time_grades(self, col_name):
        """Calcula a nota dos valores de tempo desejados

        A fórmula retorna a nota diretamente no data_frame repassado a ela, sendo
        assim sem return. Neste caso é retornada a nota normalizada, ou seja, um valor
        que irá variar de 0 a 1.  

        :param data_frame: dataframe usado no cálculo
        :param col_name: nome da coluna cuja nota será calculada
        :param excluir_coluna: exclui as colunas complementares que foram criadas apenas para serem usadas no cálculo
        """
        data_frame = self.df
        data_frame[f'delta_tempo_{col_name}'] = data_frame[f'tempo_medio_{col_name}'] - \
            data_frame[f'tempo_{col_name}']
        data_frame[f'delta_tempo_{col_name}_normalized'] = (data_frame[f'delta_tempo_{col_name}'] - data_frame[f'delta_tempo_{col_name}'].min()) / (
            data_frame[f'delta_tempo_{col_name}'].max() - data_frame[f'delta_tempo_{col_name}'].min())
        if self.relatorio_limpo:
            data_frame.drop(columns=f'delta_tempo_{col_name}', inplace=True)

    def average_grade(self, peso_fechamento=1, peso_solucao=1):
        """Calcula a média das notas dos tempos de acordo com os pesos repassados)

        :param data_frame: dataFrame a ser utilizado
        :param peso_fechamento: peso atribuiído a nota do tempo de fechamento chamado (padrão=1)
        :param peso_solucao: peso atribuído a nota de solução do chamado (padrão=1)
        :param ecluir_conta =  opção de if a camera do celular
        """
        data_frame = self.df
        data_frame['nota_final_tempos'] = (data_frame['delta_tempo_fechamento_normalized'] * peso_fechamento +
                                           data_frame['delta_tempo_solucao_normalized'] * peso_solucao) / (peso_fechamento+peso_solucao)

        if self.relatorio_limpo:
            data_frame.drop(columns=['delta_tempo_fechamento_normalized',
                            'delta_tempo_solucao_normalized'], inplace=True)

    def get_monthly_quantity_bonus(self, bonus_percentual=0.2):
        """Calcula o bônus devido a quantidade.

        A fórmula encontra a quantidade de chamados mensais por técnico, atribuindo uma bonificação percentual que varia de 0 a 20%, sendo o técnico
        com a maior quantidade de chamados a pessoa que irá receber a maior bonificação. Note que as notas serão geradas já de forma normalizada.

        :param data_frame: data frame onde os bônus serão calculados.
        :param excluir_coluna: define se a coluna dos valores de bonificação será excluída ou não do relatório final"""
        data_frame = self.df
        data_frame['bonus'] = 1+bonus_percentual*(data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count') - data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count').min()) / (
            data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count').max(
            ) - data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count').min()
        )
        data_frame['nota_final_tempos'] = data_frame['nota_final_tempos'] * \
            data_frame['bonus']
        #data_frame['nota_final_tempos'] = data_frame['nota_final_tempos'].clip(upper=1)
        data_frame['nota_final_tempos'] = (
            data_frame['nota_final_tempos'] / data_frame['nota_final_tempos'].max())

        if self.relatorio_limpo:
            data_frame.drop(columns='bonus', inplace=True)

    def grade_summary(self):
        """Gera o sumário das notas por mês

        Esta função irá gerar uma pivot_table do pandas com o intuito de gerar os dados de forma previamente resumida, sem a necessidade
        de manipulação de tabelas dinâmicas do excel. O objetivo é criar uma base de dados padronizada para no futuro apenas atualizarmos essa base
        e recebermos a nota automaticamente através de uma outra planilha de fórmulas.

        :param data_frame: data frame base para formatação das notas resumidas mensalmente."""
        data_frame = self.df
        pivot_df = data_frame.pivot_table(['id', 'nome_observador', 'tempo_fechamento', 'tempo_solucao', 'atraso', 'nota_final_tempos'], index=['nome_tecnico', 'date'],
                                          aggfunc={'id': 'nunique',
                                                   'tempo_fechamento': np.mean,
                                                   'tempo_solucao': np.mean,
                                                   'atraso': 'sum',
                                                   'nota_final_tempos': np.mean
                                                   })

        col_order = ['id', 'atraso', 'tempo_fechamento',
                     'tempo_solucao', 'nota_final_tempos']
        pivot_df.reset_index()
        pivot_df = pivot_df.reindex(col_order, axis=1)
        pivot_df = pivot_df.reset_index()
        return pivot_df

    def grade_summary_2(self):
        f = {
            'id': 'nunique',
            'tempo_fechamento': np.mean,
            'tempo_solucao': np.mean,
            'nota_final_tempos': np.mean
        }

        data_frame = self.df

        g = data_frame.groupby(['nome_tecnico', 'date'])
        v1 = g.agg(f)
        v2 = g.agg(lambda x: x.drop_duplicates(
            subset='id', keep='first').atraso.sum())
        new_df = pd.concat([v1, v2.to_frame('atraso')], axis=1)
        #new_df = new_df.reset_index().rename(columns={'id': 'chamados_atribuidos'})

        g = data_frame.groupby(['nome_observador', 'date'])
        v3 = g.agg({'id': 'count'})
        #v3 = v3.reset_index().rename(columns={'id': 'chamados_observados'})
        final_df = pd.concat([new_df, v3], axis=1)
        self.df = final_df.reset_index().rename(
            columns={'id': 'chamados_atribuidos'})

    def quick_report(self):
        self.tickets_report()
        self.grade_calculator()
        self.compute_time_grades('fechamento')
        self.compute_time_grades('solucao')
        self.average_grade()
        self.get_monthly_quantity_bonus()
        self.export_excel()

    def quick_summary(self):
        self.tickets_report()
        self.grade_calculator()
        self.compute_time_grades('fechamento')
        self.compute_time_grades('solucao')
        self.average_grade()
        self.get_monthly_quantity_bonus()
        self.grade_summary_2()
        self.export_excel()
