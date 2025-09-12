import os, requests, json, time
import pandas as pd
from src.navigations import DSSheets
from src.log import Logs
import src.global_vars as gvars

# Este módulo fornece classes utilitárias para integração com o Databricks SQL Warehouse via API REST
# e manipulação de dados em DataFrames pandas. Permite executar consultas SQL no Databricks, ler e tratar
# bases de dados Excel, e realizar o merge entre diferentes fontes para geração de extratos de cota capital.
# Inclui logging detalhado para acompanhamento das operações.

logger = Logs.load_log(__name__)

class Databricks:
    """
    Classe para interação com o endpoint SQL do Databricks via API REST.
    Métodos
    -------
    __init__():
        Inicializa a classe, buscando o token de autenticação do ambiente.
    sql_statements(statement: str, tries: int, warehouse_id: str = ''):
        Executa uma instrução SQL no Databricks SQL Warehouse.
        Caso a instrução seja um SELECT e o status retorne como PENDING, realiza novas tentativas até o sucesso ou atingir o número máximo de tentativas.
        Parâmetros
        ----------
        statement : str
            Instrução SQL a ser executada.
        tries : int
            Número máximo de tentativas em caso de status PENDING.
        warehouse_id : str, opcional
            ID do SQL Warehouse a ser utilizado (padrão: '').
        Retorna
        -------
        response : requests.Response
            Objeto de resposta da requisição HTTP.
    """
    def __init__(self):
        self.token = ''

    def sql_statements(self, statement: str, tries : int, warehouse_id: str = ''):
        """
        Executa uma instrução SQL no Databricks SQL Warehouse e trata estados pendentes para consultas SELECT.
        Parâmetros:
            statement (str): Instrução SQL a ser executada.
            tries (int): Número máximo de tentativas caso a consulta fique pendente.
            warehouse_id (str, opcional): ID do SQL Warehouse do Databricks. Padrão: ''.
        Retorna:
            requests.Response: Objeto de resposta HTTP da API do Databricks.
        Observações:
            - Para instruções SELECT, se o status inicial for 'PENDING', o método irá tentar novamente até o limite de `tries`,
              aguardando um tempo crescente entre as tentativas.
            - Requer que `self.token` esteja definido com um token válido da API do Databricks.
        """
        #logger.info(f"Enviando statement para o Databricks: {statement[:80]}...")
        
        endpoint = ''
        header = {'Authorization': f'Bearer {self.token}'}
        body = {
            "statement": statement,
            "warehouse_id": warehouse_id
        }

        response = requests.post(url=endpoint, headers=header, json=body)
        response_text_json = json.loads(response.text)
        
        if statement.split(maxsplit=1)[0] == 'SELECT':
            current_try = 0
            while current_try < tries and response_text_json['status']["state"] != "SUCCEEDED":
                current_try += 1
                time.sleep(current_try * tries * 10)
                response = requests.post(url=endpoint, headers=header, json=body)

        logger.info("Statement executado no Databricks com sucesso.")
        return response

class DataFrameBuilder:
    """
    Classe utilitária para construção e manipulação de DataFrames a partir de diferentes fontes de dados,
    como Databricks SQL e arquivos Excel. Fornece métodos para buscar, tratar e combinar bases de dados
    utilizadas no processo de geração de extratos de cota capital.

    Métodos
    -------
    get_accounts_data(statement: str, tries: int) -> pd.DataFrame
        Executa uma consulta SQL no Databricks e retorna os dados como DataFrame.
    get_index_data(path: str) -> pd.DataFrame
        Atualiza e lê uma base Excel, tratando o número da conta, e retorna como DataFrame.
    create_cota_capital() -> pd.DataFrame
        Realiza o merge entre a base de contas e o índice, retornando o DataFrame consolidado.
    """
    path_databricks = gvars.PATH_DATABRICKS
    path_index_accounts = gvars.PATH_INDEX_ACCOUNTS


    @staticmethod
    def get_accounts_data(statement: str = path_databricks, tries: int = 3) -> pd.DataFrame:
        """
        Executa uma consulta SQL no Databricks e retorna os dados como um DataFrame do pandas.

        Parâmetros:
        -----------
        statement : str, opcional
            Consulta SQL a ser executada no Databricks. Por padrão, utiliza o valor da variável de ambiente 'PATH_DATABRICKS'.
        tries : int, opcional
            Número máximo de tentativas caso a consulta fique pendente. Padrão: 3.

        Retorna:
        --------
        pd.DataFrame
            DataFrame contendo os dados retornados pela consulta SQL.
        """
        logger.info(f"Executando get_accounts_data com statement: {statement[:80]}...")
        databricks = Databricks()
        response = databricks.sql_statements(statement, tries)
        response_text_json = json.loads(response.text)
        
        data = response_text_json['result']['data_array']
        logger.info(f"Quantidade de registros retornados: {len(data)}")

        columns = response_text_json['manifest']['schema']['columns']
        column_names = [col['name'] for col in columns]
        logger.info(f"Colunas retornadas: {column_names}")
        return pd.DataFrame(data, columns=column_names)
    
    @staticmethod
    def get_index_data(path : str = path_index_accounts) -> pd.DataFrame:
        """
        Atualiza e lê uma base Excel, tratando o número da conta, e retorna como DataFrame.

        Parâmetros:
        -----------
        path : str, opcional
            Caminho para o arquivo Excel da base de índices. Por padrão, utiliza o valor da variável de ambiente 'PATH_INDEX_ACCOUNTS'.

        Retorna:
        --------
        pd.DataFrame
            DataFrame contendo os dados da base de índices, com o número da conta tratado.
        """
        logger.info('Atualizando base_completa')
        DSSheets.windows_excel_refresh_query(path, visible=True)
        df_index = pd.read_excel(path)
        logger.info('Realizando a leitura da base')

        logger.info('Tratando o número da conta')
        df_index['conta'] = df_index['conta'].astype(str).str.zfill(6)
        df_index['conta'] = df_index['conta'].str[:-1] + '-' + df_index['conta'].str[-1]
        logger.info('Leitura e tratamento da base de índices concluídos')
        return df_index
    
    @staticmethod
    def create_cota_capital():
        """
        Realiza o merge entre a base de contas (Databricks) e a base de índices (Excel),
        retornando um DataFrame consolidado para geração dos extratos.

        Retorna:
        --------
        pd.DataFrame
            DataFrame resultante do merge entre as bases de contas e índices.
        """

        logger.info("Iniciando criação do DataFrame de cota capital.")

        logger.info("Obtendo dados das contas do Databricks.")
        accounts = DataFrameBuilder.get_accounts_data()
        logger.info(f"Dados das contas obtidos: {accounts.shape[0]} linhas, {accounts.shape[1]} colunas.")

        logger.info("Obtendo dados do índice (Excel).")
        index = DataFrameBuilder.get_index_data()
        logger.info(f"Dados do índice obtidos: {index.shape[0]} linhas, {index.shape[1]} colunas.")

        logger.info("Realizando merge entre as bases de contas e índices.")
        merged_df = pd.merge(index, accounts, on='conta')
        logger.info(f"Merge concluído: {merged_df.shape[0]} linhas, {merged_df.shape[1]} colunas.")

        return merged_df
        
if __name__ == "__main__":
    # dmanager = DataFrameBuilder()
    # print(dmanager.create_cota_capital())

    # TESTE BASE DATABRICKS
    db = Databricks()

    test_statement = ""

    response = db.sql_statements(test_statement, 3)
    response_text_json = json.loads(response.text)
    # print(response_text_json)

    list_accounts = response_text_json['result']['data_array']
    rows_amnt = response_text_json['result']['row_count']
    print(f"Quantidade de itens na lista: {len(list_accounts)}, row_counts = {rows_amnt}")

    columns = response_text_json['manifest']['schema']['columns']
    column_names = [col['name'] for col in columns]
    df = pd.DataFrame(list_accounts, columns=column_names)
    #print(df)

    # def existe_valor_negativo_em_dataframe(df):
    #     """
    #     Verifica se há valores negativos no campo 'valor_transacao' dentro
    #     """
    #     for idx, row in df.iterrows():
    #         valor_mov = row['tipo_valor_data_movimentacao']
    #         if not valor_mov or valor_mov in ('', 'null', 'None'):
    #             continue  # pula se for None, vazio ou string nula
    #         movimentos = json.loads(valor_mov)
    #         for movimento in movimentos:
    #             if float(movimento.get("valor_transacao", 0)) < 0:
    #                 print(f"Conta: {row.get('conta', 'N/A')} possui valor negativo: {movimento}")
    # existe_valor_negativo_em_dataframe(df)
