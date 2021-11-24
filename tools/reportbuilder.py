import datetime
import numpy as np
import pandas as pd
from os import startfile


class ReportBuilder:
    """Classe para criação de relatórios personalizados

    Com esta classe, é possível montar relatórios selecionando quais informações serão mantidas ou não. Ela também
    auxilia na segregação do código, pois facilita a adição de novas informações ao relatório através de métodos
    que podem ser adicionados.

    Atributos:
        connection: conexão a qual se deseja usar para extrair dados
        initial_date: data inicial dos dados
        final_date: data final dos dados
        label: nome do arquivo a ser exportado
        relatorio_limpo: variável booleana para definir se as colunas inutilizadas serão excluídas ou mantidas.
    """
    def __init__(self, connection, initial_date: str, final_date: str, relatorio_limpo: bool = True, convert_seconds: bool = True):
        self.connection = connection
        self.initial_date = initial_date
        self.final_date = final_date
        self.relatorio_limpo = relatorio_limpo
        self.convert_seconds = convert_seconds       

    def tickets_report(self):
        """Gera relatório de chamados do período desejado

        :param convert_seconds: opção para converter os segundos em número de série de data/hora usados no excel"""

        first_day = f'{self.initial_date[:4]}-01-01'

        query = open("setup/query_ticket_assigned.sql", "r").read()

        df = pd.read_sql_query(
            sql=query,
            con=self.connection,
            params={
                "first_day": first_day,
                "initial_date": self.initial_date,
                "final_date": self.final_date
                }
            )

        # Coluna auxiliar para criar valor de tempo interpretado pelo excel
        df['tempo_fechamento'] = df['close_delay_stat'] / (24*60*60)
        # Coluna auxiliar para criar valor de tempo interpretado pelo excel
        df['tempo_solucao'] = df['solve_delay_stat'] / (24*60*60)
        df['tempo_medio_solucao'] = df['tempo_medio_solucao'] / (24*60*60)
        df['tempo_medio_fechamento'] = df['tempo_medio_fechamento'] / \
            (24*60*60)
        # Retorna apenas a data, removendo o horário da data do chamado
        #df['date'] = df['date'].dt.date
        if self.convert_seconds:
            df['close_delay_stat'] = pd.to_datetime(df["close_delay_stat"], unit='s').dt.strftime(
                "%H:%M:%S")  # transforma o tempo de fechamento de segundos para formato de horário
            df['solve_delay_stat'] = pd.to_datetime(df["solve_delay_stat"], unit='s').dt.strftime(
                "%H:%M:%S")  # transforma o tempo de fechamento de segundos para formato de horário
        # substitui '1' por 'Incidente' e '2' por 'Requisição'
        df['type'].replace({1: 'Incidente', 2: 'Requisição'}, inplace=True)
        # Coluna tipo booleana que retorna VERDADEIRO caso o ticket tenha atraso
        df['atraso'] = np.logical_or(
            df['solvedate'] > df['time_to_resolve'], df['time_to_resolve'] == "")
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].dt.strftime('%Y-%m')
        # relatório limpo (coloque o parâmetro clean_report=False caso queira o relatório completo)
        if self.relatorio_limpo:
            df.drop(labels=['name', 'date_mod', 'users_id_lastupdater', 'content', 'global_validation', 'ola_waiting_duration', 'olas_id_tto', 'olas_id_ttr', 'olalevels_id_ttr',
                            'internal_time_to_resolve', 'internal_time_to_own', 'validation_percent', 'requesttypes_id'], axis=1, inplace=True)
            df = df[df.nome_tecnico != 'Pedro']


        self.df = df

    def tickets_report_actualtime(self):
        """Gera relatório de chamados do período desejado com tempos do ActualTime (em desenvolvimento)

        Irá retornar o tempo total que cada técnico gastou em cada um dos chamados,
        somando o total de tarefas deste técnico no respectivo chamado. A query não retornará
        tarefas que não tenham um técnico atribuído, nem tarefas que não possuam tempo cronometrado
        ou tempo escolhido através do dropdown nativo do GLPI.

        :param initial_date: data inicial na forma yyyy-mm-dd
        :param final_date: data final na forma yyyy-mm-dd
        :param clean_report: opção de limpar ou não o relatório, removento colunas inutilizadas.
        :param convert_seconds: opção para converter os segundos em número de série de data/hora usados no excel"""

        query = open("setup/query_actualtime.sql", "r").read()

        df = pd.read_sql_query(
            sql=query,
            con=self.connection,
            params={"initial_date":self.initial_date, "final_date":self.final_date}
            )
        df.loc[df['tempo_via_plugin'] > 1000000000, 'tempo_via_plugin'] = 0
        df['tempo_eleito'] = np.where(df['tempo_via_plugin'].isnull(), df['tempo_via_glpi'], df['tempo_via_plugin'])
        df['tempo_eleito'] = df['tempo_eleito'] / (24*60*60)

        self.df = df

    def export_excel(self, label, start_file=True):
        """Exporta um dataframe do pandas para arquivo em excel.

        :param label: nome base do arquivo para salvamento. A função automaticamente remove espaços vazios e os substitui por '_', além de inserir a data no final
        :param start_file: opção de iniciar o arquivo no excel ou apenas salvá-lo sem abrir a aplicação.
        """
        label = f"{label.replace(' ','_')}_{datetime.date.today()}.xlsx"
        file_name = f".\\reports\\{label}"
        self.df.to_excel(file_name, index=False)
        print(f'Arquivo salvo em: {file_name}')
        if start_file:
            startfile(file_name)

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
        data_frame[f'max_mes_{col_name}'] = data_frame.groupby(['date'])[f'delta_tempo_{col_name}'].transform('max')
        data_frame[f'min_mes_{col_name}'] = data_frame.groupby(['date'])[f'delta_tempo_{col_name}'].transform('min')    
        data_frame[f'delta_tempo_{col_name}_normalized'] = (data_frame[f'delta_tempo_{col_name}'] - data_frame[f'min_mes_{col_name}']) \
            / (data_frame[f'max_mes_{col_name}'] - data_frame[f'min_mes_{col_name}'])
        data_frame[f'diferenca_media_vs_gasto_{col_name}'] = data_frame[f'delta_tempo_{col_name}'] / data_frame[f'tempo_medio_{col_name}']

        if self.relatorio_limpo:           
            data_frame.drop(columns=[f'max_mes_{col_name}', f'min_mes_{col_name}'], inplace=True)

    def average_grade(self, peso_fechamento=0, peso_solucao=1):
        """Calcula a média das notas dos tempos de acordo com os pesos repassados)

        :param data_frame: dataFrame a ser utilizado
        :param peso_fechamento: peso atribuiído a nota do tempo de fechamento chamado (padrão=1)
        :param peso_solucao: peso atribuído a nota de solução do chamado (padrão=1)
        """
        self.peso_fechamento = peso_fechamento
        self.peso_solucao = peso_solucao
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
        data_frame['qtde_chamados'] = data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count')
        data_frame['bonus'] = 1+bonus_percentual*(data_frame['qtde_chamados'] - data_frame.groupby(['date'])['qtde_chamados'].transform('min')) / (
            data_frame.groupby(['date'])['qtde_chamados'].transform('max') - data_frame.groupby(['date'])['qtde_chamados'].transform('min'))
        data_frame['nota_final_tempos'] = data_frame['nota_final_tempos'] * \
            data_frame['bonus']
        #data_frame['nota_final_tempos'] = data_frame['nota_final_tempos'].clip(upper=1)
        data_frame['nota_final_tempos'] = (
            data_frame['nota_final_tempos'] / data_frame.groupby(['date'])['nota_final_tempos'].transform('max'))
        if self.relatorio_limpo:
            data_frame.drop(columns=['bonus', 'qtde_chamados'], inplace=True)

    def grade_summary(self):
        f = {
            'id': 'nunique',
            'tempo_fechamento': np.mean,
            'diferenca_media_vs_gasto_fechamento': np.mean,
            'tempo_solucao': np.mean,
            'diferenca_media_vs_gasto_solucao': np.mean,
            'nota_final_tempos': np.mean
        }
        if self.peso_solucao == 0:
            f.pop('tempo_solucao')
            f.pop('diferenca_media_vs_gasto_solucao')

        if self.peso_fechamento == 0:
            f.pop('tempo_fechamento')
            f.pop('diferenca_media_vs_gasto_fechamento')

        data_frame = self.df

        g = data_frame.groupby(['nome_tecnico', 'date'])
        v1 = g.agg(f)
        v2 = g.agg(lambda x: x.drop_duplicates(
            subset='id', keep='first').atraso.sum())
        new_df = pd.concat([v1, v2.to_frame('atraso')], axis=1)
        new_df = new_df.reset_index()
        self.df = new_df
        if 'nome_observador' in self.df.columns:
            g = data_frame.groupby(['nome_observador', 'date'])
            v3 = g.agg({'id': 'count'})
            final_df = pd.concat([new_df, v3], axis=1)
            final_df = final_df.reset_index()
            final_df = final_df.rename(columns={
                'level_0': 'nome',
                'id': 'qtde_chamados'
            })
            self.df = final_df

    def quick_report(self):
        self.tickets_report()
        self.compute_time_grades('fechamento')
        self.compute_time_grades('solucao')
        self.average_grade()
        self.get_monthly_quantity_bonus()
        self.export_excel('tickets')

    def quick_summary(self):
        self.tickets_report()
        self.compute_time_grades('fechamento')
        self.compute_time_grades('solucao')
        self.average_grade()
        self.get_monthly_quantity_bonus()
        self.grade_summary()
        self.export_excel('notas')

