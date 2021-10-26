
import pandas as pd
import numpy as np
from os import startfile
import datetime
from inc.sshcon import mysql_connect, open_ssh_tunnel

def tickets_report(initial_date, final_date, clean_report=True, convert_seconds=True):
    """Gera relatório de chamados do período desejado

    :param initial_date: data inicial na forma yyyy-mm-dd
    :param final_date: data final na forma yyyy-mm-dd
    :param clean_report: opção de limpar ou não o relatório, removento colunas inutilizadas.
    :param convert_seconds: opção para converter os segundos em número de série de data/hora usados no excel"""
    
    open_ssh_tunnel()
    connection = mysql_connect()

    first_day = f'{initial_date[:4]}-01-01'

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

    """, connection, params=[first_day, final_date, first_day, final_date, initial_date, final_date, initial_date, final_date])

    # Coluna auxiliar para criar valor de tempo interpretado pelo excel
    df['tempo_fechamento'] = df['close_delay_stat'] / (24*60*60)
    # Coluna auxiliar para criar valor de tempo interpretado pelo excel
    df['tempo_solucao'] = df['solve_delay_stat'] / (24*60*60)
    df['tempo_medio_solucao'] = df['tempo_medio_solucao'] / (24*60*60)
    df['tempo_medio_fechamento'] = df['tempo_medio_fechamento'] / (24*60*60)
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
    if clean_report:
        df.drop(labels=['name', 'date_mod', 'users_id_lastupdater', 'content', 'global_validation', 'ola_waiting_duration', 'olas_id_tto', 'olas_id_ttr', 'olalevels_id_ttr',
                        'internal_time_to_resolve', 'internal_time_to_own', 'validation_percent', 'requesttypes_id'], axis=1, inplace=True)

    return df

def export_excel(data_frame, label='report', start_file=True):
    """Exporta um dataframe do pandas para arquivo em excel.
    
    :param data_frame: data_frame que se deseja exportar
    :param label: nome base do arquivo para salvamento. A função automaticamente remove espaços vazios e os substitui por '_', além de inserir a data no final
    :param star_file: opção de iniciar o arquivo no excel ou apenas salvá-lo sem abrir a aplicação.
    """
    file_name = f".\\reports\\{label.replace(' ','_')}_{datetime.date.today()}.xlsx"
    data_frame.to_excel(file_name, index=False)
    print(f'Arquivo salvo em: {file_name}')
    if start_file:
        startfile(file_name)    

