# glpi-metrics
Scripts Python combinados com SQL para geração de relatórios personalizados junto ao banco de dados do GLPI. Uso de pandas para calcular campos personalizados e formatar o relatório. 

## Detalhes:

### Classe GenericBuilder:
 - Classe genérica que possui diversas funções comuns para os diversos tipos de classes de relatório

### Classe DataBaseConnector:
 - Usada para estabelecer conexão remota via SSH entre o script e o servidor linux remoto.
 - Parâmetros para conexão são definidos por arquivo config.ini
 
### Classe TicketReportBuilder:
 - Principal classe, a qual reune diversos métodos e atributos para cálculo das notas
 - Engloba funções de cálculo de notas, tempo gasto nos serviços e contagem de chamados por técnico
 
### Disclaimer:
 - Estes scripts podem ser executados em qualquer instância do GLPI, bastando apenas ajustar os parâmetros em um arquivo .ini
 - Feito por Felipe Bartocci
