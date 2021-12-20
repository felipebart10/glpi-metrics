from tools.reportbuilder import GenericBuilder

df = GenericBuilder('users_count')
df.ler_query()
df.exportar_dataframe('quantidade_usuarios', iniciar_arquivo=False)

