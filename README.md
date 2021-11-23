# glpi-metrics
Scripts Python combinados com SQL para geração de relatórios personalizados junto ao banco de dados do GLPI. Uso de pandas para calcular campos personalizados e formatar o relatório. 

## Detalhes:
### Classe DataBaseConnector:
 - Usada para estabelecer conexão remota via SSH entre o script e o servidor linux remoto.
 - Parâmetros para conexão são definidos por arquivo config.ini
 
### Classe ReportBuilder:
 - Principal classe, a qual reune diversos métodos e atributos para elaboração de relatórios personalizados
 - Engloba funções de cálculo de notas, tempo gasto nos serviços e contagem de chamados por técnico
 
### Disclaimer:
 - Estes scripts podem ser executados em qualquer instância do GLPI, bastando apenas ajustar os parâmetros em um arquivo .ini
 - Feito por Felipe Bartocci
