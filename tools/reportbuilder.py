import datetime
import numpy as np
import pandas as pd
from os import startfile
from .databaseconnector import DataBaseConnector

class GenericBuilder:
    def __init__(self, query, data_inicial: str, data_final: str):
        self.query = query
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.set_conexao()
        
    def set_conexao(self):
        connector_object = DataBaseConnector()
        connector_object.set_tunel_ssh()
        connector_object.set_conexao_database()
        self.con = connector_object.get_conexao_database()

    def ler_query(self):
        first_day = f'{self.data_inicial[:4]}-01-01'
        query = open(f"setup/query_{self.query}.sql", "r").read()
        df = pd.read_sql_query(
            sql=query,
            con=self.con,
            params={
                "first_day": first_day,
                "initial_date": self.data_inicial,
                "final_date": self.data_final
                }
            )           
        self.df_base = df
        self.df_cru = self.df_base.copy(deep=True)
        return self.df_base    
    
    def exportar_dataframe(self, label, iniciar_arquivo=True):
        """Exporta um dataframe do pandas para arquivo em excel.

        :param label: nome base do arquivo para salvamento. A função automaticamente remove espaços vazios e os substitui por '_', além de inserir a data no final
        :param start_file: opção de iniciar o arquivo no excel ou apenas salvá-lo sem abrir a aplicação.
        """
        label = f"{label.replace(' ','_')}_{datetime.date.today()}.xlsx"
        file_name = f".\\reports\\{label}"
        self.df_base.to_excel(file_name, index=False)
        print(f'Arquivo salvo em: {file_name}')
        if iniciar_arquivo:
            startfile(file_name)

    def exportar_dataframe_cru(self, iniciar_arquivo=True):
        """Exporta o relatório sem as alterações aplicadas.

        :param start_file: opção de iniciar o arquivo no excel ou apenas salvá-lo sem abrir a aplicação.
        """
        label = f"relatorio_cru_{datetime.date.today()}.xlsx"
        file_name = f".\\reports\\{label}"
        self.df_cru.to_excel(file_name, index=False)
        print(f'Arquivo salvo em: {file_name}')
        if iniciar_arquivo:
            startfile(file_name)

class TicketReportBuilder(GenericBuilder):
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
        convert_seconds: converte os segundos para o valor decimal que o excel usa para calcular o tempo
    """
    def __init__(self, data_inicial: str, data_final: str, query:str='ticket_assigned', relatorio_limpo: bool = True, converter_segundos: bool = True):
        super().__init__(query, data_inicial, data_final)
        self.relatorio_limpo = relatorio_limpo
        self.converter_segundos = converter_segundos       

    def relatorio_tickets(self):
        """Gera relatório de chamados do período desejado"""
        df = self.ler_query()

        df['tempo_fechamento'] = df['close_delay_stat'] / (24*60*60)
        df['tempo_solucao'] = df['solve_delay_stat'] / (24*60*60)
        df['tempo_medio_solucao'] = df['tempo_medio_solucao'] / (24*60*60)
        df['tempo_medio_fechamento'] = df['tempo_medio_fechamento'] / (24*60*60)
        
        if self.converter_segundos:
            df['close_delay_stat'] = pd.to_datetime(df["close_delay_stat"], unit='s').dt.strftime("%H:%M:%S")  
            df['solve_delay_stat'] = pd.to_datetime(df["solve_delay_stat"], unit='s').dt.strftime("%H:%M:%S")  
        
        df['type'].replace({1: 'Incidente', 2: 'Requisição'}, inplace=True)
        df['atraso'] = np.logical_or(df['solvedate'] > df['time_to_resolve'], df['time_to_resolve'] == "")
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].dt.strftime('%Y-%m')
        if self.relatorio_limpo:
            df.drop(labels=['name', 'date_mod', 'users_id_lastupdater', 'content', 'global_validation', 'ola_waiting_duration', 'olas_id_tto', 'olas_id_ttr', 'olalevels_id_ttr',
                            'internal_time_to_resolve', 'internal_time_to_own', 'validation_percent', 'requesttypes_id'], axis=1, inplace=True)
            df = df[df.nome_tecnico != 'Pedro']

        self.df_base = df
        self.df_cru = self.df_base.copy(deep=True)

    def relatorio_tickets_com_actualtime(self):
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
            con=self.conexao,
            params={"initial_date":self.data_inicial, "final_date":self.data_final}
            )
        df.loc[df['tempo_via_plugin'] > 1000000000, 'tempo_via_plugin'] = 0
        df['tempo_eleito'] = np.where(df['tempo_via_plugin'].isnull(), df['tempo_via_glpi'], df['tempo_via_plugin'])
        df['tempo_eleito'] = df['tempo_eleito'] / (24*60*60)

        self.df_base = df
        self.df_cru = self.df_base.copy(deep=True)

    def __calcular_notas_tempos(self, nome_coluna):
        """Calcula a nota dos valores de tempo desejados

        Procedimento:
            - delta_tempo é calculado através da diferença do tempo médio gasto para a devida categoria do chamado e o
            tempo gasto pelo técnico para aquele chamado.
            - a coluna delta_tempo é normalizada entre valores de 0 a 1.
            - diferenca_media_vs_gasto é a diferença percentual de tempo gasto com o tempo médio de duração
         

        :param data_frame: dataframe usado no cálculo
        :param col_name: nome da coluna cuja nota será calculada
        :param excluir_coluna: exclui as colunas complementares que foram criadas apenas para serem usadas no cálculo
        """
        self.df_base[f'delta_tempo_{nome_coluna}'] = self.df_base[f'tempo_medio_{nome_coluna}'] - \
            self.df_base[f'tempo_{nome_coluna}']
        self.df_base[f'max_mes_{nome_coluna}'] = self.df_base.groupby(['date'])[f'delta_tempo_{nome_coluna}'].transform('max')
        self.df_base[f'min_mes_{nome_coluna}'] = self.df_base.groupby(['date'])[f'delta_tempo_{nome_coluna}'].transform('min')    
        self.df_base[f'delta_tempo_{nome_coluna}_normalized'] = (self.df_base[f'delta_tempo_{nome_coluna}'] - self.df_base[f'min_mes_{nome_coluna}']) \
            / (self.df_base[f'max_mes_{nome_coluna}'] - self.df_base[f'min_mes_{nome_coluna}'])
        self.df_base[f'diferenca_media_vs_gasto_{nome_coluna}'] = self.df_base[f'delta_tempo_{nome_coluna}'] / self.df_base[f'tempo_medio_{nome_coluna}']

        if self.relatorio_limpo:           
            self.df_base.drop(columns=[f'max_mes_{nome_coluna}', f'min_mes_{nome_coluna}'], inplace=True)

    def media_notas_tempo(self, **tabela_e_peso):
        """Calcula a média das notas dos tempos de acordo com os pesos repassados)

        :param kwargs **tabela_e_peso: kwargs da forma nome_tabela=peso
        """
        total_peso = 0
        data_frame = self.df_base
        data_frame[f'nota_final_tempos'] = 0
        for nome_tabela, peso in tabela_e_peso.items():
            self.__calcular_notas_tempos(nome_tabela)
            data_frame[f'nota_final_tempos'] = data_frame[f'delta_tempo_{nome_tabela}_normalized'] * peso + data_frame[f'nota_final_tempos']
            if self.relatorio_limpo:
                data_frame.drop(columns=[f'delta_tempo_{nome_tabela}_normalized'], inplace=True)
            total_peso += int(peso)        
        data_frame['nota_final_tempos'] = data_frame['nota_final_tempos'] / total_peso

    def calcular_bonus_quantidade(self, bonus_percentual=0.2):
        """Calcula o bônus devido a quantidade.

        A fórmula encontra a quantidade de chamados mensais por técnico, atribuindo uma bonificação percentual que varia de 0 a 20%, sendo o técnico
        com a maior quantidade de chamados a pessoa que irá receber a maior bonificação. Note que as notas serão geradas já de forma normalizada.

        :param data_frame: data frame onde os bônus serão calculados.
        :param excluir_coluna: define se a coluna dos valores de bonificação será excluída ou não do relatório final"""
        data_frame = self.df_base
        data_frame['qtde_chamados'] = data_frame.groupby(['date', 'nome_tecnico'])['id'].transform('count')
        data_frame['bonus'] = 1+bonus_percentual*(data_frame['qtde_chamados'] - data_frame.groupby(['date'])['qtde_chamados'].transform('min')) / (data_frame.groupby(['date'])['qtde_chamados'].transform('max') - data_frame.groupby(['date'])['qtde_chamados'].transform('min'))
        data_frame['nota_final_tempos'] = data_frame['nota_final_tempos'] * data_frame['bonus']
        data_frame['nota_final_tempos'] = (data_frame['nota_final_tempos'] / data_frame.groupby(['date'])['nota_final_tempos'].transform('max'))
        if self.relatorio_limpo:
            data_frame.drop(columns=['bonus', 'qtde_chamados'], inplace=True)

    def notas_finais(self):
        f = {
            'id': 'nunique',
            'tempo_fechamento': np.mean,
            'diferenca_media_vs_gasto_fechamento': np.mean,
            'tempo_solucao': np.mean,
            'diferenca_media_vs_gasto_solucao': np.mean,
            'nota_final_tempos': np.mean
        }

        data_frame = self.df_base

        g = data_frame.groupby(['nome_tecnico', 'date'])
        v1 = g.agg(f)
        v2 = g.agg(lambda x: x.drop_duplicates(
            subset='id', keep='first').atraso.sum())
        new_df = pd.concat([v1, v2.to_frame('atraso')], axis=1)
        new_df = new_df.reset_index()
        self.df_base = new_df
        if 'nome_observador' in self.df_base.columns:
            g = data_frame.groupby(['nome_observador', 'date'])
            v3 = g.agg({'id': 'count'})
            final_df = pd.concat([new_df, v3], axis=1)
            final_df = final_df.reset_index()
            final_df = final_df.rename(columns={
                'level_0': 'nome',
                'id': 'qtde_chamados'
            })
            return final_df

    def relatorio_rapido(self, calcular_nota_final=False):
        self.relatorio_tickets()
        self.media_notas_tempo(solucao=1, fechamento=1)
        self.calcular_bonus_quantidade()
        if calcular_nota_final:
            self.notas_finais()
            self.exportar_em_excel('notas')
        else:
            self.exportar_em_excel('tickets')

