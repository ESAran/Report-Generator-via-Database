# global_vars.py
# Este módulo define variáveis globais utilizadas em diferentes partes do projeto.
# Essas variáveis incluem tokens de autenticação, caminhos para arquivos e bases de dados,
# informações de contato, e configurações de e-mail SMTP. O objetivo é centralizar e facilitar
# a manutenção dessas configurações, evitando duplicidade e facilitando alterações futuras.
# Variáveis:
#     TOKEN (str): Token de autenticação para acesso a recursos protegidos.
#     PATH_DATABRICKS (str): Consulta SQL para extração de dados do Databricks.
#     PATH_INDEX_ACCOUNTS (str): Caminho absoluto para o arquivo de contas, personalizado para o usuário atual.
#     PATH_BASES (str): Caminho absoluto para a pasta de bases, personalizado para o usuário atual.
#     OUVIDORIA_SICREDI (str): Telefone da ouvidoria Sicredi.
#     SMTP_SERVER (str): Endereço do servidor SMTP para envio de e-mails.
#     SMTP_PORT (int): Porta do servidor SMTP.
#     SMTP_USERNAME (str): Usuário para autenticação no servidor SMTP.
#     SMTP_PASSWORD (str): Senha para autenticação no servidor SMTP.
#     EMAIL_FROM (str): Endereço de e-mail do remetente padrão.
#     EMAIL_USER_DUVIDA (str): Nome(s) do(s) usuário(s) para contato em caso de dúvidas.


TOKEN = ''
PATH_DATABRICKS = 'SELECT * FROM table_name'

PATH_INDEX_ACCOUNTS = ''
PATH_BASES = ''

OUVIDORIA_SICREDI = '0800 000 0000'

SMTP_SERVER = ''
SMTP_PORT = 00
SMTP_USERNAME = ''
SMTP_PASSWORD = ''

EMAIL_FROM = ''
EMAIL_USER_DUVIDA = ''